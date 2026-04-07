import os
import json
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://router.huggingface.co/v1")

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


def choose_action_with_llm(client, observation, task_name):
    prompt = f"""
You are controlling a startup strategy simulator.

Task: {task_name}

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
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        action = parsed.get("action", "reduce_costs")
        if action not in ACTIONS:
            return "reduce_costs"
        return action
    except Exception:
        return "reduce_costs"


def run_task(client, task_name):
    rewards = []
    success = False
    steps_taken = 0

    reset_resp = requests.post(
        f"{API_BASE_URL}/reset",
        params={"task_name": task_name}
    )
    reset_data = reset_resp.json()
    observation = reset_data["observation"]

    log_start(task_name, "openstartup-env", MODEL_NAME)

    for step in range(1, MAX_STEPS + 1):
        action = choose_action_with_llm(client, observation, task_name)

        resp = requests.post(
            f"{API_BASE_URL}/step",
            json={"action": action}
        )
        data = resp.json()

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
    client = OpenAI(
        base_url=LLM_BASE_URL,
        api_key=HF_TOKEN
    )

    for task in TASKS:
        run_task(client, task)