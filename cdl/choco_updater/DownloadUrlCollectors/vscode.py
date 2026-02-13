import requests
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# VSCode update API endpoint (32-bit is no longer supported/used based on update.ps1)
# the API endpoint format: /api/update/{platform}/{quality}/{version}
# using 'latest' to get the latest version info
releases64 = 'https://update.code.visualstudio.com/api/update/win32-x64-user/stable/latest'

# fetch JSON data for 64-bit
try:
    response64 = requests.get(releases64, headers=headers, verify=False, allow_redirects=False)

    # the API may return a 302 redirect to the actual download
    if response64.status_code == 302 or response64.status_code == 301:
        # get redirect location which contains version info
        download_url = response64.headers.get('Location', '')

        # extract version from URL like: https://update.code.visualstudio.com/1.96.2/win32-x64-user/stable
        import re
        version_match = re.search(r'/(\d+\.\d+\.\d+)/', download_url)
        version = version_match.group(1) if version_match else None
        url64 = download_url
    else:
        response64.raise_for_status()
        json64 = response64.json()
        version = json64.get('productVersion')
        url64 = json64.get('url')
except Exception as e:
    version = None
    url64 = None
    print(f"Error fetching from VSCode API: {e}")

if version and url64:
    print(f"Latest Version: {version}")
    print(f"64-bit URL: {url64}")
else:
    print("Could not get version or download URL from VSCode API")

