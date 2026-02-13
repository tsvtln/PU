import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
release = 'https://winscp.net/eng/downloads.php'

# fetch the page
response = requests.get(release, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find links matching pattern WinSCP.+Setup\.exe (not containing 'beta' or 'rc')
# Note: Removed $ anchor because href is like /download/WinSCP-6.5.5-Setup.exe/download
pattern = re.compile(r'WinSCP.+Setup\.exe')
url = None

for link in soup.find_all('a', href=True):
    href = link['href']

    if pattern.search(href):
        # exclude beta and rc versions
        if 'beta' not in href.lower() and 'rc' not in href.lower():
            url = 'https://winscp.net/eng' + href
            break

if url:
    # extract filename from URL
    # URL structure: /download/WinSCP-6.5.5-Setup.exe/download
    # split by '/' and get the segment containing Setup.exe
    parts_url = url.split('/')
    filename = next((part for part in parts_url if 'Setup.exe' in part), None)

    if filename:
        # extract version from filename
        # split by '-': ['WinSCP', '6.5.5', 'Setup.exe']
        # version is at index -2 (second from end)
        parts = filename.split('-')
        version = parts[-2] if len(parts) >= 2 else None

        if version:
            # construct SourceForge download URL
            sourceforge_url = f"https://sourceforge.net/projects/winscp/files/WinSCP/{version}/{filename}/download"

            print(f"Latest Version: {version}")
            print(f"Download URL: {sourceforge_url}")
            print(f"Filename: {filename}")
        else:
            print("Could not extract version from filename")
    else:
        print("Could not extract filename from URL")
else:
    print("Could not find WinSCP download URL")

