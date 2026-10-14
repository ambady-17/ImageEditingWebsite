from django.conf import settings
import numpy as np
import cv2
import os

def _ensure_temp_dir(filepath):
   """Ensure the directory for the temp file exists"""
   temp_dir = os.path.dirname(filepath)
   if temp_dir and not os.path.exists(temp_dir):
      os.makedirs(temp_dir, exist_ok=True)
 
def opencv_gray(path,path_temp):
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, grayscale)
 
   else:
      print('Error')


def opencv_edge(path,path_temp):
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      if len(img.shape)==3:
         grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   
      edges = cv2.Canny(img,100,200)
      _ensure_temp_dir(path_temp)   
      cv2.imwrite(path_temp, edges)
 
   else:
      print('Error')


def opencv_brightp(path,path_temp):
   img = cv2.imread(path, 1)
   if (type(img) is np.ndarray):      
      img_bright = np.float32(img)+30
      img_bright[img_bright>=255]=255
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, np.uint8(img_bright))       
   else:
      print('Error')


def opencv_brightn(path,path_temp):
   img = cv2.imread(path, 1)
   if (type(img) is np.ndarray):      
      img_bright = np.float32(img)-30
      img_bright[img_bright<=0]=0
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, np.uint8(img_bright))       
   else:
      print('Error')

def opencv_scaleup(path,path_temp):
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      res = cv2.resize(img,None,fx=1.5, fy=1.5, interpolation = cv2.INTER_CUBIC)
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, res) 
   else:
      print('Error')



def opencv_scaledown(path,path_temp):
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      res = cv2.resize(img,None,fx=.75, fy=.75, interpolation = cv2.INTER_CUBIC)
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, res) 

   else:
      print('Error')


def opencv_filter(path,path_temp):
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      if len(img.shape)==3:
         kernel = np.ones((5,5),np.float32)/25
         dst = cv2.filter2D(img,-1,kernel)
         _ensure_temp_dir(path_temp)
         cv2.imwrite(path_temp, dst)
 
   else:
      print('Error')


def opencv_crop(path,path_temp,x,y,wd,ht):
   x=int(x)
   y=int(y)
   wd=int(wd)
   ht=int(ht)
   img = cv2.imread(path, 1) 
   if (type(img) is np.ndarray):
      crop_img = img[x:x+wd, y:y+ht]
      _ensure_temp_dir(path_temp)
      cv2.imwrite(path_temp, crop_img)

   else:
      print('Error')


import cv2
import numpy as np

def opencv_blur(loc, loc_temp):
    img = cv2.imread(loc)
    blur = cv2.blur(img,(10,10))
    _ensure_temp_dir(loc_temp)
    cv2.imwrite(loc_temp, blur)


def opencv_gaussian(loc, loc_temp):
    img = cv2.imread(loc)
    gblur = cv2.GaussianBlur(img,(9,9),0)
    _ensure_temp_dir(loc_temp)
    cv2.imwrite(loc_temp, gblur)


def opencv_sharpen(loc, loc_temp):
    img = cv2.imread(loc)

    kernel = np.array([[0,-1,0],
                       [-1,5,-1],
                       [0,-1,0]])

    sharp = cv2.filter2D(img,-1,kernel)
    _ensure_temp_dir(loc_temp)
    cv2.imwrite(loc_temp, sharp)


def opencv_sepia(loc, loc_temp):
    img = cv2.imread(loc)

    kernel = np.array([[0.272,0.534,0.131],
                       [0.349,0.686,0.168],
                       [0.393,0.769,0.189]])

    sepia = cv2.transform(img, kernel)
    _ensure_temp_dir(loc_temp)
    cv2.imwrite(loc_temp, sepia)


def opencv_negative(loc, loc_temp):
    img = cv2.imread(loc)

    negative = 255 - img
    _ensure_temp_dir(loc_temp)
    cv2.imwrite(loc_temp, negative)