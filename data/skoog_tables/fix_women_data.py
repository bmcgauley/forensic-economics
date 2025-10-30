#!/usr/bin/env python3
"""
Fix Women's Worklife Data with Linear Interpolation

CRITICAL: For active litigation use

The Skoog 2019 tables have ages 41-51 missing from the women's dataset.
This script fills those gaps using LINEAR INTERPOLATION, which is the
standard accepted practice in forensic economics when specific age data
is unavailable.

Interpolation formula:
WLE(age) = WLE(40) + (age-40)/(52-40) * (WLE(52) - WLE(40))

This method is:
- Mathematically sound
- Commonly accepted in forensic economics
- Conservative (follows the trend between known data points)
- Properly documented for legal review

Usage:
    python fix_women_data.py
"""

import json
import shutil
from pathlib import Path
from typing import Dict


def interpolate_wle(age: int, age_low: int, age_high: int,
                    wle_low: float, wle_high: float) -> float:
    """
    Linear interpolation for worklife expectancy.

    Args:
        age: Target age to interpolate
        age_low: Lower bound age (known)
        age_high: Upper bound age (known)
        wle_low: WLE at lower bound
        wle_high: WLE at upper bound

    Returns:
        Interpolated WLE value
    """
    if age <= age_low:
        return wle_low
    if age >= age_high:
        return wle_high

    # Linear interpolation
    fraction = (age - age_low) / (age_high - age_low)
    return wle_low + fraction * (wle_high - wle_low)


def fill_missing_ages(data: Dict[str, Dict[str, float]],
                     missing_range: range) -> Dict[str, Dict[str, float]]:
    """
    Fill missing ages using linear interpolation.

    Args:
        data: Education level -> {age: wle} dictionary
        missing_range: Range of missing ages (e.g., range(41, 52))

    Returns:
        Updated data with interpolated values
    """
    filled_data = {}

    for edu_level, age_dict in data.items():
        filled_data[edu_level] = age_dict.copy()

        # Check if we have boundary ages
        if '40' not in age_dict or '52' not in age_dict:
            print(f"  WARNING: Cannot interpolate {edu_level} - missing boundary ages")
            continue

        wle_40 = float(age_dict['40'])
        wle_52 = float(age_dict['52'])

        print(f"\n  {edu_level}:")
        print(f"    Age 40: WLE = {wle_40}")
        print(f"    Age 52: WLE = {wle_52}")
        print(f"    Interpolating ages 41-51...")

        for age in missing_range:
            age_str = str(age)
            if age_str in age_dict:
                print(f"      Age {age}: Already exists ({age_dict[age_str]})")
                continue

            # Interpolate
            wle_interp = interpolate_wle(age, 40, 52, wle_40, wle_52)
            filled_data[edu_level][age_str] = round(wle_interp, 2)

            if age == 42:  # Highlight the critical age for Jane Doe
                print(f"      Age {age}: WLE = {wle_interp:.2f} [INTERPOLATED - JANE DOE AGE]")
            elif age in [41, 45, 51]:
                print(f"      Age {age}: WLE = {wle_interp:.2f} [INTERPOLATED]")

    return filled_data


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    json_path = script_dir / 'skoog_2019_markov_model.json'
    backup_path = script_dir / 'skoog_2019_markov_model.json.before_interpolation'

    print("="*70)
    print("Skoog Women's Data - Linear Interpolation Fixer")
    print("="*70)
    print("\nPURPOSE: Fill missing ages 41-51 for women's worklife expectancy")
    print("METHOD:  Linear interpolation between ages 40 and 52")
    print("STATUS:  Standard accepted practice in forensic economics")
    print("="*70)

    # Load existing data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Backup
    print(f"\nCreating backup: {backup_path.name}")
    shutil.copy(json_path, backup_path)

    # Get women's data
    if 'worklife_expectancy' not in data:
        print("ERROR: No worklife_expectancy data found")
        return 1

    if 'female' not in data['worklife_expectancy']:
        print("ERROR: No female data found")
        return 1

    women_data = data['worklife_expectancy']['female']

    print("\nCurrent women's data status:")
    for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
        ages = women_data.get(edu_level, {})
        age_list = sorted([int(a) for a in ages.keys()]) if ages else []

        print(f"  {edu_level}: {len(age_list)} ages", end='')
        if age_list:
            print(f" (range: {min(age_list)}-{max(age_list)})")
        else:
            print()

        # Check for missing ages 41-51
        missing = [age for age in range(41, 52) if str(age) not in ages]
        if missing:
            print(f"    Missing: {missing}")

    # Fill missing ages
    print("\nInterpolating missing ages...")
    filled_women_data = fill_missing_ages(women_data, range(41, 52))

    # Update data
    data['worklife_expectancy']['female'] = filled_women_data

    # Add documentation of interpolation
    if 'metadata' not in data:
        data['metadata'] = {}

    data['metadata']['interpolation_note'] = (
        "Ages 41-51 for female worklife expectancy were interpolated using "
        "linear interpolation between ages 40 and 52. This is standard "
        "practice in forensic economics when specific age data is unavailable "
        "from published tables. Interpolation formula: WLE(age) = WLE(40) + "
        "(age-40)/(52-40) * (WLE(52) - WLE(40))"
    )
    data['metadata']['interpolation_date'] = '2025-10-30'
    data['metadata']['interpolation_ages'] = '41-51 (female only)'

    # Write updated data
    print("\nWriting updated JSON...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Verify
    print("\nVerification:")
    with open(json_path, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)

    women_data_updated = updated_data['worklife_expectancy']['female']

    for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
        ages = women_data_updated.get(edu_level, {})
        age_list = sorted([int(a) for a in ages.keys()]) if ages else []

        print(f"  {edu_level}: {len(age_list)} ages (range: {min(age_list)}-{max(age_list)})")

        # Verify age 42
        if '42' in ages:
            print(f"    Age 42: WLE = {ages['42']} [OK - READY FOR JANE DOE CASE]")
        else:
            print(f"    Age 42: [ERROR - STILL MISSING]")

    print("\n" + "="*70)
    print("[SUCCESS] Women's data interpolation complete")
    print("="*70)
    print(f"\nBackup saved to: {backup_path.name}")
    print("Updated JSON: skoog_2019_markov_model.json")
    print("\nIMPORTANT LEGAL NOTE:")
    print("  - Interpolation method is documented in metadata")
    print("  - Standard accepted practice in forensic economics")
    print("  - Conservative approach using linear trend")
    print("  - Ages 41-51 now available for litigation use")
    print("="*70)

    return 0


if __name__ == '__main__':
    exit(main())
