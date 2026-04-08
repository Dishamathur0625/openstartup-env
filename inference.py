import os
import time
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

TASKS = [
    "easy_stable_growth",
    "medium_competition_pressure",
    "hard_pivot_or_die"
]

MAX_STEPS = 8
TIMEOUT = 15


def log_start(task, env_name, model):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True
    )


def log_end(success, steps, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)


def wait_for_server(max_retries=20, delay=2):
    for _ in range(max_retries):
        try:
            resp = requests.get(f"{API_BASE_URL}/tasks", timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                if "available_tasks" in data:
                    return True
        except Exception:
            pass
        time.sleep(delay)
    return False


def safe_post(path, **kwargs):
    resp = requests.post(f"{API_BASE_URL}{path}", timeout=TIMEOUT, **kwargs)
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(f"{path} returned non-JSON response with status {resp.status_code}")
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

    if pmf < 70:
        return "improve_product"
    if cash < 60000:
        return "reduce_costs"
    return "increase_marketing"


def run_task(task_name):
    rewards = []
    success = False
    steps_taken = 0

    status, reset_data = safe_post("/reset", params={"task_name": task_name})

    if status != 200:
        raise RuntimeError(f"/reset failed with status {status}: {reset_data}")

    if "observation" not in reset_data:
        raise RuntimeError(f"/reset response missing 'observation': {reset_data}")

    observation = reset_data["observation"]

    log_start(task_name, "openstartup-env", "rule_based")

    for step in range(1, MAX_STEPS + 1):
        action = choose_action(observation, task_name, step)

        status, data = safe_post("/step", json={"action": action})

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


if __name__ == "__main__":
    if not wait_for_server():
        raise RuntimeError(f"Environment server not reachable at {API_BASE_URL}")

    for task in TASKS:
        run_task(task)