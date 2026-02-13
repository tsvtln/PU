import requests
import re
import warnings
warnings.filterwarnings('ignore')

# Headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

release_notes_url = 'https://docs.docker.com/desktop/release-notes/'

try:
    resp = requests.get(release_notes_url, headers=headers, verify=False)
    resp.raise_for_status()
    html = resp.text
except Exception as e:
    print(f"Error fetching Docker Desktop release notes: {e}")
    html = ''

version = None
url64 = None

if html:
    # Find the first version anchor in the table of contents or headings like id="4540" and text "4.54.0"
    # Prefer extracting the textual version (x.y.z)
    # Strategy:
    # 1) Find the first occurrence of a version heading like <h2 id="4540">4.54.0</h2> (could be h2/h3)
    # 2) From that position, search for an href that points to the Windows installer under desktop.docker.com

    # Locate the first version occurrence in the page (e.g., 4.54.0)
    ver_match = re.search(r'>\s*(\d+\.\d+\.\d+)\s*<', html)
    if ver_match:
        version = ver_match.group(1)
        # Narrow slice from the first version occurrence onward
        start_idx = ver_match.start()
        slice_html = html[start_idx:]

        # Look for a Windows download link pointing to desktop.docker.com win main amd64
        # e.g., https://desktop.docker.com/win/main/amd64/212467/Docker%20Desktop%20Installer.exe
        url_match = re.search(
            r'https://desktop\.docker\.com/win/main/amd64/\d+/Docker%20Desktop%20Installer\.exe',
            slice_html
        )
        if not url_match:
            # Sometimes the link might have different casing or spaces unencoded; attempt a broader match first
            alt_match = re.search(
                r'https://desktop\.docker\.com/win/main/amd64/\d+/[^"\s]*Installer\.exe',
                slice_html
            )
            if alt_match:
                url64 = alt_match.group(0)
        else:
            url64 = url_match.group(0)

        # If still not found, the release notes might link to a checksum page; try extracting Windows link anchors
        if not url64:
            # Search for anchor text Windows near the version section and grab the href
            # e.g., <a href="https://desktop.docker.com/win/main/amd64/212467/Docker%20Desktop%20Installer.exe">Windows</a>
            win_anchor = re.search(
                r'<a[^>]+href="([^"]+)"[^>]*>\s*Windows\s*</a>',
                slice_html,
                flags=re.IGNORECASE
            )
            if win_anchor:
                candidate = win_anchor.group(1)
                if 'desktop.docker.com' in candidate and candidate.lower().endswith('.exe'):
                    url64 = candidate

    # As a fallback, search globally in the page for any matching installer URL
    if not url64:
        global_match = re.search(
            r'https://desktop\.docker\.com/win/main/amd64/\d+/Docker%20Desktop%20Installer\.exe',
            html
        )
        if global_match:
            url64 = global_match.group(0)

if version and url64:
    print(f"Latest Version: {version}")
    print(f"64-bit URL: {url64}")
else:
    print("Could not extract latest version or Windows download URL from Docker Desktop release notes")

