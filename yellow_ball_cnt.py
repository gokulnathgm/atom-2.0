import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket

url="http://10.7.170.8:8080/shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160

def goto_post(image):
  pass

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
    lower_green = np.array([157, 100, 100])
    upper_green = np.array([177, 255, 255])

    # lower_green = np.array([20, 100, 100])
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
        area = M["m00"]
        peri = cv2.arcLength(cnts1, True)
        approx = cv2.approxPolyDP(cnts1, 0.04 * peri, True)
        print 'approx: ', len(approx)
        print 'radius: ', radius
        print 'area: ', area
        print 'perimeter: ', peri
        img1 = image.copy()
        cv2.drawContours(img1, cnts1, -1, (255,0,0), 3)
        cv2.namedWindow('NEW', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('NEW', 600,600)
        cv2.imshow('NEW', img1)  
        if cv2.waitKey(1) & 0xFF == 27:
            exit
    
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
                print "Move Left"

            elif (image_y / 2) < (ball_x - 500):
                print "Move Right"

            else:
                print "Move Forward"

            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600,600)
            cv2.imshow(WINDOW_NAME, image)  
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
        #            cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        #            cv2.circle(image, center, 5, (255, 0, 0), -1)
    else:
        print 'Seek, right'
    return None


# Test with input from camera
if __name__ == "__main__":

    # camera = cv2.VideoCapture("Robo_videos/ball_tracking_example5.mp4")

    #     capture = cv2.VideoCapture(0)

    while True:

        img = cv2.imread("rose_circle.jpg")
        # (grabbed, img) = image.read()
        # imgResp = urllib.urlopen(url)
        # imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        # img = cv2.imdecode(imgNp,-1)

        track(img)
        # break
        # time.sleep(60)

        #             if not track(image):
        #                 break
        #
        #             if cv2.waitKey(1) & 0xFF == 27:
        #                 break
