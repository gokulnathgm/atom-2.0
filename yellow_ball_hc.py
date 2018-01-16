import cv2
import numpy as np
import time
from math import atan, degrees
import urllib
import socket

url="http://10.7.170.8:8080/shot.jpg"

WINDOW_NAME = "GreenBallTracker"
PICK_RADIUS = 160

def track(image):
    max_y = 0

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

    circles = cv2.HoughCircles(bmask, cv2.HOUGH_GRADIENT, 1, 30, param1=20, param2=30, minRadius=20, maxRadius=200)
    if circles is not None:
        # Need to understand what it is doing here
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if max_y < i[1] + i[2]:
                max_y = i[1] + i[2]
                nearest_one = (i[0], i[1])
                radius = i[2]
                print "radius", radius
    else:
        no_circle = True
        print "no circle"

    # Plotting the nearest Circle
    if not no_circle:
        cv2.circle(image, nearest_one, int(radius), (0, 255, 0), 2)
        # Logic for moving right and left
        ball_x, ball_y = nearest_one
        print 'nearest: ', nearest_one

        if (image_y / 2) > (ball_x + radius):
            print "Move Left"

        elif (image_y / 2) < (ball_x - radius):
            print "Move Right"

        else:
            print "Move Forward"

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 600,600)
        cv2.circle(image, nearest_one, 3, (255, 255, 255), 3)

        cv2.imshow(WINDOW_NAME, image)

        if cv2.waitKey(1) & 0xFF == 27:
            center = None

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
