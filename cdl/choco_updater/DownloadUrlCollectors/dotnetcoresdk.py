import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# Headers to mimic a browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
BASE_URL = 'https://dotnet.microsoft.com'
DOWNLOAD_ROOT = BASE_URL + '/en-us/download/dotnet'


def _abs(href: str) -> str:
    if href.startswith('http'):  # already absolute
        return href
    if href.startswith('/'):
        return BASE_URL + href
    return DOWNLOAD_ROOT.rstrip('/') + '/' + href


def _get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, verify=False)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def _find_latest_version_link(soup: BeautifulSoup) -> tuple[str, str]:
    """
    Parse the supported-versions table and return (display_version, absolute_link)
    The top entry is the latest version.
    """
    # First try the direct approach: look for all version links
    version_links = []
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        # Match /download/dotnet/{major.minor} or /en-us/download/dotnet/{major.minor}
        if re.search(r'/download/dotnet/\d+\.\d+$', href):
            text = a.get_text(strip=True)
            # Filter out empty or very short text
            if len(text) > 3:
                version_links.append((text, _abs(href)))

    if version_links:
        # Return the first one found (should be the latest)
        return version_links[0]

    # Fallback: try to find table
    table = soup.find('table', attrs={'aria-labelledby': 'dotnetcore-version'})
    if not table:
        raise RuntimeError('Supported versions table not found and no version links found')

    # Look through all rows in table (with or without tbody)
    all_rows = table.find_all('tr', recursive=True)
    for tr in all_rows:
        link = tr.find('a', href=True)
        if link and re.search(r'/download/dotnet/\d+\.\d+', link.get('href', '')):
            display_text = link.get_text(strip=True)
            href = link['href']
            return (display_text, _abs(href))

    raise RuntimeError('Latest version link not found in table or page')


def _extract_version_number(display_text: str) -> str:
    # Display text like ".NET 10.0" -> version "10.0"
    m = re.search(r'(\d+\.\d+)', display_text)
    if not m:
        # sometimes page may include preview, fallback later
        raise RuntimeError(f'Could not parse version from text: {display_text}')
    return m.group(1)


def _find_windows_x64_installer_thankyou_link(soup: BeautifulSoup, sdk_version_full: str) -> str:
    """
    On version page, find the Windows x64 SDK installer thank-you link
    e.g. /en-us/download/dotnet/thank-you/sdk-10.0.101-windows-x64-installer
    We match anchor with data-bi-dlid containing 'sdk-' and 'windows-x64-installer'.
    If multiple patch versions exist, take the first occurrence.
    """
    # prefer exact match with windows-x64-installer
    for a in soup.select('a[href][data-bi-dlid]'):
        dlid = a.get('data-bi-dlid', '')
        href = a['href']
        if 'windows-x64-installer' in dlid and dlid.startswith('sdk-'):
            return _abs(href)
    # fallback: any thank-you link that contains windows-x64-installer on href
    for a in soup.select('a[href]'):
        href = a['href']
        if 'windows-x64-installer' in href and 'thank-you' in href and 'sdk-' in href:
            return _abs(href)
    raise RuntimeError('Windows x64 SDK installer link not found on version page')


def _extract_direct_download_link(soup: BeautifulSoup) -> str:
    """
    On the thank-you page, fetch the anchor with id="directLink" or first anchor whose href
    points to builds.dotnet.microsoft.com and ends with win-x64.exe
    """
    a = soup.find('a', id='directLink', href=True)
    if a and a['href']:
        return a['href']
    # fallback: look for builds.dotnet.microsoft.com direct link
    for link in soup.select('a[href]'):
        href = link['href']
        if 'builds.dotnet.microsoft.com' in href and href.endswith('win-x64.exe'):
            return href
    raise RuntimeError('Direct download link not found on thank-you page')


def main():
    try:
        root_soup = _get_soup(DOWNLOAD_ROOT)
        display_version, version_page_url = _find_latest_version_link(root_soup)
        major_minor = _extract_version_number(display_version)

        version_page_soup = _get_soup(version_page_url)
        thankyou_link = _find_windows_x64_installer_thankyou_link(version_page_soup, major_minor)

        thankyou_soup = _get_soup(thankyou_link)
        direct_url = _extract_direct_download_link(thankyou_soup)

        # Try to infer full SDK version from the direct URL, e.g., Sdk/10.0.101/
        m = re.search(r'/Sdk/(\d+\.\d+\.\d+)/', direct_url)
        version_full = m.group(1) if m else None
        # If not present, fallback to major.minor
        version_out = version_full or major_minor

        print(f"Latest Version: {version_out}")
        print(f"64-bit URL: {direct_url}")
    except Exception as e:
        print(f"Could not get version or download URL for dotnetcoresdk: {e}")


if __name__ == '__main__':
    main()

