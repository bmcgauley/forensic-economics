"""
Integration Tests for Live API Clients

Purpose: Test Federal Reserve H.15 and CA Labor Market Info API integrations.
Tests include real API calls (when credentials available) and fallback mechanisms.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.utils.external_apis import FedClient, CALaborMarketClient


class TestFedClient:
    """Test Federal Reserve FRED API client."""

    def test_get_treasury_rates_with_mock_success(self):
        """Test successful Treasury rate fetch with mocked API response."""
        # Mock FRED API response
        mock_response = {
            'observations': [
                {
                    'date': '2025-10-28',
                    'value': '4.25'
                }
            ]
        }

        with patch.object(FedClient, 'get', return_value=mock_response):
            client = FedClient(api_key='test_key')
            result = client.get_treasury_rates()

            # Verify result structure
            assert 'treasury_1yr_rate' in result
            assert 'rates' in result
            assert 'source' in result
            assert 'retrieved_at' in result
            assert 'data_vintage' in result
            assert 'provenance' in result

            # Verify rate conversion (4.25% → 0.0425)
            assert result['treasury_1yr_rate'] == 0.0425
            assert result['rates']['1yr'] == 0.0425
            assert result['data_vintage'] == '2025-10-28'

            # Verify provenance
            assert result['provenance']['status'] == 'success'
            assert result['provenance']['series_code'] == 'DGS1'

    def test_get_treasury_rates_with_missing_api_key(self):
        """Test Treasury rate fetch fails gracefully without API key."""
        client = FedClient()  # No API key provided
        result = client.get_treasury_rates(use_fallback_on_error=True)

        # Should return fallback rate
        assert 'treasury_1yr_rate' in result
        assert 'warning' in result
        assert result['treasury_1yr_rate'] == client.fallback_rate
        assert result['provenance']['status'] == 'error'
        assert result['provenance']['fallback_used'] is True

    def test_get_treasury_rates_with_missing_data(self):
        """Test Treasury rate fetch handles missing data from FRED."""
        # Mock FRED API response with missing value
        mock_response = {
            'observations': [
                {
                    'date': '2025-10-28',
                    'value': '.'  # FRED uses '.' for missing data
                }
            ]
        }

        with patch.object(FedClient, 'get', return_value=mock_response):
            client = FedClient(api_key='test_key')
            result = client.get_treasury_rates(use_fallback_on_error=True)

            # Should return fallback rate
            assert result['treasury_1yr_rate'] == client.fallback_rate
            assert 'warning' in result
            assert result['provenance']['status'] == 'error'

    def test_get_treasury_rates_with_empty_response(self):
        """Test Treasury rate fetch handles empty API response."""
        mock_response = {'observations': []}

        with patch.object(FedClient, 'get', return_value=mock_response):
            client = FedClient(api_key='test_key')
            result = client.get_treasury_rates(use_fallback_on_error=True)

            # Should return fallback rate
            assert result['treasury_1yr_rate'] == client.fallback_rate
            assert 'warning' in result

    def test_get_treasury_rates_without_fallback_raises(self):
        """Test Treasury rate fetch raises exception when fallback disabled."""
        client = FedClient()  # No API key

        with pytest.raises(ValueError):
            client.get_treasury_rates(use_fallback_on_error=False)

    def test_provenance_data_captured(self):
        """Test provenance data is correctly captured."""
        mock_response = {
            'observations': [
                {
                    'date': '2025-10-28',
                    'value': '3.50'
                }
            ]
        }

        with patch.object(FedClient, 'get', return_value=mock_response):
            client = FedClient(api_key='test_key')
            result = client.get_treasury_rates()

            provenance = result['provenance']
            assert provenance['data_source'] == 'Federal Reserve H.15 Selected Interest Rates via FRED API'
            assert provenance['series_code'] == 'DGS1'
            assert 'source_url' in provenance
            assert 'api_endpoint' in provenance
            assert 'retrieved_at' in provenance
            assert provenance['data_vintage'] == '2025-10-28'
            assert provenance['rate_value_pct'] == '3.50'


class TestCALaborMarketClient:
    """Test California Labor Market Info EDD API client."""

    def test_get_wage_growth_with_mock_success(self):
        """Test successful wage growth fetch with mocked API response."""
        # Mock CA EDD OES API response with two years of data
        mock_response = [
            {
                'year': '2024',
                'occupation_code': '15-1252',
                'occupation_title': 'Software Developers',
                'area_name': 'California',
                'mean_wage': '150000',
                'a_mean': '150000'
            },
            {
                'year': '2023',
                'occupation_code': '15-1252',
                'occupation_title': 'Software Developers',
                'area_name': 'California',
                'mean_wage': '145000',
                'a_mean': '145000'
            }
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252', 'California')

            # Verify result structure
            assert 'growth_rate' in result
            assert 'occupation' in result
            assert 'county' in result
            assert 'source' in result
            assert 'retrieved_at' in result
            assert 'provenance' in result

            # Verify growth calculation: (150000 - 145000) / 145000 = 0.0345
            expected_growth = round((150000 - 145000) / 145000, 4)
            assert result['growth_rate'] == expected_growth

            # Verify provenance
            assert result['provenance']['status'] == 'success'
            assert result['provenance']['records_found'] == 2

    def test_get_wage_growth_with_soc_code(self):
        """Test wage growth fetch with SOC code format."""
        mock_response = [
            {'year': '2024', 'mean_wage': '100000'},
            {'year': '2023', 'mean_wage': '95000'}
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252')

            assert result['occupation'] == '15-1252'
            assert 'growth_rate' in result

    def test_get_wage_growth_with_occupation_title(self):
        """Test wage growth fetch with occupation title."""
        mock_response = [
            {'year': '2024', 'mean_wage': '100000'},
            {'year': '2023', 'mean_wage': '95000'}
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('Software Developer')

            assert result['occupation'] == 'Software Developer'
            assert 'growth_rate' in result

    def test_get_wage_growth_with_county_filter(self):
        """Test wage growth fetch with county filter."""
        mock_response = [
            {'year': '2024', 'mean_wage': '120000', 'area_name': 'Santa Clara'},
            {'year': '2023', 'mean_wage': '115000', 'area_name': 'Santa Clara'}
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252', county='Santa Clara')

            assert result['county'] == 'Santa Clara'
            assert 'growth_rate' in result

    def test_get_wage_growth_with_no_data_found(self):
        """Test wage growth fetch handles no data found."""
        mock_response = []

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('99-9999', use_fallback_on_error=True)

            # Should return fallback rate
            assert result['growth_rate'] == client.fallback_growth_rate
            assert 'warning' in result
            assert result['provenance']['status'] == 'error'

    def test_get_wage_growth_with_insufficient_years(self):
        """Test wage growth calculation with only one year of data."""
        mock_response = [
            {'year': '2024', 'mean_wage': '100000'}
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252')

            # Should return fallback rate when can't calculate growth
            assert result['growth_rate'] == client.fallback_growth_rate

    def test_get_wage_growth_with_api_error(self):
        """Test wage growth fetch handles API errors."""
        with patch.object(CALaborMarketClient, 'get', side_effect=Exception('API Error')):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252', use_fallback_on_error=True)

            # Should return fallback rate
            assert result['growth_rate'] == client.fallback_growth_rate
            assert 'warning' in result
            assert result['provenance']['status'] == 'error'

    def test_get_wage_growth_without_fallback_raises(self):
        """Test wage growth fetch raises exception when fallback disabled."""
        mock_response = []

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()

            with pytest.raises(ValueError):
                client.get_wage_growth_by_occupation('99-9999', use_fallback_on_error=False)

    def test_provenance_data_captured(self):
        """Test provenance data is correctly captured."""
        mock_response = [
            {'year': '2024', 'mean_wage': '100000'},
            {'year': '2023', 'mean_wage': '95000'}
        ]

        with patch.object(CALaborMarketClient, 'get', return_value=mock_response):
            client = CALaborMarketClient()
            result = client.get_wage_growth_by_occupation('15-1252', county='Santa Clara')

            provenance = result['provenance']
            assert provenance['data_source'] == 'California Labor Market Info - OES Wage Data via EDD Open Data Portal'
            assert provenance['occupation_searched'] == '15-1252'
            assert provenance['county_searched'] == 'Santa Clara'
            assert 'api_endpoint' in provenance
            assert 'source_url' in provenance
            assert 'retrieved_at' in provenance
            assert provenance['status'] == 'success'


class TestAPIIntegration:
    """Integration tests for API client coordination."""

    def test_both_apis_can_be_instantiated(self):
        """Test that both API clients can be instantiated together."""
        fed_client = FedClient(api_key='test_key')
        ca_client = CALaborMarketClient()

        assert fed_client is not None
        assert ca_client is not None
        assert fed_client.fallback_rate == 0.0425
        assert ca_client.fallback_growth_rate == 0.028

    def test_fallback_behavior_consistent(self):
        """Test that fallback behavior is consistent across clients."""
        with patch.object(FedClient, 'get', side_effect=Exception('Network error')):
            fed_client = FedClient(api_key='test_key')
            fed_result = fed_client.get_treasury_rates(use_fallback_on_error=True)

        with patch.object(CALaborMarketClient, 'get', side_effect=Exception('Network error')):
            ca_client = CALaborMarketClient()
            ca_result = ca_client.get_wage_growth_by_occupation('15-1252', use_fallback_on_error=True)

        # Both should have fallback indicators
        assert 'warning' in fed_result
        assert 'warning' in ca_result
        assert fed_result['provenance']['fallback_used'] is True
        assert ca_result['provenance']['fallback_used'] is True


@pytest.mark.skipif(
    True,  # Set to False to enable live API testing with real credentials
    reason="Live API tests disabled by default to avoid rate limits"
)
class TestLiveAPIs:
    """
    Live API tests (disabled by default).

    To run these tests:
    1. Set FRED_API_KEY environment variable
    2. Change skipif condition above to False
    3. Run: pytest tests/integration/test_live_apis.py::TestLiveAPIs -v
    """

    def test_live_fred_api_call(self):
        """Test real FRED API call (requires FRED_API_KEY env var)."""
        import os
        api_key = os.environ.get('FRED_API_KEY')

        if not api_key:
            pytest.skip("FRED_API_KEY not set")

        client = FedClient(api_key=api_key)
        result = client.get_treasury_rates(use_fallback_on_error=False)

        assert result['treasury_1yr_rate'] > 0
        assert result['provenance']['status'] == 'success'

    def test_live_ca_edd_api_call(self):
        """Test real CA EDD API call."""
        client = CALaborMarketClient()
        result = client.get_wage_growth_by_occupation('15-1252', use_fallback_on_error=False)

        assert result['growth_rate'] >= 0
        assert result['provenance']['status'] == 'success'
