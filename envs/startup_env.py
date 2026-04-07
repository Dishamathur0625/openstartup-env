from copy import deepcopy
from envs.models import StartupObservation
from envs.tasks import TASKS
from envs.simulator import apply_action
from graders.startup_graders import grade_task


class OpenStartupEnv:
    def __init__(self, task_name: str):
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}")

        self.task_name = task_name
        self.task = TASKS[task_name]
        self.max_months = self.task["max_months"]
        self.initial_state = deepcopy(self.task["initial_state"])
        self._state = None
        self.history = []

    def reset(self):
        self._state = deepcopy(self.initial_state)
        self._state["month"] = 0
        self._state["last_action"] = None
        self.history = []
        return self._build_observation()

    def step(self, action):
        action_name = action.action if hasattr(action, "action") else action["action"]
        self._state["last_action"] = action_name

        if action_name == "shutdown":
            self.history.append(action_name)
            done = True
            obs = self._build_observation()
            score = grade_task(self.task_name, self.initial_state, self._state, self.history)
            return obs, 0.0, done, {
                "message": "Agent chose shutdown.",
                "task_score": score
            }

        self._state, reward, reason = apply_action(self._state, action_name)
        self.history.append(action_name)

        success_condition = (
            self._state["users"] >= 10000
            and self._state["revenue"] >= 120000
            and self._state["pmf_score"] >= 75
            and self._state["cash_left"] > 0
        )

        done = (
            self._state["cash_left"] <= 0
            or self._state["month"] >= self.max_months
            or success_condition
        )

        info = {"message": reason}

        if done:
            score = grade_task(self.task_name, self.initial_state, self._state, self.history)
            info["task_score"] = score

        return self._build_observation(), reward, done, info

    def state(self):
        return deepcopy(self._state)

    def _build_observation(self):
        return StartupObservation(
            month=self._state["month"],
            startup_type=self._state["startup_type"],
            users=self._state["users"],
            revenue=self._state["revenue"],
            burn_rate=self._state["burn_rate"],
            cash_left=self._state["cash_left"],
            market_trend=self._state["market_trend"],
            competition_level=self._state["competition_level"],
            product_quality=self._state["product_quality"],
            marketing_strength=self._state["marketing_strength"],
            pmf_score=self._state["pmf_score"],
            last_action=self._state.get("last_action"),
            goal=self.task["goal"],
        )