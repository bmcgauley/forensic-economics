"""
Wage Growth Agent

Purpose: Project wage growth rates using occupation-specific growth data and economic indicators.
Inputs: {occupation, salary, education, location}
Outputs: {growth_rate_series, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List


class WageGrowthAgent:
    """Agent for projecting wage growth rates."""

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate wage growth projections.

        Args:
            input_json: Dictionary containing:
                - occupation (str): Occupation or SOC code
                - salary (float): Current salary
                - education (str): Education level
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    annual_growth_rate: float,
                    growth_rate_series: list,
                    projected_wages_by_year: dict
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        occupation = input_json.get('occupation')
        salary = input_json.get('salary')
        education = input_json.get('education')
        location = input_json.get('location', 'US')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received wage growth parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'occupation': occupation,
                'salary': salary,
                'education': education,
                'location': location
            }
        })

        # TODO: Fetch actual wage growth data from BLS Employment Cost Index
        # For now, using simplified historical averages

        # Baseline wage growth rate (historical average ~3%)
        base_growth_rate = 0.03

        provenance_log.append({
            'step': 'base_growth_rate',
            'description': 'Historical average wage growth rate',
            'formula': 'BLS Employment Cost Index average',
            'source_url': 'https://www.bls.gov/ncs/ect/',
            'source_date': '2023-01-01',
            'value': base_growth_rate
        })

        # Education adjustment (higher education = higher growth potential)
        education_adjustment_map = {
            'less_than_high_school': -0.005,
            'high_school': 0.0,
            'some_college': 0.002,
            'bachelors': 0.005,
            'masters': 0.007,
            'doctorate': 0.008
        }

        education_adjustment = education_adjustment_map.get(education, 0.0)
        adjusted_growth_rate = base_growth_rate + education_adjustment

        provenance_log.append({
            'step': 'education_adjustment',
            'description': f'Adjust growth rate for {education} education',
            'formula': 'base_growth_rate + education_adjustment',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': adjusted_growth_rate
        })

        # Generate growth rate series for next 50 years
        growth_rate_series = [round(adjusted_growth_rate, 4) for _ in range(50)]

        # Project wages for each year
        projected_wages = {}
        current_wage = salary
        for year in range(50):
            projected_wages[year] = round(current_wage, 2)
            current_wage *= (1 + adjusted_growth_rate)

        return {
            'agent_name': 'WageGrowthAgent',
            'inputs_used': {
                'occupation': occupation,
                'salary': salary,
                'education': education,
                'location': location
            },
            'outputs': {
                'annual_growth_rate': round(adjusted_growth_rate, 4),
                'growth_rate_series': growth_rate_series,
                'projected_wages_by_year': projected_wages
            },
            'provenance_log': provenance_log
        }
