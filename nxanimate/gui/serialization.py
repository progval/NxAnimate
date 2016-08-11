import json
import collections

_last_edge_id = -1
def new_edge_id():
    global _last_edge_id
    _last_edge_id += 1
    return _last_edge_id
_edge_ids = collections.defaultdict(new_edge_id)

def make_edge_id(source, target, key):
    return _edge_ids[(source, target, key)]

'''
def make_edge_id(source, target, key):
    """Make a sigma.js edge id (int) from a NetworkX edge id
    ((source, target, key)).
    This function is determinist and injective."""
    shift = max(source, target, key).bit_length()
    return (((((1 << shift) + source) << shift) + target) << shift) + local_id
'''

def serialize_node(id_, attrs):
    d = attrs.copy()
    d.update({
            'id': id_,
            'size': 10,
            })
    return d

def get_graph_edges_with_keys(graph):
    if graph.is_multigraph():
        return graph.edges(data=True, keys=True)
    else:
        print(list(graph.edges(data=True)))
        return ((u,v,0,data) for (u,v,data) in graph.edges(data=True))

def serialize_edge(source, target, key, attrs):
    d = attrs.copy()
    d.update({
            'id': make_edge_id(source, target, key),
            'source': source,
            'target': target,
            'key': key,
            })
    return d

def serialize_graph(graph):
    d = {
            'directed': graph.is_directed(),
            'multi': graph.is_multigraph(),
            'nodes': [serialize_node(*node)
                      for node in graph.nodes(data=True)],
            'edges': [serialize_edge(*edge)
                      for edge in get_graph_edges_with_keys(graph)],
            }
    return d
