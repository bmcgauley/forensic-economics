"""
Worklife Expectancy Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of worklife expectancy using Skoog data and LLM reasoning.
Inputs: {victim_age, victim_sex, occupation, education, location}
Outputs: {worklife_years, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from .skoog_table_agent import SkoogTableAgent
from ..utils.ollama_client import get_ollama_client


# Structured schema for AI analysis output
AI_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "key_findings": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
            "description": "2-3 key findings about worklife expectancy"
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
            "description": "1-2 key assumptions made"
        },
        "confidence_level": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Confidence level in the projection"
        },
        "recommendation": {
            "type": "string",
            "maxLength": 300,
            "description": "Brief recommendation (max 300 chars)"
        }
    },
    "required": ["key_findings", "risk_factors", "assumptions", "confidence_level", "recommendation"]
}


class WorklifeExpectancyAgent:
    """AI Agent for analyzing worklife expectancy with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Skoog Table Agent and Ollama LLM."""
        self.skoog_agent = SkoogTableAgent()
        self.llm = get_ollama_client(model="gemma3:1b")

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze worklife expectancy using AI reasoning and Skoog data.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Current age
                - victim_sex (str): Gender (M/F/Male/Female)
                - occupation (str): Occupation or SOC code
                - education (str): Education level
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    worklife_years: float,
                    retirement_age: int (estimated),
                    ai_analysis: str (LLM reasoning),
                    worklife_years_by_age: dict
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        print(f"[WORKLIFE_EXPECTANCY_AGENT] Starting AI analysis...")

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex', 'male')
        occupation = input_json.get('occupation')
        education = input_json.get('education')
        location = input_json.get('location', 'US')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received employment parameters for AI analysis',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'occupation': occupation,
                'education': education,
                'location': location
            }
        })

        # Fetch worklife expectancy from Skoog Table Agent
        print(f"[WORKLIFE_EXPECTANCY_AGENT] Querying Skoog tables...")
        skoog_result = self.skoog_agent.run({
            'age': victim_age,
            'gender': victim_sex,
            'education': education
        })

        # Extract worklife expectancy from Skoog agent output
        worklife_years = skoog_result['outputs']['worklife_expectancy_years']
        skoog_source = skoog_result['outputs'].get('table_source', 'Skoog Tables')

        provenance_log.append({
            'step': 'skoog_table_lookup',
            'description': f'Worklife expectancy from {skoog_source}',
            'formula': 'Markov Model of Labor Force Activity (Skoog, Ciecka, Krueger 2019)',
            'source_url': skoog_result['outputs'].get('source_url'),
            'source_date': skoog_result['outputs'].get('source_year'),
            'value': {
                'worklife_years': worklife_years,
                'source': skoog_source
            }
        })

        # Merge Skoog agent provenance
        for prov_entry in skoog_result['provenance_log']:
            provenance_log.append({
                **prov_entry,
                'step': f'skoog_agent_{prov_entry["step"]}'
            })

        # Estimate retirement age (current age + worklife years)
        retirement_age = int(victim_age + worklife_years)

        # Use AI to analyze and provide structured reasoning
        print(f"[WORKLIFE_EXPECTANCY_AGENT] Querying LLM for structured analysis...")

        ai_prompt = f"""Analyze worklife expectancy for forensic economics case.

CASE DATA:
- Victim Age: {victim_age} years old
- Gender: {victim_sex}
- Occupation: {occupation}
- Education: {education}
- Skoog Table Worklife: {worklife_years:.2f} years
- Estimated Retirement Age: {retirement_age} years

CONTEXT:
Skoog Tables (2019) use Markov Model based on 2012-2017 labor force data.

TASK:
Provide structured analysis with:
- 2-3 key findings about the worklife expectancy
- 1-2 risk factors to consider
- 1-2 key assumptions made
- Confidence level (high/medium/low)
- Brief recommendation (max 300 chars) suitable for legal/forensic report"""

        try:
            ai_analysis = self.llm.generate_structured_completion(
                prompt=ai_prompt,
                system_prompt="You are a forensic economist analyzing worklife expectancy. Respond ONLY with valid JSON.",
                schema=AI_ANALYSIS_SCHEMA,
                temperature=0.3  # Low temperature for consistent structured output
            )

            print(f"[WORKLIFE_EXPECTANCY_AGENT] Structured AI analysis complete")

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
            print(f"[WORKLIFE_EXPECTANCY_AGENT] LLM error: {e}, using fallback")
            # Structured fallback instead of freeform text
            ai_analysis = {
                "key_findings": [
                    f"Skoog Tables project {worklife_years:.2f} years of remaining worklife",
                    f"Education level ({education}) factored into projection"
                ],
                "risk_factors": [
                    "Labor market conditions may vary from 2012-2017 baseline"
                ],
                "assumptions": [
                    "Victim continues in labor force per Skoog model"
                ],
                "confidence_level": "high",
                "recommendation": f"Worklife expectancy of {worklife_years:.2f} years is statistically sound"
            }

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using structured fallback',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e), 'fallback_used': True}
            })

        provenance_log.append({
            'step': 'worklife_calculation',
            'description': 'Calculate expected worklife years from Skoog tables with AI analysis',
            'formula': 'Direct lookup from Skoog Markov model + AI reasoning',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'worklife_years': worklife_years,
                'estimated_retirement_age': retirement_age
            }
        })

        # Generate year-by-year worklife expectancy
        worklife_by_age = {}
        for year_offset in range(int(worklife_years) + 1):
            age = victim_age + year_offset
            remaining_worklife = max(0, worklife_years - year_offset)
            worklife_by_age[age] = round(remaining_worklife, 2)

        return {
            'agent_name': 'WorklifeExpectancyAgent',
            'inputs_used': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'occupation': occupation,
                'education': education,
                'location': location
            },
            'outputs': {
                'worklife_years': round(worklife_years, 2),
                'retirement_age': retirement_age,
                'worklife_years_by_age': worklife_by_age,
                'ai_analysis': ai_analysis,
                'data_source': skoog_source,
                'ai_model': self.llm.model
            },
            'provenance_log': provenance_log
        }
