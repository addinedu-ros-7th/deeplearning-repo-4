import sys
import cv2
import os
import socket
import pickle
import vlc
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PIL import Image, ImageDraw, ImageFont
from PyQt5.uic import loadUi
from ultralytics import YOLO
from datetime import datetime

CLASS_NAMES = {0: "knife"}  # Weapon detection class definition

class ReceiverThread(QThread):
    frameProcessed = pyqtSignal(object, list)
    serverStatus = pyqtSignal(bool)

    def __init__(self, tcp_port, central_port, model_path):
        super().__init__()
        self.tcp_port = tcp_port
        self.central_port = central_port
        self.running = True
        self.model = YOLO(model_path)
        self.last_timestamp = 0
        self.tcp_socket = None 

    def send_labels_to_central_server(self, labels):
        target_address = ('192.168.0.214', self.central_port)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect(target_address)
                data = pickle.dumps(labels)
                tcp_socket.sendall(len(data).to_bytes(4, 'big') + data)
                self.serverStatus.emit(True)
        except Exception:
            self.serverStatus.emit(False)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind(('0.0.0.0', self.tcp_port))
            tcp_socket.listen(5)

            while self.running:
                conn, addr = tcp_socket.accept()
                with conn:
                    while self.running:
                        try:
                            length = conn.recv(4)
                            if not length:
                                break
                            length = int.from_bytes(length, 'big')
                            data = b""
                            while len(data) < length:
                                packet = conn.recv(4096)
                                if not packet:
                                    break
                                data += packet

                            timestamp, encoded_frame = pickle.loads(data)
                            frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)
                            if timestamp > self.last_timestamp:
                                self.last_timestamp = timestamp
                                results = self.model.predict(frame)
                                for box, conf, cls in zip(
                                    results[0].boxes.xyxy.cpu().numpy(),
                                    results[0].boxes.conf.cpu().numpy(),
                                    results[0].boxes.cls.cpu().numpy()
                                ):
                                    if conf < 0.7:
                                        continue  # Skip low-confidence detections
                                    x1, y1, x2, y2 = map(int, box)
                                    label = f"{CLASS_NAMES.get(int(cls), 'unknown')} {conf:.2f}"
                                    color = (255, 0, 0)  # Blue for weapons
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                weapon_labels = [
                                    [
                                        int(box[0]), int(box[1]), int(box[2]), int(box[3]),
                                        float(conf), CLASS_NAMES.get(int(cls), "unknown")
                                    ]
                                    for box, conf, cls in zip(
                                        results[0].boxes.xyxy.cpu().numpy(),
                                        results[0].boxes.conf.cpu().numpy(),
                                        results[0].boxes.cls.cpu().numpy()
                                    )
                                ]
                                self.send_labels_to_central_server(weapon_labels)
                                self.frameProcessed.emit(frame, weapon_labels)
                            conn.sendall(b"Data received")
                        except Exception as e:
                            break

