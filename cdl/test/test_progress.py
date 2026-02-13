"""Quick test to verify progress window appears"""
import tkinter as tk
from tkinter import ttk
import time
import threading
import queue


def test_progress_window():
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("400x200")

    def show_progress():
        # Hide main window
        root.withdraw()

        # Create progress window
        progress_win = tk.Toplevel(root)
        progress_win.title("Test Progress")
        progress_win.geometry("500x150")
        progress_win.resizable(False, False)
        progress_win.lift()
        progress_win.focus_force()

        container = tk.Frame(progress_win, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        status_var = tk.StringVar(value="Working...")
        tk.Label(container, textvariable=status_var, font=("Segoe UI", 10)).pack(fill="x")

        pbar = ttk.Progressbar(container, mode="determinate", length=450)
        pbar.pack(fill="x", pady=(8, 8))
        pbar["maximum"] = 100

        percent_var = tk.StringVar(value="0%")
        tk.Label(container, textvariable=percent_var, font=("Segoe UI", 9)).pack(fill="x")

        btn_frame = tk.Frame(container)
        btn_frame.pack(fill="x", pady=(12, 0))
        continue_btn = tk.Button(btn_frame, text="Continue", state="disabled", width=12,
                                command=lambda: finish(progress_win))
        continue_btn.pack(side="right")

        # Simulate work
        prog_queue = queue.Queue()

        def worker():
            for i in range(101):
                time.sleep(0.05)
                prog_queue.put(("progress", i))
            prog_queue.put(("done",))

        def poll():
            try:
                while True:
                    item = prog_queue.get_nowait()
                    if item[0] == "progress":
                        val = item[1]
                        pbar["value"] = val
                        percent_var.set(f"{val}%")
                        status_var.set(f"Working... {val}%")
                    elif item[0] == "done":
                        status_var.set("Complete!")
                        percent_var.set("100%")
                        continue_btn.config(state="normal")
                        print("Done - Continue enabled")
                        return
            except queue.Empty:
                pass

            if progress_win.winfo_exists():
                progress_win.after(50, poll)

        threading.Thread(target=worker, daemon=True).start()
        progress_win.after(50, poll)

    def finish(win):
        win.destroy()
        root.destroy()

    btn = tk.Button(root, text="Start Test", command=show_progress, width=20)
    btn.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    test_progress_window()

