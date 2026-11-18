"""The page writes moves made at the same moment in round brackets, (12)(34), as siteswap does for sync throws
(square brackets are kept for multiplexes). The search tools work in square brackets; this turns every quoted
pattern in a block of page code into round brackets before it is written into index.html."""
import re

PATTERN = re.compile(r'''(["'])([0-9zsp\[\]|\- ]*\[[0-9zsp]{2}\][0-9zsp\[\]|\- ]*)\1''')

def round_brackets(code):
    return PATTERN.sub(lambda m: m.group(1) + m.group(2).replace('[', '(').replace(']', ')') + m.group(1), code)
