"""
External APIs Utility

Purpose: HTTP API wrappers with timeouts and retries for BLS/SSA/Fed calls.
Provides robust API client for fetching external economic data.
"""

import requests
from typing import Dict, Any, Optional
import time
from datetime import datetime


class ExternalAPIClient:
    """Client for making robust HTTP requests to external data APIs."""

    def __init__(self, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize API client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ForensicEconomics/0.1.0'
        })

    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a GET request with retry logic.

        Args:
            url: URL to request
            params: Query parameters
            **kwargs: Additional arguments to pass to requests.get

        Returns:
            Response JSON as dictionary

        Raises:
            requests.RequestException: If all retries fail
        """
        return self._request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a POST request with retry logic.

        Args:
            url: URL to request
            data: Form data
            json: JSON data
            **kwargs: Additional arguments to pass to requests.post

        Returns:
            Response JSON as dictionary

        Raises:
            requests.RequestException: If all retries fail
        """
        return self._request('POST', url, data=data, json=json, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Internal method to make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments

        Returns:
            Response JSON or error details
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )

                # Raise exception for HTTP errors
                response.raise_for_status()

                # Try to parse JSON
                try:
                    return response.json()
                except ValueError:
                    # Return text if not JSON
                    return {'data': response.text, 'status_code': response.status_code}

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

            except requests.exceptions.RequestException as e:
                last_exception = e
                # Don't retry on client errors (4xx)
                if hasattr(e.response, 'status_code') and 400 <= e.response.status_code < 500:
                    raise
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue

        # All retries failed
        raise last_exception if last_exception else requests.RequestException("Request failed")


class BLSClient(ExternalAPIClient):
    """Client for Bureau of Labor Statistics API."""

    BASE_URL = 'https://api.bls.gov/publicAPI/v2'

    def get_series(self, series_id: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch BLS time series data.

        Args:
            series_id: BLS series identifier
            start_year: Start year (optional)
            end_year: End year (optional)

        Returns:
            Series data as dictionary
        """
        # TODO: Implement actual BLS API call
        # For MVP, return placeholder
        return {
            'series_id': series_id,
            'data': [],
            'source': 'BLS API (placeholder)',
            'retrieved_at': datetime.utcnow().isoformat()
        }


class SSAClient(ExternalAPIClient):
    """Client for Social Security Administration data."""

    def get_life_table(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch SSA life table data.

        Args:
            year: Table year (optional, defaults to latest)

        Returns:
            Life table data
        """
        # TODO: Implement actual SSA data retrieval
        # For MVP, return placeholder
        return {
            'year': year or 2023,
            'table': {},
            'source': 'SSA Life Tables (placeholder)',
            'retrieved_at': datetime.utcnow().isoformat()
        }


class FedClient(ExternalAPIClient):
    """Client for Federal Reserve economic data."""

    BASE_URL = 'https://www.federalreserve.gov/datadownload'

    def get_treasury_rates(self) -> Dict[str, Any]:
        """
        Fetch current Treasury yield curve.

        Returns:
            Treasury rates by maturity
        """
        # TODO: Implement actual Fed data retrieval
        # For MVP, return placeholder
        return {
            'rates': {
                '1yr': 0.025,
                '2yr': 0.028,
                '5yr': 0.032,
                '10yr': 0.035,
                '30yr': 0.038
            },
            'source': 'Federal Reserve (placeholder)',
            'retrieved_at': datetime.utcnow().isoformat()
        }
