"""Compatibility exports for shared constants."""

try:
    from src.logic.constants import (  # type: ignore
        ASSET_TYPE_OPTIONS,
        LANDLORD_FLEXIBILITY_RISK,
        MARKET_PHASE_OPTIONS,
        REHAB_COSTS_PER_SQFT,
        US_STATES,
    )
except ImportError:
    from logic.constants import (  # type: ignore
        ASSET_TYPE_OPTIONS,
        LANDLORD_FLEXIBILITY_RISK,
        MARKET_PHASE_OPTIONS,
        REHAB_COSTS_PER_SQFT,
        US_STATES,
    )

__all__ = [
    "ASSET_TYPE_OPTIONS",
    "LANDLORD_FLEXIBILITY_RISK",
    "MARKET_PHASE_OPTIONS",
    "REHAB_COSTS_PER_SQFT",
    "US_STATES",
]
