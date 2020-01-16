import json
import re
from public import keymanage

class audiokeys:
    def __init__(self):
        #节目的文本记录点
        self.speakkey = dict()
    #获得语音识别的结果后对于json内容进行导入
    def loadAsr(self, afile):
        try:
            jau = dict()
            j = json.load(open(afile))
            #对于jaudio中的数据记录开始点和长度
            j1 = j["words"]
            for val in j1:
                jau[val["bg"]] = val["onebest"]
            return jau

        except  Exception as r:
            print(r)
            return None

    #发送语言文件给识别接口，等待识别的结果
    def getAsr(self, au_file):
        return
    #导入设定的keyword的内容
    def getKeyword(self, compid, chid):
        kwlist = keymanage.manage_kf().getAudioKey(compid, chid)
        return kwlist

    #分析文字中包含的关键词节点内容
    def analyize_word(self, afile, compid, chid):
        kl = self.getKeyword(compid, chid)
        asr = self.loadAsr(afile)
        for kw in kl:
            k1 = kw[0]
            regex = re.compile(k1)
            for ak, al in asr.items():
                if regex.findall(al):
                    self.speakkey[ak] = al
        return self.speakkey 


if __name__ == "__main__":
    #a = audiokeys()
    #b = a.analyize_word("/Users/xiaobo/vs/video/aa.json", 1, 2)
    #print(b)
    regex = re.compile("((月)(.{1,3})(号)[^起])")
    str = "观众朋友晚上好，今天是1月6号星期，欢迎收看晚间新闻。"
    str1 = "而在怒江州片马高黎贡山区域，从1月3号迎来新年第1场雪，开始到6号上午，跃进桥到片马的阅片公路、高黎贡山风雪垭口段部分路段积雪厚度高达26厘米。"
    if regex.findall(str):
        print("ok1")
    else:
        print("no1")    
    if regex.findall(str1):
        print("ok2")
    else:
        print("no2")            