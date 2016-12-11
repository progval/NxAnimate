import io

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class Formatter(HtmlFormatter):
    """Variant of HtmlFormatter with an id for each line numbers and
    an onclick property."""
    def _wrap_tablelinenos(self, inner):
        # Code copied from Pygment's _wrap_tablelinenos.
        dummyoutfile = io.StringIO()
        lncount = 0
        for t, line in inner:
            if t:
                lncount += 1
            dummyoutfile.write(line)

        fl = self.linenostart
        mw = len(str(lncount + fl - 1))
        sp = self.linenospecial
        st = self.linenostep
        aln = self.anchorlinenos
        nocls = self.noclasses
        assert not sp # Stripped that code
        assert not aln # Stripped that code
        lines = []
        for i in range(fl, fl+lncount):
            if i % st == 0:
                lines.append('<span id="lineno-%d">%*d</span>' % (i, mw, i))
            else:
                lines.append('')
        ls = '\n'.join(lines)


        assert not nocls # Stripped that code
        yield 0, ('<table class="%stable">' % self.cssclass +
                  '<tr><td class="linenos" id="linenos"><div class="linenodiv"><pre>' +
                  ls + '</pre></div></td><td class="code">')
        yield 0, dummyoutfile.getvalue()
        yield 0, '</td></tr></table>'


def highlight(code):
    lexer = get_lexer_by_name("python", stripall=True)
    formatter = Formatter(
            linenos=True, # Show line numbers.
            linespans="line", # Used for coloring the current line.
            )
    result = pygments.highlight(code, lexer, formatter)
    return result

def get_highlight_css():
    return HtmlFormatter().get_style_defs('.highlight')
