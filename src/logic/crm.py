import json
from typing import List
from dataclasses import asdict, is_dataclass

try:
    from src.shared.models import (  # type: ignore
        AcquisitionDetails,
        CapitalMarketsDetails,
        DealProfile,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        PropertyDetails,
        ProformaAssumptions,
        TaxOptimizationInputs,
        TaxOptimizationOutputs,
        UnderwritingInputs,
        UnderwritingOutputs,
    )
except ImportError:
    from shared.models import (  # type: ignore
        AcquisitionDetails,
        CapitalMarketsDetails,
        DealProfile,
        ProfitFirstInputs,
        ProfitFirstOutputs,
        PropertyDetails,
        ProformaAssumptions,
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

def save_deals(deals: List[DealProfile], filepath: str):
    """Saves a list of DealProfile objects to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(deals, f, cls=DataclassJSONEncoder, indent=4)

def load_deals(filepath: str) -> List[DealProfile]:
    """
    Loads a list of DealProfile objects from a JSON file,
    reconstructing the nested dataclass structure.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            deals = []
            for deal_dict in data:
                # Reconstruct nested dataclasses from their dictionary representations
                deal = DealProfile(
                    id=deal_dict.get("id"),
                    status=deal_dict.get("status", "Analysis"),
                    property_details=PropertyDetails(**deal_dict.get("property_details", {})),
                    acquisition_details=AcquisitionDetails(**deal_dict.get("acquisition_details", {})),
                    capital_markets_details=CapitalMarketsDetails(**deal_dict.get("capital_markets_details", {})),
                    underwriting_inputs=UnderwritingInputs(**deal_dict.get("underwriting_inputs", {})),
                    underwriting_outputs=UnderwritingOutputs(**deal_dict.get("underwriting_outputs", {})),
                    proforma_assumptions=ProformaAssumptions(**deal_dict.get("proforma_assumptions", {})),
                    tax_optimization_inputs=TaxOptimizationInputs(**deal_dict.get("tax_optimization_inputs", {})),
                    tax_optimization_outputs=TaxOptimizationOutputs(**deal_dict.get("tax_optimization_outputs", {})),
                    profit_first_inputs=ProfitFirstInputs(**deal_dict.get("profit_first_inputs", {})),
                    profit_first_outputs=ProfitFirstOutputs(**deal_dict.get("profit_first_outputs", {})),
                    other_details=deal_dict.get("other_details", {}),
                )
                deals.append(deal)
            return deals
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/corrupt, return an empty list
        return []
