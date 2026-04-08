import os
import json
import time
import requests
from openai import OpenAI

# Validator-provided LLM proxy
LLM_BASE_URL = os.getenv("API_BASE_URL")
LLM_API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Local environment server (not the LLM proxy)
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "").strip()

TASKS = [
    "easy_stable_growth",
    "medium_competition_pressure",
    "hard_pivot_or_die"
]

ACTIONS = [
    "improve_product",
    "increase_marketing",
    "reduce_costs",
    "pivot_business_model",
    "raise_funding",
    "shutdown"
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


def log_end(success, steps, rewards, error=None):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    extra = f" error={error}" if error else ""
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}{extra}",
        flush=True
    )


def candidate_env_urls():
    candidates = []
    if ENV_BASE_URL:
        candidates.append(ENV_BASE_URL.rstrip("/"))

    candidates.extend([
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:7860",
        "http://localhost:7860",
    ])

    seen = set()
    unique = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def wait_for_env_server(max_retries=20, delay=2):
    for _ in range(max_retries):
        for base_url in candidate_env_urls():
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
        raise RuntimeError(f"{path} returned non-JSON response with status {resp.status_code}")
    return resp.status_code, data


def fallback_action(observation, task_name, step):
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


def extract_action(text):
    if not text:
        return None

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
        action = parsed.get("action")
        if action in ACTIONS:
            return action
    except Exception:
        pass

    return None


def choose_action_with_llm(client, observation, task_name, step):
    prompt = f"""
You are controlling a startup strategy simulator.

Task: {task_name}
Step: {step}

Current observation:
{json.dumps(observation, indent=2)}

Available actions:
{ACTIONS}

Choose exactly one action from the list above.
Respond with JSON only in this format:
{{"action": "<one_action_name>"}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a startup strategy decision agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=50
        )
        content = response.choices[0].message.content
        action = extract_action(content)
        if action in ACTIONS:
            return action
    except Exception:
        pass

    return fallback_action(observation, task_name, step)


def run_task(client, env_base_url, task_name):
    rewards = []
    success = False
    steps_taken = 0

    try:
        status, reset_data = safe_post(env_base_url, "/reset", params={"task_name": task_name})

        if status != 200:
            log_end(False, 0, [], error=f"/reset failed with status {status}")
            return

        if "observation" not in reset_data:
            log_end(False, 0, [], error=f"/reset response missing observation: {reset_data}")
            return

        observation = reset_data["observation"]
        log_start(task_name, "openstartup-env", MODEL_NAME)

        for step in range(1, MAX_STEPS + 1):
            action = choose_action_with_llm(client, observation, task_name, step)

            status, data = safe_post(env_base_url, "/step", json={"action": action})

            if status != 200:
                log_end(False, steps_taken, rewards, error=f"/step failed with status {status}")
                return

            if "observation" not in data or "reward" not in data or "done" not in data:
                log_end(False, steps_taken, rewards, error=f"/step response malformed: {data}")
                return

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

    except Exception as e:
        log_end(False, steps_taken, rewards, error=str(e))


def main():
    client = None

    # Only use validator proxy if BOTH values are present
    if LLM_BASE_URL and LLM_API_KEY:
        try:
            client = OpenAI(
                base_url=LLM_BASE_URL,
                api_key=LLM_API_KEY
            )
        except Exception as e:
            log_end(False, 0, [], error=f"LLM client init failed: {e}")
            return

    env_base_url = wait_for_env_server()
    if not env_base_url:
        log_end(False, 0, [], error="Environment server not reachable on expected local endpoints")
        return

    for task in TASKS:
        run_task(client, env_base_url, task)


if __name__ == "__main__":
    main()