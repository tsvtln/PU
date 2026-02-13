"""
Script to launch the UiPath Remote Runtime Package Uploader application.
User needs to select the UiPathRemoteRuntime.msi file to be uploaded and the new version
The program will then upload the file to the UiPath file share
move the old file to a dated subdirectory under the file share
create a new branch, make a commit and push the changes to the repository, and will submit a PR for which
a link will be provided to the user.


tsvetelin.maslarski-ext@ldc.com
"""

from bin.graphical_window import PackageUploaderApp


PackageUploaderApp().mainloop()

