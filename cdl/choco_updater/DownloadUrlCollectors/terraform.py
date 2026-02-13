import requests
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# HashiCorp checkpoint API
checkpoint_url = 'https://checkpoint-api.hashicorp.com/v1/check/terraform'

# fetch checkpoint data
response = requests.get(checkpoint_url, headers=headers, verify=False)
response.raise_for_status()

checkpoint_data = response.json()

# get version and download URL
version = checkpoint_data.get('current_version')
current_download_url = checkpoint_data.get('current_download_url')
changelog_url = checkpoint_data.get('current_changelog_url')

if not version or not current_download_url:
    print("Could not get version or download URL from checkpoint API")
else:
    # ensure current_download_url ends with a slash
    if not current_download_url.endswith('/'):
        current_download_url += '/'

    # fetch index.json from download URL
    index_url = f"{current_download_url}index.json"
    index_response = requests.get(index_url, headers=headers, verify=False)
    index_response.raise_for_status()

    terraform_builds = index_response.json()

    # get SHA sums, maybe i can re-use them instead of calculating in the autoupdater
    shasums_file = terraform_builds.get('shasums')
    shasums_url = f"{current_download_url}{shasums_file}"
    shasums_response = requests.get(shasums_url, headers=headers, verify=False)
    shasums_response.raise_for_status()

    # parse SHA sums into a dictionary
    shasums = {}
    for line in shasums_response.text.strip().split('\n'):
        if line:
            parts = line.split('  ')
            if len(parts) == 2:
                sha, filename = parts
                shasums[filename] = sha

    # find Windows builds
    builds = terraform_builds.get('builds', [])
    build32 = None
    build64 = None

    for build in builds:
        if build.get('os') == 'windows' and build.get('arch') == '386':
            build32 = build
        elif build.get('os') == 'windows' and build.get('arch') == 'amd64':
            build64 = build

    if build32 and build64:
        url32 = build32.get('url')
        url64 = build64.get('url')
        filename32 = build32.get('filename')
        filename64 = build64.get('filename')
        checksum32 = shasums.get(filename32)
        checksum64 = shasums.get(filename64)

        print(f"Latest Version: {version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")
        print(f"32-bit Checksum: {checksum32}")
        print(f"64-bit Checksum: {checksum64}")
        if changelog_url:
            print(f"Changelog: {changelog_url}")
    else:
        print("Could not find Windows builds")
        if not build32:
            print("  Missing: 32-bit build")
        if not build64:
            print("  Missing: 64-bit build")

