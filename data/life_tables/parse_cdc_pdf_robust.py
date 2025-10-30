#!/usr/bin/env python3
"""
CDC Life Tables PDF Parser (Robust Version)

Handles various PDF formats including those with special characters and split lines.

Usage:
    python parse_cdc_pdf_robust.py

Requirements:
    pip install pdfplumber
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber")
    exit(1)


def clean_number(value: str) -> str:
    """Clean numeric values."""
    if not value:
        return ""
    value = str(value).strip()
    # Remove everything except digits, commas, periods, and negative signs
    value = re.sub(r'[^\d,.\-]', '', value)
    return value


def normalize_age_range(age_str: str) -> tuple:
    """
    Normalize age range string (handles various dash types).

    Returns: (age_display, age_start)
    """
    # Replace various dash types with standard hyphen
    age_str = re.sub(r'[\u2013\u2014\u2212�]', '-', age_str)  # en-dash, em-dash, minus, etc.

    # Handle "100 and over" or "100+"
    if 'and over' in age_str.lower() or age_str.endswith('+'):
        match = re.search(r'(\d+)', age_str)
        if match:
            age_num = match.group(1)
            return (f"{age_num}+", age_num)

    # Handle ranges like "0-1"
    if '-' in age_str:
        parts = age_str.split('-')
        if len(parts) >= 2:
            start = parts[0].strip()
            if start.isdigit():
                return (age_str, start)

    # Single number
    if age_str.isdigit():
        return (f"{age_str}-{int(age_str)+1}", age_str)

    return (age_str, age_str)


def extract_and_parse_pdf(pdf_path: Path) -> List[Dict[str, str]]:
    """
    Extract text and parse life table data.

    Strategy:
    1. Extract all text
    2. Find lines that look like data rows
    3. Use flexible regex to capture the 7 columns
    """
    print(f"Opening PDF: {pdf_path}")

    all_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")

        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i+1}...")
            text = page.extract_text()

            if text:
                lines = text.split('\n')
                all_lines.extend(lines)
                print(f"  Extracted {len(lines)} lines")

    print(f"\nTotal lines: {len(all_lines)}")

    # Parse data
    data = []

    # More flexible pattern:
    # - Age can have various dash types or dots
    # - Numbers can have commas
    # - Whitespace or dots between columns
    # Pattern groups: (age) (qx) (lx) (dx) (Lx) (Tx) (ex)

    # Match lines like:
    # "0�1. . . . 0.005588 100,000 559 99,515 7,842,141 78.4"
    # "42-43. . . 0.002143 96,234 206 96,131 5,187,456 53.9"

    pattern = r'(\d+[\u2013\u2014\u2212�\-]\d+|\d+\+?|100 and over)[.\s]+' \
              r'(0\.\d+)\s+' \
              r'([\d,]+)\s+' \
              r'([\d,]+)\s+' \
              r'([\d,]+)\s+' \
              r'([\d,]+)\s+' \
              r'(\d+\.\d+)'

    print("\nParsing data rows...")

    for line_num, line in enumerate(all_lines, 1):
        line = line.strip()

        # Try to match the pattern
        match = re.search(pattern, line)

        if match:
            age_str = match.group(1).strip()
            qx = match.group(2).strip()
            lx = match.group(3).strip()
            dx = match.group(4).strip()
            Lx = match.group(5).strip()
            Tx = match.group(6).strip()
            ex = match.group(7).strip()

            # Normalize age
            age_display, age_start = normalize_age_range(age_str)

            row_data = {
                'Age': age_display,
                'Age_Start': age_start,
                'qx_Probability_of_Dying': clean_number(qx),
                'lx_Number_Surviving': clean_number(lx),
                'dx_Number_Dying': clean_number(dx),
                'Lx_Person_Years_Lived': clean_number(Lx),
                'Tx_Total_Person_Years_Above_Age': clean_number(Tx),
                'ex_Life_Expectancy': clean_number(ex)
            }

            data.append(row_data)

            if len(data) <= 5 or len(data) >= 100:
                print(f"  Row {len(data)}: Age {age_display}, ex = {ex}")

    print(f"\nParsed {len(data)} data rows")
    return data


def create_life_table_json(data: List[Dict[str, str]],
                           title: str = "Life table for the total population: United States, 2023",
                           year: int = 2023) -> Dict[str, Any]:
    """Create the full JSON structure."""
    return {
        'Table_1_US_Life_Table_2023': {
            'title': title,
            'description': 'National Vital Statistics Reports, Vol. 74, No. 6, July 15, 2025',
            'source': 'National Center for Health Statistics, National Vital Statistics System',
            'year': year,
            'columns': {
                'Age': 'Age range in years',
                'qx_Probability_of_Dying': 'Probability of dying between ages x and x + 1',
                'lx_Number_Surviving': 'Number surviving to age x (out of 100,000)',
                'dx_Number_Dying': 'Number dying between ages x and x + 1',
                'Lx_Person_Years_Lived': 'Person-years lived between ages x and x + 1',
                'Tx_Total_Person_Years_Above_Age': 'Total number of person-years lived above age x',
                'ex_Life_Expectancy': 'Expectation of life at age x (years)'
            },
            'rows': len(data),
            'data': data
        }
    }


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    pdf_path = script_dir / 'cdc.pdf'
    json_path = script_dir / 'cdc_us_life_tables_2023.json'

    print("="*70)
    print("CDC Life Tables PDF Parser (Robust Version)")
    print("="*70)

    if not pdf_path.exists():
        print(f"\nERROR: PDF file not found at: {pdf_path}")
        return 1

    try:
        # Extract and parse
        print("\n[1/2] Extracting and parsing PDF...")
        data = extract_and_parse_pdf(pdf_path)

        if not data:
            print("\nERROR: No valid data rows parsed")
            print("\nDebugging tips:")
            print("1. Open the PDF manually and check the table format")
            print("2. Look at the sample text output above")
            print("3. The pattern might need adjustment for this specific PDF format")
            return 1

        # Create JSON
        print("\n[2/2] Creating JSON file...")
        json_data = create_life_table_json(data)

        # Write
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Successfully created: {json_path}")
        print(f"  - {len(data)} age rows")
        if data:
            print(f"  - Age range: {data[0]['Age']} to {data[-1]['Age']}")
            print(f"\n  Sample data (first 3 rows):")
            for row in data[:3]:
                print(f"    Age {row['Age']}: ex = {row['ex_Life_Expectancy']} years")
            print(f"  ...")
            print(f"  Last row:")
            print(f"    Age {data[-1]['Age']}: ex = {data[-1]['ex_Life_Expectancy']} years")

        # Validate
        print("\nValidating JSON...")
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            rows = loaded['Table_1_US_Life_Table_2023']['rows']
            print(f"[OK] JSON is valid ({rows} rows)")

            if rows < 100:
                print(f"\nWARNING: Expected ~101 rows for ages 0-100, but got {rows}")
                print("         Check if all data was extracted correctly")

        print("\n" + "="*70)
        print("Parsing complete!")
        print("="*70)
        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
