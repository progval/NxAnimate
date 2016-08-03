import json

def serialize_graph(graph):
    d = {
            'directed': False,
            'multi': False,
            'nodes': [
                {
                    'id': id_,
                    'x': attrs['x'],
                    'y': attrs['y'],
                    'size': 1,
                    }
                for (id_, attrs) in graph.nodes(data=True)],
            'edges': [
                {
                    'id': attrs['id'],
                    'source': from_,
                    'target': to,
                    }
                for (from_, to, attrs) in graph.edges(data=True)],
            }
    return json.dumps(d)
