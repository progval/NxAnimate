import json

from ws4py.websocket import WebSocket

from .serialization import *

def expose(f):
    f.exposed = True
    return f

class WebSocketHandler(WebSocket):
    def __init__(self, *args, controller, **kwargs):
        self.controller = controller
        super().__init__(*args, **kwargs)

    def received_message(self, message):
        content = message.data.decode()
        print('Received message: {}'.format(content))
        if ' ' in content:
            (method_name, arg) = content.split(' ', 1)
            arg = json.loads(arg)
        else:
            method_name = content
            arg = None

        try:
            method = getattr(self, method_name)
            if not getattr(method, 'exposed', False):
                raise AttributeError()
        except AttributeError:
            self.send('Unknown method: {}'.format(method_name))
            return

        method(arg)

    @expose
    def request_redraw_graph(self, arg):
        assert arg is None
        graph = self.controller.get_graph()
        s = 'redraw_graph ' + serialize_graph(graph)
        print(s)
        self.send(s)
