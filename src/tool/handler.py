#!-*- coding:utf-8 -*-
import shutil
import os, re
import tornado.web
import tornado.gen
from   tornado.httpclient  import AsyncHTTPClient
from   lib.util            import svnClient, Handler
from   connect.tornado.web import Route


class SvnHandler(Handler):
    importName = __name__

@Route("/svn/")
class svn(SvnHandler):
    @tornado.web.authenticated
    def get(self):
        svnLogInfo    = []
        args = self.get_argument("args", None)
        if args == "cms":
            svnDdPath     = self.settings["svnCMSDdPath"]
            svnOnlinePath = self.settings["svnCMSOnlinePath"]
        elif args == "app":
            svnDdPath     = self.settings["svnAPPDdPath"]
            svnOnlinePath = self.settings["svnAPPOnlinePath"]
        elif args == "bbs":
            svnDdPath     = self.settings["svnBBSDdPath"]
            svnOnlinePath = self.settings["svnBBSOnlinePath"]
        svnLogLimit   = self.get_argument("limit") or 10
        #print svnDdPath
        #print svnOnlinePath
        for oneData in self.svn.log(svnDdPath, limit = svnLogLimit, discover_changed_paths=True, strict_node_history=True):
            svnInfo  = {}
            svnInfo["date"]     = int(oneData["date"])
            svnInfo["author"]   = oneData["author"]
            svnInfo["revision"] = oneData["revision"].number
            svnInfo["changed"]  = []
            for file in oneData["changed_paths"]:
                action = file["action"]
                path   = file["path"]
                svnInfo["changed"].append("%s %s" %(action, path))
            svnLogInfo.append(svnInfo)
        local = locals()
        del local["self"]
        return self.render("svn.html", **local)
    @tornado.web.authenticated
    def post(self):
        tmppath = []
        username = self.get_current_user()
        filePath = self.get_arguments("filepath", [])
	print "1. filePath:%s" % filePath
        if not filePath:
            result = "请选择需要提交的文件"
        else:
            svnDdPath=""
            if self.get_argument("args", None) == "cms":
                svnDdPath     = self.settings["svnCMSDdPath"]
                svnOnlinePath = self.settings["svnCMSOnlinePath"]
            elif self.get_argument("args", None) == "app":
                svnDdPath     = self.settings["svnAPPDdPath"]
                svnOnlinePath = self.settings["svnAPPOnlinePath"]
            elif self.get_argument("args", None) == "bbs":
                svnDdPath     = self.settings["svnBBSDdPath"]
                svnOnlinePath = self.settings["svnBBSOnlinePath"]
		for i in range(0,len(filePath)):
        		old = '/bbs.u17.com.dzx3/trunk/'
        		new = ''
        		filePath[i] = filePath[i].replace(old,new)
            for file in filePath:
                if os.path.isdir(os.path.join(svnDdPath, file)) and \
                not os.path.isdir(os.path.join(svnOnlinePath, file)):
                    tmppath.append(os.path.join(svnOnlinePath, file))
                    #os.mkdir(os.path.join(svnOnlinePath, file))
            print "Tmppath:%s" % tmppath
	    print "2. %s\t" % filePath
            for x1 in sorted(tmppath, key=lambda str: len(str.split("/"))):
                    os.mkdir(x1)
            for file in filePath:
                print os.path.join(svnDdPath, file)
                if not file.endswith('config.inc.php') and os.path.isfile(os.path.join(svnDdPath, file)):
                    src = os.path.join(svnDdPath, file)
                    dst = os.path.join(svnOnlinePath, file)
                    dstDir = os.path.dirname(dst)
                    if (os.path.exists(dstDir) == False):
                        os.makedirs(dstDir)
                    shutil.copy(os.path.join(svnDdPath, file), os.path.join(svnOnlinePath, file))
            result =  "%s\n提交成功，系统会自动提交到正式环境中。" %(str("\n".join(filePath)))
            self.db.insertLog(username, str("\n".join(filePath)))
        self.write(result)

@Route("/svnlog/")
class svnlog(SvnHandler):
    @tornado.web.authenticated
    def get(self):
        args = None
        username = self.get_current_user()
        svnLogLimit   = self.get_argument("limit") or 10
        logs     = self.db.findLog(self.get_current_user(), svnLogLimit)
        local = locals(); del local["self"]
        return self.render("log.html", **local)

@Route("/log/")
class log(SvnHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.get_current_user()
        return self.render("phplog.html") 

@Route("/javasync/")
class JavaSync(SvnHandler):
    @tornado.gen.engine
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        client   = AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, "http://192.168.1.2:8080/java_sync/")
        self.write(re.search(
                             r"<form id=\"java_sync\".*?</form>", response.body, re.S).group().\
                             replace("action=\"/java_sync/\"",
                             "action=\"http://192.168.1.2:8080/java_sync/\"").\
                   replace("""<input type="submit" name="submit" value="提交">""", 
                           """<input class="btn btn-default" type="submit" value="提交"> """).\
                   replace("""<form """, """<form class="form-horizontal" """).\
                   replace("""<select """, """<select class="form-control" """)
                  )
        self.finish()
