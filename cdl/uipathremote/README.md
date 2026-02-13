# UiPath Remote Runtime Package Updater

This program automates the process of updating the UiPath Remote Runtime package in the Chocolatey repository.

## Overview

The UiPath Remote Runtime Package Updater is a GUI application that:
1. Allows you to select the UiPathRemoteRuntime.msi file to upload
2. Specify the new version number
3. Uploads the file to the Azure File Share
4. Creates new version folder in the repository
5. Clones the Git repository
6. Updates the checksum in chocolateyInstall.ps1
7. Updates the version in the nuspec file
8. Creates a new branch, commits changes, and pushes to Azure DevOps
9. Creates a pull request for review

## Requirements

- Python 3.7+
- Git installed and configured
- Access to Azure DevOps repository
- Credentials for Azure File Share mounting

### Steps in the GUI:

1. **Select File**: Click the "Browse" button to select the UiPathRemoteRuntime.msi file
2. **Enter Version**: Input the new version number (e.g., 24.10.1)
3. **Upload**: Click the "Upload" button to start the process
4. **Review Progress**: Monitor the upload progress and Git operations
5. **Copy PR Link**: When complete, copy the pull request link to send for approval

## File Structure

```
uipathremote/
├── UpdateUiPathPackage.py      # Main entry point
├── requirements.txt             # Python dependencies
├── bin/
│   ├── __init__.py             # Package marker
│   ├── archive_files.py        # Archive old files
│   ├── global_vars.py          # Global configuration
│   ├── graphical_window.py     # Main GUI
│   ├── helpers.py              # Checksum, Git, and file update helpers
│   ├── mount_share.py          # Azure File Share mounting
│   ├── updater.py              # Post-upload update operations
│   └── worker.py               # File upload worker
└── lib/
    └── app.ico                 # Application icon
```

## Configuration

Edit `bin/global_vars.py` to update:
- Azure File Share path
- Azure DevOps credentials
- Git user information
- Repository URLs

## Notes

- The application will create new version folder
- All Git operations are performed in a temporary cache directory
- The application creates a pull request that requires approval before merging

## Author

tsvetelin.maslarski-ext@ldc.com

## Related

This application is based on the SolarWinds Agent Package Updater and follows the same workflow pattern.

