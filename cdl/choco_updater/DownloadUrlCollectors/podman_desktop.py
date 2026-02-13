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
    releases_url = 'https://api.github.com/repos/podman-desktop/podman-desktop/releases/latest'
    response = requests.get(releases_url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    release_data = response.json()

    # get version from tag_name (e.g., "v1.24.2")
    tag_name = release_data.get('tag_name', '')
    version = tag_name.lstrip('v').strip()

    # get assets from the release
    assets = release_data.get('assets', [])

    # find the Windows x64 setup installer
    # pattern: podman-desktop-<version>-setup-x64.exe or similar variants
    url64 = None

    for asset in assets:
        name = asset.get('name', '')
        download_url = asset.get('browser_download_url', '')

        # Look for Windows x64 setup installer
        if name.endswith('.exe') and 'setup' in name.lower() and 'x64' in name.lower():
            if 'podman-desktop' in name.lower():
                url64 = download_url
                break

    # Fallback: if exact pattern not found, look for any setup exe with x64
    if not url64:
        for asset in assets:
            name = asset.get('name', '')
            download_url = asset.get('browser_download_url', '')

            if name.endswith('.exe') and 'setup' in name.lower() and ('x64' in name.lower() or 'amd64' in name.lower()):
                url64 = download_url
                break

    if version and url64:
        print(f"Latest Version: {version}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not find Podman Desktop Windows installer")
        if not version:
            print("  Missing: version")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch Podman Desktop version: {e}")
except Exception as e:
    print(f"Error processing Podman Desktop version: {e}")

