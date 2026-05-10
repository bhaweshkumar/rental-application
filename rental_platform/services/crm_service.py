"""CRM persistence service — deal save/load."""
import json
from dataclasses import asdict, is_dataclass
from typing import List

from rental_platform.models import (
    AcquisitionDetails,
    CapitalMarketsDetails,
    DealProfile,
    ProfitFirstInputs,
    ProfitFirstOutputs,
    ProformaAssumptions,
    PropertyDetails,
    TaxOptimizationInputs,
    TaxOptimizationOutputs,
    UnderwritingInputs,
    UnderwritingOutputs,
)


class DataclassJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder for dataclasses."""
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


def save_deals(deals: List[DealProfile], filepath: str) -> None:
    """Saves a list of DealProfile objects to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(deals, f, cls=DataclassJSONEncoder, indent=4)


def load_deals(filepath: str) -> List[DealProfile]:
    """Loads a list of DealProfile objects from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        deals = []
        for d in data:
            deal = DealProfile(
                id=d.get("id"),
                status=d.get("status", "Analysis"),
                property_details=PropertyDetails(**d.get("property_details", {})),
                acquisition_details=AcquisitionDetails(**d.get("acquisition_details", {})),
                capital_markets_details=CapitalMarketsDetails(**d.get("capital_markets_details", {})),
                underwriting_inputs=UnderwritingInputs(**d.get("underwriting_inputs", {})),
                underwriting_outputs=UnderwritingOutputs(**d.get("underwriting_outputs", {})),
                proforma_assumptions=ProformaAssumptions(**d.get("proforma_assumptions", {})),
                tax_optimization_inputs=TaxOptimizationInputs(**d.get("tax_optimization_inputs", {})),
                tax_optimization_outputs=TaxOptimizationOutputs(**d.get("tax_optimization_outputs", {})),
                profit_first_inputs=ProfitFirstInputs(**d.get("profit_first_inputs", {})),
                profit_first_outputs=ProfitFirstOutputs(**d.get("profit_first_outputs", {})),
                other_details=d.get("other_details", {}),
            )
            deals.append(deal)
        return deals
    except (FileNotFoundError, json.JSONDecodeError):
        return []
