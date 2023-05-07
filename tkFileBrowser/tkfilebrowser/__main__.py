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

#from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename, askopenpathnames
from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

root = tk.Tk()

style = ttk.Style(root)
style.theme_use("clam")
root.configure(bg=style.lookup('TFrame', 'background'))

"""
def c_open_file_old():
    rep = filedialog.askopenfilenames(parent=root, initialdir='/', initialfile='tmp',
                                      filetypes=[("PNG", "*.png"),
                                                 ("JPEG", "*.jpg"),
                                                 ("All files", "*")])
    print(rep)


def c_open_dir_old():
    rep = filedialog.askdirectory(parent=root, initialdir='/tmp')
    print(rep)


def c_save_old():
    rep = filedialog.asksaveasfilename(parent=root, defaultextension=".png",
                                       initialdir='/tmp', initialfile='image.png',
                                       filetypes=[("PNG", "*.png"),
                                                  ("JPEG", "*.jpg"),
                                                  ("Text files", "*.txt"),
                                                  ("All files", "*")])
    print(rep)
"""

def c_open_file():
    rep = askopenfilenames(parent=root, initialdir='/', initialfile='tmp',
                           filetypes=[("Pictures", "*.png|*.jpg|*.JPG"),
                                      ("All files", "*")])
    print(rep)


def c_open_dir():
    rep = askopendirname(parent=root, initialdir='/', initialfile='tmp')
    print(rep)


def c_save():
    rep = asksaveasfilename(parent=root, defaultext=".png", initialdir='/tmp', initialfile='image.png',
                            filetypes=[("Pictures", "*.png|*.jpg|*.JPG"),
                                       ("Text files", "*.txt"),
                                       ("All files", "*")])
    print(rep)


def c_path():
    rep = askopendirname(parent=root, initialdir='/', initialfile='tmp')
    print(rep)


def git_init():
    rep = askopendirname(parent=root, initialdir='/', initialfile='tmp')
    rep = subprocess.run(['git', 'init', rep]).args[2]
    print(root,rep)
    rep = askopendirname(parent=root, initialdir=rep, initialfile='tmp')
    print(rep)



    """
fdsafdsa
['git', 'init', 'C:\\Users\\32gur\\Desktop\\hi\\3-1\\OSS\\과제\\ufggchhgcjhg']
<class 'list'>
['git', 'init', 'C:\\Users\\32gur\\Desktop\\hi\\3-1\\OSS\\과제\\ufggchhgcjhg']
<class 'str'>



    rep = rep.stdout.splitlines()
    print(rep)
    print(rep[rep.index('C'):rep.index('.git')])
    print(rep)
    rep = askopendirname(parent=root, initialdir = rep, initialfile='tmp')
    print(rep)"""
    """
    returned_value = 
    Initialized empty Git repository in C:/Users/32gur/Desktop/hi/3-1/OSS/과제/.git/CompletedProcess(args=['git', 'init', 'C:\\Users\\32gur\\Desktop\\hi\\3-1\\OSS\\과제'], returncode=0)
    Initialized empty Git repository in C:/Users/32gur/Desktop/hi/3-1/OSS/과제/rewq/.git/
    CompletedProcess(args=['git', 'init', 'C:\\Users\\32gur\\Desktop\\hi\\3-1\\OSS\\과제\\rewq'], returncode=0)
    """

def git_add():
    repo_dir = askopendirname()
    subprocess.run(['git', 'add', repo_dir])
    

def git_restored():
    #operation
    pass

def git_restore_s():
    #operation
    pass

def git_rm():
    #operation
    pass

def git_rm_c():
    #operation
    pass

def git_mv():
    #operation
    pass

def git_commit():
    #operation
    pass

def git_status():
    #operation
    pass

def get_file_status(filepath):
    # `git status --porcelain` 명령어로 파일의 상태를 체크합니다.
    result = subprocess.run(['git', 'status', '--porcelain', filepath], capture_output=True, text=True)
    output = result.stdout.strip()
     # 출력된 결과에 따라 파일의 상태를 결정합니다.
    if not output:
        return 'unmodified'
    elif output.startswith('M'):
        return 'modified'
    elif output.startswith('A'):
        return 'staged'
    elif output.startswith('??'):
        return 'untracked'



"""
ttk.Label(root, text='Default dialogs').grid(                               row=0, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Open files", command=c_open_file_old).grid(          row=1, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Open folder", command=c_open_dir_old).grid(          row=2, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Save file", command=c_save_old).grid(                row=3, column=0, padx=4, pady=4, sticky='ew')
"""

ttk.Label(root, text='tkfilebrowser dialogs').grid(                         row=0, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Open files", command=c_open_file).grid(              row=1, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Open folder", command=c_open_dir).grid(              row=2, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Save file", command=c_save).grid(                    row=3, column=0, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Open paths", command=c_path).grid(                   row=4, column=0, padx=4, pady=4, sticky='ew')

ttk.Label(root, text='Git opperations').grid(                               row=0, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git init", command=git_init).grid(                   row=1, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git add", command=git_add).grid(                     row=2, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git restored", command=git_restored).grid(           row=3, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git restore --stage", command=git_restore_s).grid(   row=4, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git rm", command=git_rm).grid(                       row=5, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git rm --cached", command=git_rm_c).grid(            row=6, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git mv", command=git_mv).grid(                       row=7, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git commit", command=git_commit).grid(               row=8, column=1, padx=4, pady=4, sticky='ew')
ttk.Button(root, text="Git status", command=git_status).grid(               row=9, column=1, padx=4, pady=4, sticky='ew')

root.mainloop()