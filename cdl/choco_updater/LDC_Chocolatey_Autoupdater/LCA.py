"""
//TODO
- Fix namespace being put into the resulting nuspec like:     <ns0:version>141.0.7390.55</ns0:version>
- Send mail after successful pull request to automation team with details of the updated packages and links to the PRs.
- Have a test against a VM to install the updated packages and verify the installation.
- Destroy any created VM for the test install
- Configure the ado_token and ado_username via environment variables so the program would work in a pipeline.
"""

"""
### 0.0.6 - 2025-07-10
### Changes:
- Added error handling for git clone operation in case of network issues or invalid repository URLs.
- Improved logging to include timestamps for better tracking of events.
- Added functionality to clean up local repository clones after scanning to save disk space.
- Refactored code to use absolute paths for repository clones to avoid issues with relative paths.
- Added helper function for cleanup operations to ensure all temporary files and directories are removed after processing.
- Added cleanup before any operations at program start to ensure a fresh start.
- Added handling for SSL verification issues during git operations.
- Added handling for SSL verification issues during download of installers.
- Fixed installers naming when posted into local Chocolatey repo.
- Fixed not saving the files into the local Chocolatey repo.
- Fixed not creating branch and pull request.
- Fixed not using absolute paths for repository clones.
- Fixed repo_name being the full os path instead of just the repo name.
- Added fallbacks for several methods to avoid crashes.
- Added config subprocess for git credential helper to avoid git asking for credentials during operations.
- Added subprocess to self config the git user email and name to avoid issues during branch creation and pull requests.
- Fixed bug with repo_name split.
- Fixed several bugs with improper os path handling.
- Fixed PR message to mention updated package properly (it was the full OS path instead).
- Fixed extension on git operations trying to use OS path instead of repo name.
- Updated logger config to DEBUG level.
- Added updater getter to collect all updater modules instead of a static dict.
- Added type hints to several methods and variables to satisfy PEP 8.
- Arranged the flow of the program to be more logical and easier to follow.
"""


from bin.helpers import Logger
from bin.packages_scanner import PackagesScanner
from bin.helpers import Helpers

Logger().logger()

Helpers().cleaner()

scanner = PackagesScanner()
scanner.scan_repos()


