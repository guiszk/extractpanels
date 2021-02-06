import cv2
import os, sys
import numpy as np

if(len(sys.argv) != 2):
    print('{} <path to file or directory>'.format(sys.argv[0]))
    sys.exit(1)

newdir = os.getcwd() + "/extracted"
if not(os.path.isdir(newdir)):
    os.mkdir(newdir)

def detect(impath):
    name, ext = os.path.splitext(impath)
    if(ext == '.png' or ext == '.jpg'):
        name, ext = os.path.splitext(impath)
        image = cv2.imread(impath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

        thresh = cv2.threshold(sharpen,160,255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        image_number = 0
        print("{} panels found.".format(len([c for c in cnts if cv2.contourArea(c) > 80000])))
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 80000: #set minimum area
                x,y,w,h = cv2.boundingRect(c)
                ROI = image[y:y+h, x:x+w]
                newpath = '{}/{}_{}.png'.format(newdir, name.split("/")[-1], image_number)
                #print(newpath)
                cv2.imwrite(newpath, ROI)
                #cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
                image_number += 1
    else:
        print("{} is not a valid image file.".format(impath))

arg = sys.argv[1]
if(os.path.isfile(arg)):
    print("Extracting from {}".format(arg))
    detect(arg)
    print("Files written to {}".format(newdir))
elif(os.path.isdir(arg)):
    for i in os.listdir(arg):
        print("Extracting from {}".format(i))
        detect(os.path.join(arg, i))
    print("Files written to {}".format(newdir))
