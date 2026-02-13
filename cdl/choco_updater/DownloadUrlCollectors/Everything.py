import requests
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
changes_url = 'https://www.voidtools.com/Changes.txt'

try:
    # fetch the Changes.txt file
    response = requests.get(changes_url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    # parse the content to find the first version line
    # format: "Tuesday, 4 November 2025: Version 1.4.1.1030"
    lines = response.text.split('\n')
    version_pattern = re.compile(r': Version .+')

    version = None
    for line in lines:
        match = version_pattern.search(line)
        if match:
            # extract version from line like "Tuesday, 4 November 2025: Version 1.4.1.1030"
            parts = line.split()
            if len(parts) > 0:
                version = parts[-1].strip()
                break

    if not version:
        print("Could not find version in Changes.txt")
    else:
        # Version format is like "1.4.1.1030" with 'b' for beta (e.g., "1.5.0.1385b")
        # For Chocolatey, we need to remove 'b' and convert the last part
        # Example: 1.5.0.1385b -> 1.5.0.1385 -> choco version: 1.5.01385

        # Check if version has 'b' suffix (beta)
        is_beta = version.endswith('b')
        clean_version = version.rstrip('b')

        # Use the version as-is for Chocolatey (no conversion needed)
        choco_version = clean_version

        # Construct download URLs
        # Format: https://www.voidtools.com/Everything-1.4.1.1030.x86-Setup.exe
        #         https://www.voidtools.com/Everything-1.4.1.1030.x64-Setup.exe
        url32 = f"https://www.voidtools.com/Everything-{version}.x86-Setup.exe"
        url64 = f"https://www.voidtools.com/Everything-{version}.x64-Setup.exe"

        print(f"Latest Version: {choco_version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")

        if is_beta:
            print(f"Note: This is a beta version ({version})")

except requests.RequestException as e:
    print(f"Could not fetch Everything version: {e}")
except Exception as e:
    print(f"Error processing Everything version: {e}")

