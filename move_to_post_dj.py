import cv2
import numpy as np
import time
from math import atan, degrees, atan2
import urllib
import socket
# import cv2.cv as cv
POST_POINTS_FRONT = (1265, 619)  # should hard code before game
POST_POINTS_BACK = (1465, 619)  # should hard code before game
CLOSE_TO_POST_UPPER = (1153, 484)  # should hard code before game
CLOSE_TO_POST_LOWER = (1155, 751)  # should hard code before game
POST_RADIUS = 240
POST_FOUND = False
s = socket.socket()
url = "http://10.7.170.27:8080/shot.jpg"
port = 12345
counter = 0
s.bind(("", port))
WINDOW_NAME = 'move to post'
print "socket binded to %s" % (port)
# # put the socket into listening mode
s.listen(5)
print "socket is listening"

c, addr = s.accept()
print 'Got connection from', addr


def angle_for_dj(point1, point2, post_point):
    a0 = atan2(point2[1] - point1[1], point2[0] - point1[0])
    a1 = atan2(post_point[1] - point1[1], post_point[0] - point1[0])
    return degrees(a1 - a0)


def show_image(image):
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 600, 600)
    cv2.imshow(WINDOW_NAME, image)
    if cv2.waitKey(1) & 0xFF == 27:
        pass


def get_slope(point):
    print point
    print POST_POINTS_FRONT, point
    try:
        slope = (POST_POINTS_FRONT[0] - point[0]) / float((POST_POINTS_FRONT[1] - point[1]))
    except:
        return 90
    print slope
    return degrees(atan(slope))


def get_direction(slopeb, slopef, reversed=False):
    direction = 'right'
    if slopeb > 0 and slopef > 0:
        if slopef > slopeb:
            direction = 'left'
        elif slopeb > slopef:
            direction = 'right'
    elif slopef < 0 and slopeb < 0:
        slopeb = 180 + slopeb
        slopef = 180 + slopef
        if slopef > slopeb:
            direction = 'left'
        elif slopeb > slopef:
            direction = 'right'
    elif slopef < 0 and slopeb > 0:
        slopef = 180 + slopef
        if slopeb < slopef:
            direction = 'left'
        elif slopef < slopeb:
            direction = 'not expected condition please recheck 1'

    elif slopeb < 0 and slopef > 0:
        slopeb = 180 + slopeb
        if slopef < slopeb:
            direction = 'right'
        elif slopeb < slopef:
            direction = 'not expected condition please recheck 2'
    if reversed:
        if direction == 'right':
            direction = 'left'
        else:
            direction = 'right'
    return direction


def goto_post(image):
    '''Accepts BGR image as Numpy array
       Returns: (x,y) coordinates of centroid if found
                (-1,-1) if no centroid was found
                None if user hit ESC
    '''

    global POST_FOUND
    image_x, image_y, color_code = image.shape
    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # hsv for color pink
    lower_front = np.array([141, 60, 171])
    upper_front = np.array([183, 183, 230])

    # hsv for color blue
    lower_back = np.array([90, 100, 100])
    upper_back = np.array([110, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_back, upper_back)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cntsback, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = cv2.inRange(hsv, lower_front, upper_front)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cntsfront, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    centerb = 0
    areab = 0
    radiusb = 0

    if len(cntsback) > 0:
        cntsb = max(cntsback, key=cv2.contourArea)
        ((xb, yb), radiusb) = cv2.minEnclosingCircle(cntsb)
        M = cv2.moments(cntsb)
        centerb = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areab = M["m00"]
    #   if not areab >'some value':  check the area for duble check
    #         centerb = 0, areab=0, radiusb=0


    centerf = 0
    areaf = 0
    radiusf = 0
    if len(cntsfront) > 0:
        cntsf = max(cntsfront, key=cv2.contourArea)
        ((xb, yb), radiusf) = cv2.minEnclosingCircle(cntsf)
        M = cv2.moments(cntsf)
        centerf = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areaf = M["m00"]
        #   if not areab >'some value':  check the area for duble check
        #         centerf = 0, areaf=0, radiusf=0

    # print centerf, centerb
    # cv2.circle(image, centerf, 3, (255, 0, 0), 3)
    # cv2.circle(image, centerb, 3, (255, 0, 0), 3)

    slopef = get_slope(centerf)
    slopeb = get_slope(centerb)
    # ########### Bot position greater than Blind spot area
    print centerb, POST_POINTS_FRONT
    cv2.line(image, centerf, POST_POINTS_FRONT, (0, 255, 0), 3)
    cv2.line(image, centerb, POST_POINTS_FRONT, (0, 255, 0), 3)
    show_image(image)
    angle_for_reference = angle_for_dj(centerb, centerf, POST_POINTS_FRONT)
    angle_for_post = angle_for_dj(centerb, centerf, POST_POINTS_BACK)
    print 'angle for refernce', angle_for_reference
    if centerf[1] > CLOSE_TO_POST_UPPER[1] and centerf[0] > CLOSE_TO_POST_UPPER[0] and\
       centerf[1] < CLOSE_TO_POST_LOWER[1] and centerf[0] > CLOSE_TO_POST_LOWER[0] and\
       centerb[1] > CLOSE_TO_POST_UPPER[1] and centerb[0] > CLOSE_TO_POST_UPPER[0] and\
       centerb[1] < CLOSE_TO_POST_LOWER[1] and centerb[0] > CLOSE_TO_POST_LOWER[0] or \
       POST_FOUND:
        POST_FOUND = True
        if (angle_for_post < 205 and angle_for_post > 165 or
           angle_for_post > -205 and angle_for_post < -165):
            print 'back'
            c.send('back')
            time.sleep(3)
            c.send('stop')
            print 'drop'
            c.send('ball_drop')
        else:
            direction = get_direction(slopeb, slopef, True)
            print direction
            c.send(direction)
            time.sleep(0.1)
            c.send('stop')

    elif angle_for_reference < 25 and angle_for_reference > -25:
        print 'forward'
        c.send('forward')
        time.sleep(1)
    else:
        direction = get_direction(slopeb, slopef)
        print direction
        c.send(direction)
        time.sleep(0.1)
        c.send('stop')


if __name__ == "__main__":

    while True:
        # image = cv2.imread("/home/qburst/robot/entethala.jpg")
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        goto_post(img)
