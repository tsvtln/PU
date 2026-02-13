import requests
import warnings
warnings.filterwarnings('ignore')

# set up headers for GitHub API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

# get latest release from GitHub API
releases_url = 'https://api.github.com/repos/notepad-plus-plus/notepad-plus-plus/releases/latest'
response = requests.get(releases_url, headers=headers, verify=False)
response.raise_for_status()

release_data = response.json()

# get version (remove 'v' prefix from tag_name)
tag_name = release_data.get('tag_name', '')
version = tag_name.lstrip('v').strip()

# get assets from the release
assets = release_data.get('assets', [])

# find URLs based on asset names
# URL32_i: ends with "Installer.exe" (32-bit installer)
# URL64_i: ends with "x64.exe" (64-bit installer)
url32 = None
url64 = None

for asset in assets:
    name = asset.get('name', '')
    download_url = asset.get('browser_download_url', '')

    if name.endswith('Installer.exe') and 'x64' not in name:
        url32 = download_url
    elif name.endswith('x64.exe'):
        url64 = download_url

if version:
    print(f"Latest Version: {version}")
    print(f"32-bit URL: {url32}")
    print(f"64-bit URL: {url64}")
else:
    print("Could not find version information")

