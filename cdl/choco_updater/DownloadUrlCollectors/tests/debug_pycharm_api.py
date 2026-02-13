import requests
import json
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# JetBrains uses a data API for product releases
# Try the products releases API
print("=== Testing JetBrains Data API ===")

# JetBrains products data service
api_url = 'https://data.services.jetbrains.com/products/releases?code=PCC&latest=true&type=release'

try:
    response = requests.get(api_url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON structure: {list(data.keys()) if isinstance(data, dict) else 'Array'}")

        if isinstance(data, dict) and 'PCC' in data:
            pcc_data = data['PCC']
            print(f"\nPCC data has {len(pcc_data)} entries")

            if pcc_data:
                latest = pcc_data[0]
                print(f"\nLatest release data:")
                print(f"  Version: {latest.get('version')}")
                print(f"  Date: {latest.get('date')}")
                print(f"  Build: {latest.get('build')}")

                downloads = latest.get('downloads', {})
                print(f"\n  Available downloads: {list(downloads.keys())}")

                if 'windows' in downloads:
                    windows = downloads['windows']
                    print(f"\n  Windows download:")
                    print(f"    Link: {windows.get('link')}")
                    print(f"    Size: {windows.get('size')}")
                    print(f"    Checksum: {windows.get('checksumLink')}")

        # Print first 1000 chars of JSON for inspection
        print(f"\nFirst 1000 chars of JSON:")
        print(json.dumps(data, indent=2)[:1000])
    else:
        print(f"Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Also try other possible endpoints
print("\n\n=== Testing alternate API endpoint ===")
alt_url = 'https://data.services.jetbrains.com/products?code=PCC'
try:
    response = requests.get(alt_url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")

