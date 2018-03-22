import cv2
import numpy as np
import time
from math import atan, atan2, degrees
import urllib
import socket
# import cv2.cv as cv

s = socket.socket()
url = "http://10.7.170.8:8080/shot.jpg"
url_up = "http://10.7.170.27:8080/shot.jpg"

POST_POINTS_FRONT = (1365, 619)  # should hard code before game
CLOSE_TO_POST_UPPER = (1153, 484)  # should hard code before game
CLOSE_TO_POST_LOWER = (1155, 751)  # should hard code before game
WINDOW_NAME = "GreenBallTracker"
POST_RADIUS = 240
port = 12345
counter = 0
# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(("", port))
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


def get_slope(point):
    try:
        slope = ((POST_POINTS_FRONT[0] - point[0]) /
                 float((POST_POINTS_FRONT[1] - point[1])))
    except:
        return 90
    print slope
    return degrees(atan(slope))


def get_direction(slopeb, slopef, reversed=False):
    if slopeb > 0 and slopef > 0:
        if slopef > slopeb:
            direction = 'right'
        elif slopeb > slopef:
            direction = 'left'
    elif slopef < 0 and slopeb < 0:
        slopeb = 180 + slopeb
        slopef = 180 + slopef
        if slopef > slopeb:
            direction = 'right'
        elif slopeb > slopef:
            direction = 'left'
    elif slopef < 0 and slopeb > 0:
        slopef = 180 + slopef
        if slopeb < slopef:
            direction = 'right'
        elif slopef < slopeb:
            direction = 'not expected condition please recheck 1'

    elif slopeb < 0 and slopef > 0:
        slopeb = 180 + slopeb
        if slopef < slopeb:
            direction = 'left'
        elif slopeb < slopef:
            direction = 'not expected condition please recheck 2'
    if reversed:
        if direction == 'right':
            direction = 'left'
        else:
            direction = 'right'
    return direction


def goto_post(image, image_up):

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

    blur = cv2.GaussianBlur(image_up, (5, 5), 0)
    hsv_up = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image for only green colors
    # lower_green = np.array([50, 100, 100])
    # upper_green = np.array([70, 255, 255])

    # hsv for color pink
    lower_front = np.array([141, 60, 171])
    upper_front = np.array([183, 183, 230])

    # hsv for color blue
    lower_back = np.array([90, 100, 100])
    upper_back = np.array([110, 255, 255])

    # Front image post
    mask = cv2.inRange(hsv, lower_back, upper_back)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cnts, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)

    # UP image - Front
    mask = cv2.inRange(hsv_up, lower_front, upper_front)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cntsfront, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

    # UP image - Back
    mask = cv2.inRange(hsv_up, lower_back, upper_back)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, cntsback, _ = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)

    centerb = 0
    areab = 0
    radiusb = 0

    if len(cntsback) > 0:
        cntsb = max(cntsback, key=cv2.contourArea)
        ((xb, yb), radiusb) = cv2.minEnclosingCircle(cntsb)
        M = cv2.moments(cntsb)
        centerb = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
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

    # cnts = cnts[-2]
    slopef = get_slope(centerf)
    slopeb = get_slope(centerb)

    center = None
    nearest_one = (0, 0)
    max_y = 0
    radius = 0
    angle_for_reference = angle_for_dj(centerb, centerf, POST_POINTS_FRONT)

    turn = False
    if len(cnts) > 0:
        # centroid
        cnts1 = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(cnts1)
        M = cv2.moments(cnts1)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        area = M["m00"]
        peri = cv2.arcLength(cnts1, True)
        approx = cv2.approxPolyDP(cnts1, 0.04 * peri, True)
        contour_edges = len(approx)
        print 'approx: ', contour_edges

        # only proceed if the radius meets a minimum size
        if radius > 30 and contour_edges >= 4 and area >= 35:
            # draw the circle and centroid on the frame,
            # then update the list of tracked pointsx 1080 y 1920 3

            nearest_one = (int(x), int(y))
            radius = int(radius)
            print 'radius: ', radius
            cv2.circle(image, nearest_one, 3, (255, 0, 0), 3)
            ball_x, ball_y = nearest_one

            if (image_y / 2) > (ball_x + 500):
                print "Move Left"
                c.send("left")

            elif (image_y / 2) < (ball_x - 500):
                print "Move Right"
                c.send("right")

            else:
                if radius > 170:
                    print 'Drop....'
                    c.send("drop")
                    time.sleep(10)
                elif angle_for_reference < 30 and angle_for_reference > -30:
                    print "Move Forward"
                    c.send("forward")
                else:
                    turn = True

            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, 600, 600)
            cv2.imshow(WINDOW_NAME, image)
            if cv2.waitKey(1) & 0xFF == 27:
                pass
    elif (centerf[0] > CLOSE_TO_POST_UPPER[0] and
          centerf[1] < CLOSE_TO_POST_UPPER[1]):
        if centerf[0] + 20 > centerb[0] and centerf[0] - 20 < centerb[0] and\
           centerf[1] > centerb[1]:
            print "Move Forward"
            c.send("forward")
        else:
            print "Move Right"
            c.send("right")
    elif (centerf[0] > CLOSE_TO_POST_LOWER[0] and
          centerf[1] > CLOSE_TO_POST_LOWER[1]):
        if centerf[0] + 20 > centerb[0] and centerf[0] - 20 < centerb[0] and\
           centerf[1] < centerb[1]:
            print "Move Forward"
            c.send("forward")
        else:
            print "Move Right"
            c.send("right")
    else:
        direction = get_direction(slopeb, slopef)
        c.send(direction)
        print 'Seek'
    if turn:
        direction = get_direction(slopeb, slopef)
        c.send(direction)
        print 'Seek'
    return None


if __name__ == "__main__":

    # camera = cv2.VideoCapture("Robo_videos/ball_tracking_example5.mp4")

    #     capture = cv2.VideoCapture(0)

    while True:

        # image = cv2.imread("1.jpg")
        # (grabbed, frame) = image.read()
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)

        imgResp = urllib.urlopen(url_up)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img_up = cv2.imdecode(imgNp, -1)

        goto_post(img, img_up)
