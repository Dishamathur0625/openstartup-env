from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

ActionType = Literal[
    "improve_product",
    "increase_marketing",
    "reduce_costs",
    "pivot_business_model",
    "raise_funding",
    "shutdown"
]

MarketTrend = Literal["growing", "stable", "declining"]
CompetitionLevel = Literal["low", "medium", "high"]

class StartupObservation(BaseModel):
    month: int
    startup_type: str
    users: int
    revenue: float
    burn_rate: float
    cash_left: float
    market_trend: MarketTrend
    competition_level: CompetitionLevel
    product_quality: int = Field(ge=0, le=100)
    marketing_strength: int = Field(ge=0, le=100)
    pmf_score: int = Field(ge=0, le=100)
    last_action: Optional[ActionType] = None
    goal: str

class StartupAction(BaseModel):
    action: ActionType

class StartupReward(BaseModel):
    reward: float
    reason: str

class StepInfo(BaseModel):
    message: str
    metrics: Dict[str, Any] = {}