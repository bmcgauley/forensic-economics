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

    Parses the actual Skoog JSON structure with Table_36 (men) and Table_37 (women)
    and transforms it into the expected structure.

    Args:
        force_reload: If True, bypass cache and reload from file

    Returns:
        Dictionary containing Skoog tables data with structure:
        {
            'metadata': {...},
            'worklife_expectancy': {
                'male': {
                    'less_than_hs': {age: years, ...},
                    'hs_graduate': {age: years, ...},
                    'some_college': {age: years, ...},
                    'bachelors_plus': {age: years, ...}
                },
                'female': {...}
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
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in Skoog tables file: {e}")

    # Check if data is already in transformed format
    if 'worklife_expectancy' in raw_data and 'metadata' in raw_data:
        # Data is already transformed, use it directly
        _SKOOG_CACHE = raw_data
        return raw_data

    # Helper function to extract first number from string like "21.04 20.99 0.25"
    def extract_wle(value):
        if value is None or (isinstance(value, float) and str(value) == 'nan'):
            return None
        value_str = str(value).strip()
        if not value_str or value_str == 'NaN':
            return None
        # Split by space and take first value
        parts = value_str.split()
        if parts:
            try:
                return float(parts[0])
            except ValueError:
                return None
        return None

    # Parse male worklife table (Table_36)
    men_table = raw_data.get('Table_36_Men_Worklife_Expectancy_Part1', {})
    men_data = {
        'less_than_hs': {},
        'hs_graduate': {},
        'some_college': {},
        'bachelors_plus': {}
    }

    for row in men_table.get('data', []):
        age = row.get('Unnamed: 0')
        if age == 'Age' or not age:
            continue

        try:
            age_int = str(int(float(age)))
        except (ValueError, TypeError):
            continue

        # Extract WLE for each education level
        # Less than HS: "0-12 Years of Education"
        wle = extract_wle(row.get('0-12 Years of Education'))
        if wle is not None:
            men_data['less_than_hs'][age_int] = wle

        # High School: "High School" column
        wle = extract_wle(row.get('Unnamed: 1'))  # This column has HS WLE
        if wle is not None:
            men_data['hs_graduate'][age_int] = wle

        # Some College: "Some College" column
        wle = extract_wle(row.get('Some College'))
        if wle is not None:
            men_data['some_college'][age_int] = wle

        # Bachelor's+: "BA Degree" column
        wle = extract_wle(row.get('Unnamed: 4'))  # This column has BA WLE
        if wle is not None:
            men_data['bachelors_plus'][age_int] = wle

    # Parse female worklife table (Table_37)
    women_table = raw_data.get('Table_37_Women_Worklife_Expectancy', {})
    women_data = {
        'less_than_hs': {},
        'hs_graduate': {},
        'some_college': {},
        'bachelors_plus': {}
    }

    for row in women_table.get('data', []):
        age = row.get('Unnamed: 0')
        if age == 'Age' or not age:
            continue

        try:
            age_int = str(int(float(age)))
        except (ValueError, TypeError):
            continue

        # Extract WLE for each education level (same column structure as men)
        wle = extract_wle(row.get('0-12 Years of Education'))
        if wle is not None:
            women_data['less_than_hs'][age_int] = wle

        wle = extract_wle(row.get('Unnamed: 1'))
        if wle is not None:
            women_data['hs_graduate'][age_int] = wle

        wle = extract_wle(row.get('Some College'))
        if wle is not None:
            women_data['some_college'][age_int] = wle

        wle = extract_wle(row.get('Unnamed: 4'))
        if wle is not None:
            women_data['bachelors_plus'][age_int] = wle

    # Validate women's data is present
    if not women_data['less_than_hs']:
        raise ValueError(
            "Women's worklife table is missing or incomplete in JSON. "
            "For litigation accuracy, gender-specific data must be present. "
            "Run data/skoog_tables/create_proper_women_data.py to generate proper data."
        )

    # Create metadata
    metadata = {
        'title': 'Skoog Worklife Expectancy Tables 2019',
        'description': 'Markov Model of Labor Force Activity 2012-17',
        'source': 'Journal of Forensic Economics, Vol. 28(1-2), pp. 15-108',
        'year': 2019,
        'authors': 'Skoog, G.R., Ciecka, J.E., & Krueger, K.V.',
        'citation': 'Skoog, G.R., Ciecka, J.E., & Krueger, K.V. (2019). Markov Model of Labor Force Activity 2012-17. Journal of Forensic Economics, 28(1-2), 15-108.',
        'data_period': '2012-2017'
    }

    # Transform into expected structure
    transformed_data = {
        'metadata': metadata,
        'worklife_expectancy': {
            'male': men_data,
            'female': women_data
        }
    }

    # Cache and return
    _SKOOG_CACHE = transformed_data
    return transformed_data


def load_cdc_life_tables(force_reload: bool = False) -> Dict:
    """
    Load CDC Life Tables data from JSON file with caching.

    Parses the actual CDC JSON structure with Table_1_US_Life_Table_2023 format
    and transforms it into the expected structure.

    Args:
        force_reload: If True, bypass cache and reload from file

    Returns:
        Dictionary containing CDC life tables data with structure:
        {
            'metadata': {...},
            'life_expectancy': {
                'male': {age: remaining_years, ...},
                'female': {age: remaining_years, ...}
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
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in life tables file: {e}")

    # Parse the actual CDC structure
    if 'Table_1_US_Life_Table_2023' not in raw_data:
        raise ValueError("CDC life tables missing 'Table_1_US_Life_Table_2023' table")

    table = raw_data['Table_1_US_Life_Table_2023']

    # Extract metadata
    metadata = {
        'title': table.get('title', 'CDC US Life Tables 2023'),
        'description': table.get('description', ''),
        'source': table.get('source', 'CDC National Vital Statistics System'),
        'year': table.get('year', 2023),
        'publication_date': '2025-07-15',
        'citation': f"{table.get('description', 'CDC Life Tables')} - {table.get('source', 'NCHS')}"
    }

    # Parse life expectancy data from rows
    life_expectancy_dict = {}
    for row in table.get('data', []):
        age = row.get('Age_Start')
        ex = row.get('ex_Life_Expectancy')

        if age is not None and ex is not None:
            # Clean the values (remove commas if present)
            age_int = str(age).replace(',', '')
            ex_float = str(ex).replace(',', '')
            life_expectancy_dict[age_int] = float(ex_float)

    # Transform into expected structure
    # Since this is combined data, use same values for both genders
    # (Real CDC publishes separate male/female tables, but if we have combined, use it)
    transformed_data = {
        'metadata': metadata,
        'life_expectancy': {
            'male': life_expectancy_dict.copy(),
            'female': life_expectancy_dict.copy()
        }
    }

    # Cache and return
    _LIFE_TABLES_CACHE = transformed_data
    return transformed_data


def load_life_tables(force_reload: bool = False) -> Dict:
    """
    Alias for load_cdc_life_tables() for backward compatibility.
    """
    return load_cdc_life_tables(force_reload=force_reload)


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
        'less_than_high_school': 'less_than_hs',
        'high school graduate': 'hs_graduate',
        'high school': 'hs_graduate',
        'hs_graduate': 'hs_graduate',
        'some college': 'some_college',
        'some_college': 'some_college',
        "associate's degree": 'some_college',
        'associate degree': 'some_college',
        'associates': 'some_college',
        "bachelor's degree": 'bachelors_plus',
        'bachelor degree': 'bachelors_plus',
        'bachelors degree': 'bachelors_plus',
        'bachelors': 'bachelors_plus',
        "master's degree": 'bachelors_plus',
        'master degree': 'bachelors_plus',
        'masters degree': 'bachelors_plus',
        'masters': 'bachelors_plus',
        'doctorate': 'bachelors_plus',
        'phd': 'bachelors_plus',
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
