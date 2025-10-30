"""
Intake Model

Purpose: Validate and structure intake data from user submissions.
Implements validation rules per data-model.md specification.
"""

from typing import Dict, Any, Optional
import uuid


class ValidationError(Exception):
    """Raised when intake validation fails."""
    pass


class Intake:
    """Intake data model with validation."""

    VALID_SEXES = ['M', 'F', 'Other']
    VALID_SALARY_TYPES = ['current', 'median_jurisdiction']
    VALID_EDUCATION_LEVELS = [
        'less_than_high_school',
        'high_school',
        'some_college',
        'bachelors',
        'masters',
        'doctorate'
    ]

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize and validate intake data.

        Args:
            data: Intake data dictionary

        Raises:
            ValidationError: If validation fails
        """
        self.data = data
        self._validate()

    def _validate(self):
        """Validate intake data according to specification."""

        # Required fields
        required_fields = [
            'victim_age',
            'victim_sex',
            'occupation',
            'salary',
            'salary_type',
            'location',
            'education'
        ]

        for field in required_fields:
            if field not in self.data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate victim_age: 0 <= age <= 120
        age = self.data.get('victim_age')
        try:
            age = int(age)
            if not (0 <= age <= 120):
                raise ValidationError("victim_age must be between 0 and 120")
            self.data['victim_age'] = age
        except (TypeError, ValueError):
            raise ValidationError("victim_age must be a valid integer")

        # Validate victim_sex
        sex = self.data.get('victim_sex')
        if sex not in self.VALID_SEXES:
            raise ValidationError(f"victim_sex must be one of: {', '.join(self.VALID_SEXES)}")

        # Validate education
        education = self.data.get('education')
        if education not in self.VALID_EDUCATION_LEVELS:
            raise ValidationError(f"education must be one of: {', '.join(self.VALID_EDUCATION_LEVELS)}")

        # Validate salary: must be >= 0
        salary = self.data.get('salary')
        try:
            salary = float(salary)
            if salary < 0:
                raise ValidationError("salary must be >= 0")
            self.data['salary'] = salary
        except (TypeError, ValueError):
            raise ValidationError("salary must be a valid number")

        # Validate salary_type
        salary_type = self.data.get('salary_type')
        if salary_type not in self.VALID_SALARY_TYPES:
            raise ValidationError(f"salary_type must be one of: {', '.join(self.VALID_SALARY_TYPES)}")

        # Validate dependents: must be >= 0 (optional, defaults to 0)
        dependents = self.data.get('dependents', 0)
        try:
            dependents = int(dependents)
            if dependents < 0:
                raise ValidationError("dependents must be >= 0")
            self.data['dependents'] = dependents
        except (TypeError, ValueError):
            raise ValidationError("dependents must be a valid integer")

        # Validate benefits (optional)
        benefits = self.data.get('benefits', {})
        if not isinstance(benefits, dict):
            raise ValidationError("benefits must be a dictionary")

        # Validate individual benefit amounts if present
        for benefit_key in ['retirement_contribution', 'health_benefits']:
            if benefit_key in benefits:
                try:
                    amount = float(benefits[benefit_key])
                    if amount < 0:
                        raise ValidationError(f"{benefit_key} must be >= 0")
                    benefits[benefit_key] = amount
                except (TypeError, ValueError):
                    raise ValidationError(f"{benefit_key} must be a valid number")

        self.data['benefits'] = benefits

        # Ensure ID exists
        if 'id' not in self.data or not self.data['id']:
            self.data['id'] = str(uuid.uuid4())

        # Ensure metadata exists
        if 'metadata' not in self.data:
            self.data['metadata'] = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert intake to dictionary.

        Returns:
            Intake data as dictionary
        """
        return self.data.copy()

    @property
    def id(self) -> str:
        """Get intake ID."""
        return self.data['id']

    @property
    def victim_age(self) -> int:
        """Get victim age."""
        return self.data['victim_age']

    @property
    def victim_sex(self) -> str:
        """Get victim sex."""
        return self.data['victim_sex']

    @property
    def occupation(self) -> str:
        """Get occupation."""
        return self.data['occupation']

    @property
    def education(self) -> str:
        """Get education level."""
        return self.data['education']

    @property
    def salary(self) -> float:
        """Get salary."""
        return self.data['salary']

    @property
    def location(self) -> str:
        """Get location/jurisdiction."""
        return self.data['location']

    @property
    def dependents(self) -> int:
        """Get number of dependents."""
        return self.data.get('dependents', 0)

    @property
    def benefits(self) -> Dict[str, float]:
        """Get benefits dictionary."""
        return self.data.get('benefits', {})

    def __repr__(self) -> str:
        """String representation."""
        return f"Intake(id={self.id}, age={self.victim_age}, occupation={self.occupation})"
