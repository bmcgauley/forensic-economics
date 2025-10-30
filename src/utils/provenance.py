"""
Provenance Utility

Purpose: Normalize and serialize provenance log entries.
Provides helpers for creating consistent provenance entries across all agents.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ProvenanceLogger:
    """Helper for creating and managing provenance log entries."""

    @staticmethod
    def create_entry(
        step: str,
        description: str,
        value: Any,
        formula: Optional[str] = None,
        source_url: Optional[str] = None,
        source_date: Optional[str] = None,
        source_version: Optional[str] = None,
        license_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized provenance log entry.

        Args:
            step: Step identifier (e.g., 'input_validation', 'calculation')
            description: Human-readable description of the step
            value: The value or result from this step
            formula: Formula or calculation method used (optional)
            source_url: URL of data source (optional)
            source_date: Date of source data (optional)
            source_version: Version of source data (optional)
            license_info: License information for data source (optional)

        Returns:
            Standardized provenance entry dictionary
        """
        entry = {
            'step': step,
            'description': description,
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
        }

        if formula:
            entry['formula'] = formula
        if source_url:
            entry['source_url'] = source_url
        if source_date:
            entry['source_date'] = source_date
        if source_version:
            entry['source_version'] = source_version
        if license_info:
            entry['license_info'] = license_info

        return entry

    @staticmethod
    def create_input_entry(input_data: Dict[str, Any], description: str = "Input data received") -> Dict[str, Any]:
        """
        Create a provenance entry for input data.

        Args:
            input_data: Input data dictionary
            description: Description of the input

        Returns:
            Provenance entry for inputs
        """
        return ProvenanceLogger.create_entry(
            step='input',
            description=description,
            value=input_data,
            formula=None,
            source_url=None
        )

    @staticmethod
    def create_calculation_entry(
        step_name: str,
        description: str,
        formula: str,
        result: Any
    ) -> Dict[str, Any]:
        """
        Create a provenance entry for a calculation.

        Args:
            step_name: Name of the calculation step
            description: Description of what was calculated
            formula: Formula or method used
            result: Calculation result

        Returns:
            Provenance entry for calculation
        """
        return ProvenanceLogger.create_entry(
            step=step_name,
            description=description,
            value=result,
            formula=formula
        )

    @staticmethod
    def create_data_source_entry(
        step_name: str,
        description: str,
        source_url: str,
        value: Any,
        source_date: Optional[str] = None,
        license_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a provenance entry for external data source.

        Args:
            step_name: Name of the step
            description: Description of the data source
            source_url: URL of the data source
            value: Value retrieved from source
            source_date: Date of source data
            license_info: License information

        Returns:
            Provenance entry for data source
        """
        return ProvenanceLogger.create_entry(
            step=step_name,
            description=description,
            value=value,
            source_url=source_url,
            source_date=source_date,
            license_info=license_info
        )

    @staticmethod
    def serialize_log(provenance_log: List[Dict[str, Any]], output_path: str) -> str:
        """
        Serialize provenance log to JSON file.

        Args:
            provenance_log: List of provenance entries
            output_path: Path to save JSON file

        Returns:
            Path to saved file
        """
        with open(output_path, 'w') as f:
            json.dump(provenance_log, f, indent=2, default=str)
        return output_path

    @staticmethod
    def validate_entry(entry: Dict[str, Any]) -> bool:
        """
        Validate that a provenance entry has required fields.

        Args:
            entry: Provenance entry to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['step', 'description', 'value', 'timestamp']
        return all(field in entry for field in required_fields)

    @staticmethod
    def merge_logs(logs: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge multiple provenance logs into a single log.

        Args:
            logs: List of provenance logs to merge

        Returns:
            Merged provenance log
        """
        merged = []
        for log in logs:
            merged.extend(log)

        # Sort by timestamp
        merged.sort(key=lambda x: x.get('timestamp', ''))
        return merged
