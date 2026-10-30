"""usage: finalize_narrative.py GAME -> (re)writes the numbering note + 'cited decision IDs' appendix of narratives/gXX.md"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
g = int(sys.argv[1]); rows = load_game(g)
p = "%s/narratives/g%02d.md" % (OUT, g)
s = open(p).read()
s = s.split("\n\n## Appendix — cited decision IDs")[0]
NOTE = "> Numbering: `#N` is the display number = 1-based line N of `public_review/game-%02d.jsonl`; the exact decision ID ends `-dec-(N-1)` zero-padded to 6 digits (e.g. #113 = `...-dec-000112`). `tN` / “turn N” are global engine turn_index values (one per player-turn), not a player's own-turn count; “global decisions” counts decisions by all players in the file. Public-message/action inconsistencies are described as observable inconsistencies with cause and intent unresolved.\n" % g
if "> Numbering:" not in s:
    lines = s.split("\n", 1)
    s = lines[0] + "\n\n" + NOTE + (lines[1] if len(lines) > 1 else "")
nums = sorted({int(x) for x in re.findall(r"#(\d+)", s) if 1 <= int(x) <= len(rows)})
pref = rows[0]["decision_id"].rsplit("-dec-", 1)[0]
app = "\n\n## Appendix — cited decision IDs (prefix `%s-dec-`)\n\n" % pref + "\n".join("- #%d → …-dec-%06d (%s, %s, turn %d, %s)" % (n, n - 1, rows[n-1]["player_id"], rows[n-1]["applied_action"]["action"], rows[n-1]["turn_index"], rows[n-1]["decision_type"]) for n in nums) + "\n"
open(p, "w").write(s.rstrip("\n") + app)
print("g%02d narrative: %d cited decision numbers" % (g, len(nums)))
