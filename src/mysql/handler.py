#-*- coding: UTF-8 -*-
import tornado.web
import tornado.httpserver
from lib.util import Handler
from lib.mysendmail import send_mail
from connect.tornado.web import Route

import json

class MysqlHandler(Handler):
    importName = __name__

@Route("/mysql/")
class mysql(MysqlHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render("mysql.html")

    @tornado.web.authenticated
    def post(self):
        dbname = self.get_argument("dbname",0)
        #if not dbname or not str(name).strip():
         #   raise tornado.web.HTTPError(500, "请填写dbname")
        #comment = self.request.files['myfile']
        comment = self.get_argument("myfile")
        username = self.current_user
        res = comment.lower()
        self.db.mysqlinsert(username,dbname,res)
        alert_context =  "提交成功! 请等待审核...\n您提交的内容如下:\n%s" % res
        self.write(alert_context)

@Route("/userinfo/(.*?)/")
class userinfo(MysqlHandler):
    @tornado.web.authenticated
    def get(self,method):
        if method == "show":
            if self.current_user == "admin":
                result = self.db.mysqlonlineadminshow()
            else:
                result = self.db.mysqlonlineshow(self.current_user)
            if result:
                return self.render("user_info.html",result=result)

    @tornado.web.authenticated
    def post(self,method):
        if method == "updatemysql":
            logid = self.get_argument("logid")
            username = self.get_argument("username")
            if self.current_user == "admin":
                if self.db.updateMysql(logid):
                    self.write("上线成功")
                    temptext = "你有新的数据库上线通知,请登录系统进行查看."
                    send_mail(['%s@u17.com' % username,],'数据库上线通知','<html>用户%s你好!<br/><br/>%s<br/></html>' % (username,temptext))
                else:
                    self.write("上线失败")

              