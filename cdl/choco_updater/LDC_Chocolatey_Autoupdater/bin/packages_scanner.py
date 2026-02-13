import logging

from vars.global_vars import GlobalVars
from bin.helpers import Helpers
from bin.package_updater import PackageUpdater
import os
import requests
import subprocess
import urllib3 as u3l
u3l.disable_warnings()
import xml.etree.ElementTree as ET
import packaging.version
import base64
import hashlib
import re
import shutil


class PackagesScanner(GlobalVars):
    def __init__(self):
        super().__init__()

    def scan_repos(self):
        os_repo_path = ''
        helpers = Helpers()

        # work around the SSL verify failed
        subprocess.run([
            'git',
            'config',
            '--global',
            'http.sslVerify',
            'false'
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )

        for repo in self.AZURE_REPOS:
            repo_name = repo.split('/')[-1]
            # Use absolute path for os_repo_path
            os_repo_path: str = os.path.join(self.cwd, 'cache', 'repo_clones', repo_name)

            if not os.path.exists(os_repo_path):
                logging.info(f"Downloading repository {repo}")
                try:
                    subprocess.run(
                        ['git', 'clone', repo, os_repo_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    logging.fatal(f"Failed to download repository {repo}: {e}")

            for root, dirs, files in os.walk(os_repo_path):
                for file in files:
                    if file.endswith('.nuspec'):
                        nuspec_path = os.path.join(root, file)
                        package_id, local_version = helpers.get_nuspec_info(nuspec_path)
                        latest_version = helpers.get_latest_choco_version(package_id)

                        if local_version and latest_version and local_version != latest_version:
                            logging.info(f"Package {package_id} is outdated: "
                                         f"local version {local_version}, "
                                         f"latest version {latest_version}")
                            self.outdated_packages.append({
                                "package_id": package_id,
                                "local_version": local_version,
                                "latest_version": latest_version,
                                "nuspec_path": nuspec_path,
                                "repo_url": repo
                            })
        logging.info(f'Cleaning local repos after scan.')
        if os.path.exists(os_repo_path):
            try:
                if os.name == 'nt':
                    subprocess.run([
                        'rmdir',
                        '/S',
                        '/Q',
                        os_repo_path
                    ], shell=True)
                else:
                    subprocess.run(['rm', '-rf', os_repo_path])
            except Exception as e:
                logging.error(f"Failed to remove directory {os_repo_path}: {e}")

        if len(self.outdated_packages) >= 1:
            logging.info(f'Starting update process for {len(self.outdated_packages)} packages.')
            updater = PackageUpdater()
            updater.update_outdated_packages()
        else:
            logging.info('All packages are up to date.')