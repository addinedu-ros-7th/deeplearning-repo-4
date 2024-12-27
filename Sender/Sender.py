import cv2
import socket
import threading
import pickle
import time
class SenderServer:
    def __init__(self, device_paths=["/dev/video0", "/dev/video2", "/dev/video4", "/dev/video6"],
                 fire_station_ports=[11000, 11001, 11002, 11003],
                 police_station_ports=[12000, 12001, 12002, 12003],
                 central_server_ports=[13000, 13001, 13002, 13003],
                 fire_station_ip="192.168.0.45",  #192.168.0.18
                 police_station_ip="192.168.0.45", #192.168.0.18
                 central_server_ip="192.168.0.214"): #192.168.0.151
        self.device_paths = device_paths
        self.fire_station_ports = fire_station_ports
        self.police_station_ports = police_station_ports
        self.central_server_ports = central_server_ports
        self.fire_station_ip = fire_station_ip
        self.police_station_ip = police_station_ip
        self.central_server_ip = central_server_ip
        self.running = True
    def send_frame(self, frame, target_ip, port):
        target_address = (target_ip, port)
        timestamp = time.time()  # 타임스탬프 추가
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect(target_address)
                _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])  # 품질 설정 (0~100)
                data = pickle.dumps((timestamp, encoded_frame))
                tcp_socket.sendall(len(data).to_bytes(4, 'big') + data)
                response = tcp_socket.recv(1024).decode()
                print(f"Response from {target_address}: {response}")
        except Exception as e:
            print(f"Error sending data to {target_address}: {e}")
    def stream_from_camera(self, device_path, fire_port, police_port, central_port):
        cap = cv2.VideoCapture(device_path)
        if not cap.isOpened():
            print(f"Cannot open camera {device_path}")
            return
        print(f"Streaming from {device_path} to ports {fire_port}, {police_port}, and {central_port}")
        while self.running:
            ret, frame = cap.read()
            if ret:
                resized_frame = cv2.resize(frame, (680, 480))
                # 소방서, 경찰서, 중앙서버로 프레임 전송
                threading.Thread(target=self.send_frame, args=(resized_frame, self.fire_station_ip, fire_port)).start()
                threading.Thread(target=self.send_frame, args=(resized_frame, self.police_station_ip, police_port)).start()
                threading.Thread(target=self.send_frame, args=(resized_frame, self.central_server_ip, central_port)).start()
                time.sleep(1 / 15)  # 15FPS
        cap.release()
    def start_streaming(self):
        threads = []
        for device_path, fire_port, police_port, central_port in zip(
            self.device_paths, self.fire_station_ports, self.police_station_ports, self.central_server_ports):
            thread = threading.Thread(target=self.stream_from_camera, args=(device_path, fire_port, police_port, central_port))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    def stop(self):
        self.running = False
if __name__ == "__main__":
    sender = SenderServer()
    try:
        sender.start_streaming()
    except KeyboardInterrupt:
        sender.stop()