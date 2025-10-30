"""
XLSX Generator Module

Purpose: Consume FinalWorkbook JSON and generate legally-compatible Excel workbook.
Produces workbook with Summary, Yearly Detail, Data Sources, and Methodology sheets.

Single-file module (target <=260 lines)
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any
from datetime import datetime
import os


class XLSXGenerator:
    """Generate Excel workbooks from aggregated calculation results."""

    def __init__(self):
        """Initialize generator with style definitions."""
        self.header_font = Font(bold=True, size=12)
        self.title_font = Font(bold=True, size=14)
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    def generate(self, final_workbook: Dict[str, Any], output_path: str) -> str:
        """
        Generate Excel workbook from final workbook data.

        Args:
            final_workbook: FinalWorkbook dictionary from aggregator
            output_path: Path where to save the workbook

        Returns:
            Path to generated workbook
        """
        wb = Workbook()

        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])

        # Create worksheets
        self._create_summary_sheet(wb, final_workbook)
        self._create_yearly_detail_sheet(wb, final_workbook)
        self._create_data_sources_sheet(wb, final_workbook)
        self._create_methodology_sheet(wb, final_workbook)

        # Save workbook
        wb.save(output_path)
        return output_path

    def _create_summary_sheet(self, wb: Workbook, data: Dict[str, Any]):
        """Create Summary worksheet with key calculations."""
        ws = wb.create_sheet("Summary", 0)
        summary = data.get('summary', {})

        row = 1

        # Title
        ws[f'A{row}'] = "WRONGFUL DEATH ECONOMIC LOSS SUMMARY"
        ws[f'A{row}'].font = self.title_font
        row += 2

        # Victim Information
        ws[f'A{row}'] = "VICTIM INFORMATION"
        ws[f'A{row}'].font = self.header_font
        row += 1

        victim_info = summary.get('victim_info', {})
        ws[f'A{row}'] = "Age:"
        ws[f'B{row}'] = victim_info.get('age', '')
        row += 1
        ws[f'A{row}'] = "Sex:"
        ws[f'B{row}'] = victim_info.get('sex', '')
        row += 1
        ws[f'A{row}'] = "Occupation:"
        ws[f'B{row}'] = victim_info.get('occupation', '')
        row += 1
        ws[f'A{row}'] = "Education:"
        ws[f'B{row}'] = victim_info.get('education', '')
        row += 1
        ws[f'A{row}'] = "Jurisdiction:"
        ws[f'B{row}'] = victim_info.get('location', '')
        row += 2

        # Life & Work Expectancy
        ws[f'A{row}'] = "LIFE & WORK EXPECTANCY"
        ws[f'A{row}'].font = self.header_font
        row += 1

        life_exp = summary.get('life_expectancy', {})
        ws[f'A{row}'] = "Expected Remaining Years:"
        ws[f'B{row}'] = life_exp.get('expected_remaining_years', 0)
        row += 1

        worklife = summary.get('worklife', {})
        ws[f'A{row}'] = "Worklife Years Remaining:"
        ws[f'B{row}'] = worklife.get('worklife_years', 0)
        row += 1
        ws[f'A{row}'] = "Retirement Age:"
        ws[f'B{row}'] = worklife.get('retirement_age', 0)
        row += 2

        # Economic Summary
        ws[f'A{row}'] = "ECONOMIC CALCULATIONS"
        ws[f'A{row}'].font = self.header_font
        row += 1

        econ = summary.get('economic_summary', {})
        ws[f'A{row}'] = "Current Salary:"
        ws[f'B{row}'] = econ.get('current_salary', 0)
        ws[f'B{row}'].number_format = '$#,##0.00'
        row += 1
        ws[f'A{row}'] = "Wage Growth Rate:"
        ws[f'B{row}'] = econ.get('wage_growth_rate', 0)
        ws[f'B{row}'].number_format = '0.00%'
        row += 1
        ws[f'A{row}'] = "Discount Rate:"
        ws[f'B{row}'] = econ.get('discount_rate', 0)
        ws[f'B{row}'].number_format = '0.00%'
        row += 2

        ws[f'A{row}'] = "Total Future Earnings (Nominal):"
        ws[f'B{row}'] = econ.get('total_future_earnings', 0)
        ws[f'B{row}'].number_format = '$#,##0.00'
        ws[f'B{row}'].font = Font(bold=True)
        row += 1

        ws[f'A{row}'] = "TOTAL PRESENT VALUE:"
        ws[f'B{row}'] = econ.get('total_present_value', 0)
        ws[f'B{row}'].number_format = '$#,##0.00'
        ws[f'A{row}'].font = self.title_font
        ws[f'B{row}'].font = self.title_font

        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20

    def _create_yearly_detail_sheet(self, wb: Workbook, data: Dict[str, Any]):
        """Create Yearly Detail worksheet with year-by-year calculations."""
        ws = wb.create_sheet("Yearly Detail")
        yearly = data.get('yearly', [])

        # Headers
        headers = ['Year', 'Age', 'Base Wage', 'Total Compensation', 'Discount Rate', 'PV Factor', 'Present Value']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal='center')

        # Data rows
        for row_idx, year_data in enumerate(yearly, 2):
            ws.cell(row=row_idx, column=1, value=year_data.get('year', ''))
            ws.cell(row=row_idx, column=2, value=year_data.get('age', ''))
            ws.cell(row=row_idx, column=3, value=year_data.get('base_wage', 0)).number_format = '$#,##0.00'
            ws.cell(row=row_idx, column=4, value=year_data.get('total_compensation', 0)).number_format = '$#,##0.00'
            ws.cell(row=row_idx, column=5, value=year_data.get('discount_rate', 0)).number_format = '0.00%'
            ws.cell(row=row_idx, column=6, value=year_data.get('pv_factor', 0)).number_format = '0.000000'
            ws.cell(row=row_idx, column=7, value=year_data.get('present_value', 0)).number_format = '$#,##0.00'

        # Adjust column widths
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 18

    def _create_data_sources_sheet(self, wb: Workbook, data: Dict[str, Any]):
        """Create Data Sources worksheet."""
        ws = wb.create_sheet("Data Sources")
        data_sources = data.get('data_sources', [])

        # Title
        ws['A1'] = "DATA SOURCES & PROVENANCE"
        ws['A1'].font = self.title_font
        ws.merge_cells('A1:D1')

        # Headers
        headers = ['Agent', 'Source Name', 'URL', 'Usage']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill

        # Data rows
        for row_idx, source in enumerate(data_sources, 4):
            ws.cell(row=row_idx, column=1, value=source.get('agent', ''))
            ws.cell(row=row_idx, column=2, value=source.get('source_name', ''))
            ws.cell(row=row_idx, column=3, value=source.get('source_url', ''))
            ws.cell(row=row_idx, column=4, value=source.get('usage', ''))

        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 50
        ws.column_dimensions['D'].width = 25

    def _create_methodology_sheet(self, wb: Workbook, data: Dict[str, Any]):
        """Create Methodology worksheet."""
        ws = wb.create_sheet("Methodology")

        methodology_notes = data.get('methodology_notes', '')

        # Title
        ws['A1'] = "CALCULATION METHODOLOGY"
        ws['A1'].font = self.title_font

        # Add methodology text
        ws['A3'] = methodology_notes
        ws['A3'].alignment = Alignment(wrap_text=True, vertical='top')

        # Adjust column width
        ws.column_dimensions['A'].width = 100
        ws.row_dimensions[3].height = 400
