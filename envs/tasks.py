TASKS = {
    "easy_stable_growth": {
        "goal": "Grow the startup sustainably while maintaining healthy cash flow.",
        "max_months": 8,
        "initial_state": {
            "startup_type": "edtech",
            "users": 1500,
            "revenue": 40000.0,
            "burn_rate": 35000.0,
            "cash_left": 300000.0,
            "market_trend": "stable",
            "competition_level": "medium",
            "product_quality": 60,
            "marketing_strength": 45,
            "pmf_score": 60,
        }
    },
    "medium_competition_pressure": {
        "goal": "Manage growth under strong competition without running out of cash.",
        "max_months": 8,
        "initial_state": {
            "startup_type": "fintech",
            "users": 2000,
            "revenue": 50000.0,
            "burn_rate": 60000.0,
            "cash_left": 250000.0,
            "market_trend": "stable",
            "competition_level": "high",
            "product_quality": 55,
            "marketing_strength": 40,
            "pmf_score": 50,
        }
    },
    "hard_pivot_or_die": {
        "goal": "Recognize poor product-market fit and pivot early enough to survive.",
        "max_months": 8,
        "initial_state": {
            "startup_type": "creator_tools",
            "users": 800,
            "revenue": 15000.0,
            "burn_rate": 55000.0,
            "cash_left": 180000.0,
            "market_trend": "declining",
            "competition_level": "high",
            "product_quality": 50,
            "marketing_strength": 35,
            "pmf_score": 30,
        }
    }
}