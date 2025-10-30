"""Check what ages were extracted for women"""
import json
from pathlib import Path

backup_file = Path(__file__).parent / 'skoog_2019_markov_model.json.backup'

if backup_file.exists():
    print("Checking original data...")
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check what the mixed table has
    if 'Table_36_37_Mixed' in data:
        mixed = data['Table_36_37_Mixed']
        print(f"\nTable_36_37_Mixed has {len(mixed.get('data', []))} rows")

        # Look for rows with women's data
        print("\nSample rows from mixed table:")
        for i, row in enumerate(mixed.get('data', [])[:5]):
            print(f"  Row {i}: {list(row.keys())[:5]}")

# Check what we just extracted
from parse_skoog_pdf import extract_text_from_pdf, parse_worklife_table_from_text

pdf_path = Path(__file__).parent / 'skoog2.pdf'
lines = extract_text_from_pdf(pdf_path)

# Get women's data
women_data = parse_worklife_table_from_text(lines, 'female')

print("\n" + "="*60)
print("Women's ages extracted:")
print("="*60)

for edu_level in ['less_than_hs', 'hs_graduate', 'some_college', 'bachelors_plus']:
    ages = women_data[edu_level]
    if ages:
        age_list = sorted([int(a) for a in ages.keys()])
        print(f"\n{edu_level}:")
        print(f"  Count: {len(age_list)}")
        print(f"  Range: {min(age_list)} to {max(age_list)}")
        print(f"  Ages: {age_list}")

        # Check if 42 is there
        if '42' in ages:
            print(f"  [OK] Age 42 FOUND: WLE = {ages['42']}")
        else:
            print(f"  [MISSING] Age 42 NOT FOUND")
