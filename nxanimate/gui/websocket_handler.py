import json

from ws4py.websocket import WebSocket

from .serialization import *

def expose(f):
    f.exposed = True
    return f

class WebSocketHandler(WebSocket):
    def __init__(self, *args, controller, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        controller.add_gui(self)

    def send(self, method, arg):
        content = method + ' ' + json.dumps(arg)
        print('Sent message: {}'.format(content))
        super().send(content)

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
            self.send('unknown_method', method_name)
            return

        method(arg)

    @expose
    def request_redraw_graph(self, arg):
        assert arg is None
        graph = self.controller.get_graph()
        self.send('redraw_graph', serialize_graph(graph))

    @expose
    def request_add_node(self, arg):
        assert isinstance(arg, dict)
        graph = self.controller.get_graph()
        x = arg.pop('x')
        y = arg.pop('y')
        id_ = self.controller.add_node(x, y)
        self.send('add_node', serialize_node(id_, {'x': x, 'y': y}))

    @expose
    def request_add_edge(self, arg):
        assert isinstance(arg, dict)
        graph = self.controller.get_graph()
        source = arg.pop('source')
        target = arg.pop('target')
        (key, attrs) = self.controller.add_edge(source, target)
        if key is not None:
            self.send('add_edge', serialize_edge(source, target, key, attrs))

    @expose
    def run(self, arg):
        assert arg is None
        self.controller.run()

    @expose
    def step(self, arg):
        assert arg is None
        self.controller.step()

    def set_line(self, lineno):
        self.send('set_lineno', lineno)
