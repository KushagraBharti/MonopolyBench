"""Copy selected original evidence after whole-game reading; assign no labels."""
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
phase = here.parent.parent
manifest = json.loads((phase / 'full_review/game-20/manifest.json').read_text())
selected = [1, 4, 6, 46, 77, 83, 92, 95, 96, 97, 98, 100, 101, 119,
            129, 130, 168, 172, 176, 177, 185, 186, 187, 188, 194, 197,
            198, 244, 250, 251, 261, 263, 264, 265, 273, 274, 278,
            289, 291, 294, 295, 296, 299, 305, 306, 310, 313, 315,
            318, 322, 324, 325, 327, 328, 336, 338, 339, 340, 342,
            344, 346, 348, 353, 354]
out = []
for index in selected:
    source = manifest['sources'][index]
    line = (root / source['packet']).read_text().splitlines()[source['packet_line'] - 1]
    assert hashlib.sha256(line.encode()).hexdigest() == source['source_line_sha256']
    packet = json.loads(line)
    assert packet['decision_id'] == source['decision_id']
    out.append({'decision_index': index, 'source': source,
                **{k: packet[k] for k in ['applied_action_record', 'initial_prompt',
                                          'attempts', 'canonical_event_segment']}})
(here / 'game-20/source_checks.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'selected_original_packets_checked': len(out), 'sha256_checks': 'passed'}))
