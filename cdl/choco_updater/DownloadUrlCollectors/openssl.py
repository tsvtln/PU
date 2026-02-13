import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
domain = 'https://slproweb.com'
releases = f'{domain}/products/Win32OpenSSL.html'
LOCAL_HASHES_JSON = f'{domain}/download/win32_openssl_hashes.json'

RE_LIGHT_32 = re.compile(r'(Win32OpenSSL_Light-\d+_\d+_\d+[a-z]?\.exe)', re.IGNORECASE)
RE_LIGHT_64 = re.compile(r'(Win64OpenSSL_Light-\d+_\d+_\d+[a-z]?\.exe)', re.IGNORECASE)
RE_PRODUCT_PAGE = re.compile(r'/products/Win32OpenSSL_.*?\.html', re.IGNORECASE)


def _get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=headers, verify=False, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def _abs(href: str) -> str:
    if href.startswith('http'):
        return href
    return domain + href


def _parse_version_from_filename(filename: str) -> str:
    # filename like Win64OpenSSL_Light-3_4_1a.exe -> version 3.4.1.0 (a->0)
    m = re.search(r'-(\d+_\d+_\d+[a-z]?)\.exe', filename, re.IGNORECASE)
    if not m:
        return None
    ver = m.group(1).replace('_', '.')
    if ver[-1].isalpha():
        rev = ord(ver[-1].lower()) - ord('a')
        ver = ver[:-1] + f'.{rev}'
    return ver


def _extract_filenames_from_text(text: str):
    f32 = None
    f64 = None
    m32 = RE_LIGHT_32.search(text)
    m64 = RE_LIGHT_64.search(text)
    if m32:
        f32 = m32.group(1)
    if m64:
        f64 = m64.group(1)
    return f32, f64


def main():
    try:
        root = _get_soup(releases)

        url32 = None
        url64 = None

        # Pass 1: look for hrefs containing filenames
        for a in root.find_all('a', href=True):
            href = a['href']
            if RE_LIGHT_32.search(href) and not url32:
                url32 = _abs(href)
            elif RE_LIGHT_64.search(href) and not url64:
                url64 = _abs(href)

        # Pass 2: fallback to scan visible text for filenames and construct URLs
        if not (url32 and url64):
            f32, f64 = _extract_filenames_from_text(root.get_text("\n"))
            if f32 and not url32:
                url32 = f"{domain}/download/{f32}"
            if f64 and not url64:
                url64 = f"{domain}/download/{f64}"

        # Pass 3: crawl product pages for hrefs and text
        if not (url32 and url64):
            product_pages = set()
            for a in root.find_all('a', href=True):
                href = a['href']
                if RE_PRODUCT_PAGE.search(href):
                    product_pages.add(_abs(href))

            for page in sorted(product_pages):
                try:
                    soup = _get_soup(page)
                    # href scan
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if not url32 and RE_LIGHT_32.search(href):
                            url32 = _abs(href)
                        elif not url64 and RE_LIGHT_64.search(href):
                            url64 = _abs(href)
                    # text scan
                    if not (url32 and url64):
                        f32, f64 = _extract_filenames_from_text(soup.get_text("\n"))
                        if f32 and not url32:
                            url32 = f"{domain}/download/{f32}"
                        if f64 and not url64:
                            url64 = f"{domain}/download/{f64}"
                    if url32 and url64:
                        break
                except Exception:
                    continue

        # Pass 4: fetch local JSON hashes file (win32_openssl_hashes.json)
        if not (url32 and url64):
            try:
                rjson = requests.get(LOCAL_HASHES_JSON, headers=headers, verify=False, timeout=30)
                if rjson.status_code == 200:
                    data = rjson.json()
                    # JSON structure: { "files": { "filename": { "arch": "INTEL", "bits": 32/64, "light": true/false, "url": "...", ... } } }
                    files = data.get('files', {})

                    # Check version prefixes in order of newest first (matching the page's JavaScript logic)
                    verprefixes = ['3.6.', '3.5.', '3.4.', '3.3.', '3.2.', '3.0.', '1.1.1.']

                    for verprefix in verprefixes:
                        if url32 and url64:
                            break
                        for filename, fileinfo in files.items():
                            basever = fileinfo.get('basever', '')
                            if (basever.startswith(verprefix) and
                                fileinfo.get('installer') == 'exe' and
                                fileinfo.get('light') == True and
                                fileinfo.get('arch') == 'INTEL'):
                                bits = fileinfo.get('bits')
                                file_url = fileinfo.get('url')
                                if bits == 32 and not url32 and file_url:
                                    url32 = file_url if file_url.startswith('http') else f"{domain}{file_url}"
                                elif bits == 64 and not url64 and file_url:
                                    url64 = file_url if file_url.startswith('http') else f"{domain}{file_url}"
                                if url32 and url64:
                                    break
            except Exception:
                pass

        if not url32 or not url64:
            print("Could not find OpenSSL Light download URLs")
            if not url32:
                print("  Missing: 32-bit URL")
            if not url64:
                print("  Missing: 64-bit URL")
            return

        v32 = _parse_version_from_filename(url32)
        v64 = _parse_version_from_filename(url64)
        version = v32 or v64
        if v32 and v64 and v32 != v64:
            print(f"Warning: 32-bit version ({v32}) does not match 64-bit version ({v64})")
            try:
                from packaging.version import Version
                version = str(max(Version(v32), Version(v64)))
            except Exception:
                version = v32
        if not version:
            print("Could not extract version from filenames")
            version = 'unknown'

        print(f"Latest Version: {version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")

    except Exception as e:
        print(f"Could not fetch OpenSSL version: {e}")


if __name__ == '__main__':
    main()
