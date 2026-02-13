import os
import sys
import time
import threading
import pyautogui
import pygetwindow as gw  # Added for robust window handling
import tkinter as tk
from tkinter import ttk


class AppLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Application Launcher")
        self.root.iconbitmap(self.resource_path("app.ico"))
        self.root.configure(background='blue')
        self.root.minsize(300, 200)
        self.root.geometry("300x200+50+50")
        self.root.attributes('-topmost', True)  # Ensure window is always on top
        self.starting_label = tk.Label(self.root, text='', bg='blue', fg='white')
        self.setup_ui()

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)

    def start_apps(self):
        threading.Thread(target=self.run_app_startup, daemon=True).start()

    def run_app_startup(self):
        def minimize(window_name, sleep):
            time.sleep(sleep)
            windows = gw.getWindowsWithTitle(window_name)
            if windows:
                win = windows[0]
                if hasattr(win, 'isMinimized') and win.isMinimized:
                    win.restore()
                    time.sleep(0.5)
                win.activate()
                time.sleep(0.5)
                pyautogui.hotkey('winleft', 'down')

        progress_bar = ttk.Progressbar()
        progress_bar.place(x=50, y=140, width=200)
        progress_label = tk.Label(self.root, text='0%', bg='blue', fg='white')
        progress_label.place(x=130, y=170)

        progress_bar_step = 0
        apps = [
            'Notepad++',
            'Accodis mail',
            'Outlook',
            'Chrome',
            'PyCharm',
            'Keepass',
            'Delinea Connection Manager',
            'jiggler',
        ]
        default_path = [
            'Notepad++',
        ]

        apps_to_kill = [
            'OneDrive',
        ]

        failed_apps = []

        self.root.after(0, lambda *args: self.starting_label.pack())

        for ap in apps:
            self.root.after(0, lambda *args, ap=ap: self.starting_label.config(text=f'Starting {ap}...'))
            progress_bar_step += 100 / (len(apps) + len(apps_to_kill))
            self.root.after(0, lambda *args, v=progress_bar_step: progress_bar.config(value=v))
            percent = int(progress_bar_step)
            self.root.after(0, lambda *args, percent=percent: progress_label.config(text=f'{percent}%'))
            self.root.after(0, lambda *args: self.root.update_idletasks())
            try:
                if ap in default_path:
                    os.startfile(f"C:\\Program Files\\{ap}\\{ap}.exe")
                    minimize(ap, 3)
                elif ap == 'Chrome':
                    os.startfile(f"C:\\Program Files\\Google\\{ap}\\Application\\{ap}.exe")
                    minimize(ap, 3)
                elif ap == 'Outlook':
                    os.startfile(f"C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE")
                    minimize('Inbox - Tsvetelin.Maslarski-ext@ldc.com - Outlook', 5)
                elif ap == 'Accodis mail':
                    os.system(
                        'start shell:AppsFolder\\'
                        'microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.mail')
                    minimize('Mail - MASLARSKI Tsvetelin - Outlook', 5)
                elif ap == 'jiggler':
                    os.startfile("C:\\Users\\maslat-ext\\OneDrive - Louis Dreyfus Company\\Pictures\\Camera Roll"
                                 "\\mouse-jiggler-2-0-25\\MouseJiggler-portable\\MouseJiggler.exe")
                    time.sleep(2)
                elif ap == 'Keepass':
                    os.startfile("C:\\Program Files\\KeePass Password Safe 2\\KeePass.exe")
                    time.sleep(3)
                    pyautogui.write('')
                    pyautogui.press('enter')
                    minimize(ap, 3)
                elif ap == 'Delinea Connection Manager':
                    apname = ap.split(' ')
                    os.startfile(f"""C:\\Program Files\\{apname[0]}\\{ap}\\{ap.split(' ', 1)[0]
                                                                            + '.' + ap.split(' ',1)[1].
                                 replace(' ', '')}.exe""")
                    minimize(ap, 15)
                elif ap == 'PyCharm':
                    os.startfile("C:\\Users\\maslat-ext\\AppData\\Local\\JetBrains\\PyCharm 2024.3.4\\bin\\pycharm64.exe")
                    minimize('PyCharm', 7)
            except Exception as e:
                self.root.after(0, lambda *args, ap=ap: self.starting_label.config(text=f'Error starting {ap}'))
                failed_apps.append(ap)
                self.root.after(0, lambda *args: self.root.update_idletasks())
                time.sleep(2)

        for atk in apps_to_kill:
            print('started killing')
            self.root.after(0, lambda *args, atk=atk: self.starting_label.config(text=f'Closing {atk} if running...'))
            progress_bar_step += 100 / (len(apps) + len(apps_to_kill))
            self.root.after(0, lambda *args, v=progress_bar_step: progress_bar.config(value=v))
            percent = int(progress_bar_step)
            self.root.after(0, lambda *args, percent=percent: progress_label.config(text=f'{percent}%'))
            self.root.after(0, lambda *args: self.root.update_idletasks())
            try:
                os.system(f'taskkill /f /im {atk}.exe')
            except Exception as e:
                continue
            time.sleep(1)

            time.sleep(4)
            self.root.after(0, lambda *args: progress_bar.destroy())
            self.root.after(0, lambda *args: progress_label.destroy())
            if not failed_apps:
                self.root.after(0, lambda *args: self.starting_label.config(text='All applications started successfully!'))
            elif len(failed_apps) == len(apps):
                self.root.after(0, lambda *args: self.starting_label.config(text='Failed to start:\n' + '\n'.join(failed_apps)))

    def setup_ui(self):
        tk.Label(self.root, text="Welcome to the App Launcher v1.0.0", bg='blue', fg='white').pack(pady=20)
        launch_button = tk.Button(self.root, text="Start Applications", command=self.start_apps)
        launch_button.pack(pady=10)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AppLauncher()
    app.run()