"""
Wage Growth Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of wage growth projections using BLS data and LLM reasoning.
Inputs: {occupation, salary, education, location}
Outputs: {growth_rate_series, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

from ..utils.ollama_client import get_ollama_client
from ..utils.external_apis import CALaborMarketClient

# Load environment variables from .env file
load_dotenv()


# Structured schema for AI analysis output
AI_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "key_findings": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
            "description": "2-3 key findings about the wage growth projection"
        },
        "risk_factors": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 2,
            "description": "1-2 risk factors to consider"
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 2,
            "description": "1-2 key assumptions made in the projection"
        },
        "confidence_level": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Confidence level in the projection"
        },
        "recommendation": {
            "type": "string",
            "maxLength": 300,
            "description": "Brief recommendation for the calculation (max 300 chars)"
        }
    },
    "required": ["key_findings", "risk_factors", "assumptions", "confidence_level", "recommendation"]
}


class WageGrowthAgent:
    """AI Agent for projecting wage growth rates with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Ollama LLM and CA Labor Market client."""
        self.llm = get_ollama_client(model="gemma3:1b")
        self.ca_labor_client = CALaborMarketClient()

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

        # Check if location is California - if so, use CA Labor Market data
        if location and location.upper() in ['CA', 'CALIFORNIA']:
            print(f"[WAGE_GROWTH_AGENT] Location is California, fetching CA-specific wage growth data...")
            try:
                ca_data = self.ca_labor_client.get_wage_growth_by_occupation(
                    occupation=occupation,
                    county=None,  # Statewide
                    use_fallback_on_error=True
                )

                base_growth_rate = ca_data['growth_rate']
                print(f"[WAGE_GROWTH_AGENT] CA wage growth rate: {base_growth_rate*100:.2f}%")

                provenance_log.append({
                    'step': 'ca_labor_market_fetch',
                    'description': f'Fetched California-specific wage growth for {occupation}',
                    'formula': 'CA Labor Market Info - OES Year-over-Year Growth',
                    'source_url': ca_data['source_url'],
                    'source_date': ca_data['retrieved_at'],
                    'value': {
                        'growth_rate': base_growth_rate,
                        'occupation': occupation,
                        'source': ca_data['source'],
                        'warning': ca_data.get('warning')
                    }
                })

            except Exception as e:
                print(f"[WAGE_GROWTH_AGENT] Error fetching CA data: {e}, using BLS baseline")
                base_growth_rate = 0.03

                provenance_log.append({
                    'step': 'ca_labor_market_error',
                    'description': 'Failed to fetch CA data, using BLS baseline',
                    'formula': None,
                    'source_url': None,
                    'source_date': datetime.utcnow().isoformat(),
                    'value': {
                        'error': str(e),
                        'fallback_rate': base_growth_rate
                    }
                })
        else:
            # Non-CA location: use national BLS baseline
            base_growth_rate = 0.03

            provenance_log.append({
                'step': 'base_growth_rate',
                'description': 'Historical average wage growth rate (BLS national average)',
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

        # Use AI to analyze and provide structured reasoning
        print(f"[WAGE_GROWTH_AGENT] Querying LLM for structured analysis...")

        ai_prompt = f"""Analyze wage growth projection for forensic economics case.

CASE DATA:
- Occupation: {occupation}
- Current Salary: ${salary:,.2f}
- Education Level: {education}
- Location: {location}
- Calculated Growth Rate: {adjusted_growth_rate*100:.2f}% annually
- Projected Salary in 10 years: ${salary * ((1 + adjusted_growth_rate) ** 10):,.2f}
- Projected Salary in 20 years: ${salary * ((1 + adjusted_growth_rate) ** 20):,.2f}

CONTEXT:
Wage growth rate based on BLS Employment Cost Index (~3% baseline) adjusted for education level.

TASK:
Provide structured analysis with:
- 2-3 key findings about the wage growth projection
- 1-2 risk factors to consider
- 1-2 key assumptions made
- Confidence level (high/medium/low)
- Brief recommendation (max 300 chars) suitable for legal/forensic report"""

        try:
            ai_analysis = self.llm.generate_structured_completion(
                prompt=ai_prompt,
                system_prompt="You are a forensic economist analyzing wage growth. Respond ONLY with valid JSON.",
                schema=AI_ANALYSIS_SCHEMA,
                temperature=0.3  # Low temperature for consistent structured output
            )

            print(f"[WAGE_GROWTH_AGENT] Structured AI analysis complete")

            provenance_log.append({
                'step': 'ai_analysis',
                'description': 'Structured AI reasoning and contextual analysis',
                'formula': 'Ollama Gemma3 LLM Structured Analysis',
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'ai_model': self.llm.model,
                    'analysis_structure': 'structured_json',
                    'temperature': 0.3
                }
            })

        except Exception as e:
            print(f"[WAGE_GROWTH_AGENT] LLM error: {e}, using fallback")
            # Structured fallback instead of freeform text
            ai_analysis = {
                "key_findings": [
                    f"Projected growth rate of {adjusted_growth_rate*100:.2f}% based on BLS data",
                    f"Education level ({education}) supports growth assumptions"
                ],
                "risk_factors": [
                    "Economic conditions may vary from historical averages"
                ],
                "assumptions": [
                    "Historical wage growth patterns continue"
                ],
                "confidence_level": "medium",
                "recommendation": f"Growth rate of {adjusted_growth_rate*100:.2f}% is reasonable based on historical data"
            }

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using structured fallback',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e), 'fallback_used': True}
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
