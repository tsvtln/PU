import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
BGINFO_PAGE = 'https://learn.microsoft.com/en-us/sysinternals/downloads/bginfo'
STATIC_ZIP_URL = 'https://download.sysinternals.com/files/BGInfo.zip'


def bginfo_download_url():
    """
    Fetch BgInfo page, extract latest version from <h1 id="bginfo-vNNN">BgInfo vX.YZ</h1>,
    and print the static zip download URL.

    Output format:
      Latest Version: X.YZ
      Zip URL: https://download.sysinternals.com/files/BGInfo.zip
    """
    try:
        resp = requests.get(BGINFO_PAGE, headers=HEADERS, verify=False, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Find h1 with id starting with 'bginfo-v'
        h1 = soup.find('h1', id=re.compile(r'^bginfo-v\d+', re.IGNORECASE))
        version = None
        if h1:
            # Extract numeric part from id, convert to dotted version (e.g., v433 -> 4.33)
            m = re.search(r'bginfo-v(\d+)', h1.get('id', ''))
            if m:
                num = m.group(1)
                # Heuristic: v433 => 4.33, v440 => 4.40
                if len(num) >= 3:
                    version = f"{num[0]}.{num[1:]}"
                else:
                    # Fallback: use the text content 'BgInfo vX.YY' if present
                    t = h1.get_text(strip=True)
                    mt = re.search(r'BgInfo\s+v([\d\.]+)', t, re.IGNORECASE)
                    if mt:
                        version = mt.group(1)
        else:
            # Fallback: search for text 'BgInfo vX.YY' anywhere on page
            mt = re.search(r'BgInfo\s+v([\d\.]+)', soup.get_text(' ', strip=True), re.IGNORECASE)
            version = mt.group(1) if mt else None

        print('==============================')
        print('BgInfo Latest Version and Download URL:')
        if version:
            print(f'Latest Version: {version}')
        else:
            print('Latest Version: (not found)')
        print(f'Zip URL: {STATIC_ZIP_URL}')
    except Exception as e:
        print('==============================')
        print(f'BgInfo collector failed: {e}')


if __name__ == '__main__':
    bginfo_download_url()

