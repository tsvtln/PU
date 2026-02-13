import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases = 'https://curl.se/windows/'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find all links with .zip
zip_pattern = re.compile(r'\.zip')
urls = []

for link in soup.find_all('a', href=True):
    href = link['href']
    if zip_pattern.search(href):
        # Convert relative URLs to absolute
        full_url = urljoin(releases, href)
        urls.append(full_url)

if urls:
    # extract version from first URL
    # example: curl-8.11.0_1-win64-mingw.zip -> split by '(_\d+)?-' -> get index 1
    first_url = urls[0]
    filename = first_url.split('/')[-1]

    # split by '-' and extract version (handling optional _digit suffix)
    # curl-8.11.0_1-win64-mingw.zip -> ['curl', '8.11.0_1', 'win64', 'mingw.zip']
    parts = filename.split('-')
    version_part = parts[1] if len(parts) > 1 else ''
    # remove optional _digit suffix (e.g., 8.11.0_1 -> 8.11.0)
    version = re.sub(r'_\d+$', '', version_part)

    # find win32 URL (contains 'win32')
    url32 = next((u for u in urls if 'win32' in u), None)

    # find win64 URL (does not contain 'win32' but contains version)
    url64 = next((u for u in urls if 'win32' not in u and version in u), None)

    # find release notes URL
    release_notes = None
    for link in soup.find_all('a', href=True):
        if re.search(r'changes\.html', link['href']):
            release_notes = urljoin(releases, link['href'])
            break

    print(f"Latest Version: {version}")
    print(f"32-bit URL: {url32}" if url32 else "curl package has only 64-bit version.")
    print(f"64-bit URL: {url64}")
    if release_notes:
        print(f"Release Notes: {release_notes}")
else:
    print("Could not find download URLs")

