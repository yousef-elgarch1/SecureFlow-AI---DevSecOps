"""
Test script to verify GitHub scanning works end-to-end
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_github_scan():
    """Test GitHub repository scanning"""

    print("=" * 60)
    print("Testing GitHub Scan - NodeGoat Repository")
    print("=" * 60)

    # Test payload - NodeGoat repository
    payload = {
        "repo_url": "https://github.com/OWASP/NodeGoat",
        "branch": "master",
        "max_per_type": 5
    }

    print(f"\n1. Sending scan request...")
    print(f"   Repository: {payload['repo_url']}")
    print(f"   Branch: {payload['branch']}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/scan-github",
            json=payload,
            timeout=300  # 5 minutes timeout
        )

        print(f"\n2. Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n3. Response Data:")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Total Vulnerabilities: {data.get('total_vulns', 0)}")
            print(f"   Policies Generated: {len(data.get('results', []))}")

            if data.get('results'):
                print("\n4. Sample Policies:")
                for i, result in enumerate(data['results'][:3], 1):
                    print(f"\n   Policy {i}:")
                    print(f"   - Type: {result.get('type', 'N/A')}")
                    print(f"   - Severity: {result.get('severity', 'N/A')}")
                    print(f"   - Title: {result.get('vulnerability_title', 'N/A')[:50]}...")

                print("\nGitHub scan completed successfully!")
                print(f"Generated {len(data['results'])} security policies")
                return True
            else:
                print("\nNo results returned!")
                print("Response data:", json.dumps(data, indent=2))
                return False
        else:
            print(f"\nRequest failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\nRequest timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health():
    """Test API health"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("Backend is healthy")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to backend: {e}")
        return False

if __name__ == "__main__":
    print("\nPre-flight checks...")
    if test_health():
        print("\nStarting GitHub scan test...\n")
        success = test_github_scan()

        if success:
            print("\n" + "=" * 60)
            print("ALL TESTS PASSED")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("TEST FAILED")
            print("=" * 60)
    else:
        print("\nBackend is not running or not healthy")
        print("Please start the backend first: cd backend && ../venv/Scripts/python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
