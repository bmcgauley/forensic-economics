"""
Forensic Economics - Agent Module

This module contains independent calculation agents that perform domain-specific
economic analysis. Each agent must:
- Be implemented in a single file (<=300 lines)
- Accept JSON input via run(input_json: dict)
- Return {outputs, provenance_log} dict
- Include provenance tracking for all calculations
"""

__all__ = [
    'LifeExpectancyAgent',
    'WorklifeExpectancyAgent',
    'WageGrowthAgent',
    'DiscountRateAgent',
    'PresentValueAgent',
]
