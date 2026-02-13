import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://slproweb.com/products/Win32OpenSSL.html'

print("=== Testing OpenSSL download page ===")

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for Win32 and Win64 Light installer links
    print("\n=== Looking for Win32 OpenSSL Light installers ===")
    pattern_32 = re.compile(r'Win32.*Light.*\.exe', re.IGNORECASE)
    pattern_64 = re.compile(r'Win64.*Light.*\.exe', re.IGNORECASE)

    links = soup.find_all('a', href=True)
    print(f"Total links: {len(links)}")

    print("\n=== All href values ===")
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href:
            print(f"  href: {href[:80]} | text: {text[:40]}")

    print("\n=== Checking link text for exe files ===")
    for link in links:
        text = link.get_text(strip=True)
        if '.exe' in text.lower():
            print(f"  Found exe in text: {text}")
            print(f"    href: {link.get('href', '')}")

    print("\n=== Matching Light installers in href ===")
    found_32 = []
    found_64 = []

    for link in links:
        href = link.get('href', '')
        if pattern_32.search(href):
            found_32.append(href)
            print(f"  32-bit: {href}")
        elif pattern_64.search(href):
            found_64.append(href)
            print(f"  64-bit: {href}")

    print("\n=== Matching Light installers in text ===")
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href', '')
        if pattern_32.search(text):
            print(f"  32-bit text: {text}")
            print(f"    href: {href}")
            found_32.append((href, text))
        elif pattern_64.search(text):
            print(f"  64-bit text: {text}")
            print(f"    href: {href}")
            found_64.append((href, text))

    if found_32:
        print(f"\nFirst 32-bit URL: {found_32[0]}")
        # Try to extract version
        test_url = found_32[0]
        print(f"Extracting version from: {test_url}")

        # Split by '-' or '.exe'
        parts = re.split(r'[-.]', test_url)
        print(f"Parts: {parts}")

        # The version is typically before .exe, skip 1 from end
        if len(parts) > 2:
            version_candidate = parts[-2]
            print(f"Version candidate: {version_candidate}")

            # Replace underscores with dots
            version = version_candidate.replace('_', '.')
            print(f"Version after replacing _: {version}")

            # Check if last character is a letter (revision)
            if version and version[-1].isalpha():
                rev = ord(version[-1]) - ord('a')
                version_base = version[:-1]
                version_with_rev = f"{version_base}.{rev}"
                print(f"Version with revision: {version_with_rev}")

    if found_64:
        print(f"\nFirst 64-bit URL: {found_64[0]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

