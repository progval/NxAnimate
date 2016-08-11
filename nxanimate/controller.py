import random
import tempfile
import operator

import networkx

from .debugger.debugger import Debugger

class Controller:
    def __init__(self):
        self._last_node_id = -1
        self.guis = []
        self.script = tempfile.NamedTemporaryFile('at')
        self.script.write(self.get_source_code())
        self.script.flush()
        self.debugger = Debugger(self.script.name, self)
        self.load_graph()

    def __del__(self):
        self.script.close()

    def add_gui(self, gui):
        self.guis.append(gui)

    def load_graph(self):
        self.graph = g = networkx.Graph()
        g.add_node('foo', x=100, y=100)
        g.add_node('bar', x=200, y=100)
        g.add_node('baz', x=100, y=200)
        g.add_edge('foo', 'bar')
        g.add_edge('foo', 'baz')

    def get_source_code(self):
        return 'print("a")\nG.add_node(42)\nprint("b")\nG.remove_node(42)\nprint("c")\nprint("d")\nfor x in range(10):\n    print(x)\n'


    #####################################
    # Called from GUI

    def add_node(self, x, y):
        attrs = {'x': x, 'y': y}
        self._last_node_id += 1
        while self.graph.has_node(self._last_node_id):
            self._last_node_id += 1
        self.graph.add_node(self._last_node_id, **attrs)
        return self._last_node_id

    def add_edge(self, source, target):
        """Add an edge, return (id, attrs) if it does not exist,
        None otherwise."""
        if self.graph.is_multigraph():
            return (self.graph.add_edge(source, target), {})
        elif self.graph.has_edge(source, target):
            return None # The edge already exists, nothing to do
        else:
            self.graph.add_edge(source, target)
            return (0, {})

    def step(self):
        """Run a line of the script in the debugger."""
        print('--')
        print(list(self.graph.nodes()))
        self.debugger.step()
        print(list(self.graph.nodes()))

    def continue_(self):
        """Run the script in the debugger, until a breakpoint is met."""
        self.debugger.continue_()

    def has_breakpoint(self, lineno):
        return self.debugger.has_breakpoint(lineno)

    def add_breakpoint(self, lineno):
        assert not self.has_breakpoint(lineno)
        self.debugger.add_breakpoint(lineno)

    def remove_breakpoint(self, lineno):
        assert self.has_breakpoint(lineno)
        self.debugger.remove_breakpoint(lineno)


    #####################################
    # Called from debugger

    def on_dbg_line(self, lineno):
        for gui in self.guis:
            gui.set_line(lineno)

    def on_dbg_add_node(self, graph, id_, attrs):
        if graph is not self.graph:
            return
        else:
            if 'x' in attrs or 'y' in attrs:
                assert 'x' in attrs and 'y' in attrs
                x = attrs['x']
                y = attrs['y']
            else:
                if self.graph.number_of_nodes() >= 2:
                    # Select a random point in the minimum bounding rectangle,
                    # because it is (hopefully) included in the screen.
                    x_list = list(map(operator.itemgetter(1), graph.nodes('x')))
                    y_list = list(map(operator.itemgetter(1), graph.nodes('x')))
                    x_list.remove(None) # the x value of the new node
                    y_list.remove(None) # the y value of the new node
                    x = random.randrange(min(x_list), max(x_list))
                    y = random.randrange(min(y_list), max(y_list))
                else:
                    x = random.randrange(0, 10)
                    y = random.randrange(0, 10)
                self.graph.node[id_]['x'] = x
                self.graph.node[id_]['y'] = y
            for gui in self.guis:
                gui.add_node(id_, x, y)

    def on_dbg_remove_node(self, graph, id_):
        if graph is not self.graph:
            return
        else:
            for gui in self.guis:
                gui.remove_node(id_)
