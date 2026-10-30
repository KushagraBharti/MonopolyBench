#!/usr/bin/env python3
"""Fable's reading aid: one line per decision: actor, type, applied action, public msg head, and money/deed events."""
import json, sys, os
ROOT='/Users/kushagra/CS-Projects/MonopolyBench'
LEDGER=os.path.join(ROOT,'docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl')
game=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); full='--msg' in sys.argv
led=[json.loads(l) for l in open(LEDGER)]
led=[r for r in led if r['game']==game and a<=int(r['decision_id'].rsplit('-',1)[1])<=b]
bypk={}
for r in led: bypk.setdefault(r['packet'],[]).append(r)
recs={}
for pk,rs in bypk.items():
    want={r['packet_line']:r for r in rs}
    with open(os.path.join(ROOT,pk)) as f:
        for i,line in enumerate(f,1):
            if i in want: recs[int(want[i]['decision_id'].rsplit('-',1)[1])]=json.loads(line)
for d in sorted(recs):
    rec=recs[d]; aa=rec['applied_action_record']['action']; res=rec.get('resolution',{})
    you=rec['initial_prompt']['payload']['game_state']['you']
    evs=[]
    for e in rec['canonical_event_segment']:
        t=e['type']; p=e.get('payload',{})
        if t=='CASH_CHANGED': evs.append(f"{p.get('player_id')}{p.get('delta'):+}({p.get('reason')})")
        elif t=='PROPERTY_TRANSFERRED': evs.append(f"deed{p.get('space_index')}:{p.get('from_player_id')}->{p.get('to_player_id')}{'M' if p.get('mortgaged') else ''}")
        elif t in ('TRADE_PROPOSED','TRADE_COUNTERED','TRADE_ACCEPTED','TRADE_REJECTED'):
            evs.append(f"{t}:{json.dumps(p.get('offer'))}for{json.dumps(p.get('request'))}" if p.get('offer') else t)
        elif t in ('HOUSE_BUILT','HOUSE_SOLD','HOTEL_BUILT','HOTEL_SOLD','PROPERTY_MORTGAGED','PROPERTY_UNMORTGAGED','AUCTION_BID_PLACED','AUCTION_ENDED','PLAYER_BANKRUPT','GAME_ENDED','DICE_ROLLED','PLAYER_MOVED','RENT_PAID','CARD_DRAWN','PROPERTY_PURCHASED','AUCTION_PLAYER_DROPPED','AUCTION_STARTED','JAIL_FINE_PAID','PLAYER_JAILED','PLAYER_LEFT_JAIL','TAX_PAID'):
            evs.append(f"{t}:{json.dumps(p)[:90]}")
        elif t not in ('LLM_DECISION_REQUESTED','LLM_DECISION_RESPONSE','LLM_PUBLIC_MESSAGE','LLM_PRIVATE_THOUGHT','TURN_STARTED','TURN_ENDED'):
            evs.append(f"{t}:{json.dumps(p)[:80]}")
    flags=[]
    if res.get('fallback_used'): flags.append('FALLBACK')
    if res.get('retry_used'): flags.append('retry')
    conds=[a_.get('response_condition')+':'+a_.get('outcome') for a_ in rec.get('attempts',[])]
    msg=aa.get('public_message') or ''
    print(f"d{d:03d} t{rec['turn_index']} {rec['player_id']}({rec['model'].split('/')[-1][:10]}) cash={you.get('cash')} {rec['decision_type'][:22]} -> {aa.get('action')} {json.dumps(aa.get('args'))[:120]} [{';'.join(conds)}{' '+' '.join(flags) if flags else ''}]")
    print(f"      msg: {msg if full else msg[:140]!r}")
    if evs: print('      ev: '+' | '.join(evs))
