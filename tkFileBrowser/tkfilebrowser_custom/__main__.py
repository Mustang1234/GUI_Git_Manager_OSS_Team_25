try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

import filebrowser_custom
import os


root = tk.Tk()
style = ttk.Style(root)
style.theme_use("clam")
root.configure(bg=style.lookup('TFrame', 'background'))
ttk.Button(root, text="GIT FOR GUI",
            command=lambda: filebrowser_custom.FileBrowser(parent=root, initialdir='/', initialfile='tmp',
                           filetypes=[("All files", "*"), ("Pictures", "*.png|*.jpg|*.JPG")])
                           ).grid(row=1, column=0, padx=120, pady=60, sticky='ew')


root.mainloop()