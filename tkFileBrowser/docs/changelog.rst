Changelog
=========

.. currentmodule:: tkfilebrowser

tkfilebrowser 2.4.0
-------------------

* Add "openpath" mode to the :class:`FileBrowser` to select both files and folders
* Add :meth:`askopenpathname` and :meth:`askopenpathnames` to select path(s) 

tkfilebrowser 2.3.1
-------------------

* Fix path bar navigation in Linux
* Show networked drives on Windows

tkfilebrowser 2.3.0
-------------------

* Make package compatible with Windows
* Set initial focus on entry in save mode 
    
tkfilebrowser 2.2.6
-------------------

* No longer reset path bar when clicking on a path button
* Fix bug caused by broken links

tkfilebrowser 2.2.5
-------------------

* Add compatibility with Tk < 8.6.0 (requires :mod:`PIL.ImageTk`)
* Add desktop icon in shortcuts
* Fix handling of spaces in bookmarks 
* Fix bug due to spaces in recent file names
    
tkfilebrowser 2.2.4
-------------------
* Fix bug in desktop folder identification

tkfilebrowser 2.2.3
-------------------

* Fix :obj:`FileNotFoundError` if initialdir does not exist
* Add Desktop in shortcuts (if found)
* Improve filetype filtering

tkfilebrowser 2.2.2
-------------------

* Fix :obj:`ValueError` in after_cancel with Python 3.6.5

tkfilebrowser 2.2.1
-------------------

* Fix __main__.py for python 2

tkfilebrowser 2.2.0
-------------------

* Use :mod:`babel` instead of locale in order not to change the locale globally
* Speed up (a little) folder content display
* Improve example: add comparison with default dialogs
* Add select all on Ctrl+A if multiple selection is enabled
* Disable folder creation button if the user does not have write access
* Improve extension management in "save" mode

tkfilebrowser 2.1.1
-------------------

* Fix error if :obj:`LOCAL_PATH` does not exists or is not writable

tkfilebrowser 2.1.0
-------------------

* Add compatibility with :mod:`tkinter.filedialog` keywords *master* and *defaultextension*
* Change look of filetype selector
* Fix bugs when navigating without displaying hidden files
* Fix color alternance bug when hiding hidden files
* Fix setup.py
* Hide suggestion drop-down when nothing matches anymore

tkfilebrowser 2.0.0
-------------------

* Change package name to :mod:`tkfilebrowser` to respect `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_
* Display error message when an issue occurs during folder creation
* Cycle only through folders with key browsing in "opendir" mode
* Complete only with folder names in "opendir" mode
* Fix bug: grey/white color alternance not always respected
* Add __main__.py with an example
* Add "Recent files" shortcut
* Make the text of the validate and cancel buttons customizable
* Add possibility to disable new folder creation
* Add python 2 support
* Add horizontal scrollbar

tkFileBrowser 1.1.2
-------------------

* Add tooltips to display the full path of the shortcut if the mouse stays long enough over it.
* Fix bug: style of browser treeview applied to parent

tkFileBrowser 1.1.1
-------------------

* Fix bug: key browsing did not work with capital letters
* Add specific icons for symlinks
* Add handling of symlinks, the real path is returned instead of the link path

tkFileBrowser 1.1.0
-------------------

* Fix bug concerning the *initialfile* argument
* Add column sorting (by name, size, modification date)

tkFileBrowser 1.0.1
-------------------

* Set default :class:`Filebrowser` parent to :obj:`None` as for the usual filedialogs and messageboxes.

tkFileBrowser 1.0.0
-------------------

* Initial version
