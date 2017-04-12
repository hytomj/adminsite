import tornado.web
from lib.util            import Handler
from connect.tornado.web import Route

class IndexHandler(Handler):
    importName = __name__

@Route("/")
class index(IndexHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("index.html", username = self.get_secure_cookie("login"))
