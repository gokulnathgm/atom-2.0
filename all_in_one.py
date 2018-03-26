import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket
from datetime import datetime
import sys

s = socket.socket()
print "Socket successfully created"

url = "http://10.7.170.8:8080/shot.jpg"
# url="http://10.7.120.82:8080//shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160
port = 12345
time_counter = 0
initial = True
s.bind(("", port))
s.listen(5)
print "socket is listening"
c, addr = s.accept()
print 'Got connection from', addr

AREA_LOWER = 0
AREA_UPPER = 3000
POST_POINT = (1368, 520)
MEET_POINT = (1118, 525)
POST_EDGE1 = (1365, 398)
POST_EDGE2 = (1364, 618)
CORNER_POINT1 = (1244, 100)
CORNER_POINT2 = (1269, 929)
center_front, center_back = (), ()

url = "http://10.7.170.27:8080/shot.jpg"
WINDOW_NAME = 'Aerial View'

port = 12345
s = socket.socket()
s.bind(("", port))
s.listen(5)
print "socket is listening"

c, addr = s.accept()
print 'Got connection from', addr


def get_direction(slopef, slopeb):
    print 'slopef: ', slopef
    print 'slopeb: ', slopeb
    if slopeb == slopef:
        return "Condition not handled yet"
    if slopeb > 0 and slopef > 0:
        if slopef > slopeb:
            return 'left'
        elif slopeb > slopef:
            return 'right'

    elif slopef < 0 and slopeb < 0:
        slopeb = 180 + slopeb
        slopef = 180 + slopef
        if slopef > slopeb:
            return 'left'
        elif slopeb > slopef:
            return 'right'

    elif slopef < 0 and slopeb > 0:
        slopef = 180 + slopef
        if slopeb < slopef:
            return 'left'
        elif slopef < slopeb:
            return 'error: not expected condition please recheck 1'

    elif slopeb < 0 and slopef > 0:
        slopeb = 180 + slopeb
        if slopef < slopeb:
            return 'right'
        elif slopeb < slopef:
            return 'error: not expected condition please recheck 2'


def get_slope(point):
    try:
        slope = (POST_POINT[0] - point[0]) / float((POST_POINT[1] - point[1]))
    except:
        return 90
    return degrees(atan(slope))


def show_image(image):
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 600, 600)
    cv2.imshow(WINDOW_NAME, image)
    if cv2.waitKey(1) & 0xFF == 27:
        pass
        # cv2.waitKey(0)


def three_point_angle(p0, p1, p2):
    a = (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2
    b = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    c = (p2[0] - p0[0]) ** 2 + (p2[1] - p0[1]) ** 2
    return acos((a + b - c) / sqrt(4 * a * b)) * 180 / pi


def two_point_distance(p0, p1):
    return sqrt(((p0[0] - p1[0]) ** 2) + ((p0[1] - p1[1]) ** 2))


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
        status = False

        while True:
            lower = False
            imgResp = urllib.urlopen(url)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)
            direction = goto_target_point(img, MEET_POINT)
            print 'direction: ', direction, center_front
            pos = 'bottom' if center_front[1] > POST_POINT[1] else 'top'
            if direction.endswith('_down'):
                lower = True
                direction = direction.replace('_down', '')
            print 'direction: ', direction
            c.send(direction)
            if direction != 'forward':
                time.sleep(0.15)
                c.send('stop')
            distance_bot_meet = two_point_distance(MEET_POINT, center_front)
            print 'distance_bot_target: ', distance_bot_meet
            if distance_bot_meet <= 80:
                c.send('stop')
                while True:
                    direction_to_post = goto_target_point(img, POST_POINT)
                    c.send(direction_to_post)
                    if direction != 'forward':
                        time.sleep(0.15)
                        c.send('stop')
                    distance_bot_post = two_point_distance(POST_POINT, center_front)
                    print 'distance_bot_post: ', distance_bot_post
                    if distance_bot_post <= 150:
                        # c.send('stop')
                        c.send('dump')
                        print 'Drop command to be executed....................................'
                        status = True
                        break
                    imgResp = urllib.urlopen(url)
                    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
                    img = cv2.imdecode(imgNp, -1)
            if status:
                break
            if direction == 'forward':
                print pos, '*******************'
                print 'center_front', center_front[1]
                if lower:
                    if center_back[1] >= POST_EDGE1[1] and center_back[1] <= POST_EDGE2[1]:
                        print 'center_back', center_back[1]
                        c.send("stop")
                        break

                # distance_bot_meet = two_point_distance(MEET_POINT, center_front)
                # print 'distance_bot_target: ', distance_bot_meet
                # if distance_bot_meet <= 80:
                #     print 'Stop the bot!'
                #     c.send('stop')
                #     time.sleep(20)

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

    _, cnts, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
            cv2.resizeWindow(WINDOW_NAME, 600, 600)
            cv2.imshow(WINDOW_NAME, image)
            if cv2.waitKey(1) & 0xFF == 27:
                center = None
    else:
        c.send('right')
    return None


if __name__ == "__main__":
    pause = raw_input("Start?")
    time_counter = datetime.now()
    while True:
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        track(img)
