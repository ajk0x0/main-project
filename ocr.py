import cv2
import numpy as np
import imutils
import pytesseract
from PIL import Image
import string
import math
from utils import show_img
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
      if img is None:
         raise Exception("Failed to load the image")
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      blur = cv2.bilateralFilter(gray, 11, 17, 17)
      edged = cv2.Canny(blur, 30, 200)
      edged = cv2.dilate(edged, np.ones((3,3), np.uint8))
      edged = cv2.erode(edged, np.ones((3,3), np.uint8))

      conts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      conts = imutils.grab_contours(conts)
      conts = sorted(conts, key=cv2.contourArea, reverse=True)[:8]

      location = None
      for c in conts:
          peri = cv2.arcLength(c, True)
          approx = cv2.approxPolyDP(c, 0.02 * peri, True)
          if cv2.isContourConvex(approx):
              if len(approx) == 4:
                  location = approx
                  break

      if location is None:
          raise Exception("Failed to detect license plate contours")

      # Sort the corner points of the license plate contour
      location = location.reshape(4, 2)
      rect = np.zeros((4, 2), dtype="float32")
      s = location.sum(axis=1)
      rect[0] = location[np.argmin(s)]
      rect[2] = location[np.argmax(s)]
      diff = np.diff(location, axis=1)
      rect[1] = location[np.argmin(diff)]
      rect[3] = location[np.argmax(diff)]

      (tl, tr, br, bl) = rect

      # Calculate the width and height of the license plate region
      widthA = math.sqrt((tl[0] - tr[0]) ** 2 + (tl[1] - tr[1]) ** 2)
      widthB = math.sqrt((bl[0] - br[0]) ** 2 + (bl[1] - br[1]) ** 2)
      maxWidth = max(int(widthA), int(widthB))

      heightA = math.sqrt((tl[0] - bl[0]) ** 2 + (tl[1] - bl[1]) ** 2)
      heightB = math.sqrt((tr[0] - br[0]) ** 2 + (tr[1] - br[1]) ** 2)
      maxHeight = max(int(heightA), int(heightB))

      # Create a perspective transformation matrix and apply it to the image
      dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
      M = cv2.getPerspectiveTransform(rect, dst)
      warped = cv2.warpPerspective(gray, M, (maxWidth, maxHeight))

      # Perform additional processing on the warped license plate image
      warped = cv2.resize(warped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
      warped = cv2.GaussianBlur(warped, (5, 5), 0)

      im = Image.fromarray(warped)
      # im.show()

      # config_tesseract = "--tessdata-dir tessdata --psm 6"
      text = pytesseract.image_to_string(warped, lang="eng")
      text = "".join(ch for ch in text if ch.isalnum())
      text = text.translate(table)
      if len(text)<9:
         print(text)
         print("Detected Text length is not sufficient")
         return ""
      num = self._checkSeries(self._checkLastFour(  \
         self._checkRTO(self._checkState(text))))
      print(num)
      return num
