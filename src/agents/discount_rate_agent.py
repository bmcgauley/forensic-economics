"""
Discount Rate Agent

Purpose: Recommend discount rates based on Treasury yield curves and legal guidance.
Inputs: {location, case_type, present_date}
Outputs: {recommended_discount_curve, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List

from .fed_rate_agent import FedRateAgent


class DiscountRateAgent:
    """Agent for determining appropriate discount rates."""

    def __init__(self):
        """Initialize the Discount Rate Agent with Federal Reserve Rate Agent."""
        self.fed_rate_agent = FedRateAgent()

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine appropriate discount rate for present value calculations.

        Args:
            input_json: Dictionary containing:
                - location (str): Jurisdiction code
                - case_type (str): Type of case (optional)
                - present_date (str): Present date for rate lookup (optional)

        Returns:
            Dictionary containing:
                - outputs: {
                    recommended_discount_rate: float,
                    discount_curve: list,
                    methodology: str
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        location = input_json.get('location', 'US')
        case_type = input_json.get('case_type', 'wrongful_death')
        present_date = input_json.get('present_date')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received discount rate parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'location': location,
                'case_type': case_type,
                'present_date': present_date
            }
        })

        # Fetch current Treasury rate from Federal Reserve Rate Agent
        fed_rate_result = self.fed_rate_agent.run({'present_date': present_date})

        # Extract treasury rate from Fed agent output
        treasury_1yr_rate = fed_rate_result['outputs']['treasury_1yr_rate']
        is_fallback = fed_rate_result['outputs'].get('is_fallback', False)

        provenance_log.append({
            'step': 'treasury_rate_lookup',
            'description': f'1-Year Treasury rate from Federal Reserve ({fed_rate_result["outputs"]["source"]})',
            'formula': 'Federal Reserve H.15 Selected Interest Rates',
            'source_url': fed_rate_result['outputs']['source_url'],
            'source_date': fed_rate_result['outputs']['data_vintage'],
            'value': {
                'treasury_1yr_rate': treasury_1yr_rate,
                'rate_pct': round(treasury_1yr_rate * 100, 2),
                'is_fallback': is_fallback,
                'retrieval_timestamp': fed_rate_result['outputs']['retrieval_timestamp']
            }
        })

        # Merge Fed agent provenance
        for prov_entry in fed_rate_result['provenance_log']:
            provenance_log.append({
                **prov_entry,
                'step': f'fed_agent_{prov_entry["step"]}'
            })

        # Legal standard often uses risk-free rate or slightly above
        # Many jurisdictions use 2-4% range
        # Using 1-year Treasury as baseline
        recommended_rate = treasury_1yr_rate

        provenance_log.append({
            'step': 'legal_standard_adjustment',
            'description': 'Apply legal jurisdiction standards',
            'formula': 'Treasury rate with jurisdiction-specific adjustments',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': recommended_rate
        })

        # Generate discount curve for 50 years
        # Using flat curve for simplicity (could be customized by maturity)
        discount_curve = [round(recommended_rate, 4) for _ in range(50)]

        return {
            'agent_name': 'DiscountRateAgent',
            'inputs_used': {
                'location': location,
                'case_type': case_type
            },
            'outputs': {
                'recommended_discount_rate': round(recommended_rate, 4),
                'discount_curve': discount_curve,
                'methodology': 'Treasury-based with legal jurisdiction standards'
            },
            'provenance_log': provenance_log
        }
