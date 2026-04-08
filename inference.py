import os
import time
import requests

# IMPORTANT:
# Do NOT use API_BASE_URL here because validator may already set it
# for some unrelated service (like an LLM gateway).
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "").strip()

TASKS = [
    "easy_stable_growth",
    "medium_competition_pressure",
    "hard_pivot_or_die"
]

MAX_STEPS = 8
TIMEOUT = 10


def log_start(task, env_name, model):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True
    )


def log_end(success, steps, rewards, error=None):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    extra = f" error={error}" if error else ""
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}{extra}",
        flush=True
    )


def candidate_base_urls():
    candidates = []

    if ENV_BASE_URL:
        candidates.append(ENV_BASE_URL.rstrip("/"))

    # Common local endpoints to probe
    candidates.extend([
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:7860",
        "http://localhost:7860",
    ])

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def find_working_server(max_retries=20, delay=2):
    for _ in range(max_retries):
        for base_url in candidate_base_urls():
            try:
                resp = requests.get(f"{base_url}/tasks", timeout=TIMEOUT)
                if resp.status_code == 200:
                    data = resp.json()
                    if "available_tasks" in data:
                        return base_url
            except Exception:
                pass
        time.sleep(delay)
    return None


def safe_post(base_url, path, **kwargs):
    resp = requests.post(f"{base_url}{path}", timeout=TIMEOUT, **kwargs)
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(
            f"{path} returned non-JSON response with status {resp.status_code}"
        )
    return resp.status_code, data


def choose_action(observation, task_name, step):
    pmf = observation.get("pmf_score", 0)
    cash = observation.get("cash_left", 0)
    burn = observation.get("burn_rate", 0)
    revenue = observation.get("revenue", 0)

    if task_name == "hard_pivot_or_die":
        if step == 1 and pmf < 50:
            return "pivot_business_model"
        if pmf < 65:
            return "improve_product"
        if cash < 80000:
            return "reduce_costs"
        return "increase_marketing"

    if task_name == "medium_competition_pressure":
        if cash < 70000 or burn > revenue * 1.2:
            return "reduce_costs"
        if pmf < 60:
            return "improve_product"
        return "increase_marketing"

    # easy_stable_growth
    if pmf < 70:
        return "improve_product"
    if cash < 60000:
        return "reduce_costs"
    return "increase_marketing"


def run_task(base_url, task_name):
    rewards = []
    success = False
    steps_taken = 0

    status, reset_data = safe_post(base_url, "/reset", params={"task_name": task_name})

    if status != 200:
        raise RuntimeError(f"/reset failed with status {status}: {reset_data}")

    if "observation" not in reset_data:
        raise RuntimeError(f"/reset response missing 'observation': {reset_data}")

    observation = reset_data["observation"]

    log_start(task_name, "openstartup-env", "rule_based")

    for step in range(1, MAX_STEPS + 1):
        action = choose_action(observation, task_name, step)

        status, data = safe_post(base_url, "/step", json={"action": action})

        if status != 200:
            raise RuntimeError(f"/step failed with status {status}: {data}")

        if "observation" not in data or "reward" not in data or "done" not in data:
            raise RuntimeError(f"/step response missing required fields: {data}")

        reward = float(data["reward"])
        done = bool(data["done"])
        error = data.get("info", {}).get("message")
        observation = data["observation"]

        rewards.append(reward)
        steps_taken = step

        log_step(step, action, reward, done, error)

        if done:
            task_score = data.get("info", {}).get("task_score", 0.0)
            success = task_score > 0.5
            break

    log_end(success, steps_taken, rewards)


def main():
    base_url = find_working_server()

    if not base_url:
        log_end(
            success=False,
            steps=0,
            rewards=[],
            error="Environment server not reachable on expected local endpoints"
        )
        return

    for task in TASKS:
        try:
            run_task(base_url, task)
        except Exception as e:
            log_end(False, 0, [], error=str(e))
            # Do not raise; avoid non-zero exit that fails validation


if __name__ == "__main__":
    main()