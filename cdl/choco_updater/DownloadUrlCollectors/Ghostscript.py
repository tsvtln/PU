import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases_page = 'https://www.ghostscript.com/releases/index.html'
download_page = 'https://www.ghostscript.com/releases/gsdnld.html'

try:
    # Step 1: Get the latest version from the releases index page
    response = requests.get(releases_page, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    full_text = soup.get_text()

    # Look for pattern: "The latest release is Ghostscript X.XX.X (YYYY-MM-DD)"
    version_pattern = re.compile(r'The latest release is Ghostscript\s+(\d+\.\d+\.\d+)')
    match = version_pattern.search(full_text)

    if not match:
        print("Could not find Ghostscript version on releases page")
    else:
        version = match.group(1)

        # Convert version to tag format for download URLs
        # Example: 10.06.0 -> gs10060
        version_parts = version.split('.')
        if len(version_parts) == 3:
            # Pad major and minor to 2 digits, but keep patch as-is (no padding)
            major = version_parts[0].zfill(2)
            minor = version_parts[1].zfill(2)
            patch = version_parts[2]  # No padding for patch version
            tag = f"gs{major}{minor}{patch}"

            # Construct download URLs
            # Format: https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/gs10060w64.exe
            base_url = f"https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/{tag}"
            url64 = f"{base_url}/{tag}w64.exe"
            url32 = f"{base_url}/{tag}w32.exe"

            print(f"Latest Version: {version}")
            print(f"32-bit URL: {url32}")
            print(f"64-bit URL: {url64}")
        else:
            print(f"Unexpected version format: {version}")

except requests.RequestException as e:
    print(f"Could not fetch Ghostscript version: {e}")
except Exception as e:
    print(f"Error processing Ghostscript version: {e}")

