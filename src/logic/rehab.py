from typing import Tuple

try:
    from src.shared.constants import REHAB_COSTS_PER_SQFT  # type: ignore
except ImportError:
    from shared.constants import REHAB_COSTS_PER_SQFT  # type: ignore


def calculate_rehab_costs(
    sq_ft: int, rehab_level: str, contingency_pct: int
) -> Tuple[float, float, float]:
    """Calculates rehab costs based on property size and selected level."""
    rehab_cost_per_sqft = REHAB_COSTS_PER_SQFT.get(rehab_level, 0)
    base_rehab_cost = sq_ft * rehab_cost_per_sqft
    contingency_amount = base_rehab_cost * (contingency_pct / 100.0)
    total_rehab_budget = base_rehab_cost + contingency_amount
    return base_rehab_cost, contingency_amount, total_rehab_budget
