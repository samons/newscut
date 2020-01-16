import av
import os
import hashlib
import configparser
import av.datasets
from public import keymanage
import face_recognize
import numba
import image_compare
import time

class collect(object):

    def __init__(self):

        #节目的开始记录点
        self.prghead = dict()
        #节目的结束记录点
        self.prgend = dict()
        #节目的关键帧记录点
        self.seghead = dict()
        #节目的音频记录点
        self.segend = dict()
        #视频的关键帧点
        self.videokey = dict()
        #节目的人像记录点
        self.facekey = dict()
        current_file_path=os.path.dirname(os.path.abspath(__file__))
        print(current_file_path)
        config = configparser.ConfigParser()
        config.read(current_file_path+"/conf/config.ini")
        self.tmpath = config.get("frame", "tmpath") 
        self.datapath = config.get("frame", "datapath")  
        self.drate = config.get("frame", "drate") 
        self.distance = config.get("optimize", "distance")              
        return

    def video_info(self, video):
        self.fname = os.path.basename(video)
        container = av.open(video)
        self.duration=container.duration
        return

    #从截取的视频关键帧图片获取关键帧列表
    def load_video_key(self, video):

        tmpath = self.tmpath+ "/" + hashlib.md5(video.encode(encoding='UTF-8')).hexdigest()
        files = os.listdir(tmpath)
        files.sort()
        for f in files:
                if ".jpg" in f:
                    fname, suff = f.split(".")
                    pm = tmpath+"/"+f
                    self.videokey[fname] = pm  
                                  
    def load_keyframe_info(self, compid, chid):

        mkf = keymanage.manage_kf()
        result1 = mkf.getDB_KF(compid, chid)
        return result1

    #记录图片比对关键点信息
    # fname 文件名，可能会带后缀
    # groups 标记组信息：programe_head： 节目头 programe_end:节目尾 segments_head:片段头 segments_end:片段尾
    def regKeyPoint(self, rdict):
  
        for k, g in rdict.items():
            if g == 'programe_head':
                self.prghead[k] = g

            if g == 'programe_end':
                self.prgend[k] = g
            
            if g == 'segments_head':
                self.seghead[k] = g
            
            if g == 'segments_end':
                self.segend[k] = g

    #记录图片比对关键点信息
    # fname 文件名，可能会带后缀
    def regFacePoint(self, ptime):

        self.facekey[ptime] = 'face'

    def analyze_img(self, video, compid, chid):
    
        #从数据库中取本频道的设定转场关键帧数据
        result = self.load_keyframe_info(compid, chid)
        if not result:
            return

        #在此处引导视频目录中的所有关键帧数据到字典中    
        self.load_video_key(video)

        icomp = image_compare.compare()
        rdict = icomp.compORB(self.datapath+"/"+str(chid), self.videokey, result, float(self.drate))
        self.regKeyPoint(rdict)       
        #建立头像比较类
        dface = face_recognize.face_recognize()
        dface.loadKnowFaces(compid, chid)                        
        for key, val in self.videokey.items():        
            ret = dface.recognize(val)
            if ret:
                self.regFacePoint(key)

        return self.prghead, self.prgend, self.seghead, self.segend, self.facekey, self.videokey        

if  __name__ == "__main__":
        vk = collect()
        video = "/Users/xiaobo/vs/video/v2.mp4"
        vk.video_info(video)
        result = vk.analyze_img(video , 1, 2)