import cv2
import numpy as np

# For OpenCV2 image display
import time

WINDOW_NAME = 'GreenBallTracker'
CENTROID = 640


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
    lower_green = np.array([20, 100, 100])
    upper_green = np.array([200, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)

    cnts = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = cnts[-2]
    center = None
    nearest_one = (0, 0)
    max_y = 0
    radius = 0

    # if len(cnts) > 0:
    #     # centroid
    #     c = max(cnts, key=cv2.contourArea)
    #     ((x, y), radius) = cv2.minEnclosingCircle(c)
    #     M = cv2.moments(c)
    #     center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    #
    #     # only proceed if the radius meets a minimum size
    #     if radius > 30:
    #         # draw the circle and centroid on the frame,
    #         # then update the list of tracked points
    #         nearest_one = (int(x), int(y))
    #         radius = int(radius)
    #     #            cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
    #     #            cv2.circle(image, center, 5, (255, 0, 0), -1)

    circles = cv2.HoughCircles(bmask, cv2.HOUGH_GRADIENT, 1, 30, param1=20, param2=30, minRadius=20, maxRadius=400)
    if circles is not None:
        # Need to understand what it is doing here
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if max_y < i[1] + i[2]:
                max_y = i[1] + i[2]
                nearest_one = (i[0], i[1])
                radius = i[2]
                print 'radius', radius
    else:
        no_circle = True
        print 'no circle'

    # Plotting the nearest Circle
    if not no_circle:
        cv2.circle(image, nearest_one, int(radius), (0, 255, 0), 2)

        # Logic for moving right and left
        ball_x, ball_y = nearest_one

        if (image_y / 2) > ball_x:
            print "Move Left"
        elif (image_y / 2) < ball_x:
            print "Move Right"
        else:
            print "Move Forward"

        cv2.circle(image, nearest_one, 3, (255, 255, 255), 3)

        cv2.imshow(WINDOW_NAME, image)

        if cv2.waitKey(1) & 0xFF == 27:
            center = None

        return nearest_one
    return None


# Test with input from camera
if __name__ == '__main__':

    camera = cv2.VideoCapture("Robo_videos/ball_tracking_example5.mp4")

    #     capture = cv2.VideoCapture(0)

    while True:

        # image = cv2.imread('1.jpg')
        (grabbed, frame) = camera.read()

        if True:
            print track(frame)

            #             if not track(image):
            #                 break
            #
            #             if cv2.waitKey(1) & 0xFF == 27:
            #                 break
            time.sleep(0.25)
        else:

            print('Capture failed')
            break
