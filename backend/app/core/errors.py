"""
Shared error conventions.

All errors carry a stable code plus a human-readable message.
Layer-specific subclasses make it easy for the API layer to map failures
into ApiError responses without leaking internal details.
"""

from typing import Optional


class InventoryIQError(Exception):
    """Base exception for the whole application."""

    def __init__(self, message: str, *, code: str = "internal_error", details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DataAccessError(InventoryIQError):
    """Google Sheets or other data source is unreachable or malformed."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="data_access_error", details=details)


class ValidationError(InventoryIQError):
    """Raw data fails validation."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="validation_error", details=details)


class ProcessingError(InventoryIQError):
    """Failure while normalizing or combining validated data."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="processing_error", details=details)


class AnalyticsError(InventoryIQError):
    """Failure while computing deterministic analytics."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="analytics_error", details=details)


class RecommendationError(InventoryIQError):
    """Failure inside the recommendation engine."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="recommendation_error", details=details)


class AIContextError(InventoryIQError):
    """Failure while building verified AI context."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="ai_context_error", details=details)


class GeminiError(InventoryIQError):
    """Gemini API failure or unsafe response."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="gemini_error", details=details)


class NotFoundError(InventoryIQError):
    """Requested resource does not exist."""

    def __init__(self, message: str, *, details: Optional[dict] = None):
        super().__init__(message, code="not_found", details=details)
