#!/usr/bin/python
# -*- coding: UTF-8 -*-
#根据opencv的识别库进行人的正脸的识别

import face_recognition
import cv2
import os
import sys
import time
import configparser
import numpy as np
from PIL import Image
from public import *

class face_recognize:

    scaleFactor = 0
    minNeighbors = 0
    minSize = 0
    tolerance = 0
   
    known_face_names=[]
    known_face_encodings=[]   
    mycode = ""

    def __init__(self):
       
        current_file_path=os.path.dirname(os.path.abspath(__file__))
        print(current_file_path)
        self.faceCascade = cv2.CascadeClassifier(current_file_path+"/conf/haarcascade_frontalface_alt2.xml")        
        config = configparser.ConfigParser()
        config.read(current_file_path+"/conf/config.ini")
        self.scaleFactor = config.getfloat("face_recognize", "scaleFactor")       
        self.minNeighbors = config.getint("face_recognize", "minNeighbors")
        self.tolerance = config.getfloat("face_recognize", "tolerance")
        self.minSize = config.getint("face_recognize", "minSize")
        self.datapath = config.get("frame", "datapath")
        self.km = keymanage.manage_kf()          

    #导入该频道的人像识别信息
    def loadKnowFaces(self, compid, chid):

        result = self.km.getFace(compid, chid)
        for r in result:
            faceimg = self.datapath +"/"+str(chid)+"/face/"+r[1]
            image = cv2.imread(faceimg)
            someone_img = face_recognition.face_encodings(image)[0]
            #someone_face_encoding = face_recognition.face_encodings(image, someone_img)[0] 
            self.known_face_encodings.append(someone_img) 

    def getImage(self, imgurl):      
        image = io.imread(imgurl)
        #image = cv2.imread(imgurl)
        return image

    def detectFace(self, fimage):

        img = cv2.imread(fimage)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cimages = []
        faces = self.faceCascade.detectMultiScale(
          gray,
          scaleFactor=self.scaleFactor,
          minNeighbors=self.minNeighbors,
          minSize=(self.minSize, self.minSize)    
                #flags = cv2.CV_HAAR_SCALE_IMAGE
        )
        for (x, y, w, h) in faces:
            cropImg = img[y:y+h, x:x+w]
            # im = Image.fromarray(cropImg)
            # im.save('/tmp/'+str(time.time())+".jpg")
            cimages.append(cropImg)       
        return cimages
    #保存图像中识别出的人脸的信息
    def saveFace(self, fimage, compid, chid):

        face_path = self.datapath +"/"+str(chid)+"/face/"
        if not os.path.isdir(face_path):
            os.makedirs(face_path)

        faces = self.detectFace(fimage)
        for cropImg in faces:
            t = time.time()
            cv2.imwrite(face_path+str(t)+".jpg", cropImg)
            self.km.saveFace(compid, chid, str(t)+".jpg")          
    #对于图像中的提取的人脸与库中的标本进行处理；   
    def recognize(self, image):

        faces = self.detectFace(image)
        #正常新闻类的节目，经常性出现2个主持人，为了提高效率，对于超过4个人脸的判定，都返回false
        if len(faces) > 2:
            return False

        for cropImg1 in faces:
            try:
                #有可能侦测出的人脸不能够被确认，所以如果不确认的人脸，也认为不匹配的；
                someone_img = face_recognition.face_encodings(cropImg1)[0]
                match = face_recognition.compare_faces(self.known_face_encodings, someone_img, tolerance=self.tolerance)
                if True in match:
                    return True
            except:
                continue
        return False

if __name__== '__main__': 

    face_recognize = face_recognize()
    face_recognize.saveFace("/Users/xiaobo/vs/data/2/002984303.jpg", 1, 2)
    # ret = face_recognize.loadKnowFaces(1, 3)
    # ret1 = face_recognize.recognize("/tmp/newscut/d1d245763411d7f9e1f7685a00abd236/000023202.jpg", 1, 2)
    # print(ret1)
