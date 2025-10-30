#!/usr/bin/env python3
"""
CDC Life Tables PDF Parser (Enhanced)

This enhanced version can handle PDFs where tables aren't automatically detected.
It uses text extraction and pattern matching to parse life table data.

Usage:
    python parse_cdc_pdf_enhanced.py

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


def clean_number(value: str) -> str:
    """Clean numeric values (keep commas and decimals)."""
    if not value:
        return ""
    value = str(value).strip()
    # Keep commas, decimals, negative signs, and digits
    value = re.sub(r'[^\d,.\-]', '', value)
    return value


def extract_text_from_pdf(pdf_path: Path) -> List[str]:
    """
    Extract all text from PDF, line by line.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of text lines
    """
    print(f"Opening PDF: {pdf_path}")

    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")

        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i+1}...")
            text = page.extract_text()

            if text:
                lines = text.split('\n')
                print(f"  Extracted {len(lines)} lines")
                all_text.extend(lines)
            else:
                print(f"  No text extracted")

    print(f"\nTotal lines: {len(all_text)}")
    return all_text


def parse_life_table_from_text(lines: List[str]) -> List[Dict[str, str]]:
    """
    Parse life table data from text lines.

    Looks for patterns like:
    0    0.005588  100,000    559   99,515  7,842,141   78.4
    1    0.000439   99,441     44   99,419  7,742,626   77.9

    Or with age ranges:
    0-1  0.005588  100,000    559   99,515  7,842,141   78.4

    Args:
        lines: List of text lines from PDF

    Returns:
        List of parsed data dictionaries
    """
    data = []

    # Pattern to match a data row (flexible for different formats)
    # Age (0-100+), then 6 numeric columns separated by whitespace
    pattern = r'^(\d+[-\+]?\d*)\s+([\d.]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)'

    print("\nParsing text lines for life table data...")
    found_table = False

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check if this looks like a header row
        line_lower = line.lower()
        if 'age' in line_lower and ('qx' in line_lower or 'probability' in line_lower):
            print(f"Found table header at line {line_num}: {line[:60]}...")
            found_table = True
            continue

        # Try to match data pattern
        match = re.match(pattern, line)
        if match:
            age_str = match.group(1)
            qx = match.group(2)
            lx = match.group(3)
            dx = match.group(4)
            Lx = match.group(5)
            Tx = match.group(6)
            ex = match.group(7)

            # Parse age range
            if '-' in age_str:
                age_display = age_str
                age_start = age_str.split('-')[0]
            elif '+' in age_str:
                age_display = age_str
                age_start = age_str.replace('+', '')
            else:
                age_start = age_str
                # Check if next line has age+1 to determine range format
                if int(age_str) < 100:
                    age_display = f"{age_str}-{int(age_str)+1}"
                else:
                    age_display = f"{age_str}+"

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

            if len(data) <= 5:
                print(f"  Row {len(data)}: Age {age_display}, ex = {ex}")

    if not found_table:
        print("\nWARNING: No table header found. Data may be incomplete.")

    print(f"\nParsed {len(data)} data rows")
    return data


def create_life_table_json(data: List[Dict[str, str]],
                           title: str = "Life table for the total population: United States, 2023",
                           year: int = 2023) -> Dict[str, Any]:
    """Create the full JSON structure."""
    return {
        'Table_1_US_Life_Table_2023': {
            'title': title,
            'description': f'National Vital Statistics Reports, Vol. 74, No. 6, July 15, 2025',
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
    print("CDC Life Tables PDF Parser (Enhanced)")
    print("="*70)

    if not pdf_path.exists():
        print(f"\nERROR: PDF file not found at: {pdf_path}")
        print("Please ensure 'cdc.pdf' is in the same directory as this script.")
        return 1

    try:
        # Extract text
        print("\n[1/3] Extracting text from PDF...")
        lines = extract_text_from_pdf(pdf_path)

        if not lines:
            print("\nERROR: No text extracted from PDF")
            return 1

        # Show sample of extracted text
        print("\nSample of extracted text:")
        for i, line in enumerate(lines[:20]):
            if line.strip():
                print(f"  Line {i+1}: {line[:80]}")

        # Parse data
        print("\n[2/3] Parsing life table data...")
        data = parse_life_table_from_text(lines)

        if not data:
            print("\nERROR: No valid data rows parsed")
            print("\nTIP: The PDF might use a different format than expected.")
            print("     Check the PDF manually and adjust the regex pattern if needed.")
            return 1

        # Create JSON
        print("\n[3/3] Creating JSON file...")
        json_data = create_life_table_json(data)

        # Write to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Successfully created: {json_path}")
        print(f"  - {len(data)} age rows")
        print(f"  - Age range: {data[0]['Age']} to {data[-1]['Age']}")

        # Show sample
        print("\nSample data:")
        for row in data[:3]:
            print(f"  Age {row['Age']}: Life expectancy = {row['ex_Life_Expectancy']} years")

        # Validate
        print("\nValidating output...")
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            print(f"✓ JSON is valid and contains {loaded['Table_1_US_Life_Table_2023']['rows']} rows")

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
