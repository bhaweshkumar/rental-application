import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PropertyDetails:
    address: str = ""
    asset_type: str = "Single-Family"
    sq_ft: int = 1000
    year_built: int = 2000
    market_phase: str = "Expansion"
    state: str = ""

@dataclass
class AcquisitionDetails:
    purchase_price: int = 250000
    rehab_level: str = "Light (Cosmetic/Paint)"
    rehab_cost_per_sqft: float = 20.0
    base_rehab_cost: float = 0.0
    contingency_pct: int = 15
    total_rehab_budget: float = 0.0
    arv: int = 350000

@dataclass
class BrrrrMetrics:
    all_in_cost: float = 0.0
    equity_capture: float = 0.0
    refi_loan_amount: float = 0.0
    cash_out_proceeds: float = 0.0

@dataclass
class CapitalMarketsDetails:
    loan_type: str = "DSCR"
    ltv_pct: int = 75
    interest_rate_pct: float = 7.5
    term_years: int = 30
    closing_costs_pct: int = 3
    loan_amount: float = 0.0
    down_payment: float = 0.0
    closing_costs: float = 0.0
    monthly_payment: float = 0.0
    annual_debt_service: float = 0.0

@dataclass
class UnderwritingInputs:
    monthly_gross_rent: int = 2000
    vacancy_pct: int = 5
    opex_pct: int = 40 # As a percentage of Effective Gross Income (EGI)

@dataclass
class UnderwritingOutputs:
    noi: float = 0.0
    cap_rate_purchase: float = 0.0
    dscr: float = 0.0
    cash_on_cash_return: float = 0.0
    total_cash_invested: float = 0.0


@dataclass
class ExpenseLineItems:
    annual_property_taxes: float = 0.0
    annual_insurance: float = 0.0
    monthly_hoa: float = 0.0
    monthly_property_management: float = 0.0
    monthly_maintenance_reserve: float = 0.0
    monthly_owner_paid_utilities: float = 0.0
    monthly_other_expenses: float = 0.0


@dataclass
class VerdictInputs:
    monthly_rent: float = 0.0
    monthly_other_income: float = 0.0
    vacancy_pct: int = 5
    rent_ready_repairs: float = 0.0


@dataclass
class VerdictOutputs:
    annual_operating_expenses: float = 0.0
    effective_gross_income: float = 0.0
    noi: float = 0.0
    monthly_cash_flow: float = 0.0
    dscr: float = 0.0
    cap_rate: float = 0.0
    cash_on_cash_return: float = 0.0
    total_cash_required: float = 0.0
    verdict_status: str = "Fail"
    verdict_reasons: List[str] = field(default_factory=list)

@dataclass
class ProformaAssumptions:
    holding_period_years: int = 5
    rent_growth_pct: float = 3.0
    expense_growth_pct: float = 2.0

@dataclass
class ProformaYear:
    year: int
    gross_potential_rent: float
    vacancy_loss: float
    effective_gross_income: float
    operating_expenses: float
    noi: float
    debt_service: float
    cash_flow_before_tax: float

@dataclass
class TaxOptimizationInputs:
    enable_cost_segregation: bool = False
    cost_seg_5_year_pct: int = 15
    cost_seg_15_year_pct: int = 10

@dataclass
class TaxOptimizationOutputs:
    year_1_bonus_depreciation: float = 0.0
    year_1_standard_depreciation: float = 0.0
    total_year_1_depreciation: float = 0.0
    remaining_basis_for_std_dep: float = 0.0
    annual_std_depreciation_after_y1: float = 0.0

@dataclass
class ProfitFirstInputs:
    profit_tap_pct: int = 5
    owners_pay_tap_pct: int = 15
    tax_tap_pct: int = 10

@dataclass
class ProfitFirstOutputs:
    profit_allocation: float = 0.0
    owners_pay_allocation: float = 0.0
    tax_allocation: float = 0.0
    opex_allocation: float = 0.0

@dataclass
class DealProfile:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "Analysis"  # e.g., "Analysis", "Under Contract", "Closed", "Rejected"
    property_details: PropertyDetails = field(default_factory=PropertyDetails)
    acquisition_details: AcquisitionDetails = field(default_factory=AcquisitionDetails)
    capital_markets_details: CapitalMarketsDetails = field(default_factory=CapitalMarketsDetails)
    underwriting_inputs: UnderwritingInputs = field(default_factory=UnderwritingInputs)
    underwriting_outputs: UnderwritingOutputs = field(default_factory=UnderwritingOutputs)
    expense_line_items: ExpenseLineItems = field(default_factory=ExpenseLineItems)
    verdict_inputs: VerdictInputs = field(default_factory=VerdictInputs)
    verdict_outputs: VerdictOutputs = field(default_factory=VerdictOutputs)
    proforma_assumptions: ProformaAssumptions = field(default_factory=ProformaAssumptions)
    tax_optimization_inputs: TaxOptimizationInputs = field(default_factory=TaxOptimizationInputs)
    tax_optimization_outputs: TaxOptimizationOutputs = field(default_factory=TaxOptimizationOutputs)
    profit_first_inputs: ProfitFirstInputs = field(default_factory=ProfitFirstInputs)
    profit_first_outputs: ProfitFirstOutputs = field(default_factory=ProfitFirstOutputs)
    # This can be extended with other feature models
    other_details: Dict[str, Any] = field(default_factory=dict)
