import cv2
import numpy as np
import time
from math import atan, degrees, atan2
import urllib
import socket
# import cv2.cv as cv
POST_POINTS = (1388, 598) #should hard code before game
POST_RADIUS = 240

# s = socket.socket()
url = "http://10.7.170.27:8080/shot.jpg"
WINDOW_NAME = 'post'
port = 12345
s = socket.socket()
s.bind(("", port))
s.listen(5)
print "socket is listening"

c, addr = s.accept()
print 'Got connection from', addr

def angle_for_dj(point1, point2):
    a0 = atan2(point2[1] - point1[1], point2[0] - point1[0])
    a1 = atan2(POST_POINTS[1] - point1[1], POST_POINTS[0] - point1[0])
    return degrees(a1 - a0)


def show_image(image):
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 600, 600)
    cv2.imshow(WINDOW_NAME, image)
    if cv2.waitKey(1) & 0xFF == 27:
        pass

def get_slope(point):
    slope = (POST_POINTS[0] - point[0]) / float((POST_POINTS[1] - point[1]))
    print slope
    return  degrees(atan(slope))

def move_towardds_post(image):
    '''Accepts BGR image as Numpy array
       Returns: (x,y) coordinates of centroid if found
                (-1,-1) if no centroid was found
                None if user hit ESC
    '''

    image_x, image_y, color_code = image.shape
    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    #hsv for color pink
    lower_front = np.array([157, 100, 100])
    upper_front = np.array([177, 255, 255])

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
    if len(cntsback) >0:
        cntsb = max(cntsback, key=cv2.contourArea)
        ((xb,yb), radiusb) = cv2.minEnclosingCircle(cntsb)
        M = cv2.moments(cntsb)
        centerb = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areab = M["m00"]
    #   if not areab >'some value':  check the area for duble check
    #         centerb = 0, areab=0, radiusb=0

    centerf = 0
    areaf = 0
    radiusf = 0
    if len(cntsfront) >0:
        cntsf = max(cntsfront, key=cv2.contourArea)
        ((xb, yb), radiusf) = cv2.minEnclosingCircle(cntsf)
        M = cv2.moments(cntsf)
        centerf = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areaf = M["m00"]
        #   if not areab >'some value':  check the area for duble check
        #         centerf = 0, areaf=0, radiusf=0

    cv2.line(image, centerf, POST_POINTS, (0, 255, 0), 3)

    cv2.line(image, centerb, POST_POINTS, (0, 255, 0), 3)
    show_image(image)

    slopef = get_slope(centerf)
    slopeb = get_slope(centerb)
    print "slopeF " + str(slopef), "slopeB " + str(slopeb)
    if slopeb == slopef:
        print "Condition not handled yet"
    if slopeb>0 and slopef>0:
        if slopef > slopeb:
            print 'left'
            c.send('left')
        elif slopeb >slopef:
            print 'right'
            c.send('right')

    elif slopef<0 and slopeb<0:
        slopeb = 180+slopeb
        slopef = 180+slopef
        if slopef > slopeb:
            print 'left'
            c.send('left')
        elif slopeb > slopef:
            print 'right'
            c.send('right')

    elif slopef <0 and slopeb>0:
        slopef = 180+slopef
        if slopeb < slopef:
            print 'left'
            c.send('left')
        elif slopef < slopeb:
            print 'not expected condition please recheck 1'

    elif slopeb <0 and slopef>0:
        slopeob = 180+slopeb
        if slopef <slopeb:
            print 'right'
            c.send('right')
        elif slopeb <slopef:
            print 'not expected condition please recheck 2'


if __name__ == "__main__":

    while True:
        # image = cv2.imread("/home/qburst/robot/entethala.jpg")
        imgResp = urllib.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        move_towardds_post(img)


