"""Write the full first-decision record of the sixteen necessary-collateral episodes to data/sixteen_first_decisions.txt."""
import io
from lib import *
from dump import dump
SIXTEEN = [(1,476),(2,216),(4,270),(4,308),(5,263),(6,185),(8,257),(11,203),(12,190),(13,195),(17,234),(17,254),(18,309),(18,313),(20,291),(20,327)]
if __name__ == "__main__":
    buf = io.StringIO()
    for g, d in SIXTEEN:
        dump(g, d, notes=True, timeline=False, holdings=True, out=buf)
        buf.write("\n")
    (HERE.parent / "data" / "sixteen_first_decisions.txt").write_text(buf.getvalue())
    print(len(buf.getvalue()))
