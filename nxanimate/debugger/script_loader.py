import types
import os.path

_script_number = 0

def load_script(file_path):
    global _script_number
    _script_number += 1
    module_name = os.path.basename(file_path).rsplit('.', 1)[0]
    module_path = 'nxanimate.script{}.{}'.format(_script_number, module_name)
    with open(file_path) as fd:
        code = compile(fd.read(), file_path, 'exec')
    return code
