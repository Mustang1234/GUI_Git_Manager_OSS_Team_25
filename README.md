# GUI_Git_Manager_OSS_Team_25






## How to Execute

- 다음 실행 방법은 윈도우를 기준으로 작성되었습니다.
- 프로젝트는 파이썬 3.11 버전을 기준으로 구현되었습니다.  
- 해당 프로그램은 Visual Studio Code에서 구현되었습니다.


#### 설치 및 실행 준비
1. GUI_Git_Manager_OSS_Team_25 레포지토리로 가서 Code -> Download ZIP 버튼을 눌러 원하는 곳에 파일을 다운로드한 후 압축 해제합니다.
2. pip를 포함한 python을 설치합니다. (custom을 따로 하지 않는다면 보통 pip는 자동으로 설치됩니다.)
3. cmd 창을 켜고
  - pip install tkfilebrowser
  - pip install pywin32  
명령어를 차례로 입력해 필요한 파일을 다운로드합니다.  (만약 문제가 발생한다면 ["문제 발생 시 참고사항"](#문제-발생-시-참고사항) 1번을 통해 해결해주세요.) 



#### 실행 방법
1. Visual Studio Code에서 Open Folder -> 깃 레포에서 다운받은 파일을 열고 \GUI_Git_Manager_OSS_Team_25\tkFileBrowser을 선택해서 엽니다.
2. Extentions -> 파이썬 검색 -> Python (2023.8.0) install로 vs code에서 파이썬을 실행할 준비를 합니다.
3. Explorer에 docs, tests, tkfilebrowser, tkfilebrowser_custom 이렇게 4개의 폴더가 나오는데, tkfilebrowser_custom 폴더에서 \_\_main\_\_.py를 엽니다.
4. Ctrl+F5 또는 run -> run without Debugging으로 실행합니다.  



###### 문제 발생 시 참고사항
1. pip를 포함한 python을 설치했음에도 cmd 창에서 "'pip'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다." 라는 메세지가 나올 수 있습니다.
- pip를 시스템 환경 변수에 등록하세요. (제어판->시스템->고급시스템 설정->환경변수->시스템 변수의 path에 파이썬 경로와 파이썬 경로\Scripts 2개 추가)
 
 <img width="842" alt="pip1" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/5e1352d0-9b7f-45c2-860c-b2aec702ff16">  
 제어판에서 시스템 및 보안 클릭  


<img width="837" alt="pip2" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/246b3387-2c71-427f-9bf2-0f93de8b66e1">  
시스템 클릭  


<img width="308" alt="pip3" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/20d87c83-0e1b-4c3f-83d7-1341b9d4a7fd">  
고급시스템 설정 클릭  


<img width="340" alt="pip4" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/a9171bbf-8f29-4272-bb5f-dceebfb661dc">  
환경변수 클릭  


<img width="319" alt="pip5" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/59ceecfa-f21a-40ab-a95c-a6eef852ac9f">  
하단 시스템 변수의 Path 항목 더블클릭  


<img width="454" alt="pip6" src="https://github.com/Mustang1234/GUI_Git_Manager_OSS_Team_25/assets/80468377/d2c82099-7512-4ab8-9ea7-8be1a02a2ea5">  
본인의 파이썬 경로를 복사해와서 파이썬 경로, 파이썬경로\scripts 두 개를 추가  



- 그 다음 cmd 창을 새로 켜서 위의 명령어를 실행합니다. ["설치 및 실행 준비"]  
(#설치-및-실행-준비) 3번 다시 시도하기.
