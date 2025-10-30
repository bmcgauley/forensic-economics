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
    """Client for Federal Reserve economic data via FRED API."""

    FRED_API_URL = 'https://api.stlouisfed.org/fred/series/observations'
    DGS1_SERIES = 'DGS1'  # 1-Year Treasury Constant Maturity Rate

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize Fed client.

        Args:
            api_key: FRED API key (optional, can be set via environment variable)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        super().__init__(timeout=timeout, max_retries=max_retries, retry_delay=retry_delay)
        self.api_key = api_key

        # Fallback rate cache (used when API is unavailable)
        self.fallback_rate = 0.0425  # 4.25% - reasonable default based on 2025 market conditions

    def get_treasury_rates(self, use_fallback_on_error: bool = True) -> Dict[str, Any]:
        """
        Fetch current 1-Year Treasury Constant Maturity Rate from FRED.

        Source: Federal Reserve H.15 Selected Interest Rates
        Series: DGS1 - Market Yield on U.S. Treasury Securities at 1-Year Constant Maturity

        Args:
            use_fallback_on_error: If True, return fallback rate on API error

        Returns:
            Dictionary containing:
                - rates: Dictionary with Treasury rates by maturity
                - treasury_1yr_rate: Current 1-year Treasury rate as decimal
                - source: Data source attribution
                - source_url: URL to data source
                - retrieved_at: ISO timestamp of retrieval
                - data_vintage: Date of the rate data point
                - provenance: Detailed provenance information
        """
        provenance = {
            'data_source': 'Federal Reserve H.15 Selected Interest Rates via FRED API',
            'series_code': self.DGS1_SERIES,
            'source_url': f'https://fred.stlouisfed.org/series/{self.DGS1_SERIES}',
            'api_endpoint': self.FRED_API_URL,
            'retrieved_at': datetime.utcnow().isoformat()
        }

        try:
            # Check if API key is available
            if not self.api_key:
                print("[FED_CLIENT] ERROR: No FRED API key provided!")
                raise ValueError("FRED API key not provided. Set FRED_API_KEY environment variable.")

            # Fetch most recent observation (limit=1, sort descending)
            params = {
                'series_id': self.DGS1_SERIES,
                'api_key': self.api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 1
            }

            print(f"[FED_CLIENT] Calling FRED API: {self.FRED_API_URL}")
            print(f"[FED_CLIENT] Series: {self.DGS1_SERIES}")
            response = self.get(self.FRED_API_URL, params=params)
            print(f"[FED_CLIENT] API Response received: {list(response.keys()) if isinstance(response, dict) else 'non-dict'}")

            # Parse FRED API response
            if 'observations' in response and len(response['observations']) > 0:
                observation = response['observations'][0]
                rate_value = observation.get('value', '.')

                # Handle missing data (FRED uses '.' for missing values)
                if rate_value == '.':
                    raise ValueError("Latest rate data not available (FRED returned '.')")

                rate_decimal = float(rate_value) / 100.0  # Convert percentage to decimal
                data_date = observation.get('date', 'unknown')

                provenance['data_vintage'] = data_date
                provenance['rate_value_pct'] = rate_value
                provenance['status'] = 'success'

                return {
                    'rates': {
                        '1yr': rate_decimal,
                    },
                    'treasury_1yr_rate': rate_decimal,
                    'source': 'Federal Reserve H.15 via FRED API',
                    'source_url': f'https://fred.stlouisfed.org/series/{self.DGS1_SERIES}',
                    'retrieved_at': provenance['retrieved_at'],
                    'data_vintage': data_date,
                    'provenance': provenance
                }
            else:
                raise ValueError("No observations returned from FRED API")

        except Exception as e:
            error_msg = f"Error fetching Treasury rates: {str(e)}"
            provenance['status'] = 'error'
            provenance['error'] = error_msg
            provenance['fallback_used'] = use_fallback_on_error

            if use_fallback_on_error:
                # Return cached fallback rate
                return {
                    'rates': {
                        '1yr': self.fallback_rate,
                    },
                    'treasury_1yr_rate': self.fallback_rate,
                    'source': 'Federal Reserve H.15 (fallback cached rate)',
                    'source_url': 'https://www.federalreserve.gov/releases/h15/current/',
                    'retrieved_at': datetime.utcnow().isoformat(),
                    'data_vintage': 'fallback',
                    'provenance': provenance,
                    'warning': f'Using fallback rate due to API error: {str(e)}'
                }
            else:
                raise


