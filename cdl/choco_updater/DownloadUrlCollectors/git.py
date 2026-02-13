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
releases_url = 'https://api.github.com/repos/git-for-windows/git/releases/latest'
response = requests.get(releases_url, headers=headers, verify=False)
response.raise_for_status()

release_data = response.json()

# get assets from the release
assets = release_data.get('assets', [])

# find 32-bit and 64-bit exe files
# pattern: Git-.+-32-bit.exe and Git-.+-64-bit.exe
pattern_32 = re.compile(r'Git-.+-32-bit\.exe')
pattern_64 = re.compile(r'Git-.+-64-bit\.exe')

url32 = None
url64 = None

for asset in assets:
    name = asset.get('name', '')
    download_url = asset.get('browser_download_url', '')

    if pattern_32.search(name) and not url32:
        url32 = download_url
    elif pattern_64.search(name) and not url64:
        url64 = download_url

    if url32 and url64:
        break

if url64:
    # extract version from URL
    # example: https://github.com/git-for-windows/git/releases/download/v2.52.0.windows.1/Git-2.52.0-64-bit.exe
    # get filename and split by '-'
    # git-2.52.0-64-bit.exe -> ['Git', '2.52.0', '64', 'bit.exe']
    filename64 = url64.split('/')[-1]
    parts64 = filename64.split('-')

    # version is at index 1
    version = parts64[1] if len(parts64) > 1 else None

    if version:
        print(f"Latest Version: {version}")
        if url32:
            filename32 = url32.split('/')[-1]
            parts32 = filename32.split('-')
            version32 = parts32[1] if len(parts32) > 1 else None

            if version32 != version:
                print("Different versions for 32-Bit and 64-Bit detected.")
            print(f"32-bit URL: {url32}")
        else:
            print(f"32-bit URL: Not available (Git for Windows no longer provides 32-bit installers)")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not extract version")
else:
    print("Could not find download URLs")

