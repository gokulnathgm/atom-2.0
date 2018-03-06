import cv2
import numpy as np
import time
from math import sqrt, acos, pi
import urllib
import socket

POST_POINT = ()
MEET_POINT = ()

url = "http://10.7.170.27:8080/shot.jpg"

def three_point_angle(p0, p1, p2)
    a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
    return acos( (a+b-c) / sqrt(4*a*b) ) * 180/pi

def two_point_distance(p0, p1):
    return sqrt(((p0[0] - p1[0])**2)  - ((p0[0] - p[1])**2))

def goto_meet_point(image):

    image_x, image_y, color_code = image.shape
    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    #hsv for color pink
    lower_front = np.array([141, 60, 171])
    upper_front = np.array([183, 183, 230])

    # hsv for color blue
    lower_back = np.array([90, 100, 100])
    upper_back = np.array([110, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_back, upper_back)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cnts_back, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    mask = cv2.inRange(hsv, lower_front, upper_front)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cnts_front, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    center_back = 0
    area_back = 0
    radius_back = 0

    if len(cnts_back) > 0:
        cntsb = max(cnts_back, key=cv2.contourArea)
        ((xb,yb), radius_back) = cv2.minEnclosingCircle(cntsb)
        M = cv2.moments(cntsb)
        center_back = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        area_back = M["m00"]
        #   if not area_back >'some value':  check the area for duble check
        #   center_back = 0, area_back=0, radius_back=0


    center_front = 0
    area_front = 0
    radius_front = 0

    if len(cnts_front) > 0:
        cntsf = max(cnts_front, key=cv2.contourArea)
        ((xb, yb), radius_front) = cv2.minEnclosingCircle(cntsf)
        M = cv2.moments(cntsf)
        center_front = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        area_front = M["m00"]
        #   if not area_back >'some value':  check the area for duble check
        #   center_front = 0, area_front=0, radius_front=0

    #check if bot is in the other half of the MEET_POINT wrt the post
    if center_front[0] < MEET_POINT[0] and center_back[0] < MEET_POINT[0]:
        print 'Upper Half!'
        angle = three_point_angle(center_back, center_front, MEET_POINT)
        if (angle >= 170 and angle <= 180) and (center_front[0] > center_back[0]):
            print 'Move straight to meet point...'
            return 'forward'
        else:
            print 'Turn to find a suitable angle...'
            return 'right'

    if center_front[0] > MEET_POINT[0] and center_back[0] > MEET_POINT[0]:
        print 'Lower Half!'
        angle = three_point_angle(center_back, center_front, MEET_POINT)
        if (angle >= 170 and angle <= 180) and (center_front[0] < center_back[0]):
            print 'Move straight to meet point...'
            return 'forward'
        else:
            print 'Turn to find a suitable angle...'
            return 'right'
    else:
        print 'Middle region'
        angle = three_point_angle(center_back, center_front, MEET_POINT)
        if angle >= 170 and angle <= 180:
            if (center_back[1] > center_front[1] > MEET_POINT[1]) or (center_back[1] > center_front[1] > MEET_POINT[1])
                print 'Move straight to meet point...'
                return 'forward'
            else:
                print 'Turn to find a suitable angle...'
                return 'right'


if __name__ == "__main__":

    while True:
        # image = cv2.imread("/home/qburst/robot/entethala.jpg")
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        direction = goto_meet_point(img)
        if direction == 'forward':
            distance_bot_meet = two_point_distance(MEET_POINT, center_front)
            if distance_bot_meet <=100:
                print 'Stop the bot!'

