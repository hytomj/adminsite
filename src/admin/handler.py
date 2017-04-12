#!coding:utf-8
import os
import tornado.web
from lib.util            import Handler
from connect.tornado.web import Route

class AdminHandler(Handler):
    importName = __name__

@Route("/admin/(.*?)/?")
class Admin(AdminHandler):
    @tornado.web.authenticated
    def get(self, method):
        self.checkAdmin()
        method = method or "show"
        if method == "show":
            self.render("user.html", userinfo = self.db.showUser())
        elif method == "showgroup":
            self.render("group.html", userinfo = self.db.showGroup())
        elif method == "update":
            username  = self.get_argument("username")
            password  = self.get_argument("password")
            groupid   = self.get_argument("groupid") or 0
            status    = 1 if self.get_argument("status") == "true" else 0
            ftpstatus = 1 if self.get_argument("ftpstatus") == "true" else 0
            self.db.setUser(username, password, status, ftpstatus, groupid)
            self.ftpuser(username, self.db.getGroupName(groupid), ftpstatus)
            self.render("user.html", userinfo = self.db.showUser())
        elif method == "updategroup":
            groupname = self.get_argument("groupname")
            status    = 1 if self.get_argument("status") == "true" else 0
            self.db.addGroup(groupname, status)
            self.render("group.html", userinfo = self.db.showGroup())
        elif method == "setgroup":
            groupid   = self.get_argument("groupid")
            groupname = self.get_argument("groupname")
            status    = 1 if self.get_argument("status") == "true" else 0
            self.db.setGroup(self, groupid, groupname, status)
            self.render("group.html", userinfo = self.db.showGroup())
        elif method == "delgroup":
            groupid   = self.get_argument("groupid")
            self.db.delGroup(groupid)
            self.render("group.html", userinfo = self.db.showGroup())
        elif method == "deluser":
            userid = self.get_argument("userid")
            self.db.delUser(userid)
            self.render("user.html", userinfo = self.db.showUser())
           
           
            

    @tornado.web.authenticated
    def checkAdmin(self):
        if not self.get_secure_cookie("login") == "admin":
            self.redirect("/")

    def ftpuser(self, username, groupname, method = 0):
        if u"美术" in groupname:
            path = "/data/svnonline/beta.cms.u17.com/static/"
        elif u"开发" in groupname:
            path = "/data/svnonline/"
        filepath = os.path.join("/etc/vsftpd/vuser_conf/", username)
        conf = "\n".join([
                           "local_root=%s" %path,
                           "write_enable=YES",
                           "anon_umask=022",
                           "anon_upload_enable=YES",
                           "anon_world_readable_only=NO",
                           "anon_mkdir_write_enable=YES",
                           "anon_other_write_enable=YES"
                        ])
        with open(filepath, "w") as f:
            if method:
                f.write(conf)
