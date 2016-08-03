import networkx

class Controller:
    def get_graph(self):
        g = networkx.Graph()
        g.add_node('foo', x=1, y=1)
        g.add_node('bar', x=2, y=1)
        g.add_node('baz', x=1, y=2)
        g.add_edge('foo', 'bar', id=1)
        g.add_edge('foo', 'baz', id=2)
        return g
