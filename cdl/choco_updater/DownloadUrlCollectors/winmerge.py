import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases = 'http://winmerge.org/downloads/'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find installers
# Pattern: WinMerge-.*-Setup.exe for 32-bit (case-insensitive)
# Pattern: WinMerge-.*-x64-Setup.exe for 64-bit (case-insensitive)
# Exclude ARM64 versions
pattern_32 = re.compile(r'winmerge-.*-Setup\.exe', re.IGNORECASE)
pattern_64 = re.compile(r'winmerge-.*-x64-Setup\.exe', re.IGNORECASE)

url32 = None
url64 = None

for link in soup.find_all('a', href=True):
    href = link['href']

    # Skip ARM64 versions
    if 'arm64' in href.lower():
        continue

    if pattern_64.search(href) and not url64:
        url64 = href
    elif pattern_32.search(href) and 'x64' not in href and not url32:
        url32 = href

if url32 and url64:
    # extract version from URL
    # example: WinMerge-2.16.52.2-x64-Setup.exe
    # Use regex to extract version pattern (digits separated by dots)
    version_match = re.search(r'WinMerge-(\d+(?:\.\d+)+)', url64, re.IGNORECASE)
    version = version_match.group(1) if version_match else None

    if version:
        print(f"Latest Version: {version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not extract version from URL")
else:
    print("Could not find WinMerge download URLs")
    if not url32:
        print("  Missing: 32-bit URL")
    if not url64:
        print("  Missing: 64-bit URL")

