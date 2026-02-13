import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases = 'https://www.python.org/downloads/windows/'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find release links matching pattern: href contains 'release' and text matches "^Python 3\.[0-9]\.[0-9] - .+$"
version_pattern = re.compile(r'^Python 3\.[0-9]+\.[0-9]+ - .+$')
release_links = []

for link in soup.find_all('a', href=True):
    href = link['href']
    text = link.get_text(strip=True)

    if 'release' in href and version_pattern.match(text):
        release_links.append({
            'href': href,
            'text': text
        })

if release_links:
    # take the first (latest) release
    latest_release = release_links[0]

    # extract version from text like "Python 3.12.0 - Sept. 23, 2024"
    # split by space and take index 1
    version_text = latest_release['text'].split()[1]

    # go to the release page
    release_href = latest_release['href']
    if not release_href.startswith('http'):
        release_href = 'https://www.python.org' + release_href

    release_page = requests.get(release_href, headers=headers, verify=False)
    release_page.raise_for_status()

    release_soup = BeautifulSoup(release_page.text, 'html.parser')

    # find installers
    # 32-bit: python-.+.(exe|msi)$ and NOT amd64
    # 64-bit: python-.+amd64\.(exe|msi)$
    pattern_32 = re.compile(r'python-.+\.(exe|msi)$')
    pattern_64 = re.compile(r'python-.+amd64\.(exe|msi)$')

    url32 = None
    url64 = None

    for link in release_soup.find_all('a', href=True):
        href = link['href']

        if pattern_64.search(href) and not url64:
            url64 = href if href.startswith('http') else 'https://www.python.org' + href
        elif pattern_32.search(href) and 'amd64' not in href and not url32:
            url32 = href if href.startswith('http') else 'https://www.python.org' + href

    if url32 and url64:
        print(f"Latest Version: {version_text}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")
    else:
        print(f"Found version {version_text} but missing installer URLs")
        if not url32:
            print("  Missing: 32-bit URL")
        if not url64:
            print("  Missing: 64-bit URL")
else:
    print("Could not find Python releases")

