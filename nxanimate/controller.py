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
        self.graph = networkx.Graph()

    def __del__(self):
        self.script.close()

    def add_gui(self, gui):
        self.guis.append(gui)

    def remove_gui(self, gui):
        self.guis.remove(gui)

    def get_source_code(self):
        return '''import networkx as nx
import nxanimate.animations as nxa
G = nx.erdos_renyi_graph(10, 1/3)
print(1)
nxa.use_graph(G)
print(2)

print("a")
G.add_node(42)
print("b")
G.remove_node(42)
print("c")
G.add_edge("bar", "baz")
G.remove_edge("bar", "baz")
print("d")
for (n, data) in G.nodes(data=True):
    print(n)
    data["color"] = {"border": "red"}
'''


    #####################################
    # Called from GUI

    def add_node(self, x, y):
        attrs = {'x': x, 'y': y}
        self._last_node_id += 1
        while self.graph.has_node(self._last_node_id):
            self._last_node_id += 1
        self.graph.add_node(self._last_node_id, **attrs)
        return self._last_node_id

    def add_edge(self, from_, to):
        """Add an edge, return (id, attrs) if it does not exist,
        None otherwise."""
        if self.graph.is_multigraph():
            return (self.graph.add_edge(from_, to), {})
        elif self.graph.has_edge(from_, to):
            return None # The edge already exists, nothing to do
        else:
            self.graph.add_edge(from_, to)
            return (0, {})

    def step(self):
        """Run a line of the script in the debugger."""
        self.debugger.step()

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

    def on_dbg_new_graph(self, graph):
        print('new graph2')
        self.graph = graph
        for gui in self.guis:
            gui.request_redraw_graph(None)

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
                self.graph.add_node(id_, x=x, y=y)
            else:
                # Select a random point in the minimum bounding rectangle,
                # because it is (hopefully) included in the screen.
                x_set = {x for (n,x) in graph.nodes('x')}
                y_set = {y for (n,y) in graph.nodes('y')}
                x_set.remove(None) # the x value of the new node
                y_set.remove(None) # the y value of the new node
                if len(x_set) >= 2 and len(y_set) >= 2:
                    x = random.uniform(min(x_set), max(x_list))
                    y = random.uniform(min(y_set), max(y_list))
                else:
                    x = random.randrange(0, 10)
                    y = random.randrange(0, 10)
                self.graph.add_node(id_, x=x, y=y)
                self.graph.node[id_][x] = x
                self.graph.node[id_][y] = y

    def on_dbg_set_node_attribute(self, graph, id_, key, value):
        if graph is not self.graph:
            return
        else:
            for gui in self.guis:
                gui.update_node(id_, {key: value})

    def on_dbg_del_node_attribute(self, graph, id_, key):
        raise NotImplementedError('Deleting node attribute')

    def on_dbg_remove_node(self, graph, id_):
        if graph is not self.graph:
            return
        else:
            for gui in self.guis:
                gui.remove_node(id_)

    def on_dbg_add_edge(self, graph, from_, to, key, attrs):
        if graph is not self.graph:
            return
        else:
            for gui in self.guis:
                gui.add_edge(from_, to, key)

    def on_dbg_remove_edge(self, graph, from_, to, key):
        if graph is not self.graph:
            return
        else:
            for gui in self.guis:
                gui.remove_edge(from_, to, key)
