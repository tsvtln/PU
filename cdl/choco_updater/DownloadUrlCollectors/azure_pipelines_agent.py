import requests
import os
import warnings
warnings.filterwarnings('ignore')

# set up headers for GitHub API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/vnd.github.v3+json'
}

# add GitHub token if available (for higher rate limits)
github_token = os.environ.get('github_api_key') or os.environ.get('GITHUB_TOKEN')
if github_token:
    headers['Authorization'] = f'token {github_token}'

# get latest release from GitHub API
releases_url = 'https://api.github.com/repos/Microsoft/azure-pipelines-agent/releases/latest'
response = requests.get(releases_url, headers=headers, verify=False)
response.raise_for_status()

release_data = response.json()

# check if release name starts with 'v'
if not release_data.get('name', '').startswith('v'):
    print("Could not find valid version information")
else:
    # extract version (remove 'v' prefix)
    version = release_data['name'][1:]

    # get assets URL and fetch asset details
    assets_url = release_data['assets_url']
    assets_response = requests.get(assets_url, headers=headers, verify=False)
    assets_response.raise_for_status()
    assets = assets_response.json()

    # the first asset should be a JSON file with download URLs
    if assets:
        # download the JSON asset that contains platform-specific download URLs
        asset_json_url = assets[0]['browser_download_url']
        asset_json_response = requests.get(asset_json_url, headers=headers, verify=False)
        asset_json_response.raise_for_status()
        assets_json = asset_json_response.json()

        # find win-x86 and win-x64 platform URLs
        url32 = None
        url64 = None

        for asset in assets_json:
            if asset.get('platform') == 'win-x86':
                url32 = asset.get('downloadUrl')
            elif asset.get('platform') == 'win-x64':
                url64 = asset.get('downloadUrl')

        print(f"Latest Version: {version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")
    else:
        print("No assets found in release")

