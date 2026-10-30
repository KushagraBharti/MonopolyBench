"""usage: cand_lines.py CANDIDATE_ID  -> note lines tagged with that candidate id (from notes/*.txt)"""
import sys, glob, re, os
cid = sys.argv[1]
g = re.match(r"G(\d+)-", cid).group(1)
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for nf in sorted(glob.glob(OUT + "/notes/g%02d-p*.txt" % int(g))):
    for raw in open(nf):
        p = raw.rstrip("\n").split("|")
        if len(p) > 2 and cid in [c.strip() for c in p[2].split(",")]:
            rows.append((int(p[0]), p[1]))
print(cid, "lines:", ",".join(str(r[0]) for r in rows))
if len(sys.argv) > 2:
    for ln, n in rows: print(" ", ln, n[:140])
