import requests
import warnings
warnings.filterwarnings('ignore')

# set up headers for GitHub API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

try:
    # get latest release from GitHub API
    releases_url = 'https://api.github.com/repos/microsoft/AzureStorageExplorer/releases/latest'
    response = requests.get(releases_url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    release_data = response.json()

    # get version from tag_name (e.g., "v1.35.0")
    version = release_data.get('tag_name', '').strip()
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]

    # get assets from the release
    assets = release_data.get('assets', [])

    # find Windows x64 installer (not ARM64)
    # Pattern: StorageExplorer-windows-x64.exe
    # Azure Storage Explorer typically has files like:
    # - StorageExplorer-windows-x64.exe (x64 version - we want this)
    # - StorageExplorer-windows-arm64.exe (ARM version - skip this)
    url = None

    for asset in assets:
        name = asset.get('name', '')
        download_url = asset.get('browser_download_url', '')

        # Look for Windows x64 exe installer, skip ARM64
        if name.endswith('.exe') and 'windows' in name.lower() and 'x64' in name.lower():
            url = download_url
            break
        elif name.endswith('.exe') and 'x64' in name.lower() and 'StorageExplorer' in name:
            url = download_url
            break

    if url and version:
        print(f"Latest Version: {version}")
        print(f"64-bit URL: {url}")
        print(f"Release Notes: https://github.com/microsoft/AzureStorageExplorer/releases/tag/v{version}")
    else:
        print("Could not find Azure Storage Explorer download URL")
        if not version:
            print("  Missing: version")
        if not url:
            print("  Missing: download URL")

except requests.RequestException as e:
    print(f"Could not fetch Azure Storage Explorer version: {e}")
except Exception as e:
    print(f"Error processing Azure Storage Explorer version: {e}")

