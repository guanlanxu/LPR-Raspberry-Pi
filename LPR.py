#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 11:52:13 2021

@author: guanlanxu
"""



import cv2
import imutils
import numpy as np
import pytesseract

img = cv2.imread('/Users/guanlanxu/Pictures/CarPlate/passed_1st_ model/MA.jpg',cv2.IMREAD_COLOR)
img = cv2.resize(img, (600,400) )
cv2.imshow("original", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
cv2.imwrite("01.jpg", img)


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
gray = cv2.bilateralFilter(gray, 13, 15, 15) 

edged = cv2.Canny(gray, 30, 200) 
cv2.imwrite("02.jpg", edged)
contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours)
contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
screenCnt = None

for c in contours:
    
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
 
    if len(approx) == 4:
        screenCnt = approx
        break

if screenCnt is None:
    detected = 0
    print ("No contour detected")
else:
     detected = 1

if detected == 1:
    cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)
 
    
cv2.imwrite("03.jpg", img)

mask = np.zeros(gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)

new_image = cv2.bitwise_and(img,img,mask=mask)
cv2.imwrite("04.jpg", new_image)

(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x), np.min(y))
(bottomx, bottomy) = (np.max(x), np.max(y))
Cropped = gray[topx:bottomx+1, topy:bottomy+1]

cv2.imshow("cropped",Cropped)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


text = pytesseract.image_to_string(Cropped, lang='eng', config='--oem 3 -l eng --psm 11')
text2 = pytesseract.image_to_data(Cropped, output_type='data.frame')
text2 = text2[text2.conf != -1]
conf = text2.groupby(['block_num'])['conf'].mean()

print("programming_fever's License Plate Recognition\n")
print("Detected license plate Number is:",text)
print("confidence level is:",conf[2])


img = cv2.resize(img,(500,300))
Cropped = cv2.resize(Cropped,(400,200))
cv2.imshow('car',img)
cv2.imshow('Cropped2',Cropped)
cv2.imwrite("05.jpg", Cropped)

#cv2.waitKey(0)
#cv2.destroyAllWindows()