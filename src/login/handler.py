#!-*- coding:utf-8 -*-
from lib.util            import Handler
from connect.tornado.web import Route

class LoginHandler(Handler):
    importName = __name__

@Route("/login/")
class login(LoginHandler):
    def get(self):
        local = locals(); del local["self"]
        local["msg"] = self.get_argument("msg", None)
        self.render("login.html", **local)
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        self.db.loginCheck(username, password)
        if (self.settings["admin"].get(username, None) == password and username == "admin") or \
            self.db.loginCheck(username, password):
            self.set_secure_cookie("login", username)
            self.redirect("/")
        else:
            self.redirect("/login/?msg=认证失败")

@Route("/logout/")
class logout(LoginHandler):
    def get(self):
        self.clear_cookie("login")
        self.redirect("/login/")

@Route("/adduser/")
class addUser(LoginHandler):
    def post(self):
        js = """<script language="javascript"> alert("%s");window.history.back(-1);</script>"""
        username = self.get_argument("username")
        password = self.get_argument("password")
        if self.db.addUser(username, password):
            self.write(js %("申请成功，请联系管理员开通功能。"))
        else:
            self.write(js %("申请失败，用户已经存在。"))
            
