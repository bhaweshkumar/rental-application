"""Smoke tests for rental_platform.models."""
from rental_platform.models import (
    DealProfile,
    PropertyDetails,
    VerdictOutputs,
    CapitalMarketsDetails,
    ExpenseLineItems,
)


def test_deal_profile_defaults():
    profile = DealProfile()
    assert profile.property_details.asset_type == "Single-Family"
    assert profile.verdict_outputs.verdict_status == "Fail"
    assert isinstance(profile.id, str) and len(profile.id) > 0


def test_deal_profile_unique_ids():
    p1 = DealProfile()
    p2 = DealProfile()
    assert p1.id != p2.id


def test_nested_defaults_are_independent():
    p1 = DealProfile()
    p2 = DealProfile()
    p1.property_details.address = "123 Main St"
    assert p2.property_details.address == ""


def test_verdict_outputs_defaults():
    vo = VerdictOutputs()
    assert vo.verdict_status == "Fail"
    assert vo.verdict_reasons == []


def test_capital_markets_details_defaults():
    cmd = CapitalMarketsDetails()
    assert cmd.loan_type == "DSCR"
    assert cmd.ltv_pct == 75
    assert cmd.loan_amount == 0.0


def test_expense_line_items_defaults():
    e = ExpenseLineItems()
    assert e.annual_property_taxes == 0.0
    assert e.monthly_hoa == 0.0
