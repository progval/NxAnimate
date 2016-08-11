from .controller import Controller
from .gui.main import start as gui_start
from .gui.main import gen_config as gen_gui_config
from .debugger.patch_networkx import patch_networkx

def main():
    patch_networkx()
    controller = Controller()
    gui_config = gen_gui_config(
            controller=controller,
            )
    gui_start(
            controller=controller,
            config=gui_config,
            )
