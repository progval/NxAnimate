import sys

from .debugger import Debugger
from ..controller import Controller

def get_debugger():
    """Browse the call stack to find the controller of the script calling
    this function."""
    frame = sys._getframe().f_back
    while frame:
        debugger = frame.f_globals.get('__NxAnimate_debugger', None)
        if debugger is not None:
            assert isinstance(debugger, Debugger)
            return debugger
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            if isinstance(obj, Debugger):
                return obj
            elif isinstance(obj, Controller):
                return obj.debugger
        frame = frame.f_back
    raise ValueError(
            'magic.get_debugger() was not called from a debugged script.')
