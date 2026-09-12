"""
Recommendation contract.

The recommendation engine is deterministic and backend-owned.
These structures define what later phases will produce and the frontend
will display verbatim.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
        description="Whether incoming shipments cover the projected gap",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Short, verifiable reasons behind the recommendation",
    )

    def is_actionable(self) -> bool:
        return self.action in {
            RecommendationAction.REORDER,
            RecommendationAction.REDUCE_EXCESS,
            RecommendationAction.MONITOR_PREPARE,
        }
