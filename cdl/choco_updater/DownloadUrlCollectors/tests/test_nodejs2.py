import requests
from bs4 import BeautifulSoup
import re
import warnings
import sys
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
dist_url = 'https://nodejs.org/dist/'

print("Fetching Node.js dist page...", file=sys.stderr)

try:
    # fetch the dist index page with shorter timeout
    response = requests.get(dist_url, headers=headers, verify=False, timeout=10)
    response.raise_for_status()

    print("Page fetched successfully", file=sys.stderr)

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # find version directories matching pattern: v{major}.{minor}.{patch}/
    # example: v25.2.1/
    version_pattern = re.compile(r'v(\d+\.\d+\.\d+)/')

    versions = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        match = version_pattern.match(href)
        if match:
            version = match.group(1)
            versions.append(version)

    print(f"Found {len(versions)} versions", file=sys.stderr)

    if not versions:
        print("Could not find Node.js versions on dist page")
    else:
        # Parse versions and find the latest by comparing major.minor.patch
        # Convert each version string to tuple of ints for proper comparison
        # e.g., "25.2.1" -> (25, 2, 1)
        def parse_version(v):
            parts = v.split('.')
            return tuple(int(p) for p in parts)

        # Sort versions by parsed tuple (descending) and take the first
        latest_version = sorted(versions, key=parse_version, reverse=True)[0]

        print(f"Latest version after sorting: {latest_version}", file=sys.stderr)

        # Construct download URLs for the latest version
        # Format: https://nodejs.org/dist/v25.2.1/node-v25.2.1-x64.msi
        #         https://nodejs.org/dist/v25.2.1/node-v25.2.1-x86.msi
        base_url = f"https://nodejs.org/dist/v{latest_version}"
        url64 = f"{base_url}/node-v{latest_version}-x64.msi"
        url32 = f"{base_url}/node-v{latest_version}-x86.msi"

        print(f"Latest Version: {latest_version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")

except requests.Timeout:
    print(f"Timeout while fetching Node.js dist page")
except requests.RequestException as e:
    print(f"Could not fetch Node.js version: {e}")
except Exception as e:
    print(f"Error processing Node.js version: {e}")

