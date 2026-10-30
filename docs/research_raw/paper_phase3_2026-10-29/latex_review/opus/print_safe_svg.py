"""Derive a print-safe copy of an SVG whose fills use CSS custom properties.

librsvg (rsvg-convert) does not resolve CSS var(), so such fills render black.
This substitutes the light-scheme values declared on .viz and drops the dark-scheme
media block and the hover rule. Coordinates, text and data are unchanged.
Usage: python3 -I print_safe_svg.py <in.svg> <out.svg>
"""
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
decl = re.search(r"\.viz\{([^}]*)\}", src).group(1)
vars_ = dict(re.findall(r"(--[\w-]+):([^;]+)", decl))
out = re.sub(r"@media \(prefers-color-scheme: dark\)\{.*?\}\}", "", src, flags=re.S)
out = re.sub(r"g\.c:hover rect\{[^}]*\}", "", out)
out = re.sub(r"var\((--[\w-]+)\)", lambda m: vars_[m.group(1)], out)
assert "var(" not in out
open(sys.argv[2], "w", encoding="utf-8").write(out)
print(len(vars_), "variables substituted")
