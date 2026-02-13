import hashlib
from bin.global_vars import GlobalVars
import os

import urllib3 as u3l

u3l.disable_warnings()

import requests
import subprocess
import base64
import xml.etree.ElementTree as ET

# Constant to hide console windows when running subprocess commands
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

def run_hidden(*args, **kwargs):
    # Always hide the window on Windows
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs['startupinfo'] = si
        kwargs['creationflags'] = kwargs.get('creationflags', 0) | _NO_WINDOW
    return subprocess.run(*args, **kwargs)

class CheckSumCalculator:
    @staticmethod
    def calculate_checksum(file_path, checksum_type):
        """
        Calculate the checksum of a file using the specified type (e.g., 'sha256', 'sha1', 'md5').
        Returns the hex digest string.
        """
        hash_func = getattr(hashlib, checksum_type, None)
        if hash_func is None:
            print(f'[ERROR] Unsupported checksum type: {checksum_type} was passed.', flush=True)
            raise ValueError(f"Unsupported checksum type: {checksum_type}")

        h = hash_func()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

class SaveCheckSums(GlobalVars):
    def __init__(self):
        super().__init__()

    def save_checksums(self) -> list:
        """
        Scan the version subfolder in the fileshare directory for UiPath Remote Runtime MSI file and calculate its SHA256 checksum.
        Sets the checksum on the GlobalVars class so it's accessible globally.
        :return: List of items with calculated checksums for printing.
        """
        # The file is now in a version subfolder (e.g., uipathremoteruntime/25.1.1/UiPathRemoteRuntime.msi)
        version_dir = os.path.join(GlobalVars.uipath_fileshare_path, GlobalVars.uipath_version)

        if not os.path.exists(version_dir):
            return [f'ERROR: Version folder {GlobalVars.uipath_version} does not exist']

        file_path = os.path.join(version_dir, 'UiPathRemoteRuntime.msi')

        if os.path.isfile(file_path):
            GlobalVars.uipath_checksum = CheckSumCalculator.calculate_checksum(file_path, 'sha256')
            return [f'CheckSum for {GlobalVars.uipath_version}\\UiPathRemoteRuntime.msi: {GlobalVars.uipath_checksum}']
        else:
            return [f'ERROR: UiPathRemoteRuntime.msi not found in {GlobalVars.uipath_version} folder']

