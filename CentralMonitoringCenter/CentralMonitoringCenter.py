import os
import cv2
import socket
import pickle
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QSizePolicy, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect
from PyQt5.QtGui import QImage, QPixmap, QColor, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QEvent, QObject, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
import mysql.connector
import vlc
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, abort
import os
app = Flask(__name__)
import threading


# 동영상 저장 경로
VIDEO_DIR = "/home/jieun/dev_ws/videos"  # 실제 동영상 디렉터리 경로로 설정
@app.route('/video/<filename>')
def stream_video(filename):
    """
    요청된 파일 이름으로 동영상을 스트리밍
    """
    video_path = os.path.join(VIDEO_DIR, filename)  # 파일 경로 생성
    # 파일이 존재하지 않으면 404 반환
    if not os.path.exists(video_path):
        abort(404, description="Video file not found.")
    # 파일 스트리밍 반환
    return send_file(video_path, as_attachment=False)



class FireStationApp(QThread):
    serverStatus = pyqtSignal(bool)  # 연결 상태 신호 (True: 연결, False: 끊김)

    def __init__(self, ports, central_ports):
        super().__init__()
        self.ports = ports
        self.central_ports = central_ports
        self.running = True

    def check_connection(self):
        previous_status = None
        for port in self.central_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect(('127.0.0.1', port))
                    if previous_status is not True:
                        self.serverStatus.emit(True)
                        previous_status = True
            except Exception:
                if previous_status is not False:
                    self.serverStatus.emit(False)
                    previous_status = False
    def run(self):
        while self.running:
            self.check_connection()
            self.msleep(5000)

class PoliceStationApp(QThread):
    serverStatus = pyqtSignal(bool)  # 연결 상태 신호 (True: 연결, False: 끊김)

    def __init__(self, ports, central_ports):
        super().__init__()
        self.ports = ports
        self.central_ports = central_ports
        self.running = True

    def check_connection(self):
        previous_status = None
        for port in self.central_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect(('127.0.0.1', port))
                    if previous_status is not True:
                        self.serverStatus.emit(True)
                        previous_status = True
            except Exception:
                if previous_status is not False:
                    self.serverStatus.emit(False)
                    previous_status = False

    def run(self):
        while self.running:
            self.check_connection()
            self.msleep(5000)





class FireLabelReceiverThread(QThread):
    fireLabelsReceived = pyqtSignal(list, int)  # (라벨 리스트, 카메라 ID)

    def __init__(self, tcp_port, camera_id):
        super().__init__()
        self.tcp_port = tcp_port
        self.camera_id = camera_id
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind(('0.0.0.0', self.tcp_port))
            tcp_socket.listen(5)
            print(f"Receiving FireStation labels on port {self.tcp_port}...")

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

                            labels = pickle.loads(data)
                            self.fireLabelsReceived.emit(labels, self.camera_id)
                            conn.sendall(b"Fire labels received")
                        except Exception as e:
                            print(f"Error receiving FireStation labels on port {self.tcp_port}: {e}")
                            break

class WeaponLabelReceiverThread(QThread):
    weaponLabelsReceived = pyqtSignal(list, int)  # (라벨 리스트, 카메라 ID)

    def __init__(self, tcp_port, camera_id):
        super().__init__()
        self.tcp_port = tcp_port
        self.camera_id = camera_id
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind(('0.0.0.0', self.tcp_port))
            tcp_socket.listen(5)
            print(f"Receiving PoliceStation labels on port {self.tcp_port}...")

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

                            labels = pickle.loads(data)
                            self.weaponLabelsReceived.emit(labels, self.camera_id)
                            conn.sendall(b"Weapon labels received")
                        except Exception as e:
                            print(f"Error receiving PoliceStation labels on port {self.tcp_port}: {e}")
                            break

