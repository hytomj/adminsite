import os, sys
import tornado.web
import tornado.ioloop
import tornado.httpserver
from   tornado.web     import URLSpec
from   tornado.options import define, options  
from   util            import get_root_path

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, **dict):
        for key in dict.keys():
            setattr(self, key, dict[key])

    def get_template_path(self):
        if getattr(self, "importName", None):
            templatePath = os.path.join(get_root_path(self.importName),getattr(self, "templatePath", "template"))
            return templatePath
        super(BaseHandler, self).get_template_path()
  #      print '[one] %s' % super(BaseHandler, self).get_template_path()
  #      print '[two] %s' % super(BaseHandler, self)


class Route(object):
    _routes    = []
    initialize = {}

    def __init__(self, route, init={}, name=None, host=".*$"):
        self.route = route
        self.init  = init or self.initialize
        self.name  = name
        self.host  = host

    @classmethod
    def initialize(self, **kwargs):
        if kwargs: self.initialize = kwargs

    def __call__(self, handler):
        name = self.name or handler.__name__
        spec = URLSpec(self.route, handler, self.init, name=name)
        self._routes.append({'host': self.host, 'spec': spec})
        return handler

    @classmethod
    def routes(cls, application=None):
        if application:
            for route in cls._routes:
                application.add_handlers(route['host'], route['spec'])
        else:
            return [route['spec'] for route in cls._routes]

class App(object):
    settings   = {}
    initialize = {}
    
    def __init__(self):
        pass

    @classmethod
    def register(self, name):
        self.initialize = self.__dict__.get("initialize", {})
        if self.initialize: Route.initialize = self.initialize
        __import__(name)
        

    @classmethod
    def run(self):
        basePath      = os.path.dirname(os.path.abspath(sys.argv[0]))
        srcPath       = os.path.join(basePath, "src")
        logPath       = os.path.join(basePath, "log")
        uploadPath    = os.path.join(basePath, "upload")
        staticPath    = os.path.join(basePath, "static")
        templatePath  = os.path.join(basePath, "template")
        for Path in [staticPath, templatePath, logPath, uploadPath]:
            if not os.path.isdir(Path): os.makedirs(Path)
        if not os.path.isdir(srcPath):
            if not os.path.isdir(srcPath): os.makedirs(srcPath)
            with open(os.path.join(srcPath, "__init__.py"), "w") as f: pass
        if not self.settings.get("port",              None): self.settings["port"]  = 5000
        if not self.settings.get("gzip",              None): self.settings["gzip"]  = False
        if not self.settings.get("debug",             None): self.settings["debug"] = False
        if not self.settings.get("xsrf_cookies",      None): self.settings["xsrf_cookies"]  = False
        if not self.settings.get("cookie_secret",     None): self.settings["cookie_secret"] = "qazxswedcvfrtgbnhyujmkiolp"
        if not self.settings.get("static_path",       None): self.settings["static_path"]   = staticPath
        if not self.settings.get("template_path",     None): self.settings["template_path"] = templatePath
        if not self.settings.get("static_url_prefix", None): self.settings["static_url_prefix"] = "/static/"
        define("port", default = self.settings["port"], help = "run on the given port", type = int)
        tornado.options.parse_command_line()
        application = tornado.web.Application(Route.routes(), **self.settings)
        server = tornado.httpserver.HTTPServer(application)
        server.bind(options.port)
        server.start()
        tornado.ioloop.IOLoop.instance().start()
