import socket,cv2, pickle,struct
from networking import Network

class VideoClient:
    def __init__(self) -> None:
        self.network = Network()
        self.host_ip = self.network.get_host_ip()
        self.port = 9999
        self.camera = cv2.VideoCapture(-1)

    def start_stream(self, width, height) -> None:
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.connect((self.host_ip,self.port)) 
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
                while len(data) < payload_size:
                        packet = client_socket.recv(254*1024) # 4Kb
                        if not packet: break
                        data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]
                while len(data) < msg_size:
                        data += client_socket.recv(254*1024)
                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)

                cv2.namedWindow("RECEIVING VIDEO", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("RECEIVING VIDEO", width, height)
                cv2.imshow("RECEIVING VIDEO",frame)
                cv2.moveWindow("RECEIVING VIDEO", 40,30)
                cv2.resizeWindow("Resized_Window", width, height)
                if str(cv2.waitKey(1)) == '13':
                        client_socket.close()
                        cv2.getWindowProperty("RECEIVING VIDEO", 0)
                        cv2.destroyAllWindows()
                        return

    def getFrame(self):
        ret, frame = self.camera.read()
        if not ret:
                print("Failed to capture frame")
                return None
        else: return frame
