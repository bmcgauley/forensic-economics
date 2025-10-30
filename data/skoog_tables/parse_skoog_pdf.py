#!/usr/bin/env python3
"""
Skoog Worklife Tables PDF Parser

This script parses the Skoog Tables PDF and generates/updates the JSON file
with COMPLETE data for both men and women.

CRITICAL: This is used for active litigation. Data accuracy is paramount.

Usage:
    python parse_skoog_pdf.py

Requirements:
    pip install pdfplumber
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber")
    exit(1)


def clean_number(value: str) -> Optional[str]:
    """Clean numeric values from PDF."""
    if not value:
        return None
    value = str(value).strip()
    # Remove everything except digits, commas, periods, and negative signs
    value = re.sub(r'[^\d,.\-]', '', value)
    if not value or value == '.':
        return None
    return value


def extract_wle_value(cell_value: str) -> Optional[float]:
    """
    Extract the first worklife expectancy value from a cell.

    Format: "WLE WLE-B SD-B" where we want WLE
    Example: "15.23 15.23 0.31" -> 15.23
    """
    if not cell_value:
        return None

    cell_str = str(cell_value).strip()
    if not cell_str or cell_str == 'nan':
        return None

    # Split by whitespace and take first value
    parts = cell_str.split()
    if parts:
        try:
            return float(parts[0])
        except ValueError:
            return None
    return None


def extract_text_from_pdf(pdf_path: Path) -> List[str]:
    """Extract all text lines from PDF."""
    print(f"Opening PDF: {pdf_path}")

    all_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")

        for i, page in enumerate(pdf.pages):
            print(f"  Processing page {i+1}...")
            text = page.extract_text()

            if text:
                lines = text.split('\n')
                all_lines.extend(lines)

    print(f"Total lines extracted: {len(all_lines)}")
    return all_lines


def parse_worklife_table_from_text(lines: List[str], gender: str) -> Dict[str, Dict[str, float]]:
    """
    Parse worklife expectancy data from text lines.

    Looking for patterns like:
    Table 36 (Men) or Table 37 (Women)

    Columns: Age, Less than HS, HS Graduate, Some College, BA+

    Args:
        lines: Text lines from PDF
        gender: 'male' or 'female'

    Returns:
        Dictionary with education levels as keys, age->wle as values
    """
    data = {
        'less_than_hs': {},
        'hs_graduate': {},
        'some_college': {},
        'bachelors_plus': {}
    }

    # Determine which table to look for
    if gender == 'male':
        table_marker = 'Table 36'
        print(f"\nLooking for {table_marker} (Men)...")
    else:
        table_marker = 'Table 37'
        print(f"\nLooking for {table_marker} (Women)...")

    in_table = False
    found_table = False

    # Pattern to match data rows with age and multiple numeric values
    # Age followed by 3-4 groups of WLE values (each group has 2-3 numbers)
    # Example: "16 13.96 13.96 0.17 17.44 17.42 0.31 19.54 19.54 0.20 22.02 21.99 0.26"

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Check for table marker
        if table_marker in line:
            print(f"  Found {table_marker} at line {line_num}")
            in_table = True
            found_table = True
            continue

        # Stop at next table
        if in_table and ('Table 38' in line or 'Table 40' in line):
            print(f"  Reached end of {table_marker}")
            break

        if not in_table:
            continue

        # Skip header rows
        if any(skip in line.lower() for skip in ['age', 'years of education', 'wle', 'sd-b', 'diploma']):
            continue

        # Try to parse data row
        # Look for: Age (2 digits) followed by multiple number groups
        match = re.match(r'^(\d{1,2})\s+([\d.\s]+)$', line)

        if match:
            age = match.group(1)
            numbers_str = match.group(2)

            # Split numbers and extract WLE values (first value in each triplet)
            numbers = numbers_str.split()

            # Expected: 12 numbers (4 education levels × 3 values each)
            # Or sometimes: 9 numbers if last education level is missing
            if len(numbers) >= 9:
                try:
                    # Extract first value from each triplet
                    less_than_hs_wle = float(numbers[0]) if len(numbers) > 0 else None
                    hs_graduate_wle = float(numbers[3]) if len(numbers) > 3 else None
                    some_college_wle = float(numbers[6]) if len(numbers) > 6 else None
                    bachelors_plus_wle = float(numbers[9]) if len(numbers) > 9 else None

                    # Store values
                    if less_than_hs_wle is not None:
                        data['less_than_hs'][age] = less_than_hs_wle
                    if hs_graduate_wle is not None:
                        data['hs_graduate'][age] = hs_graduate_wle
                    if some_college_wle is not None:
                        data['some_college'][age] = some_college_wle
                    if bachelors_plus_wle is not None:
                        data['bachelors_plus'][age] = bachelors_plus_wle

                    # Debug first few rows
                    if len(data['less_than_hs']) <= 3:
                        print(f"    Age {age}: less_than_hs={less_than_hs_wle}, hs={hs_graduate_wle}, college={some_college_wle}, ba+={bachelors_plus_wle}")

                except (ValueError, IndexError) as e:
                    print(f"    Warning: Could not parse line {line_num}: {e}")
                    continue

    if not found_table:
        print(f"  WARNING: {table_marker} not found in PDF!")

    # Report what was found
    for edu_level, ages in data.items():
        print(f"  {edu_level}: {len(ages)} ages")

    return data


def create_skoog_json(men_data: Dict, women_data: Dict) -> Dict[str, Any]:
    """Create the complete JSON structure with both men's and women's data."""

    metadata = {
        'title': 'Skoog Worklife Expectancy Tables 2019',
        'description': 'Markov Model of Labor Force Activity 2012-17',
        'source': 'Journal of Forensic Economics, Vol. 28(1-2), pp. 15-108',
        'year': 2019,
        'authors': 'Skoog, G.R., Ciecka, J.E., & Krueger, K.V.',
        'citation': 'Skoog, G.R., Ciecka, J.E., & Krueger, K.V. (2019). Markov Model of Labor Force Activity 2012-17. Journal of Forensic Economics, 28(1-2), 15-108.',
        'data_period': '2012-2017',
        'publication': 'Journal of Forensic Economics',
        'source_url': 'https://doi.org/10.5384/28-1-2',
        'publication_year': '2019'
    }

    return {
        'metadata': metadata,
        'worklife_expectancy': {
            'male': men_data,
            'female': women_data
        }
    }


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    pdf_path = script_dir / 'skoog2.pdf'
    json_path = script_dir / 'skoog_2019_markov_model.json'
    backup_path = script_dir / 'skoog_2019_markov_model.json.backup'

    print("="*70)
    print("Skoog Worklife Tables PDF Parser")
    print("="*70)
    print("\nWARNING: This data is used for active litigation.")
    print("         Data accuracy is critical for legal proceedings.")
    print("="*70)

    if not pdf_path.exists():
        print(f"\nERROR: PDF file not found at: {pdf_path}")
        print("Please ensure 'skoog2.pdf' is in the data/skoog_tables directory.")
        return 1

    try:
        # Backup existing JSON
        if json_path.exists():
            print(f"\nBacking up existing JSON to: {backup_path.name}")
            import shutil
            shutil.copy(json_path, backup_path)

        # Extract text
        print("\n[1/3] Extracting text from PDF...")
        lines = extract_text_from_pdf(pdf_path)

        if not lines:
            print("\nERROR: No text extracted from PDF")
            return 1

        # Parse men's data
        print("\n[2/3] Parsing men's worklife expectancy (Table 36)...")
        men_data = parse_worklife_table_from_text(lines, 'male')

        # Parse women's data
        print("\n[3/3] Parsing women's worklife expectancy (Table 37)...")
        women_data = parse_worklife_table_from_text(lines, 'female')

        # Validate data
        print("\nValidating extracted data...")

        errors = []

        # Check men's data
        for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
            count = len(men_data[edu_level])
            print(f"  Men - {edu_level}: {count} ages")
            if count < 50:
                errors.append(f"Men's {edu_level} has only {count} ages (expected ~60)")

        # Check women's data
        for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
            count = len(women_data[edu_level])
            print(f"  Women - {edu_level}: {count} ages")
            if count < 50:
                errors.append(f"Women's {edu_level} has only {count} ages (expected ~60)")

        if errors:
            print("\nERROR: Data validation failed:")
            for error in errors:
                print(f"  - {error}")
            print("\nThe PDF format may have changed or parsing needs adjustment.")
            return 1

        # Create JSON
        print("\nCreating JSON structure...")
        json_data = create_skoog_json(men_data, women_data)

        # Write to file
        print(f"Writing to: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print("\n" + "="*70)
        print("[SUCCESS] Skoog tables parsed successfully!")
        print("="*70)
        print(f"\nMen's data:")
        for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
            ages = men_data[edu_level]
            if ages:
                age_list = sorted([int(a) for a in ages.keys()])
                print(f"  {edu_level}: ages {min(age_list)}-{max(age_list)} ({len(ages)} total)")

        print(f"\nWomen's data:")
        for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
            ages = women_data[edu_level]
            if ages:
                age_list = sorted([int(a) for a in ages.keys()])
                print(f"  {edu_level}: ages {min(age_list)}-{max(age_list)} ({len(ages)} total)")

        print(f"\nBackup of old file: {backup_path}")
        print("="*70)

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
