#weapon detect test python file

import cv2
from ultralytics import YOLO
from roboflow import Roboflow


# yolov8s 모델 사용
model = YOLO('yolov8n.pt')

# 1. yolov8 형식 dataset 수집

rf = Roboflow(api_key="API KEY")  # Roboflow 계정의 API 키
project = rf.workspace().project("knife_object")  # 프로젝트 이름
dataset = project.version(1).download("yolov8")  # YOLOv8 형식으로 다운로드

# 2. 학습 수행
model.train(
    data="/home/hun/ws/yolov8/knife_object-1/data.yaml",  # Roboflow에서 다운로드한 data.yaml 경로
    epochs=120,                        # 학습 반복 횟수
    batch=16,                         # 배치 크기
    imgsz=640                         # 이미지 크기
)

# 3. 학습 완료된 모델 저장
model_path = "runs/detect/train/weights/best.pt"  # 학습된 모델 경로


# 4. 모델 평가 및 결과 출력

model = YOLO("runs/detect/train/weights/best.pt")

# 테스트 데이터로 평가
results = model.val(data="/home/hun/ws/yolov8/knife_object-1/data.yaml")

# 평가 결과 출력
print(dir(results))  # Precision, Recall, mAP 등


# 웹캠을 통해 knife 이미지 인식 

# 웹캠 열기
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("웹캠 영상이 존재하지 않습니다.")
        break

    # 객체 탐지 수행
    results = model.predict(source=frame, save=False, conf=0.6)

    annotated_frame = results[0].plot()

    cv2.imshow("knife Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:  # 27은 ESC 키의 ASCII 코드
        break

cap.release()
cv2.destroyAllWindows()
