import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket
from datetime import datetime
import sys
# import cv2.cv as cv

s = socket.socket()         
print "Socket successfully created"

url="http://10.7.170.8:8080/shot.jpg"
# url="http://10.7.120.82:8080//shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160
port = 12345
time_counter = 0
initial = True
# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests 
# coming from other computers on the network
s.bind(("", port))        
# print "socket binded to %s" %(port)
 
# # put the socket into listening mode
s.listen(5)     
print "socket is listening"  

c, addr = s.accept()     
print 'Got connection from', addr

def goto_post(image):
    global time_counter

    '''Accepts BGR image as Numpy array
       Returns: (x,y) coordinates of centroid if found
                (-1,-1) if no centroid was found
                None if user hit ESC
    '''

    image_x, image_y, color_code = image.shape
    # print 'x', image_x, 'y', image_y, color_code

    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower_green = np.array([90, 100, 100])
    upper_green = np.array([110, 255, 255])


    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)

    _,cnts,_ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # cnts = cnts[-2]
    center = None
    nearest_one = (0, 0)
    max_y = 0
    radius = 0

    if len(cnts) > 0:
        cnts1 = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(cnts1)
        M = cv2.moments(cnts1)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # area = M["m00"]
        # peri = cv2.arcLength(cnts1, True)
        # approx = cv2.approxPolyDP(cnts1, 0.04 * peri, True)
        # contour_edges = len(approx)
        # print 'approx: ', contour_edges
    
        # only proceed if the radius meets a minimum size
        if radius > 30:# and contour_edges >= 4 and area >= 35:
            # draw the circle and centroid on the frame,
            # then update the list of tracked pointsx 1080 y 1920 3

            nearest_one = (int(x), int(y))
            radius = int(radius)
            print 'radius: ', radius
            cv2.circle(image, nearest_one, 3, (255, 0, 0), 3)
            ball_x, ball_y = nearest_one

            if (image_y / 2) > (ball_x + 500):
                print "Post: Move Left"
                c.send("left")
                time.sleep(0.15)
                c.send("stop")
                return "left"

            elif (image_y / 2) < (ball_x - 500):
                print "Post: Move Right"
                c.send("right")
                time.sleep(0.15)
                c.send("stop")
                return "right"

            else:
                if radius > 155:
                    print "Post: Drop"
                    c.send("drop")
                    time.sleep(10)
                    time_counter = datetime.now()
                    return "drop"
                else:
                    print "Post: Move Forward"
                    c.send("forward")
                    return "forward"


            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600,600)
            cv2.imshow(WINDOW_NAME, image)  
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
    else:
        print 'Post: Seek, right'
        c.send("right")
        return "right"

def track(image):
    global time_counter, initial
    if len(sys.argv) > 1 and initial:
        initial = False
        c.send("initial")
        time.sleep(14)
        time_counter = datetime.now()
    delta = datetime.now() - time_counter
    print 'Delta: ', delta.seconds
    if delta.seconds > 20:
        status = ''
        while True:
            if status == 'drop':
                image = img
                break
            imgResp = urllib.urlopen(url)
            imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
            img = cv2.imdecode(imgNp,-1)
            status = goto_post(img)

    image_x, image_y, color_code = image.shape
    # print 'x', image_x, 'y', image_y, color_code

    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image for only green colors
    lower_green = np.array([20, 100, 100])
    upper_green = np.array([30, 255, 255])


    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)

    _,cnts,_ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # cnts = cnts[-2]
    center = None
    nearest_one = (0, 0)
    max_y = 0
    radius = 0

    if len(cnts) > 0:
        # centroid
        cnts1 = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(cnts1)
        M = cv2.moments(cnts1)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        peri = cv2.arcLength(cnts1, True)
        approx = cv2.approxPolyDP(cnts1, 0.04 * peri, True)
        contour_edges = len(approx)
        # only proceed if the radius meets a minimum size
        if radius > 30 and contour_edges >= 4: 

            # draw the circle and centroid on the frame,
            # then update the list of tracked pointsx 1080 y 1920 3

            nearest_one = (int(x), int(y))
            radius = int(radius)
            print 'radius: ', radius
            print 'nearest one: ', nearest_one
            cv2.circle(image, nearest_one, 3, (255, 0, 0), 3)
            ball_x, ball_y = nearest_one

            if (image_y / 2) > (ball_x + 500):
                c.send('left')
                print "Move Left"

            elif (image_y / 2) < (ball_x - 500):
                c.send('right')
                print "Move Right"

            else:
                c.send("forward")
                print "Move Forward"

            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600,600)
            cv2.imshow(WINDOW_NAME, image)  
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
    else:
        c.send('right')
    return None


# Test with input from camera
if __name__ == "__main__":
    pause = raw_input("Start?")
    # camera = cv2.VideoCapture("Robo_videos/ball_tracking_example5.mp4")

    #     capture = cv2.VideoCapture(0)
    time_counter = datetime.now()
    while True:
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img = cv2.imdecode(imgNp,-1)
        track(img)