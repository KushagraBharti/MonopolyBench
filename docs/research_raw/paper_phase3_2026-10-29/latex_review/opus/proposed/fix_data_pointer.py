"""Opus proposal: move each figure's 'Underlying data' pointer from a \\tablenote placed after
\\end{figure} (which creates an extra text page and, inside pdflscape, an unrotated float page)
into the end of the caption itself. Idempotent. Usage: python3 -I fix_data_pointer.py <latex dir>"""
import re, sys
from pathlib import Path
for p in sorted(Path(sys.argv[1], 'figures').glob('f*.tex')):
    t = p.read_text()
    m = re.search(r'\n% Native data cross-reference\n\\tablenote\{(Underlying data: [^\n]*?)\}\n', t)
    if not m:
        continue
    pointer = m.group(1)
    t = t[:m.start()] + '\n'
    # insert before the closing brace of \caption[..]{...}, i.e. just before '}\n\label{fig:'
    t, n = re.subn(r'\}\n\\label\{fig:', ' ' + pointer.replace('\\', '\\\\') + '}\n\\\\label{fig:', t, count=1)
    assert n == 1, p
    p.write_text(t)
    print('moved into caption:', p.name)
