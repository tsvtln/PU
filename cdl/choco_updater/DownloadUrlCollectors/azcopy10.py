import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

GITHUB_REPO = 'https://github.com/Azure/azure-storage-azcopy'
LATEST_RELEASE = f'{GITHUB_REPO}/releases/latest'
GITHUB_RELEASES = f'{GITHUB_REPO}/releases'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}


def _get_latest_stable_tag_url():
    # Try releases/latest first; if it points to a preview tag, fall back to scanning releases list
    r = requests.get(LATEST_RELEASE, headers=HEADERS, allow_redirects=True, verify=False, timeout=20)
    r.raise_for_status()
    final_url = r.url
    # If the tag contains preview suffix, scan releases page
    if re.search(r"/tag/(v[^/]*preview[^/]*)", final_url, re.IGNORECASE):
        page = requests.get(GITHUB_RELEASES, headers=HEADERS, verify=False, timeout=20)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')
        # Find release tag links and pick the first stable (no preview) tag
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/Azure/azure-storage-azcopy/releases/tag/' in href:
                # e.g., /Azure/azure-storage-azcopy/releases/tag/v10.31.0
                if re.search(r"/tag/(v\d+\.\d+\.\d+)$", href):
                    return 'https://github.com' + href
        # Fallback to final_url if none found
        return final_url
    return final_url


def azcopy10_download_url():
    """
    Resolve the latest azcopy v10 release from GitHub and print:
      Latest Version: v10.xx.x
      amd64 URL: <download url>
      386 URL: <download url>
    """
    try:
        # Resolve latest stable tag URL
        final_url = _get_latest_stable_tag_url()
        m = re.search(r"/tag/(v\d+\.\d+\.\d+)$", final_url)
        version_tag = m.group(1) if m else None

        amd64_url = None
        i386_url = None

        if version_tag:
            # Deterministic asset URLs based on the version tag
            base_dl = f"{GITHUB_REPO}/releases/download/{version_tag}"
            i386_url = f"{base_dl}/azcopy_windows_386_{version_tag.replace('v','')}\.zip".replace('\\', '')
            amd64_url = f"{base_dl}/azcopy_windows_amd64_{version_tag.replace('v','')}\.zip".replace('\\', '')

        # Fallback: Parse assets from tag page, skipping preview files
        if not amd64_url or not i386_url:
            page = requests.get(final_url, headers=HEADERS, verify=False, timeout=20)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                href_l = href.lower()
                if '/Azure/azure-storage-azcopy/releases/download/' in href and href.endswith('.zip'):
                    if 'preview' in href_l:
                        continue
                    full = 'https://github.com' + href
                    if 'windows_amd64' in href_l:
                        amd64_url = full
                    elif 'windows_386' in href_l:
                        i386_url = full

        print('==============================')
        print('AzCopy v10 Latest Version and Download URLs:')
        if version_tag:
            print(f'Latest Version: {version_tag}')
        else:
            print('Latest Version: (not found)')
        if amd64_url:
            print(f'amd64 URL: {amd64_url}')
        else:
            print('Missing: amd64 URL')
        if i386_url:
            print(f'386 URL: {i386_url}')
        else:
            print('Missing: 386 URL')
    except Exception as e:
        print('==============================')
        print(f'AzCopy v10 collector failed: {e}')


if __name__ == '__main__':
    azcopy10_download_url()
