#!/usr/bin/env python3
"""Fable's arithmetic aid: upper bound on cash raisable at a decision by selling ALL buildings then mortgaging ALL unmortgaged deeds.
Engine facts used (read from engine notes/observed events): mortgage value = price//2; house sells for house_cost//2; a hotel sells
as 5 x house_cost//2 (downgrade to 4 houses then sell them); a deed can be mortgaged once no building remains in its colour group.
This is an UPPER BOUND on immediately raisable cash. It does not certify a legal ordering under bank-house availability for hotel
downgrades (a hotel downgrade needs 4 bank houses), nor that any sequence is strategically sensible.
Usage: liq.py GAME DEC [DEBT]
"""
import json, sys, os, importlib.util
ROOT='/Users/kushagra/CS-Projects/MonopolyBench'
board=json.load(open(os.path.join(ROOT,'contracts/data/board.json')))
sp={s['name'].upper().replace(' ','_').replace('.','').replace('&','').replace('__','_'):s for s in board['spaces'] if 'price' in s}
# build key map by normalized key used in game (e.g., B_O_RAILROAD, ST_JAMES_PLACE)
def norm(n):
    n=n.upper().replace('.','').replace('&','O').replace(' ','_')
    return n
keymap={}
for s in board['spaces']:
    if 'price' not in s: continue
    k=s['name'].upper().replace('.','').replace(' ','_').replace('&','_')
    k=k.replace('B__O','B_O')
    keymap[k]=s
hc=board['house_cost_by_group']
spec=importlib.util.spec_from_file_location('bv',os.path.join(os.path.dirname(os.path.abspath(__file__)),'bundle_view.py')); bv=importlib.util.module_from_spec(spec); spec.loader.exec_module(bv)
def compute(game,dec,verbose=True):
    rec,led=bv.load(game,dec)
    you=rec['initial_prompt']['payload']['game_state']['you']
    cash=you['cash']; bld=0; mort=0; lines=[]
    for p in you['holdings']['owned']:
        k=p['space_key']; s=keymap.get(k)
        if s is None:
            # try fuzzy
            cands=[kk for kk in keymap if kk.replace('_','') in k.replace('_','') or k.replace('_','') in kk.replace('_','')]
            s=keymap[cands[0]] if cands else None
        if s is None: lines.append(f'  !! unknown key {k}'); continue
        g=s.get('group'); cost=hc.get(g,0) if g in hc else 0
        b=0
        if p.get('hotel'): b=5*(cost//2)
        elif p.get('houses'): b=p['houses']*(cost//2)
        m=0 if p.get('mortgaged') else s['price']//2
        bld+=b; mort+=m
        lines.append(f"  {k:<24} price={s['price']:>4} houses={p.get('houses')} hotel={p.get('hotel')} mortgaged={p.get('mortgaged')} -> buildings {b:>4} mortgage {m:>4}")
    total=cash+bld+mort
    if verbose:
        print(f"GAME {game} DEC {dec:06d} {rec['player_id']} {rec['model']} turn {rec['turn_index']} type={rec['decision_type']}")
        print('\n'.join(lines))
        print(f"  cash {cash} + buildings {bld} + mortgages {mort} = MAX {total}")
    return cash,bld,mort,total,rec
if __name__=='__main__':
    g=int(sys.argv[1]); d=int(sys.argv[2]); debt=int(sys.argv[3]) if len(sys.argv)>3 else None
    cash,bld,mort,total,rec=compute(g,d)
    if debt is not None: print(f"  debt {debt}: {'PAYABLE by upper bound (surplus '+str(total-debt)+')' if total>=debt else 'NOT payable (short '+str(debt-total)+')'}")
