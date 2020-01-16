from public import pmysql

#关键帧数据管理，从数据库中提取数据
class manage_kf(object):

    def __init__(self):
        self.pm = pmysql.pmy()
    #按频道获取数据库中保存的关键帧数据
    def getDB_KF(self, compid, chid):

        sql = "select kframe, url, groups from keyframe where companyid = %s and channelid = %s and status = 'normal'" 
        result1 = self.pm.get_all(sql, (compid, chid))
        return result1

    #保存频道的人脸信息
    def saveFace(self, compid, chid, face):
        sql = "insert into face(facename, url, companyid, channelid) values(%s, %s, %s, %s)"
        self.pm.insert(sql, (face, face, compid, chid))
        return

    #获取频道的人脸信息
    def getFace(self, compid, chid):
        sql = "select facename, url, companyid, channelid from face where companyid=%s and channelid = %s and status='normal'"
        result = self.pm.get_all(sql, (compid, chid))
        return result
    #获取频道的语音信息
    def getAudioKey(self, compid, chid):
        sql = "select kw from keyword where companyid=%s and channelid = %s and status='normal'"
        result = self.pm.get_all(sql, (compid, chid))
        return result        