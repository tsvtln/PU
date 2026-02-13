import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
from typing import Optional, Callable
from bin.global_vars import GlobalVars
from bin.helpers import SaveCheckSums
from bin.helpers import GitWorker
from bin.helpers import FileUpdater

class Updater:
    """
    Updater class that performs post-upload operations and displays output in a GUI window.
    """

    def __init__(self, parent: tk.Tk, on_finish: Optional[Callable[[], None]] = None, uploaded_path: Optional[str] = None) -> None:
        """
        Initialize the Updater.

        Args:
            parent: Parent Tk window
            on_finish: Callback to execute when Finish button is clicked
            uploaded_path: Path where files were uploaded (for checksum calculation)
        """
        self.parent = parent
        self.on_finish = on_finish
        self.uploaded_path = uploaded_path
        self.window: Optional[tk.Toplevel] = None
        self.output_text: Optional[scrolledtext.ScrolledText] = None
        self.finish_btn: Optional[tk.Button] = None

    def _lib_dir(self) -> str:
        """Get the lib directory path."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        proj_root = os.path.dirname(script_dir)
        return os.path.join(proj_root, "lib")

    def show_window(self) -> None:
        """Create and show the updater window."""
        print("Creating updater window")  # Debug

        # create window
        self.window = tk.Toplevel(self.parent)
        self.window.title("Package Updater - Processing")
        self.window.geometry("700x500")
        self.window.resizable(True, True)

        # set icon
        try:
            lib_ico = os.path.join(self._lib_dir(), "app.ico")
            if os.path.isfile(lib_ico):
                self.window.iconbitmap(lib_ico)
        except Exception:
            pass

        # make sure window appears on top
        self.window.lift()
        self.window.focus_force()
        self.window.attributes('-topmost', True)
        self.window.after(100, lambda: self.window.attributes('-topmost', False))

        # handle window close button (X)
        def on_close():
            if messagebox.askyesno("Close", "Are you sure you want to close?"):
                self._on_finish_click()

        self.window.protocol("WM_DELETE_WINDOW", on_close)

        # UI elements
        container = tk.Frame(self.window, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        # header
        header = tk.Label(
            container,
            text="Processing updates...",
            font=("Segoe UI", 12, "bold")
        )
        header.pack(anchor="w", pady=(0, 8))

        # output text area with scrollbar
        output_frame = tk.Frame(container)
        output_frame.pack(fill="both", expand=True)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Consolas", 9),
            state="normal"  # Keep as normal to allow selection and copying
        )
        self.output_text.pack(fill="both", expand=True)

        # Make text read-only by binding key events (but allow Ctrl+C, Ctrl+A, selection)
        def make_readonly(event):
            # Allow Ctrl+C (copy), Ctrl+A (select all), arrow keys, and mouse selection
            if event.keysym in ('c', 'a', 'C', 'A') and (event.state & 0x4):  # Ctrl key pressed
                return
            if event.keysym in ('Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Prior', 'Next'):
                return
            # Block all other key presses
            return "break"

        self.output_text.bind("<Key>", make_readonly)

        # Add right-click context menu
        context_menu = tk.Menu(self.output_text, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: self.output_text.event_generate("<<Copy>>"))
        context_menu.add_command(label="Select All", command=lambda: self.output_text.tag_add("sel", "1.0", "end"))

        def show_context_menu(event):
            context_menu.post(event.x_root, event.y_root)

        self.output_text.bind("<Button-3>", show_context_menu)  # Right-click

        # button frame
        btn_frame = tk.Frame(container)
        btn_frame.pack(fill="x", pady=(12, 0))

        self.finish_btn = tk.Button(
            btn_frame,
            text="Finish",
            state="disabled",
            width=12,
            command=self._on_finish_click
        )
        self.finish_btn.pack(side="right")

        print("Updater window created")  # Debug

    def print(self, message: str) -> None:
        """
        Print a message to the output window.

        Args:
            message: The message to display
        """
        if self.output_text and self.window and self.window.winfo_exists():
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)  # Auto-scroll to bottom
            self.window.update_idletasks()  # Force UI update

    def enable_finish_button(self) -> None:
        """Enable the Finish button (call this when your logic is complete)."""
        if self.finish_btn:
            self.finish_btn.config(state="normal")
            print("Updater: Finish button enabled")  # Debug

    def _on_finish_click(self) -> None:
        """Handle Finish button click."""
        if self.window:
            self.window.destroy()
        if self.on_finish:
            self.on_finish()

    def run_updates(self) -> None:
        """
        Main method to run your update logic.
        Override this method or call it with your custom logic.

        Example usage:
            updater = Updater(parent, uploaded_path=dest_dir)
            updater.show_window()
            updater.run_updates()
        """
        self.print("=" * 50)
        self.print("Starting update process...")
        self.print("=" * 50)

        # Calculate checksums from the uploaded files
        self.print("Getting checksum of file...")

        # Use the uploaded path if provided, otherwise use the default
        if self.uploaded_path:
            original_path = GlobalVars.uipath_fileshare_path
            GlobalVars.uipath_fileshare_path = self.uploaded_path
            self.print(f"Calculating checksum from: {self.uploaded_path}")
        else:
            original_path = None
            self.print(f"Calculating checksum from: {GlobalVars.uipath_fileshare_path}")

        try:
            init_checksum_calc = SaveCheckSums()
            checksum_scanned = init_checksum_calc.save_checksums()
            for i in checksum_scanned:
                self.print(i)
            self.print("=" * 50)
        finally:
            # Restore original path if we changed it
            if original_path:
                GlobalVars.uipath_fileshare_path = original_path

        GitWorker()
        cloning_repo = GitWorker.update_from_repo()
        self.print(cloning_repo)
        self.print("=" * 50)

        self.print("\nUpdating checksum in chocolateyInstall.ps1...")
        updated_checksums = FileUpdater.update_ps()
        for i in updated_checksums:
            self.print(i)
            self.print('\n')
        self.print("=" * 50)

        self.print("\nUpdating nuspec file...")
        FileUpdater.update_nuspec()
        self.print(f"Version in nuspec updated to {GlobalVars.uipath_version}")
        self.print("=" * 50)

        self.print("\nCreating a pull request...")
        GitWorker.create_and_push_branch()
        pr_url = GitWorker.create_pull_request()
        self.print("=" * 50)

        if pr_url:
            self.print(f"\nCopy the following link and send it to an automations team member for approval:\n{GlobalVars.pull_request_url}")

        # enable the finish button:
        self.enable_finish_button()


# example usage (for testing):
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # hide the root window

    def on_finish():
        print("Finish clicked - closing app")
        root.destroy()

    updater = Updater(root, on_finish=on_finish)
    updater.show_window()

    # simulate some work
    updater.print("Testing updater window...")
    updater.print("This is a test message")
    updater.print("Another line of output")

    # enable finish after 2 seconds (for demo)
    root.after(2000, updater.enable_finish_button)

    root.mainloop()

