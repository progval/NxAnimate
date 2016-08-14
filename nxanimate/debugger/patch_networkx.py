"""Monkey-patches NetworkX's classes."""

import sys
import collections

import networkx as nx

from .debugger import Debugger
from ..controller import Controller

def magically_get_debugger():
    """Browse the call stack to find the controller of the script calling
    this function."""
    frame = sys._getframe().f_back
    while frame:
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            if isinstance(obj, Debugger):
                return obj
            elif isinstance(obj, Controller):
                return obj.debugger
        frame = frame.f_back
    raise ValueError(
            'magically_get_debugger() was not called from a debugged script.')

class NodeDict(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._graph = sys._getframe().f_back.f_locals['self']
        self._controller = magically_get_debugger().controller
        if not isinstance(self._graph, nx.Graph):
            raise ValueError(
                    'NodeDict may only be instantiated from a Graph.')

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._controller.on_dbg_add_node(self._graph, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        # The controller won't be called if the key does not exist (on purpose)
        self._controller.on_dbg_remove_node(self._graph, key)


class OuterEdgeDict(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._graph = sys._getframe().f_back.f_locals['self']
        self._controller = magically_get_debugger().controller
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
