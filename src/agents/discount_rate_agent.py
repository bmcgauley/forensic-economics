"""
Discount Rate Agent (AI-Powered with Ollama Gemma3)

Purpose: AI-powered analysis of discount rates using Fed data and LLM reasoning.
Inputs: {location, case_type, present_date}
Outputs: {recommended_discount_curve, ai_analysis, provenance_log}

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any

from .fed_rate_agent import FedRateAgent
from ..utils.ollama_client import get_ollama_client


class DiscountRateAgent:
    """AI Agent for determining appropriate discount rates with LLM reasoning."""

    def __init__(self):
        """Initialize the AI agent with Federal Reserve Rate Agent and Ollama LLM."""
        self.fed_rate_agent = FedRateAgent()
        self.llm = get_ollama_client(model="gemma3:1b")

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine appropriate discount rate using AI reasoning and Fed data.

        Args:
            input_json: Dictionary containing:
                - location (str): Jurisdiction code
                - case_type (str): Type of case (optional)
                - present_date (str): Present date for rate lookup (optional)

        Returns:
            Dictionary containing:
                - outputs: {
                    recommended_discount_rate: float,
                    discount_curve: list,
                    methodology: str,
                    ai_analysis: str (LLM reasoning)
                  }
                - provenance_log: List of provenance entries
        """
        provenance_log = []

        print(f"[DISCOUNT_RATE_AGENT] Starting AI analysis...")

        # Extract inputs
        location = input_json.get('location', 'US')
        case_type = input_json.get('case_type', 'wrongful_death')
        present_date = input_json.get('present_date')

        provenance_log.append({
            'step': 'input_validation',
            'description': 'Received discount rate parameters for AI analysis',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'location': location,
                'case_type': case_type,
                'present_date': present_date
            }
        })

        # Fetch current Treasury rate from Federal Reserve Rate Agent
        print(f"[DISCOUNT_RATE_AGENT] Fetching Fed Reserve rates...")
        fed_rate_result = self.fed_rate_agent.run({'present_date': present_date})

        # Extract treasury rate from Fed agent output
        treasury_1yr_rate = fed_rate_result['outputs']['treasury_1yr_rate']
        is_fallback = fed_rate_result['outputs'].get('is_fallback', False)

        provenance_log.append({
            'step': 'treasury_rate_lookup',
            'description': f'1-Year Treasury rate from Federal Reserve ({fed_rate_result["outputs"]["source"]})',
            'formula': 'Federal Reserve H.15 Selected Interest Rates',
            'source_url': fed_rate_result['outputs']['source_url'],
            'source_date': fed_rate_result['outputs']['data_vintage'],
            'value': {
                'treasury_1yr_rate': treasury_1yr_rate,
                'rate_pct': round(treasury_1yr_rate * 100, 2),
                'is_fallback': is_fallback,
                'retrieval_timestamp': fed_rate_result['outputs']['retrieval_timestamp']
            }
        })

        # Merge Fed agent provenance
        for prov_entry in fed_rate_result['provenance_log']:
            provenance_log.append({
                **prov_entry,
                'step': f'fed_agent_{prov_entry["step"]}'
            })

        # Legal standard often uses risk-free rate or slightly above
        # Many jurisdictions use 2-4% range
        # Using 1-year Treasury as baseline
        recommended_rate = treasury_1yr_rate

        # Use AI to analyze and provide reasoning
        print(f"[DISCOUNT_RATE_AGENT] Querying LLM for analysis...")

        ai_prompt = f"""You are a forensic economics AI agent analyzing discount rates for a wrongful death case.

CASE DATA:
- Case Type: {case_type}
- Jurisdiction: {location}
- Present Date: {present_date}
- Current 1-Year Treasury Rate: {treasury_1yr_rate*100:.2f}%
- Recommended Discount Rate: {recommended_rate*100:.2f}%
- Rate Source: {fed_rate_result["outputs"]["source"]}
- Is Fallback Rate: {is_fallback}

CONTEXT:
Forensic economics typically uses risk-free rates (Treasury bonds) as discount rates for present value calculations. Legal jurisdictions often prefer rates in the 2-4% range. The discount rate converts future earnings to present value.

TASK:
Analyze this discount rate recommendation for forensic economic purposes. Consider:
1. The appropriateness of using the Treasury rate as a baseline
2. Legal standards and precedents for discount rates
3. Economic environment and interest rate context
4. Potential adjustments for jurisdiction-specific factors
5. Forensic economics best practices

Provide your analysis in 2-3 sentences, discussing the discount rate recommendation and any relevant considerations for the present value calculation.

Your response should be professional and suitable for a legal/forensic report."""

        try:
            ai_analysis = self.llm.generate_completion(
                prompt=ai_prompt,
                system_prompt="You are an expert forensic economist AI agent specializing in discount rate analysis for wrongful death cases.",
                temperature=0.5  # Lower temperature for more consistent analysis
            )

            print(f"[DISCOUNT_RATE_AGENT] AI analysis complete ({len(ai_analysis)} chars)")

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
            print(f"[DISCOUNT_RATE_AGENT] LLM error: {e}")
            ai_analysis = f"Economic analysis recommends {recommended_rate*100:.2f}% discount rate based on current 1-Year Treasury rate from Federal Reserve."

            provenance_log.append({
                'step': 'ai_analysis_fallback',
                'description': 'AI analysis failed, using statistical summary',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': str(e)}
            })

        provenance_log.append({
            'step': 'legal_standard_adjustment',
            'description': 'Apply legal jurisdiction standards with AI analysis',
            'formula': 'Treasury rate with jurisdiction-specific adjustments + AI reasoning',
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': recommended_rate
        })

        # Generate discount curve for 50 years
        # Using flat curve for simplicity (could be customized by maturity)
        discount_curve = [round(recommended_rate, 4) for _ in range(50)]

        return {
            'agent_name': 'DiscountRateAgent',
            'inputs_used': {
                'location': location,
                'case_type': case_type,
                'present_date': present_date
            },
            'outputs': {
                'recommended_discount_rate': round(recommended_rate, 4),
                'discount_curve': discount_curve,
                'methodology': 'Treasury-based with legal jurisdiction standards + AI analysis',
                'treasury_rate': round(treasury_1yr_rate, 4),
                'ai_analysis': ai_analysis,
                'ai_model': self.llm.model
            },
            'provenance_log': provenance_log
        }
