"""
Skoog Table Agent

Purpose: Provides actuarial worklife data to WorklifeExpectancyAgent.
Inputs: {age, gender, education}
Outputs: {worklife_expectancy_years, table_source, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from ..utils.data_loader import (
    load_skoog_tables,
    get_skoog_worklife,
    get_data_citations
)


class SkoogTableAgent:
    """Agent for fetching worklife expectancy from Skoog Tables."""

    def __init__(self):
        """Initialize the Skoog Table Agent."""
        # Preload tables to ensure they're available
        try:
            self.skoog_data = load_skoog_tables()
            self.tables_available = True
        except Exception as e:
            self.skoog_data = None
            self.tables_available = False
            self.load_error = str(e)

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch worklife expectancy from Skoog Tables.

        Args:
            input_json: Dictionary containing:
                - age (float): Person's age
                - gender (str): 'male', 'female', or 'M', 'F'
                - education (str): Education level (e.g., "Bachelor's Degree")

        Returns:
            Dictionary containing:
                - agent_name: str
                - inputs_used: dict
                - outputs: {
                    worklife_expectancy_years: float,
                    table_source: str,
                    source_citation: str,
                    source_year: str
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        age = input_json.get('age')
        gender = input_json.get('gender', 'male')
        education = input_json.get('education', 'High School Graduate')

        # Normalize gender input
        if gender.upper() in ['M', 'MALE']:
            gender = 'male'
        elif gender.upper() in ['F', 'FEMALE']:
            gender = 'female'

        # Record input provenance
        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received Skoog table lookup parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'age': age,
                'gender': gender,
                'education': education
            }
        })

        # Check if tables are available
        if not self.tables_available:
            error_msg = f"Skoog tables not available: {self.load_error}"
            provenance_log.append({
                'step': 'skoog_table_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': error_msg}
            })

            return {
                'agent_name': 'SkoogTableAgent',
                'inputs_used': {
                    'age': age,
                    'gender': gender,
                    'education': education
                },
                'outputs': {
                    'worklife_expectancy_years': 0.0,
                    'table_source': 'Skoog Tables (unavailable)',
                    'source_citation': None,
                    'source_year': None,
                    'error': error_msg
                },
                'provenance_log': provenance_log
            }

        # Fetch worklife expectancy from Skoog Tables
        try:
            worklife_years = get_skoog_worklife(age, gender, education)

            # Get citation information
            metadata = self.skoog_data.get('metadata', {})
            citation = metadata.get('citation', 'Skoog, Ciecka, & Krueger (2019)')
            source_url = metadata.get('source_url', 'https://doi.org/10.5384/28-1-2')
            publication_year = metadata.get('publication_year', '2019')

            provenance_log.append({
                'step': 'skoog_table_lookup',
                'description': f'Looked up worklife expectancy for {gender}, age {age}, education {education}',
                'formula': 'Markov Model of Labor Force Activity (Skoog, Ciecka, Krueger 2019)',
                'source_url': source_url,
                'source_date': publication_year,
                'value': {
                    'worklife_expectancy_years': worklife_years,
                    'age': age,
                    'gender': gender,
                    'education': education
                }
            })

            # Add metadata provenance
            provenance_log.append({
                'step': 'data_source_metadata',
                'description': 'Skoog Tables metadata',
                'formula': None,
                'source_url': source_url,
                'source_date': publication_year,
                'value': {
                    'citation': citation,
                    'publication': metadata.get('publication', 'Journal of Forensic Economics'),
                    'volume_issue': metadata.get('volume_issue', '28(1-2)'),
                    'pages': metadata.get('pages', '15-108'),
                    'data_period': metadata.get('data_period', '2012-2017')
                }
            })

            return {
                'agent_name': 'SkoogTableAgent',
                'inputs_used': {
                    'age': age,
                    'gender': gender,
                    'education': education
                },
                'outputs': {
                    'worklife_expectancy_years': round(worklife_years, 2),
                    'table_source': 'Skoog, Ciecka, & Krueger (2019) - Markov Model of Labor Force Activity',
                    'source_citation': citation,
                    'source_year': publication_year,
                    'source_url': source_url,
                    'publication': metadata.get('publication', 'Journal of Forensic Economics')
                },
                'provenance_log': provenance_log
            }

        except KeyError as e:
            # Age not found in tables
            error_msg = f"Age {age} not found in Skoog tables: {str(e)}"
            provenance_log.append({
                'step': 'skoog_table_lookup_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'error': error_msg,
                    'age': age,
                    'gender': gender,
                    'education': education
                }
            })

            # Return 0 for out-of-range ages
            return {
                'agent_name': 'SkoogTableAgent',
                'inputs_used': {
                    'age': age,
                    'gender': gender,
                    'education': education
                },
                'outputs': {
                    'worklife_expectancy_years': 0.0,
                    'table_source': 'Skoog Tables (age out of range)',
                    'source_citation': None,
                    'source_year': None,
                    'error': error_msg
                },
                'provenance_log': provenance_log
            }

        except ValueError as e:
            # Invalid gender or education
            error_msg = f"Invalid input parameters: {str(e)}"
            provenance_log.append({
                'step': 'skoog_table_validation_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'error': error_msg,
                    'age': age,
                    'gender': gender,
                    'education': education
                }
            })

            return {
                'agent_name': 'SkoogTableAgent',
                'inputs_used': {
                    'age': age,
                    'gender': gender,
                    'education': education
                },
                'outputs': {
                    'worklife_expectancy_years': 0.0,
                    'table_source': 'Skoog Tables (validation error)',
                    'source_citation': None,
                    'source_year': None,
                    'error': error_msg
                },
                'provenance_log': provenance_log
            }

        except Exception as e:
            # General error
            error_msg = f"Error fetching Skoog table data: {str(e)}"
            provenance_log.append({
                'step': 'skoog_table_general_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': error_msg}
            })

            return {
                'agent_name': 'SkoogTableAgent',
                'inputs_used': {
                    'age': age,
                    'gender': gender,
                    'education': education
                },
                'outputs': {
                    'worklife_expectancy_years': 0.0,
                    'table_source': 'Skoog Tables (error)',
                    'source_citation': None,
                    'source_year': None,
                    'error': error_msg
                },
                'provenance_log': provenance_log
            }


if __name__ == "__main__":
    """Test the Skoog Table Agent."""
    print("Testing Skoog Table Agent...")

    agent = SkoogTableAgent()

    if not agent.tables_available:
        print(f"ERROR: Skoog tables not available - {agent.load_error}")
        exit(1)

    # Test cases
    test_cases = [
        {'age': 40, 'gender': 'male', 'education': "Bachelor's Degree"},
        {'age': 35, 'gender': 'female', 'education': 'High School Graduate'},
        {'age': 50.5, 'gender': 'male', 'education': "Master's Degree"},
        {'age': 60, 'gender': 'female', 'education': 'Some College'},
        {'age': 25, 'gender': 'male', 'education': 'Less than High School'}
    ]

    print("\nRunning test cases:")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\nTest {i}: Age={test_input['age']}, Gender={test_input['gender']}, Education={test_input['education']}")
        result = agent.run(test_input)

        if 'error' in result['outputs']:
            print(f"  ERROR: {result['outputs']['error']}")
        else:
            print(f"  Worklife Expectancy: {result['outputs']['worklife_expectancy_years']} years")
            print(f"  Source: {result['outputs']['table_source']}")
            print(f"  Citation: {result['outputs']['source_citation']}")

    # Test edge cases
    print("\n\nEdge cases:")

    # Out of range age
    print("\nTest: Age out of range (80)")
    result = agent.run({'age': 80, 'gender': 'male', 'education': "Bachelor's Degree"})
    print(f"  Worklife: {result['outputs']['worklife_expectancy_years']} years")
    if 'error' in result['outputs']:
        print(f"  (Expected behavior: {result['outputs']['error']})")

    # Invalid gender
    print("\nTest: Normalized gender ('M' -> 'male')")
    result = agent.run({'age': 40, 'gender': 'M', 'education': "Bachelor's Degree"})
    print(f"  Worklife: {result['outputs']['worklife_expectancy_years']} years")
    print(f"  Gender used: {result['inputs_used']['gender']}")
