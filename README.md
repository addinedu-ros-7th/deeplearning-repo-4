![image](https://github.com/user-attachments/assets/3d029147-ea95-443c-aec7-5cf51d77ab02)

# City Guardian : 인공지능 안전 관제 시스템
# 1. Project Overview 
## 1-1 Topic
&nbsp;이 시스템은 **지능형 CCTV**를 활용하여 **화재, 폭력, 흉기** 상황을 자동으로 감지하고, 중앙 서버에서 데이터를 관리하며, 실시간으로 알림을 제공하는 관제 시스템입니다.<br>
&nbsp;**지능형 CCTV** 는 단순한 물체를 모니터링 하는 역할을 넘어 안전 골든타임을 확보하고 국민 일상과 사회문제를 해결하는 핵심기술 입니다.<br>
다양한 분야에서 수요가 높아지는 만큼 앞으로 **지능형 CCTV**를 통해 사람은 안전하고 기업은 효율적이며 환경은 안전해지는 사회를 구축할 수 있길 기대합니다.

## 1-2 Tech Stacks
<div align=center>

  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
  <br>
  
  <img src="https://img.shields.io/badge/Visual Studio Code-007ACC?style=for-the-badge&logo=Visual Studio Code&logoColor=white"/>
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white">
  <img src="https://img.shields.io/badge/confluence-0052CC?style=for-the-badge&logo=confluence&logoColor=white">
  <br>
  
  <img src="https://img.shields.io/badge/slack-FFD700?style=for-the-badge&logo=slack&logoColor=white">
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/PyQt5-83B81A?style=for-the-badge&logo=PyQt5&logoColor=white">
  <img src="https://img.shields.io/badge/YOLO-FF55FF?style=for-the-badge&logo=YOLO&logoColor=white">
  <br>

</div>

<br>

## 1-3 Team & Responsibility
|이름|담당 업무|
|:---:|---|
|**조지은(팀장)**| • Central Server GUI 구현<br> • 녹화영상 HTTP 통신<br> • 영상 로그 TCP 통신<br> • 위험상황 카운트 및 표시등 기능 구현|
|**김완섭(팀원)**| • Fire Segment, Fall Down Pose & 딥러닝 YOLO 모델 구현<br> • PPT 자료 준비, 발표|
|**유재현(팀원)**| • 실시간 영상 TCP 통신 및 딥러닝 모델 적용<br> • Violence Pose & LSTM 모델 구현<br> • Fire Station, Police Station GUI 구현<br> • Jira, Confluence, DB, Github
|**이영훈(팀원)**| • Knife Detect YOLO 모델 구현|
---
# 2.Project Plan
## 2-1 System Requirement
|카테고리|Function (기능)|Description (구체화)|우선순위|비고|
|:---:|:---:|---|:---:|:---:|
|상황감지|화재 감지 기능|* 화재 감지<br> - YOLO v8n-Segment 모델을 활용하여 화재 상황 감지|1|PASS|
||실신 감지 기능|* 실신 감지<br> - YOLO v8m-Pose & 딥러닝 모델을 활용하여 실신 상황 감지|1|PASS|
||흉기 감지 기능|* 흉기 감지<br> - YOLO v8n-Object Detection 모델을 활용하여 흉기(칼)의 존재를 감지|1|PASS|
|위험 상황 처리|위험 상황 카운트|* 일간 위험 상황 카운트<br> - 위험 상황을 실시간으로 카운트 하고, 이를 소방서, 경찰서 GUI 에 표시|1|PASS|
||위험 상황 표시등|* 위험 상황 발생 시 표시등 ON|1|PASS|
||CCTV 모니터링|* 실시간 영상 확인<br> - 각 구역에 대한 실시간 CCTV 영상 스트리밍 제공|1|PASS|
||CCTV 모니터 확대|* 상세하게 실시간 영상을 볼 수 있도록 영상 클릭 시 확대 제공|2|PASS|
||위험 상황 자동 녹화|* 위험 상황 발생 시 영상 자동 녹화<br> - 위험 상황 발생 시 자동으로 녹화를 시작하고, 관련된 데이터를 저장|2|PASS|
||위험 상황 표시|* 위험 상황 발생 시, 지도에 화재, 실신, 흉기 표시버튼이 표시됨|2||
|위험 상황 조회|위험 상황 기록 조회|* 상세 검색 조건에 따라 녹화 영상 로그 조회|2|PASS|
||녹화 영상 열람|* 사건 발생 시간, 종류, 위치 등 세부 검색 조건에 맞게 영상 조회|2|PASS|
|위험 상황 알림|SMS 알림|* 위험 상황 발생 시 사용자에게 SMS 문자 전송|3||

## 2-2 System Configuration
![Image](https://github.com/user-attachments/assets/0f72aec8-db2d-4d93-998d-8e21b9d2d5a4)

## 2-3 ER - Diagram
![Image](https://github.com/user-attachments/assets/8e511662-2230-492e-ad75-f386ffb6bcf8)

## 2-4 GUI Design (Central Server)
![Image](https://github.com/user-attachments/assets/bd964069-0c5b-4fb0-a37f-b4ec2244c663)
![Image](https://github.com/user-attachments/assets/90b168bc-4566-4e17-bcb4-6c5f0506bab5)

## 2-5 GUI Design (Fire Station)
![Image](https://github.com/user-attachments/assets/73bc53dd-e0e5-493b-9787-d27dc6c29d77)
![Image](https://github.com/user-attachments/assets/8bda5b58-e8dd-43ce-8104-3afa03357b1e)

## 2-6 GUI Design (Police Station)
![Image](https://github.com/user-attachments/assets/be01e030-7838-43e6-9cdc-ff8a44ad0737)
![Image](https://github.com/user-attachments/assets/ed95f4b7-4039-4fa0-bd41-e305043387d4)

---
# 3. Main Functions
## 3-1 Fire Segmentation
[동영상 보기]https://github.com/addinedu-ros-7th/deeplearning-repo-4/blob/main/videos/lighter%20segment.avi
![Screenshot from 2024-12-13 16-13-42](https://github.com/user-attachments/assets/02e044d1-bd50-40be-ae3a-b4c807a0198e)

## 3-2 Fall Down Pose Estimation
[동영상 보기]https://github.com/addinedu-ros-7th/deeplearning-repo-4/blob/main/videos/fall_down%20pose%20detection.mp4
![Screenshot from 2024-12-13 16-13-52](https://github.com/user-attachments/assets/2d6b678f-a8b5-4cd7-8ebf-7ac3da057b5f)

## 3-3 Knife Object Detection
![Screenshot from 2024-12-13 16-13-56](https://github.com/user-attachments/assets/ea695c40-f84d-4a03-9d73-f0ce2df5ac63)

## 3-4 Violence Detection
[동영상 보기]https://youtu.be/kUtSx9mMoa8?si=makyOqP7ukipDyiu
![Image](https://github.com/user-attachments/assets/8243469e-1099-4f68-9e6f-bcb5876898e1)

![Image](https://github.com/user-attachments/assets/1764f6d0-663e-4253-b2b7-6712e32f671e)

---
# 4. Problems & Improvement
- **화재 Segment 학습 간 인식률 문제**
  - 화재 동영상 촬영 후 프레임 단위 이미지 데이터 분류
  - Roboflow 활용 라벨링 진행
 
- **쓰러짐 Pose 인식률 문제**
  - Pose 모델 키포인트 데이터 변환 및 레이블 json 파일 분류
  - 딥러닝 학습
  - 박스 높이보다 너비가 길 경우 넘어짐으로 판단 인식률 증가
  
- **흉기 감지 Object Detection 인식률 문제**
  - Knife 인식과 함께 뾰족한 사물도 Knife로 인식되는 문제가 발생하여  Dataset을 추가적으로 학습시켜 인식률을 높임

- **흉기 감지모델과 폭력 감지 모델 통합**
  - 호환성 문제로 두개의 모델이 하나의 영상에서 결과 데이터가 표시가 되지 않는 문제 해결 필요
---
# 5. Review
|이름|소감|
|:---:|---|
|**조지은(팀장)**| GUI를 설계하는 과정에서  TCP 소켓과 Flask 기반의 HTTP 스트리밍을 활용해 안정적인 데이터 송수신 환경을 구축하며 네트워크 통신의 중요성을 알게 되었고 이번 프로젝트를 통해 사용자 중심의 설계와 기술적 문제를 해결하는 과정에서 많은 것을 배우고 성장할 수 있었습니다. |
|**김완섭(팀원)**| 팀에서 YOLO를 담당하여 데이터 분류, 라벨링, 학습 등 여러가지 모델을 진행 하면서 어려움이 있었지만, 프로젝트 기간동안 실력 숙달이 된 것 같고, 내가 재미있어 하는 분야를 찾은 것 같아 좋은 경험이 되었습니다. |
|**유재현(팀원)**| 시스템에 TCP 통신과 화재, 흉기 감지 딥러닝 모델을 적용하여 실시간 위험상황 감지 기능을 구현 해보았습니다. 실신, 폭력 감지 모델을 GUI에 통합 시키는 과정에서 아쉬운 부분이 있었지만 서버 연결 상태와 시스템 기능을 원활히 유지하며 기술 역량을 향상할 수 있었던 소중한 기회였습니다.|
|**이영훈(팀원)**| 이미지나 영상에서 사물을 학습시켜 인식을 하는 새로운 경험을 하게 되어 흥미로웠고, YOLO와 같은 모듈은 사용하기 쉬웠지만, 다른 모델을 사용할때는 어려운점도 있었습니다.|

# 6. Presentation
[발표자료]https://docs.google.com/presentation/d/1MKaWEkayNhbj-BMBYFziAtfxzu7jGDmBcmMe2kjy_6M/edit?usp=sharing
