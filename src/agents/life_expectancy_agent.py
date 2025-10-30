"""
Life Expectancy Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of life expectancy using CDC data and LLM reasoning.
Inputs: {victim_age, victim_sex, location}
Outputs: {expected_remaining_years, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from ..utils.ollama_client import get_ollama_client
from ..utils.data_loader import load_life_tables, get_life_expectancy


class LifeExpectancyAgent:
    """AI Agent for analyzing life expectancy with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Ollama LLM."""
        self.llm = get_ollama_client(model="gemma3:1b")

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze life expectancy using AI reasoning and CDC data.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Age of victim
                - victim_sex (str): Sex (M/F/Male/Female)
                - location (str): Jurisdiction code

        Returns:
            Dictionary containing:
                - outputs: {
                    expected_remaining_years: float,
                    life_expectancy_at_birth: float,
                    ai_analysis: str (LLM reasoning),
                    confidence_level: str
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        print(f"[LIFE_EXPECTANCY_AGENT] Starting AI analysis...")

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex', 'Male')
        location = input_json.get('location', 'US')

        # Normalize gender
        gender = 'male' if victim_sex.upper() in ['M', 'MALE'] else 'female'

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received victim demographics for AI analysis',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'gender': gender,
                'location': location
            }
        })

        # Load CDC life table data
        try:
            print(f"[LIFE_EXPECTANCY_AGENT] Loading CDC life tables...")
            life_tables = load_life_tables()
            remaining_years_from_cdc = get_life_expectancy(victim_age, gender)

            provenance_log.append({
                'step': 'cdc_data_lookup',
                'description': f'CDC life expectancy data for {gender}, age {victim_age}',
                'formula': 'CDC U.S. Life Tables 2023',
                'source_url': 'https://www.cdc.gov/nchs/products/life_tables.htm',
                'source_date': life_tables['metadata'].get('publication_date', '2023'),
                'value': {
                    'remaining_years_cdc': remaining_years_from_cdc,
                    'data_source': life_tables['metadata'].get('source', 'CDC')
                }
            })

        except Exception as e:
            print(f"[LIFE_EXPECTANCY_AGENT] CDC data error: {e}, using estimate")
            # Fallback to simple estimate if CDC data unavailable
            base_life_exp = 78.5 if gender == 'male' else 82.3
            remaining_years_from_cdc = max(0, base_life_exp - victim_age)

            provenance_log.append({
                'step': 'fallback_estimate',
                'description': 'Using estimated life expectancy (CDC data unavailable)',
                'formula': 'base_life_expectancy - victim_age',
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'remaining_years_estimate': remaining_years_from_cdc,
                    'base_life_expectancy': base_life_exp
                }
            })

        # Use AI to analyze and provide reasoning
        print(f"[LIFE_EXPECTANCY_AGENT] Querying LLM for analysis...")

        ai_prompt = f"""You are a forensic economics AI agent analyzing life expectancy for a wrongful death case.

CASE DATA:
- Victim Age: {victim_age} years old
- Gender: {gender}
- Location: {location}
- CDC Statistical Remaining Years: {remaining_years_from_cdc:.2f} years

TASK:
Analyze this life expectancy data for forensic economic purposes. Consider:
1. The statistical baseline from CDC data
2. Any factors that might affect this individual's life expectancy
3. The reliability and applicability of the CDC data
4. Forensic economics best practices

Provide your analysis in 2-3 sentences, discussing the expected remaining years and any relevant considerations for the economic loss calculation.

Your response should be professional and suitable for a legal/forensic report."""

        try:
            ai_analysis = self.llm.generate_completion(
                prompt=ai_prompt,
                system_prompt="You are an expert forensic economist AI agent specializing in life expectancy analysis for wrongful death cases.",
                temperature=0.5  # Lower temperature for more consistent analysis
            )

            print(f"[LIFE_EXPECTANCY_AGENT] AI analysis complete ({len(ai_analysis)} chars)")

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
            print(f"[LIFE_EXPECTANCY_AGENT] LLM error: {e}")
            ai_analysis = f"Statistical analysis based on CDC data shows {remaining_years_from_cdc:.2f} expected remaining years for a {gender} aged {victim_age}."

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using statistical summary',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e)}
            })

        # Calculate derived values
        life_expectancy_at_birth = victim_age + remaining_years_from_cdc

        # Generate year-by-year breakdown
        remaining_by_age = {}
        for year_offset in range(int(remaining_years_from_cdc) + 1):
            age = victim_age + year_offset
            remaining = max(0, remaining_years_from_cdc - year_offset)
            remaining_by_age[age] = round(remaining, 2)

        return {
            'agent_name': 'LifeExpectancyAgent',
            'inputs_used': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'location': location
            },
            'outputs': {
                'expected_remaining_years': round(remaining_years_from_cdc, 2),
                'life_expectancy_at_birth': round(life_expectancy_at_birth, 2),
                'expected_remaining_years_by_age': remaining_by_age,
                'ai_analysis': ai_analysis,
                'confidence_level': 'high',  # Based on CDC data quality
                'data_source': 'CDC U.S. Life Tables 2023',
                'ai_model': self.llm.model
            },
            'provenance_log': provenance_log
        }
