"""
Person Investigation Agent

Purpose: Validate and enrich initial person data entry
Inputs: Raw victim data from user intake
Outputs: Validated and normalized person data
Role: Data Validation & Enrichment

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List
import re


class PersonInvestigationAgent:
    """Agent for validating and enriching person investigation data."""

    # Education level normalization mapping
    EDUCATION_NORMALIZATION = {
        'less than high school': 'less_than_high_school',
        'less_than_high_school': 'less_than_high_school',
        'high school': 'high_school',
        'high_school': 'high_school',
        'hs': 'high_school',
        'some college': 'some_college',
        'some_college': 'some_college',
        'bachelors': 'bachelors',
        "bachelor's": 'bachelors',
        'bachelor': 'bachelors',
        'ba': 'bachelors',
        'bs': 'bachelors',
        'masters': 'masters',
        "master's": 'masters',
        'master': 'masters',
        'ma': 'masters',
        'ms': 'masters',
        'mba': 'masters',
        'doctorate': 'doctorate',
        'doctoral': 'doctorate',
        'phd': 'doctorate',
        'md': 'doctorate',
        'jd': 'doctorate'
    }

    def __init__(self):
        """Initialize the agent."""
        pass

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize person data.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Age of victim
                - victim_sex (str): Gender (M/F/male/female)
                - occupation (str): Occupation or SOC code
                - education (str): Education level
                - location (str): Jurisdiction code
                - salary (float): Annual salary
                - present_date (str, optional): Present date

        Returns:
            Dictionary containing:
                - agent_name: 'PersonInvestigationAgent'
                - inputs_used: Original input data
                - outputs: {
                    validated_age: int,
                    normalized_sex: str (M or F),
                    occupation: str,
                    occupation_soc_code: str or None,
                    normalized_education: str,
                    location_jurisdiction: str,
                    validated_salary: float,
                    validation_notes: List[str],
                    data_quality_score: str (high/medium/low)
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex', '').lower().strip()
        occupation = input_json.get('occupation', '').strip()
        education = input_json.get('education', '').lower().strip()
        location = input_json.get('location', 'US').strip()
        salary = input_json.get('salary')
        present_date = input_json.get('present_date')

        provenance_log.append({
            'step': 'input_received',
            'description': 'Raw person data received for validation',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'occupation': occupation,
                'education': education,
                'location': location,
                'salary': salary,
                'present_date': present_date
            }
        })

        validation_notes = []
        data_quality_issues = 0

        # === 1. Normalize and validate sex ===
        if victim_sex in ['m', 'male', 'man']:
            normalized_sex = 'M'
        elif victim_sex in ['f', 'female', 'woman']:
            normalized_sex = 'F'
        else:
            normalized_sex = 'M'  # Default
            validation_notes.append(f"Invalid sex '{victim_sex}', defaulting to 'M'")
            data_quality_issues += 1

        provenance_log.append({
            'step': 'sex_normalization',
            'description': f'Normalized sex from "{victim_sex}" to "{normalized_sex}"',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'original': victim_sex,
                'normalized': normalized_sex
            }
        })

        # === 2. Validate age ===
        age_valid = True
        if victim_age is None:
            validation_notes.append("Age is missing")
            data_quality_issues += 2
            age_valid = False
        elif not isinstance(victim_age, (int, float)):
            validation_notes.append(f"Age '{victim_age}' is not a number")
            data_quality_issues += 2
            age_valid = False
        elif victim_age < 0 or victim_age > 120:
            validation_notes.append(f"Age {victim_age} is out of valid range (0-120)")
            data_quality_issues += 2
            age_valid = False
        elif victim_age < 16:
            validation_notes.append(f"Age {victim_age} is below typical working age (16+)")
            data_quality_issues += 1

        provenance_log.append({
            'step': 'age_validation',
            'description': 'Validated victim age',
            'formula': 'Age must be between 0 and 120',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'age': victim_age,
                'valid': age_valid
            }
        })

        # === 3. Normalize education ===
        normalized_education = self.EDUCATION_NORMALIZATION.get(education.lower())

        if normalized_education is None:
            # Try partial matching
            for key, value in self.EDUCATION_NORMALIZATION.items():
                if key in education.lower() or education.lower() in key:
                    normalized_education = value
                    validation_notes.append(f"Education '{education}' fuzzy-matched to '{normalized_education}'")
                    break

            if normalized_education is None:
                normalized_education = 'high_school'  # Default
                validation_notes.append(f"Unknown education '{education}', defaulting to 'high_school'")
                data_quality_issues += 1

        provenance_log.append({
            'step': 'education_normalization',
            'description': f'Normalized education from "{education}" to "{normalized_education}"',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'original': education,
                'normalized': normalized_education
            }
        })

        # === 4. Parse SOC code from occupation ===
        soc_code = None
        soc_pattern = r'\b\d{2}-\d{4}\b'  # Format: XX-XXXX

        if re.search(soc_pattern, occupation):
            match = re.search(soc_pattern, occupation)
            soc_code = match.group(0)
            validation_notes.append(f"Found SOC code in occupation: {soc_code}")

        provenance_log.append({
            'step': 'occupation_parsing',
            'description': 'Parsed occupation for SOC code',
            'formula': 'Regex pattern: XX-XXXX',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'occupation': occupation,
                'soc_code': soc_code
            }
        })

        # === 5. Validate salary ===
        salary_valid = True
        if salary is None:
            validation_notes.append("Salary is missing")
            data_quality_issues += 2
            salary_valid = False
        elif not isinstance(salary, (int, float)):
            validation_notes.append(f"Salary '{salary}' is not a number")
            data_quality_issues += 2
            salary_valid = False
        elif salary <= 0:
            validation_notes.append(f"Salary {salary} is not positive")
            data_quality_issues += 2
            salary_valid = False
        elif salary < 15000:
            validation_notes.append(f"Salary {salary} is below federal minimum wage equivalent (~$15,000/year)")
            data_quality_issues += 1
        elif salary > 1000000:
            validation_notes.append(f"Salary {salary} is unusually high (>$1M/year), verify accuracy")
            data_quality_issues += 1

        provenance_log.append({
            'step': 'salary_validation',
            'description': 'Validated salary amount',
            'formula': 'Salary must be positive and reasonable',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'salary': salary,
                'valid': salary_valid
            }
        })

        # === 6. Validate location ===
        if not location or len(location) < 2:
            validation_notes.append(f"Location '{location}' is invalid or missing, defaulting to 'US'")
            location = 'US'
            data_quality_issues += 1

        # === 7. Calculate data quality score ===
        if data_quality_issues == 0:
            data_quality_score = 'high'
        elif data_quality_issues <= 2:
            data_quality_score = 'medium'
        else:
            data_quality_score = 'low'

        provenance_log.append({
            'step': 'data_quality_assessment',
            'description': 'Assessed overall data quality',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'data_quality_score': data_quality_score,
                'issues_found': data_quality_issues,
                'validation_notes_count': len(validation_notes)
            }
        })

        # Final validation summary
        provenance_log.append({
            'step': 'validation_complete',
            'description': 'Person data validation and normalization complete',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'normalized_sex': normalized_sex,
                'normalized_education': normalized_education,
                'soc_code': soc_code,
                'data_quality_score': data_quality_score
            }
        })

        return {
            'agent_name': 'PersonInvestigationAgent',
            'inputs_used': input_json,
            'outputs': {
                'validated_age': victim_age,
                'normalized_sex': normalized_sex,
                'occupation': occupation,
                'occupation_soc_code': soc_code,
                'normalized_education': normalized_education,
                'location_jurisdiction': location,
                'validated_salary': salary,
                'validation_notes': validation_notes,
                'data_quality_score': data_quality_score
            },
            'provenance_log': provenance_log
        }