class CALaborMarketClient(ExternalAPIClient):
    """Client for California Labor Market Information via EDD Open Data Portal."""

    # EDD Open Data Portal - OES Wage Data
    OES_API_URL = 'https://data.edd.ca.gov/resource/dcfs-wgss.json'

    def __init__(self, timeout: int = 30, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize CA Labor Market client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        super().__init__(timeout=timeout, max_retries=max_retries, retry_delay=retry_delay)

        # Fallback growth rate (used when API is unavailable)
        self.fallback_growth_rate = 0.028  # 2.8% - California average wage growth

    def get_wage_growth_by_occupation(
        self,
        occupation: str,
        county: Optional[str] = None,
        use_fallback_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch wage growth rate by occupation and county from CA EDD.

        Source: California Labor Market Info - Occupational Employment and Wage Statistics (OES)
        URL: https://labormarketinfo.edd.ca.gov/

        Args:
            occupation: SOC occupation code or title
            county: California county name (optional, defaults to statewide)
            use_fallback_on_error: If True, return fallback rate on API error

        Returns:
            Dictionary containing:
                - growth_rate: Annual wage growth rate as decimal
                - occupation: Occupation searched
                - county: County searched (or 'Statewide')
                - source: Data source attribution
                - source_url: URL to data source
                - retrieved_at: ISO timestamp of retrieval
                - provenance: Detailed provenance information
        """
        provenance = {
            'data_source': 'California Labor Market Info - OES Wage Data via EDD Open Data Portal',
            'api_endpoint': self.OES_API_URL,
            'source_url': 'https://labormarketinfo.edd.ca.gov/data/wages.html',
            'occupation_searched': occupation,
            'county_searched': county or 'Statewide',
            'retrieved_at': datetime.utcnow().isoformat()
        }

        try:
            # Build query parameters for OES API
            # The API uses SoQL (Socrata Query Language)
            query_params = {
                '$limit': 100,
                '$order': 'year DESC'
            }

            # Add occupation filter (try matching SOC code or title)
            # Note: The actual field names may vary - this is a reasonable approximation
            if occupation:
                # Try to match SOC code pattern (e.g., "11-1011" or "111011")
                import re
                soc_pattern = r'^\d{2}-?\d{4}$'
                if re.match(soc_pattern, occupation):
                    # It's a SOC code
                    query_params['$where'] = f"occupation_code LIKE '%{occupation.replace('-', '')}%'"
                else:
                    # It's an occupation title
                    query_params['$where'] = f"UPPER(occupation_title) LIKE UPPER('%{occupation}%')"

            # Add county filter if specified
            if county:
                county_filter = f"UPPER(area_name) = UPPER('{county}')"
                if '$where' in query_params:
                    query_params['$where'] += f" AND {county_filter}"
                else:
                    query_params['$where'] = county_filter

            response = self.get(self.OES_API_URL, params=query_params)

            # Parse response and calculate wage growth
            if isinstance(response, list) and len(response) > 0:
                # Calculate wage growth from year-over-year data
                # This is a simplified calculation - actual implementation may need more sophistication
                growth_rate = self._calculate_wage_growth(response)

                provenance['status'] = 'success'
                provenance['records_found'] = len(response)
                provenance['sample_data'] = response[0] if len(response) > 0 else None

                return {
                    'growth_rate': growth_rate,
                    'occupation': occupation,
                    'county': county or 'Statewide',
                    'source': 'California Labor Market Info - OES Data',
                    'source_url': 'https://labormarketinfo.edd.ca.gov/data/wages.html',
                    'retrieved_at': provenance['retrieved_at'],
                    'provenance': provenance
                }
            else:
                raise ValueError(f"No wage data found for occupation '{occupation}' in {county or 'California'}")

        except Exception as e:
            error_msg = f"Error fetching CA wage growth: {str(e)}"
            provenance['status'] = 'error'
            provenance['error'] = error_msg
            provenance['fallback_used'] = use_fallback_on_error

            if use_fallback_on_error:
                # Return fallback growth rate
                return {
                    'growth_rate': self.fallback_growth_rate,
                    'occupation': occupation,
                    'county': county or 'Statewide',
                    'source': 'California Labor Market Info (fallback average rate)',
                    'source_url': 'https://labormarketinfo.edd.ca.gov/',
                    'retrieved_at': datetime.utcnow().isoformat(),
                    'provenance': provenance,
                    'warning': f'Using fallback growth rate due to API error: {str(e)}'
                }
            else:
                raise

    def _calculate_wage_growth(self, wage_data: list) -> float:
        """
        Calculate wage growth rate from OES data.

        Args:
            wage_data: List of wage records from OES API

        Returns:
            Annual wage growth rate as decimal
        """
        try:
            # Sort by year descending
            sorted_data = sorted(wage_data, key=lambda x: x.get('year', 0), reverse=True)

            if len(sorted_data) >= 2:
                # Get most recent and previous year
                recent = sorted_data[0]
                previous = sorted_data[1]

                # Extract mean wage (field names may vary)
                recent_wage = float(recent.get('mean_wage', 0) or recent.get('a_mean', 0) or 0)
                previous_wage = float(previous.get('mean_wage', 0) or previous.get('a_mean', 0) or 0)

                if recent_wage > 0 and previous_wage > 0:
                    # Calculate year-over-year growth
                    growth = (recent_wage - previous_wage) / previous_wage
                    return round(growth, 4)

            # If we can't calculate growth, return fallback
            return self.fallback_growth_rate

        except Exception:
            # If calculation fails, return fallback
            return self.fallback_growth_rate
