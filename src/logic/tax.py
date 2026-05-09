from ..shared.models import TaxOptimizationInputs, TaxOptimizationOutputs

def calculate_depreciation(
    improvement_basis: float,
    depreciation_period_years: float,
    inputs: TaxOptimizationInputs,
) -> TaxOptimizationOutputs:
    """
    Calculates depreciation, handling standard and accelerated (cost segregation) scenarios.
    """
    if improvement_basis <= 0 or depreciation_period_years <= 0:
        return TaxOptimizationOutputs()

    if not inputs.enable_cost_segregation:
        # Standard straight-line depreciation
        annual_depreciation = improvement_basis / depreciation_period_years
        return TaxOptimizationOutputs(
            year_1_bonus_depreciation=0,
            year_1_standard_depreciation=annual_depreciation,
            total_year_1_depreciation=annual_depreciation,
            remaining_basis_for_std_dep=improvement_basis,
            annual_std_depreciation_after_y1=annual_depreciation,
        )
    else:
        # Accelerated depreciation with 100% bonus
        cost_seg_5_year_value = improvement_basis * (inputs.cost_seg_5_year_pct / 100.0)
        cost_seg_15_year_value = improvement_basis * (inputs.cost_seg_15_year_pct / 100.0)
        
        # Per 2026 rules, 5, 7, and 15-year property qualifies for 100% bonus depreciation
        bonus_depreciation = cost_seg_5_year_value + cost_seg_15_year_value
        
        remaining_basis = improvement_basis - bonus_depreciation
        std_dep_on_remainder = remaining_basis / depreciation_period_years

        return TaxOptimizationOutputs(
            year_1_bonus_depreciation=bonus_depreciation,
            year_1_standard_depreciation=std_dep_on_remainder,
            total_year_1_depreciation=bonus_depreciation + std_dep_on_remainder,
            remaining_basis_for_std_dep=remaining_basis,
            annual_std_depreciation_after_y1=std_dep_on_remainder,
        )