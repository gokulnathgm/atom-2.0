import cv2
import numpy as np
import time
from math import atan, degrees, sqrt, acos, pi
import urllib
import socket
from datetime import datetime
import sys

s = socket.socket()
print "Socket successfully created"

url = "http://10.7.170.8:8080/shot.jpg"
url_top = "http://10.7.170.27:8080/shot.jpg"

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
POST_POINT = (1379, 506)
MEET_POINT = (1078, 551)
POST_EDGE1 = (1364, 460)
POST_EDGE2 = (1361, 566)
CORNER_POINT1 = (1249, 93)
CORNER_POINT2 = (1259, 921)


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
        slope = (MEET_POINT[0] - point[0]) / float((MEET_POINT[1] - point[1]))
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


def goto_target_point(image, target_point):
    global center_front, center_back

    image_x, image_y, color_code = image.shape
    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # hsv for color pink
    # lower_front = np.array([141, 60, 171])
    # upper_front = np.array([183, 183, 230])

    lower_front = np.array([150, 100, 100])
    upper_front = np.array([170, 255, 255])

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
    cv2.drawContours(img, cnts_front, -1, (0, 255, 0), 3)
    # cv2.waitKey(0)
    center_back = 0
    area_back = 0

    if len(cnts_back) > 0:
        found_contour = False
        for cntsb in cnts_back:
            M = cv2.moments(cntsb)
            area_back = M["m00"]
            if area_back >= AREA_LOWER and area_back <= AREA_UPPER:
                print "MY AREA BACK", area_back
                found_contour = True
                break
        if not found_contour:
            return 'stop'
        center_back = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if center_back != 0:
            cv2.circle(image, center_back, 3, (255, 0, 0), 3)
        else:
            return 'stop'

    center_front = 0
    area_front = 0

    if len(cnts_front) > 0:
        found_contour = False
        for cntsf in cnts_front:
            M = cv2.moments(cntsf)
            area_front = M["m00"]
            if area_front >= AREA_LOWER and area_front <= AREA_UPPER:
                print "MY AREA FRONT", area_front
                found_contour = True
                break
        if not found_contour:
            return 'stop'
        center_front = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if center_front != 0:
            cv2.circle(image, center_front, 3, (255, 0, 0), 3)
        else:
            return 'stop'

    cv2.circle(image, MEET_POINT, 3, (255, 0, 0), 3)
    show_image(image)
    if center_back == 0 or center_front == 0:
        return 'stop'
    # check if bot is in the other half of the MEET_POINT wrt the post
    if center_front[0] < target_point[0] and center_back[0] < target_point[0]:
        print 'Upper Half!'
        angle = three_point_angle(center_back, center_front, target_point)
        print 'Angle: ', angle
        if (angle >= 165 and angle <= 180) and (center_front[0] > center_back[0]):
            print 'Move straight to meet point...'
            return 'forward'
        else:
            slope_front = get_slope(center_front)
            slope_back = get_slope(center_back)
            return get_direction(slope_front, slope_back)

    if center_front[0] > target_point[0] and center_back[0] > target_point[0]:
        print 'Lower Half!'
        angle = three_point_angle(center_back, center_front, MEET_POINT)
        print 'Angle: ', angle
        if (angle >= 165 and angle <= 180) and (center_front[0] < center_back[0]):
            return 'forward'
        else:
            slope_front = get_slope(center_front)
            slope_back = get_slope(center_back)
            return get_direction(slope_front, slope_back)
    else:
        print 'Middle region'
        angle = three_point_angle(center_back, center_front, target_point)
        print 'Angle: ', angle
        if angle >= 165 and angle <= 180:
            if (center_back[1] > center_front[1] > target_point[1]) or (
                    center_back[1] > center_front[1] > target_point[1]):
                print 'Move straight to meet point...'
                return 'forward'
        slope_front = get_slope(center_front)
        slope_back = get_slope(center_back)
        return get_direction(slope_front, slope_back)

def goto_post(image):
    global time_counter

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

    _, cnts, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
        if radius > 30:  # and contour_edges >= 4 and area >= 35:
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
                if radius > 165:
                    print "Post: Drop"
                    c.send("drop")
                    time.sleep(10)
                    time_counter = datetime.now()
                    return "drop"
                else:
                    print "Post: Move Forward"
                    c.send("forward")
                    time.sleep(0.15)
                    c.send("stop")
                    return "forward"

            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600, 600)
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
    if delta.seconds > 1:
        status = ''

        while True:
            imgResp = urllib.urlopen(url_top)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)
            direction = goto_target_point(img, MEET_POINT)
            if direction.endswith('_down'):
                direction = direction.replace('_down', '')
            print 'direction: ', direction
            c.send(direction)
            if direction != 'forward':
                time.sleep(0.15)
                c.send('stop')
            if center_front == 0:
                return None
            distance_bot_meet = two_point_distance(MEET_POINT, center_front)
            print 'distance_bot_target: ', distance_bot_meet
            if distance_bot_meet <= 80:
                c.send('stop')
                break

        while True:
            if status == 'drop':
                image = img
                break
            imgResp = urllib.urlopen(url)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)
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
