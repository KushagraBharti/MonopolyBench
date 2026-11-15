"""Write every decision of the six above-bound financing attempts, all channels, to data/six_above_bound.txt."""
import io
from lib import *
from dump import dump
SIX = {7: [286, 287], 9: [194, 195, 196, 197], 17: [396, 397, 398], 18: [344], 19: [224, 225], 20: [273, 274]}
buf = io.StringIO()
for g, ds in SIX.items():
    for k, d in enumerate(ds):
        dump(g, d, notes=(k == 0), timeline=False, holdings=(k == 0), out=buf)
        buf.write("\n")
(HERE.parent / "data" / "six_above_bound.txt").write_text(buf.getvalue())
print(len(buf.getvalue()))
