import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
domain = 'https://qgis.org'
download_page = f'{domain}/download/'

try:
    # fetch the page
    response = requests.get(download_page, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    version = None
    url64 = None

    # Find version from text like "Latest Release 3.44"
    # Look for the pattern in the page text
    page_text = soup.get_text()
    version_pattern = re.compile(r'Latest\s+Release\s+(\d+\.\d+)', re.IGNORECASE)
    version_match = version_pattern.search(page_text)

    if version_match:
        major_minor = version_match.group(1)  # e.g., "3.44"

        # Find the MSI download link (not Qt6 version)
        # Pattern: /downloads/QGIS-OSGeo4W-{version}.msi (relative URL)
        # The full version includes patch number like 3.44.5-1
        # Exclude QGISQT6 variants
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')

            # Check if it's a QGIS MSI link (not Qt6 version)
            if '/downloads/QGIS-OSGeo4W-' in href and href.endswith('.msi') and 'QT6' not in href.upper():
                # Check if it matches the major.minor version
                if f'QGIS-OSGeo4W-{major_minor}.' in href:
                    # Convert relative URL to absolute
                    if href.startswith('/'):
                        url64 = domain + href
                    elif href.startswith('http'):
                        url64 = href
                    else:
                        url64 = domain + '/' + href

                    # Extract full version from URL
                    # Example: /downloads/QGIS-OSGeo4W-3.44.5-1.msi -> 3.44.5-1
                    full_version_match = re.search(r'QGIS-OSGeo4W-(\d+\.\d+\.\d+(?:-\d+)?)', href)
                    if full_version_match:
                        version = full_version_match.group(1)
                        if '-' in version:
                            version = version.replace('-', '')
                    break

    if version and url64:
        print(f"Latest Version: {version}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not find QGIS version or download URL")
        if not version:
            print("  Missing: version")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch QGIS version: {e}")
except Exception as e:
    print(f"Error processing QGIS version: {e}")

