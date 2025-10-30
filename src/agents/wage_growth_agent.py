"""
Wage Growth Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of wage growth projections using BLS data and LLM reasoning.
Inputs: {occupation, salary, education, location}
Outputs: {growth_rate_series, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from ..utils.ollama_client import get_ollama_client


class WageGrowthAgent:
    """AI Agent for projecting wage growth rates with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Ollama LLM."""
        self.llm = get_ollama_client(model="gemma3:1b")

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate wage growth projections using AI reasoning.

        Args:
            input_json: Dictionary containing:
                - occupation (str): Occupation or SOC code
                - salary (float): Current salary
                - education (str): Education level
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    annual_growth_rate: float,
                    growth_rate_series: list,
                    projected_wages_by_year: dict,
                    ai_analysis: str (LLM reasoning)
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        print(f"[WAGE_GROWTH_AGENT] Starting AI analysis...")

        # Extract inputs
        occupation = input_json.get('occupation')
        salary = input_json.get('salary')
        education = input_json.get('education')
        location = input_json.get('location', 'US')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received wage growth parameters for AI analysis',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'occupation': occupation,
                'salary': salary,
                'education': education,
                'location': location
            }
        })

        # Baseline wage growth rate (historical average ~3%)
        base_growth_rate = 0.03

        provenance_log.append({
            'step': 'base_growth_rate',
            'description': 'Historical average wage growth rate',
            'formula': 'BLS Employment Cost Index average',
            'source_url': 'https://www.bls.gov/ncs/ect/',
            'source_date': '2023-01-01',
            'value': base_growth_rate
        })

        # Education adjustment (higher education = higher growth potential)
        education_adjustment_map = {
            'less_than_high_school': -0.005,
            'high_school': 0.0,
            'some_college': 0.002,
            'bachelors': 0.005,
            'masters': 0.007,
            'doctorate': 0.008
        }

        education_adjustment = education_adjustment_map.get(education, 0.0)
        adjusted_growth_rate = base_growth_rate + education_adjustment

        provenance_log.append({
            'step': 'education_adjustment',
            'description': f'Adjust growth rate for {education} education',
            'formula': 'base_growth_rate + education_adjustment',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': adjusted_growth_rate
        })

        # Use AI to analyze and provide reasoning
        print(f"[WAGE_GROWTH_AGENT] Querying LLM for analysis...")

        ai_prompt = f"""You are a forensic economics AI agent analyzing wage growth projections for a wrongful death case.

CASE DATA:
- Occupation: {occupation}
- Current Salary: ${salary:,.2f}
- Education Level: {education}
- Location: {location}
- Calculated Growth Rate: {adjusted_growth_rate*100:.2f}% annually
- Projected Salary in 10 years: ${salary * ((1 + adjusted_growth_rate) ** 10):,.2f}
- Projected Salary in 20 years: ${salary * ((1 + adjusted_growth_rate) ** 20):,.2f}

CONTEXT:
The wage growth rate is based on BLS Employment Cost Index averages (≈3% baseline) adjusted for education level. Higher education typically correlates with stronger wage growth potential.

TASK:
Analyze this wage growth projection for forensic economic purposes. Consider:
1. The reasonableness of the calculated growth rate
2. Economic factors that might affect this occupation
3. Education level's impact on career progression
4. Potential for wage inflation or deflation
5. Forensic economics best practices

Provide your analysis in 2-3 sentences, discussing the wage growth assumptions and any relevant considerations for the economic loss calculation.

Your response should be professional and suitable for a legal/forensic report."""

        try:
            ai_analysis = self.llm.generate_completion(
                prompt=ai_prompt,
                system_prompt="You are an expert forensic economist AI agent specializing in wage growth analysis for wrongful death cases.",
                temperature=0.5  # Lower temperature for more consistent analysis
            )

            print(f"[WAGE_GROWTH_AGENT] AI analysis complete ({len(ai_analysis)} chars)")

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
            print(f"[WAGE_GROWTH_AGENT] LLM error: {e}")
            ai_analysis = f"Economic analysis projects {adjusted_growth_rate*100:.2f}% annual wage growth based on historical BLS data and {education} education level."

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using statistical summary',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e)}
            })

        # Generate growth rate series for next 50 years
        growth_rate_series = [round(adjusted_growth_rate, 4) for _ in range(50)]

        # Project wages for each year
        projected_wages = {}
        current_wage = salary
        for year in range(50):
            projected_wages[year] = round(current_wage, 2)
            current_wage *= (1 + adjusted_growth_rate)

        # DEBUG: Log output
        print(f"[WAGE_GROWTH_AGENT] Generated {len(projected_wages)} wage projections")
        print(f"  - Year 0 wage: ${projected_wages.get(0, 0):,.2f}")
        print(f"  - Year 10 wage: ${projected_wages.get(10, 0):,.2f}")
        print(f"  - Annual growth rate: {adjusted_growth_rate*100:.2f}%")

        return {
            'agent_name': 'WageGrowthAgent',
            'inputs_used': {
                'occupation': occupation,
                'salary': salary,
                'education': education,
                'location': location
            },
            'outputs': {
                'annual_growth_rate': round(adjusted_growth_rate, 4),
                'growth_rate_series': growth_rate_series,
                'projected_wages_by_year': projected_wages,
                'ai_analysis': ai_analysis,
                'ai_model': self.llm.model
            },
            'provenance_log': provenance_log
        }
