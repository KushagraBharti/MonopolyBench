"""Convert a downloaded arXiv HTML page to plain text with '## ' section markers.

Usage: python3 -I html2txt.py <in.html> <out.txt>
Prints the section index (character offset and heading) for navigation.
"""
import html
import re
import sys

t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
# Keep LaTeXML math as its alttext so signs and values survive conversion.
t = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', lambda m: " " + html.unescape(m.group(1)) + " ", t, flags=re.S)
t = re.sub(r"<math.*?</math>", "", t, flags=re.S)
t = re.sub(r"<(h[1-6])[^>]*>", "\n\n## ", t)
t = re.sub(r"</(p|div|li|tr|h[1-6])>", "\n", t)
t = html.unescape(re.sub(r"<[^>]+>", " ", t))
t = re.sub(r"[ \t]+", " ", t)
t = re.sub(r"\n\s*\n+", "\n\n", t)
open(sys.argv[2], "w").write(t)
for m in re.finditer(r"\n## [^\n]*", t):
    print(m.start(), m.group(0).strip()[:110])
