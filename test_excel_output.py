"""
Quick test script to generate an Excel file with the new legal format.
"""

from src.models.intake import Intake
from src.agents.supervisor_agent import SupervisorAgent
from src.xlsx.xlsx_generator import XLSXGenerator
from src.aggregator import Aggregator

# Create sample intake with dates
sample_intake = {
    'full_name': 'Jane Smith',
    'date_of_birth': '1981-05-20',
    'date_of_death': '2023-08-15',
    'present_date': '2025-01-10',
    'gender': 'Female',
    'level_of_schooling': 'masters',
    'occupation': 'Financial Analyst',
    'employment_status': 'employed_full_time',
    'annual_salary': 86900.00,
    'california_county': 'Fresno'
}

# Validate intake
intake = Intake(sample_intake)
print(f"Intake validated: {intake}")
print(f"Calculated age: {intake.victim_age}")

# Run supervisor agent
print("\nRunning supervisor agent...")
supervisor = SupervisorAgent()
result = supervisor.run(intake.to_dict())

# Aggregate results
print("\nAggregating results...")
aggregator = Aggregator()
final_workbook = aggregator.aggregate(
    result['outputs']['agent_results'],
    intake.to_dict()
)

# Generate Excel file
print("\nGenerating Excel file...")
xlsx_gen = XLSXGenerator()
output_path = 'wrongful_death_report_test.xlsx'
xlsx_gen.generate(final_workbook, output_path)

print(f"\n✓ Excel file generated: {output_path}")
print(f"\n📊 Summary:")
print(f"  - Total Present Value: ${final_workbook['summary']['economic_summary']['total_present_value']:,.2f}")
print(f"  - Total Future Earnings: ${final_workbook['summary']['economic_summary']['total_future_earnings']:,.2f}")
print(f"  - Yearly cashflows: {len(final_workbook['yearly'])} rows")
print(f"\nPlease open {output_path} to verify the legal format!")
