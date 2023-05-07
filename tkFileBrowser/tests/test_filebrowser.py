from tkfilebrowser.filebrowser import FileBrowser
from tests import BaseWidgetTest, TestEvent
try:
    import ttk
except ImportError:
    from tkinter import ttk
import os
from pynput.keyboard import Key, Controller


class TestFileBrowser(BaseWidgetTest):
    def test_filebrowser_openpath(self):
        # --- multiple selection
        path = os.path.expanduser('~')
        fb = FileBrowser(self.window, initialdir=path, initialfile="test", mode="openpath",
                         multiple_selection=True,
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        fb.event_generate('<Control-a>')
        self.window.update()
        self.window.update_idletasks()
        fb.validate()
        walk = os.walk(path)
        root, dirs, files = walk.send(None)
        res = list(fb.get_result())
        res.sort()
        dirs = [os.path.realpath(os.path.join(root, d)) for d in dirs]
        files = [os.path.realpath(os.path.join(root, f)) for f in files]
        paths = dirs + files
        paths.sort()
        self.assertEqual(res, paths)
        # --- single selection
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openpath",
                         multiple_selection=False,
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.validate()
        self.assertEqual(fb.get_result(), '')
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openpath",
                         multiple_selection=False,
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        files = fb.right_tree.tag_has('file')
        if files:
            fb.right_tree.selection_set(files[0])
            fb.validate()
            self.assertTrue(os.path.isfile(fb.get_result()))
        else:
            fb.validate()
            self.assertEqual(fb.get_result(), '')
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openpath",
                         multiple_selection=False,
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        dirs = fb.right_tree.tag_has('folder')
        if dirs:
            fb.right_tree.selection_set(dirs[0])
            fb.validate()
            self.assertTrue(os.path.isdir(fb.get_result()))
        else:
            fb.validate()
            self.assertEqual(fb.get_result(), '')

    def test_filebrowser_opendir(self):
        # --- multiple selection
        path = os.path.expanduser('~')
        fb = FileBrowser(self.window, initialdir=path, initialfile="test", mode="opendir",
                         multiple_selection=True, defaultext=".png",
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        fb.event_generate('<Control-a>')
        self.window.update()
        self.window.update_idletasks()
        fb.validate()
        walk = os.walk(path)
        root, dirs, _ = walk.send(None)
        res = list(fb.get_result())
        res.sort()
        dirs = [os.path.realpath(os.path.join(root, d)) for d in dirs]
        dirs.sort()
        self.assertEqual(res, dirs)
        # --- single selection
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="opendir",
                         multiple_selection=False, defaultext=".png",
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.validate()
        self.assertTrue(os.path.isdir(fb.get_result()))

    def test_filebrowser_openfile(self):
        # --- multiple selection
        path = os.path.expanduser('~')
        fb = FileBrowser(self.window, initialdir=path, initialfile="test", mode="openfile",
                         multiple_selection=True, defaultext=".png",
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        fb.event_generate('<Control-a>')
        self.window.update()
        self.window.update_idletasks()
        fb.validate()
        walk = os.walk(path)
        root, _, files = walk.send(None)
        res = list(fb.get_result())
        res.sort()
        files = [os.path.realpath(os.path.join(root, f)) for f in files]
        files.sort()
        self.assertEqual(res, files)
        # --- single selection
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openfile",
                         multiple_selection=False, defaultext="",
                         title="Test", filetypes=[("PNG", '*.png'), ('ALL', '*')],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.validate()
        self.assertEqual(fb.get_result(), '')
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openfile",
                         multiple_selection=False, defaultext="",
                         title="Test", filetypes=[("PNG", '*.png'), ('ALL', '*')],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        fb.validate()
        self.assertEqual(fb.get_result(), '')
        fb = FileBrowser(self.window, initialdir=".", initialfile="test", mode="openfile",
                         multiple_selection=False, defaultext="",
                         title="Test", filetypes=[],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=False)
        self.window.update()
        # walk = os.walk(os.path.abspath("."))
        # root, _, files = walk.send(None)
        files = fb.right_tree.tag_has('file')
        if files:
            fb.right_tree.selection_set(files[0])
            fb.validate()
            self.assertTrue(os.path.isfile(fb.get_result()))
        else:
            fb.validate()
            self.assertEqual(fb.get_result(), '')

    def test_filebrowser_save(self):
        fb = FileBrowser(self.window, initialdir="/", initialfile="test", mode="save",
                         multiple_selection=True, defaultext=".png",
                         title="Test", filetypes=[("PNG", '*.png'), ('ALL', '*')],
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=True)
        self.window.update()
        fb.validate()
        self.assertEqual(os.path.abspath(fb.get_result()),
                         os.path.abspath('/test.png'))
        fb = FileBrowser(self.window, initialdir="/", initialfile="test.png", mode="save",
                         filetypes=[("PNG", '*.png|*.PNG'), ("JPG", '*.jpg|*.JPG'),
                                    ('ALL', '*')])
        self.window.update()
        self.assertEqual(fb.entry.get(), "test.png")
        fb.filetype.set('JPG')
        self.window.update()
        self.assertEqual(fb.entry.get(), "test.jpg")
        fb.filetype.set('ALL')
        self.window.update()
        self.assertEqual(fb.entry.get(), "test.jpg")
        fb.filetype.set('PNG')
        self.window.update()
        self.assertEqual(fb.entry.get(), "test.png")
        fb.entry.delete(0, 'end')
        fb.entry.insert(0, "test.JPG")
        fb.filetype.set('JPG')
        self.window.update()
        self.assertEqual(fb.entry.get(), "test.JPG")

    def test_filebrowser_keybrowse(self):
        # --- openfile
        fb = FileBrowser(self.window, initialdir="/", mode="openfile",
                         multiple_selection=True)
        if not fb.hide:
            fb.toggle_hidden()
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        ch = fb.right_tree.get_children('')
        letters = [fb.right_tree.item(c, 'text')[0].lower() for c in ch]
        i = 65
        while chr(i).lower() in letters:
            i += 1
        letter = chr(i).lower()
        keyboard = Controller()
        if letter.isalnum():
            fb.right_tree.focus_force()
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            self.assertTrue(fb.key_browse_entry.winfo_ismapped())
            self.assertEqual(fb.key_browse_entry.get().lower(), letter)
            fb.right_tree.event_generate('<Escape>')
            self.window.update()
            self.assertFalse(fb.key_browse_entry.winfo_ismapped())
        if ch:
            fb.right_tree.focus_force()
            letter = fb.right_tree.item(ch[0], 'text')[0]
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            self.assertTrue(fb.key_browse_entry.winfo_ismapped())
            self.assertEqual(fb.key_browse_entry.get().lower(), letter)
            self.assertEqual(fb.right_tree.selection(), (ch[0],))
            l = [c for c in ch if fb.right_tree.item(c, 'text')[0] == letter]
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Down>')
            self.window.update()
            if len(l) > 1:
                self.assertEqual(tuple(fb.right_tree.selection()), (l[1],))
            else:
                self.assertEqual(tuple(fb.right_tree.selection()), (l[0],))
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Up>')
            self.window.update()
            self.assertEqual(tuple(fb.right_tree.selection()), (l[0],))
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Escape>')
            self.window.update()
            self.assertFalse(fb.key_browse_entry.winfo_ismapped())
            fb.right_tree.focus_force()
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            fb.right_tree.event_generate('<Return>')
            self.window.update()
            item = os.path.realpath(ch[0])
            if os.path.isdir(item):
                self.assertEqual(fb.history[-1], ch[0])
            else:
                self.assertEqual(fb.get_result(), (item,))

        # --- opendir
        fb = FileBrowser(self.window, initialdir="/", mode="opendir",
                         multiple_selection=True)
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        ch = fb.right_tree.tag_has('folder')
        letters = [fb.right_tree.item(c, 'text')[0].lower() for c in ch]
        i = 65
        while chr(i).lower() in letters:
            i += 1
        letter = chr(i).lower()
        if letter.isalnum():
            fb.right_tree.focus_force()
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            self.assertTrue(fb.key_browse_entry.winfo_ismapped())
            self.assertEqual(fb.key_browse_entry.get(), letter)
            fb.right_tree.event_generate('<Return>')
            self.window.update()
            self.assertEqual(fb.get_result(), (os.path.abspath('/'),))
        fb = FileBrowser(self.window, initialdir="/", mode="opendir",
                         multiple_selection=True)
        self.window.update()
        fb.right_tree.focus_force()
        if ch:
            letter = fb.right_tree.item(ch[-1], 'text')[0].lower()
            l = [c for c in ch if fb.right_tree.item(c, 'text')[0].lower() == letter]
            fb.right_tree.focus_force()
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            self.assertTrue(fb.key_browse_entry.winfo_ismapped())
            self.assertEqual(fb.key_browse_entry.get(), letter)
            self.assertEqual(fb.right_tree.selection(), (l[0],))
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Down>')
            self.window.update()
            if len(l) > 1:
                self.assertEqual(tuple(fb.right_tree.selection()), (l[1],))
            else:
                self.assertEqual(tuple(fb.right_tree.selection()), (l[0],))
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Up>')
            self.window.update()
            self.assertEqual(tuple(fb.right_tree.selection()), (l[0],))
            fb.key_browse_entry.focus_force()
            fb.key_browse_entry.event_generate('<Escape>')
            self.window.update()
            self.assertFalse(fb.key_browse_entry.winfo_ismapped())
            fb.right_tree.focus_force()
            keyboard.press(letter)
            keyboard.release(letter)
            self.window.update()
            fb.right_tree.event_generate('<Return>')
            self.window.update()
            self.assertEqual(fb.get_result(), (l[0],))

        # --- arrow nav
        fb = FileBrowser(self.window, initialdir="/", mode="opendir",
                         multiple_selection=True)
        self.window.update()
        fb.right_tree.focus_force()
        self.window.update()
        fb.event_generate('<Left>')
        self.window.update()
        fb.left_tree.focus_force()
        fb.event_generate('<Up>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Left>')
        self.window.update()
        fb.left_tree.focus_force()
        fb.event_generate('<Down>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Down>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Alt-Left>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Alt-Right>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Alt-Up>')
        self.window.update()
        fb.right_tree.focus_force()
        fb.event_generate('<Alt-Down>')
        self.window.update()

    def test_filebowser_foldercreation(self):
        initdir = os.path.abspath('/')
        fb = FileBrowser(self.window, initialdir=initdir,
                         foldercreation=True)
        self.window.update()
        self.assertTrue(fb.b_new_folder.winfo_ismapped())
        self.assertIs('disabled' not in fb.b_new_folder.state(), os.access(initdir, os.W_OK))
        fb.display_folder(os.path.expanduser('~'))
        self.window.update()
        self.assertTrue(fb.b_new_folder.winfo_ismapped())
        self.assertFalse('disabled' in fb.b_new_folder.state())
        fb.left_tree.selection_clear()
        fb.left_tree.selection_set('recent')
        self.window.update()
        self.assertFalse(fb.b_new_folder.winfo_ismapped())

    def test_filebrowser_sorting(self):
        fb = FileBrowser(self.window, initialdir="/",
                         multiple_selection=True, defaultext=".png",
                         title="Test", filetypes=[], mode="opendir",
                         okbuttontext=None, cancelbuttontext="Cancel",
                         foldercreation=True)
        self.window.update()
        walk = os.walk(os.path.abspath('/'))
        root, dirs, files = walk.send(None)
        dirs = [os.path.join(root, d) for d in dirs]
        files = [os.path.join(root, f) for f in files]

        # --- sort by name
        fb._sort_files_by_name(True)
        self.window.update()
        ch = fb.right_tree.get_children()
        dirs.sort(reverse=True)
        files.sort(reverse=True)
        self.assertEqual(ch, tuple(dirs) + tuple(files))

        fb._sort_files_by_name(False)
        self.window.update()
        ch = fb.right_tree.get_children()
        dirs.sort()
        files.sort()
        self.assertEqual(ch, tuple(dirs) + tuple(files))

        # --- sort by size
        fb._sort_by_size(False)
        self.window.update()
        ch = fb.right_tree.get_children()
        files.sort(key=os.path.getsize)
        self.assertEqual(ch, tuple(dirs) + tuple(files))
        fb._sort_by_size(True)
        ch = fb.right_tree.get_children()
        files.sort(key=os.path.getsize, reverse=True)
        self.assertEqual(ch, tuple(dirs) + tuple(files))

        # --- sort by date
        fb._sort_by_date(False)
        self.window.update()
        ch = fb.right_tree.get_children()
        dirs.sort(key=lambda d: os.path.getmtime(d))
        files.sort(key=lambda f: os.path.getmtime(f))
        self.assertEqual(ch, tuple(dirs) + tuple(files))

        fb._sort_by_date(True)
        self.window.update()
        ch = fb.right_tree.get_children()
        dirs.sort(key=os.path.getmtime, reverse=True)
        files.sort(key=os.path.getmtime, reverse=True)
        self.assertEqual(ch, tuple(dirs) + tuple(files))

        # --- sort by location
        fb.left_tree.selection_clear()
        fb.left_tree.selection_set('recent')
        self.window.update()
        locations = list(fb.right_tree.get_children())
        fb._sort_by_location(True)
        self.window.update()
        ch = fb.right_tree.get_children()
        locations.sort(reverse=True)
        self.assertEqual(ch, tuple(locations))

        fb._sort_by_location(False)
        self.window.update()
        ch = fb.right_tree.get_children()
        locations.sort()
        self.assertEqual(ch, tuple(locations))

    def test_filebrowser_on_selection(self):
        path = os.path.expanduser('~')
        fb = FileBrowser(self.window, initialdir=path, mode="opendir")
        fb.focus_force()
        fb.event_generate("<Control-l>")
        self.window.update()
        self.assertTrue(fb.entry.winfo_ismapped())
        self.assertEqual(fb.entry.get(), '')
        ch = fb.right_tree.tag_has('folder')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(os.path.abspath(fb.entry.get()),
                             os.path.abspath(os.path.join(fb.right_tree.item(ch[0], 'text'), '')))
        fb.focus_force()
        fb.event_generate("<Control-l>")
        self.window.update()
        self.assertFalse(fb.entry.winfo_ismapped())
        fb.focus_force()
        fb.event_generate("<Control-l>")
        self.window.update()
        ch = fb.right_tree.tag_has('file')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(fb.entry.get(),
                             '')
        fb = FileBrowser(self.window, initialdir=path, mode="openfile")
        fb.focus_force()
        fb.event_generate("<Control-l>")
        self.window.update()
        self.assertTrue(fb.entry.winfo_ismapped())
        self.assertEqual(fb.entry.get(), '')
        ch = fb.right_tree.tag_has('folder')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(os.path.abspath(fb.entry.get()),
                             os.path.abspath(os.path.join(fb.right_tree.item(ch[0], 'text'), '')))
        ch = fb.right_tree.tag_has('file')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(fb.entry.get(),
                             fb.right_tree.item(ch[0], 'text'))
        fb = FileBrowser(self.window, initialdir=path, mode="save")
        self.assertTrue(fb.entry.winfo_ismapped())
        self.assertEqual(fb.entry.get(), '')
        ch = fb.right_tree.tag_has('folder')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(fb.entry.get(),
                             '')
        ch = fb.right_tree.tag_has('file')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(fb.entry.get(),
                             fb.right_tree.item(ch[0], 'text'))
        fb.left_tree.selection_clear()
        fb.left_tree.selection_set('recent')
        self.window.update()
        ch = fb.right_tree.tag_has('file')
        if ch:
            fb.right_tree.selection_clear()
            fb.right_tree.selection_set(ch[0])
            self.window.update()
            self.assertEqual(fb.entry.get(),
                             ch[0], 'text')
