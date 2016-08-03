from .controller import Controller
from .gui.main import start as gui_start
from .gui.main import gen_config as gen_gui_config

def main():
    controller = Controller()
    gui_config = gen_gui_config(
            controller=controller,
            )
    gui_start(config=gui_config)
