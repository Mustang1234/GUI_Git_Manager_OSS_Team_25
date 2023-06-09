# -*- coding: utf-8 -*-
"""
tkfilebrowser - Alternative to filedialog for Tkinter
Copyright 2017-2018 Juliette Monsel <j_4321@protonmail.com>

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


Main class
"""
import os
import tkinter as tk
import tkinter.simpledialog as simpledialog
from tkinter import messagebox
import subprocess
import tkfilebrowser


import psutil
from re import search
from subprocess import check_output
from os import walk, mkdir, stat, access, W_OK, listdir
from os import name as OSNAME
from os.path import sep as SEP
from os.path import exists, join, getmtime, realpath, split, expanduser, \
    abspath, isabs, splitext, dirname, getsize, isdir, isfile, islink
try:
    from os import scandir
    SCANDIR = True
except ImportError:
    SCANDIR = False
import traceback
import constants_custom as cst
from constants_custom import unquote, tk, ttk, key_sort_files, \
    get_modification_date, display_modification_date, display_size
from autoscrollbar_custom import AutoScrollbar
from path_button_custom import PathButton
from tooltip_custom import TooltipTreeWrapper
from recent_files_custom import RecentFiles
import configparser


if OSNAME == 'nt':
    from win32com.shell import shell, shellcon

_ = cst._


class Stats:
    """Fake stats class to create dummy stats for broken links."""
    def __init__(self, **kwargs):
        self._prop = kwargs

    def __getattr__(self, attr):
        if attr not in self._prop:
            raise AttributeError("Stats has no attribute %s." % attr)
        else:
            return self._prop[attr]


