![image](https://github.com/user-attachments/assets/3d029147-ea95-443c-aec7-5cf51d77ab02)

# City Guardian : 인공지능 안전 관제 시스템
# 1. Project Overview 
## 1.1 Topic
&nbsp;이 시스템은 **지능형 CCTV**를 활용하여 **화재, 폭력, 흉기** 상황을 자동으로 감지하고, 중앙 서버에서 데이터를 관리하며, 실시간으로 알림을 <br> 제공하는 관제 시스템입니다.<br>
&nbsp;**지능형 CCTV** 는 단순한 물체를 모니터링 하는 역할을 넘어 안전 골든타임을 확보하고 국민 일상과 사회문제를 해결하는 핵심기술이 됐다.<br>
다양한 분야에서 수요가 높아지는 만큼 앞으로 **지능형 CCTV**를 통해 사람은 안전하고 기업은 효율적이며 환경은 안전해지는 사회를 구축할 수 <br> 있길 기대한다.

## 1.2 Tech Stacks
<div align=center>

  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
  <img src="https://img.shields.io/badge/c++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white">
  <br>
  
  <img src="https://img.shields.io/badge/Visual Studio Code-007ACC?style=for-the-badge&logo=Visual Studio Code&logoColor=white"/>
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white">
  <img src="https://img.shields.io/badge/confluence-0052CC?style=for-the-badge&logo=confluence&logoColor=white">
  <br>
  
  <img src="https://img.shields.io/badge/slack-FFD700?style=for-the-badge&logo=slack&logoColor=white">
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/PyQt5-83B81A?style=for-the-badge&logo=PyQt5&logoColor=white">
  <br>

</div>

<br>

## 1.3 Team & Responsibility
|이름|담당 업무|
|:---:|---|
|**조지은(팀장)**| GUI 전체 구현 및 Central Server - 소켓 통신|
|**김완섭(팀원)**| Fire Segment, Fall Down Pose & 딥러닝 YOLO 모델 구현, PPT 자료 준비|
|**유재현(팀원)**| Central Server 구현, GUI - 소켓 통신, DB / Github 관리
|**이영훈(팀원)**| Knife Detect YOLO 모델 구현|
---
# 2.Project Plan
## 2.1 System Requirement
|카테고리|Function (기능)|Description (구체화)|우선순위|비고|
|:---:|:---:|---|:---:|:---:|
|상황감지|화재 감지 기능|* 화재 감지<br> - YOLO v8n-Segment 모델을 활용하여 화재 상황 감지|1|PASS|
||실신 감지 기능|* 실신 감지<br> - YOLO v8m-Pose & 딥러닝 모델을 활용하여 실신 상황 감지|1|PASS|
||흉기 감지 기능|* 흉기 감지<br> - YOLO v8n-Object Detection 모델을 활용하여 흉기(칼)의 존재를 감지|1|PASS|
|위험 상황 처리|위험 상황 카운트|* 일간 위험 상황 카운트<br> - 위험 상황을 실시간으로 카운트 하고, 이를 소방서, 경찰서 GUI 에 표시|1|PASS|
||위험 상황 표시등|* 위험 상황 발생 시 표시등 ON|1|PASS|
||CCTV 모니터링|* 실시간 영상 확인<br> - 각 구역에 대한 실시간 CCTV 영상 스트리밍 제공|1||
||CCTV 모니터 확대|* 상세하게 실시간 영상을 볼 수 있도록 영상 클릭 시 확대 제공|2||
||위험 상황 자동 녹화|* 위험 상황 발생 시 영상 자동 녹화<br> - 위험 상황 발생 시 자동으로 녹화를 시작하고, 관련된 데이터를 저장|2||
||위험 상황 표시|* 위험 상황 발생 시, 지도에 화재, 실신, 흉기 표시버튼이 표시됨|2||
|위험 상황 조회|위험 상황 기록 조회|* 상세 검색 조건에 따라 녹화 영상 로그 조회|2||
||녹화 영상 열람|* 사건 발생 시간, 종류, 위치 등 세부 검색 조건에 맞게 영상 조회|2||
|위험 상황 알림|SMS 알림|* 위험 상황 발생 시 사용자에게 SMS 문자 전송|3||

## 2.2 System Configuration
![image](https://github.com/user-attachments/assets/288fdb89-6750-4021-b530-93a7d0d688c1)

---
# 3. Main Functions
---
# 4. Problems & Improvement
- **화재 YOLO v8n-Segment 학습 간 인식률 저하**
  - 화재 동영상 촬영 후 프레임 단위 이미지 데이터 분류
  - Roboflow 활용 라벨링 진행
 
- **쓰러짐 YOLO v8m-Pose 학습 간 인식률 저하**
  - Pose 모델 키포인트 데이터 변환 및 레이블 json 파일 분류
  - 딥러닝 학습
  - 박스 높이보다 너비가 길 경우 넘어짐으로 판단 인식률 증가
