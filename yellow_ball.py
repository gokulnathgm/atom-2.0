import cv2
import numpy as np

# For OpenCV2 image display
WINDOW_NAME = 'GreenBallTracker'
CENTROID = 640

def track(image):

   '''Accepts BGR image as Numpy array
      Returns: (x,y) coordinates of centroid if found
               (-1,-1) if no centroid was found
               None if user hit ESC
   '''

   # Blur the image to reduce noise
   blur = cv2.GaussianBlur(image, (5,5),0)

   # Convert BGR to HSV
   hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

   # Threshold the HSV image for only green colors
   lower_green = np.array([20, 100, 100])
   upper_green = np.array([200, 255, 255])

   # Threshold the HSV image to get only green colors
   mask = cv2.inRange(hsv, lower_green, upper_green)
   
   # Blur the mask
   bmask = cv2.GaussianBlur(mask, (5,5),0)

   cnts = cv2.findContours(bmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
   cnts = cnts[-2]
   center = None
 

   if len(cnts) > 0:
       # centroid
       c = max(cnts, key=cv2.contourArea)
       ((x, y), radius) = cv2.minEnclosingCircle(c)
       M = cv2.moments(c)
       center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

       # only proceed if the radius meets a minimum size
       if radius > 5:
          # draw the circle and centroid on the frame,
          # then update the list of tracked points
          cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
          cv2.circle(image, center, 5, (255, 0, 0), -1)
          
   circles = cv2.HoughCircles(bmask, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
   circles = np.uint16(np.around(circles))
   for i in circles[0,:]:
       if i[2] > 100:
          cv2.circle(image,(i[0],i[1]),i[2],(0,255,0),2)
          cv2.circle(image,(i[0],i[1]),2,(255,0,255),3)
          
   cv2.imshow(WINDOW_NAME, image)

   if cv2.waitKey(1) & 0xFF == 27:
       center = None

   return center

# Test with input from camera
if __name__ == '__main__':

#     capture = cv2.VideoCapture(0)

    while True:

        image = cv2.imread('moonu.jpg')

        if True:
            print track(image)

#             if not track(image):
#                 break
#           
#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

        else:

           print('Capture failed')
           break