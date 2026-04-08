EPS_MIN = 0.01
EPS_MAX = 0.99


def clamp_score(score: float) -> float:
    if score <= 0:
        return EPS_MIN
    if score >= 1:
        return EPS_MAX
    return round(score, 2)


def grade_easy(initial_state, final_state, history):
    score = 0.0

    if final_state["cash_left"] > 0:
        score += 0.30
    if final_state["revenue"] > initial_state["revenue"]:
        score += 0.25
    if final_state["users"] > initial_state["users"]:
        score += 0.20
    if final_state["pmf_score"] >= initial_state["pmf_score"]:
        score += 0.15
    if "shutdown" not in history:
        score += 0.10

    return clamp_score(score)


def grade_medium(initial_state, final_state, history):
    score = 0.0

    if final_state["cash_left"] > 0:
        score += 0.25
    if final_state["revenue"] > initial_state["revenue"]:
        score += 0.20
    if final_state["users"] > initial_state["users"]:
        score += 0.20
    if final_state["burn_rate"] <= initial_state["burn_rate"]:
        score += 0.15
    if final_state["pmf_score"] > initial_state["pmf_score"]:
        score += 0.20

    return clamp_score(score)


def grade_hard(initial_state, final_state, history):
    score = 0.0
    used_pivot = "pivot_business_model" in history
    pmf_jump = final_state["pmf_score"] - initial_state["pmf_score"]

    if final_state["cash_left"] > 0:
        score += 0.20
    if used_pivot:
        score += 0.25
    if pmf_jump >= 15:
        score += 0.25
    if final_state["revenue"] > initial_state["revenue"]:
        score += 0.15
    if final_state["users"] > initial_state["users"]:
        score += 0.15

    return clamp_score(score)


def grade_task(task_name, initial_state, final_state, history):
    if task_name == "easy_stable_growth":
        return grade_easy(initial_state, final_state, history)
    elif task_name == "medium_competition_pressure":
        return grade_medium(initial_state, final_state, history)
    elif task_name == "hard_pivot_or_die":
        return grade_hard(initial_state, final_state, history)
    else:
        return EPS_MIN