from .controller import Controller
from .gui.main import start as gui_start
from .debugger.patch_networkx import patch_networkx

def main():
    patch_networkx()
    controller = Controller()
    gui_start(
            controller=controller,
            config='config.ini',
            )
