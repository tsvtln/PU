import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
DOWNLOAD_PAGE = 'https://www.mythicsoft.com/agentransack/download/'
VERSION_HISTORY_PAGE = 'https://www.mythicsoft.com/agentransack/information/'
BASE_URL = 'https://www.mythicsoft.com'


def normalize_url(href: str) -> str:
    if href.startswith('http'):
        return href
    return BASE_URL + href


def extract_version_from_text(text: str):
    """
    Try to extract version like 2024.x.y or x.y.z from text.
    Mythicsoft often shows something like "Agent Ransack 2024" or full versions near MSI links.
    We'll look for common patterns.
    """
    # Common semantic version x.y.z
    m = re.search(r"\b(\d+\.\d+\.\d+)\b", text)
    if m:
        return m.group(1)
    # Year-based-like 2024.x or 2024.x.y
    m2 = re.search(r"\b(20\d{2}(?:\.\d+){0,2})\b", text)
    if m2:
        return m2.group(1)
    return None


def extract_version_from_url(url: str):
    # Try to extract x.y.z from filename or query
    m = re.search(r"(\d+\.\d+\.\d+)", url)
    if m:
        return m.group(1)
    # Try year-based like 20xx.y.z
    m2 = re.search(r"(20\d{2}(?:\.\d+){0,2})", url)
    if m2:
        return m2.group(1)
    return None


def resolve_final_url(href: str) -> str:
    try:
        # Follow redirects to get the actual file URL
        resp = requests.get(normalize_url(href), headers=HEADERS, verify=False, allow_redirects=True, timeout=20)
        # Prefer content-disposition filename if present
        cd = resp.headers.get('Content-Disposition')
        if cd and 'filename=' in cd:
            # We can't easily reconstruct full URL from filename; return request URL
            return resp.url
        return resp.url
    except Exception:
        return normalize_url(href)


def agentransack_download_url():
    """
    Fetch Agent Ransack latest version from the version history page, then extract 32-bit and 64-bit MSI ZIP download URLs
    from the download page. Prints results in the standard collector format.
    """
    # Step 1: Get version from version history page (format: Year (Build) ... → Year.Build)
    version = None
    try:
        vresp = requests.get(VERSION_HISTORY_PAGE, headers=HEADERS, verify=False)
        vresp.raise_for_status()
        vsoup = BeautifulSoup(vresp.text, 'html.parser')
        # Prefer table with id=TableChanges and first row class=versionheading
        table = vsoup.select_one('#TableChanges')
        if table:
            first_heading = table.select_one('tr.versionheading td')
            if first_heading:
                heading_text = first_heading.get_text(strip=True)
                m_hist = re.search(r"\b(20\d{2})\s*\((\d+)\)\b", heading_text)
                if m_hist:
                    year, build = m_hist.group(1), m_hist.group(2)
                    version = f"{year}.{build}"
        # Fallback to global text if table not found
        if not version:
            vtext = vsoup.get_text(' ', strip=True)
            m_hist = re.search(r"\b(20\d{2})\s*\((\d+)\)\b", vtext)
            if m_hist:
                year, build = m_hist.group(1), m_hist.group(2)
                version = f"{year}.{build}"
    except Exception as e:
        print(f"[WARNING] Failed to fetch version from history page: {e}")

    # Step 2: Parse download page for MSI ZIP links (x86 and x64)
    resp = requests.get(DOWNLOAD_PAGE, headers=HEADERS, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Agent Ransack download anchors look like:
    # href="//download.mythicsoft.com/flp/<build>/agentransack_x86_msi_<build>.zip"
    # href="//download.mythicsoft.com/flp/<build>/agentransack_x64_msi_<build>.zip"
    # We'll locate by href substrings to avoid markup dependencies.

    def ensure_https(url: str) -> str:
        if url.startswith('//'):
            return 'https:' + url
        return url

    url32 = None
    url64 = None

    for a in soup.find_all('a', href=True):
        href = a['href']
        href_l = href.lower()
        if 'agentransack_x86_msi' in href_l and href_l.endswith('.zip'):
            url32 = ensure_https(href)
        elif 'agentransack_x64_msi' in href_l and href_l.endswith('.zip'):
            url64 = ensure_https(href)

    # If not found via simple scan, try id-based selectors
    if not url32:
        el = soup.select_one('a[href*="agentransack_x86_msi"][href$=".zip"]')
        if el and el.get('href'):
            url32 = ensure_https(el['href'])
    if not url64:
        el = soup.select_one('a[href*="agentransack_x64_msi"][href$=".zip"]')
        if el and el.get('href'):
            url64 = ensure_https(el['href'])

    # Print results
    # Derive version Year.Build using build number from URLs and version history page
    if not version:
        build = None
        for candidate in (url32, url64):
            if candidate:
                m_build = re.search(r"/flp/(\d+)/", candidate)
                if m_build:
                    build = m_build.group(1)
                    break
        try:
            vresp = requests.get(VERSION_HISTORY_PAGE, headers=HEADERS, verify=False)
            vresp.raise_for_status()
            vsoup = BeautifulSoup(vresp.text, 'html.parser')
            table = vsoup.select_one('#TableChanges')
            if table:
                # If we have a build, find matching row; else take the first heading row
                rows = table.select('tr.versionheading')
                if rows:
                    matched = None
                    if build:
                        for row in rows:
                            td = row.select_one('td')
                            if not td:
                                continue
                            text = td.get_text(strip=True)
                            m = re.search(r"\b(20\d{2})\s*\((\d+)\)\b", text)
                            if m and m.group(2) == build:
                                matched = (m.group(1), m.group(2))
                                break
                    if not matched and rows:
                        # fallback to first row
                        td = rows[0].select_one('td')
                        if td:
                            text = td.get_text(strip=True)
                            m = re.search(r"\b(20\d{2})\s*\((\d+)\)\b", text)
                            if m:
                                matched = (m.group(1), m.group(2))
                    if matched:
                        version = f"{matched[0]}.{matched[1]}"
            # Extra fallback: use raw HTML text regex with known build, including HTML tag boundaries
            if not version and build:
                raw = vresp.text
                m_raw = re.search(r">\s*(\d{4})\s*\(\s*" + re.escape(build) + r"\s*\)\s*<", raw)
                if m_raw:
                    major = m_raw.group(1)
                    version = f"{major}.{build}"
            if not version and build and rows:
                # As a last resort, take the major from the first heading row and combine with known build
                td0 = rows[0].select_one('td')
                if td0:
                    text0 = td0.get_text(strip=True)
                    m0 = re.search(r"\b(\d{4})\b", text0)
                    if m0:
                        version = f"{m0.group(1)}.{build}"
        except Exception:
            pass

    print("==============================")
    print("Agent Ransack Latest Version and Download URLs:")
    if version:
        print(f"Latest Version: {version}")
    else:
        print("Latest Version: (not found)")
    if url32:
        print(f"32-bit URL: {url32}")
    else:
        print("Missing: 32-bit MSI URL")
    if url64:
        print(f"64-bit URL: {url64}")
    else:
        print("Missing: 64-bit MSI URL")


if __name__ == '__main__':
    agentransack_download_url()
