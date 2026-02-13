"""
Script to launch the Software Package Uploader application.
User needs to select at least 1 file to be uploaded and the new version of SolarWinds
The program will then upload the selected files to the SolarWinds file share
move the old files to a dated subdirectory under the file share
create a new branch, make a commit and push the changes to the repository, and will submit a PR for which
a link will be provided to the user.


tsvetelin.maslarski-ext@ldc.com
"""

from bin.graphical_window import PackageUploaderApp


PackageUploaderApp().mainloop()
