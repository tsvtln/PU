import requests
import json
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== Testing different API parameters ===\n")

# Test 1: Without latest=true filter (get all releases)
print("1. All releases (no latest filter):")
api_url1 = 'https://data.services.jetbrains.com/products/releases?code=PCC&type=release'
try:
    response = requests.get(api_url1, headers=headers, verify=False, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if 'PCC' in data:
            print(f"   Found {len(data['PCC'])} releases")
            for i, release in enumerate(data['PCC'][:5]):
                print(f"   {i+1}. Version: {release.get('version')}, Date: {release.get('date')}, Type: {release.get('type')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Without type filter (get all types)
print("\n2. All types (no type filter):")
api_url2 = 'https://data.services.jetbrains.com/products/releases?code=PCC&latest=true'
try:
    response = requests.get(api_url2, headers=headers, verify=False, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if 'PCC' in data:
            print(f"   Found {len(data['PCC'])} releases")
            for i, release in enumerate(data['PCC'][:5]):
                print(f"   {i+1}. Version: {release.get('version')}, Date: {release.get('date')}, Type: {release.get('type')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: No filters at all
print("\n3. No filters:")
api_url3 = 'https://data.services.jetbrains.com/products/releases?code=PCC'
try:
    response = requests.get(api_url3, headers=headers, verify=False, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if 'PCC' in data:
            print(f"   Found {len(data['PCC'])} releases")
            for i, release in enumerate(data['PCC'][:10]):
                version = release.get('version')
                date = release.get('date')
                rtype = release.get('type')
                has_windows = 'windows' in release.get('downloads', {})
                print(f"   {i+1}. Version: {version}, Date: {date}, Type: {rtype}, Has Windows: {has_windows}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Check for 2025.3 specifically
print("\n4. Looking for version 2025.3:")
try:
    response = requests.get(api_url3, headers=headers, verify=False, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if 'PCC' in data:
            for release in data['PCC']:
                version = release.get('version', '')
                if version.startswith('2025.3'):
                    print(f"   Found: {version}")
                    print(f"   Date: {release.get('date')}")
                    print(f"   Type: {release.get('type')}")
                    downloads = release.get('downloads', {})
                    if 'windows' in downloads:
                        print(f"   Windows URL: {downloads['windows'].get('link')}")
except Exception as e:
    print(f"   Error: {e}")