class PoliceStationApp(QDialog):
    def __init__(self, ports, central_ports, model_path, central_server_port):
        super().__init__()
        ui_path = "/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/Police_Station_v2.ui"
        loadUi(ui_path, self)

        self.central_server_port = central_server_port  # 중앙 서버 포트 저장

        self.label_mapping = {
            ports[0]: self.label,  # Placeholder for video frame 1
            ports[1]: self.label_2,  # Placeholder for video frame 2
            ports[2]: self.label_3,  # Placeholder for video frame 3
            ports[3]: self.label_4,  # Placeholder for video frame 4
        }

        self.weapon_count_label = self.weapon_count  # UI objectName: weapon_count
        self.weapon_count = 0


        self.hidden_file_paths = []  # 파일 경로 저장


        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_xwindow(int(self.videowidget.winId()))


        self.searchButton.clicked.connect(self.request_videos_from_central)
        self.viewButton.clicked.connect(self.play_video)


        # 버튼 이벤트 연결
        self.Monitoring_Button.clicked.connect(self.show_monitoring_page)
        self.Event_Log_Button.clicked.connect(self.show_event_log_page)

        self.threads = []
        for port, central_port in zip(ports, central_ports):
            thread = ReceiverThread(port, central_port, model_path)
            thread.frameProcessed.connect(self.update_gui(port))
            thread.serverStatus.connect(self.update_server_status)
            thread.start()
            self.threads.append(thread)



        self.active_style = """
            QPushButton {
                background-color: #03A9F4; /* 활성화 시 진한 파란색 배경  */
                color: #FFFFFF; /* 흰색 텍스트 */
                border: 2px solid #0288D1; /* 짙은 파란색 테두리 */
                font-weight: bold; /* 굵은 글자 */
                border-radius: 5px; /* 둥근 버튼 */
                padding: 5px 10px; /* 안쪽 여백 */
            }
        """

        self.default_style = """
            QPushButton {
                background-color: #B3E5FC; /* 기본 상태 밝은 파랑색 배경 */
                color: #000000; /* 검은색 텍스트 */
                border: 1px solid #01579B; /* 딥블루 테두리 */
                border-radius: 5px; /* 둥근 버튼 */
                padding: 5px 10px; /* 안쪽 여백 */
            }
        """


        self.reset_button_styles()
        self.Monitoring_Button.setStyleSheet(self.active_style)  # 초기 활성화 버튼 설정

    def show_monitoring_page(self):
        """첫 번째 페이지로 전환"""
        self.reset_button_styles()
        self.Monitoring_Button.setStyleSheet(self.active_style)  # 관제 버튼 활성화
        self.stackedWidget.setCurrentIndex(0)

    def show_event_log_page(self):
        """두 번째 페이지로 전환"""
        self.reset_button_styles()
        self.Event_Log_Button.setStyleSheet(self.active_style)  # 기록 조회 버튼 활성화        
        self.stackedWidget.setCurrentIndex(1)

    def reset_button_styles(self):
        """모든 버튼 스타일을 기본값으로 초기화"""
        self.Monitoring_Button.setStyleSheet(self.default_style)
        self.Event_Log_Button.setStyleSheet(self.default_style)


    def update_gui(self, port):
        def inner(frame, labels):
            label = self.label_mapping[port]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            # OpenCV 프레임을 Pillow 이미지로 변환
            pil_image = Image.fromarray(rgb_frame)

            # Pillow의 ImageDraw 사용
            draw = ImageDraw.Draw(pil_image)

            # 한글 지원 폰트 경로 설정 (Windows/Linux에 맞게 변경)
            font_path = "/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/NanumGothicBold.ttf"  
            font = ImageFont.truetype(font_path, 20)  # 폰트 크기 설정

            # 텍스트 추가
            camera_id = list(self.label_mapping.keys()).index(port)
            text_ip = f"IP: 192.168.0.4{camera_id}"  # IP 먼저 표시
            text_channel = f"대륭3차 카메라 {camera_id + 1}번"  # 카메라 정보 다음에 표시
            draw.text((10, 50), text_ip, font=font, fill=(173, 216, 230))  # 연하늘색
            draw.text((10, 20), text_channel, font=font, fill=(173, 216, 230))

            # Pillow 이미지를 OpenCV 형식으로 변환
            rgb_frame = np.array(pil_image)






            h, w, ch = rgb_frame.shape
            qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            label.setPixmap(pixmap)

            # Initialize weapon detection state and timestamps for this port if not already
            if not hasattr(self, 'weapon_states'):
                self.weapon_states = {p: False for p in self.label_mapping.keys()}
                self.weapon_counts = {p: 0 for p in self.label_mapping.keys()}
                self.weapon_detection_start = {p: None for p in self.label_mapping.keys()}
                self.weapon_no_label_start = {p: None for p in self.label_mapping.keys()}

            # Weapon detection logic
            weapon_detected = any(label[4] >= 0.7 for label in labels)
            current_time = datetime.now()

            if weapon_detected:
                # 감지 시작 상태 처리
                if not self.weapon_states[port]:  # 새로 감지가 시작된 경우
                    if self.weapon_detection_start[port] is None:  # 타이머 시작
                        self.weapon_detection_start[port] = current_time
                    elif (current_time - self.weapon_detection_start[port]).total_seconds() >= 1:
                        # 감지가 1초 이상 지속된 경우 상태 활성화
                        self.weapon_states[port] = True
                        self.weapon_detect.setIcon(QIcon("/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/ui/weapon_on.png"))  # 활성화 아이콘
                        self.weapon_detection_start[port] = None  # 타이머 초기화
                self.weapon_no_label_start[port] = None  # 감지 해제 타이머 초기화

            else:
                # 감지 종료 상태 처리
                if self.weapon_states[port]:  # 감지 상태에서 해제로 전환
                    if self.weapon_no_label_start[port] is None:  # 타이머 시작
                        self.weapon_no_label_start[port] = current_time
                    elif (current_time - self.weapon_no_label_start[port]).total_seconds() >= 1:
                        # 감지가 1초 이상 발생하지 않은 경우 상태 비활성화
                        self.weapon_states[port] = False
                        self.weapon_counts[port] += 1  # 카운트 증가
                        self.weapon_count_label.setText(str(sum(self.weapon_counts.values())))  # 카운트 갱신
                        self.weapon_detect.setIcon(QIcon("/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/ui/weapon_off.png"))  # 비활성화 아이콘
                        self.weapon_no_label_start[port] = None  # 타이머 초기화

                self.weapon_detection_start[port] = None  # 감지 시작 타이머 초기화

        return inner


    def update_server_status(self, status):
        if status:
            self.police_server_on.setIcon(QIcon("/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/ui/light_on.png"))  # on 상태 아이콘 경로 바꿔야함
        else:
            self.police_server_on.setIcon(QIcon("/home/zeus/ws/AEGISVISION/src/aegis_gui/test_2/ui/light_off.png"))  # off 상태 아이콘 경로 바꿔야함           

    def closeEvent(self, event):
        for thread in self.threads:
            thread.running = False
            thread.wait()
            if hasattr(thread, 'tcp_socket') and thread.tcp_socket:
                thread.tcp_socket.close()  # 소켓 명시적으로 닫기
        print("All threads stopped and sockets closed.")
        event.accept()

    def request_videos_from_central(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                print(f"Connecting to central server at 127.0.0.1:{self.central_server_port}")
                client_socket.connect(('192.168.0.214', self.central_server_port))

                # 날짜, 시간, 분 조건 설정
                selected_date = self.dateEdit.date().toString("yyyyMMdd")
                selected_hour = self.comboBox.currentText().replace("시", "").zfill(2)
                selected_min = self.comboBox_2.currentText().replace("분", "")

                # 분 범위 매핑
                minute_ranges = {
                    "0": ("00", "09"),
                    "10": ("10", "19"),
                    "20": ("20", "29"),
                    "30": ("30", "39"),
                    "40": ("40", "49"),
                    "50": ("50", "59"),
                }

                if selected_min not in minute_ranges:
                    print("유효하지 않은 분 선택입니다.")
                    return

                start_minute, end_minute = minute_ranges[selected_min]
                time_prefix = f"{selected_date}_{selected_hour}"
                time_start = f"{time_prefix}{start_minute}"
                time_end = f"{time_prefix}{end_minute}"

                # 요청 데이터 생성
                request_data = {
                    "action": "get_videos",
                    "event_type": "knife" if self.Weapon_radioButton.isChecked() else "weapon",
                    "time_range": {"start": time_start, "end": time_end}
                }
                serialized_request = pickle.dumps(request_data)
                client_socket.sendall(len(serialized_request).to_bytes(4, 'big') + serialized_request)

                # 응답 데이터 길이 수신
                length_bytes = client_socket.recv(4)
                if not length_bytes:
                    print("No response length received from central server.")
                    return
                length = int.from_bytes(length_bytes, 'big')

                # 데이터 수신
                data = b""
                while len(data) < length:
                    packet = client_socket.recv(min(4096, length - len(data)))
                    if not packet:
                        print("Connection closed by central server.")
                        return
                    data += packet

                # 데이터 역직렬화
                video_list = pickle.loads(data)
                print(f"Received video list from server: {video_list}")

                # 테이블 업데이트
                self.update_table(video_list)

        except socket.error as se:
            print(f"Socket error while communicating with central server: {se}")
        except Exception as e:
            print(f"Error communicating with central server: {e}")

    def update_table(self, video_list):
        if not video_list:
            print("No data received from central server.")
            self.tableWidget.setRowCount(0)  # 데이터가 없을 때 테이블 비우기
            return

        print(f"Updating table with video list: {video_list}")
        self.tableWidget.setRowCount(len(video_list))  # 행 수 설정
        self.tableWidget.setColumnCount(3)  # 열 수 설정
        self.tableWidget.setHorizontalHeaderLabels(['비디오 ID', '파일 이름', '저장 시간'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 헤더 크기 자동 조정
        self.tableWidget.verticalHeader().setVisible(False)  # 행 헤더 숨기기

        # 숨겨진 파일 경로 리스트 초기화
        self.hidden_file_paths = []

        for row_index, video in enumerate(video_list):
            try:
                # 딕셔너리 형식 데이터 처리
                video_id = video.get('video_id', 'Unknown')
                file_name = video.get('file_name', 'Unknown')
                file_path = video.get('file_path', 'Unknown')
                upload_time = video.get('upload_time', 'Unknown')

                # 테이블에 데이터 삽입
                id_item = QTableWidgetItem(str(video_id))
                id_item.setTextAlignment(Qt.AlignCenter)  # 비디오 ID 중앙 정렬
                self.tableWidget.setItem(row_index, 0, id_item)
                #self.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(video_id)))
                self.tableWidget.setItem(row_index, 1, QTableWidgetItem(file_name))
                self.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(upload_time)))

                # 숨겨진 파일 경로 추가
                self.hidden_file_paths.append(file_path)
            except Exception as e:
                print(f"Error updating row {row_index}: {e}")


    def play_video(self):
        """
        선택한 비디오를 중앙 서버에서 스트리밍으로 재생
        """
        selected_row = self.tableWidget.currentRow()  # 선택된 테이블 행
        if selected_row >= 0:
            # 숨겨진 파일 경로에서 파일 이름만 가져옴
            file_name = self.hidden_file_paths[selected_row].split('/')[-1]  # 파일 이름만 추출
            # 중앙 서버의 HTTP 스트리밍 URL 생성
            streaming_url = f"http://192.168.0.214:5000/video/{file_name}"  # 중앙 서버 IP 사용
            print(f"Streaming video from: {streaming_url}")
            # VLC 플레이어에 스트리밍 URL 설정
            media = self.instance.media_new(streaming_url)
            self.player.set_media(media)
            self.player.play()
        else:
            print("No video selected.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoliceStationApp(
        ports=[12000, 12001, 12002, 12003],
        central_ports=[15000, 15001, 15002, 15003],
        model_path="/home/zeus/ws/AEGISVISION/src/weapon_detect_model/runs/detect/train/weights/best.pt",
        central_server_port=15009
    )
    window.show()
    window.setWindowTitle("Police Station")
    sys.exit(app.exec_())
