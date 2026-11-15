import json,glob,sys
Q=[
 (99,0,'LIQ_NOTE',"Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should not raise enough cash."),
 (1,170,'LLM_PUBLIC_MESSAGE',"No thanks, p2. I'm not giving up a complete Pink monopoly without getting a completed monopoly in return."),
 (2,122,'LLM_PUBLIC_MESSAGE',"p1, sit on Marvin. Selling it to p4 gives them a second monopoly on top of light blue — the only stack that can actually finish you. I'm not raising."),
 (2,119,'LLM_PUBLIC_MESSAGE',"Marvin controls access to a well-funded yellow monopoly. $450 buys that leverage; $200 doesn't."),
 (2,124,'LLM_PUBLIC_MESSAGE',"Marvin completes your yellows. $650 buys it; $325 doesn't compensate for handing you that monopoly."),
 (15,166,'LLM_PUBLIC_MESSAGE',"GPT now owns 2 reds, 2 greens and 2 yellows and has $1000+ in cash. He's the one to watch, so let's not hand him the last piece of any set."),
 (15,169,'LLM_PUBLIC_MESSAGE',"No. I'm not handing you a yellow monopoly so you can build it this turn. Ventnor stays mine."),
 (15,169,'LLM_PRIVATE_THOUGHT_SPAN',"Trade gives p4 Atlantic+Ventnor+Marvin and ~$830 plus mortgage capacity to drop 5+ yellow houses ($150) immediately, then they roll again on doubles. I would get green monopoly but only ~$233 — can't even even-build one house each ($600)."),
 (12,190,'LLM_PRIVATE_THOUGHT',"Three houses sell for $225; Baltic and both light blues mortgage for $130. With $53 cash, maximum liquidity is $408, below $500 owed. No legal liquidation can save me."),
 (17,234,'LLM_PRIVATE_THOUGHT',"I owe $550 rent on Tennessee Avenue, and my total liquidatable value is only $530 (5 Dark Blue houses at $100 each plus $30 for mortgaging Baltic Avenue). Since I cannot raise $550, I must declare bankruptcy."),
 (1,476,'LLM_PRIVATE_THOUGHT',"Short $149 on RR $200. Only legal raise is Marvin 1h ($75) → cash ~$126, still ~$74 short. Must sell before yellows can be mortgaged. Next prompt: mortgage one yellow (Atlantic/Ventnor $130 or Marvin $140) to clear the debt. Do not bankrupt — 1v1, p3 inherits the win. After pay, cash will be thin; no rebuild, no unmortgage. Jail cards stay."),
 (20,327,'LLM_PRIVATE_THOUGHT',"Full liquidation should yield $1,414 including cash and all mortgages, enough for $1,400 rent by $14. Must sell all development and mortgage everything; survive rather than concede. If hotel sales leave four houses, sell those next evenly."),
 (20,336,'LLM_PRIVATE_THOUGHT',"Final $30 mortgage covers $16 shortfall, leaving $14 after rent. Survive; rebuild cash through GO and avoid greens."),
]
def run(g):
    base='railway-research-12-games-2026-10-25' if g<=12 else 'railway-research-8-games-2026-10-26'
    return glob.glob(f'/Users/kushagra/CS-Projects/MonopolyBench/saved_games/{base}/game-{g:02d}-*/run')[0]
res=[]
for g,d,t,txt in Q:
    found=False; who=None
    if t=='LIQ_NOTE':
        u=json.load(open(glob.glob(run(20)+'/prompts/*dec-000327_user.json')[0]))
        found = u['action_state']['scenario']['note']==txt; who='engine'
        res.append(dict(game=20,decision=327,type=t,exact=found,player=who,text=txt)); print('G20 d327 scenario note','EXACT' if found else 'NOT FOUND'); continue
    span = t.endswith('_SPAN'); t=t.replace('_SPAN','')
    for l in open(run(g)+'/events.jsonl'):
        e=json.loads(l)
        if e['type']!=t: continue
        p=e['payload']
        if not (p.get('decision_id') or '').endswith(f'{d:06d}'): continue
        val=p.get('message') if t=='LLM_PUBLIC_MESSAGE' else (p.get('thought') or p.get('text') or p.get('private_thought'))
        if (val==txt) or (span and val and txt in val): found=True; who=p.get('player_id')
        else: print('MISMATCH',g,d,t,'\n  src:',val,'\n  q  :',txt)
    res.append(dict(game=g,decision=d,type=t,exact=found,player=who,text=txt))
    print(g,d,t,'EXACT' if found else 'NOT FOUND',who)
json.dump(res,open(sys.argv[1],'w'),indent=1,ensure_ascii=False)
