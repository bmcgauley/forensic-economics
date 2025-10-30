#!/usr/bin/env python3
"""
Create Proper Women's Data with Interpolation

Uses the existing data_loader to get structured data,
then applies interpolation for missing ages.
"""

import json
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_skoog_tables


def interpolate_wle(age: int, age_low: int, age_high: int,
                    wle_low: float, wle_high: float) -> float:
    """Linear interpolation."""
    if age <= age_low:
        return wle_low
    if age >= age_high:
        return wle_high
    fraction = (age - age_low) / (age_high - age_low)
    return wle_low + fraction * (wle_high - wle_low)


def main():
    print("="*70)
    print("Creating Proper Women's Worklife Data with Interpolation")
    print("="*70)

    # Load using data_loader (this applies the fallback)
    print("\nLoading data via data_loader...")
    data = load_skoog_tables()

    women_data = data['worklife_expectancy']['female']

    print("\nCurrent women's data:")
    for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
        ages = women_data[edu_level]
        age_list = sorted([int(a) for a in ages.keys()])
        print(f"  {edu_level}: {len(age_list)} ages (range: {min(age_list)}-{max(age_list)})")

    # Now we have complete data from fallback, but we want to apply proper
    # women-specific adjustments where we have real data

    # For litigation: Document that we're using:
    # 1. Real women's data where available (ages 16-40, 52-75)
    # 2. Interpolation for ages 41-51
    # 3. Men's data as conservative fallback for ages outside women's table range

    print("\nApplying interpolation for ages 41-51...")

    for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
        ages_dict = women_data[edu_level]

        if '40' not in ages_dict or '52' not in ages_dict:
            print(f"  WARNING: {edu_level} missing boundary ages")
            continue

        wle_40 = float(ages_dict['40'])
        wle_52 = float(ages_dict['52'])

        for age in range(41, 52):
            age_str = str(age)
            wle_interp = interpolate_wle(age, 40, 52, wle_40, wle_52)
            women_data[edu_level][age_str] = round(wle_interp, 2)

            if age == 42:
                print(f"  Age 42 ({edu_level}): {wle_interp:.2f} [INTERPOLATED]")

    # Update metadata
    data['metadata']['interpolation_note'] = (
        "Female worklife expectancy ages 41-51 use linear interpolation "
        "between ages 40 and 52, which is standard forensic economics practice."
    )

    # Save
    output_path = Path(__file__).parent / 'skoog_2019_markov_model.json'
    backup_path = Path(__file__).parent / 'skoog_2019_markov_model.json.before_interp_fix'

    print(f"\nBacking up to: {backup_path.name}")
    import shutil
    if output_path.exists():
        shutil.copy(output_path, backup_path)

    print(f"Writing new JSON to: {output_path.name}")

    # Write in the NEW structure format
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n[SUCCESS] Women's data created with interpolation")
    print("\nNEXT STEP: Remove the fallback code in data_loader.py")

    return 0


if __name__ == '__main__':
    exit(main())
