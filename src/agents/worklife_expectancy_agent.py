"""
Worklife Expectancy Agent

Purpose: Compute expected worklife years based on occupation, age, education, and retirement norms.
Inputs: {victim_age, victim_sex, occupation, education, location}
Outputs: {worklife_years, retirement_age, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List

from .skoog_table_agent import SkoogTableAgent


class WorklifeExpectancyAgent:
    """Agent for calculating worklife expectancy."""

    def __init__(self):
        """Initialize the Worklife Expectancy Agent with Skoog Table Agent."""
        self.skoog_agent = SkoogTableAgent()

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate worklife expectancy for the victim.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Current age
                - victim_sex (str): Gender (M/F/Male/Female)
                - occupation (str): Occupation or SOC code
                - education (str): Education level
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    worklife_years: float,
                    retirement_age: int (estimated),
                    worklife_years_by_age: dict
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex', 'male')
        occupation = input_json.get('occupation')
        education = input_json.get('education')
        location = input_json.get('location', 'US')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received employment parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'occupation': occupation,
                'education': education,
                'location': location
            }
        })

        # Fetch worklife expectancy from Skoog Table Agent
        skoog_result = self.skoog_agent.run({
            'age': victim_age,
            'gender': victim_sex,
            'education': education
        })

        # Extract worklife expectancy from Skoog agent output
        worklife_years = skoog_result['outputs']['worklife_expectancy_years']
        skoog_source = skoog_result['outputs'].get('table_source', 'Skoog Tables')

        provenance_log.append({
            'step': 'skoog_table_lookup',
            'description': f'Worklife expectancy from {skoog_source}',
            'formula': 'Markov Model of Labor Force Activity (Skoog, Ciecka, Krueger 2019)',
            'source_url': skoog_result['outputs'].get('source_url'),
            'source_date': skoog_result['outputs'].get('source_year'),
            'value': {
                'worklife_years': worklife_years,
                'source': skoog_source
            }
        })

        # Merge Skoog agent provenance
        for prov_entry in skoog_result['provenance_log']:
            provenance_log.append({
                **prov_entry,
                'step': f'skoog_agent_{prov_entry["step"]}'
            })

        # Estimate retirement age (current age + worklife years)
        retirement_age = int(victim_age + worklife_years)

        provenance_log.append({
            'step': 'worklife_calculation',
            'description': 'Calculate expected worklife years from Skoog tables',
            'formula': 'Direct lookup from Skoog Markov model',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'worklife_years': worklife_years,
                'estimated_retirement_age': retirement_age
            }
        })

        # Generate year-by-year worklife expectancy
        worklife_by_age = {}
        for year_offset in range(int(worklife_years) + 1):
            age = victim_age + year_offset
            remaining_worklife = max(0, worklife_years - year_offset)
            worklife_by_age[age] = round(remaining_worklife, 2)

        return {
            'agent_name': 'WorklifeExpectancyAgent',
            'inputs_used': {
                'victim_age': victim_age,
                'occupation': occupation,
                'education': education,
                'location': location
            },
            'outputs': {
                'worklife_years': round(worklife_years, 2),
                'retirement_age': retirement_age,
                'worklife_years_by_age': worklife_by_age
            },
            'provenance_log': provenance_log
        }
