import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
download_page = 'https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17'

try:
    # fetch the page
    response = requests.get(download_page, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text()

    version = None
    url32 = None
    url64 = None

    # Find version from text like "Release number: 18.5.2.1"
    version_pattern = re.compile(r'Release\s+number:\s*(\d+\.\d+\.\d+\.\d+)', re.IGNORECASE)
    version_match = version_pattern.search(page_text)

    if version_match:
        version = version_match.group(1)

    # Find download links for ODBC Driver
    # Pattern: "Download Microsoft ODBC Driver 18 for SQL Server (x64)"
    # Pattern: "Download Microsoft ODBC Driver 18 for SQL Server (x86)"
    # Links are typically go.microsoft.com redirect links like:
    # https://go.microsoft.com/fwlink/?linkid=2335671

    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)

        # Check if it's an ODBC Driver download link
        if 'go.microsoft.com/fwlink' in href.lower():
            # Check link text to determine architecture
            if 'odbc driver' in text.lower() and 'sql server' in text.lower():
                if '(x64)' in text:
                    url64 = href
                elif '(x86)' in text:
                    url32 = href

    # Fallback: Look for any go.microsoft.com links in the page
    if not url64 or not url32:
        # Find all go.microsoft.com fwlink URLs
        fwlink_pattern = re.compile(r'(https://go\.microsoft\.com/fwlink/\?linkid=\d+)', re.IGNORECASE)
        fwlinks = fwlink_pattern.findall(response.text)

        if len(fwlinks) >= 2:
            # Typically, the first two fwlinks on the ODBC page are x64 and x86
            # We need to check the context around each link
            for fwlink in fwlinks:
                # Find the context around this link in the page text
                link_index = response.text.find(fwlink)
                if link_index != -1:
                    # Get surrounding text (500 chars before and after)
                    context_start = max(0, link_index - 500)
                    context_end = min(len(response.text), link_index + 500)
                    context = response.text[context_start:context_end].lower()

                    if 'x64' in context or '(64)' in context:
                        if not url64:
                            url64 = fwlink
                    elif 'x86' in context or '(86)' in context or '32-bit' in context:
                        if not url32:
                            url32 = fwlink

    if version and (url32 or url64):
        print(f"Latest Version: {version}")
        if url32:
            print(f"32-bit URL: {url32}")
        if url64:
            print(f"64-bit URL: {url64}")
    else:
        print("Could not find SQL Server ODBC Driver version or download URLs")
        if not version:
            print("  Missing: version")
        if not url32:
            print("  Missing: 32-bit URL")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch SQL Server ODBC Driver info: {e}")
except Exception as e:
    print(f"Error processing SQL Server ODBC Driver info: {e}")

