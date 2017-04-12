#!-*- coding:utf-8 -*-
import os
from lib.util            import db, svnClient
from connect.tornado.web import Route, App

if __name__ == "__main__":
    App.settings["debug"]            = True
    App.settings["login_url"]        = "/login/"
    App.settings["static_path"]      = 	os.path.join(os.path.dirname(__file__), "static")
    App.settings["svnCMSDdPath"]     = "/data/svnonline/beta.cms.u17.com/"
    App.settings["svnCMSOnlinePath"] = "/data/svnonline-prod/cms.u17.com/"
    App.settings["svnAPPDdPath"]     = "/data/svnonline/beta.app.u17.com/"
    App.settings["svnAPPOnlinePath"] = "/data/svnonline-prod/app.u17.com/"
    App.settings["svnBBSDdPath"]     = "/data/svnonline/beta.bbs.u17.com/"
    App.settings["svnBBSOnlinePath"] = "/data/svnonline-prod/bbs.u17.com/"
    App.settings["admin"]         = { "admin" : "111111" }
    
    Route.initialize(db = db(), svn = svnClient())
    App.register("src.index.handler")
    App.register("src.tool.handler")
    App.register("src.login.handler")
    App.register("src.admin.handler")
    App.register("src.mysql.handler")
    App.run()