class FileBrowser(tk.Toplevel):
    """Filebrowser dialog class."""
    def __init__(self, parent, initialdir="", initialfile="", mode="openfile",
                 multiple_selection=False, defaultext="", title="Filebrowser",
                 filetypes=[], okbuttontext=None, cancelbuttontext=_("Cancel"),
                 foldercreation=True, **kw):
        """
        Create a filebrowser dialog.

        Arguments:

        parent : Tk or Toplevel instance
            parent window

        title : str
            the title of the filebrowser window

        initialdir : str
            directory whose content is initially displayed

        initialfile : str
            initially selected item (just the name, not the full path)

        mode : str
            kind of dialog: "openpath", "openfile", "opendir" or "save"

        multiple_selection : bool
            whether to allow multiple items selection (open modes only)

        defaultext : str (e.g. '.png')
            extension added to filename if none is given (default is none)

        filetypes : list :obj:`[("name", "*.ext1|*.ext2|.."), ...]`
          only the files of given filetype will be displayed,
          e.g. to allow the user to switch between displaying only PNG or JPG
          pictures or dispalying all files:
          :obj:`filtypes=[("Pictures", "\*.png|\*.PNG|\*.jpg|\*.JPG'), ("All files", "\*")]`

        okbuttontext : str
            text displayed on the validate button, default is "Open".

        cancelbuttontext : str
            text displayed on the button that cancels the selection, default is "Cancel".

        foldercreation : bool
            enable the user to create new folders if True (default)
        """
        # compatibility with tkinter.filedialog arguments: the parent window is called 'master'
        self.parent = parent
        if 'master' in kw and parent is None:
            parent = kw.pop('master')
        if 'defaultextension' in kw and not defaultext:
            defaultext = kw.pop('defaultextension')
        tk.Toplevel.__init__(self, parent, **kw)

        # python version compatibility
        if SCANDIR:
            self.display_folder = self._display_folder_scandir
        else:
            self.display_folder = self._display_folder_walk

        # keep track of folders to be able to move backward/foreward in history
        if initialdir:
            self.history = [initialdir]
        else:
            self.history = [expanduser("~")]
        self._hist_index = -1

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title(title)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.mode = mode
        self.result = ""
        self.foldercreation = foldercreation

        self.git_addcreation = False
        self.git_commitcreation = False
        self.git_restorecreation = False
        self.git_restore_screation = False
        self.git_rmcreation = False
        self.git_rm_cachedcreation = False
        self._git_rename_wrappercreation = False

        # hidden files/folders visibility
        self.hide = False
        # hidden items
        self.hidden = ()

        # ---  style
        style = ttk.Style(self)
        bg = style.lookup("TFrame", "background")
        style.layout("right.tkfilebrowser.Treeview.Item",
                     [('Treeitem.padding',
                       {'children':
                           [('Treeitem.image', {'side': 'left', 'sticky': ''}),
                            ('Treeitem.focus',
                             {'children':
                                 [('Treeitem.text',
                                   {'side': 'left', 'sticky': ''})],
                              'side': 'left',
                              'sticky': ''})],
                        'sticky': 'nswe'})])
        style.layout("left.tkfilebrowser.Treeview.Item",
                     [('Treeitem.padding',
                       {'children':
                           [('Treeitem.image', {'side': 'left', 'sticky': ''}),
                            ('Treeitem.focus',
                             {'children':
                                 [('Treeitem.text', {'side': 'left', 'sticky': ''})],
                              'side': 'left',
                              'sticky': ''})],
                        'sticky': 'nswe'})])
        style.configure("right.tkfilebrowser.Treeview", font="TkDefaultFont")
        style.configure("right.tkfilebrowser.Treeview.Item", padding=2)
        style.configure("right.tkfilebrowser.Treeview.Heading",
                        font="TkDefaultFont")
        style.configure("left.tkfilebrowser.Treeview.Heading",
                        font="TkDefaultFont")
        style.configure("left.tkfilebrowser.Treeview.Item", padding=2)
        style.configure("listbox.tkfilebrowser.TFrame", background="white", relief="sunken")
        field_bg = style.lookup("TEntry", "fieldbackground", default='white')
        tree_field_bg = style.lookup("ttk.Treeview", "fieldbackground",
                                     default='white')
        fg = style.lookup('TLabel', 'foreground', default='black')
        active_bg = style.lookup('TButton', 'background', ('active',))
        sel_bg = style.lookup('Treeview', 'background', ('selected',))
        sel_fg = style.lookup('Treeview', 'foreground', ('selected',))
        self.option_add('*TCombobox*Listbox.selectBackground', sel_bg)
        self.option_add('*TCombobox*Listbox.selectForeground', sel_fg)
        style.map('types.tkfilebrowser.TCombobox', foreground=[], fieldbackground=[])
        style.configure('types.tkfilebrowser.TCombobox', lightcolor=bg,
                        fieldbackground=bg)
        style.configure('types.tkfilebrowser.TCombobox.Item', background='red')
        style.configure("left.tkfilebrowser.Treeview", background=active_bg,
                        font="TkDefaultFont",
                        fieldbackground=active_bg)
        self.configure(background=bg)
        # path button style
        style.configure("path.tkfilebrowser.TButton", padding=2)
        selected_bg = style.lookup("TButton", "background", ("pressed",))
        map_bg = style.map("TButton", "background")
        map_bg.append(("selected", selected_bg))
        style.map("path.tkfilebrowser.TButton",
                  background=map_bg,
                  font=[("selected", "TkDefaultFont 9 bold")])
        # tooltip style
        style.configure('tooltip.tkfilebrowser.TLabel', background='black',
                        foreground='white')

        # ---  images
        self.im_file = cst.PhotoImage(file=cst.IM_FILE, master=self)
        self.im_folder = cst.PhotoImage(file=cst.IM_FOLDER, master=self)
        self.im_desktop = cst.PhotoImage(file=cst.IM_DESKTOP, master=self)
        self.im_file_link = cst.PhotoImage(file=cst.IM_FILE_LINK, master=self)
        self.im_link_broken = cst.PhotoImage(file=cst.IM_LINK_BROKEN, master=self)
        self.im_folder_link = cst.PhotoImage(file=cst.IM_FOLDER_LINK, master=self)
        self.im_new = cst.PhotoImage(file=cst.IM_NEW, master=self)
        self.im_drive = cst.PhotoImage(file=cst.IM_DRIVE, master=self)
        self.im_home = cst.PhotoImage(file=cst.IM_HOME, master=self)
        self.im_recent = cst.PhotoImage(file=cst.IM_RECENT, master=self)
        self.im_recent_24 = cst.PhotoImage(file=cst.IM_RECENT_24, master=self)
        self.git_status_update = cst.PhotoImage(file=cst.GIT_STATUS_UPDATE, master=self)

        # ---  recent files
        self._recent_files = RecentFiles(cst.RECENT_FILES, 30)

        # ---  path completion
        self.complete = self.register(self._completion)
        self.listbox_var = tk.StringVar(self)
        self.listbox_frame = ttk.Frame(self, style="listbox.tkfilebrowser.TFrame", borderwidth=1)
        self.listbox = tk.Listbox(self.listbox_frame,
                                  listvariable=self.listbox_var,
                                  highlightthickness=0,
                                  borderwidth=0,
                                  background=field_bg,
                                  foreground=fg,
                                  selectforeground=sel_fg,
                                  selectbackground=sel_bg)
        self.listbox.pack(expand=True, fill="x")

        # ---  path bar
        self.path_var = tk.StringVar(self)
        self.frame_bar = ttk.Frame(self)
        self.frame_bar.columnconfigure(0, weight=1)
        self.frame_bar.grid(row=1, sticky="ew", pady=3, padx=10)
        self.frame_recent = ttk.Frame(self.frame_bar)
        self.frame_recent.grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(self.frame_recent, image=self.im_recent_24).pack(side="left")
        ttk.Label(self.frame_recent, text=_("Recently used"),
                  font="TkDefaultFont 9 bold").pack(side="left", padx=4)
        self.path_bar = ttk.Frame(self.frame_bar)
        self.path_bar.grid(row=0, column=0, sticky="ew")
        self.path_bar_buttons = []
        self.b_new_folder = ttk.Button(self.frame_bar, image=self.im_new,
                                       command=self.create_folder)
        self.b_update_status = ttk.Button(self.frame_bar, image=self.git_status_update,
                                       command=self.update_status)
        self.frame_buttons1 = ttk.Frame(self)
        self.frame_buttons1.grid(row=3, sticky="ew", pady=3, padx=10)
        self.frame_buttons2 = ttk.Frame(self)
        self.frame_buttons2.grid(row=4, sticky="ew", pady=3, padx=10)
        self.b_branch = ttk.Button(self.frame_buttons1, text="Branch",
                                       command=self.branch_function)
        self.b_branch_list=[]
        self.l_branch_head = ttk.Label(self.frame_buttons1, text="Hi *^v^*")
        self.b_log = ttk.Button(self.frame_buttons1, text="Log",
                                       command=self.log)
        self.b_clone = ttk.Button(self.frame_buttons2, text="Clone",
                                       command=self.clone)
        self.b_quit = ttk.Button(self.frame_buttons2, text=cancelbuttontext,
                                       command=self.quit).pack(side="right", padx=(4,0))
        self.b_git_init = ttk.Button(self.frame_buttons2, text="git init",
                                       command=self.git_init)
        self.b_git_add = ttk.Button(self.frame_buttons2, text="git add",
                                       command=self.git_add)
        self.b_git_commit = ttk.Button(self.frame_buttons2, text="git commit",
                                       command=self.git_commit)
        self.b_git_restore = ttk.Button(self.frame_buttons2, text="git restore",
                                       command=self.git_restore)
        self.b_git_restore_s = ttk.Button(self.frame_buttons2, text="git restore --staged",
                                       command=self.git_restore_s)
        self.b_git_mv = ttk.Button(self.frame_buttons2, text="git mv",
                                       command=self.git_rename)
        self.b_git_rm = ttk.Button(self.frame_buttons2, text="git rm",
                                       command=self.git_rm)
        self.b_git_rm_cached = ttk.Button(self.frame_buttons2, text="git rm --cached",
                                       command=self.git_rm_cached)
        self.b_git_rename_wrapper = ttk.Button(self.frame_buttons2, text="git mv",
                                       command=self._git_rename_wrapper)
        
        if self.foldercreation:
            self.b_new_folder.grid(row=0, column=2, sticky="e")

        self.b_update_status.grid(row=0, column=1, sticky="e")
        if mode == "save":
            ttk.Label(self.path_bar, text=_("Folder: ")).grid(row=0, column=0)
            self.defaultext = defaultext

            frame_name = ttk.Frame(self)
            frame_name.grid(row=0, pady=(10, 0), padx=10, sticky="ew")
            ttk.Label(frame_name, text=_("Name: ")).pack(side="left")
            self.entry = ttk.Entry(frame_name, validate="key",
                                   validatecommand=(self.complete, "%d", "%S",
                                                    "%i", "%s"))
            self.entry.pack(side="left", fill="x", expand=True)

            if initialfile:
                self.entry.insert(0, initialfile)
        else:
            self.multiple_selection = multiple_selection
            self.entry = ttk.Entry(self.frame_bar, validate="key",
                                   validatecommand=(self.complete, "%d", "%S",
                                                    "%i", "%s"))
            self.entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0,
                            pady=(10, 0))
            self.entry.grid_remove()

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=2, sticky="eswn", pady=3,padx=10)

        # ---  filetypes
        self.filetype = tk.StringVar(self)
        self.filetypes = {}
        if filetypes:
            for name, exts in filetypes:
                if name not in self.filetypes:
                    self.filetypes[name] = []
                self.filetypes[name] = r'%s$' % exts.strip().replace('.', '\.').replace('*', '.*')
            values = list(self.filetypes.keys())
            w = max([len(f) for f in values] + [5])
            self.b_filetype = ttk.Combobox(self.frame_buttons1, textvariable=self.filetype,
                                      state='readonly',
                                      style='types.tkfilebrowser.TCombobox',
                                      values=values,
                                      width=w).pack(side="right", padx=(12,0))
            self.filetype.set(filetypes[0][0])
            try:
                self.filetype.trace_add('write', lambda *args: self._change_filetype())
            except AttributeError:
                self.filetype.trace('w', lambda *args: self._change_filetype())
        else:
            self.filetypes[""] = r".*$"

        # ---  left pane
        left_pane = ttk.Frame(paned)
        left_pane.columnconfigure(0, weight=1)
        left_pane.rowconfigure(0, weight=1)

        paned.add(left_pane, weight=0)
        self.left_tree = ttk.Treeview(left_pane, selectmode="browse",
                                      style="left.tkfilebrowser.Treeview")
        wrapper = TooltipTreeWrapper(self.left_tree)
        self.left_tree.column("#0", width=150)
        self.left_tree.heading("#0", text=_("Shortcuts"), anchor="w")
        self.left_tree.grid(row=0, column=0, sticky="sewn")

        scroll_left = AutoScrollbar(left_pane, command=self.left_tree.yview)
        scroll_left.grid(row=0, column=1, sticky="ns")
        self.left_tree.configure(yscrollcommand=scroll_left.set)

        # list devices and bookmarked locations
        # -------- recent
        self.left_tree.insert("", "end", iid="recent", text=_("Recent"),
                              image=self.im_recent)
        wrapper.add_tooltip("recent", _("Recently used"))

        # -------- devices
        devices = psutil.disk_partitions(all=True if OSNAME == "nt" else False)

        for d in devices:
            m = d.mountpoint
            if m == "/":
                txt = "/"
            else:
                if OSNAME == 'nt':
                    txt = m
                else:
                    txt = split(m)[-1]
            self.left_tree.insert("", "end", iid=m, text=txt,
                                  image=self.im_drive)
            wrapper.add_tooltip(m, m)

        # -------- home
        home = expanduser("~")
        self.left_tree.insert("", "end", iid=home, image=self.im_home,
                              text=split(home)[-1])
        wrapper.add_tooltip(home, home)

        # -------- desktop
        if OSNAME == 'nt':
            desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
        else:
            try:
                desktop = check_output(['xdg-user-dir', 'DESKTOP']).decode().strip()
            except Exception:
                # FileNotFoundError in python3 if xdg-users-dir is not installed,
                # but OSError in python2
                desktop = join(home, 'Desktop')
            if exists(desktop):
                self.left_tree.insert("", "end", iid=desktop, image=self.im_desktop,
                                      text=split(desktop)[-1])
                wrapper.add_tooltip(desktop, desktop)

        # -------- bookmarks
        if OSNAME == 'nt':
            bm = []
            for folder in [shellcon.CSIDL_PERSONAL, shellcon.CSIDL_MYPICTURES,
                           shellcon.CSIDL_MYMUSIC, shellcon.CSIDL_MYVIDEO]:
                try:
                    bm.append([shell.SHGetFolderPath(0, folder, None, 0)])
                except Exception:
                    pass
        else:
            path_bm = join(home, ".config", "gtk-3.0", "bookmarks")
            path_bm2 = join(home, ".gtk-bookmarks")  # old location
            if exists(path_bm):
                with open(path_bm) as f:
                    bms = f.read().splitlines()
            elif exists(path_bm2):
                with open(path_bm) as f:
                    bms = f.read().splitlines()
            else:
                bms = []
            bms = [ch.split() for ch in bms]
            bm = []
            for ch in bms:
                ch[0] = unquote(ch[0]).replace("file://", "")
                bm.append(ch)
        for l in bm:
            if len(l) == 1:
                txt = split(l[0])[-1]
            else:
                txt = l[1]
            self.left_tree.insert("", "end", iid=l[0],
                                  text=txt,
                                  image=self.im_folder)
            wrapper.add_tooltip(l[0], l[0])

        # ---  right pane
        right_pane = ttk.Frame(paned)
        right_pane.columnconfigure(0, weight=1)
        right_pane.rowconfigure(0, weight=1)
        paned.add(right_pane, weight=1)

        if mode != "save" and multiple_selection:
            selectmode = "extended"
        else:
            selectmode = "browse"

        self.right_tree = ttk.Treeview(right_pane, selectmode=selectmode,
                                       style="right.tkfilebrowser.Treeview",
                                       columns=("location", "size", "date","gitstatus"),
                                       displaycolumns=("size", "date","gitstatus"))
        # headings
        self.right_tree.heading("#0", text=_("Name"), anchor="w",
                                command=lambda: self._sort_files_by_name(True))
        self.right_tree.heading("location", text=_("Location"), anchor="w",
                                command=lambda: self._sort_by_location(False))
        self.right_tree.heading("size", text=_("Size"), anchor="w",
                                command=lambda: self._sort_by_size(False))
        self.right_tree.heading("date", text=_("Modified"), anchor="w",
                                command=lambda: self._sort_by_date(False))
        self.right_tree.heading("gitstatus", text=_("Git Status"), anchor="w",
                                command=lambda: self._sort_by_status(False))
        # columns
        self.right_tree.column("#0", width=250)
        self.right_tree.column("location", width=100)
        self.right_tree.column("size", stretch=False, width=85)
        self.right_tree.column("date", width=120)
        self.right_tree.column("gitstatus", width=120)
        # tags
        self.right_tree.tag_configure("0", background=tree_field_bg)
        self.right_tree.tag_configure("1", background=active_bg)
        self.right_tree.tag_configure("folder", image=self.im_folder)
        self.right_tree.tag_configure("file", image=self.im_file)
        self.right_tree.tag_configure("folder_link", image=self.im_folder_link)
        self.right_tree.tag_configure("file_link", image=self.im_file_link)
        self.right_tree.tag_configure("link_broken", image=self.im_link_broken)
        self.right_tree.tag_configure("modified", foreground="#00A000")
        self.right_tree.tag_configure("committed", foreground="#0000A0")
        self.right_tree.tag_configure("staged", foreground="#00A0A0")
        self.right_tree.tag_configure("untracked", foreground="#A00000")

        if mode == "opendir":
            self.right_tree.tag_configure("file", foreground="gray")
            self.right_tree.tag_configure("file_link", foreground="gray")

        self.right_tree.grid(row=0, column=0, sticky="eswn")
        # scrollbar
        self._scroll_h = AutoScrollbar(right_pane, orient='horizontal',
                                       command=self.right_tree.xview)
        self._scroll_h.grid(row=1, column=0, sticky='ew')
        scroll_right = AutoScrollbar(right_pane, command=self.right_tree.yview)
        scroll_right.grid(row=0, column=1, sticky="ns")
        self.right_tree.configure(yscrollcommand=scroll_right.set,
                                  xscrollcommand=self._scroll_h.set)

        # ---  buttons
        if okbuttontext is None:
            if mode == "save":
                okbuttontext = _("Save")
            else:
                okbuttontext = _("Open")
                   
        # ---  key browsing entry
        self.key_browse_var = tk.StringVar(self)
        self.key_browse_entry = ttk.Entry(self, textvariable=self.key_browse_var,
                                          width=10)
        cst.add_trace(self.key_browse_var, "write", self._key_browse)
        # list of folders/files beginning by the letters inserted in self.key_browse_entry
        self.paths_beginning_by = []
        self.paths_beginning_by_index = 0  # current index in the list

        # ---  initialization
        if not initialdir:
            initialdir = expanduser("~")

        self.display_folder(initialdir)
        initialpath = join(initialdir, initialfile)
        if initialpath in self.right_tree.get_children(""):
            self.right_tree.see(initialpath)
            self.right_tree.selection_add(initialpath)

        # ---  bindings
        # filetype combobox
        self.bind_class('TCombobox', '<<ComboboxSelected>>',
                        lambda e: e.widget.selection_clear(),
                        add=True)
        # left tree
        self.left_tree.bind("<<TreeviewSelect>>", self._shortcut_select)
        # right tree
        self.right_tree.bind("<Double-1>", self._select)
        self.right_tree.bind("<Return>", self._select)
        self.right_tree.bind("<Left>", self._go_left)
        if multiple_selection:
            self.right_tree.bind("<Control-a>", self._right_tree_select_all)

        if mode == "save":
            self.right_tree.bind("<<TreeviewSelect>>",
                                 self._file_selection_save)
        elif mode == "opendir":
            self.right_tree.bind("<<TreeviewSelect>>",
                                 self._file_selection_opendir)
        else:
            self.right_tree.bind("<<TreeviewSelect>>",
                                 self._file_selection_openfile)

        self.right_tree.bind("<KeyPress>", self._key_browse_show)
        # listbox
        self.listbox.bind("<FocusOut>",
                          lambda e: self.listbox_frame.place_forget())
        # path entry
        self.entry.bind("<Escape>",
                        lambda e: self.listbox_frame.place_forget())
        self.entry.bind("<Down>", self._down)
        self.entry.bind("<Return>", self.validate)
        self.entry.bind("<Right>", self._tab)
        self.entry.bind("<Tab>", self._tab)
        self.entry.bind("<Control-a>", self._select_all)

        # key browse entry
        self.key_browse_entry.bind("<FocusOut>", self._key_browse_hide)
        self.key_browse_entry.bind("<Escape>", self._key_browse_hide)
        self.key_browse_entry.bind("<Return>", self._key_browse_validate)

        # main bindings
        self.bind("<Control-h>", self.toggle_hidden)
        self.bind("<Alt-Left>", self._hist_backward)
        self.bind("<Alt-Right>", self._hist_forward)
        self.bind("<Alt-Up>", self._go_to_parent)
        self.bind("<Alt-Down>", self._go_to_child)
        self.bind("<Button-1>", self._unpost, add=True)
        self.bind("<FocusIn>", self._hide_listbox)

        if mode != "save":
            self.bind("<Control-l>", self.toggle_path_entry)
        if self.foldercreation:
            self.right_tree.bind("<Control-Shift-N>", self.create_folder)

        self.update_idletasks()
        self.lift()
        if mode == 'save':
            self.entry.selection_range(0, 'end')
            self.entry.focus_set()

    def _right_tree_select_all(self, event):
        if self.mode == "openpath":
            items = self.right_tree.tag_has('folder') + self.right_tree.tag_has('folder_link') \
                + self.right_tree.tag_has('file') + self.right_tree.tag_has('file_link')
        elif self.mode == 'opendir':
            items = self.right_tree.tag_has('folder') + self.right_tree.tag_has('folder_link')
        else:
            items = self.right_tree.tag_has('file') + self.right_tree.tag_has('file_link')
        self.right_tree.selection_clear()
        self.right_tree.selection_set(items)

    def _select_all(self, event):
        """Select all entry content."""
        event.widget.selection_range(0, "end")
        return "break"  # suppress class binding

    # ---  key browsing
    def _key_browse_hide(self, event):
        """Hide key browsing entry."""
        if self.key_browse_entry.winfo_ismapped():
            self.key_browse_entry.place_forget()
            self.key_browse_entry.delete(0, "end")

    def _key_browse_show(self, event):
        """Show key browsing entry."""
        if event.char.isalnum() or event.char in [".", "_", "(", "-", "*", "$"]:
            self.key_browse_entry.place(in_=self.right_tree, relx=0, rely=1,
                                        y=4, x=1, anchor="nw")
            self.key_browse_entry.focus_set()
            self.key_browse_entry.insert(0, event.char)

    def _key_browse_validate(self, event):
        """Hide key browsing entry and validate selection."""
        self._key_browse_hide(event)
        self.right_tree.focus_set()
        self.validate()

    def _key_browse(self, *args):
        """Use keyboard to browse tree."""
        self.key_browse_entry.unbind("<Up>")
        self.key_browse_entry.unbind("<Down>")
        deb = self.key_browse_entry.get().lower()
        if deb:
            if self.mode == 'opendir':
                children = list(self.right_tree.tag_has("folder"))
                children.extend(self.right_tree.tag_has("folder_link"))
                children.sort()
            else:
                children = self.right_tree.get_children("")
            self.paths_beginning_by = [i for i in children if split(i)[-1][:len(deb)].lower() == deb]
            sel = self.click()
            if sel:
                self.right_tree.selection_remove(*sel)
            if self.paths_beginning_by:
                self.paths_beginning_by_index = 0
                self._browse_list(0)
                self.key_browse_entry.bind("<Up>",
                                           lambda e: self._browse_list(-1))
                self.key_browse_entry.bind("<Down>",
                                           lambda e: self._browse_list(1))

    def _browse_list(self, delta):
        """
        Navigate between folders/files with Up/Down keys.

        Navigation between folders/files beginning by the letters in
        self.key_browse_entry.
        """
        self.paths_beginning_by_index += delta
        self.paths_beginning_by_index %= len(self.paths_beginning_by)
        sel = self.click()
        if sel:
            self.right_tree.selection_remove(*sel)
        path = abspath(join(self.history[self._hist_index],
                            self.paths_beginning_by[self.paths_beginning_by_index]))
        self.right_tree.see(path)
        self.right_tree.selection_add(path)

    # ---  column sorting
    def _sort_files_by_name(self, reverse):
        """Sort files and folders by (reversed) alphabetical order."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        folders = list(self.right_tree.tag_has("folder"))
        folders.extend(list(self.right_tree.tag_has("folder_link")))
        files.sort(reverse=reverse)
        folders.sort(reverse=reverse)

        for index, item in enumerate(folders):
            self.move_item(item, index)
        l = len(folders)

        for index, item in enumerate(files):
            self.move_item(item, index + l)
        self.right_tree.heading("#0",
                                command=lambda: self._sort_files_by_name(not reverse))

    def _sort_by_location(self, reverse):
        """Sort files by location."""
        l = [(self.right_tree.set(k, "location"), k) for k in self.right_tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.move_item(k, index)
        self.right_tree.heading("location",
                                command=lambda: self._sort_by_location(not reverse))

    def _sort_by_size(self, reverse):
        """Sort files by size."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        nb_folders = len(self.right_tree.tag_has("folder"))
        nb_folders += len(list(self.right_tree.tag_has("folder_link")))
        files.sort(reverse=reverse, key=getsize)

        for index, item in enumerate(files):
            self.move_item(item, index + nb_folders)

        self.right_tree.heading("size",
                                command=lambda: self._sort_by_size(not reverse))

    def _sort_by_date(self, reverse):
        """Sort files and folders by modification date."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        folders = list(self.right_tree.tag_has("folder"))
        folders.extend(list(self.right_tree.tag_has("folder_link")))
        l = len(folders)
        folders.sort(reverse=reverse, key=getmtime)
        files.sort(reverse=reverse, key=getmtime)

        for index, item in enumerate(folders):
            self.move_item(item, index)
        for index, item in enumerate(files):
            self.move_item(item, index + l)

        self.right_tree.heading("date",
                                command=lambda: self._sort_by_date(not reverse))

    def click(self):
        sel = self.right_tree.selection()
        if len(sel) > 0 and self.is_git_repo():
            tags = self.right_tree.item(sel[0], "tags")
            if "committed" in tags:
                self.clear_buttons()
                self.b_git_rm.pack(side="left", padx=(0,4))
                self.b_git_rm_cached.pack(side="left", padx=(0,4))
                self.b_git_rename_wrapper.pack(side="left", padx=(0,4))
            if "staged" in tags:
                self.clear_buttons()
                self.b_git_rm_cached.pack(side="left", padx=(0,4))
                self.b_git_restore_s.pack(side="left", padx=(0,4))
                self.b_git_commit.pack(side="left", padx=(0,4))
                self.b_git_mv.pack(side="left", padx=(0,4))
            if "modified" in tags:
                self.clear_buttons()
                self.b_git_add.pack(side="left", padx=(0,4))
                self.b_git_restore.pack(side="left", padx=(0,4))
            if "untracked" in tags:
                self.clear_buttons()
                self.b_git_add.pack(side="left", padx=(0,4))
        return sel

    def clear_buttons(self):
        self.b_git_add.pack_forget()
        self.b_git_restore.pack_forget()
        self.b_git_mv.pack_forget()
        self.b_git_restore_s.pack_forget()  
        self.b_git_commit.pack_forget()
        self.b_git_rm.pack_forget()
        self.b_git_rm_cached.pack_forget()
        self.b_git_rename_wrapper.pack_forget()


    def init_need(self,dir):
        if ".git" not in walk(dir).send(None)[1]:
            self.b_git_init.pack(side="left", padx=(0,4))
            self.b_clone.pack(side="left", padx=(0,4))
        else:
            self.b_git_init.pack_forget()
            self.b_clone.pack_forget()

    def init_need_num(self,num):
        if num == 0:
            self.b_git_init.pack(side="left", padx=(0,4))
            self.b_clone.pack(side="left", padx=(0,4))
        else:
            self.b_git_init.pack_forget()
            self.b_clone.pack_forget()

    def update_status(self):
        self._display_folder_walk(self.getdir())

    def getdir(self):
        return self.history[len(self.history)-1]
    
    def split_dir_name(self,fullname : str):
        filedir=fullname[::-1]
        filedir=fullname[:len(fullname)-filedir.index("\\")-1]
        filename=fullname[len(filedir)+1:]
        return filename, filedir
    
    def is_git_repo(self):
        cur_dir=self.getdir()
        for dir in self.history:
            if dir in cur_dir:
                if ".git" in walk(dir).send(None)[1]:
                    return True
        return False

    def getstatus(self, fullname):
        filename,filedir=self.split_dir_name(fullname)
        if ".git" in filename:
            return "IT_IS_DOT_GIT"
        if self.is_git_repo():
            try:
                arg=subprocess.run(['git', 'status', filename], cwd=filedir, capture_output=True).stdout.decode().strip()
                stages=["Untracked", "Changes not staged for commit", "Changes to be committed", "nothing to commit"]
                stages_to_return=["untracked" , "modified" , "staged" , "committed"]
                ret=[]
                for i in range(len(stages)):
                    if stages[i] in arg:
                        ret.append(stages_to_return[i])
                        if i==0:
                            break
                return " & ".join(_ for _ in ret)
            except StopIteration:
                self._display_folder_listdir(dir)
            except PermissionError as e:
                cst.showerror('PermissionError', str(e), master=self)
        else:
            return "NOT_IN_GIT_DIR"
                

        
    def _sort_by_status(self, reverse):
        """Sort files and folders by stage."""
        
        files_folders = list(self.right_tree.tag_has("file"))
        files_folders.extend(list(self.right_tree.tag_has("file_link")))
        files_folders.extend(list(self.right_tree.tag_has("folder")))
        files_folders.extend(list(self.right_tree.tag_has("folder_link")))
        files_folders.sort(reverse=reverse, key=self.getstatus)
        
        for index, item in enumerate(files_folders):
            self.move_item(item, index)
        
        self.right_tree.heading("gitstatus",
                                command=lambda: self._sort_by_status(not reverse))

    # ---  file selection
    def _file_selection_save(self, event):
        """Save mode only: put selected file name in name_entry."""
        sel = self.click()
        if sel:
            sel = sel[0]
            tags = self.right_tree.item(sel, "tags")
            if ("file" in tags) or ("file_link" in tags):
                self.entry.delete(0, "end")
                if self.path_bar.winfo_ismapped():
                    self.entry.insert(0, self.right_tree.item(sel, "text"))
                else:
                    # recently used files
                    self.entry.insert(0, sel)
                self.entry.selection_clear()
                self.entry.icursor("end")

    def _file_selection_openfile(self, event):
        """Put selected file name in path_entry if visible."""
        sel = self.click()
        if sel and self.entry.winfo_ismapped():
            self.entry.delete(0, 'end')
            self.entry.insert("end", self.right_tree.item(sel[0], "text"))
            self.entry.selection_clear()
            self.entry.icursor("end")

    def _file_selection_opendir(self, event):
        """
        Prevent selection of files in opendir mode and put selected folder
        name in path_entry if visible.
        """
        sel = self.click()
        if sel:
            for s in sel:
                tags = self.right_tree.item(s, "tags")
                if ("file" in tags) or ("file_link" in tags):
                    self.right_tree.selection_remove(s)
            sel = self.click()
            if len(sel) == 1 and self.entry.winfo_ismapped():
                self.entry.delete(0, 'end')
                self.entry.insert("end", self.right_tree.item(sel[0], "text"))
                self.entry.selection_clear()
                self.entry.icursor("end")

    def _shortcut_select(self, event):
        """Selection of a shortcut (left pane)."""
        sel = self.left_tree.selection()
        if sel:
            sel = sel[0]
            if sel != "recent":
                self.display_folder(sel)
            else:
                self._display_recents()

    def _display_recents(self):
        """Display recently used files/folders."""
        self.path_bar.grid_remove()
        self.right_tree.configure(displaycolumns=("location", "size", "date", "gitstatus"))
        w = self.right_tree.winfo_width() - 305
        if w < 0:
            w = 250
        self.right_tree.column("#0", width=w)
        self.right_tree.column("location", stretch=False, width=100)
        self.right_tree.column("size", stretch=False, width=85)
        self.right_tree.column("date", width=120)
        self.right_tree.column("gitstatus", width=120)
        if self.foldercreation:
            self.b_new_folder.grid_remove()
        extension = self.filetypes[self.filetype.get()]
        files = self._recent_files.get()
        self.right_tree.delete(*self.right_tree.get_children(""))
        i = 0
        if self.mode == "opendir":
            paths = []
            for p in files:
                if isfile(p):
                    p = dirname(p)
                d, f = split(p)
                tags = [str(i % 2)]
                vals = ()
                if f:
                    if f[0] == ".":
                        tags.append("hidden")
                else:
                    f = "/"
                if isdir(p):
                    if islink(p):
                        tags.append("folder_link")
                    else:
                        tags.append("folder")
                    vals = (p, "", get_modification_date(p))
                if vals and p not in paths:
                    i += 1
                    paths.append(p)
                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=vals)
        else:
            for p in files:
                d, f = split(p)
                tags = [str(i % 2)]
                vals = ()
                if f:
                    if f[0] == ".":
                        tags.append("hidden")
                else:
                    f = "/"
                if islink(p):
                    if isfile(p):
                        if extension == r".*$" or search(extension, f):
                            tags.append("file_link")
                            stats = stat(p)
                            vals = (p, display_size(stats.st_size),
                                    display_modification_date(stats.st_mtime))
                    elif isdir(p):
                        tags.append("folder_link")
                        vals = (p, "", get_modification_date(p))
                elif isfile(p):
                    if extension == r".*$" or search(extension, f):
                        tags.append("file")
                        stats = stat(p)
                        vals = (p, display_size(stats.st_size),
                                display_modification_date(stats.st_mtime))
                elif isdir(p):
                    tags.append("folder")
                    vals = (p, "", get_modification_date(p))
                if vals:
                    i += 1
                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=vals)

    def _select(self, event):
        """display folder content on double click / Enter, validate if file."""
        sel = self.click()
        if sel:
            sel = sel[0]
            tags = self.right_tree.item(sel, "tags")
            if ("folder" in tags) or ("folder_link" in tags):
                self.display_folder(sel)
            elif self.mode != "opendir":
                self.validate(event)
        elif self.mode == "opendir":
            self.validate(event)



    def _unpost(self, event):
        """Hide self.key_browse_entry."""
        if event.widget != self.key_browse_entry:
            self._key_browse_hide(event)

    def _hide_listbox(self, event):
        """Hide the path proposition listbox."""
        if event.widget not in [self.listbox, self.entry, self.listbox_frame]:
            self.listbox_frame.place_forget()

    def _change_filetype(self):
        """Update view on filetype change."""
        if self.path_bar.winfo_ismapped():
            self.display_folder(self.history[self._hist_index])
        else:
            self._display_recents()
        if self.mode == 'save':
            filename = self.entry.get()
            new_ext = self.filetypes[self.filetype.get()]
            if filename and not search(new_ext, filename):
                old_ext = search(r'\..+$', filename).group()
                exts = [e[2:].replace('\.', '.') for e in new_ext[:-1].split('|')]
                exts = [e for e in exts if search(r'\.[^\*]+$', e)]
                if exts:
                    filename = filename.replace(old_ext, exts[0])
                self.entry.delete(0, 'end')
                self.entry.insert(0, filename)

    # ---  path completion in entries: key bindings
    def _down(self, event):
        """Focus listbox on Down arrow press in entry."""
        self.listbox.focus_set()
        self.listbox.selection_set(0)

    def _tab(self, event):
        """Go to the end of selected text and remove selection on tab press."""
        self.entry = event.widget
        self.entry.selection_clear()
        self.entry.icursor("end")
        return "break"

    def _select_enter(self, event, d):
        """Change entry content on Return key press in listbox."""
        self.entry.delete(0, "end")
        self.entry.insert(0, join(d, self.listbox.selection_get()))
        self.entry.selection_clear()
        self.entry.focus_set()
        self.entry.icursor("end")

    def _select_mouse(self, event, d):
        """Change entry content on click in listbox."""
        self.entry.delete(0, "end")
        self.entry.insert(0, join(d, self.listbox.get("@%i,%i" % (event.x, event.y))))
        self.entry.selection_clear()
        self.entry.focus_set()
        self.entry.icursor("end")

    def _completion(self, action, modif, pos, prev_txt):
        """Complete the text in the path entry with existing folder/file names."""
        if self.entry.selection_present():
            sel = self.entry.selection_get()
            txt = prev_txt.replace(sel, '')
        else:
            txt = prev_txt
        if action == "0":
            self.listbox_frame.place_forget()
            txt = txt[:int(pos)] + txt[int(pos) + 1:]
        elif isabs(txt) or self.path_bar.winfo_ismapped():
            txt = txt[:int(pos)] + modif + txt[int(pos):]
            d, f = split(txt)
            if f and not (f[0] == "." and self.hide):
                if not isabs(txt):
                    d2 = join(self.history[self._hist_index], d)
                else:
                    d2 = d

                try:
                    root, dirs, files = walk(d2).send(None)
                    dirs.sort(key=lambda n: n.lower())
                    l2 = []
                    if self.mode != "opendir":
                        files.sort(key=lambda n: n.lower())
                        extension = self.filetypes[self.filetype.get()]
                        if extension == r".*$":
                            l2.extend([i.replace(" ", "\ ") for i in files if i[:len(f)] == f])
                        else:
                            for i in files:
                                if search(extension, i) and i[:len(f)] == f:
                                    l2.append(i.replace(" ", "\ "))
                    l2.extend([i.replace(" ", "\ ") + "/" for i in dirs if i[:len(f)] == f])

                except StopIteration:
                    # invalid content
                    l2 = []

                if len(l2) == 1:
                    self.listbox_frame.place_forget()
                    i = self.entry.index("insert")
                    self.entry.delete(0, "end")
                    self.entry.insert(0, join(d, l2[0]))
                    self.entry.selection_range(i + 1, "end")
                    self.entry.icursor(i + 1)

                elif len(l2) > 1:
                    self.listbox.bind("<Return>", lambda e, arg=d: self._select_enter(e, arg))
                    self.listbox.bind("<Button-1>", lambda e, arg=d: self._select_mouse(e, arg))
                    self.listbox_var.set(" ".join(l2))
                    self.listbox_frame.lift()
                    self.listbox.configure(height=len(l2))
                    self.listbox_frame.place(in_=self.entry, relx=0, rely=1,
                                             anchor="nw", relwidth=1)
                else:
                    self.listbox_frame.place_forget()
        return True

    def _go_left(self, event):
        """Move focus to left pane."""
        sel = self.left_tree.selection()
        if not sel:
            sel = expanduser("~")
        else:
            sel = sel[0]
        self.left_tree.focus_set()
        self.left_tree.focus(sel)

    # ---  go to parent/children folder with Alt+Up/Down
    def _go_to_parent(self, event):
        """Go to parent directory."""
        parent = dirname(self.path_var.get())
        self.display_folder(parent, update_bar=False)

    def _go_to_child(self, event):
        """Go to child directory."""
        lb = [b.get_value() for b in self.path_bar_buttons]
        i = lb.index(self.path_var.get())
        if i < len(lb) - 1:
            self.display_folder(lb[i + 1], update_bar=False)

    # ---  navigate in history with Alt+Left/ Right keys
    def _hist_backward(self, event):
        """Navigate backward in folder selection history."""
        if self._hist_index > -len(self.history):
            self._hist_index -= 1
            self.display_folder(self.history[self._hist_index], reset=False)

    def _hist_forward(self, event):
        """Navigate forward in folder selection history."""
        try:
            self.left_tree.selection_remove(*self.left_tree.selection())
        except TypeError:
            # error raised in python 2 by empty selection
            pass
        if self._hist_index < -1:
            self._hist_index += 1
            self.display_folder(self.history[self._hist_index], reset=False)

    def _update_path_bar(self, path):
        """Update the buttons in path bar."""
        for b in self.path_bar_buttons:
            b.destroy()
        self.path_bar_buttons = []
        if path == "/":
            folders = []
        else:
            folders = path.split(SEP)
            while '' in folders:
                folders.remove('')
        if OSNAME == 'nt':
            p = folders.pop(0) + '\\'
            b = PathButton(self.path_bar, self.path_var, p, text=p,
                           command=lambda path=p: self.display_folder(path, update_bar=False))
        else:
            p = "/"
            b = PathButton(self.path_bar, self.path_var, p, image=self.im_drive,
                           command=lambda path=p: self.display_folder(path, update_bar=False))
        self.path_bar_buttons.append(b)
        b.grid(row=0, column=1, sticky="ns")
        for i, folder in enumerate(folders):
            p = join(p, folder)
            b = PathButton(self.path_bar, self.path_var, p, text=folder,
                           command=lambda f=p: self.display_folder(f, update_bar=False),
                           style="path.tkfilebrowser.TButton")
            self.path_bar_buttons.append(b)
            b.grid(row=0, column=i + 2, sticky="ns")

    def _display_folder_listdir(self, folder, reset=True, update_bar=True):
        """
        Display the content of folder in self.right_tree.
        Arguments:
            * reset (boolean): forget all the part of the history right of self._hist_index
            * update_bar (boolean): update the buttons in path bar
        """
        self.clear_buttons()
        # remove trailing / if any
        folder = abspath(folder)
        # reorganize display if previous was 'recent'
        if not self.path_bar.winfo_ismapped():
            self.path_bar.grid()
            self.right_tree.configure(displaycolumns=("size", "date","gitstatus"))
            w = self.right_tree.winfo_width() - 205
            if w < 0:
                w = 250
            self.right_tree.column("#0", width=w)
            self.right_tree.column("size", stretch=False, width=85)
            self.right_tree.column("date", width=120)
            self.right_tree.column("gitstatus",width=120)
            if self.foldercreation:
                self.b_new_folder.grid()
            self.b_update_status.grid()

        # reset history
        if reset:
            if not self._hist_index == -1:
                self.history = self.history[:self._hist_index + 1]
                self._hist_index = -1
            self.history.append(folder)
        # update path bar
        if update_bar:
            self._update_path_bar(folder)
        self.path_var.set(folder)
        # disable new folder creation if no write access
        if self.foldercreation:
            if access(folder, W_OK):
                self.b_new_folder.state(('!disabled',))
            else:
                self.b_new_folder.state(('disabled',))
        # clear self.right_tree
        self.right_tree.delete(*self.right_tree.get_children(""))
        self.right_tree.delete(*self.hidden)
        self.hidden = ()
        root = folder
        extension = self.filetypes[self.filetype.get()]
        content = listdir(folder)
        self.branch()
        self.log_need()
        self.update_branch_head()
        self.init_need_num(len(content))
        i = 0
        for f in content:
            self.init_need(folder)
            p = join(root, f)
            if f[0] == ".":
                tags = ("hidden",)
                if not self.hide:
                    tags = (str(i % 2),)
                    i += 1
            else:
                tags = (str(i % 2),)
                i += 1
            if isfile(p):
                if extension == r".*$" or search(extension, f):
                    if islink(p):
                        tags = tags + ("file_link",)
                    else:
                        tags = tags + ("file",)
                    
                    gits=self.getstatus(p)
                    if "untracked" in gits or "modified" in gits:
                        self.b_git_add.pack(side="left", padx=(0,4))
                    if gits != "NOT_IN_GIT_DIR":
                        for g in gits.split(" & "):
                            tags = tags + (g, )
                    else:
                        gits=""

                    try:
                        stats = stat(p)
                    except OSError:
                        self.right_tree.insert("", "end", p, text=f, tags=tags,
                                               values=("", "??", "??", gits))
                    else:
                        self.right_tree.insert("", "end", p, text=f, tags=tags,
                                               values=("",
                                                       display_size(stats.st_size),
                                                       display_modification_date(stats.st_mtime),
                                                       gits))
            elif isdir(p):
                if islink(p):
                    tags = tags + ("folder_link",)
                else:
                    tags = tags + ("folder",)
                    
                gits=self.getstatus(p)
                if "untracked" in gits or "modified" in gits:
                    self.b_git_add.pack(side="left", padx=(0,4))
                if gits == "IT_IS_DOT_GIT":
                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=("", "", get_modification_date(p)))
                else:
                    if gits != "NOT_IN_GIT_DIR":
                        for g in gits.split(" & "):
                            tags = tags + (g, )
                    else:
                        gits=""
                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=("", "", get_modification_date(p), gits))
            else:  # broken link
                tags = tags + ("link_broken",)
                self.right_tree.insert("", "end", p, text=f, tags=tags,
                                       values=("", "??", "??"))

        items = self.right_tree.get_children("")
        if items:
            self.right_tree.focus_set()
            self.right_tree.focus(items[0])
        if self.hide:
            self.hidden = self.right_tree.tag_has("hidden")
            self.right_tree.detach(*self.right_tree.tag_has("hidden"))
        self._sort_files_by_name(False)

    def _display_folder_walk(self, folder, reset=True, update_bar=True):
        """
        Display the content of folder in self.right_tree.
        Arguments:
            * reset (boolean): forget all the part of the history right of self._hist_index
            * update_bar (boolean): update the buttons in path bar
        """
        self.clear_buttons()
        # remove trailing / if any
        folder = abspath(folder)
        # reorganize display if previous was 'recent'
        if not self.path_bar.winfo_ismapped():
            self.path_bar.grid()
            self.right_tree.configure(displaycolumns=("size", "date","gitstatus"))
            w = self.right_tree.winfo_width() - 205
            if w < 0:
                w = 250
            self.right_tree.column("#0", width=w)
            self.right_tree.column("size", stretch=False, width=85)
            self.right_tree.column("date", width=120)
            self.right_tree.column("gitstatus",width=120)
            
            if self.foldercreation:
                self.b_new_folder.grid()
            self.b_update_status.grid()

        # reset history
        if reset:
            if not self._hist_index == -1:
                self.history = self.history[:self._hist_index + 1]
                self._hist_index = -1
            self.history.append(folder)
        # update path bar
        if update_bar:
            self._update_path_bar(folder)
        self.path_var.set(folder)
        # disable new folder creation if no write access
        if self.foldercreation:
            if access(folder, W_OK):
                self.b_new_folder.state(('!disabled',))
            else:
                self.b_new_folder.state(('disabled',))
        # clear self.right_tree
        self.right_tree.delete(*self.right_tree.get_children(""))
        self.right_tree.delete(*self.hidden)
        self.hidden = ()
        self.branch()
        self.log_need()
        self.update_branch_head()
        try:
            root, dirs, files = walk(folder).send(None)
            self.init_need_num(len(files)+len(dirs))
            # display folders first
            dirs.sort(key=lambda n: n.lower())
            i = 0
            for d in dirs:
                p = join(root, d)
                if islink(p):
                    tags = ("folder_link",)
                else:
                    tags = ("folder",)
                if d[0] == ".":
                    tags = tags + ("hidden",)
                    if not self.hide:
                        tags = tags + (str(i % 2),)
                        i += 1
                else:
                    tags = tags + (str(i % 2),)
                    i += 1
                
                gits=self.getstatus(p)
                self.init_need(self.getdir())
                if "untracked" in gits or "modified" in gits:
                    self.b_git_add.pack(side="left", padx=(0,4))
                if gits == "IT_IS_DOT_GIT":
                    self.right_tree.insert("", "end", p, text=d, tags=tags,
                                           values=("", "", get_modification_date(p)))
                else:
                    if gits != "NOT_IN_GIT_DIR":
                        for g in gits.split(" & "):
                            tags = tags + (g, )
                    else:
                        gits=""
                    self.right_tree.insert("", "end", p, text=d, tags=tags,
                                           values=("", "", get_modification_date(p), gits))
            # display files
            files.sort(key=lambda n: n.lower())
            extension = self.filetypes[self.filetype.get()]
            for f in files:
                if extension == r".*$" or search(extension, f):
                    p = join(root, f)
                    if islink(p):
                        tags = ("file_link",)
                    else:
                        tags = ("file",)
                    try:
                        stats = stat(p)
                    except FileNotFoundError:
                        stats = Stats(st_size="??", st_mtime="??")
                        tags = ("link_broken",)
                    if f[0] == ".":
                        tags = tags + ("hidden",)
                        if not self.hide:
                            tags = tags + (str(i % 2),)
                            i += 1
                    else:
                        tags = tags + (str(i % 2),)
                        i += 1

                    gits=self.getstatus(p)
                    self.init_need(self.getdir())
                    if "untracked" in gits or "modified" in gits:
                        self.b_git_add.pack(side="left", padx=(0,4))
                    if gits != "NOT_IN_GIT_DIR":
                        for g in gits.split(" & "):
                            tags = tags + (g, )
                    else:
                        gits=""

                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=("",
                                                   display_size(stats.st_size),
                                                   display_modification_date(stats.st_mtime),
                                                   gits))
            items = self.right_tree.get_children("")
            if items:
                self.right_tree.focus_set()
                self.right_tree.focus(items[0])
            if self.hide:
                self.hidden = self.right_tree.tag_has("hidden")
                self.right_tree.detach(*self.right_tree.tag_has("hidden"))
        except StopIteration:
            self._display_folder_listdir(folder, reset, update_bar)
        except PermissionError as e:
            cst.showerror('PermissionError', str(e), master=self)

    def _display_folder_scandir(self, folder, reset=True, update_bar=True):
        """
        Display the content of folder in self.right_tree.

        Arguments:
            * reset (boolean): forget all the part of the history right of self._hist_index
            * update_bar (boolean): update the buttons in path bar
        """
        self.clear_buttons()
        # remove trailing / if any
        folder = abspath(folder)
        # reorganize display if previous was 'recent'
        if not self.path_bar.winfo_ismapped():
            self.path_bar.grid()
            self.right_tree.configure(displaycolumns=("size", "date","gitstatus"))
            w = self.right_tree.winfo_width() - 205
            if w < 0:
                w = 250
            self.right_tree.column("#0", width=w)
            self.right_tree.column("size", stretch=False, width=85)
            self.right_tree.column("date", width=120)
            self.right_tree.column("gitstatus",width=120)
            if self.foldercreation:
                self.b_new_folder.grid()
            self.b_update_status.grid()

        # reset history
        if reset:
            if not self._hist_index == -1:
                self.history = self.history[:self._hist_index + 1]
                self._hist_index = -1
            self.history.append(folder)
        # update path bar
        if update_bar:
            self._update_path_bar(folder)
        self.path_var.set(folder)
        # disable new folder creation if no write access
        if self.foldercreation:
            if access(folder, W_OK):
                self.b_new_folder.state(('!disabled',))
            else:
                self.b_new_folder.state(('disabled',))
        # clear self.right_tree
        self.right_tree.delete(*self.right_tree.get_children(""))
        self.right_tree.delete(*self.hidden)
        self.hidden = ()
        extension = self.filetypes[self.filetype.get()]
        self.branch()
        self.log_need()
        self.update_branch_head()
        try:
            content = sorted(scandir(folder), key=key_sort_files)
            self.init_need_num(len(content))
            i = 0
            tags_array = [["folder", "folder_link"],
                          ["file", "file_link"]]
            for f in content:
                b_file = f.is_file()
                name = f.name
                try:
                    stats = f.stat()
                    tags = (tags_array[b_file][f.is_symlink()],)
                except FileNotFoundError:
                    stats = Stats(st_size="??", st_mtime="??")
                    tags = ("link_broken",)
                if name[0] == '.':
                    tags = tags + ("hidden",)
                    if not self.hide:
                        tags = tags + (str(i % 2),)
                        i += 1
                else:
                    tags = tags + (str(i % 2),)
                    i += 1

                gits=self.getstatus(folder+"\\"+name)
                self.init_need(self.getdir())
                if "untracked" in gits or "modified" in gits:
                    self.b_git_add.pack(side="left", padx=(0,4))
                if gits == "IT_IS_DOT_GIT":
                    self.right_tree.insert("", "end", f.path, text=name, tags=tags,
                                           values=("", "",
                                                   display_modification_date(stats.st_mtime)))
                else:
                    if gits != "NOT_IN_GIT_DIR":
                        for g in gits.split(" & "):
                            tags = tags + (g, )
                    else:
                        gits=""

                    if b_file:
                        if extension == r".*$" or search(extension, name):
                            self.right_tree.insert("", "end", f.path, text=name, tags=tags,
                                                   values=("",
                                                           display_size(stats.st_size),
                                                           display_modification_date(stats.st_mtime),
                                                           gits))
                    else:
                        self.right_tree.insert("", "end", f.path, text=name, tags=tags,
                                               values=("", "",
                                                       display_modification_date(stats.st_mtime),
                                                       gits))
            items = self.right_tree.get_children("")
            if items:
                self.right_tree.focus_set()
                self.right_tree.focus(items[0])
            if self.hide:
                self.hidden = self.right_tree.tag_has("hidden")
                self.right_tree.detach(*self.right_tree.tag_has("hidden"))
        except FileNotFoundError:
            self._display_folder_scandir(expanduser('~'), reset=True, update_bar=True)
        except PermissionError as e:
            cst.showerror('PermissionError', str(e), master=self)

    def create_folder(self, event=None):
        """Create new folder in current location."""
        def ok(event):
            name = e.get()
            e.destroy()
            if name:
                folder = join(path, name)
                try:
                    mkdir(folder)
                except Exception:
                    # show exception to the user (typically PermissionError or FileExistsError)
                    cst.showerror(_("Error"), traceback.format_exc())
                self.display_folder(path)

        def cancel(event):
            e.destroy()
            self.right_tree.delete("tmp")

        path = self.path_var.get()

        if self.path_bar.winfo_ismapped() and access(path, W_OK):
            self.right_tree.insert("", 0, "tmp", tags=("folder", "1"))
            self.right_tree.see("tmp")
            e = ttk.Entry(self)
            x, y, w, h = self.right_tree.bbox("tmp", column="#0")
            e.place(in_=self.right_tree, x=x + 24, y=y,
                    width=w - x - 4)
            e.bind("<Return>", ok)
            e.bind("<Escape>", cancel)
            e.bind("<FocusOut>", cancel)
            e.focus_set()
        

    def move_item(self, item, index):
        """Move item to index and update dark/light line alternance."""
        self.right_tree.move(item, "", index)
        tags = [t for t in self.right_tree.item(item, 'tags')
                if t not in ['1', '0']]
        tags.append(str(index % 2))
        self.right_tree.item(item, tags=tags)

    def toggle_path_entry(self, event):
        """Toggle visibility of path entry."""
        if self.entry.winfo_ismapped():
            self.entry.grid_remove()
            self.entry.delete(0, "end")
        else:
            self.entry.grid()
            self.entry.focus_set()

    def toggle_hidden(self, event=None):
        """Toggle the visibility of hidden files/folders."""
        if self.hide:
            self.hide = False
            for item in reversed(self.hidden):
                self.right_tree.move(item, "", 0)
            self.hidden = ()
        else:
            self.hide = True
            self.hidden = self.right_tree.tag_has("hidden")
            self.right_tree.detach(*self.right_tree.tag_has("hidden"))
        # restore color alternance
        for i, item in enumerate(self.right_tree.get_children("")):
            tags = [t for t in self.right_tree.item(item, 'tags')
                    if t not in ['1', '0']]
            tags.append(str(i % 2))
            self.right_tree.item(item, tags=tags)

    def get_result(self):
        """Return selection."""
        return self.result
    
    def git_init(self):
        dir=self.getdir()
        subprocess.run(['git', 'init', dir])
        self._display_folder_walk(dir)
        
    def git_add(self):
        dir = self.getdir()
        
        if self.is_git_repo():
            sel = self.click()
        
            if len(sel) == 0:
                answer = messagebox.askquestion("Confirmation", "Do you want to add all modified files?")
                if answer == "yes":
                    subprocess.run(['git', 'add', '.'], cwd=dir)
                    self.update_status()
                else:
                    return
        
            for fnf in sel:
                subprocess.run(['git', 'add', fnf], cwd=dir)
                self.update_status()

        else:
            print("fatal: not a git repository (or any of the parent directories): .git")

    
    def git_commit(self):
        dir = self.getdir()
        staged_list = []
      
        staged_search = ['git', 'diff', '--name-only', '--cached'] # "Changes to be committed" 상태의 파일을 이름만 출력해주는 명령어
        result = subprocess.run(staged_search, stdout=subprocess.PIPE, text=True, cwd=dir) #stdout에 출력값 저장
        
        output_lines = result.stdout.strip().split('\n') #파일이름을 하나씩 staged_list에 저장
        for line in output_lines:
            staged_list.append(line)
        
        message = "Do you want to commit this staged files?\n\n[ Staged changes ] :\n" + "\n".join(staged_list)
        is_ok_commit = messagebox.askquestion("Staged file list to commit", message)
        if is_ok_commit == 'yes':
            msg = simpledialog.askstring("commit", "Enter your commit message: ") #커밋메세지 작성
        
            if msg and msg.strip(): # 커밋 메세지 작성 후 "OK" 버튼이 눌렀을 때
                subprocess.run(['git', 'commit', '-m', msg], cwd=dir)
                self.update_status()
            elif msg is not None: # "OK" 버튼이 눌렸을 때 메시지가 빈 문자열인 경우
                messagebox.showerror("Error", "Commit message cannot be empty.")
            elif msg is None: #"Cancel" 버튼 눌렀을 때
                pass    
        else:
            return
            
                        
    def git_restore(self): # modified -> unmodified (���� add�� ������ �� ���¿��� �ֱ� Ŀ�� ���·� ���ư��� == ���� ���)
        file_tuple = self.click() #Ʃ������
        
        if len(file_tuple)>0:   # tuple�� empty���� �ѹ� �� üũ
            for file_path in file_tuple:
                file_name, dir = self.split_dir_name(file_path) #����� ������ �κ��� file_name

                subprocess.run(['git', 'restore', file_name], cwd=dir)
                self.update_status()
        else:
            messagebox.showerror("Error", "No file selected for restore.")
            print("No file selected.")
    
    def git_restore_s(self): # staged -> modified (add �� ���¿��� add �� ������ �� ���·� ���ư��� == add ���)
        file_tuple = self.click() #Ʃ������
        if len(file_tuple)>0:   # tuple�� empty���� �ѹ� �� üũ
            for file_path in file_tuple:
                file_name, dir = self.split_dir_name(file_path) #����� ������ �κ��� file_name

                subprocess.run(['git', 'restore', '--staged', file_name], cwd=dir)
                self.update_status()
        else:
            messagebox.showerror("Error", "No file selected for restore.")
            print("No file selected.")

    def git_rm(self): #committed -> staged
        file_tuple = self.click()
        if len(file_tuple) > 0:
            for file_path in file_tuple:
                file_name, dir = self.split_dir_name(file_path) #����� ������ �κ��� file_name
                result = subprocess.run(['git', 'rm', '-r', file_name], cwd=dir)
                if result.returncode == 0:  # subprocess ������ ���������� ���� ���
                    self.update_status()
                else:
                    print("Failed to remove file from git repository.")
        else:
            print("No file selected.")

    def git_rm_cached(self):
        file_tuple = self.click()
        if len(file_tuple) > 0:
            for file_path in file_tuple:
                file_name, dir = self.split_dir_name(file_path) #����� ������ �κ��� file_name

                result = subprocess.run(['git', 'rm', '-r', '--cached', file_name], cwd=dir)
                if result.returncode == 0:
                    self.update_status()
                else:
                    print("Failed to remove file from git repository.")
        else:
            print("No file selected.")
    
    
    def _get_git_directory(self):
        """Returns the path to the .git directory."""
        cur_dir = self.getdir()
        for dir in self.history:
            if dir in cur_dir and ".git" in walk(dir).send(None)[1]:
                return dir
        return None
            

    def _git_rename_wrapper(self):
        if self._get_git_directory():
            self.git_rename()
            
    def git_rename(self):
        old_path = self.click()[0]
        # Ask for new file path

        while True:
            new_path = tkfilebrowser.askopendirname(parent=self.parent)
            print(new_path, new_path == "")
            if new_path == "":
                return

            new_file_name = os.path.basename(old_path)
            while True:
                # Ask for new file name
                new_file_name = simpledialog.askstring("New file name", "Enter the new file name", initialvalue=new_file_name)
                print(new_file_name, new_file_name == None)
                if new_file_name == None:
                    return
                if not new_file_name:
                    return
                new_path = os.path.join(new_path, new_file_name)

                # Check if the new file path already exists
                if os.path.exists(new_path):
                    if tk.messagebox.askyesno("File Already Exists", "File '{}' already exists. Do you want to overwrite it?".format(new_path)):
                        break
                else:
                    break
            
            new_path = new_path.replace("/","\\")
            if self._get_git_directory() not in new_path:
                messagebox.showerror("Not in git repository")
            else:
                break

        try:
            subprocess.run(["git", "mv", old_path, new_path], cwd=self._get_git_directory(), check=True, shell=False, stderr=subprocess.PIPE)
            self._display_folder_walk(self.getdir())
        except subprocess.CalledProcessError as e:
            print("Failed to rename file using git mv command. stderr:", e.stderr.decode())

    def branch(self):
        if self.is_git_repo():
            self.b_branch.pack(side="left",padx=(0,3))

            #브랜치 헤드 업데이트
            self.update_branch_head()
        else:
            self.b_branch.pack_forget()
    
    def branch_function(self):
        #branch 버튼을 클릭하면 새 창 띄우고 깃의 모든 원격 브랜치와 로컬 브랜치 리스트 버튼 보여주기
        if self.is_git_repo():

            #브랜치 헤드 업데이트
            self.update_branch_head()

            # 브랜치 새 창 띄우기
            root = tk.Tk()
            style = ttk.Style(root)
            style.theme_use("clam")
            root.configure(bg=style.lookup('TFrame', 'background'))

            # 브랜치 기능 버튼
            ttk.Label(root, text="Git Branch Function").grid(columnspan=5, padx=60, pady=10, sticky='ew')
            ttk.Button(root, text="Create Branch", command=lambda: self.create_branch(root)).grid(column=0, columnspan=5, pady=(0,4))
            ttk.Button(root, text="Delete Branch", command=lambda: self.delete_branch(root)).grid(column=0, columnspan=5, pady=(0,4))
            ttk.Button(root, text="Rename Branch", command=lambda: self.rename_branch(root)).grid(column=0, columnspan=5, pady=(0,4))
            ttk.Button(root, text="Checkout Branch", command=lambda: self.checkout_branch(root)).grid(column=0, columnspan=5, pady=(0,4))
            ttk.Button(root, text="Merge Branch", command=lambda: self.merge_branch(root)).grid(column=0, columnspan=5, pady=(0,4))

            
    def return_branch_list(self):
        if self.is_git_repo():
            # 원격 브랜치
            headbr = None
            cmd=subprocess.run(['git', 'branch' , '-r'], cwd=self._get_git_directory(), capture_output=True).stdout.decode().strip().split("\n")
            for i in range(len(cmd)):
                if i>=len(cmd):
                    break
                cmd[i]=cmd[i].replace(" ", "")
                if "->" in cmd[i]:
                    headbr = cmd[i].split("->")
                    del cmd[i]
                    #headbr[-1]에 헤드가 가리키는 브랜치가 있다.
            
            # 로컬 브랜치
            curbr = None
            cmdL=subprocess.run(['git', 'branch'], cwd=self._get_git_directory(), capture_output=True).stdout.decode().strip().split("\n")
            for j in range(len(cmdL)):
                if j>=len(cmdL):
                    break
                cmdL[j]=cmdL[j].replace(" ", "")
                if "*" in cmdL[j]:
                    cmdL[j] = cmdL[j].replace("*", "")
                    curbr = cmdL[j]
            
            return cmd, cmdL, i, j, headbr, curbr   
            
    def create_branch(self, root):
        dir = self.getdir()
        
        if self.is_git_repo():
            branch_name=simpledialog.askstring("Create Branch", "Enter the new branch name: ")

            if branch_name and branch_name.strip(): # 브랜치 이름 작성하고 "OK" 버튼이 눌렀을 때
                try:
                    result = subprocess.run(['git', 'branch', branch_name], cwd=dir, stderr=subprocess.PIPE)
                    result.check_returncode()  # 오류확인

                    if result.returncode == 0:
                        # create가 정상적으로 수행되었을 때 확인 메세지창
                        messagebox.showinfo("Git create Message", "Create successful! Now [ " + branch_name + " ] branch is exists.")
                        self.update_status()

                        root.destroy()

                except subprocess.CalledProcessError as e:
                    # 오류가 발생한 경우 오류 메시지창 띄우기
                    if e.stderr:
                        error_message = e.stderr.strip()
                        messagebox.showerror("Error", error_message)
                    else:
                        print(str(e))
            elif branch_name is not None: # "OK" 버튼이 눌렸을 때 메시지가 빈 문자열인 경우
                messagebox.showerror("Error", "Branch name cannot be empty.")
            elif branch_name is None: # "Cancel" 버튼 눌렀을 때
                pass
        else:
            print("fatal: not a git repository (or any of the parent directories): .git")
    
    def clicked_to_delete(self, curbr, branch_name, root, root_del):
            dir=self.getdir()
            try:
                result = subprocess.run(['git', 'branch', '-d', branch_name], cwd=dir, stderr=subprocess.PIPE)
                result.check_returncode()

                if result.returncode == 0:
                    # delete가 정상적으로 수행되었을 때 확인 메세지창
                    messagebox.showinfo("Git delete Message", "Delete successful! Now [ " + branch_name + " ] branch is not exists.")
                    self.update_status()
                    
                    root_del.destroy()  # 만약 실행 후 창을 닫고 싶으면 이 줄만 실행
                    #self.delete_branch(root) # 만약 새로 고침을 하고 싶다면 이 줄도 추가

                    root.destroy()
            
            except subprocess.CalledProcessError as e:
                if branch_name == curbr :
                    error_message = "You cannot delete the current branch (head branch).\nIf you want to delete the current branch, please checkout to another branch and press the delete button again to select the branch you want to delete."
                    messagebox.showerror("Error", error_message)
                elif e.stderr:
                    error_message = e.stderr.strip()
                    messagebox.showerror("Error", error_message)   
                else:
                    print(str(e))
            
    def delete_branch(self, root):
        #branch 버튼을 클릭하면 새 창 띄우고 깃의 모든 원격 브랜치와 로컬 브랜치 리스트 버튼 보여주기
        if self.is_git_repo():
            cmd, cmdL, i, j, headbr, curbr = self.return_branch_list()  #headbr=remote, curbr=local
            # 브랜치 새 창 띄우기
            root_del = tk.Tk()
            style = ttk.Style(root_del)
            style.theme_use("clam")
            root_del.configure(bg=style.lookup('TFrame', 'background'))
            ttk.Label(root_del, text="Select one branch you want to delete.").grid(row=0, column=0, columnspan=5)
            ttk.Label(root_del, text=" ").grid(row=1, column=0, columnspan=5)
            ttk.Label(root_del, text="[Remote branch]").grid(row=2, column=0, columnspan=5)

            arrange=0   # 원격 브랜치 나타내기
            if i>0 and curbr != None: # 원격 브랜치가 있을 때

                for i in cmd:
                    q,r=divmod(arrange,5)
                    if i == headbr[-1]:     # 헤드가 가리키는 원격 브랜치 색 바꾸기
                        style.configure("Custom.TButton", foreground="red")

                        head_remote = ttk.Button(root_del, text=i, style="Custom.TButton")
                        head_remote.grid(row=q+3, column=r)

                        self.b_branch_list.append(head_remote)
                    else:
                        self.b_branch_list.append(ttk.Button(root_del, text=i).grid(row=q+3, column=r))
                    
                    self.b_branch_list[len(self.b_branch_list)-1]
                    arrange += 1

                    
            else: # 원격 브랜치가 없을 때
                ttk.Label(root_del, text="There is no remote branch yet.", foreground="blue").grid(row=3, column=0, columnspan=5)
                ttk.Label(root_del, text=" ").grid(row=4, column=0, columnspan=5)          
                ttk.Label(root_del, text="[Local branch]").grid(row=5, column=0, columnspan=5)
            

            # 로컬 브랜치 나타내기
            q,r=divmod(arrange,5)
            ttk.Label(root_del, text=" ").grid(row=q+4, column=0, columnspan=5)
            ttk.Label(root_del, text="[Local branch]").grid(row=q+5, column=0, columnspan=5)
                
            arr=0
            for j in cmdL:
                q,rd=divmod(arrange,5)
                qd,r=divmod(arr,5)
                if j == curbr and curbr != None:
                    style.configure("Custom.TButton", foreground="red")
                    head_local = ttk.Button(root_del, text=j, command=lambda id=j: self.clicked_to_delete(curbr, id, root, root_del), style="Custom.TButton")
                    head_local.grid(row=q+6, column=r)

                    self.b_branch_list.append(head_local)
                else:
                    self.b_branch_list.append(ttk.Button(root_del, text=j, command=lambda id=j: self.clicked_to_delete(curbr, id, root, root_del)).grid(row=q+6, column=r))

                self.b_branch_list[len(self.b_branch_list)-1]
                arrange += 1
                arr += 1
            
        else:
            self.b_branch_list=[]

    def clicked_to_rename(self, old_branch_name, root, root_ren):
            dir=self.getdir()
            
            new_branch_name=simpledialog.askstring("Rename Branch", "Enter the new branch name for rename the branch:")
            if new_branch_name and new_branch_name.strip(): # rename할 브랜치 이름 작성하고 "OK" 버튼이 눌렀을 때
                try:
                    result = subprocess.run(['git', 'branch', '-m', old_branch_name, new_branch_name], cwd=dir, stderr=subprocess.PIPE)
                    result.check_returncode()  
                    
                    if result.returncode == 0:
                        # rename이 정상적으로 수행되었을 때 확인 메세지창
                        messagebox.showinfo("Git rename Message", "Rename successful! Now [ " + old_branch_name + " ] branch is [ " + new_branch_name + " ] branch.")
                        self.update_status()
                
                        root_ren.destroy()  # 만약 실행 후 창을 닫고 싶으면 이 줄만 실행
                        #self.rename_branch(root) # 만약 새로 고침을 하고 싶다면 이 줄도 추가 

                        root.destroy()

                except subprocess.CalledProcessError as e:
                    if e.stderr:
                        error_message = e.stderr.strip()
                        messagebox.showerror("Error", error_message)
                    else:
                        print(str(e))   
            elif new_branch_name is not None: # "OK" 버튼이 눌렸을 때 메시지가 빈 문자열인 경우
                messagebox.showerror("Error", "Branch name cannot be empty.")
            elif new_branch_name is None: # "Cancel" 버튼 눌렀을 때
                pass 
            
               
                        
    def rename_branch(self, root):
        #branch 버튼을 클릭하면 새 창 띄우고 깃의 모든 원격 브랜치와 로컬 브랜치 리스트 버튼 보여주기
        if self.is_git_repo():
            cmd, cmdL, i, j, headbr, curbr = self.return_branch_list()
            # 브랜치 새 창 띄우기
            root_ren = tk.Tk()
            style = ttk.Style(root_ren)
            style.theme_use("clam")
            root_ren.configure(bg=style.lookup('TFrame', 'background'))
            ttk.Label(root_ren, text="Select one branch you want to rename.").grid(row=0, column=0, columnspan=5)
            ttk.Label(root_ren, text=" ").grid(row=1, column=0, columnspan=5)
            ttk.Label(root_ren, text="[Remote branch]").grid(row=2, column=0, columnspan=5)

            arrange=0   # 원격 브랜치 나타내기
            if i>0 and curbr != None: # 원격 브랜치가 있을 때

                for i in cmd:
                    q,r=divmod(arrange,5)
                    if i == headbr[-1]:     # 헤드가 가리키는 원격 브랜치 색 바꾸기
                        style.configure("Custom.TButton", foreground="red")

                        head_remote = ttk.Button(root_ren, text=i, style="Custom.TButton")
                        head_remote.grid(row=q+3, column=r)

                        self.b_branch_list.append(head_remote)
                    else:
                        self.b_branch_list.append(ttk.Button(root_ren, text=i).grid(row=q+3, column=r))
                    
                    self.b_branch_list[len(self.b_branch_list)-1]
                    arrange += 1

                    
            else: # 원격 브랜치가 없을 때
                ttk.Label(root_ren, text="There is no remote branch yet.", foreground="blue").grid(row=3, column=0, columnspan=5)
                ttk.Label(root_ren, text=" ").grid(row=4, column=0, columnspan=5)          
                ttk.Label(root_ren, text="[Local branch]").grid(row=5, column=0, columnspan=5)
            

            # 로컬 브랜치 나타내기
            q,r=divmod(arrange,5)
            ttk.Label(root_ren, text=" ").grid(row=q+4, column=0, columnspan=5)
            ttk.Label(root_ren, text="[Local branch]").grid(row=q+5, column=0, columnspan=5)
                
            arr=0
            button_num=1
            for j in cmdL:
                q,rd=divmod(arrange,5)
                qd,r=divmod(arr,5)
                if j == curbr and curbr != None:
                    style.configure("Custom.TButton", foreground="red")

                    head_local = ttk.Button(root_ren, text=j, command=lambda id=j: self.clicked_to_rename(id,root,root_ren), style="Custom.TButton")
                    head_local.grid(row=q+6, column=r)

                    self.b_branch_list.append(head_local)
                else:
                    self.b_branch_list.append(ttk.Button(root_ren, text=j, command=lambda id=j: self.clicked_to_rename(id,root,root_ren)).grid(row=q+6, column=r))

                self.b_branch_list[len(self.b_branch_list)-1]
                arrange += 1
                arr += 1              
        else:
            self.b_branch_list=[]
        
        

    def clicked_to_checkout(self, iscurbr, branch_name, root, root_che):
        dir = self.getdir()

        try:
            result = subprocess.run(['git', 'checkout', branch_name], cwd=dir, stderr=subprocess.PIPE)
            result.check_returncode()  # 오류확인
            self.update_status()
            
            if result.returncode == 0:
                # checkout이 정상적으로 수행되었을 때 확인 메세지창
                if iscurbr == "Y":
                    messagebox.showinfo("Git Checkout Message", "The branch you just chose is the current branch. So checkout is executed, but the branch is unchanged.")
                else:
                    messagebox.showinfo("Git Checkout Message", "Checkout successful! Now you are in [ " + branch_name + " ] branch.")
                
                root_che.destroy()  # 만약 실행 후 창을 닫고 싶으면 이 줄만 실행
                #self.checkout_branch(root) # 만약 새로 고침을 하고 싶다면 이 줄도 추가

                root.destroy()
            
        except subprocess.CalledProcessError as e:
            # 오류가 발생한 경우 오류 메시지창 띄우기
            if e.stderr:
                error_message = e.stderr.strip()
                messagebox.showerror("Error", error_message)
            else:
                print(str(e))


    def checkout_branch(self, root):
        #branch 버튼을 클릭하면 새 창 띄우고 깃의 모든 원격 브랜치와 로컬 브랜치 리스트 버튼 보여주기
        if self.is_git_repo():
            cmd, cmdL, i, j, headbr, curbr = self.return_branch_list()
            
            # 브랜치 새 창 띄우기
            root_che = tk.Tk()
            style = ttk.Style(root_che)
            style.theme_use("clam")
            root_che.configure(bg=style.lookup('TFrame', 'background'))
            ttk.Label(root_che, text="Select one branch you want to checkout").grid(row=0, column=0, columnspan=5)
            ttk.Label(root_che, text=" ").grid(row=1, column=0, columnspan=5)
            ttk.Label(root_che, text="[Remote branch]").grid(row=2, column=0, columnspan=5)

            arrange=0   # 원격 브랜치 나타내기
            if i>0 and curbr != None: # 원격 브랜치가 있을 때

                for i in cmd:
                    q,r=divmod(arrange,5)
                    if i == headbr[-1]:     # 헤드가 가리키는 원격 브랜치 색 바꾸기
                        style.configure("Custom.TButton", foreground="red")

                        head_remote = ttk.Button(root_che, text=i, style="Custom.TButton")
                        head_remote.grid(row=q+3, column=r)

                        self.b_branch_list.append(head_remote)
                    else:
                        self.b_branch_list.append(ttk.Button(root_che, text=i).grid(row=q+3, column=r))
                    
                    self.b_branch_list[len(self.b_branch_list)-1]
                    arrange += 1

                    
            else: # 원격 브랜치가 없을 때
                ttk.Label(root_che, text="There is no remote branch yet.", foreground="blue").grid(row=3, column=0, columnspan=5)
                ttk.Label(root_che, text=" ").grid(row=4, column=0, columnspan=5)          
                ttk.Label(root_che, text="[Local branch]").grid(row=5, column=0, columnspan=5)
            

            # 로컬 브랜치 나타내기
            q,r=divmod(arrange,5)
            ttk.Label(root_che, text=" ").grid(row=q+4, column=0, columnspan=5)
            ttk.Label(root_che, text="[Local branch]").grid(row=q+5, column=0, columnspan=5)
                
            arr=0
            for j in cmdL:
                q,rd=divmod(arrange,5)
                qd,r=divmod(arr,5)
                if j == curbr and curbr != None:
                    style.configure("Custom.TButton", foreground="red")

                    head_local = ttk.Button(root_che, text=j, command=lambda id=j: self.clicked_to_checkout("Y", id, root, root_che), style="Custom.TButton")
                    head_local.grid(row=q+6, column=r)

                    self.b_branch_list.append(head_local)
                else:
                    self.b_branch_list.append(ttk.Button(root_che, text=j, command=lambda id=j: self.clicked_to_checkout("N", id, root, root_che)).grid(row=q+6, column=r))

                self.b_branch_list[len(self.b_branch_list)-1]
                arrange += 1
                arr += 1
            
        else:
            self.b_branch_list=[]
        
    def clicked_to_merge(self, branch_name, root, root_mer):
        dir = self.getdir()

        try:
            result = subprocess.run(['git', 'merge', branch_name], cwd=dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result.check_returncode()  # 오류확인

            # merge가 정상적으로 수행되었을 때 git 메시지 출력(정상 merge, already up to date)
            git_message = result.stdout.strip().decode('utf-8')
            messagebox.showinfo("Git Merge Message", git_message)
            self.update_status()

            root_mer.destroy()  # 만약 실행 후 창을 닫고 싶으면 이 줄만 실행
            #self.rename_branch() # 만약 새로 고침을 하고 싶다면 이 줄도 추가 

            root.destroy()

        except subprocess.CalledProcessError as e:
            # 오류가 발생한 경우 오류 메시지창 띄우기
            if e.stderr:
                error_message = e.stderr.strip()
                messagebox.showerror("Error", error_message)
            else:
                if "non-zero exit status 1" in str(e):
                    messagebox.showerror("Merge Conflict Error", "CONFLICT (content): Merge conflict occured.\nThe merge will be canceled automatically by git merge --abort.")
                    
                    unmerged_s = subprocess.run(['git', 'status'], cwd=dir, stdout=subprocess.PIPE)
                    unmerged_s_d = unmerged_s.stdout.strip().decode('utf-8')
                    split_s = unmerged_s_d.split("\n\n")
                    pick_unmerged_p = "Unmerged paths:"
                    unmerged_p_l = [string for string in split_s if pick_unmerged_p in string] # list타입
                    split_unm = unmerged_p_l[0].split("\n")   # split_unm[1] 제외하고 모두 보여주기.
                    unmerged_path = split_unm[:1] + split_unm[2:]
                    
                    root_unm = tk.Tk()
                    style = ttk.Style(root_unm)
                    style.theme_use("clam")
                    root_unm.configure(bg=style.lookup('TFrame', 'background'))    
                    for n in range(len(unmerged_path)):
                        ttk.Label(root_unm, text=unmerged_path[n]).grid(row=n, column=0, padx=10, pady=5, sticky="w")
                    
                    msg_row = len(unmerged_path) + 1
                    ttk.Label(root_unm, text=" ").grid(row=msg_row, column=0, padx=10, sticky="w")
                    msg_text = "Fix these files directly to prevent conflicts.\nPlease press the merge button again after solving it."
                    ttk.Label(root_unm, text=msg_text).grid(row=msg_row+1, column=0, padx=10, pady=5, sticky="w")
                    subprocess.run(['git', 'merge', '--abort'], cwd=dir)


    def merge_branch(self, root):
        #branch 버튼을 클릭하면 새 창 띄우고 깃의 모든 원격 브랜치와 로컬 브랜치 리스트 버튼 보여주기
        if self.is_git_repo():
            cmd, cmdL, i, j, headbr, curbr = self.return_branch_list()
            # 브랜치 새 창 띄우기
            root_mer = tk.Tk()
            style = ttk.Style(root_mer)
            style.theme_use("clam")
            root_mer.configure(bg=style.lookup('TFrame', 'background'))
            ttk.Label(root_mer, text="Select one branch to merge with the current branch.").grid(row=0, column=0, columnspan=5)
            ttk.Label(root_mer, text=" ").grid(row=1, column=0, columnspan=5)
            ttk.Label(root_mer, text="[Remote branch]").grid(row=2, column=0, columnspan=5)

            arrange=0   # 원격 브랜치 나타내기
            if i>0 and curbr != None: # 원격 브랜치가 있을 때

                for i in cmd:
                    q,r=divmod(arrange,5)
                    if i == headbr[-1]:     # 헤드가 가리키는 원격 브랜치 색 바꾸기
                        style.configure("Custom.TButton", foreground="red")

                        head_remote = ttk.Button(root_mer, text=i, style="Custom.TButton")
                        head_remote.grid(row=q+3, column=r)

                        self.b_branch_list.append(head_remote)
                    else:
                        self.b_branch_list.append(ttk.Button(root_mer, text=i).grid(row=q+3, column=r))
                    
                    self.b_branch_list[len(self.b_branch_list)-1]
                    arrange += 1

                    
            else: # 원격 브랜치가 없을 때
                ttk.Label(root_mer, text="There is no remote branch yet.", foreground="blue").grid(row=3, column=0, columnspan=5)
                ttk.Label(root_mer, text=" ").grid(row=4, column=0, columnspan=5)          
                ttk.Label(root_mer, text="[Local branch]").grid(row=5, column=0, columnspan=5)
            

            # 로컬 브랜치 나타내기
            q,r=divmod(arrange,5)
            ttk.Label(root_mer, text=" ").grid(row=q+4, column=0, columnspan=5)
            ttk.Label(root_mer, text="[Local branch]").grid(row=q+5, column=0, columnspan=5)
                
            arr=0
            for j in cmdL:
                q,rd=divmod(arrange,5)
                qd,r=divmod(arr,5)
                if j == curbr and curbr != None:
                    style.configure("Custom.TButton", foreground="red")

                    head_local = ttk.Button(root_mer, text=j, command=lambda id=j: self.clicked_to_merge(id, root, root_mer), style="Custom.TButton")
                    head_local.grid(row=q+6, column=r)

                    self.b_branch_list.append(head_local)
                else:
                    self.b_branch_list.append(ttk.Button(root_mer, text=j, command=lambda id=j: self.clicked_to_merge(id, root, root_mer)).grid(row=q+6, column=r))

                self.b_branch_list[len(self.b_branch_list)-1]
                arrange += 1
                arr += 1
            
        else:
            self.b_branch_list=[]

    def update_branch_head(self):

        if self.is_git_repo():
            # 헤드가 가리키는 로컬 브랜치 나타내기
            style = ttk.Style()
            style.configure("Custom.TLabel", foreground="red")
            self.l_branch_head.configure(style="Custom.TLabel")
            cmd, cmdL, i, j, headbr, curbr = self.return_branch_list()
            if curbr == None:
                self.l_branch_head["text"] = "No branch yet"
            else:
                self.l_branch_head["text"] = "Head -> " + curbr
            self.l_branch_head.pack(side="right", padx=(0,4))
        else:
            self.l_branch_head.pack_forget()

    def log_need(self):
        if self.is_git_repo():
            self.b_log.pack(side="left",padx=(0,3))
        else:
            self.b_log.pack_forget()

    def log(self):
        def open_scrolls(width, height):
            root = tk.Tk()
            style = ttk.Style(root)
            style.theme_use("clam")
            root.configure(bg=style.lookup('TFrame', 'background'))
            container = ttk.Frame(root)
            canvas = tk.Canvas(container, width=max(min(800, width),320), height=max(min(500, height),200), bg=style.lookup('TFrame', 'background'))
            scrollbar_Y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollbar_X = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
            frame = ttk.Frame(canvas)
            frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_Y.set, xscrollcommand=scrollbar_X.set)
            scrollbar_Y.pack(side="right", fill="y")
            scrollbar_X.pack(side="bottom", fill="x")
            canvas.pack(side="bottom")
            container.pack()
            return frame
                    
        def spec(commit_hash):
            specs=[_ for _ in subprocess.run(['git', 'log', '-1', '-U', commit_hash], cwd=self._get_git_directory(), capture_output=True).stdout.decode().strip().split("\n")][:50]
            frame = open_scrolls(len(max(specs, key=len)*6), len(specs)*6)
            for i in range(len(specs)):
                ttk.Label(frame, text=specs[i]).grid(row=i+2, column=0, sticky="w")

        if self.is_git_repo():
            logs=[_[:_.find(" ")] for _ in subprocess.run(['git', 'log', '--pretty=oneline'], cwd=self._get_git_directory(), capture_output=True).stdout.decode().strip().split("\n")]
            glog=[_ for _ in subprocess.run(['git', 'log', '--pretty=oneline', '--graph'], cwd=self._get_git_directory(), capture_output=True).stdout.decode().strip().split("\n")]
            if len(glog) != 1 or glog[0] != '':
                frame = open_scrolls(len(max(glog, key=len)*6), len(glog)*6)
                for i in range(len(glog)):
                    graph=glog[i]
                    for j in range(len(logs)):
                        if logs[j] in glog[i]:
                            graph=glog[i][:glog[i].find(logs[j])]
                            ttk.Button(frame, text=logs[j][:7], command=(lambda d: lambda: spec(d))(logs[j])).grid(column=1, row=i, sticky="w")
                            ttk.Label(frame, text=glog[i][glog[i].find(logs[j])+40:glog[i].find(logs[j])+200]).grid(column=2, row=i, sticky="w")
                            break
                    label=ttk.Label(frame, text=graph, font=("Courier", 15))
                    label.grid(column=0, row=i, sticky="w")
            else:
                messagebox.showerror("Error", "No commits exist")

    def clone(self):
        repository_address = simpledialog.askstring("GitHub Clone", "Enter the GitHub repository address:")
        if repository_address != None:
            repository_type = messagebox.askyesno("Visibility", "Public?\nYes : public / No : private")
            if repository_type != None:
                if repository_address.find("https://github.com/") == 0:
                    if ".git" not in repository_address:
                        repository_address += ".git"

                    if repository_type == True:
                        # Public일때 실행하는 코드
                            if subprocess.run(['git', 'clone' , repository_address], cwd=self.getdir(), capture_output=True).returncode == 0:
                                self.update_status()
                            else:
                                messagebox.showerror("Clone Failed", "Failed to clone from public repository.")

                    elif repository_type == False:
                        # Private일때 실행하는 코드
                        ID = repository_address[19:19+repository_address[19:].find("/")]
                        found = "not found"
                        config_file = 'config.ini'
                        config = configparser.ConfigParser()
                        config.read(config_file)
                        for i in range(1,len(config)):
                            if config[str(i)]['GitHub_access_ID'] == ID:
                                found = str(i)   
                                break
                            
                        if found != "not found":
                            access_token = config[found]['GitHub_access_token']
                        else:
                            access_token = simpledialog.askstring("GitHub Clone", "Enter the access token:")
                        
                        if access_token != None:
                            repository_address_1 = repository_address[:repository_address.find("https://")+len("https://")]
                            repository_address_2 = repository_address[repository_address.find("https://")+len("https://"):]
                            repository_address_token = repository_address_1 + access_token + ":x-oauth-basic@" + repository_address_2
                            if subprocess.run(['git', 'clone' , repository_address_token], cwd=self.getdir(), capture_output=True).returncode == 0:
                                self.update_status()
                                if found == "not found":
                                    num=str(len(config))
                                    config[num] = {}
                                    config[num]['GitHub_access_ID'] = ID
                                    config[num]['GitHub_access_token'] = access_token
                                    with open(config_file, 'w') as config_file:
                                        config.write(config_file)
                            else:
                                messagebox.showerror("Clone Failed", "Failed to clone from private repository.")
                        
                    else:
                        messagebox.showerror("Invalid Repository Type", "Invalid repository type specified.")
                else:
                    messagebox.showerror("Invalid Repository Name", "Invalid repository Name.")


    def quit(self):
        """Destroy dialog."""
        self.destroy()
        if self.result:
            if isinstance(self.result, tuple):
                for path in self.result:
                    self._recent_files.add(path)
            else:
                self._recent_files.add(self.result)

    def _validate_save(self):
        """Validate selection in save mode."""
        name = self.entry.get()
        if name:
            ext = splitext(name)[-1]
            if not ext and not name[-1] == "/":
                # append default extension if none given
                name += self.defaultext
            if isabs(name):
                # name is an absolute path
                if exists(dirname(name)):
                    rep = True
                    if isfile(name):
                        rep = cst.askyesnocancel(_("Confirmation"),
                                                 _("The file {file} already exists, do you want to replace it?").format(file=name),
                                                 icon="warning")
                    elif isdir(name):
                        # it's a directory
                        rep = False
                        self.display_folder(name)
                    path = name
                else:
                    # the path is invalid
                    rep = False
            elif self.path_bar.winfo_ismapped():
                # we are not in the "recent files"
                path = join(self.history[self._hist_index], name)
                rep = True
                if exists(path):
                    if isfile(path):
                        rep = cst.askyesnocancel(_("Confirmation"),
                                                 _("The file {file} already exists, do you want to replace it?").format(file=name),
                                                 icon="warning")
                    else:
                        # it's a directory
                        rep = False
                        self.display_folder(path)
                elif not exists(dirname(path)):
                    # the path is invalid
                    rep = False
            else:
                # recently used file
                sel = self.click()
                if len(sel) == 1:
                    path = sel[0]
                    tags = self.right_tree.item(sel, "tags")
                    if ("folder" in tags) or ("folder_link" in tags):
                        rep = False
                        self.display_folder(path)
                    elif isfile(path):
                        rep = cst.askyesnocancel(_("Confirmation"),
                                                 _("The file {file} already exists, do you want to replace it?").format(file=name),
                                                 icon="warning")
                    else:
                        rep = True
                else:
                    rep = False

            if rep:
                self.result = realpath(path)
                self.quit()
            elif rep is None:
                self.quit()
            else:
                self.entry.delete(0, "end")
                self.entry.focus_set()

    def _validate_from_entry(self):
        """
        Validate selection from path entry in open mode.

        Return False if the entry is empty, True otherwise.
        """
        name = self.entry.get()
        if name:  # get file/folder from entry
            if not isabs(name) and self.path_bar.winfo_ismapped():
                # we are not in the "recent files"
                name = join(self.history[self._hist_index], name)
            if not exists(name):
                self.entry.delete(0, "end")
            elif self.mode == "openfile":
                if isfile(name):
                    if self.multiple_selection:
                        self.result = (realpath(name),)
                    else:
                        self.result = realpath(name)
                    self.quit()
                else:
                    self.display_folder(name)
                    self.entry.grid_remove()
                    self.entry.delete(0, "end")
            else:
                if self.multiple_selection:
                    self.result = (realpath(name),)
                else:
                    self.result = realpath(name)
                self.quit()
            return True
        else:
            return False

    def _validate_multiple_sel(self):
        """Validate selection in open mode with multiple selection."""
        sel = self.click()
        if self.mode == "openfile":
            if len(sel) == 1:
                sel = sel[0]
                tags = self.right_tree.item(sel, "tags")
                if ("folder" in tags) or ("folder_link" in tags):
                    self.display_folder(sel)
                else:
                    self.result = (realpath(sel),)
                    self.quit()
            elif len(sel) > 1:
                files = tuple(s for s in sel if "file" in self.right_tree.item(s, "tags"))
                files = files + tuple(realpath(s) for s in sel if "file_link" in self.right_tree.item(s, "tags"))
                if files:
                    self.result = files
                    self.quit()
                else:
                    self.right_tree.selection_remove(*sel)
        else:
            if sel:
                self.result = tuple(realpath(s) for s in sel)
            else:
                self.result = (realpath(self.history[self._hist_index]),)
            self.quit()

    def _validate_single_sel(self):
        """Validate selection in open mode without multiple selection."""
        sel = self.click()
        if self.mode == "openfile":
            if len(sel) == 1:
                sel = sel[0]
                tags = self.right_tree.item(sel, "tags")
                if ("folder" in tags) or ("folder_link" in tags):
                    self.display_folder(sel)
                else:
                    self.result = realpath(sel)
                    self.quit()
        elif self.mode == "opendir":
            if len(sel) == 1:
                self.result = realpath(sel[0])
            else:
                self.result = realpath(self.history[self._hist_index])
            self.quit()
        else:  # mode is "openpath"
            if len(sel) == 1:
                self.result = realpath(sel[0])
                self.quit()

    def validate(self, event=None):
        """Validate selection and store it in self.results if valid."""
        if self.mode == "save":
            self._validate_save()
        else:
            validation = self._validate_from_entry()
            if not validation:
                # the entry is empty
                if self.multiple_selection:
                    self._validate_multiple_sel()
                else:
                    self._validate_single_sel()