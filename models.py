from pydantic import BaseModel, Field
from typing import Optional


class Acquisition(BaseModel):
    purchase_price: int = 300000


class Financing(BaseModel):
    down_payment_percent: float = 0.25
    interest_rate: float = 0.07
    loan_term_years: int = 30


class Underwriting(BaseModel):
    projected_monthly_gross_rent: int = 2500
    total_monthly_expenses: int = 1000
    projected_cash_flow: Optional[float] = None


class VerdictOutputs(BaseModel):
    final_verdict: str = "Undetermined"
    cash_flow_monthly: float = 0.0

class DealProfile(BaseModel):
    acquisition: Acquisition = Field(default_factory=Acquisition)
    financing: Financing = Field(default_factory=Financing)
    underwriting: Underwriting = Field(default_factory=Underwriting)
    verdict_outputs: Optional[VerdictOutputs] = None