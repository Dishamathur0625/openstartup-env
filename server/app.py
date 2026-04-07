from fastapi import FastAPI, Query
import uvicorn

from envs.startup_env import OpenStartupEnv
from envs.models import StartupAction
from envs.tasks import TASKS

app = FastAPI(title="OpenStartupEnv")

current_task = "easy_stable_growth"
env = OpenStartupEnv(task_name=current_task)


@app.post("/reset")
def reset(task_name: str = Query(default="easy_stable_growth")):
    global env, current_task
    if task_name not in TASKS:
        return {"error": f"Invalid task_name. Available tasks: {list(TASKS.keys())}"}

    current_task = task_name
    env = OpenStartupEnv(task_name=current_task)
    obs = env.reset()
    return {
        "task_name": current_task,
        "observation": obs.model_dump()
    }


@app.post("/step")
def step(action: StartupAction):
    obs, reward, done, info = env.step(action)
    return {
        "task_name": current_task,
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }


@app.get("/state")
def state():
    return {
        "task_name": current_task,
        "state": env.state()
    }


@app.get("/tasks")
def tasks():
    return {
        "available_tasks": list(TASKS.keys())
    }


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()