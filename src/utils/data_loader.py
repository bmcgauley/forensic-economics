"""
Data Loader Utility for Static Data Sources

This module provides functions to load and cache static data files used by
the forensic economics agents, including Skoog Tables and CDC Life Tables.

Functions:
    load_skoog_tables() -> dict: Load worklife expectancy tables
    load_life_tables() -> dict: Load CDC life expectancy tables
    get_skoog_worklife(age, gender, education) -> float: Lookup worklife expectancy
    get_life_expectancy(age, gender) -> float: Lookup life expectancy
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

# Cache for loaded data files
_SKOOG_CACHE: Optional[Dict] = None
_LIFE_TABLES_CACHE: Optional[Dict] = None

# Data file paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SKOOG_FILE = DATA_DIR / "skoog_tables" / "skoog_2019_markov_model.json"
LIFE_TABLES_FILE = DATA_DIR / "life_tables" / "cdc_us_life_tables_2023.json"


def load_skoog_tables(force_reload: bool = False) -> Dict:
    """
    Load Skoog Tables data from JSON file with caching.

    The Skoog Tables contain worklife expectancy data based on Markov chain
    analysis of labor force participation (2012-2017 data).

    Args:
        force_reload: If True, bypass cache and reload from file

    Returns:
        Dictionary containing Skoog tables data with structure:
        {
            'metadata': {...},
            'worklife_expectancy': {
                'male': {'less_than_hs': {...}, ...},
                'female': {'less_than_hs': {...}, ...}
            }
        }

    Raises:
        FileNotFoundError: If Skoog tables file doesn't exist
        ValueError: If JSON file is invalid or missing required fields
    """
    global _SKOOG_CACHE

    # Return cached data if available
    if _SKOOG_CACHE is not None and not force_reload:
        return _SKOOG_CACHE

    # Check file exists
    if not SKOOG_FILE.exists():
        raise FileNotFoundError(
            f"Skoog tables file not found at: {SKOOG_FILE}\n"
            f"Expected location: data/skoog_tables/skoog_2019_markov_model.json"
        )

    # Load and validate JSON
    try:
        with open(SKOOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in Skoog tables file: {e}")

    # Validate required fields
    required_fields = ['metadata', 'worklife_expectancy']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Skoog tables missing required field: {field}")

    # Validate structure
    if 'male' not in data['worklife_expectancy'] or 'female' not in data['worklife_expectancy']:
        raise ValueError("Skoog tables must contain 'male' and 'female' worklife data")

    # Cache and return
    _SKOOG_CACHE = data
    return data


def load_life_tables(force_reload: bool = False) -> Dict:
    """
    Load CDC Life Tables data from JSON file with caching.

    The CDC Life Tables contain life expectancy data by age and gender from
    the National Vital Statistics Reports.

    Args:
        force_reload: If True, bypass cache and reload from file

    Returns:
        Dictionary containing CDC life tables data with structure:
        {
            'metadata': {...},
            'life_expectancy': {
                'male': {...},
                'female': {...}
            }
        }

    Raises:
        FileNotFoundError: If life tables file doesn't exist
        ValueError: If JSON file is invalid or missing required fields
    """
    global _LIFE_TABLES_CACHE

    # Return cached data if available
    if _LIFE_TABLES_CACHE is not None and not force_reload:
        return _LIFE_TABLES_CACHE

    # Check file exists
    if not LIFE_TABLES_FILE.exists():
        raise FileNotFoundError(
            f"CDC life tables file not found at: {LIFE_TABLES_FILE}\n"
            f"Expected location: data/life_tables/cdc_us_life_tables_2023.json"
        )

    # Load and validate JSON
    try:
        with open(LIFE_TABLES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in life tables file: {e}")

    # Validate required fields
    required_fields = ['metadata', 'life_expectancy']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Life tables missing required field: {field}")

    # Validate structure
    if 'male' not in data['life_expectancy'] or 'female' not in data['life_expectancy']:
        raise ValueError("Life tables must contain 'male' and 'female' life expectancy data")

    # Cache and return
    _LIFE_TABLES_CACHE = data
    return data


def get_skoog_worklife(age: float, gender: str, education: str) -> float:
    """
    Lookup worklife expectancy from Skoog Tables.

    Args:
        age: Person's age (can be decimal, will use interpolation)
        gender: 'male' or 'female' (case-insensitive)
        education: Education level (e.g., 'High School Graduate', 'Bachelor's Degree')

    Returns:
        Expected remaining worklife in years

    Raises:
        ValueError: If invalid gender or education level
        KeyError: If age not found in tables
    """
    data = load_skoog_tables()

    # Normalize gender
    gender = gender.lower()
    if gender not in ['male', 'female']:
        raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")

    # Map education level to Skoog table key
    education_mapping = {
        'less than high school': 'less_than_hs',
        'high school graduate': 'hs_graduate',
        'some college': 'some_college',
        "associate's degree": 'some_college',
        "bachelor's degree": 'bachelors_plus',
        "master's degree": 'bachelors_plus',
        'doctorate': 'bachelors_plus',
        'professional degree': 'bachelors_plus'
    }

    education_lower = education.lower()
    if education_lower not in education_mapping:
        # Default to high school graduate if unknown
        education_key = 'hs_graduate'
    else:
        education_key = education_mapping[education_lower]

    # Get the worklife table
    worklife_table = data['worklife_expectancy'][gender][education_key]

    # Handle integer age (exact lookup)
    if age == int(age):
        age_key = str(int(age))
        if age_key in worklife_table:
            return float(worklife_table[age_key])
        else:
            # Age out of range - return 0 for ages > 75
            if age > 75:
                return 0.0
            raise KeyError(f"Age {age} not found in Skoog tables")

    # Handle decimal age (linear interpolation)
    age_floor = int(age)
    age_ceil = age_floor + 1

    if str(age_floor) in worklife_table and str(age_ceil) in worklife_table:
        value_floor = float(worklife_table[str(age_floor)])
        value_ceil = float(worklife_table[str(age_ceil)])

        # Linear interpolation
        fraction = age - age_floor
        interpolated_value = value_floor + fraction * (value_ceil - value_floor)
        return interpolated_value
    else:
        # Age out of range
        if age > 75:
            return 0.0
        raise KeyError(f"Age {age} not found in Skoog tables for interpolation")


def get_life_expectancy(age: float, gender: str) -> float:
    """
    Lookup life expectancy from CDC Life Tables.

    Args:
        age: Person's age (can be decimal, will use interpolation)
        gender: 'male' or 'female' (case-insensitive)

    Returns:
        Expected remaining life years

    Raises:
        ValueError: If invalid gender
        KeyError: If age not found in tables
    """
    data = load_life_tables()

    # Normalize gender
    gender = gender.lower()
    if gender not in ['male', 'female']:
        raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")

    # Get the life expectancy table
    life_table = data['life_expectancy'][gender]

    # Handle integer age (exact lookup)
    if age == int(age):
        age_key = str(int(age))
        if age_key in life_table:
            return float(life_table[age_key])
        else:
            # Age out of range - return minimal value for ages > 100
            if age > 100:
                return 0.5
            raise KeyError(f"Age {age} not found in life tables")

    # Handle decimal age (linear interpolation)
    age_floor = int(age)
    age_ceil = age_floor + 1

    if str(age_floor) in life_table and str(age_ceil) in life_table:
        value_floor = float(life_table[str(age_floor)])
        value_ceil = float(life_table[str(age_ceil)])

        # Linear interpolation
        fraction = age - age_floor
        interpolated_value = value_floor + fraction * (value_ceil - value_floor)
        return interpolated_value
    else:
        # Age out of range
        if age > 100:
            return 0.5
        raise KeyError(f"Age {age} not found in life tables for interpolation")


def get_data_citations() -> Dict[str, str]:
    """
    Get citation information for all data sources.

    Returns:
        Dictionary with citation information for Skoog and CDC tables
    """
    citations = {}

    try:
        skoog_data = load_skoog_tables()
        citations['skoog'] = skoog_data['metadata']['citation']
    except Exception:
        citations['skoog'] = "Skoog tables not available"

    try:
        life_data = load_life_tables()
        citations['cdc'] = life_data['metadata']['citation']
    except Exception:
        citations['cdc'] = "CDC life tables not available"

    return citations


def validate_data_files() -> Dict[str, bool]:
    """
    Validate that all required data files exist and can be loaded.

    Returns:
        Dictionary with validation status for each data source
    """
    results = {
        'skoog_tables_exist': False,
        'skoog_tables_valid': False,
        'life_tables_exist': False,
        'life_tables_valid': False
    }

    # Check Skoog tables
    results['skoog_tables_exist'] = SKOOG_FILE.exists()
    if results['skoog_tables_exist']:
        try:
            load_skoog_tables(force_reload=True)
            results['skoog_tables_valid'] = True
        except Exception:
            pass

    # Check life tables
    results['life_tables_exist'] = LIFE_TABLES_FILE.exists()
    if results['life_tables_exist']:
        try:
            load_life_tables(force_reload=True)
            results['life_tables_valid'] = True
        except Exception:
            pass

    return results


if __name__ == "__main__":
    # Test data loading
    print("Testing data loader...")

    # Validate files
    validation = validate_data_files()
    print(f"\nValidation results:")
    for key, value in validation.items():
        status = "[OK]" if value else "[FAIL]"
        print(f"  {status} {key}: {value}")

    if all(validation.values()):
        print("\n[OK] All data files loaded successfully!")

        # Test lookups
        print("\nTest lookups:")
        worklife = get_skoog_worklife(40, 'male', "Bachelor's Degree")
        print(f"  Worklife (Male, 40, Bachelor's): {worklife} years")
        print(f"  Life expectancy (Male, 40): {get_life_expectancy(40, 'male')} years")
        print(f"  Life expectancy (Female, 40): {get_life_expectancy(40, 'female')} years")

        # Citations
        print("\nData sources:")
        citations = get_data_citations()
        for source, citation in citations.items():
            print(f"  {source}: {citation[:100]}...")
    else:
        print("\n[FAIL] Some data files failed validation")
