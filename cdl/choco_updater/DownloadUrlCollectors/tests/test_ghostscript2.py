import requests
import re
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

# Try GitHub API for ghostpdl-downloads
print("=== Testing GitHub API ===")
url = 'https://api.github.com/repos/ArtifexSoftware/ghostpdl-downloads/releases/latest'

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        tag = data.get('tag_name', '')
        print(f"Tag: {tag}")

        # Extract version from tag (e.g., gs10060 -> 10.06.0)
        version_match = re.match(r'gs(\d{2})(\d{2})(\d{2,3})', tag)
        if version_match:
            major = version_match.group(1)
            minor = version_match.group(2)
            patch = version_match.group(3)
            version = f"{major}.{minor}.{patch}"
            print(f"Version: {version}")

        # Find download URLs
        assets = data.get('assets', [])
        print(f"Assets: {len(assets)}")

        for asset in assets:
            name = asset.get('name', '')
            download_url = asset.get('browser_download_url', '')
            if name.endswith('.exe'):
                print(f"  {name}: {download_url}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"Error: {e}")

