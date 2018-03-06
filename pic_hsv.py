import cv2
import numpy as np


image = cv2.imread("/home/qburst/robot/pink.jpeg")
blur = cv2.GaussianBlur(image, (5, 5), 0)
# Convert BGR to HSV
hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

image_x, image_y, color_code = image.shape
max_hsv = np.int_(image[0, 0])
min_hsv = np.int_(image[0, 0])
image = np.int_(image)
for a in range(0, image_x):
    for b in range(0, image_y):
        if image[a,b][0] ==0 and image[a,b][1] == 0  and image[a,b][2] ==0:
           continue

        if image[a,b][0] < min_hsv[0]:
            min_hsv[0] = image[a,b][0]
        if image[a,b][1] < min_hsv[1]:
            min_hsv[1] = image[a,b][1]
        if image[a,b][2] < min_hsv[2]:
            min_hsv[2] = image[a,b][2]

        if image[a,b][0] > max_hsv[0]:
            max_hsv[0] = image[a,b][0]
        if image[a, b][1] > max_hsv[1]:
            max_hsv[1] = image[a, b][1]
        if image[a, b][2] > max_hsv[2]:
            max_hsv[2] = image[a,b][2]

print min_hsv, max_hsv


