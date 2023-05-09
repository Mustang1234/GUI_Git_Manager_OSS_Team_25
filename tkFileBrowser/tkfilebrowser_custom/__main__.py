# -*- coding: utf-8 -*-
"""
tkfilebrowser - Alternative to filedialog for Tkinter
Copyright 2017 Juliette Monsel <j_4321@protonmail.com>

tkfilebrowser is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

tkfilebrowser is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Example
"""
#
"""
import subprocess
import os
#from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename, askopenpathnames
from functions_custom import askopendirname, askopenfilenames, asksaveasfilename
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
"""
import os
import subprocess
from functions_custom import askopendirname, askopenfilenames, asksaveasfilename
from tkinter.scrolledtext import ScrolledText

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

import filebrowser_custom
root = tk.Tk()

style = ttk.Style(root)
style.theme_use("clam")
root.configure(bg=style.lookup('TFrame', 'background'))

def c_open_file():
    rep = filebrowser_custom.FileBrowser(parent=root, initialdir='/', initialfile='tmp',
                           filetypes=[("All files", "*"), ("Pictures", "*.png|*.jpg|*.JPG")])
    # rep = askopenfilenames(parent=root, initialdir='/', initialfile='tmp',
    #                        filetypes=[("Pictures", "*.png|*.jpg|*.JPG"),
    #                                   ("All files", "*")])
    print(rep)


#git add가 잘 되었는지 test를 위해서
def git_status():
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    result = subprocess.run(['git', 'status'], capture_output=True, text=True)
    
    status_root = tk.Tk()
    status_root.title("Git Status")
    
    text_box = ScrolledText(status_root)
    text_box.pack(expand=True, fill='both')
    text_box.insert('end', result.stdout)
    
    status_root.mainloop()

ttk.Button(root, text="Open file Browser", command=c_open_file).grid(              row=1, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git status", command=git_status).grid(               row=9, column=1, padx=4, pady=4, sticky='ew')

root.mainloop()