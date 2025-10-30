"""
Intake Model

Purpose: Validate and structure intake data from user submissions.
Implements validation rules per data-model.md specification.
"""

from typing import Dict, Any, Optional
from datetime import datetime, date
import uuid


class ValidationError(Exception):
    """Raised when intake validation fails."""
    pass


class Intake:
    """Intake data model with validation."""

    VALID_GENDERS = ['Male', 'Female', 'Other']
    VALID_EMPLOYMENT_STATUSES = [
        'employed_full_time',
        'employed_part_time',
        'self_employed',
        'unemployed',
        'retired'
    ]
    VALID_EDUCATION_LEVELS = [
        'less_than_high_school',
        'high_school',
        'some_college',
        'bachelors',
        'masters',
        'doctorate'
    ]

    # California counties (all 58 counties)
    CALIFORNIA_COUNTIES = [
        'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa',
        'Del Norte', 'El Dorado', 'Fresno', 'Glenn', 'Humboldt', 'Imperial', 'Inyo',
        'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles', 'Madera', 'Marin', 'Mariposa',
        'Mendocino', 'Merced', 'Modoc', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange',
        'Placer', 'Plumas', 'Riverside', 'Sacramento', 'San Benito', 'San Bernardino',
        'San Diego', 'San Francisco', 'San Joaquin', 'San Luis Obispo', 'San Mateo',
        'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Siskiyou',
        'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tulare',
        'Tuolumne', 'Ventura', 'Yolo', 'Yuba'
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

        # Required fields per assignment
        required_fields = [
            'full_name',
            'date_of_birth',
            'present_date',
            'gender',
            'level_of_schooling',
            'occupation',
            'employment_status',
            'annual_salary',
            'california_county'
        ]

        for field in required_fields:
            if field not in self.data or not self.data[field]:
                raise ValidationError(f"Missing required field: {field}")

        # Validate full_name: non-empty string
        full_name = self.data.get('full_name', '').strip()
        if not full_name:
            raise ValidationError("full_name must be a non-empty string")
        self.data['full_name'] = full_name

        # Validate date_of_birth: valid date, must be in past
        try:
            dob = self._parse_date(self.data.get('date_of_birth'))
            if dob >= date.today():
                raise ValidationError("date_of_birth must be in the past")
            self.data['date_of_birth'] = dob.isoformat()
        except (TypeError, ValueError) as e:
            raise ValidationError(f"date_of_birth must be a valid date: {str(e)}")

        # Validate present_date: defaults to today
        try:
            present = self._parse_date(self.data.get('present_date', date.today()))
            self.data['present_date'] = present.isoformat()
        except (TypeError, ValueError) as e:
            raise ValidationError(f"present_date must be a valid date: {str(e)}")

        # Validate date_of_death: optional, must be after DOB if present
        date_of_death = self.data.get('date_of_death')
        if date_of_death:
            try:
                dod = self._parse_date(date_of_death)
                dob = self._parse_date(self.data['date_of_birth'])
                if dod <= dob:
                    raise ValidationError("date_of_death must be after date_of_birth")
                self.data['date_of_death'] = dod.isoformat()
            except (TypeError, ValueError) as e:
                raise ValidationError(f"date_of_death must be a valid date: {str(e)}")

        # Calculate age from date_of_birth and present_date
        dob = self._parse_date(self.data['date_of_birth'])
        present = self._parse_date(self.data['present_date'])
        age = present.year - dob.year - ((present.month, present.day) < (dob.month, dob.day))
        self.data['victim_age'] = age

        # Validate gender
        gender = self.data.get('gender')
        if gender not in self.VALID_GENDERS:
            raise ValidationError(f"gender must be one of: {', '.join(self.VALID_GENDERS)}")

        # Validate level_of_schooling
        education = self.data.get('level_of_schooling')
        if education not in self.VALID_EDUCATION_LEVELS:
            raise ValidationError(f"level_of_schooling must be one of: {', '.join(self.VALID_EDUCATION_LEVELS)}")

        # Validate employment_status
        employment_status = self.data.get('employment_status')
        if employment_status not in self.VALID_EMPLOYMENT_STATUSES:
            raise ValidationError(f"employment_status must be one of: {', '.join(self.VALID_EMPLOYMENT_STATUSES)}")

        # Validate annual_salary: must be >= 0
        salary = self.data.get('annual_salary')
        try:
            salary = float(salary)
            if salary < 0:
                raise ValidationError("annual_salary must be >= 0")
            self.data['annual_salary'] = salary
            # Also set 'salary' for backward compatibility with existing agents
            self.data['salary'] = salary
        except (TypeError, ValueError):
            raise ValidationError("annual_salary must be a valid number")

        # Validate california_county
        county = self.data.get('california_county')
        if county not in self.CALIFORNIA_COUNTIES:
            raise ValidationError(f"california_county must be one of the 58 California counties")

        # Set backward compatibility fields for existing agents
        self.data['victim_sex'] = 'M' if gender == 'Male' else 'F' if gender == 'Female' else 'Other'
        self.data['education'] = education
        self.data['location'] = f"{county}, CA"

        # Ensure ID exists
        if 'id' not in self.data or not self.data['id']:
            self.data['id'] = str(uuid.uuid4())

        # Ensure metadata exists
        if 'metadata' not in self.data:
            self.data['metadata'] = {}

    def _parse_date(self, date_input) -> date:
        """Parse date from various formats."""
        if isinstance(date_input, date):
            return date_input
        if isinstance(date_input, datetime):
            return date_input.date()
        if isinstance(date_input, str):
            # Try ISO format first (YYYY-MM-DD)
            try:
                return datetime.fromisoformat(date_input).date()
            except ValueError:
                pass
            # Try common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_input, fmt).date()
                except ValueError:
                    continue
        raise ValueError(f"Unable to parse date: {date_input}")

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
    def full_name(self) -> str:
        """Get full name."""
        return self.data['full_name']

    @property
    def date_of_birth(self) -> str:
        """Get date of birth."""
        return self.data['date_of_birth']

    @property
    def date_of_death(self) -> Optional[str]:
        """Get date of death."""
        return self.data.get('date_of_death')

    @property
    def present_date(self) -> str:
        """Get present date."""
        return self.data['present_date']

    @property
    def victim_age(self) -> int:
        """Get victim age (calculated from DOB and present date)."""
        return self.data['victim_age']

    @property
    def gender(self) -> str:
        """Get gender."""
        return self.data['gender']

    @property
    def victim_sex(self) -> str:
        """Get victim sex (backward compatibility)."""
        return self.data['victim_sex']

    @property
    def level_of_schooling(self) -> str:
        """Get level of schooling."""
        return self.data['level_of_schooling']

    @property
    def education(self) -> str:
        """Get education level (backward compatibility)."""
        return self.data['education']

    @property
    def occupation(self) -> str:
        """Get occupation."""
        return self.data['occupation']

    @property
    def employment_status(self) -> str:
        """Get employment status."""
        return self.data['employment_status']

    @property
    def annual_salary(self) -> float:
        """Get annual salary."""
        return self.data['annual_salary']

    @property
    def salary(self) -> float:
        """Get salary (backward compatibility)."""
        return self.data['salary']

    @property
    def california_county(self) -> str:
        """Get California county."""
        return self.data['california_county']

    @property
    def location(self) -> str:
        """Get location (backward compatibility)."""
        return self.data['location']

    def __repr__(self) -> str:
        """String representation."""
        return f"Intake(id={self.id}, age={self.victim_age}, occupation={self.occupation})"
