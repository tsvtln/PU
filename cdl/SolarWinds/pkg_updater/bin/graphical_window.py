import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Dict, Optional
import os
import threading
import queue

from bin.worker import Uploader
from bin.updater import Updater
from bin.global_vars import GlobalVars


class PackageUploaderApp(tk.Tk):
    def __init__(self, icon_path: Optional[str] = None, taskbar_icon_path: Optional[str] = None) -> None:
        super().__init__()
        self.title("SolarWinds Agent Package Updater")
        self.geometry("720x360")
        self.resizable(False, False)

        # attempt to set custom icons (window + taskbar)
        self._set_window_and_taskbar_icons(icon_path, taskbar_icon_path)

        # store selected file paths keyed by display name
        self.selected_files: Dict[str, Optional[str]] = {}

        # store version input
        self.version_var: Optional[tk.StringVar] = None

        # store upload button reference to enable/disable based on version
        self.upload_btn: Optional[tk.Button] = None

        # store upload destination for passing to updater
        self.upload_destination: Optional[str] = None

        # define the package entries to show
        self.packages = [
            "SolarWinds-Agent-Windows-Active-001.7z",
            "SolarWinds-Agent-Windows-Active-002.7z",
            "Solarwinds-Agent-Windows-Passive.zip",
            "swagent-rhel-001.tar.gz",
            "swagent-rhel-002.tar.gz",
            "swiagent-rhel-passive.tar.gz",
        ]

        self._build_ui()

    def _lib_dir(self) -> str:
        # lib folder is expected to be sibling of bin (project structure shows bin/ and lib/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        proj_root = os.path.dirname(script_dir)
        return os.path.join(proj_root, "lib")

    def _set_window_and_taskbar_icons(self, icon_path: Optional[str], taskbar_icon_path: Optional[str]) -> None:
        # On Windows, iconbitmap with .ico handles both window and taskbar
        try:
            ico_candidate = None
            if icon_path and os.path.isfile(icon_path):
                ico_candidate = icon_path
            else:
                # default to lib/app.ico
                lib_ico = os.path.join(self._lib_dir(), "app.ico")
                if os.path.isfile(lib_ico):
                    ico_candidate = lib_ico
            if ico_candidate:
                self.iconbitmap(ico_candidate)
        except Exception:
            pass

    def _build_ui(self) -> None:
        # container frame with padding
        container = tk.Frame(self, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        # Header
        header = tk.Label(
            container,
            text="Select package files to upload",
            font=("Segoe UI", 12, "bold"),
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # create rows: label, entry (read-only), browse button
        self.entry_vars: Dict[str, tk.StringVar] = {}
        for i, pkg in enumerate(self.packages, start=1):
            # Label
            tk.Label(container, text=pkg, anchor="w").grid(
                row=i, column=0, sticky="w", padx=(0, 8)
            )

            # entry to show path (read-only)
            var = tk.StringVar(value="")
            self.entry_vars[pkg] = var
            entry = tk.Entry(container, textvariable=var, width=70, state="readonly")
            entry.grid(row=i, column=1, sticky="we", padx=(0, 8))

            # browse button
            btn = tk.Button(
                container,
                text="Browse",
                command=lambda name=pkg: self._browse_file(name),
                width=10,
            )
            btn.grid(row=i, column=2, sticky="e")

        # version input field
        version_label = tk.Label(
            container,
            text="SolarWinds Version:",
            font=("Segoe UI", 9),
            anchor="w"
        )
        version_label.grid(row=7, column=0, sticky="w", pady=(12, 0))

        # spacer
        spacer_row = len(self.packages) + 1
        tk.Label(container, text="").grid(row=spacer_row, column=0)



        # action buttons
        actions_row = spacer_row + 1
        self.upload_btn = tk.Button(container, text="Upload", command=self._on_upload, width=12, state="disabled")
        cancel_btn = tk.Button(container, text="Cancel", command=self._on_cancel, width=12)
        # put actions bottom-right
        container.grid_columnconfigure(1, weight=1)
        cancel_btn.grid(row=actions_row, column=2, sticky="e")
        self.upload_btn.grid(row=actions_row, column=1, sticky="e", padx=(0, 8))

        version_row = spacer_row + 1

        self.version_var = tk.StringVar(value="")

        # add trace to enable/disable upload button based on version input
        def on_version_change(*args):
            version_text = self.version_var.get().strip()
            if version_text:
                self.upload_btn.config(state="normal")
            else:
                self.upload_btn.config(state="disabled")

        self.version_var.trace_add("write", on_version_change)

        # validation function to allow only digits and dots
        def validate_version_input(new_value):
            # allow empty string
            if new_value == "":
                return True
            # only allow digits and dots
            return all(c.isdigit() or c == '.' for c in new_value)

        # register validation
        vcmd = (container.register(validate_version_input), '%P')

        version_entry = tk.Entry(
            container,
            textvariable=self.version_var,
            width=30,
            font=("Segoe UI", 9),
            validate="key",
            validatecommand=vcmd
        )
        version_entry.grid(row=7, column=1, sticky="w", pady=(12, 0), padx=(0, 8))

        # footer with fileshare access info
        footer_row = version_row + 1
        footer_text = "©SolarWinds Agent Updater, Copyright 2025, LDC"
        footer_label = tk.Label(
            container,
            text=footer_text,
            font=("Segoe UI", 9),
            fg="#666666",
            anchor="w"
        )
        footer_label.grid(row=footer_row, column=0, columnspan=3, sticky="w", pady=(12, 0))

        # version info
        footer_row = version_row + 2
        footer_text = "Version 1.0.0"
        footer_label = tk.Label(
            container,
            text=footer_text,
            font=("Segoe UI", 9),
            fg="#666666",
            anchor="w"
        )
        footer_label.grid(row=footer_row, column=0, columnspan=3, sticky="w", pady=(12, 0))

    def _browse_file(self, name: str) -> None:
        # choose any file; initial dir can be workspace if desired
        path = filedialog.askopenfilename(
            title=f"Select file for {name}",
            initialdir="C:/",
        )
        if path:
            self.selected_files[name] = path
            # update entry text
            self.entry_vars[name].set(path)

    def _on_upload(self) -> None:
        # save version to GlobalVars (version is guaranteed to be non-empty since button is disabled otherwise)
        if self.version_var:
            version = self.version_var.get().strip()
            GlobalVars.solarwinds_version = version
            print(f"Version saved: {version}")  # Debug

        # validate selections
        empty = [name for name in self.packages if not self.selected_files.get(name)]
        if empty:
            msg = (
                "The following entries have no selected file:\n- "
                + "\n- ".join(empty)
                + "\n\nProceed with upload anyway?"
            )
            proceed = messagebox.askyesno("Missing files", msg)
            if not proceed:
                return

        # build map of target name -> selected file path (skip empties)
        files_map: Dict[str, str] = {
            name: path for name, path in self.selected_files.items() if path
        }

        if not files_map:
            messagebox.showwarning("No files", "No files selected to upload.")
            return

        # destination UNC path (requested share)
        #dest_dir = r"\\csm1pdmlsto002.file.core.windows.net\chocolatey\_test_upload"
        dest_dir = GlobalVars.solarwinds_fileshare_path

        # store the destination for later use in updater
        self.upload_destination = dest_dir

        # show progress window and start background upload
        self._show_progress_and_start_upload(files_map, dest_dir)

    def _show_progress_and_start_upload(self, files_map: Dict[str, str], dest_dir: str) -> None:
        print(f"Creating progress window for {len(files_map)} file(s)")  # Debug

        # create a modal progress window BEFORE hiding main window
        progress_win = tk.Toplevel(self)
        progress_win.title("Uploading packages…")
        progress_win.geometry("600x180")
        progress_win.resizable(False, False)

        # set icon for progress window (same as main window)
        try:
            lib_ico = os.path.join(self._lib_dir(), "app.ico")
            if os.path.isfile(lib_ico):
                progress_win.iconbitmap(lib_ico)
        except Exception:
            pass

        print("Progress window created")  # Debug

        # handle window close button (X)
        def on_progress_close():
            if messagebox.askyesno("Cancel Upload", "Upload in progress. Are you sure you want to cancel?"):
                progress_win.destroy()
                self.destroy()  # Close the entire app

        progress_win.protocol("WM_DELETE_WINDOW", on_progress_close)

        # now hide the selection window
        self.withdraw()

        print("Main window hidden")  # Debug

        # make sure the progress window appears on top and has focus
        progress_win.lift()
        progress_win.focus_force()
        progress_win.attributes('-topmost', True)
        progress_win.after(100, lambda: progress_win.attributes('-topmost', False))

        # UI elements
        container = tk.Frame(progress_win, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        status_var = tk.StringVar(value="Preparing upload…")
        tk.Label(container, textvariable=status_var, anchor="w", font=("Segoe UI", 10)).pack(fill="x")

        pbar = ttk.Progressbar(container, mode="determinate", length=550)
        pbar.pack(fill="x", pady=(8, 8))

        percent_var = tk.StringVar(value="0%")
        tk.Label(container, textvariable=percent_var, anchor="e", font=("Segoe UI", 9)).pack(fill="x")

        btn_frame = tk.Frame(container)
        btn_frame.pack(fill="x", pady=(12, 0))
        continue_btn = tk.Button(btn_frame, text="Continue", state="disabled", width=12,
                                 command=lambda: self._finish_after_upload(progress_win))
        continue_btn.pack(side="right")

        # queue for progress updates
        prog_queue: queue.Queue = queue.Queue()

        def progress_callback(done: int, total: int, current: str) -> None:
            prog_queue.put(("progress", done, total, current))

        def worker_thread() -> None:
            try:
                print(f"Starting upload to {dest_dir}")  # Debug
                uploader = Uploader()
                uploader.upload(files_map, dest_dir, progress=progress_callback)
                prog_queue.put(("done", None, None, None))  # signal completion
                print("Upload complete")  # Debug
            except Exception as exc:
                print(f"Upload error: {exc}")  # Debug
                prog_queue.put(("error", str(exc), None, None))

        thread = threading.Thread(target=worker_thread, daemon=True)
        thread.start()

        # poll for progress
        def poll() -> None:
            try:
                while True:
                    item = prog_queue.get_nowait()
                    tag = item[0]

                    if tag == "progress":
                        _, done, total, current = item
                        if total and total > 0:
                            pbar["maximum"] = total
                            pbar["value"] = done
                            pct = int(done * 100 / total) if total else 0
                            percent_var.set(f"{pct}%")
                            if current:
                                status_var.set(f"Uploading: {current}")
                        else:
                            # indeterminate if total unknown
                            pbar.configure(mode="indeterminate")
                            pbar.start(10)
                    elif tag == "done":
                        status_var.set("Upload complete.")
                        pbar.stop()
                        if pbar["maximum"]:
                            pbar["value"] = pbar["maximum"]
                        percent_var.set("100%")
                        continue_btn.config(state="normal")
                        print("Progress window: Upload done, Continue enabled")  # Debug
                        return  # Stop polling
                    elif tag == "error":
                        _, error_msg, _, _ = item
                        pbar.stop()
                        status_var.set(f"Error: {error_msg}")
                        continue_btn.config(state="normal")
                        print(f"Progress window: Error occurred, Continue enabled")  # Debug
                        return  # Stop polling
            except queue.Empty:
                pass

            # Keep polling
            if progress_win.winfo_exists():
                progress_win.after(100, poll)

        # start polling after a small delay to ensure window is visible
        progress_win.after(50, poll)


    def _finish_after_upload(self, progress_win: tk.Toplevel) -> None:
        try:
            progress_win.destroy()
        finally:
            # after upload completes, show the updater window
            print("Opening updater window...")  # Debug
            updater = Updater(self, on_finish=self._on_updater_finish, uploaded_path=self.upload_destination)
            updater.show_window()

            # run the actual updates for GIT
            updater.run_updates()

    def _on_updater_finish(self) -> None:
        """Called when the Updater Finish button is clicked."""
        print("Updater finished - closing app")  # Debug
        self.destroy()

    def _on_cancel(self) -> None:
        # close the window
        self.destroy()


def main(icon_path: Optional[str] = None, taskbar_icon_path: Optional[str] = None) -> None:
    app = PackageUploaderApp(icon_path=icon_path, taskbar_icon_path=taskbar_icon_path)
    app.mainloop()


if __name__ == "__main__":
    main()
