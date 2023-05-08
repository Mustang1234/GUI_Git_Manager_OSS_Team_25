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



#git here

def git_init():
    repo_dir = askopendirname()
    subprocess.run(['git', 'init', repo_dir])

def git_add():
    #해당 깃레포(디렉토리)를 선택하면 전체 수정파일을 staging area로 올려줌.
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    result = subprocess.run(['git', 'add', '.'])
    
    #추후에 메세지 박스 대신 root에서 띄우도록 수정
    if result.returncode == 0:
        messagebox.showinfo("Success", "git add successfully executed!")
    else:
        messagebox.showerror("Error", "git add failed.")
    
    """
    #클릭해서 add하는 경우
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    subprocess.run(['git', 'add', repo_dir])
    """
    
    """
    #입력받아서 add하는 경우
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    msg = tk.simpledialog.askstring("add", "file name: ")
    subprocess.run(['git', 'add', msg])
    """
    
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
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    msg = tk.simpledialog.askstring("commit", "commit message: ") #커밋메세지 입력
    """
    #입력받은 커밋 메세지 보여주기
    if msg:
        messagebox.showinfo("committed", f"Ok to commit: {msg}")
    """
    result = subprocess.run(['git', 'commit', '-m', msg])
    
    #추후에 메세지 박스 대신 root에서 띄우도록 수정
    if result.returncode == 0:
        messagebox.showinfo("Success", "git commit successfully executed!")
    else:
        messagebox.showerror("Error", "git comiit failed.")

def git_status():
    repo_dir = askopendirname()
    os.chdir(repo_dir)
    result = subprocess.run(['git', 'status'], capture_output=True, text=True)
    
    #result를 화면창에 띄우기. 추후에 git_status_f 이용해서 좀 더 깔끔하게 파일 상태 보여주기
    status_root = tk.Tk()
    status_root.title("Git Status")
    
    text_box = ScrolledText(status_root)
    text_box.pack(expand=True, fill='both')
    text_box.insert('end', result.stdout)
    
    status_root.mainloop()
    
    
def git_status_f(): #나중에 버튼 합쳐서 상태에 따라서 알아서 restore, restore --staged 구분해주는 기능 구현한다면 필요한 함수
    # git status --porcelain : 파일의 상태 확인
    filepath = askopendirname()
    result = subprocess.run(['git', 'status', '--porcelain', filepath], capture_output=True, text=True)
    output = result.stdout.strip()

    if not output:
        return 'unmodified'
    elif output.startswith('M'):
        return 'modified'
    elif output.startswith('A'):
        return 'staged'
    elif output.startswith('??'):
        return 'untracked'



"""
#기존의 기본 윈도우 파일탐색기 부분 삭제
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
#ttk.Button(root, text="Git status", command=git_status_f).grid(             row=9, column=1, padx=4, pady=4, sticky='ew')

root.mainloop()