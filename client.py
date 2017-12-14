# Import socket module
import socket
from serial import Serial
 
bot = Serial("/dev/ttyACM0")

# Create a socket object
s = socket.socket()         
 
# Define the port on which you want to connect
port = 12345
 
# connect to the server on local computer
s.connect(("10.7.30.6", port))
 
#receive data from the server
while True:
	msg = s.recv(64)
	if len(msg):
		if msg.startswith("left"):
			turn_time = msg.split(" ")[1]
			turn_time = float(turn_time)
			bot.write("l")
			time.sleep(turn_time)
			bot.write("s")
		elif msg.startswith("right"):
			turn_time = msg.split(" ")[1]
			turn_time = float(turn_time)
			bot.write("r")
			time.sleep(turn_time)
			bot.write("s")
		elif msg.startswith("forward"):
			turn_time = msg.split(" ")[1]
			turn_time = float(turn_time)
			bot.write("f")
			time.sleep(turn_time)
			bot.write("s")
		elif msg.startswith("pick"):
			# TODO: Pick logic 
			pass

# close the connection
s.close()   
