"""Monkey-patches NetworkX's classes."""

import sys
import collections

import networkx as nx

from . import magic
from .debugger import Debugger
from ..controller import Controller


class AttrsDict(collections.UserDict):
    def __init__(self, data, graph, controller, node_id):
        super().__init__()
        self.data = data
        self._graph = graph
        self._controller = controller
        self._node_id = node_id

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._controller.on_dbg_set_node_attribute(self._graph,
                self._node_id, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._controller.on_dbg_del_node_attribute(self._graph,
                self._node_id, key)


class NodeDict(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._graph = sys._getframe().f_back.f_locals['self']
        self._controller = magic.get_debugger().controller
        if not isinstance(self._graph, nx.Graph):
            raise ValueError(
                    'NodeDict may only be instantiated from a Graph.')

    def __setitem__(self, id_, attrs):
        if not isinstance(attrs, AttrsDict):
            attrs = AttrsDict(attrs, self._graph, self._controller, id_)
        super().__setitem__(id_, attrs)
        self._controller.on_dbg_add_node(self._graph, id_, attrs)

    def __delitem__(self, id_):
        super().__delitem__(id_)
        # The controller won't be called if the key does not exist (on purpose)
        self._controller.on_dbg_remove_node(self._graph, id_)


class OuterEdgeDict(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._graph = sys._getframe().f_back.f_locals['self']
        self._controller = magic.get_debugger().controller
        if not isinstance(self._graph, nx.Graph):
            raise ValueError(
                    'InnerEdgeDict may only be instantiated from a Graph.')

    def __setitem__(self, from_, inner):
        assert isinstance(inner, InnerEdgeDict)
        super().__setitem__(from_, inner)
        inner._graph = self._graph
        inner._controller = self._controller
        inner._from = from_

class InnerEdgeDict(collections.UserDict):
    # Attributes _graph, _controller, and _from are set by OuterEdgeDict
    # when the InnerEdgeDict instance is added to it.

    def __setitem__(self, to, attrs):
        assert not self._graph.is_multigraph() # TODO

        already_has_edge = not self._graph.is_directed() and \
                self._graph.has_edge(to, self._from)

        super().__setitem__(to, attrs)

        if not already_has_edge:
            # Do not notify controller twice for undirected graphs.
            self._controller.on_dbg_add_edge(self._graph, self._from, to, 0, attrs)

    def __delitem__(self, to):
        assert not self._graph.is_multigraph() # TODO

        already_has_edge = not self._graph.is_directed() and \
                self._graph.has_edge(to, self._from)

        super().__delitem__(to)

        if already_has_edge:
            self._controller.on_dbg_remove_edge(self._graph, self._from, to, 0)



def patch_graph_class(cls):
    cls.node_dict_factory = NodeDict
    cls.adjlist_outer_dict_factory = OuterEdgeDict
    cls.adjlist_inner_dict_factory = InnerEdgeDict


def patch_networkx():
    for cls in (nx.Graph, nx.DiGraph):
        # TODO: multi(di)graphs
        patch_graph_class(cls)
