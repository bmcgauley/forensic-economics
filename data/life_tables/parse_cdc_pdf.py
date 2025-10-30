#!/usr/bin/env python3
"""
CDC Life Tables PDF Parser

This script parses the CDC life tables PDF (cdc.pdf) and generates/updates
the cdc_us_life_tables_2023.json file.

Usage:
    python parse_cdc_pdf.py

Requirements:
    pip install pdfplumber

The script expects:
- Input: cdc.pdf in the same directory
- Output: cdc_us_life_tables_2023.json (will be created/overwritten)

CDC Life Table Format:
The PDF contains a life table with columns:
- Age (x): Age range
- qx: Probability of dying between ages x and x+1
- lx: Number surviving to age x (out of 100,000)
- dx: Number dying between ages x and x+1
- Lx: Person-years lived between ages x and x+1
- Tx: Total person-years lived above age x
- ex: Life expectancy at age x
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
    """
    Clean numeric values from PDF (remove spaces, handle decimals).

    Args:
        value: Raw string value from PDF

    Returns:
        Cleaned string suitable for JSON
    """
    if not value:
        return ""

    # Remove extra whitespace
    value = str(value).strip()

    # Keep commas, decimals, and digits
    value = re.sub(r'[^\d,.\-]', '', value)

    return value


def parse_age_range(age_str: str) -> tuple[str, str]:
    """
    Parse age range string to get age and starting age.

    Args:
        age_str: Age string like "0-1", "1-2", "100 and over", etc.

    Returns:
        Tuple of (age_display, age_start)
    """
    age_str = str(age_str).strip()

    # Handle "100 and over"
    if 'and over' in age_str.lower() or 'and older' in age_str.lower():
        match = re.search(r'(\d+)', age_str)
        if match:
            age_num = match.group(1)
            return (f"{age_num}+", age_num)

    # Handle ranges like "0-1", "1-2"
    if '-' in age_str:
        parts = age_str.split('-')
        if len(parts) == 2:
            start = parts[0].strip()
            return (age_str, start)

    # Handle single numbers
    if age_str.isdigit():
        return (f"{age_str}-{int(age_str)+1}", age_str)

    return (age_str, age_str)


def extract_table_from_pdf(pdf_path: Path, page_num: int = 0) -> List[List[str]]:
    """
    Extract table data from PDF using pdfplumber.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to extract (0-indexed), or None for all pages

    Returns:
        List of rows, where each row is a list of cell values
    """
    print(f"Opening PDF: {pdf_path}")

    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")

        # Try to extract from all pages if table spans multiple pages
        for i, page in enumerate(pdf.pages):
            print(f"\nProcessing page {i+1}...")

            # Extract tables from the page
            tables = page.extract_tables()

            if not tables:
                print(f"  No tables found on page {i+1}")
                continue

            print(f"  Found {len(tables)} table(s) on page {i+1}")

            # Process each table
            for table_idx, table in enumerate(tables):
                print(f"  Table {table_idx+1}: {len(table)} rows x {len(table[0]) if table else 0} columns")

                # Skip empty tables
                if not table or len(table) < 2:
                    continue

                # Add rows (skip header on subsequent pages)
                if i == 0 and table_idx == 0:
                    # First table on first page - include header
                    all_rows.extend(table)
                else:
                    # Skip header row (usually first row)
                    # Check if first row looks like a header
                    if table[0] and any('age' in str(cell).lower() for cell in table[0] if cell):
                        all_rows.extend(table[1:])
                    else:
                        all_rows.extend(table)

    print(f"\nTotal rows extracted: {len(all_rows)}")
    return all_rows


def parse_life_table(rows: List[List[str]]) -> List[Dict[str, str]]:
    """
    Parse raw table rows into structured life table data.

    Args:
        rows: Raw table rows from PDF

    Returns:
        List of dictionaries with life table data
    """
    if not rows or len(rows) < 2:
        raise ValueError("No data rows found in table")

    # First row should be header
    header = rows[0]
    print(f"\nHeader row: {header}")

    # Expected columns (flexible matching)
    column_mapping = {
        'age': ['age', 'x', 'age(x)'],
        'qx': ['qx', 'q(x)', 'probability of dying'],
        'lx': ['lx', 'l(x)', 'number surviving'],
        'dx': ['dx', 'd(x)', 'number dying'],
        'Lx': ['Lx', 'L(x)', 'person-years lived', 'person years'],
        'Tx': ['Tx', 'T(x)', 'total person-years', 'total person years'],
        'ex': ['ex', 'e(x)', 'expectation', 'life expectancy']
    }

    # Map column indices
    column_indices = {}
    for i, cell in enumerate(header):
        cell_lower = str(cell).lower().strip() if cell else ''
        for key, aliases in column_mapping.items():
            if any(alias in cell_lower for alias in aliases):
                column_indices[key] = i
                break

    print(f"Detected columns: {column_indices}")

    if 'age' not in column_indices:
        print("WARNING: Could not detect Age column. Using first column.")
        column_indices['age'] = 0

    # Parse data rows
    data = []
    for row_idx, row in enumerate(rows[1:], start=1):
        # Skip empty rows
        if not row or not any(row):
            continue

        # Skip rows that look like headers or notes
        first_cell = str(row[0]).lower() if row and row[0] else ''
        if any(skip_word in first_cell for skip_word in ['age', 'source', 'note', 'table']):
            continue

        try:
            # Extract age
            age_col = column_indices.get('age', 0)
            if age_col >= len(row):
                continue

            age_str = str(row[age_col]).strip()
            if not age_str or age_str == 'None':
                continue

            age_display, age_start = parse_age_range(age_str)

            # Build row data
            row_data = {
                'Age': age_display,
                'Age_Start': age_start
            }

            # Extract other columns
            if 'qx' in column_indices and column_indices['qx'] < len(row):
                row_data['qx_Probability_of_Dying'] = clean_number(row[column_indices['qx']])

            if 'lx' in column_indices and column_indices['lx'] < len(row):
                row_data['lx_Number_Surviving'] = clean_number(row[column_indices['lx']])

            if 'dx' in column_indices and column_indices['dx'] < len(row):
                row_data['dx_Number_Dying'] = clean_number(row[column_indices['dx']])

            if 'Lx' in column_indices and column_indices['Lx'] < len(row):
                row_data['Lx_Person_Years_Lived'] = clean_number(row[column_indices['Lx']])

            if 'Tx' in column_indices and column_indices['Tx'] < len(row):
                row_data['Tx_Total_Person_Years_Above_Age'] = clean_number(row[column_indices['Tx']])

            if 'ex' in column_indices and column_indices['ex'] < len(row):
                row_data['ex_Life_Expectancy'] = clean_number(row[column_indices['ex']])

            # Only add if we have at least age and life expectancy
            if 'ex_Life_Expectancy' in row_data and row_data['ex_Life_Expectancy']:
                data.append(row_data)

        except Exception as e:
            print(f"Warning: Error parsing row {row_idx}: {e}")
            continue

    print(f"\nParsed {len(data)} data rows")
    return data


def create_life_table_json(data: List[Dict[str, str]],
                           title: str = "Life table for the total population: United States, 2023",
                           year: int = 2023) -> Dict[str, Any]:
    """
    Create the full JSON structure for life tables.

    Args:
        data: List of parsed data rows
        title: Table title
        year: Year of the data

    Returns:
        Complete JSON structure
    """
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
    """Main function to parse PDF and create JSON."""
    # Set up paths
    script_dir = Path(__file__).parent
    pdf_path = script_dir / 'cdc.pdf'
    json_path = script_dir / 'cdc_us_life_tables_2023.json'

    print("="*70)
    print("CDC Life Tables PDF Parser")
    print("="*70)

    # Check if PDF exists
    if not pdf_path.exists():
        print(f"\nERROR: PDF file not found at: {pdf_path}")
        print("Please ensure 'cdc.pdf' is in the same directory as this script.")
        return 1

    try:
        # Extract table from PDF
        print("\n[1/3] Extracting table from PDF...")
        rows = extract_table_from_pdf(pdf_path)

        if not rows:
            print("\nERROR: No table data extracted from PDF")
            return 1

        # Parse into structured data
        print("\n[2/3] Parsing life table data...")
        data = parse_life_table(rows)

        if not data:
            print("\nERROR: No valid data rows parsed")
            return 1

        # Create JSON structure
        print("\n[3/3] Creating JSON file...")
        json_data = create_life_table_json(data)

        # Write to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Successfully created: {json_path}")
        print(f"  - {len(data)} age rows")
        print(f"  - Age range: {data[0]['Age']} to {data[-1]['Age']}")

        # Validate output
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
