"""
Module for mounting Azure File Share on Windows using net use command.
"""
import subprocess
import os
from typing import Optional

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

from bin.global_vars import GlobalVars


class AzureFileShareMounter:
    """
    Handles mounting Azure File Share on Windows.
    """

    def __init__(self, storage_account: str = "csm1pdmlsto002", share_name: str = "chocolatey"):
        self.storage_account = storage_account
        self.share_name = share_name
        self.share_path = f"\\\\{storage_account}.file.core.windows.net\\{share_name}"

    def mount(self, username: str, password: str, persistent: bool = False) -> tuple[bool, str]:
        """
        Mount the Azure File Share using net use command.

        Args:
            username: User in format "GLOBAL\\USERNAME"
            password: Access key or password
            persistent: Whether to make the connection persistent

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # build the net use command
            persistence = "yes" if persistent else "no"

            # use subprocess with password passed securely
            cmd = [
                "net", "use",
                self.share_path,
                password,
                f"/user:{username}",
                f"/persistent:{persistence}"
            ]

            print(f"Mounting: {self.share_path}")
            print(f"User: {username}")

            # execute the command
            result = run_hidden(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return True, f"Successfully mounted {self.share_path}"
            else:
                # check if already mounted
                if "already" in result.stderr.lower() or "multiple connections" in result.stderr.lower():
                    return True, f"Already mounted: {self.share_path}"

                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return False, f"Failed to mount: {error_msg}"

        except Exception as e:
            return False, f"Exception during mount: {str(e)}"

    def unmount(self) -> tuple[bool, str]:
        """
        Unmount the Azure File Share.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["net", "use", self.share_path, "/delete"]

            result = run_hidden(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                creationflags=_NO_WINDOW
            )

            if result.returncode == 0:
                return True, f"Successfully unmounted {self.share_path}"
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return False, f"Failed to unmount: {error_msg}"

        except Exception as e:
            return False, f"Exception during unmount: {str(e)}"

    def is_mounted(self) -> bool:
        """
        Check if the share is currently mounted.

        Returns:
            True if mounted, False otherwise
        """
        try:
            # net use to list current connections
            result = run_hidden(
                ["net", "use"],
                capture_output=True,
                text=True,
                check=False,
                creationflags=_NO_WINDOW
            )

            # check if our share path appears in the output
            return self.share_path.lower() in result.stdout.lower()

        except Exception:
            return False


def get_credentials_from_env() -> tuple[Optional[str], Optional[str]]:
    """
    Get credentials from environment variables.

    Returns:
        Tuple of (username, password) or (None, None) if not found
    """
    username = GlobalVars.fileshare_username
    password = GlobalVars.fileshare_password

    return username, password
