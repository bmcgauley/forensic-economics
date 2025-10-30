"""
Aggregator Module

Purpose: Accept AgentResult objects and produce FinalWorkbook JSON structure.
Assembles outputs from all agents into a cohesive data structure for XLSX generation.

Single-file module (target <=140 lines)
"""

from typing import Dict, Any, List
from datetime import datetime


class Aggregator:
    """Aggregates results from multiple agents into final workbook structure."""

    def aggregate(self, agent_results: List[Dict[str, Any]], intake: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate agent results into FinalWorkbook structure.

        Args:
            agent_results: List of agent result dictionaries
            intake: Original intake data

        Returns:
            FinalWorkbook dictionary with structure:
                - summary: Top-level calculations
                - yearly: Year-by-year breakdown
                - data_sources: All data sources used
                - methodology_notes: Calculation methodology
                - version_metadata: Generation metadata
        """

        # Organize results by agent name
        results_by_agent = {
            result['agent_name']: result for result in agent_results
        }

        # Extract key outputs
        life_expectancy = results_by_agent.get('LifeExpectancyAgent', {}).get('outputs', {})
        worklife = results_by_agent.get('WorklifeExpectancyAgent', {}).get('outputs', {})
        wage_growth = results_by_agent.get('WageGrowthAgent', {}).get('outputs', {})
        discount_rate = results_by_agent.get('DiscountRateAgent', {}).get('outputs', {})
        present_value = results_by_agent.get('PresentValueAgent', {}).get('outputs', {})

        # Build summary
        summary = {
            'victim_info': {
                'age': intake.get('victim_age'),
                'sex': intake.get('victim_sex'),
                'occupation': intake.get('occupation'),
                'education': intake.get('education'),
                'location': intake.get('location')
            },
            'life_expectancy': {
                'expected_remaining_years': life_expectancy.get('expected_remaining_years', 0),
                'life_expectancy_at_birth': life_expectancy.get('life_expectancy_at_birth', 0)
            },
            'worklife': {
                'worklife_years': worklife.get('worklife_years', 0),
                'retirement_age': worklife.get('retirement_age', 0)
            },
            'economic_summary': {
                'current_salary': intake.get('salary', 0),
                'wage_growth_rate': wage_growth.get('annual_growth_rate', 0),
                'discount_rate': discount_rate.get('recommended_discount_rate', 0),
                'total_future_earnings': present_value.get('total_future_earnings', 0),
                'total_present_value': present_value.get('total_present_value', 0)
            }
        }

        # Build yearly breakdown
        yearly = present_value.get('yearly_cashflows', [])

        # Collect all data sources from provenance logs
        data_sources = []
        for result in agent_results:
            for prov_entry in result.get('provenance_log', []):
                if prov_entry.get('source_url'):
                    data_sources.append({
                        'agent': result['agent_name'],
                        'source_name': prov_entry.get('description', 'Unknown'),
                        'source_url': prov_entry['source_url'],
                        'source_date': prov_entry.get('source_date', ''),
                        'usage': prov_entry.get('step', '')
                    })

        # Deduplicate data sources by URL
        unique_sources = {}
        for source in data_sources:
            url = source['source_url']
            if url not in unique_sources:
                unique_sources[url] = source

        # Build methodology notes
        methodology_notes = self._build_methodology_notes(intake, summary)

        # Build version metadata
        version_metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'generator_version': '0.1.0',
            'spec_ref': 'specs/1-wrongful-death-econ/spec.md',
            'input_id': intake.get('id', 'unknown')
        }

        return {
            'summary': summary,
            'yearly': yearly,
            'data_sources': list(unique_sources.values()),
            'methodology_notes': methodology_notes,
            'version_metadata': version_metadata,
            'provenance_logs': {
                result['agent_name']: result.get('provenance_log', [])
                for result in agent_results
            }
        }

    def _build_methodology_notes(self, intake: Dict[str, Any], summary: Dict[str, Any]) -> str:
        """Build methodology documentation text."""

        notes = f"""
WRONGFUL DEATH ECONOMIC LOSS CALCULATION METHODOLOGY

Victim Profile:
- Age: {intake.get('victim_age')} years
- Sex: {intake.get('victim_sex')}
- Occupation: {intake.get('occupation')}
- Education: {intake.get('education')}
- Jurisdiction: {intake.get('location')}

Calculation Approach:

1. Life Expectancy Analysis
   - Based on actuarial life tables for demographic cohort
   - Expected remaining years: {summary['life_expectancy']['expected_remaining_years']} years

2. Worklife Expectancy
   - Estimated retirement age: {summary['worklife']['retirement_age']} years
   - Remaining worklife: {summary['worklife']['worklife_years']} years

3. Wage Growth Projection
   - Annual growth rate: {summary['economic_summary']['wage_growth_rate']:.2%}
   - Based on historical wage trends and education level

4. Discount Rate
   - Discount rate applied: {summary['economic_summary']['discount_rate']:.2%}
   - Based on Treasury yield curve and legal standards

5. Present Value Calculation
   - Total future earnings (nominal): ${summary['economic_summary']['total_future_earnings']:,.2f}
   - Total present value: ${summary['economic_summary']['total_present_value']:,.2f}

All calculations include full provenance tracking with data sources and formulas.
See "Data Sources" and "Provenance" worksheets for complete audit trail.

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        return notes.strip()
