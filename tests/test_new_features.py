"""
Test script for new adaptive prompts and policy tracking features
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_profile_templates():
    """Test 1: Verify profile templates endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Profile Templates Endpoint")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/profile-templates")
    data = response.json()

    if data['success'] and len(data['templates']) >= 7:
        print(f"[PASS] SUCCESS: Found {len(data['templates'])} profile templates")
        print(f"  Templates: {', '.join(data['templates'].keys())}")
        return True
    else:
        print(f"[FAIL] Expected at least 7 templates, got {len(data.get('templates', {}))}")
        return False


def test_policy_dashboard():
    """Test 2: Verify policy dashboard endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Policy Dashboard Endpoint")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/policies/dashboard")
    data = response.json()

    if data['success']:
        stats = data['stats']
        print(f"[PASS] SUCCESS: Dashboard accessible")
        print(f"  Total policies: {stats['total_policies']}")
        print(f"  Compliance: {stats['compliance_percentage']}%")
        return True
    else:
        print(f"[FAIL] Dashboard not accessible")
        return False


def test_adaptive_prompts():
    """Test 3: Generate policies with different expertise levels"""
    print("\n" + "="*60)
    print("TEST 3: Adaptive Prompts (Beginner vs Advanced)")
    print("="*60)

    # Check if sample file exists
    sast_file = Path("data/sample_reports/sast_sample.json")
    if not sast_file.exists():
        print(f"[SKIP] Sample file not found: {sast_file}")
        return None

    print("\n[INFO] Testing BEGINNER level policy generation...")
    with open(sast_file, 'rb') as f:
        files = {'sast_file': f}
        params = {
            'max_per_type': 1,
            'expertise_level': 'beginner',
            'user_role': 'junior_developer',
            'user_name': 'Test Beginner'
        }
        response = requests.post(f"{BASE_URL}/api/generate-policies", files=files, params=params, timeout=120)

    if response.status_code == 200:
        beginner_result = response.json()
        print(f"[PASS] Beginner policy generated")

        # Check for beginner-specific content
        if beginner_result['results']:
            policy_text = json.dumps(beginner_result['results'][0])
            has_learning = "Learn" in policy_text or "Understanding" in policy_text
            if has_learning:
                print(f"  [PASS] Contains learning/educational content")
            else:
                print(f"  [WARN] Missing educational content")
    else:
        print(f"[FAIL] Beginner policy generation failed ({response.status_code})")
        return False

    print("\n[INFO] Testing ADVANCED level policy generation...")
    with open(sast_file, 'rb') as f:
        files = {'sast_file': f}
        params = {
            'max_per_type': 1,
            'expertise_level': 'advanced',
            'user_role': 'security_engineer',
            'user_name': 'Test Advanced'
        }
        response = requests.post(f"{BASE_URL}/api/generate-policies", files=files, params=params, timeout=120)

    if response.status_code == 200:
        advanced_result = response.json()
        print(f"[PASS] Advanced policy generated")

        # Check for advanced-specific content
        if advanced_result['results']:
            policy_text = json.dumps(advanced_result['results'][0])
            has_technical = "CVSS" in policy_text or "SIEM" in policy_text or "NIST" in policy_text
            if has_technical:
                print(f"  [PASS] Contains technical/compliance details")
            else:
                print(f"  [WARN] Missing technical details")
    else:
        print(f"[FAIL] Advanced policy generation failed ({response.status_code})")
        return False

    return True


def main():
    print("\n" + "="*60)
    print("SECURAI - NEW FEATURES INTEGRATION TEST")
    print("="*60)
    print("\nTesting endpoints at:", BASE_URL)

    results = []

    # Run tests
    results.append(("Profile Templates", test_profile_templates()))
    results.append(("Policy Dashboard", test_policy_dashboard()))
    results.append(("Adaptive Prompts", test_adaptive_prompts()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results:
        if result is True:
            status = "[PASS]"
        elif result is False:
            status = "[FAIL]"
        else:
            status = "[SKIP]"
        print(f"{status:10} {test_name}")

    passed = sum(1 for _, r in results if r is True)
    total = len([r for r in results if r[1] is not None])

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Features are fully integrated.")
    else:
        print("\n[WARNING] Some tests failed. Check output above.")


if __name__ == "__main__":
    main()
