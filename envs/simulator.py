def clamp(value, low, high):
    return max(low, min(high, value))

def apply_action(state: dict, action: str) -> tuple[dict, float, str]:
    reward = 0.0
    reason = []

    prev_users = state["users"]
    prev_revenue = state["revenue"]
    prev_pmf = state["pmf_score"]
    prev_burn = state["burn_rate"]

    # monthly operating cost always hits
    state["cash_left"] -= state["burn_rate"]
    state["month"] += 1

    if action == "improve_product":
        state["product_quality"] = clamp(state["product_quality"] + 10, 0, 100)
        state["pmf_score"] = clamp(state["pmf_score"] + 8, 0, 100)
        state["burn_rate"] += 5000
        reason.append("Improved product and PMF, but spending increased.")

    elif action == "increase_marketing":
        state["marketing_strength"] = clamp(state["marketing_strength"] + 10, 0, 100)
        state["users"] += int(200 + state["pmf_score"] * 2)
        state["revenue"] += 8000 + state["users"] * 0.5
        state["burn_rate"] += 7000
        reason.append("Marketing boosted users and revenue, but burn increased.")

    elif action == "reduce_costs":
        state["burn_rate"] = max(10000, state["burn_rate"] - 10000)
        state["product_quality"] = clamp(state["product_quality"] - 5, 0, 100)
        reason.append("Costs reduced, but product quality dropped slightly.")

    elif action == "pivot_business_model":
        if state["pmf_score"] < 50:
            state["startup_type"] = "pivoted_" + state["startup_type"]
            state["pmf_score"] = clamp(state["pmf_score"] + 25, 0, 100)
            state["users"] = int(state["users"] * 0.8)
            state["revenue"] = max(0, state["revenue"] * 0.85)
            state["burn_rate"] += 3000
            reason.append("Pivot improved product-market fit but caused short-term loss.")
        else:
            state["users"] = int(state["users"] * 0.9)
            state["revenue"] *= 0.9
            state["pmf_score"] = clamp(state["pmf_score"] - 5, 0, 100)
            reason.append("Unnecessary pivot hurt the business.")

    elif action == "raise_funding":
        if state["pmf_score"] >= 50:
            state["cash_left"] += 120000
            state["burn_rate"] += 3000
            reward += 0.15
            reason.append("Funding raised successfully.")
        else:
            state["cash_left"] += 40000
            reward -= 0.10
            reason.append("Funding raised weakly because PMF is poor.")

    elif action == "shutdown":
        reason.append("Startup shut down by agent.")
        return state, 0.0, " ".join(reason)

    # passive business dynamics after action
    trend_multiplier = {
        "growing": 1.10,
        "stable": 1.00,
        "declining": 0.90,
    }[state["market_trend"]]

    competition_penalty = {
        "low": 1.00,
        "medium": 0.95,
        "high": 0.88,
    }[state["competition_level"]]

    pmf_factor = 1 + (state["pmf_score"] - 50) / 100.0
    product_factor = 1 + (state["product_quality"] - 50) / 200.0

    state["users"] = max(
        0,
        int(state["users"] * trend_multiplier * competition_penalty * pmf_factor)
    )
    state["revenue"] = max(
        0.0,
        state["users"] * 18 * product_factor
    )

    # reward shaping
    if state["users"] > prev_users:
        reward += 0.20
    else:
        reward -= 0.10

    if state["revenue"] > prev_revenue:
        reward += 0.20
    else:
        reward -= 0.10

    if state["pmf_score"] > prev_pmf:
        reward += 0.25

    if state["burn_rate"] < prev_burn:
        reward += 0.15

    if state["cash_left"] > 0:
        reward += 0.10

    if state["cash_left"] <= 0:
        reward = -1.0
        reason.append("Startup went bankrupt.")

    return state, round(reward, 2), " ".join(reason)