# from Tkinter import *
# from filedialog import askopenfilename
# from PIL import Image, ImageTk
# import tkSimpleDialog
import urllib
from Tkinter import *
import tkSimpleDialog, tkMessageBox
# from filedialog import askopenfilename
import cv2
import numpy as np

from PIL import Image, ImageTk


root = Tk()

url="http://10.7.170.8:8080/shot.jpg"

imgResp = urllib.urlopen(url)
imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
img = cv2.imdecode(imgNp,-1)
cv2.imwrite("pink.jpg", img)

#setting up a Tkinter canvas
w = Canvas(root, width=1440, height=1080)
w.pack()

#adding the image
# File = askopenfilename(parent=root, initialdir="./",title='Select an image')
original = Image.open('/home/qburst/robot/entethala.jpg')
# original = original.resize((1000,1000)) #resize image
img = ImageTk.PhotoImage(original)
w.create_image(0, 0, image=img, anchor="nw")

#ask for pressure and temperature extent
# xmt = tkSimpleDialog.askfloat("Temperature", "degrees in x-axis")
# ymp = tkSimpleDialog.askfloat("Pressure", "bars in y-axis")

#ask for real PT values at origin
# xc = tkSimpleDialog.askfloat("Temperature", "Temperature at origin")
# yc = tkSimpleDialog.askfloat("Pressure", "Pressure at origin")

#instruction on 3 point selection to define grid
# tkMessageBox.showinfo("Instructions", "Click: \n"
#                                             "1) Origin \n"
#                                             "2) Temperature end \n"
#                                             "3) Pressure end")

# From here on I have no idea how to get it to work...

# Determine the origin by clicking
def getorigin(eventorigin):
    global x0,y0
    x0 = eventorigin.x
    y0 = eventorigin.y
    print 'Cordinates: ', (x0,y0)
    w.bind("<Button 1>", printcoords)
#mouseclick event
w.bind("<Button 1>",getorigin)

# Determine the extent of the figure in the x direction (Temperature)
def getextentx(eventextentx):
    global xe
    xe = eventextentx.x
    print(xe)
    w.bind("<Button 1>",getextenty)

# Determine the extent of the figure in the y direction (Pressure)
def getextenty(eventextenty):
    global ye
    ye = eventextenty.y
    print(ye)
    tkMessageBox.showinfo("Grid", "Grid is set. You can start picking coordinates.")
    w.bind("<Button 1>",printcoords)

#Coordinate transformation into Pressure-Temperature space
def printcoords(event):
    # xmpx = xe-x0
    # xm = xmt/xmpx
    # ympx = ye-y0
    # ym = -ymp/ympx

    #coordinate transformation
    # newx = (event.x-x0)*(xm)+xc
    # newy = (event.y-y0)*(ym)+yc

    #outputting x and y coords to console
    print 'Points: ', (event.x, event.y)

root.mainloop()