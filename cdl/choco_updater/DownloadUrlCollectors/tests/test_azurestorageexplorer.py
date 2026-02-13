import requests
import re
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

# Test GitHub API for Azure Storage Explorer
print("=== Testing Azure Storage Explorer GitHub API ===")
url = 'https://api.github.com/repos/microsoft/AzureStorageExplorer/releases/latest'

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        tag = data.get('tag_name', '')
        print(f"Tag: {tag}")

        # Get assets
        assets = data.get('assets', [])
        print(f"Total assets: {len(assets)}")

        # Look for Windows installers
        for asset in assets:
            name = asset.get('name', '')
            download_url = asset.get('browser_download_url', '')
            if name.endswith('.exe'):
                print(f"  {name}")
                print(f"    URL: {download_url}")

    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"Error: {e}")

