import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.citrix.com/downloads/workspace-app/workspace-app-for-windows-long-term-service-release/workspace-app-for-windows-LTSR-Latest.html'

print("=== Testing Citrix Workspace download page ===")

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for version text
    print("\n=== Looking for version text ===")
    page_text = soup.get_text()
    lines = page_text.split('\n')
    for i, line in enumerate(lines[:300]):
        if 'version' in line.lower() and ('24' in line or '2402' in line):
            print(f"Line {i}: {line.strip()[:150]}")

    # Look for LTSR patterns
    print("\n=== Looking for LTSR patterns ===")
    ltsr_pattern = re.compile(r'LTSR\s+\d{4}[^<>\n]{0,100}', re.IGNORECASE)
    matches = ltsr_pattern.findall(page_text)
    for i, match in enumerate(matches[:10]):
        print(f"{i+1}. {match.strip()[:150]}")

    # Look for version pattern 24.2.4001.1
    print("\n=== Looking for specific version pattern ===")
    version_pattern = re.compile(r'\d{2}\.\d+\.\d{4}\.\d+')
    matches = version_pattern.findall(page_text)
    for match in matches[:10]:
        print(f"  Found: {match}")

    # Look for downloads.citrix.com links with parameters
    print("\n=== Looking for download links ===")
    download_pattern = re.compile(r'https://downloads\.citrix\.com/[^\s"\'<>]+')
    matches = download_pattern.findall(response.text)
    for i, match in enumerate(matches[:5]):
        print(f"{i+1}. {match[:200]}")

    # Look specifically for __gda__ parameters
    print("\n=== Looking for __gda__ parameters ===")
    gda_pattern = re.compile(r'__gda__=[^\s"\'&<>]+')
    gda_matches = gda_pattern.findall(response.text)
    if gda_matches:
        for i, match in enumerate(gda_matches[:5]):
            print(f"{i+1}. {match[:200]}")
    else:
        print("No __gda__ parameters found in page source")

    # Look for download URLs with full query strings
    print("\n=== Looking for full download URLs with query params ===")
    full_url_pattern = re.compile(r'https://downloads\.citrix\.com/\d+/[^?\s"\'<>]+\?[^\s"\'<>]+')
    full_matches = full_url_pattern.findall(response.text)
    if full_matches:
        for i, match in enumerate(full_matches[:3]):
            print(f"{i+1}. {match}")
    else:
        print("No full URLs with query params found")

    # Look for Offline Installer buttons/links
    print("\n=== Looking for Offline Installer elements ===")
    for element in soup.find_all(['a', 'button', 'div']):
        text = element.get_text(strip=True)
        if 'offline' in text.lower() and 'installer' in text.lower():
            print(f"Element: {element.name}")
            print(f"  Text: {text[:100]}")
            print(f"  Attributes: {dict(element.attrs)}")
            print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

