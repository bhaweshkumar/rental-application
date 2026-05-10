import streamlit as st
import numpy_financial as npf
from src.models import DealProfile, VerdictOutputs


def normalize_financing(deal: DealProfile):
    """
    Placeholder function to normalize financing details.
    This is where you would implement logic like calculating the loan amount
    from the purchase price and down payment percentage.
    """
    # This function can be expanded to handle more complex scenarios.
    pass


def evaluate_deal_verdict(deal: DealProfile) -> VerdictOutputs:
    """
    Evaluates the deal based on the data in the DealProfile object and
    returns the verdict and key metrics.
    """
    try:
        # Extract values from the deal profile
        purchase_price = deal.acquisition.purchase_price
        down_payment_pct = deal.financing.down_payment_percent
        interest_rate = deal.financing.interest_rate
        loan_term = deal.financing.loan_term_years
        gross_rent = deal.underwriting.projected_monthly_gross_rent
        expenses = deal.underwriting.total_monthly_expenses

        # Perform calculations
        loan_amount = purchase_price * (1 - down_payment_pct)
        
        # Handle edge cases for mortgage calculation
        if loan_term > 0 and interest_rate > 0:
            monthly_interest_rate = interest_rate / 12
            num_payments = loan_term * 12
            monthly_p_i = -npf.pmt(monthly_interest_rate, num_payments, loan_amount)
        else:
            monthly_p_i = 0

        cash_flow_monthly = gross_rent - expenses - monthly_p_i

        # Determine the verdict
        verdict = "Fail"
        if cash_flow_monthly > 200:
            verdict = "Pass"
        elif cash_flow_monthly >= 0:
            verdict = "Caution"

        return VerdictOutputs(final_verdict=verdict, cash_flow_monthly=cash_flow_monthly)

    except (TypeError, ValueError) as e:
        st.toast(f"Calculation error: {e}", icon="⚠️")
        return VerdictOutputs()


def refresh_deal_calculations(deal: DealProfile) -> None:
    """Central function to re-compute all derived financial and verdict data."""
    normalize_financing(deal)
    verdict_outputs = evaluate_deal_verdict(deal)
    deal.verdict_outputs = verdict_outputs
    if deal.verdict_outputs:
        deal.underwriting.projected_cash_flow = deal.verdict_outputs.cash_flow_monthly