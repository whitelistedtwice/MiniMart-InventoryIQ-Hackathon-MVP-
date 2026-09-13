"""
Recommendation contract.

The recommendation engine is deterministic and backend-owned.
These structures define what later phases will produce and the frontend
will display verbatim.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .analytics import DemandTrend


class RecommendationAction(str, Enum):
    """Allowed recommendation statuses."""

    REORDER = "REORDER"
    REDUCE_EXCESS = "REDUCE EXCESS"
    MONITOR_PREPARE = "MONITOR / PREPARE"
    NO_ACTION = "NO ACTION"
    UNAVAILABLE = "UNAVAILABLE"


class RecommendationPriority(int, Enum):
    """
    Deterministic precedence order.

    Lower number = higher priority.
    """

    UNAVAILABLE = 0
    REORDER = 1
    REDUCE_EXCESS = 2
    MONITOR_PREPARE = 3
    NO_ACTION = 4


class RecommendationResult(BaseModel):
    """The final deterministic action for one product."""

    product_id: str
    product_name: str
    action: RecommendationAction = RecommendationAction.UNAVAILABLE
    priority: RecommendationPriority = RecommendationPriority.UNAVAILABLE
    reorder_quantity: Optional[int] = Field(
        None,
        description="Suggested additional units to order when action is REORDER",
    )
    reorder_timing: Optional[str] = Field(
        None,
        description="Human-readable timing guidance, e.g. 'within 2 days'",
    )
    incoming_stock_sufficient: Optional[bool] = Field(
        None,
        description="True if incoming shipments arrive before stock runs out; "
        "False if stock runs out first; None when there is no incoming shipment",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Short, verifiable reasons behind the recommendation",
    )
    # Supporting metrics copied from verified analytics (facts, not recomputed).
    current_stock: Optional[int] = Field(None, description="Verified current stock")
    incoming_quantity: Optional[int] = Field(None, description="Verified incoming shipment quantity")
    days_of_stock_remaining: Optional[float] = Field(None, description="Verified current stock coverage in days")
    days_until_arrival: Optional[int] = Field(None, description="Verified days until next incoming shipment")
    demand_trend: DemandTrend = Field(DemandTrend.UNAVAILABLE, description="Verified demand trend")
    target_stock_days: Optional[int] = Field(None, description="Product's configured target coverage in days")
    excess_units: Optional[float] = Field(None, description="Verified units above target coverage")

    def is_actionable(self) -> bool:
        return self.action in {
            RecommendationAction.REORDER,
            RecommendationAction.REDUCE_EXCESS,
            RecommendationAction.MONITOR_PREPARE,
        }
