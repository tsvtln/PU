import requests
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers for GitHub API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

try:
    # get latest release from GitHub API
    releases_url = 'https://api.github.com/repos/containers/podman/releases/latest'
    response = requests.get(releases_url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    release_data = response.json()

    # get version from tag_name (e.g., "v5.3.1")
    tag_name = release_data.get('tag_name', '')
    version = tag_name.lstrip('v').strip()

    # get assets from the release
    assets = release_data.get('assets', [])

    # find the Windows amd64 installer
    # pattern: podman-installer-windows-amd64.exe or similar variants
    # also check for podman-<version>-setup.exe or other naming patterns
    url64 = None

    for asset in assets:
        name = asset.get('name', '')
        download_url = asset.get('browser_download_url', '')

        # Look for Windows amd64 installer
        if name.endswith('.exe') and 'windows' in name.lower() and 'amd64' in name.lower():
            if 'installer' in name.lower() or 'setup' in name.lower():
                url64 = download_url
                break

    # Fallback: if exact pattern not found, look for any Windows exe
    if not url64:
        for asset in assets:
            name = asset.get('name', '')
            download_url = asset.get('browser_download_url', '')

            if name.endswith('.exe') and ('windows' in name.lower() or 'win' in name.lower()):
                url64 = download_url
                break

    if version and url64:
        print(f"Latest Version: {version}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not find Podman Windows installer")
        if not version:
            print("  Missing: version")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch Podman version: {e}")
except Exception as e:
    print(f"Error processing Podman version: {e}")

