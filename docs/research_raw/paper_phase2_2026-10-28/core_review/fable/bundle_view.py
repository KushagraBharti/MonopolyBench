#!/usr/bin/env python3
"""Fable's reading aid: print one original decision bundle from the phase-1 review packets.

Usage: bundle_view.py GAME DEC [DEC ...] [--full] [--events-only]
  DEC may be a zero-based integer suffix (e.g. 112) or a display number with '#' (e.g. '#113').
This prints the original packet content (observation, legal menu, every attempt's channels,
applied action, canonical events). It performs no classification.
"""
import json, sys, os
ROOT = '/Users/kushagra/CS-Projects/MonopolyBench'
LEDGER = os.path.join(ROOT, 'docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl')

_ledger = None
def ledger():
    global _ledger
    if _ledger is None:
        _ledger = {}
        with open(LEDGER) as f:
            for line in f:
                r = json.loads(line)
                _ledger[(r['game'], int(r['decision_id'].rsplit('-', 1)[1]))] = r
    return _ledger

def load(game, dec):
    r = ledger()[(game, dec)]
    with open(os.path.join(ROOT, r['packet'])) as f:
        for i, line in enumerate(f, 1):
            if i == r['packet_line']:
                return json.loads(line), r
    raise KeyError

def money(x):
    return f"${x}" if x is not None else "?"

def fmt_props(props):
    out = []
    for p in props:
        if isinstance(p, dict):
            k = p.get('space_key') or p.get('key') or p.get('name') or str(p)
            flags = []
            if p.get('mortgaged'): flags.append('M')
            h = p.get('houses'); 
            if h: flags.append(f"h{h}")
            if p.get('hotel'): flags.append('HOTEL')
            out.append(k + ('[' + ','.join(flags) + ']' if flags else ''))
        else:
            out.append(str(p))
    return ', '.join(out)

def show(game, dec, full=False, events_only=False):
    rec, led = load(game, dec)
    ip = rec.get('initial_prompt', {})
    pl = ip.get('payload', {})
    gs = pl.get('game_state', {})
    ast = pl.get('action_state', {})
    you = gs.get('you', {})
    print('=' * 100)
    print(f"GAME {game} DEC {dec:06d} (#{dec+1})  id={rec['decision_id']}  player={rec.get('player_id')} model={rec.get('model')} turn={rec.get('turn_index')} type={rec.get('decision_type')}")
    print(f"packet={led['packet'].split('/')[-1]} line={led['packet_line']}")
    if not events_only:
        print('-- YOU:', json.dumps(you)[:1500] if full else json.dumps({k: v for k, v in you.items() if k not in ('properties',)})[:600])
        if 'properties' in you:
            print('   props:', fmt_props(you['properties']))
        for o in gs.get('others', []):
            print('-- OTHER:', json.dumps({k: v for k, v in o.items() if k != 'properties'})[:300])
            if 'properties' in o:
                print('   props:', fmt_props(o['properties']))
        print('-- BANK:', json.dumps(gs.get('bank'))[:300])
        print('-- META:', json.dumps(gs.get('metadata'))[:200])
        print('-- ACTION STATE:', json.dumps(ast)[:2500 if full else 1200])
        mem = gs.get('memory', {})
        for k, v in mem.items():
            s = json.dumps(v)
            print(f"-- MEMORY {k}: ({len(s)} chars)")
            if full or k in ('your_private_thoughts_last_10',):
                print(s[:6000])
            else:
                print(s[:2500])
        for a in rec.get('attempts', []):
            print(f"-- ATTEMPT {a.get('attempt_index_zero_based')} cond={a.get('response_condition')} outcome={a.get('outcome')} model={a.get('requested_model')} err={a.get('error_type')} verr={a.get('validation_errors')}")
            if a.get('prompt') and not a['prompt'].get('initial_prompt_ref'):
                print('   RETRY PROMPT:', json.dumps(a['prompt'])[:1500])
            ac = a.get('assistant_content')
            if ac: print('   assistant_content:', (ac if full else ac[:2500]))
            for tc in a.get('parsed_tool_calls') or []:
                print('   tool:', tc.get('name'), (tc.get('arguments') if full else str(tc.get('arguments'))[:3000]))
            rr = a.get('raw_response') or {}
            ch = (rr.get('choices') or [{}])[0] if isinstance(rr.get('choices'), list) and rr.get('choices') else {}
            msg = ch.get('message') or {}
            rs = msg.get('reasoning')
            if rs: print('   provider.reasoning:', (rs if full else str(rs)[:4000]))
            rd = msg.get('reasoning_details')
            if rd:
                txt = json.dumps(rd)
                print('   provider.reasoning_details:', (txt if full else txt[:3000]))
            ref = msg.get('refusal')
            if ref: print('   provider.refusal:', str(ref)[:1500])
            if msg.get('content') and msg.get('content') != ac:
                print('   message.content:', str(msg.get('content'))[:2500])
        aa = rec.get('applied_action_record', {}).get('action', {})
        res = rec.get('resolution', {})
        print(f"-- APPLIED: {aa.get('action')} args={json.dumps(aa.get('args'))}")
        print(f"   public_message: {aa.get('public_message')!r}")
        print(f"   private_thought: {aa.get('private_thought')!r}")
        print(f"   fallback_used={res.get('fallback_used')} fallback_reason={res.get('fallback_reason')} retry_used={res.get('retry_used')} events {res.get('emitted_event_seq_start')}-{res.get('emitted_event_seq_end')}")
    print('-- EVENTS:')
    for e in rec.get('canonical_event_segment', []):
        print(f"   {e['seq']:>5} t{e.get('turn_index')} {e['type']:<28} {e.get('actor',{}).get('player_id') or 'ENGINE':>6} {json.dumps(e.get('payload'))[:400]}")

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    full = '--full' in sys.argv
    ev = '--events-only' in sys.argv
    game = int(args[0])
    for d in args[1:]:
        dec = int(d[1:]) - 1 if d.startswith('#') else int(d)
        show(game, dec, full=full, events_only=ev)
