import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.jetbrains.com/pycharm/download/other.html'

print("=== Testing PyCharm download page ===")

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for "Version:" in text
    print("\n=== Looking for Version text ===")
    page_text = soup.get_text()
    lines = page_text.split('\n')
    for i, line in enumerate(lines[:100]):
        if 'version' in line.lower() or '2025' in line or '2024' in line:
            print(f"Line {i}: {line.strip()[:100]}")

    # Look for download links
    print("\n=== Looking for download links ===")
    links = soup.find_all('a', href=True)
    print(f"Total links: {len(links)}")

    exe_links = []
    for link in links:
        href = link.get('href', '')
        if '.exe' in href and 'pycharm' in href.lower():
            exe_links.append(href)
            print(f"  Found: {href}")

    if not exe_links:
        print("No .exe links with pycharm found")
        print("\n=== All download.jetbrains.com links ===")
        for link in links:
            href = link.get('href', '')
            if 'download.jetbrains.com' in href:
                print(f"  {href}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

