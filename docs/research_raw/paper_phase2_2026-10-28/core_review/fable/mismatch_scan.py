#!/usr/bin/env python3
"""Fable's mechanical screen: for each decision in a game, compare the tool named in the applied attempt's assistant_content JSON
(if any) with the applied action; also flag public messages that look like refusals on accept_trade and claims of building on end_turn.
Screen hits are candidates for reading, never labels."""
import json, sys, os, re, importlib.util
spec=importlib.util.spec_from_file_location('bv',os.path.join(os.path.dirname(os.path.abspath(__file__)),'bundle_view.py')); bv=importlib.util.module_from_spec(spec); spec.loader.exec_module(bv)
game=int(sys.argv[1])
L=bv.ledger(); rows=sorted(d for (g,d) in L if g==game)
def content_tool(ac):
    if not ac: return None
    m=re.search(r'"name"\s*:\s*"([a-z_]+)"', ac)
    return m.group(1) if m else None
hits=[]
for d in rows:
    rec,_=bv.load(game,d)
    aa=rec['applied_action_record']['action']; applied=aa['action']
    atts=rec.get('attempts',[])
    # applied attempt = last valid
    valid=[a for a in atts if a.get('outcome')=='valid']
    if not valid: continue
    a=valid[-1]
    ct=content_tool(a.get('assistant_content'))
    msg=(aa.get('public_message') or '')
    flag=[]
    if ct and ct!=applied: flag.append(f'content={ct}')
    if applied=='accept_trade' and re.match(r"\s*(no\b|not\b|pass\b|reject)", msg, re.I): flag.append('accept-with-No')
    if applied=='end_turn' and re.search(r'houses? (are|is) up|built|building|hotel', msg, re.I) and not re.search(r"not|no |won't|isn't", msg, re.I): flag.append('end_turn-with-build-claim')
    if applied in ('pay_jail_fine',) and re.search(r'roll|not paying', msg, re.I): flag.append('pay-with-roll-msg')
    if applied in ('roll_for_doubles',) and re.search(r'\bpay(ing)?\b', msg, re.I) and not re.search(r'not pay', msg, re.I): flag.append('roll-with-pay-msg')
    if applied=='start_auction' and re.search(r"mine|i'll take|buy", msg, re.I) and not re.search(r"auction|pass|not", msg, re.I): flag.append('auction-with-buy-msg')
    if flag: hits.append((d,rec['player_id'],rec['model'].split('/')[-1],applied,';'.join(flag),msg[:90]))
for h in hits: print(h)
print('total decisions',len(rows),'screen hits',len(hits))
