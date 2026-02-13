import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Test the Node.js dist page
print("=== Testing Node.js dist page ===")
url = 'https://nodejs.org/dist/'

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for version directories (e.g., v25.2.0/)
    version_pattern = re.compile(r'v(\d+\.\d+\.\d+)/')

    links = soup.find_all('a', href=True)
    print(f"Total links: {len(links)}")

    versions = []
    for link in links:
        href = link.get('href', '')
        match = version_pattern.match(href)
        if match:
            version = match.group(1)
            versions.append(version)

    if versions:
        print(f"\nFound {len(versions)} versions")
        print(f"First 10 versions: {versions[:10]}")
        print(f"Latest version: {versions[0]}")

        # Test the version-specific page
        latest_version = versions[0]
        version_url = f"https://nodejs.org/dist/v{latest_version}/"
        print(f"\n=== Testing version page: {version_url} ===")

        response2 = requests.get(version_url, headers=headers, verify=False, timeout=30)
        print(f"Status: {response2.status_code}")

        soup2 = BeautifulSoup(response2.text, 'html.parser')

        # Look for MSI files
        for link in soup2.find_all('a', href=True):
            href = link.get('href', '')
            if href.endswith('.msi'):
                print(f"  Found MSI: {href}")
    else:
        print("No versions found")

except Exception as e:
    print(f"Error: {e}")

