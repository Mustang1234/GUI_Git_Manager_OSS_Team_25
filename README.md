# GUI_Git_Manager_OSS_Team_25






## How to Execute

- 다음 실행 방법은 윈도우10 을 기준으로 작성되었습니다.
- 프로젝트는 파이썬 3.11 버전을 기준으로 구현되었습니다.  
- 해당 프로그램은 Visual Studio Code에서 구현되었습니다.


#### 설치 및 실행 준비
1. GUI_Git_Manager_OSS_Team_25 레포지토리로 가서 Code -> Download ZIP 버튼을 눌러 원하는 곳에 파일을 다운로드한 후 압축 해제합니다.
2. pip를 포함한 python 3.11을 설치합니다. (custom을 따로 하지 않는다면 보통 pip는 자동으로 설치됩니다.)
3. cmd 창을 켜고
```pip install tkfilebrowser```
```pip install pywin32```
명령어를 차례로 입력해 필요한 파일을 다운로드합니다.  (만약 문제가 발생한다면 ["문제 발생 시 참고사항"](#문제-발생-시-참고사항) 1번, 2번을 통해 해결해주세요.) 



#### 실행 방법
1. Visual Studio Code에서 Open Folder -> 깃 레포에서 다운받은 파일을 열고 \GUI_Git_Manager_OSS_Team_25\tkFileBrowser을 선택해서 엽니다.
2. Extentions -> 파이썬 검색 -> Python (2023.8.0) install로 vs code에서 파이썬을 실행할 준비를 합니다.
3. Explorer에 docs, tests, tkfilebrowser, tkfilebrowser_custom 이렇게 4개의 폴더가 나오는데, tkfilebrowser_custom 폴더에서 \_\_main\_\_.py를 엽니다.
4. Ctrl+F5 또는 run -> run without Debugging으로 실행합니다.  


#### 사용 방법
##### 1) 파일 브라우저 기능
폴더 더블 클릭 : 해당 폴더로 들어가짐.
파일 클릭 : 해당 파일에게 git 기능을 쓸 수 있는 상태

##### 2) git 기능
###### 1. git init 버튼
  : .git 폴더가 없는 곳에 버튼이 활성화 됨.
  
  how to use? 내가 git repository를 만들고 싶은 폴더 (git init 명령을 쓰고싶은 폴더) 내에 들어가 있는 상태로 해당 버튼을 누르기. 
  
  주의: git repository를 만들고 싶은 폴더를 더블 클릭 후 들어가 있는 상태에서 해야 함. 한 번만 클릭하면 클릭한 폴더의 상위 폴더인 현재 폴더로 명령이 실행되므로 반드시 더블클릭을 하여 들어간 후 버튼을 눌러야 함. 또한 원래의 git과 마찬가지로 .git폴더가 있는 폴더에 나란히 있는 다른 폴더 안으로 들어가서 .git을 만드는게 가능한 것처럼 우리 프로그램에서도 가능하지만 이런 사용은 권장하지 않음. gui구현 특성상 상위 .git과 하위 .git의 표현이 모호하기 때문.

###### 2. git add 버튼

how to use? .git이 있는 폴더 안에서

modified나 untracked 상태의 파일을 마우스로 클릭하고 git add 버튼을 누르면 클릭한 파일만 git add
파일을 선택하지 않고 git add를 누르면 폴더의 전체 파일을 git add .(먼저 메시지 창을 통해 전체 파일을 모두 add할 것인지 물어보고, yes를 누르면 git add한다.)

###### 3. git commit 버튼

: staged상태인 파일을 눌렀을 때 버튼이 활성화 됨.

how to use? 내가 커밋하고싶은 git repository(.git이 있는 폴더)에 들어가서 staged 상태의 파일 중 아무거나 클릭한 후 commit버튼을 누르면 staged changes가 뜨면서 staging area에 있는 변화들을 커밋을 할 것인지 확인하는 창이 뜬다. yes버튼을 누르면 커밋메세지창이 뜨고 거기에 커밋메세지를 입력하고 OK버튼을 누르기. 커밋메세지를 입력하지 않은 경우 에러메세지가 뜸. 커밋메세지창이 띄워진 상태에서 커밋을 하고 싶지 않다면 Cancle버튼을 눌러서 창을 나가면 됨.

주의: 기본적인 옵션의 커밋 (git commit –m) 은 staging area에 있는 파일들을 한 번에 커밋하므로 해당 커밋 버튼으로 특정 파일만 선택에서 commit을 할 수 없게 구현했음. 따라서 특정 파일을 클릭 후 commit버튼을 누르더라도 다른 add된 파일이 있다면 같이 commit 됨.

###### 4. git restore

: modified상태인 파일을 눌렀을 때 버튼이 활성화 됨.

how to use? 수정을 취소하고 싶은 파일을 클릭 후 해당 버튼을 누르면 아직 add전 수정만 한 상태에서 최근 커밋 상태로 돌아가게 된다. (수정 취소) 
즉 modified -> unmodified(committed) 상태로 변화하게 된다. 

###### 5. git restore —staged
: staged상태인 파일을 눌렀을 때 버튼이 활성화 됨.

how to use? add하기 전의 상태로 돌아가고 싶은 파일을 클릭 후 해당 버튼을 누르면 add 한 상태에서 add 전 수정만 한 상태로 돌아가게 된다. (add 취소) 
즉 staged -> modified 상태로 변화하게 된다.

###### 6. git mv

How to use? .git이 포함된 폴더에서 파일을 클릭하고 git_mv 버튼을 누른다. 그러면 선택한 파일의 이름이나 경로를 변경할 수 있다.

###### 7. git rm

How to use? : .git이 포함된 폴더에서 파일을 클릭하고 git_rm 버튼을 누른다. 그러면 선택한 파일이 git 저장소에서 제거된다.

###### 8. git rm --cached 버튼

how to use?
.git이 있는 폴더 안에서 staged나 committed 상태의 파일을 마우스로 클릭하고 git rm --cached 버튼을 누르면 클릭한 파일에 대해서 기능이 수행된다.

###### 9. git status 기능과 관련된 버튼들

how to use? 깃 레포지토리 안의 파일이나 폴더에 들어가면 파일이나 폴더의 상태를 git status column을 통해 git status를 나타낸다. git status버튼을 누르면 git status가 정렬된다. 상단 오른쪽의update_status 버튼을 누르면 status 들이 새로고침된다.

###### 10. status에 따른 버튼 활성화 기능 구현
how to use? status에 따라서 누를 수 있는 버튼들을 표시해주는 함수이다. 수정하고 싶은 파일을 선택하거나 폴더에 들어가면 그 파일/폴더에 맞는 상태들이 나타난다. 위의 깃 기능에 따라서 상태에 따라서 버튼이 나타난다.


###### 문제 발생 시 참고사항
1. pip를 포함한 python을 설치했음에도 cmd 창에서 "'pip'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다." 라는 메세지가 나올 수 있습니다.
- pip를 시스템 환경 변수에 등록하세요. (제어판->시스템->고급시스템 설정->환경변수->시스템 변수의 path에 파이썬 경로와 파이썬 경로\Scripts 2개 추가)
</br>

<img width="842" alt="pip1" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/76bc6484-74b8-406f-a344-24d57dd77d5d"></img></br>
제어판에서 시스템 및 보안 클릭</br></br>


<img width="837" alt="pip2" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/1b7e21e3-4fb8-4028-b006-2b67123377f4"></img></br>
시스템 클릭</br></br>


<img width="308" alt="pip3" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/927dd381-bf59-4af1-a756-89cded334d74"></img></br>
고급시스템 설정 클릭</br></br>


<img width="340" alt="pip4" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/e9a9a621-df1e-4ac8-bab0-29c569a6dfd6"></img></br>
환경변수 클릭</br></br>


<img width="319" alt="pip5" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/63369aeb-960f-4e9d-a24e-f419dcecf2fd"></img></br>
하단 시스템 변수의 Path 항목 더블클릭</br></br>


<img width="454" alt="pip6" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/e71e78f0-7f94-4559-990b-d446c8afa269"></img></br>
본인의 파이썬 경로를 복사해와서 파이썬 경로, 파이썬경로\scripts 두 개를 추가</br></br>



- 그 다음 cmd 창을 새로 켜서 위의 명령어를 실행합니다.</br>
["설치 및 실행 준비"](#설치-및-실행-준비) 3번 다시 시도하기.</br></br></br>


2. 특정 모듈이 다운로드 되지 않을 때 해당 명령어를 입력하여 pip를 최신화 해주세요.  </br>
```pip install --update pip```
