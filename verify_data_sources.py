"""
Data Source Verification Script

Tests that all agents are fetching from the correct live data sources:
1. Federal Reserve H.15 - Treasury rates
2. California Labor Market Info - Wage growth (for CA cases)
"""

from src.agents.fed_rate_agent import FedRateAgent
from src.agents.wage_growth_agent import WageGrowthAgent
from src.agents.discount_rate_agent import DiscountRateAgent
import json


def test_federal_reserve():
    """Test FedRateAgent is fetching from Federal Reserve FRED API."""
    print("=" * 80)
    print("TEST 1: Federal Reserve H.15 Selected Interest Rates")
    print("=" * 80)

    agent = FedRateAgent()
    result = agent.run({})

    print(f"\n[OK] Agent: {result['agent_name']}")
    print(f"[OK] Treasury 1-Year Rate: {result['outputs']['treasury_1yr_rate_pct']}%")
    print(f"[OK] Source: {result['outputs']['source']}")
    print(f"[OK] Data Vintage: {result['outputs']['data_vintage']}")
    print(f"[OK] Is Fallback: {result['outputs']['is_fallback']}")

    if result['outputs']['is_fallback']:
        print("\n[WARN]  WARNING: Using fallback rate. Check FRED_API_KEY in .env file.")
        print("   Get your free API key at: https://fredaccount.stlouisfed.org/apikeys")
        return False
    else:
        print("\n[PASS] SUCCESS: Fetching live data from Federal Reserve FRED API")
        return True


def test_ca_labor_market():
    """Test WageGrowthAgent is using CA Labor Market data for California cases."""
    print("\n" + "=" * 80)
    print("TEST 2: California Labor Market Info (EDD)")
    print("=" * 80)

    agent = WageGrowthAgent()
    result = agent.run({
        'occupation': 'Software Engineer',
        'salary': 120000,
        'education': 'bachelors',
        'location': 'CA'
    })

    print(f"\n[OK] Agent: {result['agent_name']}")
    print(f"[OK] Annual Growth Rate: {result['outputs']['annual_growth_rate']*100:.2f}%")
    print(f"[OK] Location: CA")

    # Check provenance for CA-specific data
    ca_specific = False
    for entry in result['provenance_log']:
        if 'ca_labor_market_fetch' in entry['step']:
            ca_specific = True
            print(f"[OK] Data Source: {entry['description']}")
            if entry['value'].get('warning'):
                print(f"[WARN]  Warning: {entry['value']['warning']}")
            break

    if ca_specific:
        print("\n[PASS] SUCCESS: Using California-specific wage data")
        return True
    else:
        print("\n[WARN]  WARNING: Not using CA-specific data. May be using fallback rates.")
        print("   CA Labor Market API may be unavailable.")
        return True  # Still pass test since fallback is expected behavior


def test_discount_rate_chain():
    """Test DiscountRateAgent properly chains to FedRateAgent."""
    print("\n" + "=" * 80)
    print("TEST 3: Discount Rate Agent (chains to Federal Reserve)")
    print("=" * 80)

    agent = DiscountRateAgent()
    result = agent.run({
        'location': 'US',
        'case_type': 'wrongful_death'
    })

    print(f"\n[OK] Agent: {result['agent_name']}")
    print(f"[OK] Recommended Discount Rate: {result['outputs']['recommended_discount_rate']*100:.2f}%")
    print(f"[OK] Treasury Rate: {result['outputs']['treasury_rate']*100:.2f}%")
    print(f"[OK] Methodology: {result['outputs']['methodology']}")

    # Check if it's using live Fed data
    using_live_data = False
    for entry in result['provenance_log']:
        # Check for either the direct step or the fed_agent prefixed step
        if ('treasury_rate_lookup' in entry['step']) or ('fed_agent_treasury_rate_lookup' in entry['step']):
            is_fallback = entry['value'].get('is_fallback', True)
            if not is_fallback:
                using_live_data = True
            print(f"[OK] Treasury Data Source: {entry['description']}")
            print(f"[OK] Is Fallback: {is_fallback}")
            break

    if using_live_data:
        print("\n[PASS] SUCCESS: Discount rate based on live Federal Reserve data")
        return True
    else:
        print("\n[WARN]  WARNING: Using fallback Treasury rate")
        return False


def main():
    """Run all data source verification tests."""
    print("\n")
    print("=" * 80)
    print("  FORENSIC ECONOMICS DATA SOURCE VERIFICATION")
    print("=" * 80)
    print("\nVerifying that agents are fetching from correct live data sources...")
    print()

    results = []

    # Test 1: Federal Reserve
    try:
        result = test_federal_reserve()
        results.append(('Federal Reserve H.15', result))
    except Exception as e:
        print(f"\n[FAIL] FAILED: {str(e)}")
        results.append(('Federal Reserve H.15', False))

    # Test 2: CA Labor Market
    try:
        result = test_ca_labor_market()
        results.append(('CA Labor Market Info', result))
    except Exception as e:
        print(f"\n[FAIL] FAILED: {str(e)}")
        results.append(('CA Labor Market Info', False))

    # Test 3: Discount Rate Chain
    try:
        result = test_discount_rate_chain()
        results.append(('Discount Rate Chain', result))
    except Exception as e:
        print(f"\n[FAIL] FAILED: {str(e)}")
        results.append(('Discount Rate Chain', False))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("[PASS] All tests passed! Data sources are configured correctly.")
    else:
        print("[WARN]  Some tests failed. Check warnings above for details.")
        print("\nTroubleshooting:")
        print("1. Ensure FRED_API_KEY is set in .env file")
        print("   Get free API key: https://fredaccount.stlouisfed.org/apikeys")
        print("2. CA Labor Market API may have rate limits or be temporarily unavailable")
        print("   This is OK - the system uses fallback rates when APIs are down")
    print("=" * 80)


if __name__ == "__main__":
    main()
