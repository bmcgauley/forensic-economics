# CDC Life Tables Data

This directory contains CDC life tables data used for life expectancy calculations in forensic economics.

## Quick Start

To parse the CDC PDF and update the JSON file:

```bash
cd data/life_tables
python parse_cdc.py
```

That's it! The script will automatically extract data from `cdc.pdf` and update `cdc_us_life_tables_2023.json`.

## Files

- **cdc.pdf**: Original CDC National Vital Statistics Report containing life tables
- **cdc_us_life_tables_2023.json**: Parsed life table data in JSON format
- **parse_cdc.py**: **[USE THIS]** Simple wrapper script - easiest way to run the parser
- **parse_cdc_pdf_robust.py**: The robust parser implementation (called by parse_cdc.py)
- **parse_cdc_pdf.py**: Alternative parser using table extraction (may not work with all PDF formats)
- **parse_cdc_pdf_enhanced.py**: Alternative parser using text extraction (less reliable than robust version)

## Data Source

- **Source**: National Center for Health Statistics, National Vital Statistics System
- **Report**: National Vital Statistics Reports, Vol. 74, No. 6, July 15, 2025
- **Title**: Life table for the total population: United States, 2023
- **Citation**: CDC/NCHS, National Vital Statistics System, Mortality

## Using the Parser

### Prerequisites

Install required dependencies:

```bash
pip install pdfplumber
```

Or install all project requirements:

```bash
pip install -r ../../requirements.txt
```

### Running the Parser

**Simple method** (recommended):

```bash
cd data/life_tables
python parse_cdc.py
```

**Advanced method** (if you need to customize parsing):

```bash
cd data/life_tables
python parse_cdc_pdf_robust.py
```

The robust parser handles various PDF formats including those with special characters (en-dashes, em-dashes) and complex layouts.

The script will:
1. Read `cdc.pdf` from the current directory
2. Extract the life table data using pdfplumber
3. Parse and clean the data
4. Generate `cdc_us_life_tables_2023.json` with the structured data

### Output Format

The generated JSON has the following structure:

```json
{
  "Table_1_US_Life_Table_2023": {
    "title": "Life table for the total population: United States, 2023",
    "description": "National Vital Statistics Reports, Vol. 74, No. 6, July 15, 2025",
    "source": "National Center for Health Statistics, National Vital Statistics System",
    "year": 2023,
    "columns": {
      "Age": "Age range in years",
      "qx_Probability_of_Dying": "Probability of dying between ages x and x + 1",
      "lx_Number_Surviving": "Number surviving to age x (out of 100,000)",
      "dx_Number_Dying": "Number dying between ages x and x + 1",
      "Lx_Person_Years_Lived": "Person-years lived between ages x and x + 1",
      "Tx_Total_Person_Years_Above_Age": "Total number of person-years lived above age x",
      "ex_Life_Expectancy": "Expectation of life at age x (years)"
    },
    "rows": 101,
    "data": [
      {
        "Age": "0-1",
        "Age_Start": "0",
        "qx_Probability_of_Dying": "0.005588",
        "lx_Number_Surviving": "100,000",
        "dx_Number_Dying": "559",
        "Lx_Person_Years_Lived": "99,515",
        "Tx_Total_Person_Years_Above_Age": "7,842,141",
        "ex_Life_Expectancy": "78.4"
      },
      ...
    ]
  }
}
```

## Data Dictionary

### Life Table Columns

- **Age**: Age range (e.g., "0-1", "1-2", "100+")
- **Age_Start**: Starting age for lookups (e.g., "0", "1", "100")
- **qx_Probability_of_Dying**: Probability of dying between ages x and x+1
- **lx_Number_Surviving**: Number of persons surviving to age x (out of 100,000 births)
- **dx_Number_Dying**: Number dying between ages x and x+1
- **Lx_Person_Years_Lived**: Person-years lived between ages x and x+1
- **Tx_Total_Person_Years_Above_Age**: Total number of person-years lived above age x
- **ex_Life_Expectancy**: Expectation of life (life expectancy) at age x in years

## Updating the Data

When a new CDC life table report is released:

1. Download the new PDF report
2. Replace `cdc.pdf` with the new version
3. Update the metadata in `parse_cdc_pdf.py` if needed:
   - `title` parameter
   - `year` parameter
   - `description` (report volume/number/date)
4. Run the parser: `python parse_cdc_pdf.py`
5. Verify the output JSON file

## Troubleshooting

### "No table data extracted from PDF"

- The PDF structure may have changed. Check that the PDF contains a tabular life table.
- Try opening the PDF manually to verify it's not corrupted.

### "Column detection failed"

- The parser uses flexible column name matching. If CDC changes column names significantly, you may need to update the `column_mapping` in `parse_life_table()`.

### Missing data rows

- Check that the PDF table is properly formatted and not split across columns incorrectly.
- The parser skips rows that don't have at least an age and life expectancy value.

## Notes

- The parser is designed to handle CDC life table PDFs that follow the standard format used in National Vital Statistics Reports.
- Numbers are preserved as strings to maintain formatting (e.g., commas in large numbers).
- The parser can handle tables that span multiple pages.
