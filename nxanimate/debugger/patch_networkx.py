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

class NodeDictFactory(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._graph = sys._getframe().f_back.f_locals['self']
        self._controller = magically_get_debugger().controller
        if not isinstance(self._graph, nx.Graph):
            raise ValueError(
                    'NodeDictFactory may only be instantiated from a Graph.')

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._controller.on_dbg_add_node(self._graph, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        # The controller won't be called if the key does not exist (on purpose)
        self._controller.on_dbg_remove_node(self._graph, key)


def patch_graph_class(cls):
    cls.node_dict_factory = NodeDictFactory
    

def patch_networkx():
    for cls in (nx.Graph, nx.DiGraph):
        # TODO: multi(di)graphs
        patch_graph_class(cls)
