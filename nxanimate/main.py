import os
import sys
from .controller import Controller
from .gui.main import start as gui_start
from .debugger.patch_networkx import patch_networkx

def main():
    patch_networkx()
    controller = Controller()

    if len(sys.argv) == 1:
        config = None
    elif len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        config = sys.argv[1]
    else:
        print('Syntax: {} [config.ini]'.format(sys.argv[0]))
        exit(1)

    gui_start(
            controller=controller,
            config=config,
            )
