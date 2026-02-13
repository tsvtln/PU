import base64

from vars.global_vars import GlobalVars
import xml.etree.ElementTree as ET
import logging
import os
from datetime import datetime

import os
import requests
import subprocess
import urllib3 as u3l
u3l.disable_warnings()
import packaging.version

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
# for testing
from decouple import config

class Helpers(GlobalVars):
    def __init__(self):
        super().__init__()

    def get_nuspec_info(self, nuspec_path):
        try:
            tree = ET.parse(nuspec_path)
            root = tree.getroot()
            ns = {'ns': self.nuspec_schema}
            version = root.find('ns:version', ns)
            package_id = root.find('.//ns:id', ns)
            if package_id is not None and version is not None:
                return package_id.text, version.text
        except Exception as exp_ns:
            logging.warning('Failed to parse nuspec file with namespace, will try without namespace.')

        # fallback to non-namespaced parsing
        try:
            tree = ET.parse(nuspec_path)
            root = tree.getroot()
            version = root.find('.//version')
            package_id = root.find('.//id')
            if package_id is not None and version is not None:
                return package_id.text, version.text
        except Exception as exp_non_ns:
            logging.warning(f"Failed to parse nuspec file {nuspec_path}: {exp_non_ns}."
                          f"Will fallback to filename parsing.")

        # fallback to try extracting from filename or repo name
        package_id = os.path.splitext(os.path.basename(nuspec_path))[0]
        version = None

        # try extracting version from file as plain text
        try:
            with open(nuspec_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '<version>' in line:
                        version = line.split('<version>')[1].split('</version>')[0].strip()
                        break
        except Exception as exp_file:
            logging.error(f"Failed to extract version from file {nuspec_path}: {exp_file}"
                          f"Package ID extracted from filename: {package_id}"
                          f"Version extracted: {version}")
        return package_id, version

    def get_latest_choco_version(self, package_id):
        """
        Query Chocolatey API to get the latest version of a package by its ID.
        """
        # Use FindPackagesById endpoint for reliable results
        url = f"{self.choco_api}FindPackagesById()?id='{package_id.lower()}'"
        response = requests.get(url, verify=False)
        versions = []

        if response.status_code == 200:
            tree = ET.fromstring(response.content)
            # Find all version elements in the XML response
            for ver in tree.findall(self.d_version):
                if ver is not None and ver.text:
                    if 'rtw' in ver.text:
                        ver_redacted = ver.text.replace('-rtw', '')
                        versions.append(ver_redacted)
                    elif 'prerelease' in ver.text:
                        ver_redacted = ver.text.replace('-prerelease', '')
                        versions.append(ver_redacted)
                    else:
                        versions.append(ver.text)
            # Log the extracted versions for debugging
            logging.debug(f"Extracted versions for {package_id}: {versions}")
            if versions:
                # Sort versions using packaging.version to handle complex versioning schemes
                return sorted(versions, key=packaging.version.parse)[-1]
            else:
                logging.fatal(f"Failed to extract versions for {package_id}: {versions}")
            return None
        return None

    def update_nuspec_version(self, nuspec_path, new_version):
        tree = ET.parse(nuspec_path)
        root = tree.getroot()
        ns = {'ns': self.nuspec_schema}
        version = root.find('ns:version', ns)
        if version is not None:
            version.text = new_version
        else:
            version = root.find('.//version')
            if version is not None:
                version.text = new_version
            else:
                logging.fatal(f"Could not find version element in {nuspec_path}")
                return False
        tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)
        return True

    @staticmethod
    def cleaner():
        cwd = os.getcwd()
        download_dir = os.path.join(cwd, 'cache', 'downloaded_pkgs')
        repo_clones = os.path.join(cwd, 'cache', 'repo_clones')

        def clean_dir(dir_path):
            # remove all directories from list_dir
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        try:
                            if os.name == 'nt':
                                subprocess.run([
                                    'rmdir',
                                    '/S',
                                    '/Q',
                                    file_path
                                ], shell=True)
                            else:
                                subprocess.run(['rm', '-rf', file_path])
                        except Exception as e:
                            logging.error(f"Failed to remove directory {file_path}: {e}")

                    elif os.path.isdir(file_path):
                        try:
                            if os.name == 'nt':
                                subprocess.run([
                                    'rmdir',
                                    '/S',
                                    '/Q',
                                    file_path
                                ], shell=True)
                            else:
                                subprocess.run(['rm', '-rf', file_path])
                        except Exception as e:
                            logging.error(f"Failed to remove directory {file_path}: {e}")
                except Exception as e:
                    logging.fatal(f"Failed to remove directory {file_path}: {e}")


        if os.path.exists(download_dir):
            clean_dir(download_dir)
        if os.path.exists(repo_clones):
            clean_dir(repo_clones)



