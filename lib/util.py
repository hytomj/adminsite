import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
import pysvn

from connect.tornado.web import Route, BaseHandler
from connect.tornado.db  import Connection

enu = enumerate

def currentTime():
    return time.strftime('%Y-%m-%d 00:00:00',time.localtime(time.time()))

def svnClient():
    return pysvn.Client()

def sec2str(sec):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec))

def svnPathSplit(s):
    return s.split(" ")[1].replace("/cms.u17.com/branches/cms.u17.com-1.5_dd/", "").replace("/app.u17.com/branches/v3/", "").replace("/bbs.u17.com/branches/v_dd/", "")

class Handler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie("login")

class db(object):
    def __init__(self):
        self.database = Connection(host = "127.0.0.1:3301", database = "yunwei", user = "root", password = "111111", charset='utf8')

    def __getattr__(self, name):
        return getattr(self.database, name) or self

    def getUserId(self, username):
        if username == "admin":
            userid = 0
        else:
            userid = self.database.get("select userid from user where username = '%s'" %username)["userid"]
        return userid

    def getUsername(self, userid):
        if userid == 0:
            username = "admin"
        else:
            username = self.database.get("select username from user where userid = %s" %userid)["username"]
        return username

    def loginCheck(self, username, password):
        return self.database.get("select userid from user where username = '%s' and password = '%s' and status = 1" %(username, password))

    def addUser(self, username, password):
        if username == "admin": return 0
        try:
            self.database.execute("insert into user set username = '%s', password = '%s'" %(username, password))
            return 1
        except:
            return 0
    def getGroupName(self, groupid):
        if groupid == 0:
            return 0
        else:
            return self.database.get("select groupname from group1 where groupid = %s" %groupid)["groupname"]

    def addGroup(self, groupname, status):
        self.database.execute("insert into group1 set groupname = '%s', status = %s" %(groupname, status))

    def setGroup(self, groupid, groupname, status):
        self.database.execute("update groups set status = %s, groupname = '%s' where groupid = %s" %(status, username, groupid))

    def delGroup(self, groupid):
        self.database.execute("delete from group1 where groupid = %s" %(groupid))

    def delUser(self, userid):
        self.database.execute("delete from user where userid = %s" %(userid))
        self.database.execute("delete from log where userid = %s"  %(userid))

    def setUser(self, username, password, status, ftpstatus, groupid):
        self.database.execute("update user set status = %s, password = '%s', ftpstatus = %s, groupid = %s where username = '%s'" %(status, password, ftpstatus, groupid, username))
    
    def showUser(self):
        sql = "select * from user"
        return self.database.query(sql)

    def showGroup(self):
        sql = "select * from group1"
        return self.database.query(sql)

    def insertLog(self, username, msg):
        insertsql = "insert into log set userid='%s', msg='%s'" %(self.getUserId(username), msg)
        self.database.execute(insertsql)

    def findLog(self, username, limit):
        sql = "select msg, createtime, userid from log where userid=%s order by createtime desc " %(self.getUserId(username))
        if username == "admin":
            sql = sql.replace(" where userid=%s" %self.getUserId(username), "")
            print sql
        if not limit == 0:
            sql += " limit %s" %limit
        return self.database.query(sql)

    def findGroup(self):
        sql = "select groupid, groupname from group1"
        return self.database.query(sql)

    def mysqlinsert(self, username , dbname , msg):
        sql = """insert into mysqlonline set username="%s",dbname="%s",msg="%s" """ %(username , dbname , msg)
        self.database.execute(sql)

    def mysqlonlineshow(self, username):
        sql = "select logid,username,createtime,dbname,msg,`status` from mysqlonline where username='%s' and createtime>='%s';" % (username,currentTime())
        return self.database.query(sql)

    def mysqlonlineadminshow(self):
        sql = "select logid,username,createtime,dbname,msg,`status` from mysqlonline where createtime>='%s';" % currentTime()
        return self.database.query(sql)

    def updateMysql(self,logid):
        self.database.execute("update mysqlonline set `status`=1 where logid = %s" %(logid))
        sql = "select `status` from mysqlonline where logid='%s';" % logid
        return self.database.query(sql)