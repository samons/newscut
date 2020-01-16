import configparser
import keys_collect
import video_prepare
import audiokeys
import time
import hashlib
import os


class newscut:
    def __init__(self):

        current_file_path=os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(current_file_path+"/conf/config.ini")
        self.distance = config.get("optimize", "distance")  
        self.seg_min = config.get("optimize", "seg_min")  
        self.seg_max = config.get("optimize", "seg_max")
        self.domain = config.get("frame", "domain")                  
        return

    #二次合并相近点内容；标识片段中少于seg_min的点，标识片段长于seg_max的点
    def again_merg_dict(self, merg_dict):

        new_dict = {v : k for k, v in merg_dict.items()}
        pstart = new_dict.get('programe_head', 0) 
        pend = new_dict.get('programe_end', 600000000)
        items = sorted(merg_dict.items())
        ptm = 0
        for k, v in items:
            if v == 'programe_head' or v == 'programe_end':
                continue
            #超出节目头和尾的点除掉；
            if k < pstart or k > pend:
                merg_dict.pop(k)
                continue
            if ptm == 0:
                ptm = k
                continue
            
            if (k - ptm) < int(self.seg_min):
                merg_dict.pop(k)
                continue

            if (k - ptm) > int(self.seg_max):
                merg_dict[k] = 'no_sure'
            ptm = k
        return merg_dict

    #获得视频内容的可能截取点，视频内容需要分解为video和audio分别进行处理；    
    def get_key(self, video, compid, chid):
        #该video处理类会返回6个值，分别是头、尾、节目头/尾，人脸，关键帧列表;
        kcc = keys_collect.collect()
        aks = audiokeys.audiokeys()
        t1 = time.time()
        prghead, prgend, seghead, segend, facekey, videokey  = kcc.analyze_img(video, compid, chid)
        #语音识别会返回一个识别列表；
        speakkey = aks.analyize_word("/Users/xiaobo/vs/video/more/0108wjxw.m4a.json", 1, 2)
        #语音识别的信息，可能会是一个过程节点，需要找到附近的关键帧点进行双条件确认；所以，需要向前找关键帧；
        ssl = sorted(speakkey.items())
        videokey1 = sorted(videokey.items())
        for k1, v1 in ssl:
            k12 = k1
            for k2, v2 in videokey1:
                if int(k2) > int(k1) :
                    speakkey.pop(k1)
                    speakkey[k12] = v1
                    break;
                k12 = k2
        print(float(time.time()-t1))
        
        distance = int(self.distance)
        k0 = 0 - distance

        merg_dict = dict()      #merg_dic为了合并取值点的信息
        prghead1 =  dict()
        #处理prehead的信息，因为有时会有多个片头的图片，所以会有多个识别点，取最前的识别点；
        for k, v in prghead.items():
            if (int(k) - k0) > distance:
                prghead1[k] = v
                k0 =  int(k)

        k0 = 0 - distance
        prgend1 =  dict()
        #处理prgend的信息，因为有时会有多个片尾的图片，所以会有多个识别点，取最前的识别点；
        for k, v in prgend.items():
            if (int(k) - k0) > distance:
                prgend1[k] = v
                k0 =  int(k)

        k0 = 0 - distance
        seghead1 =  dict()
        #处理seghead的识别点；
        for k, v in seghead.items():
            if (int(k) - k0) > distance:
                seghead1[k] = v
                k0 =  int(k)
                merg_dict[k0] = 'key_start'

        k0 = 0 - distance
        segend1 =  dict()
        #处理segend的识别点；
        for k, v in segend.items():
            if (int(k) - k0) > distance:
                segend1[k] = v
                k0 =  int(k)
                merg_dict[k0] = 'key_end'

        k0 = 0 - distance
        facekey1 =  dict()
        #处理facekey的识别点；
        for k, v in facekey.items():
            if (int(k) - k0) > distance:
                facekey1[k] = v
                k0 =  int(k)
                merg_dict[k0] = 'key_start'

        # k0 = 0 - distance
        # videokey1 =  dict()
        # #处理videokey的识别点；
        # for k, v in videokey.items():
        #     if (int(k) - k0) > distance:
        #         videokey1[k] = v
        #         k0 =  int(k)

        k0 = 0 - distance
        speakkey1 =  dict()
        #处理speakkey的识别点；
        for k, v in speakkey.items():
            if (int(k) - k0) > distance:
                speakkey1[k] = v
                k0 =  int(k)
                merg_dict[k0] = 'key_start'

        
        #把头和尾的内容写入到merg_dict中
        pitems = sorted(prghead1.items())
        pstart = 0
        pend = 0
        for k, v in pitems:
            merg_dict[int(k)] = 'programe_head'
            pstart = int(k)
            break

        peitems = sorted(prgend1.items(), reverse=True)
        for k, v in peitems:
            merg_dict[int(k)] = 'programe_end'
            pend = int(k)
            break

        merg_dict = self.again_merg_dict(merg_dict)

        print(merg_dict)
        #生成返回的智能拆条的处理结果，其中包括:{"companyid":"1", "channelid":"1", "video":{"url":"http:", "duration":"1234", "start":"1234", "end":"2345"},"segment":{"001":"programe_head", "002":"segment_head",... }, keys:{""}}
        rpack = {}
        rpack["companyid"] = compid
        rpack["channelid"] = chid
        tvideo = {}
        tvideo["url"] = video
        duration = (pend - pstart) if pend > pstart else -1
        tvideo["news_start"] = pstart
        tvideo["news_end"] = pend
        tvideo["duration"] = duration
        rpack["video"] = tvideo
        rpack["segment"] = merg_dict
        #根据时间戳来生成关键帧的图片地址；
        vp = hashlib.md5(video.encode(encoding='UTF-8')).hexdigest()
        seg_image = {}
        for k, v in merg_dict.items():
            seg_image[k] = self.domain+"/"+vp+"/"+"%09d" % k+".jpg"
        rpack["seg_image"] = seg_image
        #把videokey中的本地址变为网络地址
        vkey1 = {}
        for k, v in videokey.items():
            vkey1[int(k)] = self.domain+"/"+vp+"/"+k+".jpg"
        rpack["keys"] = vkey1
        print(rpack)

if  __name__ == "__main__":

        t1 = time.time()
        nc = newscut()
        vp = video_prepare.prepare()
        video = "http://192.168.3.250/0108wjxw.mp4"
        vp.video_capture_and_audio_strip(video)
        result = nc.get_key(video , 1, 2)   
        print(time.time()-t1)                                       