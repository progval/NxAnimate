import os.path
import functools

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

from .highlighting import highlight, get_highlight_css
from .websocket_handler import WebSocketHandler

PORT = 8000
RESOURCES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client-resources')

cherrypy.config.update({'server.socket_port': PORT})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

class Root(object):
    def __init__(self, controller):
        self.controller = controller
        super().__init__()

    @cherrypy.expose
    def index(self):
        source_code = self.controller.get_source_code()
        source_code = highlight(source_code).encode()
        cherrypy.response.headers['Content-Type'] = 'application/xhtml+xml'
        with open(os.path.join(RESOURCES_PATH, 'index.xhtml'), 'rb') as fd:
            return fd.read().replace(b'{{sourcecode}}', source_code)

    @cherrypy.expose('highlight.css')
    def highlight(self):
        cherrypy.response.headers['Content-Type'] = 'text/css'
        return get_highlight_css()

    @cherrypy.expose('config.js')
    def config(self):
        cherrypy.response.headers['Content-Type'] = 'text/javascript'
        return 'websocket_url = "ws://localhost:{}/websocket";'.format(PORT).encode()

    @cherrypy.expose
    def websocket(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler


def gen_config(*, controller):
    return {
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': RESOURCES_PATH,
                },
            '/websocket': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls':
                        functools.partial(WebSocketHandler,
                            controller=controller,
                            ),
                },
            }

def start(controller, config=None):
    cherrypy.quickstart(Root(controller), '/', config=config)
