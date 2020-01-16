import cv2
import numpy as np
from io import BytesIO
import os
import time

#此类编写主要是通过一次计算hash的值后，实现多次比对，并通过多线程实现效率的提升；
class compare(object):

    #slist为原始的图片的列表， tlist为需要对比的图片列表；
    def __init__(self):
        return

    def compORB(self, spath, slist, tlist, drate=0.5):

        tdict = {}
        count = 0
        #先提取tlist中记录的ORG的值
        rdict = {}
        orb = cv2.ORB_create()
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        try:        
            for r in tlist:

                kframe = r[0]
                url = r[1]
                groups = r[2]
                kpic = spath+"/"+url              
                img2 = cv2.imread(kpic, cv2.IMREAD_GRAYSCALE)
                # 提取并计算特征点
                kp2, des2 = orb.detectAndCompute(img2, None)
                #只有groups和des2的数据参与到后面的计算中，所以生成的字典可以只包含这两个内容；
                tdict[count] = [des2, groups, kpic]
                count += 1

            for key, val in slist.items():
                # 读取图片
                img1 = cv2.imread(val, cv2.IMREAD_GRAYSCALE)
                kp1, des1 = orb.detectAndCompute(img1, None)
                #对于数据库中保存的关键帧进行比对；
                for k, r in tdict.items():
                    des = r[0]
                    grp = r[1]
                    kp = r[2]
                    # knn筛选结果
                    try:
                        matches = bf.knnMatch(des1, trainDescriptors=des, k=2)   
                        # 查看最大匹配点数目
                        good = [m for (m, n) in matches if m.distance < 0.90 * n.distance]
                        similary = float(len(good))/len(matches)
                        if similary > drate:
                            rdict[key] = grp
                            print("%s, %s, %s, %s" % (val, kp, grp, similary))
                    except:
                        continue
        except Exception as e:
            print('无法计算两张图片相似度', e)
        return rdict
    def gist(self, pimg1, pimg2):

        orb = cv2.ORB_create()

        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        img1 = cv2.imread(pimg1, cv2.IMREAD_GRAYSCALE)
        kp1, des1 = orb.detectAndCompute(img1, None)

        img2 = cv2.imread(pimg2, cv2.IMREAD_GRAYSCALE)
        kp2, des2 = orb.detectAndCompute(img2, None)
        
        matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)     
        good = [m for (m, n) in matches if m.distance < 0.95 * n.distance]
        similary = float(len(good))/len(matches)
        print(similary)

if __name__ == "__main__":
    p1="./data/2/001795642.jpg"
    p2="./data/2/002990303.jpg"

    comp = compare()
    comp.gist(p1, p2)
