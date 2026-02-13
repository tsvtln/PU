import logging

from bin.checksum_calculator import CheckSumCalculator
from bin.helpers import GitWorker
from bin.helpers import Helpers
import os
import requests
import subprocess
import urllib3 as u3l
u3l.disable_warnings()
import xml.etree.ElementTree as ET
import re
import shutil

class GoogleChrome:
    def __init__(self, ldc_choco_url, azure_url, organization, project):
        self.icon = ('https://cdn.jsdelivr.net/gh/chocolatey-community/'
                       'chocolatey-packages@edba4a5849ff756e767cba86641bea97ff5721fe/icons/chrome.svg')
        self.scr_text = 'https://github.com/chocolatey-community/chocolatey-packages/tree/master/automatic/googlechrome'
        self.url64 = 'https://dl.google.com/chrome/install/googlechromestandaloneenterprise64.msi'
        self.url32 = "https://dl.google.com/chrome/install/googlechromestandaloneenterprise.msi"
        self.scr_tag = "https://github.com/chocolatey-community/chocolatey-packages/tree/master/automatic/googlechrome"
        self.installer64_temp = 'googlechromestandaloneenterprise64_'
        self.installer32_temp = 'googlechromestandaloneenterprise_'
        self.ldc_choco_url = ldc_choco_url
        self.azure_url = azure_url
        self.organization = organization
        self.project = project

    @staticmethod
    def strip_namespace(tree):
        for elem in tree.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        return tree

    def update_nuspec(self, nuspec_path, new_version):
        tree = ET.parse(nuspec_path)
        root = tree.getroot()

        # update version
        version_tag = root.find('.//{*}version')
        if version_tag is not None:
            version_tag.text = new_version
        else:
            logging.error(f"Failed to find version tag for {nuspec_path}")

        # update <iconUrl>
        icon_tag = root.find('.//{*}iconUrl')
        if icon_tag is not None:
            icon_tag.text = self.icon
        else:
            logging.error(f"Failed to find iconUrl tag for {nuspec_path}")

        # update <packageSourceUrl>
        src_tag = root.find('.//{*}packageSourceUrl')
        if src_tag is not None:
            src_tag.text = self.scr_text
        else:
            logging.error(f"Failed to find packageSourceUrl tag for {nuspec_path}")

        # Remove namespaces before writing
        self.strip_namespace(tree)
        tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)


    def download_installers(self, version, share_base, package_name):
        """
        Download official Google Chrome MSI installers and save to cache/downloaded_pkgs.
        Also copy them to the fileshare.
        Returns the full paths to the saved MSI files.
        """
        # Always use cache/downloaded_pkgs for downloads
        download_dir = os.path.join(os.getcwd(), 'LDC_Chocolatey_Autoupdater', 'cache', 'downloaded_pkgs', package_name, version)
        os.makedirs(download_dir, exist_ok=True)
        installer64_temp = os.path.join(download_dir, f"{self.installer64_temp}{version}.msi")
        installer32_temp = os.path.join(download_dir, f"{self.installer32_temp}{version}.msi")
        download64 = requests.get(self.url64, stream=True, verify=False)
        download32 = requests.get(self.url32, stream=True, verify=False)

        logging.info(f"Downloading {installer64_temp}")
        with open(installer64_temp, 'wb') as file64:
            for chunk in download64.iter_content(chunk_size=8192):
                file64.write(chunk)

        logging.info(f"Downloading {installer32_temp}")
        with open(installer32_temp, 'wb') as file32:
            for chunk in download32.iter_content(chunk_size=8192):
                file32.write(chunk)

        # Copy to fileshare
        fileshare_base = share_base
        fileshare_dir = os.path.join(fileshare_base, package_name, version)
        try:
            os.makedirs(fileshare_dir, exist_ok=True)
            shutil.copy2(installer32_temp, os.path.join(fileshare_dir, os.path.basename(installer32_temp.replace(version, '').replace('_', ''))))
            shutil.copy2(installer64_temp, os.path.join(fileshare_dir, os.path.basename(installer64_temp.replace(version, '').replace('_', ''))))
            logging.info(f"Copied installers to fileshare: {fileshare_dir}")
        except Exception as e:
            logging.error(f"Failed to copy installers to fileshare: {e}")

        return installer32_temp, installer64_temp

    def update_install_ps1(self, ps1_path, new_version, installer_path32, installer_path64):
        logging.info(f"Updating install.ps1 at {ps1_path}")
        # read the file
        with open(ps1_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # extract checksum type
        checksum_type_match = re.search(r"checksumType\s*=\s*'([^']+)'", content)
        checksum_type64_match = re.search(r"checksumType64\s*=\s*'([^']+)'", content)
        checksum_type = checksum_type_match.group(1) if checksum_type_match else 'sha256'
        checksum_type64 = checksum_type64_match.group(1) if checksum_type64_match else 'sha256'

        # get the calculated checksums
        checksum64 = CheckSumCalculator.calculate_checksum(installer_path64, checksum_type64)
        checksum32 = CheckSumCalculator.calculate_checksum(installer_path32, checksum_type)

        # build new URLs for internal repo
        url64_script = f"{self.ldc_choco_url}googlechrome/{new_version}/{self.installer64_temp[:-1]}.msi"
        url32_script = f"{self.ldc_choco_url}googlechrome/{new_version}/{self.installer32_temp[:-1]}.msi"

        # update the content
        content = re.sub(r"\$version\s*=\s*'[^']+'", f"$version = '{new_version}'", content)
        content = re.sub(r"\$url64\s*=\s*'[^']+'", f"$url64 = '{url64_script}'", content)
        content = re.sub(r"\$url\s*=\s*'[^']+'", f"$url = '{url32_script}'", content)
        content = re.sub(r"\$checksum\s*=\s*'[^']+'", f"$checksum = '{checksum32}'", content)
        content = re.sub(r"\$checksum64\s*=\s*'[^']+'", f"$checksum64 = '{checksum64}'", content)

        # write back the updated content
        with open(ps1_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def update_package(self, pkg, share_base=None):
        os.makedirs(share_base, exist_ok=True)
        repo_url = pkg["repo_url"]
        repo_name = repo_url.split('/')[-1]
        branch_name = f'update-to-{pkg["latest_version"]}'
        cwd = os.getcwd()
        os_repo_path = None

        # clone repo
        if not os.path.exists(repo_name):
            logging.info(f'Cloning repository {repo_name}')
            os_repo_path = os.path.join(cwd, 'LDC_Chocolatey_Autoupdater', 'cache', 'repo_clones', repo_name)
            clone_url = f"https://{self.azure_url}/{self.organization}/{self.project}/_git/{repo_name}"
            subprocess.run([
                'git',
                'clone',
                clone_url,
                os_repo_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        # download and save installers
        installer32_path, installer64_path = self.download_installers(
            pkg["latest_version"],
            share_base,
            'googlechrome'
        )

        # update nuspec
        nuspec_path = os.path.join(os_repo_path, 'googlechrome.nuspec')
        self.update_nuspec(nuspec_path, pkg["latest_version"])

        # update install.ps1
        install_ps1_path = os.path.join(os_repo_path, 'tools', 'chocolateyinstall.ps1')
        self.update_install_ps1(install_ps1_path, pkg["latest_version"], installer32_path, installer64_path)

        # run git operations
        git_worker = GitWorker()
        git_worker.create_and_push_branch(os_repo_path, branch_name)
        git_worker.create_pull_request(os_repo_path, branch_name, pkg)

        # clean up
        Helpers.cleaner()