import bdb
import threading

from .script_loader import load_script

class NxAnimateBdb(bdb.Bdb):
    def __init__(self, release_line, line_callback):
        super().__init__()
        self.stepping = True
        self.continue_execution = release_line
        self._line_callback = line_callback

    def is_skipped_module(self, module_name):
        return module_name.startswith('nxanimate.script')

    def user_line(self, frame):
        if not frame.f_globals.get('__NxAnimate_debugged_script', False):
            return
        self.continue_execution.clear()
        if self.stepping or self.break_here(frame):
            self._line_callback(frame.f_lineno)
            self.continue_execution.wait() # Wait before going to the next line

class Debugger:
    def __init__(self, file_name, controller):
        self._file_name = file_name
        self._code = load_script(file_name)
        self.controller = controller
        self._thread = None

        self.continue_execution = threading.Event()
        self._bdb = NxAnimateBdb(self.continue_execution, self.controller.on_dbg_line)
        self._bdb.set_step()

    def _run(self):
        globals_env = {'G': self.controller.graph, '__NxAnimate_debugged_script': True}
        self._thread = threading.Thread(target=self._bdb.run,
                args=(self._code,), kwargs={'globals': globals_env})
        self._thread.start()

    def step(self):
        self._bdb.stepping = True
        self.continue_execution.set()
        if not self._thread:
            self._run()

    def continue_(self):
        self._bdb.stepping = False
        self.continue_execution.set()
        if not self._thread:
            self._run()

    def has_breakpoint(self, lineno):
        return self._bdb.get_break(self._file_name, lineno)

    def add_breakpoint(self, lineno):
        self._bdb.set_break(self._file_name, lineno)

    def remove_breakpoint(self, lineno):
        self._bdb.clear_break(self._file_name, lineno)
