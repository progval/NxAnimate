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
        if self.stream is None:
            self.controller.remove_gui(self)
            return
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
        graph = self.controller.graph
        self.send('redraw_graph', serialize_graph(graph))

    @expose
    def request_add_node(self, arg):
        assert isinstance(arg, dict)
        graph = self.controller.graph
        x = arg.pop('x')
        y = arg.pop('y')
        id_ = self.controller.add_node(x, y)

    def add_node(self, id_, x, y):
        self.send('add_node', serialize_node(id_, {'x': x, 'y': y}))

    def remove_node(self, id_):
        self.send('remove_node', id_)

    @expose
    def request_add_edge(self, arg):
        assert isinstance(arg, dict)
        graph = self.controller.graph
        print(arg)
        from_ = arg.pop('from')
        to = arg.pop('to')
        res = self.controller.add_edge(from_, to)
        if res is not None:
            (key, attrs) = res
            self.send('add_edge', serialize_edge(from_, to, key, attrs))

    @expose
    def step(self, arg):
        assert arg is None
        self.controller.step()

    @expose
    def cont(self, arg):
        assert arg is None
        self.controller.continue_()

    def set_line(self, lineno):
        # Called from the controller
        self.send('set_lineno', lineno)

    @expose
    def flip_breakpoint(self, lineno):
        if self.controller.has_breakpoint(lineno):
            self.send('remove_breakpoint', lineno)
            self.controller.remove_breakpoint(lineno)
        else:
            self.send('add_breakpoint', lineno)
            self.controller.add_breakpoint(lineno)
