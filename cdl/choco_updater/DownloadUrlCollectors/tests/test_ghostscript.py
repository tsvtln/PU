import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Test the releases index page
print("=== Testing releases index page ===")
url1 = 'https://www.ghostscript.com/releases/index.html'
try:
    response1 = requests.get(url1, headers=headers, verify=False, timeout=30)
    print(f"Status: {response1.status_code}")

    soup1 = BeautifulSoup(response1.text, 'html.parser')
    text = soup1.get_text()

    # Look for version pattern
    pattern = re.compile(r'The latest release is Ghostscript\s+(\d+\.\d+\.\d+)')
    match = pattern.search(text)
    if match:
        version = match.group(1)
        print(f"Found version: {version}")
    else:
        print("Version not found")
        # Show some text to debug
        lines = text.split('\n')
        for i, line in enumerate(lines[:30]):
            if 'latest' in line.lower() or 'ghostscript' in line.lower():
                print(f"Line {i}: {line.strip()}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing download page ===")
url2 = 'https://www.ghostscript.com/releases/gsdnld.html'
try:
    response2 = requests.get(url2, headers=headers, verify=False, timeout=30)
    print(f"Status: {response2.status_code}")

    soup2 = BeautifulSoup(response2.text, 'html.parser')

    # Look for download links
    download_pattern = re.compile(r'ghostpdl-downloads/releases/download/gs\d+/gs\d+w(64|32)\.exe')

    links = soup2.find_all('a', href=True)
    print(f"Total links: {len(links)}")

    for link in links:
        href = link.get('href', '')
        if download_pattern.search(href):
            print(f"Found download link: {href}")

except Exception as e:
    print(f"Error: {e}")

