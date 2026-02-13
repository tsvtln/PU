import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://qgis.org/download/'

print("=== Testing QGIS download page ===")

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for "Latest Release" in text
    print("\n=== Looking for Latest Release text ===")
    page_text = soup.get_text()
    lines = page_text.split('\n')
    for i, line in enumerate(lines[:200]):
        if 'latest' in line.lower() and ('release' in line.lower() or '3.' in line or '4.' in line):
            print(f"Line {i}: {line.strip()[:150]}")

    # Look for MSI download links
    print("\n=== Looking for MSI download links ===")
    links = soup.find_all('a', href=True)
    print(f"Total links: {len(links)}")

    msi_links = []
    for link in links:
        href = link.get('href', '')
        if '.msi' in href and 'qgis' in href.lower():
            msi_links.append(href)
            print(f"  Found: {href}")

    if not msi_links:
        print("No .msi links with qgis found")
        print("\n=== Looking for any qgis.org links ===")
        for link in links[:50]:
            href = link.get('href', '')
            if 'qgis.org' in href:
                print(f"  {href}")

    # Look for buttons or specific elements
    print("\n=== Looking for download buttons ===")
    buttons = soup.find_all(['button', 'a'], class_=True)
    for button in buttons[:20]:
        text = button.get_text(strip=True)
        href = button.get('href', '')
        if text and ('download' in text.lower() or 'release' in text.lower() or '3.' in text):
            print(f"  Button/Link: {text[:80]}")
            if href:
                print(f"    href: {href}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

