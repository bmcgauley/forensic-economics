"""
Life Expectancy Agent

Purpose: Compute expected remaining years of life based on age, sex, and jurisdiction.
Inputs: {victim_age, victim_sex, location}
Outputs: {expected_remaining_years_by_age, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List


class LifeExpectancyAgent:
    """Agent for calculating life expectancy based on demographic data."""

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate life expectancy for the victim.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Age of victim
                - victim_sex (str): Sex (M/F/Other)
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    expected_remaining_years: float,
                    life_expectancy_at_birth: float,
                    expected_remaining_years_by_age: dict
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex')
        location = input_json.get('location', 'US')

        # Record input provenance
        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received victim demographics',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'location': location
            }
        })

        # TODO: Fetch actual life table data from SSA or national statistics
        # For now, using simplified placeholder calculations

        # Placeholder life expectancy calculation
        # Based on simplified actuarial tables
        base_life_expectancy = 78.5 if victim_sex == 'M' else 82.3

        provenance_log.append({
            'step': 'life_table_lookup',
            'description': f'Base life expectancy for {victim_sex} in {location}',
            'formula': 'SSA Life Table (placeholder)',
            'source_url': 'https://www.ssa.gov/oact/STATS/table4c6.html',
            'source_date': '2023-01-01',
            'value': base_life_expectancy
        })

        # Calculate remaining years
        expected_remaining_years = max(0, base_life_expectancy - victim_age)

        provenance_log.append({
            'step': 'remaining_years_calculation',
            'description': 'Calculate expected remaining years',
            'formula': 'base_life_expectancy - victim_age',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': expected_remaining_years
        })

        # Generate year-by-year survival probabilities (placeholder)
        remaining_by_age = {}
        for year_offset in range(int(expected_remaining_years) + 1):
            age = victim_age + year_offset
            remaining = max(0, expected_remaining_years - year_offset)
            remaining_by_age[age] = round(remaining, 2)

        return {
            'agent_name': 'LifeExpectancyAgent',
            'inputs_used': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'location': location
            },
            'outputs': {
                'expected_remaining_years': round(expected_remaining_years, 2),
                'life_expectancy_at_birth': base_life_expectancy,
                'expected_remaining_years_by_age': remaining_by_age
            },
            'provenance_log': provenance_log
        }