class GitWorker(GlobalVars):
    def __init__(self):
        super().__init__()

        run_hidden([
            'git', 'config', '--global', 'user.name', self.git_user_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        run_hidden([
            'git', 'config', '--global', 'user.email', self.git_user_email
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    @staticmethod
    def update_from_repo():
        if not os.path.exists(GlobalVars.cache_dir):
            os.makedirs(os.path.join(GlobalVars.cache_dir), exist_ok=True)
        repo_url = "https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/uipathremoteruntime"
        tp = (f"Cloning repository from {repo_url}")
        run_hidden([
            'git',
            'clone',
            repo_url,
            GlobalVars.cache_dir
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_NO_WINDOW)

        return tp


    @staticmethod
    def create_and_push_branch():
        os_repo_path = os.path.join(GlobalVars.cache_dir)

        GlobalVars.branch_name = f'update-to-{GlobalVars.uipath_version}'

        # create branch
        result = run_hidden([
            'git', 'checkout', '-b', GlobalVars.branch_name
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                print(f'[ERROR] {line}')

        # add the changes and log any errors
        result = run_hidden([
            'git', 'add', '.'
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                print(f'[ERROR] {line}')

        # commit the changes and log any errors
        result = run_hidden([
            'git', 'commit', '-m',
            f"Updating UiPath Remote Runtime to version {GlobalVars.uipath_version} "
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('[') or 'Updating UiPath' in line:
                print(f'[INFO] {line}')
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                print(f'[ERROR] {line}')

        # push branch, log any errors
        push_url = "https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/uipathremoteruntime"
        result = run_hidden([
            'git', 'push', push_url, GlobalVars.branch_name
        ], cwd=os_repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=_NO_WINDOW)
        for line in result.stdout.splitlines():
            if line.startswith('To ') or line.startswith(' * ') or 'branch' in line:
                print(f'[INFO] {line}')
        for line in result.stderr.splitlines():
            if 'fatal:' in line or 'error:' in line:
                print(f'[ERROR] {line}')


    @staticmethod
    def create_pull_request():

        api_url = (f"https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey"
                   f"/_apis/git/repositories/uipathremoteruntime/pullrequests?api-version=7.0")
        headers = {
            "Authorization": "Basic " + base64.b64encode(f":{GlobalVars.ado_token}".encode()).decode(),
            "Content-Type": "application/json"
        }
        pull_request_data = {
            'sourceRefName': f'refs/heads/{GlobalVars.branch_name}',
            'targetRefName': 'refs/heads/master',
            "title": f"Updating UiPath Remote Runtime to version {GlobalVars.uipath_version}",
            "description": f"Update of UiPath Remote Runtime from the LDC UiPath Package Updater tool.",
        }
        try:
            response = requests.post(api_url, headers=headers, json=pull_request_data, verify=False)
            if response.status_code == 201:
                pr_id = response.json().get('url').split('/')[-1]
                pr_url = (f"https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/"
                               f"uipathremoteruntime/pullrequest/{pr_id}")
                GlobalVars.pull_request_url = pr_url
                return True
            else:
                print(f'[FATAL] Failed to create pull request '
                      f'Response code: {response.status_code}, Response: {response.text}')
                return False
        except Exception as pr_ex:
            print(f'[FATAL] Unexpected failure to create pull request: {pr_ex}', flush=True)
            return False

class FileUpdater:
    @staticmethod
    def update_ps() -> list:
        """
        Update the checksum in the chocolateyinstall.ps1 file for UiPath Remote Runtime MSI.
        Uses context-aware replacement by identifying the URL line first, then updating the checksum below it.
        """
        # validate that checksum has been calculated
        if not GlobalVars.uipath_checksum:
            raise ValueError("uipath_checksum is empty! Run save_checksums() first.")

        ps_path = os.path.join(GlobalVars.cache_dir, 'tools', 'chocolateyinstall.ps1')

        with open(ps_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # track which checksums we've updated
        updated = []

        # process line by line to find and update the $checksum64 variable assignment
        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for the $checksum64 variable assignment with quotes (not the reference in hashtable)
            # The assignment line will have quotes: $checksum64 = '...' or $checksum64 = "..."
            if '$checksum64' in line and '=' in line and ("'" in line or '"' in line):
                # Make sure this is not inside the hashtable (hashtable lines don't have $ prefix for values)
                line_stripped = line.strip()
                if line_stripped.startswith('$checksum64'):
                    # Extract the current value for logging
                    old_checksum = line.split('=')[1].strip().strip("'\"")

                    # Preserve indentation and format
                    indent = line[:len(line) - len(line.lstrip())]
                    lines[i] = f"{indent}$checksum64     = '{GlobalVars.uipath_checksum.upper()}'\n"

                    updated.append(f"UiPathRemoteRuntime.msi: Updated checksum from {old_checksum[:16]}... to {GlobalVars.uipath_checksum.upper()[:16]}...")
                    i += 1
                    continue

            i += 1

        # verify we updated the checksum
        if len(updated) != 1:
            raise ValueError(f"Expected to update 1 checksum but updated {len(updated)}: {updated}")

        # write the updated content back
        with open(ps_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return updated


    @staticmethod
    def update_nuspec():
        """
        Update the version in the uipathremoteruntime.nuspec file.
        Uses the version from GlobalVars.uipath_version.
        """
        # Validate that version has been set
        if not GlobalVars.uipath_version:
            raise ValueError("uipath_version is empty! Set the version first.")

        nuspec_path = os.path.join(GlobalVars.cache_dir, 'uipathremoteruntime.nuspec')

        if not os.path.exists(nuspec_path):
            raise FileNotFoundError(f"Nuspec file not found at: {nuspec_path}")

        # Parse the XML file
        tree = ET.parse(nuspec_path)
        root = tree.getroot()

        # Find the version tag (with namespace support)
        version_tag = root.find('.//{*}version')

        if version_tag is not None:
            old_version = version_tag.text
            version_tag.text = GlobalVars.uipath_version
            result = f"Version updated: {old_version} -> {GlobalVars.uipath_version}"
        else:
            raise ValueError('Failed to find <version> tag in nuspec file')

        # Strip namespace for cleaner output
        def strip_namespace(tr):
            for elem in tr.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            return tr

        strip_namespace(tree)

        # Write back to file
        tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)

        return result