class CentralFrameReceiverThread(QThread):
    frameReceived = pyqtSignal(np.ndarray, int)

    def __init__(self, tcp_port, camera_id):
        super().__init__()
        self.tcp_port = tcp_port
        self.camera_id = camera_id
        self.running = True
        self.last_timestamp = 0

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind(('0.0.0.0', self.tcp_port))
            tcp_socket.listen(5)
            print(f"Receiving frames on port {self.tcp_port}...")

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
                            frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)  # 압축 해제
                            if timestamp > self.last_timestamp:
                                self.last_timestamp = timestamp
                                self.frameReceived.emit(frame, self.camera_id)
                            conn.sendall(b"Frame received")
                        except Exception as e:
                            print(f"Error receiving frame on port {self.tcp_port}: {e}")
                            break

class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # 클릭 신호

    def mousePressEvent(self, event):
        self.clicked.emit()  # 클릭되면 신호 발생


class CentralServerApp(QDialog):
    def __init__(self, fire_ports, weapon_ports, frame_ports):
        super().__init__()
        loadUi("/home/jieun/dev_ws/test_2/Central_Server_v3.ui", self)


        # FireStationApp과 PoliceStationApp 초기화
        self.fire_station = FireStationApp(fire_ports, fire_ports)
        self.police_station = PoliceStationApp(weapon_ports, weapon_ports)

        # 연결 상태 신호 처리
        self.fire_station.serverStatus.connect(self.update_fire_server_icon)
        self.police_station.serverStatus.connect(self.update_police_server_icon)

        # 초기 아이콘 상태 설정
        self.fire_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_off.png"))  # 초기 off 상태
        self.police_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_off.png"))  # 초기 off 상태

        # # 연결 상태 신호 처리
        # self.fire_station.serverStatus.connect(self.update_fire_server_icon)
        # self.police_station.serverStatus.connect(self.update_police_server_icon)


        # FireStationApp과 PoliceStationApp 실행
        self.fire_station.start()
        self.police_station.start()

        self.db_config = {
            "host": "localhost",
            "user": "lento",
            "password": "0819",
            "database": "aegis"
        }

        self.db = mysql.connector.connect(**self.db_config)
        self.cursor = self.db.cursor()

        # 소켓 서버 초기화
        self.server_thread = QThread()
        self.server_worker = ServerWorker(self.db_config)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.finished.connect(self.server_thread.quit)
        self.server_worker.finished.connect(self.server_worker.deleteLater)
        self.server_thread.finished.connect(self.server_thread.deleteLater)
        self.server_thread.start()

        self.fireLabels = {i: [] for i in range(len(frame_ports))}
        self.weaponLabels = {i: [] for i in range(len(frame_ports))}
        self.frames = {i: np.zeros((680, 480, 3), dtype=np.uint8) for i in range(len(frame_ports))}
        self.video_writers = {i: None for i in range(len(frame_ports))}
        self.recording_start_times = {i: None for i in range(len(frame_ports))}

        self.video_save_path = "/home/jieun/dev_ws/videos"
        os.makedirs(self.video_save_path, exist_ok=True)




        # 각 카메라의 상태를 저장
        self.list_of_cameras_state = {
            "Camera_1": "Normal",
            "Camera_2": "Normal",
            "Camera_3": "Normal",
            "Camera_4": "Normal"
        }



        self.label_mapping = {
            0: self.label,
            1: self.label_2,
            2: self.label_3,
            3: self.label_4
        }


        # 각 카메라 QLabel에 이벤트 필터 추가
        for camera_id, label in self.label_mapping.items():
            label.setObjectName(f"Camera_{camera_id + 1}")  # QLabel 이름 지정
            label.installEventFilter(self)  # 이벤트 필터 등록

        self.fire_receivers = [FireLabelReceiverThread(port, i) for i, port in enumerate(fire_ports)]
        self.weapon_receivers = [WeaponLabelReceiverThread(port, i) for i, port in enumerate(weapon_ports)]
        self.frame_receivers = [CentralFrameReceiverThread(port, i) for i, port in enumerate(frame_ports)]

        for receiver in self.fire_receivers:
            receiver.fireLabelsReceived.connect(self.update_fire_labels)
            receiver.start()

        for receiver in self.weapon_receivers:
            receiver.weaponLabelsReceived.connect(self.update_weapon_labels)
            receiver.start()

        for receiver in self.frame_receivers:
            receiver.frameReceived.connect(self.update_frame)
            receiver.start()

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_xwindow(int(self.videowidget.winId()))

        self.searchButton.clicked.connect(self.search_videos)
        self.viewButton.clicked.connect(self.play_video)



        # 버튼 이벤트 연결
        self.Monitoring_Button.clicked.connect(self.show_monitoring_page)
        self.Event_Log_Button.clicked.connect(self.show_event_log_page)

        


        self.active_style = """
            QPushButton {
                background-color: #4CAF50; /* 활성화 시 진한 초록색 배경 */
                color: #FFFFFF; /* 흰색 텍스트 */
                border: 2px solid #388E3C; /* 짙은 초록 테두리 */
                font-weight: bold; /* 굵은 글자 */
                border-radius: 5px; /* 둥근 버튼 */
                padding: 5px 10px; /* 안쪽 여백 */
            }
        """

        self.default_style = """
            QPushButton {
                background-color: #C8E6C9; /* 기본 상태 밝은 초록색 배경 */
                color: #000000; /* 검은색 텍스트 */
                border: 1px solid #1B5E20; /* 딥 그린 */
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


    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        """
        더블 클릭 이벤트를 처리하여 카메라 화면 상태 전환
        """
        if event.type() == QEvent.MouseButtonDblClick:
            camera_name = source.objectName()  # 클릭된 QLabel 이름 가져오기
            if camera_name in self.list_of_cameras_state:
                state = self.list_of_cameras_state[camera_name]
                label = source  # 현재 클릭된 QLabel
                
                if state == "Normal":
                    # 다른 카메라 숨기기
                    for key, lbl in self.label_mapping.items():
                        if lbl.objectName() != camera_name:
                            lbl.hide()

                    # QLabel을 전체 화면으로 확장 (비율 유지)
                    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    label.resize(self.width(), self.height())  # 창 크기에 맞게 QLabel 크기 조정
                    label.setAlignment(Qt.AlignCenter)  # 중앙 정렬
                    self.list_of_cameras_state[camera_name] = "Maximized"
                
                else:
                    # 모든 카메라 다시 표시
                    for lbl in self.label_mapping.values():
                        lbl.show()
                        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                        # lbl.setFixedSize(680, 480)
                    self.list_of_cameras_state[camera_name] = "Normal"
            return True
        return super(CentralServerApp, self).eventFilter(source, event)



    def update_fire_labels(self, labels, camera_id):
        self.fireLabels[camera_id] = labels
        self.update_combined_view(camera_id)

    def update_weapon_labels(self, labels, camera_id):
        self.weaponLabels[camera_id] = labels
        self.update_combined_view(camera_id)

    def update_frame(self, frame, camera_id):
        self.frames[camera_id] = frame
        self.update_combined_view(camera_id)

    def update_combined_view(self, camera_id):
        canvas = self.frames[camera_id].copy()

        # 감지 상태 및 타이머 관리
        fire_active = getattr(self, f"fire_active_{camera_id}", False)
        weapon_active = getattr(self, f"weapon_active_{camera_id}", False)
        fire_detection_start = getattr(self, f"fire_detection_start_{camera_id}", None)
        weapon_detection_start = getattr(self, f"weapon_detection_start_{camera_id}", None)
        fire_no_label_start = getattr(self, f"fire_no_label_start_{camera_id}", None)
        weapon_no_label_start = getattr(self, f"weapon_no_label_start_{camera_id}", None)
        recording_active = getattr(self, f"recording_active_{camera_id}", False)
        current_time = datetime.now()

        # --- 화재 감지 처리 ---
        fire_detecting = False
        for label in self.fireLabels[camera_id]:
            x1, y1, x2, y2, conf, cls = label
            if conf >= 0.7:
                fire_detecting = True
                cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(canvas, f"{cls} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if fire_detecting:
            if not fire_detection_start:
                setattr(self, f"fire_detection_start_{camera_id}", current_time)
            elif (current_time - fire_detection_start).total_seconds() >= 1 and not fire_active:
                fire_active = True
                self.fire_detect.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/fire_on.png"))  # 활성화 아이콘
            setattr(self, f"fire_no_label_start_{camera_id}", None)
        else:
            setattr(self, f"fire_detection_start_{camera_id}", None)
            if not fire_no_label_start:
                setattr(self, f"fire_no_label_start_{camera_id}", current_time)
            elif (current_time - fire_no_label_start).total_seconds() >= 1 and fire_active:
                fire_active = False
                self.fire_detect.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/fire_off.png"))  # 비활성화 아이콘
                # 화재 감지 카운트 증가
                current_count = int(self.fire_count.text()) if self.fire_count.text().isdigit() else 0
                self.fire_count.setText(str(current_count + 1))

        setattr(self, f"fire_active_{camera_id}", fire_active)

        # --- 무기 감지 처리 ---
        weapon_detecting = False
        for label in self.weaponLabels[camera_id]:
            x1, y1, x2, y2, conf, cls = label
            if conf >= 0.7:
                weapon_detecting = True
                cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(canvas, f"{cls} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        if weapon_detecting:
            if not weapon_detection_start:
                setattr(self, f"weapon_detection_start_{camera_id}", current_time)
            elif (current_time - weapon_detection_start).total_seconds() >= 1 and not weapon_active:
                weapon_active = True
                self.weapon_detect.show()
                self.weapon_no_detect.hide()
            #self.weapon_detect.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/weapon_on.png"))  # 활성화 아이콘
            setattr(self, f"weapon_no_label_start_{camera_id}", None)
        else:
            setattr(self, f"weapon_detection_start_{camera_id}", None)
            if not weapon_no_label_start:
                setattr(self, f"weapon_no_label_start_{camera_id}", current_time)
            elif (current_time - weapon_no_label_start).total_seconds() >= 1 and weapon_active:
                weapon_active = False
                self.weapon_detect.hide()
                self.weapon_no_detect.show()
                #self.weapon_detect.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/weapon_off.png"))  # 비활성화 아이콘
                # 무기 감지 카운트 증가
                current_count = int(self.weapon_count.text()) if self.weapon_count.text().isdigit() else 0
                self.weapon_count.setText(str(current_count + 1))

        setattr(self, f"weapon_active_{camera_id}", weapon_active)

        # --- 동영상 저장 처리 ---
        is_detecting = fire_active or weapon_active
        self.handle_video_recording(camera_id, canvas, is_detecting)

        # 프레임 디스플레이
        self.display_frame(canvas, camera_id)


    def handle_video_recording(self, camera_id, frame, is_detecting):
        """
        특정 카메라 ID에서 감지 상태에 따라 비디오 녹화 시작/종료 및 DB에 저장
        """
        # 감지된 클래스명 가져오기
        detected_class = None
        if self.fireLabels[camera_id]:
            detected_class = self.fireLabels[camera_id][0][-1]  # fire 감지
        elif self.weaponLabels[camera_id]:
            detected_class = self.weaponLabels[camera_id][0][-1]  # weapon 감지

        if is_detecting and detected_class:  # 감지 중이며 감지된 클래스명이 있을 경우
            if self.video_writers[camera_id] is None:  # 새로운 녹화 시작
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{detected_class}_{timestamp}.mp4"
                file_path = f"{self.video_save_path}/{file_name}"

                # MP4 코덱 설정
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                height, width, _ = frame.shape
                self.video_writers[camera_id] = cv2.VideoWriter(file_path, fourcc, 20.0, (width, height))
                self.recording_start_times[camera_id] = datetime.now()
                print(f"Started recording for camera {camera_id}: {file_path}")

                # 비디오 메타데이터를 DB에 삽입
                upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_query = """
                    INSERT INTO video_metadata (file_name, file_path, upload_time)
                    VALUES (%s, %s, %s)
                """
                try:
                    self.cursor.execute(insert_query, (file_name, file_path, upload_time))
                    self.db.commit()
                    print(f"Inserted video metadata into database: {file_name}")
                except Exception as e:
                    print(f"Error inserting video metadata into database: {e}")

            # 현재 프레임 기록
            self.video_writers[camera_id].write(frame)

        elif not is_detecting:  # 감지 종료 시 녹화 중단
            if self.video_writers[camera_id] is not None:
                self.video_writers[camera_id].release()
                self.video_writers[camera_id] = None
                print(f"Stopped recording for camera {camera_id}")

    def search_videos(self):
        # 날짜, 시간 및 분 조건 설정
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

        # 시간 패턴 및 범위 설정
        time_prefix = f"{selected_date}_{selected_hour}"
        time_start = f"{time_prefix}{start_minute}"
        time_end = f"{time_prefix}{end_minute}"

        # 이벤트 필터
        if self.Fire_radioButton.isChecked():
            event_filter = f"file_name LIKE 'fire_%' AND file_name BETWEEN 'fire_{time_start}' AND 'fire_{time_end}'"
        elif self.Weapon_radioButton.isChecked():
            event_filter = f"file_name LIKE 'knife_%' AND file_name BETWEEN 'knife_{time_start}' AND 'knife_{time_end}'"
        else:
            print("이벤트 유형이 선택되지 않았습니다.")
            return

        # SQL 쿼리 작성
        query = f"""
            SELECT video_id, file_name, file_path, upload_time
            FROM video_metadata
            WHERE {event_filter}
        """
        print(f"Generated Query: {query}")  # SQL 쿼리 출력 (디버깅용)


        if query:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(3)  # File Path는 숨기므로 3열만 표시
            self.tableWidget.setHorizontalHeaderLabels(['비디오 ID', '파일 이름', '저장 시간'])
            # TableWidget 헤더를 Stretch 모드로 설정
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tableWidget.verticalHeader().setVisible(False)  # 행 번호 숨기기

            # 테이블에 데이터 채우기 (file_path는 숨기고 백그라운드에 저장)
            self.hidden_file_paths = []  # 파일 경로를 저장하는 리스트
            for row_index, row in enumerate(rows):
                    # Video ID (가운데 정렬 적용)
                item_id = QTableWidgetItem(str(row[0]))
                item_id.setTextAlignment(Qt.AlignCenter)  # 가운데 정렬
                self.tableWidget.setItem(row_index, 0, item_id)
                #self.tableWidget.setItem(row_index, 0, QTableWidgetItem(str(row[0])))  # Video ID
                self.tableWidget.setItem(row_index, 1, QTableWidgetItem(str(row[1])))  # File Name
                self.tableWidget.setItem(row_index, 2, QTableWidgetItem(str(row[3])))  # Upload Time
                self.hidden_file_paths.append(row[2])  # File Path 저장
        else:
            print("이벤트 유형이 선택되지 않았습니다. 이벤트 유형을 선택하세요.")


    def play_video(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            file_path = self.hidden_file_paths[selected_row]  # 숨겨진 file_path 가져오기
            if os.path.exists(file_path):
                media = self.instance.media_new(file_path)
                self.player.set_media(media)
                self.player.play()
            else:
                print("Selected file does not exist.")

    def display_frame(self, frame, camera_id):
        """
        프레임을 QLabel에 표시하며 텍스트를 추가합니다.
        """
        # 텍스트 정보 수정
        text_ip = f"IP: 192.168.0.4{camera_id}" 
        text_channel = f"대륭3차 카메라{camera_id + 1}번"  # 한글 텍스트

        if frame is None or frame.size == 0:
            print(f"Warning: Empty frame received for camera {camera_id}")
            return

        try:
            # OpenCV BGR -> RGB 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Pillow Image로 변환
            pil_image = Image.fromarray(rgb_frame)
            draw = ImageDraw.Draw(pil_image)

            # 한글 폰트 로드 (시스템에서 사용할 폰트 경로를 지정하세요)
            font_path = "/home/jieun/dev_ws/test_2/NanumGothicBold.ttf"  # 경로 확인 필요
            font = ImageFont.truetype(font_path, 20)

            # 텍스트 추가
            draw.text((10, 10), text_channel, font=font, fill=(0, 255, 0))
            draw.text((10, 40), text_ip, font=font, fill=(0, 255, 0))

            # Pillow 이미지를 OpenCV 형식으로 변환
            rgb_frame = np.array(pil_image)

            # QImage로 변환
            h, w, ch = rgb_frame.shape
            qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # QLabel에 픽스맵 설정
            label = self.label_mapping[camera_id]
            label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setContentsMargins(0, 0, 0, 0)

        except Exception as e:
            print(f"Error displaying frame for camera {camera_id}: {e}")

    def update_fire_server_icon(self, status):
        """
        FireStation 연결 상태에 따라 아이콘 변경
        """
        if status:
            self.fire_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_on.png"))
        else:
            self.fire_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_off.png"))

    def update_police_server_icon(self, status):
        """
        PoliceStation 연결 상태에 따라 아이콘 변경
        """
        if status:
            self.police_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_on.png"))
        else:
            self.police_server_on.setIcon(QIcon("/home/jieun/dev_ws/test_2/ui/light_off.png"))


    def closeEvent(self, event):
        for receiver in self.fire_receivers + self.weapon_receivers + self.frame_receivers:
            receiver.running = False
            receiver.wait()
        self.server_worker.stop()
        self.server_thread.quit()
        self.server_thread.wait()
        self.db.close()
        super().closeEvent(event)


class ServerWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, db_config):
        super().__init__()
        self.running = True
        self.db_config = db_config  # DB 설정 저장

    def stop(self):
        self.running = False

    def run(self):
        server_port = 15009  # 소방서에서 연결할 포트
        print(f"Server is running on port {server_port}...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 포트 재사용 설정
            server_socket.bind(('0.0.0.0', server_port))
            server_socket.listen(5)

            while self.running:
                conn, addr = server_socket.accept()
                print(f"Connection established with {addr}")
                with conn:
                    self.handle_connection(conn)

    def handle_connection(self, conn):
        """
        단일 클라이언트 연결 처리
        """
        try:
            # 요청 데이터 수신
            length = conn.recv(4)
            if not length:
                return
            length = int.from_bytes(length, 'big')
            data = conn.recv(length)
            request = pickle.loads(data)

            if request["action"] == "get_videos":
                event_type = request.get("event_type", "unknown")
                time_range = request.get("time_range", None)  # 시간 범위 추가
                response = self.filter_videos(event_type, time_range)
                response_data = pickle.dumps(response)

                # 응답 전송
                conn.sendall(len(response_data).to_bytes(4, 'big'))
                conn.sendall(response_data)
                print(f"Sent video data for event type: {event_type}, time range: {time_range}")

        except Exception as e:
            print(f"Error handling connection: {e}")

    def filter_videos(self, event_type, time_range):
        """`
        이벤트 유형과 시간 범위에 따라 비디오 데이터를 필터링
        """
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor()

            # 기본 쿼리 설정
            query = f"SELECT video_id, file_name, file_path, upload_time FROM video_metadata WHERE file_name LIKE '{event_type}_%'"

            # 시간 범위 추가
            if time_range:
                time_start = time_range.get("start")
                time_end = time_range.get("end")
                if time_start and time_end:
                    query += f" AND file_name BETWEEN '{event_type}_{time_start}' AND '{event_type}_{time_end}'"

            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            db.close()

            # 결과를 리스트로 반환
            return [{"video_id": row[0], "file_name": row[1], "file_path": row[2], "upload_time": row[3]} for row in rows]
        except Exception as e:
            print(f"Error filtering videos: {e}")
            return []



if __name__ == "__main__":
    def start_flask():
        app.run(host='0.0.0.0', port=5000)  # Flask 서버 실행
        #app.run(host='0.0.0.0', port=5001)  # Flask 서버 실행

    # Flask 서버를 별도의 스레드에서 실행
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # PyQt 애플리케이션 실행
    app = QApplication([])
    window = CentralServerApp(
        fire_ports=[14000, 14001, 14002, 14003],
        weapon_ports=[15000, 15001, 15002, 15003],
        frame_ports=[13000, 13001, 13002, 13003]
    )
    window.show()
    window.setWindowTitle("Central Monitoring Center")
    app.exec_()