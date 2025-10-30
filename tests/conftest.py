"""
Pytest configuration and fixtures for Forensic Economics tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_intake():
    """Sample intake data for testing."""
    return {
        'id': 'test-123',
        'victim_age': 35,
        'victim_sex': 'M',
        'occupation': 'Software Engineer',
        'education': 'bachelors',
        'salary': 85000.00,
        'salary_type': 'current',
        'location': 'US',
        'dependents': 2,
        'benefits': {
            'retirement_contribution': 5000.00,
            'health_benefits': 8000.00
        },
        'metadata': {
            'submission_timestamp': '2025-10-29T12:00:00Z',
            'user_agent': 'pytest'
        }
    }


@pytest.fixture
def sample_agent_results():
    """Sample agent results for testing aggregator."""
    return [
        {
            'agent_name': 'LifeExpectancyAgent',
            'outputs': {
                'expected_remaining_years': 43.5,
                'life_expectancy_at_birth': 78.5
            },
            'provenance_log': []
        },
        {
            'agent_name': 'WorklifeExpectancyAgent',
            'outputs': {
                'worklife_years': 32.0,
                'retirement_age': 67
            },
            'provenance_log': []
        },
        {
            'agent_name': 'WageGrowthAgent',
            'outputs': {
                'annual_growth_rate': 0.035,
                'projected_wages_by_year': {i: 85000 * (1.035 ** i) for i in range(50)}
            },
            'provenance_log': []
        },
        {
            'agent_name': 'DiscountRateAgent',
            'outputs': {
                'recommended_discount_rate': 0.035,
                'discount_curve': [0.035] * 50
            },
            'provenance_log': []
        },
        {
            'agent_name': 'PresentValueAgent',
            'outputs': {
                'yearly_cashflows': [],
                'total_future_earnings': 3500000.00,
                'total_present_value': 2100000.00
            },
            'provenance_log': []
        }
    ]
