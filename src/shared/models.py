"""Compatibility exports for shared dataclasses."""

try:
    from src.logic.models import (  # type: ignore
        AcquisitionDetails,
        BrrrrMetrics,
        CapitalMarketsDetails,
        DealProfile,
        ExpenseLineItems,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        ProformaAssumptions,
        ProformaYear,
        PropertyDetails,
        TaxOptimizationInputs,
        TaxOptimizationOutputs,
        UnderwritingInputs,
        UnderwritingOutputs,
        VerdictInputs,
        VerdictOutputs,
    )
except ImportError:
    from logic.models import (  # type: ignore
        AcquisitionDetails,
        BrrrrMetrics,
        CapitalMarketsDetails,
        DealProfile,
        ExpenseLineItems,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        ProformaAssumptions,
        ProformaYear,
        PropertyDetails,
        TaxOptimizationInputs,
        TaxOptimizationOutputs,
        UnderwritingInputs,
        UnderwritingOutputs,
        VerdictInputs,
        VerdictOutputs,
    )

__all__ = [
    "AcquisitionDetails",
    "BrrrrMetrics",
    "CapitalMarketsDetails",
    "DealProfile",
    "ExpenseLineItems",
    "ProfitFirstInputs",
    "ProfitFirstOutputs",
    "ProformaAssumptions",
    "ProformaYear",
    "PropertyDetails",
    "TaxOptimizationInputs",
    "TaxOptimizationOutputs",
    "UnderwritingInputs",
    "UnderwritingOutputs",
    "VerdictInputs",
    "VerdictOutputs",
]
