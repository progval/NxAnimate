import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def highlight(code):
    lexer = get_lexer_by_name("python", stripall=True)
    formatter = HtmlFormatter(linenos=True, linespans="line")
    result = pygments.highlight(code, lexer, formatter)
    return result

def get_highlight_css():
    return HtmlFormatter().get_style_defs('.highlight')
