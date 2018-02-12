# Import socket module
import socket
from serial import Serial
import time
 
bot = Serial("/dev/ttyACM0")

# Create a socket object
s = socket.socket()         
 
# Define the port on which you want to connect
port = 12345
 
# connect to the server on local computer
s.connect(("10.7.170.21", port))
 
#receive data from the server
while True:
	msg = s.recv(64)
	if len(msg):
		if msg.startswith("left"):
			print 'Left'
			bot.write("l")
		elif msg.startswith("right"):
			print 'Right'
			bot.write("r")
		elif msg.startswith("forward"):
			print 'Forward'
			bot.write("f")
		elif msg.startswith("drop"): 
			print 'Drop'
                        bot.write("r")
			time.sleep(2.2)
			bot.write("b")
			time.sleep(2.5)
			bot.write("d")
		elif msg.startswith("initial"):
			print "Initial"
			bot.write("f")
			time.sleep(4)
			bot.write("b")
			time.sleep(6)
			bot.write("s")
			bot.write("d")
# close the connection
s.close()   
