"""Unit tests for Intake model"""

import pytest
from src.models.intake import Intake, ValidationError


def test_intake_validation_success(sample_intake):
    """Test successful intake validation."""
    intake = Intake(sample_intake)
    assert intake.victim_age == 35
    assert intake.victim_sex == 'M'
    assert intake.salary == 85000.00


def test_intake_missing_required_field():
    """Test validation fails with missing required field."""
    data = {
        'victim_age': 35,
        'victim_sex': 'M'
        # Missing other required fields
    }
    with pytest.raises(ValidationError, match="Missing required field"):
        Intake(data)


def test_intake_invalid_age():
    """Test validation fails with invalid age."""
    data = {
        'victim_age': 150,  # Too old
        'victim_sex': 'M',
        'occupation': 'Engineer',
        'education': 'bachelors',
        'salary': 50000,
        'salary_type': 'current',
        'location': 'US'
    }
    with pytest.raises(ValidationError, match="victim_age must be between 0 and 120"):
        Intake(data)


def test_intake_invalid_sex():
    """Test validation fails with invalid sex."""
    data = {
        'victim_age': 35,
        'victim_sex': 'X',  # Invalid
        'occupation': 'Engineer',
        'education': 'bachelors',
        'salary': 50000,
        'salary_type': 'current',
        'location': 'US'
    }
    with pytest.raises(ValidationError, match="victim_sex must be one of"):
        Intake(data)


def test_intake_negative_salary():
    """Test validation fails with negative salary."""
    data = {
        'victim_age': 35,
        'victim_sex': 'M',
        'occupation': 'Engineer',
        'education': 'bachelors',
        'salary': -50000,  # Negative
        'salary_type': 'current',
        'location': 'US'
    }
    with pytest.raises(ValidationError, match="salary must be >= 0"):
        Intake(data)


def test_intake_auto_generate_id():
    """Test that ID is auto-generated if not provided."""
    data = {
        'victim_age': 35,
        'victim_sex': 'M',
        'occupation': 'Engineer',
        'education': 'bachelors',
        'salary': 50000,
        'salary_type': 'current',
        'location': 'US'
    }
    intake = Intake(data)
    assert intake.id is not None
    assert len(intake.id) > 0


def test_intake_to_dict():
    """Test conversion to dictionary."""
    data = {
        'id': 'test-123',
        'victim_age': 35,
        'victim_sex': 'M',
        'occupation': 'Engineer',
        'education': 'bachelors',
        'salary': 50000,
        'salary_type': 'current',
        'location': 'US',
        'dependents': 2
    }
    intake = Intake(data)
    result = intake.to_dict()
    assert result['id'] == 'test-123'
    assert result['victim_age'] == 35
    assert result['dependents'] == 2
