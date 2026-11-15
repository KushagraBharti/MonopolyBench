"""Opus final review: exact source spans proposed in replacement_prose.tex.

Reads saved decisions.jsonl only. For each span, prints the game, decision,
attempt, field, character offset, field SHA-256 and whether the exact text occurs.
"""
import json, hashlib, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
gm = json.load(open(ROOT / 'docs/research_raw/paper_revision_2026-11-12/integrated/data/game_map.json'))

SPANS = [
    ('g18-d431-reservation', 18, 431, 'reasoning', "Buying Pacific might just prolong p1's survival, so maybe it's smarter to hold onto cash"),
    ('g18-d438-extends', 18, 438, 'reasoning', "giving them $450 mainly just extends the game"),
    ('g15-d162-policy', 15, 162, 'private_thought', "Never trade Ventnor or Penn Ave."),
    ('g15-d165-policy', 15, 165, 'private_thought', "Never trade Ventnor or Penn Ave."),
    ('g2-d115-blocker', 2, 115, 'private_thought', "Keep Marvin blocking p4's yellows"),
    ('g2-d119-public', 2, 119, 'public_message', "Marvin controls access to a well-funded yellow monopoly."),
    ('g13-d251-solvency', 13, 251, 'reasoning', "That payment also keeps p4 solvent enough to cover Short Line rent to p2, which matters for how the game continues."),
    ('g5-d263-first-block', 5, 263, 'reasoning', "Selling all six houses would only raise $600."),
    ('g5-d258-carried', 5, 258, 'private_thought', "my total liquidatable cash + houses is $774 < $900"),
]

out = []
cache = {}
for sid, g, d, field, text in SPANS:
    if g not in cache:
        cache[g] = {}
        for line_no, l in enumerate(open(ROOT / gm[str(g)] / 'decisions.jsonl'), 1):
            x = json.loads(l)
            if x['phase'] == 'decision_resolved':
                cache[g][int(x['decision_id'].rsplit('-', 1)[1])] = (line_no, x)
    line_no, x = cache[g][d]
    att = len(x['attempts']) - 1
    if field == 'reasoning':
        val = x['attempts'][-1]['raw_response']['choices'][0]['message'].get('reasoning') or ''
        ch = 'provider-returned reasoning text (final attempt)'
    else:
        val = x['final_action'].get(field) or ''
        ch = {'private_thought': 'applied private note', 'public_message': 'public message'}[field]
    off = val.find(text)
    out.append({'id': sid, 'game': g, 'decision': d, 'decisions_jsonl_line': line_no, 'attempt': att,
                'player': x['player_name'], 'turn': x['turn_index'], 'channel': ch,
                'response_condition': x['attempts'][-1].get('response_condition'),
                'offset': off, 'exact_match': off >= 0,
                'field_sha256': hashlib.sha256(val.encode()).hexdigest(), 'span': text})
json.dump(out, sys.stdout, indent=1)
print()
