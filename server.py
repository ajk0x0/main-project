# This code is for the server 
# Lets import the libraries
import socket, cv2, pickle,struct,imutils
from imutils.video import VideoStream

# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = '192.168.248.94'
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)
# Socket Accept
while True:
	client_socket,addr = server_socket.accept()
	try:
		print('GOT CONNECTION FROM:',addr)
		if client_socket:
			cf = VideoStream(usePiCamera=False,
							resolution=(280,280),
							framerate=24).start()
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
