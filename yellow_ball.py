import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket
# import cv2.cv as cv

s = socket.socket()         
print "Socket successfully created"

url="http://10.7.170.8:8080/shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160
port = 12345
counter = 0
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
    image_x, image_y, color_code = image.shape
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([130, 255, 255])
    _,cnts,_ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts,_ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    nearest_one = (0, 0)
    radius = 0
    if len(cnts) > 0:
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        nearest_one = (int(x), int(y))
        if radius < 30:
            print 'move forward'
            c.send("forward")
            return False

        else:
            print 'Drop the ball'
            return True

    else:
        # hard code the time to sleep
        print 'move left'
        c.send("left")
        return False

def track(image):
    global counter

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
    lower_green = np.array([20, 100, 100])
    upper_green = np.array([30, 255, 255])

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

            if (image_y / 2) > (ball_x + 500):
                # c.send("left " + str(turn_time))
                time.sleep(2)
                c.send('left')
                print "Move Left"
                # direction = "left"
                # if combi_move:
                #     time.sleep(0.5)
                #     c.send("forward")

            elif (image_y / 2) < (ball_x - 500):
                # c.send("right " + str(turn_time))
                time.sleep(2)
                c.send('right')
                print "Move Right"
                # direction = "right"
                # if combi_move:
                #     time.sleep(0.5)
                #     c.send("forward")

            else:
                print 'counter: ', counter
                counter += 1
                print "Move Forward"
                c.send("forward")
                # if radius >= PICK_RADIUS:
                #     print "pick"
                #     c.send("pick")
                #     time.sleep(2)
                #     return "pick"
                # else:
                #     c.send("forward")

            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600,600)
            cv2.imshow(WINDOW_NAME, image)  
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
        #            cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        #            cv2.circle(image, center, 5, (255, 0, 0), -1)
    else:
        if counter > 200:
            goto_post(image)
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
