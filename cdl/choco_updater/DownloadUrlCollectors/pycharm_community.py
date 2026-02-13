import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# JetBrains Data Services API for PyCharm Community (code=PCC)
api_url = 'https://data.services.jetbrains.com/products/releases?code=PCC&type=release'

version = None
url64 = None

try:
    # Fetch all releases from API (not just latest=true)
    response = requests.get(api_url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict) and 'PCC' in data:
        pcc_data = data['PCC']

        if pcc_data and len(pcc_data) > 0:
            # Get the first (latest) release
            latest = pcc_data[0]
            api_version = latest.get('version')

            # Get Windows download link from API
            downloads = latest.get('downloads', {})
            if 'windows' in downloads:
                windows = downloads['windows']
                api_url64 = windows.get('link')

            # Now try to find newer versions by checking constructed URLs
            # Pattern from the page: https://download.jetbrains.com/python/pycharm-{version}.exe
            # Extract major.minor from API version (e.g., 2025.2 from 2025.2.5)
            parts = api_version.split('.')
            if len(parts) >= 2:
                major = parts[0]
                minor = parts[1]

                # Try incrementing minor version to find newer releases
                # Check up to 5 versions ahead
                found_newer = False
                for i in range(int(minor), int(minor) + 6):
                    test_version = f"{major}.{i}"
                    test_url = f"https://download.jetbrains.com/python/pycharm-{test_version}.exe"

                    try:
                        # Use HEAD request to check if URL exists
                        head_resp = requests.head(test_url, headers=headers, verify=False, timeout=10, allow_redirects=True)
                        if head_resp.status_code == 200:
                            version = test_version
                            url64 = test_url
                            found_newer = True
                        else:
                            # If this version doesn't exist, stop checking
                            if found_newer:
                                break
                    except:
                        # If request fails, try community variant
                        test_url_community = f"https://download.jetbrains.com/python/pycharm-community-{test_version}.exe"
                        try:
                            head_resp = requests.head(test_url_community, headers=headers, verify=False, timeout=10, allow_redirects=True)
                            if head_resp.status_code == 200:
                                version = test_version
                                url64 = test_url_community
                                found_newer = True
                            elif found_newer:
                                break
                        except:
                            if found_newer:
                                break

                # If no newer version found, use API version
                if not version:
                    version = api_version
                    url64 = api_url64

except Exception as e:
    pass

if version and url64:
    print(f"Latest Version: {version}")
    print(f"64-bit URL: {url64}")
else:
    print("Could not find PyCharm Community version or download URL")
    if not version:
        print("  Missing: version")
    if not url64:
        print("  Missing: 64-bit URL")


