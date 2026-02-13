import os

class GlobalVars:
    uipath_version = ''
    uipath_fileshare_path = '\\\\csm1pdmlsto002.file.core.windows.net\\chocolatey\\uipathremoteruntime'
    uipath_checksum = ''  # UiPathRemoteRuntime.msi

    # Secrets: provide at runtime via environment variables
    ado_token = os.environ.get('ADO_TOKEN', '')
    ado_username = os.environ.get('ADO_USERNAME', '')
    git_user_name = os.environ.get('GIT_USER_NAME', '')
    git_user_email = os.environ.get('GIT_USER_EMAIL', '')

    cache_dir = os.path.join('C:\\', 'Temp', 'uipath_pkg_updater_cache')
    branch_name = ''
    pull_request_url = ''

    # creds for the fileshare mounting
    fileshare_username = os.environ.get('FILESHARE_USERNAME', '')
    fileshare_password = os.environ.get('FILESHARE_PASSWORD', '')
