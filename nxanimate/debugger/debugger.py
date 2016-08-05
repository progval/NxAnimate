import bdb
import threading

from .script_loader import load_script

class Debugger(bdb.Bdb):
    def __init__(self, file_name, controller):
        self._code = load_script(file_name)
        self._controller = controller
        self._release_line = threading.Event()
        super().__init__()
        self.set_step()

    def run(self):
        self.thread = threading.Thread(target=super().run, args=(self._code,))
        self.thread.start()

    def is_skipped_module(self, module_name):
        print(module_name)
        return module_name.startswith('nxanimate.script')

    def user_line(self, frame):
        self._release_line.clear()
        self._controller.on_dbg_line(frame.f_lineno)
        self._release_line.wait()

    def step(self):
        self._release_line.set()
