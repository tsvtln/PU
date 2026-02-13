import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
DOWNLOADS_PAGE = 'https://helgeklein.com/download/'


def delprof2_download_url():
    """
    Fetch Helge Klein downloads page, locate the DelProf2 section, extract latest version text
    (e.g., "DelProf2 1.6.0") and the ZIP download link from the anchor's data-url.

    Output:
      Latest Version: 1.6.0
      Zip URL: https://helgeklein.com/downloads/DelProf2/current/Delprof2%201.6.0.zip
    """
    print('DEBUG: Starting delprof2_download_url')
    try:
        resp = requests.get(DOWNLOADS_PAGE, headers=HEADERS, verify=False, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        version = None
        zip_url = None

        # Strategy:
        # - Find the h2 with name="delprof2" to locate the section
        # - Then find the following 'Download Delprof2' paragraph and get the anchor with class tbd_link or data-url
        # - Extract version from anchor text and URL from data-url attribute
        delprof_h2 = soup.find('h2')
        # Find the <h2> with id='delprof2' (case-insensitive)
        delprof_h2 = None
        for h2 in soup.find_all('h2'):
            if h2.get('id', '').lower() == 'delprof2':
                delprof_h2 = h2
                break
        link = None
        if delprof_h2:
            sibling = delprof_h2.next_sibling
            while sibling:
                if getattr(sibling, 'find_all', None):
                    for a in sibling.find_all('a', href=True):
                        href = a.get('href')
                        if href and 'DelProf2/current' in href:
                            link = a
                            break
                if link:
                    break
                sibling = sibling.next_sibling
        # Fallback: search entire soup for href
        if not link:
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and 'DelProf2/current' in href:
                    link = a
                    break
        if link:
            print(f"DEBUG: Found anchor: {link}")
            text = link.get_text(strip=True)
            m = re.search(r'DelProf2\s+([\d.]+)', text, re.IGNORECASE)
            if m:
                version = m.group(1)
            zip_url = link.get('href')
            if zip_url:
                if not zip_url.lower().startswith('http'):
                    zip_url = 'https://helgeklein.com' + zip_url
                zip_url = zip_url.replace(' ', '%20')
        else:
            print("DEBUG: No anchor found with href containing 'DelProf2/current'")

        print('==============================')
        print('DelProf2 Latest Version and Download URL:')
        if version:
            print(f'Latest Version: {version}')
        else:
            print('Latest Version: (not found)')
        if zip_url:
            print(f'Zip URL: {zip_url}')
        else:
            print('Missing: Zip URL')
    except Exception as e:
        print('==============================')
        print(f'DelProf2 collector failed: {e}')


if __name__ == '__main__':
    delprof2_download_url()
