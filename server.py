# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct,imutils
from imutils.video import VideoStream
from networking import Network

class VideoServer:
	def __init__(self) -> None:
		self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		host_ip = Network().get_host_ip()
		port = 9999
		self.socket_address = (host_ip,port)
	
	def start_server(self):
		print('Server started in :',self.socket_address[0], ":", self.socket_address[1])
		self.server_socket.bind(self.socket_address)
		self.server_socket.listen(5)
		while True:
			client_socket,addr = self.server_socket.accept()
			try:
				print('GOT CONNECTION FROM:',addr)
				if client_socket:
					cf = VideoStream(-1, resolution=(280,280), framerate=24).start()
					while(cf.stream.isOpened()):
						frame = cf.read()
						frame = imutils.resize(frame,width=280)
						a = pickle.dumps(frame)
						message = struct.pack("Q",len(a))+a
						client_socket.sendall(message)
						if cv2.waitKey(1) == '13':
							client_socket.close()
			except KeyboardInterrupt:
				print("close")
				client_socket.close()
VideoServer().start_server()