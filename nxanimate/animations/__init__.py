from ..debugger import magic

def use_graph(graph):
    print('use graph1')
    debugger = magic.get_debugger()
    debugger.controller.on_dbg_new_graph(graph)
