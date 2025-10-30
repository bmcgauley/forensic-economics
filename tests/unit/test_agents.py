"""Unit tests for agents"""

import pytest
from src.agents.life_expectancy_agent import LifeExpectancyAgent
from src.agents.worklife_expectancy_agent import WorklifeExpectancyAgent
from src.agents.wage_growth_agent import WageGrowthAgent
from src.agents.discount_rate_agent import DiscountRateAgent
from src.agents.present_value_agent import PresentValueAgent


def test_life_expectancy_agent(sample_intake):
    """Test LifeExpectancyAgent produces expected output."""
    agent = LifeExpectancyAgent()
    result = agent.run(sample_intake)

    assert 'agent_name' in result
    assert result['agent_name'] == 'LifeExpectancyAgent'
    assert 'outputs' in result
    assert 'expected_remaining_years' in result['outputs']
    assert 'provenance_log' in result
    assert len(result['provenance_log']) > 0


def test_worklife_expectancy_agent(sample_intake):
    """Test WorklifeExpectancyAgent produces expected output."""
    agent = WorklifeExpectancyAgent()
    result = agent.run(sample_intake)

    assert 'agent_name' in result
    assert result['agent_name'] == 'WorklifeExpectancyAgent'
    assert 'outputs' in result
    assert 'worklife_years' in result['outputs']
    assert 'retirement_age' in result['outputs']
    assert 'provenance_log' in result


def test_wage_growth_agent(sample_intake):
    """Test WageGrowthAgent produces expected output."""
    agent = WageGrowthAgent()
    result = agent.run(sample_intake)

    assert 'agent_name' in result
    assert result['agent_name'] == 'WageGrowthAgent'
    assert 'outputs' in result
    assert 'annual_growth_rate' in result['outputs']
    assert 'projected_wages_by_year' in result['outputs']
    assert 'provenance_log' in result


def test_discount_rate_agent(sample_intake):
    """Test DiscountRateAgent produces expected output."""
    agent = DiscountRateAgent()
    result = agent.run(sample_intake)

    assert 'agent_name' in result
    assert result['agent_name'] == 'DiscountRateAgent'
    assert 'outputs' in result
    assert 'recommended_discount_rate' in result['outputs']
    assert 'discount_curve' in result['outputs']
    assert 'provenance_log' in result


def test_present_value_agent():
    """Test PresentValueAgent produces expected output."""
    agent = PresentValueAgent()

    # Create test input with required data
    input_data = {
        'victim_age': 35,
        'worklife_years': 30.0,
        'projected_wages': {i: 85000 * (1.03 ** i) for i in range(50)},
        'discount_curve': [0.035] * 50,
        'benefits': {
            'retirement_contribution': 5000,
            'health_benefits': 8000
        }
    }

    result = agent.run(input_data)

    assert 'agent_name' in result
    assert result['agent_name'] == 'PresentValueAgent'
    assert 'outputs' in result
    assert 'total_present_value' in result['outputs']
    assert 'yearly_cashflows' in result['outputs']
    assert result['outputs']['total_present_value'] > 0
    assert 'provenance_log' in result


def test_agent_provenance_structure(sample_intake):
    """Test that all agents produce properly structured provenance."""
    agents = [
        LifeExpectancyAgent(),
        WorklifeExpectancyAgent(),
        WageGrowthAgent(),
        DiscountRateAgent()
    ]

    for agent in agents:
        result = agent.run(sample_intake)
        provenance_log = result['provenance_log']

        assert isinstance(provenance_log, list)
        assert len(provenance_log) > 0

        for entry in provenance_log:
            assert 'step' in entry
            assert 'description' in entry
            assert 'value' in entry
