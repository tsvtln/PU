import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')
import logging

# Set up headers to mimic a browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# URLs
NUSPEC_URL = 'https://raw.githubusercontent.com/chocolatey-community/chocolatey-packages/master/automatic/sysinternals/sysinternals.nuspec'
RELEASES_PAGE = 'https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite'


def get_version_from_nuspec():
    """
    Fetch the version from the Chocolatey GitHub nuspec file.
    Returns version string or None.
    """
    try:
        response = requests.get(NUSPEC_URL, headers=HEADERS, verify=False, timeout=20)
        response.raise_for_status()

        # Parse XML to find <version>...</version>
        version_match = re.search(r'<version>([\d.]+)</version>', response.text)
        if version_match:
            return version_match.group(1)
    except Exception as e:
        logging.error(f"Error fetching version from nuspec: {e}")
        print(f"Error fetching version from nuspec: {e}")
    return None


def get_download_urls():
    """
    Fetch the Sysinternals Suite download page and extract URLs for:
    - Regular SysinternalsSuite.zip
    - Nano version (SysinternalsSuite-Nano.zip)

    Returns tuple (regular_url, nano_url) or (None, None) on error.
    """
    try:
        response = requests.get(RELEASES_PAGE, headers=HEADERS, verify=False, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        regular_url = None
        nano_url = None

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Look for SysinternalsSuite-Nano.zip
            if 'SysinternalsSuite-Nano.zip' in href or href.endswith('Nano.zip'):
                if not nano_url:
                    nano_url = href
            # Look for SysinternalsSuite.zip (but not Nano)
            elif 'SysinternalsSuite.zip' in href and 'Nano' not in href:
                if not regular_url:
                    regular_url = href

        # Fallback to known static URLs if not found on page
        if not regular_url:
            regular_url = 'https://download.sysinternals.com/files/SysinternalsSuite.zip'
        if not nano_url:
            nano_url = 'https://download.sysinternals.com/files/SysinternalsSuite-Nano.zip'

        return regular_url, nano_url
    except Exception as e:
        logging.error(f"Error fetching download URLs: {e}")
        print(f"Error fetching download URLs: {e}")
        # Return known static URLs as fallback
        return (
            'https://download.sysinternals.com/files/SysinternalsSuite.zip',
            'https://download.sysinternals.com/files/SysinternalsSuite-Nano.zip'
        )


def main():
    """
    Main function to fetch and print Sysinternals version and download URLs.
    """
    print('==============================')
    print('Sysinternals Latest Version and Download URLs:')
    logging.info('Sysinternals Latest Version and Download URLs:')

    # Get version from Chocolatey nuspec
    version = get_version_from_nuspec()

    if version:
        print(f'Latest Version: {version}')
        logging.info(f'Latest Version: {version}')
    else:
        print('Latest Version: (not found)')
        logging.error('Latest Version: (not found)')

    # Get download URLs
    regular_url, nano_url = get_download_urls()

    print(f'Regular Suite URL: {regular_url}')
    logging.info(f'Regular Suite URL: {regular_url}')

    print(f'Nano Suite URL: {nano_url}')
    logging.info(f'Nano Suite URL: {nano_url}')

    print('==============================')


if __name__ == '__main__':
    main()

