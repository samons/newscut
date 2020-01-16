from public import pmysql

class mytask(object):

    def __init__(self):
        self.pm = pmysql.pmy()

    def gettask(self, companyid = 0, channelid=0, taskid = 0):

        sql = "select video from task where companyid = %s and channelid = %s and taskid = %s and status = 'normal'"
        
        result = self.pm.get_one(sql, (companyid, channelid, taskid))
        return result
