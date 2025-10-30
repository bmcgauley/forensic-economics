"""
Present Value Agent

Purpose: Compute present value of future economic losses using cashflow projections and discount rates.
Inputs: {victim_age, worklife_years, projected_wages, discount_curve}
Outputs: {yearly_cashflows, pv_table, total_pv, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any, List


class PresentValueAgent:
    """Agent for calculating present value of economic losses."""

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate present value of future economic losses.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Current age
                - worklife_years (float): Years of remaining worklife
                - projected_wages (dict): Wage projections by year
                - discount_curve (list): Discount rates by year
                - benefits (dict): Additional benefits (optional)

        Returns:
            Dictionary containing:
                - outputs: {
                    yearly_cashflows: list,
                    pv_table: list,
                    total_pv: float,
                    total_future_earnings: float
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        # Extract inputs
        victim_age = input_json.get('victim_age')
        worklife_years = input_json.get('worklife_years')
        projected_wages = input_json.get('projected_wages', {})
        discount_curve = input_json.get('discount_curve', [])
        benefits = input_json.get('benefits', {})

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received present value calculation parameters',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'worklife_years': worklife_years,
                'has_projected_wages': len(projected_wages) > 0,
                'has_discount_curve': len(discount_curve) > 0
            }
        })

        # Calculate yearly cashflows
        yearly_cashflows = []
        pv_table = []
        total_future_earnings = 0
        total_pv = 0

        retirement_contribution = benefits.get('retirement_contribution', 0)
        health_benefits = benefits.get('health_benefits', 0)

        worklife_years_int = int(worklife_years)

        for year in range(worklife_years_int):
            # Get projected wage for this year
            base_wage = projected_wages.get(str(year), projected_wages.get(year, 0))

            # Add benefits
            total_compensation = base_wage + retirement_contribution + health_benefits

            # Get discount rate for this year
            discount_rate = discount_curve[year] if year < len(discount_curve) else discount_curve[-1]

            # Calculate present value factor: 1 / (1 + r)^t
            pv_factor = 1 / ((1 + discount_rate) ** (year + 1))

            # Calculate present value
            pv = total_compensation * pv_factor

            yearly_cashflows.append({
                'year': year,
                'age': victim_age + year,
                'base_wage': round(base_wage, 2),
                'total_compensation': round(total_compensation, 2),
                'discount_rate': round(discount_rate, 4),
                'pv_factor': round(pv_factor, 6),
                'present_value': round(pv, 2)
            })

            total_future_earnings += total_compensation
            total_pv += pv

        provenance_log.append({
            'step': 'cashflow_projection',
            'description': f'Projected {worklife_years_int} years of cashflows',
            'formula': 'total_compensation = base_wage + benefits',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'years_projected': worklife_years_int,
                'total_future_earnings': round(total_future_earnings, 2)
            }
        })

        provenance_log.append({
            'step': 'present_value_calculation',
            'description': 'Calculate present value using discount curve',
            'formula': 'PV = Σ(cashflow_t / (1 + r_t)^t)',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'total_pv': round(total_pv, 2),
                'discount_method': 'Year-by-year compounding'
            }
        })

        return {
            'agent_name': 'PresentValueAgent',
            'inputs_used': {
                'victim_age': victim_age,
                'worklife_years': worklife_years,
                'benefits': benefits
            },
            'outputs': {
                'yearly_cashflows': yearly_cashflows,
                'total_future_earnings': round(total_future_earnings, 2),
                'total_present_value': round(total_pv, 2),
                'calculation_summary': {
                    'years_calculated': worklife_years_int,
                    'average_annual_compensation': round(total_future_earnings / worklife_years_int, 2) if worklife_years_int > 0 else 0
                }
            },
            'provenance_log': provenance_log
        }
