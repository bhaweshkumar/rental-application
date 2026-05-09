"""Compatibility exports for shared dataclasses."""

try:
    from src.logic.models import (  # type: ignore
        AcquisitionDetails,
        BrrrrMetrics,
        CapitalMarketsDetails,
        DealProfile,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        ProformaAssumptions,
        ProformaYear,
        PropertyDetails,
        TaxOptimizationInputs,
        TaxOptimizationOutputs,
        UnderwritingInputs,
        UnderwritingOutputs,
    )
except ImportError:
    from logic.models import (  # type: ignore
        AcquisitionDetails,
        BrrrrMetrics,
        CapitalMarketsDetails,
        DealProfile,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        ProformaAssumptions,
        ProformaYear,
        PropertyDetails,
        TaxOptimizationInputs,
        TaxOptimizationOutputs,
        UnderwritingInputs,
        UnderwritingOutputs,
    )

__all__ = [
    "AcquisitionDetails",
    "BrrrrMetrics",
    "CapitalMarketsDetails",
    "DealProfile",
    "ProfitFirstInputs",
    "ProfitFirstOutputs",
    "ProformaAssumptions",
    "ProformaYear",
    "PropertyDetails",
    "TaxOptimizationInputs",
    "TaxOptimizationOutputs",
    "UnderwritingInputs",
    "UnderwritingOutputs",
]
