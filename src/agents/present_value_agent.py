"""
Present Value Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of present value calculations using LLM reasoning.
Inputs: {victim_age, worklife_years, projected_wages, discount_curve}
Outputs: {yearly_cashflows, pv_table, total_pv, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from ..utils.ollama_client import get_ollama_client


class PresentValueAgent:
    """AI Agent for calculating present value with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Ollama LLM."""
        self.llm = get_ollama_client(model="gemma3:1b")

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate present value of future losses using AI reasoning.

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
                    total_pv: float,
                    total_future_earnings: float,
                    ai_analysis: str (LLM reasoning)
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        print(f"[PRESENT_VALUE_AGENT] Starting AI analysis...")

        # Extract inputs
        victim_age = input_json.get('victim_age')
        worklife_years = input_json.get('worklife_years')
        projected_wages = input_json.get('projected_wages', {})
        discount_curve = input_json.get('discount_curve', [])
        benefits = input_json.get('benefits', {})

        # DEBUG: Log received inputs
        print(f"[PRESENT_VALUE_AGENT] Input validation:")
        print(f"  - victim_age: {victim_age}")
        print(f"  - worklife_years: {worklife_years}")
        print(f"  - projected_wages keys: {list(projected_wages.keys())[:5] if projected_wages else 'EMPTY'}")
        print(f"  - discount_curve length: {len(discount_curve)}")
        print(f"  - benefits: {benefits}")

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received present value calculation parameters for AI analysis',
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

        # Use AI to analyze and provide reasoning
        print(f"[PRESENT_VALUE_AGENT] Querying LLM for analysis...")

        # Get average discount rate
        avg_discount_rate = sum(discount_curve[:worklife_years_int]) / worklife_years_int if worklife_years_int > 0 else 0

        # Calculate PV reduction safely (avoid division by zero)
        pv_reduction = 0.0
        if total_future_earnings > 0:
            pv_reduction = ((total_future_earnings - total_pv) / total_future_earnings * 100)

        ai_prompt = f"""You are a forensic economics AI agent analyzing present value calculations for a wrongful death case.

CASE DATA:
- Victim Age: {victim_age} years old
- Worklife Years: {worklife_years:.2f} years
- Total Future Earnings (Nominal): ${total_future_earnings:,.2f}
- Total Present Value: ${total_pv:,.2f}
- Average Discount Rate: {avg_discount_rate*100:.2f}%
- Present Value Reduction: {pv_reduction:.1f}%

CONTEXT:
Present value converts future earnings to their current value by applying discount rates. This accounts for the time value of money - $1 today is worth more than $1 in the future. The calculation uses the formula: PV = Σ(cashflow_t / (1 + r_t)^t)

TASK:
Analyze this present value calculation for forensic economic purposes. Consider:
1. The reasonableness of the total present value relative to future earnings
2. The impact of the discount rate on the final calculation
3. Any factors that might affect the economic loss estimate
4. The methodology and its acceptance in forensic economics
5. Key takeaways for legal/insurance purposes

Provide your analysis in 2-3 sentences, discussing the present value result and any relevant considerations for the wrongful death economic loss assessment.

Your response should be professional and suitable for a legal/forensic report."""

        try:
            ai_analysis = self.llm.generate_completion(
                prompt=ai_prompt,
                system_prompt="You are an expert forensic economist AI agent specializing in present value calculations for wrongful death cases.",
                temperature=0.5  # Lower temperature for more consistent analysis
            )

            print(f"[PRESENT_VALUE_AGENT] AI analysis complete ({len(ai_analysis)} chars)")

            provenance_log.append({
                'step': 'ai_analysis',
                'description': 'AI reasoning and contextual analysis',
                'formula': 'Ollama Gemma3 LLM Analysis',
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'ai_model': self.llm.model,
                    'analysis_length': len(ai_analysis),
                    'temperature': 0.5
                }
            })

        except Exception as e:
            print(f"[PRESENT_VALUE_AGENT] LLM error: {e}")
            ai_analysis = f"Economic analysis calculates total present value of ${total_pv:,.2f} from future earnings of ${total_future_earnings:,.2f} over {worklife_years:.2f} years using standard discount methodology."

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using statistical summary',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e)}
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
                    'average_annual_compensation': round(total_future_earnings / worklife_years_int, 2) if worklife_years_int > 0 else 0,
                    'average_discount_rate': round(avg_discount_rate, 4)
                },
                'ai_analysis': ai_analysis,
                'ai_model': self.llm.model
            },
            'provenance_log': provenance_log
        }
