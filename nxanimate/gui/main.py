import os.path
import functools
import configparser

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

from .highlighting import highlight, get_highlight_css
from .websocket_handler import WebSocketHandler

RESOURCES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client-resources')

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
        host = cherrypy.request.headers['Host']
        return 'websocket_url = "ws://{}/websocket";'.format(host).encode()

    @cherrypy.expose
    def websocket(self):
        pass


def gen_default_config(*, controller):
    default_config = {
            '/': {
                },
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
    return default_config

    parser = configparser.ConfigParser()
    for (section, values) in default_config.items():
        parser[section] = values
    return {k: dict(v) for (k,v) in parser.items()}

def start(controller, config=None):
    app = cherrypy.Application(Root(controller))
    app.merge(gen_default_config(controller=controller))

    cherrypy.quickstart(app, '/', config=config)
