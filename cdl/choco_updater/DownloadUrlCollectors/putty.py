import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases = 'https://www.chiark.greenend.org.uk/~sgtatham/putty/download.html'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find MSI installers
# pattern: w32.*\.msi$ for 32-bit and w64.*\.msi$ for 64-bit
pattern_32_msi = re.compile(r'w32.*\.msi$')
pattern_64_msi = re.compile(r'w64.*\.msi$')

# find portable ZIP files
# pattern: w32.*putty.zip for 32-bit and w64.*putty.zip for 64-bit
pattern_32_zip = re.compile(r'w32.*putty\.zip')
pattern_64_zip = re.compile(r'w64.*putty\.zip')

url32_installer = None
url64_installer = None
url32_portable = None
url64_portable = None

for link in soup.find_all('a', href=True):
    href = link['href']

    if pattern_32_msi.search(href) and not url32_installer:
        url32_installer = href
    elif pattern_64_msi.search(href) and not url64_installer:
        url64_installer = href
    elif pattern_32_zip.search(href) and not url32_portable:
        url32_portable = href
    elif pattern_64_zip.search(href) and not url64_portable:
        url64_portable = href

# check if all URLs were found
if not url32_installer or not url64_installer or not url32_portable or not url64_portable:
    print("Error: Either 32bit or 64bit installer/portable was not found.")
else:
    # extract version from URL
    # split by '-' and take last 1, skip 1
    # example: https://the.earth.li/~sgtatham/putty/latest/w32/putty-0.67-installer.msi
    # split: [..., 'putty', '0.67', 'installer.msi']
    # last 1 skip 1: take from end, skip last, get next = '0.67'
    parts = url32_installer.split('-')
    version = parts[-2] if len(parts) >= 2 else None

    if version:
        print(f"Latest Version: {version}")
        print(f"32-bit Installer URL: {url32_installer}")
        print(f"64-bit Installer URL: {url64_installer}")
        print(f"32-bit Portable URL: {url32_portable}")
        print(f"64-bit Portable URL: {url64_portable}")
    else:
        print("Could not extract version from URL")

