import pytest
from src.logic.proforma import generate_proforma
from src.shared.models import ProformaAssumptions

def test_generate_proforma():
    """Tests the multi-year proforma generation logic."""
    # Inputs
    initial_gross_rent = 24000  # From underwriting_inputs.monthly_gross_rent * 12
    initial_opex = 9120         # From (EGI * opex_pct) -> (24000 * 0.95) * 0.40
    vacancy_pct = 5             # From underwriting_inputs
    annual_debt_service = 10000 # From capital_markets_details
    assumptions = ProformaAssumptions(
        holding_period_years=3,
        rent_growth_pct=3.0,
        expense_growth_pct=2.0,
    )

    proforma = generate_proforma(
        initial_gross_rent, initial_opex, vacancy_pct, annual_debt_service, assumptions
    )

    assert len(proforma) == 3

    # Year 1
    year1 = proforma[0]
    assert year1.year == 1
    assert year1.gross_potential_rent == pytest.approx(24000)
    assert year1.vacancy_loss == pytest.approx(1200) # 24000 * 0.05
    assert year1.effective_gross_income == pytest.approx(22800)
    assert year1.operating_expenses == pytest.approx(9120)
    assert year1.noi == pytest.approx(13680) # 22800 - 9120
    assert year1.debt_service == pytest.approx(10000)
    assert year1.cash_flow_before_tax == pytest.approx(3680)

    # Year 2
    year2 = proforma[1]
    assert year2.year == 2
    assert year2.gross_potential_rent == pytest.approx(24720) # 24000 * 1.03
    assert year2.vacancy_loss == pytest.approx(1236) # 24720 * 0.05
    assert year2.effective_gross_income == pytest.approx(23484)
    assert year2.operating_expenses == pytest.approx(9302.4) # 9120 * 1.02
    assert year2.noi == pytest.approx(14181.6)
    assert year2.debt_service == pytest.approx(10000)
    assert year2.cash_flow_before_tax == pytest.approx(4181.6)

    # Year 3
    year3 = proforma[2]
    assert year3.year == 3
    assert year3.gross_potential_rent == pytest.approx(25461.6) # 24720 * 1.03
    assert year3.operating_expenses == pytest.approx(9488.448) # 9302.4 * 1.02
    assert year3.noi == pytest.approx(14700.072)
    assert year3.cash_flow_before_tax == pytest.approx(4700.072)