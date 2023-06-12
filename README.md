# GUI_Git_Manager_OSS_Team_25



## Project Description
Our project is a git browser that adds a git function to the file browser, tkfilebrowser.</br>
(version1:tag v1) In addition to the existing file browsing function, simple git functions were additionally implemented so that a git repository could be created locally and projects could be carried out using git.</br>
(version2:tag v2) Also, the file browser was upgraded to make git work easier by adding the Branch management function, the ability to show commit history using the git log button, and the git clone function.

The language was implemented using python.


## How to Execute

- The following execution methods are based on Windows 10.
- The project was implemented as of Python 3.11.
- The program was implemented in Visual Studio Code.


#### Install and prepare execution
1. Go to the GUI_Git_Manager_OSS_Team_25 repository and press the Code -> Download ZIP button to download and extract the file wherever you want.
2. Install python 3.11 including pip. (If you don't do custom, pip is usually installed automatically.)
3. Turn on the cmd window
- ```pip install tkfilebrowser```
- ```pip install pywin32```
</br>Download the required files by entering the commands in turn.  (If there is a problem, please solve it through ["Reference in case of a problem"](#Reference-in-case-of-a-problem) 1 and 2.)



#### How to run
1. In Visual Studio Code, Open Folder -> open the downloaded file from Git Repository -> select \GUI_Git_Manager_OSS_Team_25\tkFileBrowser to open it.
2. (Prepare to run Python in VS code)Extensions -> Search Python -> Python (2023.8.0) install.
3. There are four folders in Explorer: docs, tests, tkfilebrowser, and tkfilebrowser_custom. Open \_\_main\_\_.py in the tkfilebrowser_custom folder.
4. Run as Ctrl+F5 or run -> run without debugging.


#### How to use
##### 1) File Browser Features
Double-click a folder: You have entered that folder.</br>
Click File: Status to write git function to that file.

##### 2) git function
###### 1. git init
: The button is active where the .git folder does not exist.
  
- how to use? Press the git init button while in the folder where I want to create the git repository (the folder where I want to write the git init command).
  
- Caution: You must double-click the folder in which you want to create the Git repository. A single click will execute the command to the current folder, the parent folder of the clicked folder, so you must double-click to enter it and press the button. Also, like the original git, it's possible for our program to go side by side from one folder where the .git folder is located to create a .git, but I don't recommend using this. This is because the expressions of upper .git and lower .git are ambiguous due to the nature of gui implementation.

###### 2. git add

- how to use? Press the git add button within a folder containing the .git directory

- If you click on a file in the "modified" or "untracked" state and press the git add button, only the clicked file will be added using the "git add ".
If you press git add without selecting a file, it will perform the git add . feature, adding all files in the folder. (First, it will ask through a message window if you want to add all files, and if you choose "yes," it will perform git add.)


###### 3. git commit
: The button is active when you click on a file in the "staged" state.

- how to use? After entering the git repository (the folder with the .git), click on any file in the "staged" state and press the commit button. This will bring up a dialog box showing the staged changes and asking if you want to commit the changes in the staging area.
  - Press the "yes" button to proceed. A commit message window will appear, where you should enter the commit message, and then press the OK button.
  - If you don't enter a commit message, an error message will be displayed.
  - If you don't want to commit while the commit message window is open, you can simply press the Cancel button to exit the window.

- Note: The default option for committing (git commit -m) commits all the files in the staging area at once. The feature to selectively commit specific files is not implemented in this case. Therefore, even if you click on a specific file and press the commit button, if there are other added files, they will be committed together.

###### 4. git restore

: The button is active when you click on a file in the "modified" state.

- how to use? If you click on a file that has modifications and press the git restore button, it will revert the changes made to the file, effectively undoing the modifications made since the last commit. The file will transition from the "modified" state to the "unmodified" state, representing the state it was in at the latest commit.

###### 5. git restore —staged
: The button is active when you click on a file in the "staged" state.

- how to use? If you click on a file that has been added (in the staged state) but you want to revert it back to the state before the add operation, pressing the button will undo the git add operation. The file will transition from the "staged" state to the "modified" state.

###### 6. git mv

- How to use? If you click on a file within a folder that contains the .git directory and press the git_mv button, you can change the name or path of the selected file.

###### 7. git rm

- How to use? If you click on a file within a folder that contains the .git directory and press the git_rm button, the selected file will be removed from the Git repository.

###### 8. git rm --cached 버튼

- how to use? If you click on a file within a folder that contains the .git directory and the file is in the staged or committed state, and then press the git rm --cached button, the file will be removed from the staging area. The file will still exist in your local working directory, but it will be untracked by Git.

###### 9. git status 기능과 관련된 버튼들

- how to use? When you enter a file or folder inside a Git repository, the status of the file or folder is indicated by the git status column. Pressing the git status button will sort the git status entries. Clicking the update_status button in the top right corner will refresh the displayed status.


###### 10. status에 따른 버튼 활성화 기능 구현

- how to use? This is a function that displays buttons based on the Git status. As you choose a file or enter a folder, the Git status specific to that file or folder will be displayed, and corresponding buttons will appear based on those Git status.


#### Reference in case of a problem
1. Even after installing Python, including pip, you may encounter the error message "'pip' is not recognized as an internal or external command, operable program, or batch file" in the command prompt.

- Register pip in the system environment variables. (Control Panel -> System -> Advanced System Settings -> Environment Variables -> Add Python path and Python path\Scripts to the "Path" variable under System Variables)
</br>

<img width="842" alt="pip1" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/76bc6484-74b8-406f-a344-24d57dd77d5d"></img></br>
Click on "System and Security" in the Control Panel.</br></br>


<img width="837" alt="pip2" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/1b7e21e3-4fb8-4028-b006-2b67123377f4"></img></br>
Click on "System"</br></br>


<img width="308" alt="pip3" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/927dd381-bf59-4af1-a756-89cded334d74"></img></br>
Click on "Advanced System Settings"</br></br>


<img width="340" alt="pip4" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/e9a9a621-df1e-4ac8-bab0-29c569a6dfd6"></img></br>
Click on "Environment Variables"</br></br>


<img width="319" alt="pip5" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/63369aeb-960f-4e9d-a24e-f419dcecf2fd"></img></br>
Double-click on the "Path" entry under the "System Variables" section at the bottom.</br></br>


<img width="454" alt="pip6" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/e71e78f0-7f94-4559-990b-d446c8afa269"></img></br>
Copy your Python path and add it, along with the Python path\Scripts, as two separate entries.</br></br>



- Afterwards, open a new command prompt window and execute the above command.</br>
["Install and prepare execution"](#Install-and-prepare-execution) Try number 3 again.</br></br></br>


2. To update pip when a specific module fails to download, please enter the following command to upgrade pip to the latest version:</br>
```pip install --update pip```
