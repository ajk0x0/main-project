import cv2
import numpy as np
import imutils
import pytesseract
from PIL import Image
import string
table = str.maketrans('', '', string.ascii_lowercase)

class LicensePlateDetector:
   def _correctToText(self, text) -> str:
      for i in range(len(text)):
         if text[i]=="5":
            text=text=text.replace("5","S")
         elif text[i]=="2":
            text=text.replace("2","Z")
         elif text[i]=="4":
            text=text.replace("4","A")
         elif text[i]=="8":
            text=text.replace("8","B")
         elif text[i]=="7":
            text=text.replace("7","Z")
      return text
   
   def _correctToNumbers(self, text) -> str:
      for i in range(len(text)):
         if text[i]=="S":
            text=text.replace("S","5")
         elif text[i]=="Z":
            text=text.replace("Z","2")
         elif text[i]=="A":
            text=text.replace("A","4")
         elif text[i]=="B":
            text=text.replace("B","8")
         elif text[i]=="I":
            text=text.replace("I","1")
         elif text[i]=="O":
            text=text.replace("O","0")
         elif text[i]=="T":
            text=text.replace("T","1")
      return text
   
   def _checkState(self, text) -> str:
      list_of_states=["AN","AP","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR","HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR","PY","PN","RJ","SK","TN","TR","UP","WB"]
      if text[0:2] in list_of_states:
         return text
      else:
         return self._correctToText(text[0:2])+text[2:]
      
   def _checkRTO(self, text) -> str:
      if not(text[2].isnumeric() and text[3].isnumeric()):
         return text[0:2] + self._correctToNumbers(text[2:4])+text[4:]
      else:
         return text
      
   def _checkLastFour(self, text) -> str:
      if not ((text[-1].isnumeric() and text[-2].isnumeric()) and (text[-3].isnumeric() and text[-4].isnumeric())):
         return text[:-4] + self._correctToNumbers(text[-4:])
      else:
         return text

   def _checkSeries(self, text) -> str:
      isthereanum=False
      for i in text[4:][:-4]:
         if i.isnumeric():
               isthereanum=True
      if isthereanum:
         return text[0:4] + self._correctToText(text[4:][:-4])+text[-4:]
      else:
         return text

   def getNumber(self, img) -> str:
      (H, W) = img.shape[:2]
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      blur = cv2.bilateralFilter(gray, 11, 17, 17)
      edged = cv2.Canny(blur, 30, 200)
      #closing
      edged= cv2.dilate(edged,np.ones((3,3),np.uint8))
      edged= cv2.erode(edged,np.ones((3,3),np.uint8)) 
      #closed
      conts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      conts = imutils.grab_contours(conts) 
      conts = sorted(conts, key=cv2.contourArea, reverse=True)[:8] 
      location = None
      for c in conts:
         peri = cv2.arcLength(c, True)
         aprox = cv2.approxPolyDP(c, 0.02 * peri, True)
         if cv2.isContourConvex(aprox):
            if len(aprox) == 4:
               location = aprox
               break
      if location is None:
        raise Exception("Failed to detect license plate contours")
      mask = np.zeros(gray.shape, np.uint8) 
      img_plate = cv2.drawContours(mask, [location], 0, 255, -1)
      img_plate = cv2.bitwise_and(img, img, mask=mask)

      (y, x) = np.where(mask==255)
      (beginX, beginY) = (np.min(x), np.min(y))
      (endX, endY) = (np.max(x), np.max(y))

      plate = gray[beginY:endY, beginX:endX]
      plate=cv2.resize(plate, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
      plate=cv2.GaussianBlur(plate, (5, 5), 0)

      im=Image.fromarray(plate)
      # im.show()
      config_tesseract = "--tessdata-dir tessdata --psm 6"
      text = pytesseract.image_to_string(plate, lang="eng")
      text="".join(ch for ch in text if ch.isalnum())
      text=text.translate(table)
      return self._checkSeries(self._checkLastFour(  \
         self._checkRTO(self._checkState(text))))
