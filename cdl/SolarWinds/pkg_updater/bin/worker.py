from __future__ import annotations
from typing import Callable, Dict, Iterable, Tuple
import os
from bin.archive_files import archive_files
from bin.mount_share import AzureFileShareMounter, get_credentials_from_env

# Type aliases
ProgressCallback = Callable[[int, int, str], None]
# callback(bytes_uploaded_so_far, total_bytes, current_filename)


class Uploader:
    """
    Handles uploading files to a destination directory (local or UNC) with progress callbacks.
    """

    def __init__(self, chunk_size: int = 1024 * 1024) -> None:
        self.chunk_size = chunk_size
        self.mounter: AzureFileShareMounter | None = None
        self.share_mounted: bool = False

    def mount_share(self, username: str | None = None, password: str | None = None) -> tuple[bool, str]:
        """
        Mount the Azure File Share before uploading.

        Args:
            username: from global vars
            password: from global vars

        Returns:
            Tuple of (success: bool, message: str)
        """
        # get credentials from environment which checks the global vars
        if username is None or password is None:
            env_user, env_pass = get_credentials_from_env()
            username = username or env_user
            password = password or env_pass

        if not password:
            return False, "No password provided and AZURE_SHARE_PASSWORD or USR_PASS var not set"

        # initialize mounter to mount the fileshare where we need to upload the packages
        self.mounter = AzureFileShareMounter()

        # check if already mounted
        if self.mounter.is_mounted():
            self.share_mounted = True
            return True, "Share already mounted"

        # mount the share
        success, message = self.mounter.mount(username, password, persistent=False)
        self.share_mounted = success

        return success, message

    def _ensure_destination(self, dest_dir: str) -> None:
        os.makedirs(dest_dir, exist_ok=True)

    def _compute_total_size(self, items: Iterable[Tuple[str, str]]) -> int:
        total = 0
        for _target_name, src in items:
            if src and os.path.isfile(src):
                try:
                    total += os.path.getsize(src)
                except OSError:
                    # if size can't be determined, skip counting it
                    pass
        return total

    def upload(
        self,
        files_map: Dict[str, str],
        dest_dir: str,
        progress: ProgressCallback | None = None,
        overwrite: bool = True,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """
        Upload files to dest_dir.

        files_map: mapping from target_filename to source_path
        dest_dir: destination directory path (UNC supported if accessible)
        progress: callback receiving (bytes_done, total_bytes, current_target_name)
        overwrite: whether to overwrite existing files
        username: Optional username for mounting Azure File Share
        password: Optional password for mounting Azure File Share
        """

        # mount the share if it's a UNC path and not already mounted
        if dest_dir.startswith("\\\\") and not self.share_mounted:
            if progress:
                progress(0, 100, "Mounting Azure File Share...")

            success, message = self.mount_share(username, password)

            if not success:
                raise RuntimeError(f"Failed to mount share: {message}")

            if progress:
                progress(0, 100, f"Share mounted: {message}")

        # prepare list and compute total size
        items: Tuple[str, str]
        items = tuple((target, src) for target, src in files_map.items() if src)

        # first move old files to archive if needed
        for fn, src in items:
            if progress:
                progress(0, 100, f"Archiving old file: {fn}")
            archive_files(fn)

        total_bytes = self._compute_total_size(items)
        bytes_done = 0

        self._ensure_destination(dest_dir)

        for target_name, src_path in items:
            if not src_path or not os.path.isfile(src_path):
                # skip missing selections
                continue

            dst_path = os.path.join(dest_dir, target_name)
            # if not overwriting, skip existing
            if (not overwrite) and os.path.exists(dst_path):
                continue

            # stream copy with progress
            with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
                while True:
                    chunk = src.read(self.chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
                    bytes_done += len(chunk)
                    if progress:
                        progress(bytes_done, total_bytes, target_name)

        # final callback to ensure 100%
        if progress:
            progress(total_bytes, total_bytes, "")

