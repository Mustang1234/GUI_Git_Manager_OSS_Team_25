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
import subprocess
import os
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

#from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename, askopenpathnames
from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename
from tkinter import messagebox

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

import filebrowser
root = tk.Tk()

style = ttk.Style(root)
style.theme_use("clam")
root.configure(bg=style.lookup('TFrame', 'background'))

def c_open_file():
    rep = filebrowser.FileBrowser(parent=root, initialdir='/', initialfile='tmp',
                           filetypes=[("All files", "*"), ("Pictures", "*.png|*.jpg|*.JPG")])
    # rep = askopenfilenames(parent=root, initialdir='/', initialfile='tmp',
    #                        filetypes=[("Pictures", "*.png|*.jpg|*.JPG"),
    #                                   ("All files", "*")])
    print(rep)



ttk.Button(root, text="Open file Browser", command=c_open_file).grid(              row=1, column=0, padx=4, pady=4, sticky='ew')

root.mainloop()