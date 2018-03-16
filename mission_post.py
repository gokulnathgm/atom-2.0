import cv2
import numpy as np
import time
from math import sqrt, acos, pi, degrees, atan
import urllib
import socket

POST_POINT = (1809, 569)
MEET_POINT = (1481, 582)
center_front = ()

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
        slopeob = 180 + slopeb
        if slopef < slopeb:
            return 'right'
        elif slopeb < slopef:
            return 'error: not expected condition please recheck 2'


def get_slope(point):
    slope = (POST_POINT[0] - point[0]) / float((POST_POINT[1] - point[1]))
    return  degrees(atan(slope))


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
    return sqrt(((p0[0] - p1[0]) ** 2) + ((p0[0] - p1[1]) ** 2))


def goto_target_point(image, target_point):
    global center_front

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
    radius_back = 0

    if len(cnts_back) > 0:
        cntsb = max(cnts_back, key=cv2.contourArea)
        ((xb, yb), radius_back) = cv2.minEnclosingCircle(cntsb)
        M = cv2.moments(cntsb)
        center_back = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        area_back = M["m00"]
        cv2.circle(image, center_back, 3, (255, 0, 0), 3)
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
        cv2.circle(image, center_front, 3, (255, 0, 0), 3)
        #   if not area_back >'some value':  check the area for double check
        #   center_front = 0, area_front=0, radius_front=0

    cv2.circle(image, MEET_POINT, 3, (255, 0, 0), 3)
    show_image(image)

    # check if bot is in the other half of the MEET_POINT wrt the post
    if center_front[0] < target_point[0] and center_back[0] < target_point[0]:
        print 'Upper Half!'
        angle = three_point_angle(center_back, center_front, target_point)
        print 'Angle: ', angle
        if (angle >= 170 and angle <= 180) and (center_front[0] > center_back[0]):
            print 'Move straight to meet point...'
            return 'forward'
        else:
            slope_front = get_slope(center_front)
            slope_back = get_slope(center_back)
            return get_direction(slope_front, slope_back)

    if center_front[0] > target_point[0] and center_back[0] > target_point[0]:
        print 'Lower Half!'
        angle = three_point_angle(center_back, center_front, target_point)
        print 'Angle: ', angle
        if (angle >= 170 and angle <= 180) and (center_front[0] < center_back[0]):
            print 'Move straight to meet point...'
            return 'forward'
        else:
            slope_front = get_slope(center_front)
            slope_back = get_slope(center_back)
            return get_direction(slope_front, slope_back)
    else:
        print 'Middle region'
        angle = three_point_angle(center_back, center_front, target_point)
        print 'Angle: ', angle
        if angle >= 175 and angle <= 180:
            if (center_back[1] > center_front[1] > target_point[1]) or (
                    center_back[1] > center_front[1] > target_point[1]):
                print 'Move straight to meet point...'
                return 'forward'
            else:
                slope_front = get_slope(center_front)
                slope_back = get_slope(center_back)
                return get_direction(slope_front, slope_back)


if __name__ == "__main__":

    while True:
        # image = cv2.imread("/home/qburst/robot/entethala.jpg")
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        direction = goto_target_point(img, MEET_POINT)
        c.send(direction)
        if direction != 'forward':
            time.sleep(0.15)
            c.send('stop')

        if direction == 'forward':
            distance_bot_meet = two_point_distance(MEET_POINT, center_front)
            print 'distance_bot_target: ', distance_bot_meet
            if distance_bot_meet <= 400:
                print 'Stop the bot!'
                c.send('stop')
                # while True:
                #     direction = goto_target_point(img, POST_POINT)
                #     if direction == 'forward':
                #         distance_bot_post = two_point_distance(POST_POINT, center_front)
                #         if distance_bot_post <= 100:
                #             print 'Drop the ball!'
                #             break
                #     else:
                #         print 'Keep turning to locate the post...'
