import networkx

class Controller:
    def __init__(self):
        self._last_node_id = -1
        self.load_graph()

    def load_graph(self):
        g = networkx.Graph()
        g.add_node('foo', x=100, y=100)
        g.add_node('bar', x=200, y=100)
        g.add_node('baz', x=100, y=200)
        g.add_edge('foo', 'bar')
        g.add_edge('foo', 'baz')
        self.graph = g

    def get_graph(self):
        return self.graph

    def add_node(self, x, y):
        attrs = {'x': x, 'y': y}
        self._last_node_id += 1
        while self.graph.has_node(self._last_node_id):
            self._last_node_id += 1
        self.graph.add_node(self._last_node_id)
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
