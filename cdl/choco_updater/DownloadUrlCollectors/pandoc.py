import requests
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers for GitHub API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

# get latest release from GitHub API
releases_url = 'https://api.github.com/repos/jgm/pandoc/releases/latest'
response = requests.get(releases_url, headers=headers, verify=False)
response.raise_for_status()

release_data = response.json()

# get version from tag_name
version = release_data.get('tag_name', '').strip()

# get assets from the release
assets = release_data.get('assets', [])

# find MSI file matching pattern pandoc-(.+?)-windows-.*.msi
pattern = re.compile(r'pandoc-(.+?)-windows-.*.msi')
url = None

for asset in assets:
    name = asset.get('name', '')
    download_url = asset.get('browser_download_url', '')

    if pattern.search(name):
        url = download_url
        break

if url and version:
    print(f"Latest Version: {version}")
    print(f"64-bit URL: {url}")
    print(f"Release Notes: https://github.com/jgm/pandoc/releases/tag/{version}")
else:
    print("Could not find pandoc download URLs")