class GitWorker(GlobalVars):
    def __init__(self):
        super().__init__()
        subprocess.run(
            [
                'git',
                'config',
                '--global',
                'credential.helper',
                'manager-core'
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run([
            'git',
            'config',
            'user.name',
            'Tsvetelin.Maslarski'
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run(
            [
            'git',
            'config',
            '--global',
            'user.email',
            'tsvetelin.maslarski-ext@ldc.com'
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def create_and_push_branch(self, repo_name, branch_name):
        # repo_name is just the repo name, os_repo_path is the local path
        repo_name_split = repo_name.split('\\')[-1]
        os_repo_path = os.path.join(os.getcwd(), 'cache', 'repo_clones', repo_name)

        # create branch
        result = subprocess.run([
            'git', 'checkout', '-b', branch_name
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                logging.error(line)
        # add and commit all changes
        result = subprocess.run([
            'git', 'add', '.'
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                logging.error(line)
        result = subprocess.run([
            'git', 'commit', '-m',
            f"Automated update by Chocolatey Updater for {repo_name_split} to version {branch_name.replace('update-to-', '')}"
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('[') or 'Automated update by Chocolatey Updater' in line:
                logging.info(line)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                logging.error(line)
        # push branch (use repo_name for remote URL)
        push_url = (f"https://{self.ado_username}:{self.ado_token}@{self.azure_url}/"
                    f"{self.organization}/{self.project}/_git/{repo_name_split}")
        result = subprocess.run([
            'git', 'push', push_url, branch_name
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('To ') or line.startswith(' * ') or 'branch' in line:
                logging.info(line)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                logging.error(line)

    def create_pull_request(self, repo_name, branch_name, package):
        repo_name_split = repo_name.split('\\')[-1]
        api_url = f"https://{self.azure_url}/{self.organization}/{self.project}/_apis/git/repositories/{repo_name_split}/pullrequests?api-version=7.0"
        headers = {
            "Authorization": "Basic " + base64.b64encode(f":{self.ado_token}".encode()).decode(),
            "Content-Type": "application/json"
        }
        pull_request_data = {
            'sourceRefName': f'refs/heads/{branch_name}',
            'targetRefName': 'refs/heads/master',
            "title": f"Automated update of {package['package_id']} to {package['latest_version']}",
            "description": f"Automated update of {package['package_id']} from {package['local_version']} to {package['latest_version']}",
        }
        try:
            response = requests.post(api_url, headers=headers, json=pull_request_data, verify=False)
            if response.status_code == 201:
                logging.info(f"Successfully created pull request {package['package_id']}")
            else:
                logging.fatal(f"Failed to create pull request for {package['package_id']}. Response code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as pr_ex:
            logging.fatal(f"Unexpected failure to create pull request for {repo_name_split}: {pr_ex}")
            return False


class Logger(GlobalVars):
    def __init__(self):
        super().__init__()

    def logger(self):
        """
        set the output file (filename=logname)
        set it to append (filemode='a') rather than overwrite (filemode='w')
        determine the format of the output message (format=...)
        determine the format of the output date and time (datefmt='%Y-%m-%d')
        and determine the minimum message level it will accept (level=logging.DEBUG).
        """

        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'chocoupdater' + datetime.today().strftime('%Y-%m-%d') + '.log')
        logging.basicConfig(filename=log_file,
                            filemode='a',
                            format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d',
                            level=logging.DEBUG)

        logging.info("\n##########################################\n"
                     "####### Running Chocolatey Updater #######\n"
                     "##########################################")
