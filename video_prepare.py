import av
import os
import shutil
import hashlib
import av.datasets
import configparser
import time
import subprocess

#视频处理准备类，对于视频的内容进行关键帧提取， 并分离出音频文件，都保存在tmpath的临时目录中，供http访问；
class prepare:
    def __init__(self):

        current_file_path=os.path.dirname(os.path.abspath(__file__))
        print(current_file_path)
        config = configparser.ConfigParser()
        config.read(current_file_path+"/conf/config.ini")
        #该目录定义在config.ini中做为截图的临时路径，处理完成后可以删除，只做为临时处理时使用；
        self.tmpath = config.get("frame", "tmpath") 
        self.domain = config.get("frame", "domain")                
        return

    #生成关键帧图片，对于正常的视频来说，一个小时的视频可能会有几千个图片,对于音频剥离；
    def video_capture_and_audio_strip(self, video):

        #先使用/tmp做为临时主目录，/tmp/newscut/taskid/为截图的目录
        if not os.path.exists(self.tmpath):
            os.mkdir(self.tmpath)
        vtpath = self.tmpath + "/" + hashlib.md5(video.encode(encoding='UTF-8')).hexdigest()
        vtdomain = self.domain + "/" + hashlib.md5(video.encode(encoding='UTF-8')).hexdigest()

        if os.path.exists(vtpath):
            shutil.rmtree(vtpath)

        os.mkdir(vtpath)
        #先进行音频的分离操作
        self.mk_audio_wav(video, vtpath)
        container = av.open(video)
        # Signal that we only want to look at keyframes.
        stream = container.streams.video[0]
        stream.codec_context.skip_frame = 'NONKEY'

        for frame in container.decode(stream):
            #print(frame.time_base)
            #为了控制处理的时间，把所有的图片都截成320x180;
            frame1 = frame.reformat(320, 180, 'rgb24')
            frame1.to_image().save(vtpath+'/{:09d}.jpg'.format(int(frame.time*1000)), quality=60,)

        files = os.listdir(vtpath)
        files.sort()
        vkey = {}
        for f in files:
            if ".jpg" in f:
                fname, suff = f.split(".")
                pm = vtdomain+"/"+f
                vkey[fname] = pm 
        return vkey

    #做音频的分离，试了多种方式，还是系统调用最快；所以通过调用ffmpeg来进行处理，生成的文件与截图的在同一个目录下，文件名为audio.m4a（因为没有重编码，音频的内容可能不是AAC的）
    def mk_audio_wav(self, video, tpath):
        try:
            ret = subprocess.check_call([
                'ffmpeg',
                '-y',
                '-i', video,
                '-vn',
                '-acodec', 'copy',
                tpath+"/audio.m4a",
            ])
        except:
            raise Exception("转换音频文件出错！", video)

if  __name__ == "__main__":
        kf = prepare()
        t1 = time.time()
        kf.video_capture_and_audio_strip("http://192.168.3.250/0106wjxw.mp4")
        print(time.time()-t1)