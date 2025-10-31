"""
Federal Reserve Rate Agent

Purpose: Provides current treasury/discount rates to DiscountRateAgent.
Inputs: {present_date}
Outputs: {treasury_1yr_rate, retrieval_timestamp, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any
import os
from dotenv import load_dotenv

from ..utils.external_apis import FedClient

# Load environment variables from .env file
load_dotenv()


class FedRateAgent:
    """Agent for fetching current Federal Reserve treasury rates."""

    def __init__(self):
        """Initialize the Federal Reserve Rate Agent with API client."""
        # Get FRED API key from environment
        api_key = os.getenv('FRED_API_KEY')
        self.fed_client = FedClient(api_key=api_key)

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch current 1-Year Treasury Constant Maturity Rate from Federal Reserve.

        Args:
            input_json: Dictionary containing:
                - present_date (str, optional): Date for which to fetch rates (ISO format)

        Returns:
            Dictionary containing:
                - agent_name: str
                - inputs_used: dict
                - outputs: {
                    treasury_1yr_rate: float (decimal, e.g., 0.0425 for 4.25%),
                    retrieval_timestamp: str (ISO format),
                    data_vintage: str (date of rate data),
                    source: str,
                    source_url: str
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        present_date = input_json.get('present_date')

        # Record input provenance
        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received Federal Reserve rate fetch parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'present_date': present_date
            }
        })

        # Fetch current Treasury rates from Federal Reserve H.15 via FRED API
        try:
            print(f"[FED_RATE_AGENT] Fetching Treasury rates from FRED API...")
            rate_data = self.fed_client.get_treasury_rates(use_fallback_on_error=True)
            print(f"[FED_RATE_AGENT] Received rate data: {rate_data.get('treasury_1yr_rate')}")

            treasury_1yr_rate = rate_data.get('treasury_1yr_rate')
            retrieval_timestamp = rate_data.get('retrieved_at')
            data_vintage = rate_data.get('data_vintage')
            source = rate_data.get('source')
            source_url = rate_data.get('source_url')

            # Check if we're using fallback
            is_fallback = 'warning' in rate_data

            provenance_log.append({
                'step': 'fed_rate_fetch',
                'description': f'Fetched 1-Year Treasury rate from Federal Reserve ({source})',
                'formula': 'Federal Reserve H.15 Selected Interest Rates - DGS1 series',
                'source_url': source_url,
                'source_date': data_vintage,
                'value': {
                    'treasury_1yr_rate': treasury_1yr_rate,
                    'rate_pct': round(treasury_1yr_rate * 100, 2),
                    'is_fallback': is_fallback,
                    'warning': rate_data.get('warning', None)
                }
            })

            # Add provenance from FedClient
            if 'provenance' in rate_data:
                fed_provenance = rate_data['provenance']
                provenance_log.append({
                    'step': 'api_provenance',
                    'description': 'Detailed API call information',
                    'formula': None,
                    'source_url': fed_provenance.get('source_url'),
                    'source_date': fed_provenance.get('data_vintage'),
                    'value': fed_provenance
                })

            return {
                'agent_name': 'FedRateAgent',
                'inputs_used': {
                    'present_date': present_date
                },
                'outputs': {
                    'treasury_1yr_rate': round(treasury_1yr_rate, 6),
                    'treasury_1yr_rate_pct': round(treasury_1yr_rate * 100, 2),
                    'retrieval_timestamp': retrieval_timestamp,
                    'data_vintage': data_vintage,
                    'source': source,
                    'source_url': source_url,
                    'is_fallback': is_fallback
                },
                'provenance_log': provenance_log
            }

        except Exception as e:
            # Log error and return fallback rate
            error_msg = f"Error fetching Federal Reserve rates: {str(e)}"
            provenance_log.append({
                'step': 'fed_rate_fetch_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'error': error_msg,
                    'fallback_rate': self.fed_client.fallback_rate
                }
            })

            # Return fallback rate
            fallback_rate = self.fed_client.fallback_rate
            return {
                'agent_name': 'FedRateAgent',
                'inputs_used': {
                    'present_date': present_date
                },
                'outputs': {
                    'treasury_1yr_rate': round(fallback_rate, 6),
                    'treasury_1yr_rate_pct': round(fallback_rate * 100, 2),
                    'retrieval_timestamp': datetime.utcnow().isoformat(),
                    'data_vintage': 'fallback',
                    'source': 'Federal Reserve H.15 (fallback cached rate)',
                    'source_url': 'https://www.federalreserve.gov/releases/h15/current/',
                    'is_fallback': True,
                    'error': error_msg
                },
                'provenance_log': provenance_log
            }


if __name__ == "__main__":
    """Test the Federal Reserve Rate Agent."""
    print("Testing Federal Reserve Rate Agent...")

    agent = FedRateAgent()

    # Test with no input (should use current date)
    print("\nTest 1: Fetch current Treasury rate")
    result = agent.run({})

    print(f"Agent: {result['agent_name']}")
    print(f"Treasury 1-Year Rate: {result['outputs']['treasury_1yr_rate_pct']}%")
    print(f"Rate (decimal): {result['outputs']['treasury_1yr_rate']}")
    print(f"Source: {result['outputs']['source']}")
    print(f"Data Vintage: {result['outputs']['data_vintage']}")
    print(f"Retrieved At: {result['outputs']['retrieval_timestamp']}")
    print(f"Is Fallback: {result['outputs']['is_fallback']}")

    print(f"\nProvenance Log ({len(result['provenance_log'])} entries):")
    for entry in result['provenance_log']:
        print(f"  - {entry['step']}: {entry['description']}")

    # Test with specific date
    print("\n\nTest 2: Fetch rate for specific date")
    result2 = agent.run({'present_date': '2025-01-15'})
    print(f"Treasury 1-Year Rate: {result2['outputs']['treasury_1yr_rate_pct']}%")
    print(f"Source: {result2['outputs']['source']}")
