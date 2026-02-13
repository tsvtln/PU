import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
download_page = 'https://www.microsoft.com/en-us/download/details.aspx?id=56041'

try:
    # fetch the page
    response = requests.get(download_page, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = response.text

    version = None
    url32 = None
    url64 = None

    # Find version on Microsoft download pages
    # Version is typically in the page title or metadata
    # Pattern: look for version numbers like 11.0.7001.0
    version_pattern = re.compile(r'\b(\d+\.\d+\.\d+\.\d+)\b')
    version_matches = version_pattern.findall(page_text)

    if version_matches:
        # Get the first version found (should be the package version)
        version = version_matches[0]

    # Microsoft download pages often have download links in specific formats
    # Look for sqlncli MSI files
    # Pattern: sqlncli_x64.msi and sqlncli_x86.msi or similar

    # Try to find direct download links
    msi_pattern_64 = re.compile(r'(https://download\.microsoft\.com/[^"\s<>]+sqlncli[^"\s<>]*x64[^"\s<>]*\.msi)', re.IGNORECASE)
    msi_pattern_32 = re.compile(r'(https://download\.microsoft\.com/[^"\s<>]+sqlncli[^"\s<>]*x86[^"\s<>]*\.msi)', re.IGNORECASE)

    match_64 = msi_pattern_64.search(page_text)
    match_32 = msi_pattern_32.search(page_text)

    if match_64:
        url64 = match_64.group(1)
    if match_32:
        url32 = match_32.group(1)

    # Fallback: Look for any download.microsoft.com links and filter
    if not url64 or not url32:
        all_download_links = re.findall(r'(https://download\.microsoft\.com/[^"\s<>]+\.msi)', page_text, re.IGNORECASE)

        for link in all_download_links:
            if 'sqlncli' in link.lower():
                if 'x64' in link.lower() and not url64:
                    url64 = link
                elif 'x86' in link.lower() and not url32:
                    url32 = link

    # Another fallback: Check for links in anchor tags
    if not url64 or not url32:
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'download.microsoft.com' in href and '.msi' in href.lower() and 'sqlncli' in href.lower():
                if 'x64' in href.lower() and not url64:
                    url64 = href
                elif 'x86' in href.lower() and not url32:
                    url32 = href

    if version and (url32 or url64):
        print(f"Latest Version: {version}")
        if url32:
            print(f"32-bit URL: {url32}")
        if url64:
            print(f"64-bit URL: {url64}")
    else:
        print("Could not find SQL Server 2012 Native Client version or download URLs")
        if not version:
            print("  Missing: version")
        if not url32:
            print("  Missing: 32-bit URL")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch SQL Server 2012 Native Client info: {e}")
except Exception as e:
    print(f"Error processing SQL Server 2012 Native Client info: {e}")

