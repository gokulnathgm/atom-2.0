import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket
# import cv2.cv as cv

s = socket.socket()         
# print "Socket successfully created"

url="http://10.7.170.8:8080/shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160
port = 12345

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

def calculate_time(image_x, image_y, ball_x, ball_y):
    slope = 0
    angle = 0
    slope = (image_x - ball_y) / (image_y - ball_x)
    print 'image: ', image_x, image_y
    print 'ball: ', ball_x, ball_y
    angle = atan(degrees(slope))
    print 'angle: ', angle
    time = angle/180.0
    return time

def track(image):

    no_circle = False
    '''Accepts BGR image as Numpy array
       Returns: (x,y) coordinates of centroid if found
                (-1,-1) if no centroid was found
                None if user hit ESC
    '''

    image_x, image_y, color_code = image.shape
    print 'x', image_x, 'y', image_y, color_code

    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image for only green colors
    lower_green = np.array([10, 100, 100])
    upper_green = np.array([40, 255, 255])

    # lower_green = np.array([10, 100, 100])
    # upper_green = np.array([40, 255, 255])


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
    
        # only proceed if the radius meets a minimum size
        if radius > 30:
            # draw the circle and centroid on the frame,
            # then update the list of tracked pointsx 1080 y 1920 3

            nearest_one = (int(x), int(y))
            radius = int(radius)
            print 'radius: ', radius
            print 'nearest one: ', nearest_one
            cv2.circle(image, nearest_one, 3, (255, 0, 0), 3)
            ball_x, ball_y = nearest_one

            if (image_y / 2) > (ball_x + 300):
                turn_time = calculate_time(image_x, image_y, ball_x, ball_y)
                # c.send("left " + str(turn_time))
                c.send('left')
                print "Move Left"
                # direction = "left"
                # if combi_move:
                #     time.sleep(0.5)
                #     c.send("forward")

            elif (image_y / 2) < (ball_x - 300):
                turn_time = calculate_time(image_x, image_y, ball_x, ball_y)
                # c.send("right " + str(turn_time))
                c.send('right')
                print "Move Right"
                # direction = "right"
                # if combi_move:
                #     time.sleep(0.5)
                #     c.send("forward")

            else:
                print "Move Forward"
                c.send("forward")
                # if radius >= PICK_RADIUS:
                #     print "pick"
                #     c.send("pick")
                #     time.sleep(2)
                #     return "pick"
                # else:
                #     c.send("forward")

            cv2.imshow(WINDOW_NAME, image)  
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
        #            cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        #            cv2.circle(image, center, 5, (255, 0, 0), -1)
    else:
        c.send('right')
    return None


# Test with input from camera
if __name__ == "__main__":

    # camera = cv2.VideoCapture("Robo_videos/ball_tracking_example5.mp4")

    #     capture = cv2.VideoCapture(0)

    while True:

        # image = cv2.imread("1.jpg")
        # (grabbed, frame) = image.read()
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img = cv2.imdecode(imgNp,-1)

        track(img)
        # time.sleep(0.25)

        #             if not track(image):
        #                 break
        #
        #             if cv2.waitKey(1) & 0xFF == 27:
        #                 break
