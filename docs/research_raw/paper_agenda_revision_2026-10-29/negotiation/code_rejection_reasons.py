"""Retain the manually read 74-record stated-reason coding with exact spans.

This is an annotation export, NOT an automatic text classifier. Each tuple was
assigned after reading both complete fields. Matching text checks transcription.
Codes concern stated considerations; they do not certify factual correctness,
coherent intent, causal reliance, or optimality. Provider summaries are excluded.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFINITIONS = {
    "D": "Explicit rival completion, development, financing, survival, or estate-denial consideration.",
    "C": "Explicit own price, liquidity, affordability, reserve or financing consideration.",
    "R": "Explicit retention of own holdings/income or own portfolio priority beyond a bare decline.",
    "T": "Explicit timing disadvantage or a stated future condition for reconsideration.",
    "F": "Speaker's claimed buyer/seller role contradicts the recorded offer and current holdings.",
    "N": "No applicable explicit consideration in the two observed fields.",
}
# game, decision, code: (channel, exact supporting substring).
CODING = [
 (1,207,{'D':('private','NY completes p1 orange'),'C':('private','cannot build and stay solvent'),'R':('private','Keep both blockers.')}),
 (1,210,{'D':('private','would allow p2 (who has $808 cash) to immediately build'),'T':('private','cannot build on Red ($150/house) until my turn.')}),
 (1,212,{'D':('private','Giving p2 the Pink monopoly on their turn'),'C':('private','only have $598 cash'),'T':('private','on their turn')}),
 (1,223,{'D':('private','NY completes p1 orange'),'C':('private','cannot build dark blue')}),
 (1,225,{'D':('private','NY completes p1 orange'),'C':('private',"I still can't build dark blue")} ),
 (1,232,{'D':('private','NY completes p1 orange'),'C':('private',"still can't build dark blue")} ),
 (1,243,{'D':('private','NY completes p1 orange'),'C':('private',"can't build dark blue")} ),
 (1,255,{'D':('private','giving p2 the Pink monopoly plus $400'),'T':('private','during their turn')}),
 (1,261,{'D':('private','NY completes p1 orange'),'C':('private',"can't build dark blue")} ),
 (1,265,{'D':('private','p1 gets dark blue'),'C':('private',"Can't build orange"),'R':('private','This cash and the PP $175 buffer belong to yellow and survival')}),
 (1,267,{'D':('private','p1 still gets dark blue'),'C':('private',"Can't build")} ),
 (1,269,{'D':('private','p1 would get dark blue'),'C':('private',"Orange can't be built safely.")} ),
 (1,271,{'D':('private','p1 gets dark blue'),'C':('private','leaving me unable to build orange'),'R':('private','I already own yellow, the better set')}),
 (1,294,{'D':('private','would bail them out'),'T':('private',"it is p2's turn.")} ),
 (1,320,{'D':('private','would only bail them out and create a threat.')}),
 (1,360,{'D':('private','Giving p2 two monopolies'),'R':('private','my commanding lead')}),
 (1,362,{'D':('private','would create a major threat')}),
 (1,364,{'D':('private','give p2 a monopoly and $700 to build')}),
 (1,391,{'D':('private','enough money to rebuild houses on the Pink monopoly'),'C':('public',"not looking to spend $700")} ),
 (1,393,{'D':('private','rebuild houses on Pink and survive longer')}),
 (1,395,{'D':('private','rebuild houses on Pink and extend their survival')}),
 (1,434,{'C':('private','no reason to give up three railroads and $300'),'R':('public',"I'm keeping the railroads.")} ),
 (2,166,{'D':('private','Giving p1 the Orange monopoly and $350 cash'),'T':('private','on their turn')}),
 (2,220,{'D':('private','extend their survival or let them rebuild their Yellow monopoly'),'R':('private','I already own all four Railroads')}),
 (2,222,{'D':('private','Denying p1 cash keeps them on the brink of bankruptcy')}),
 (3,180,{'D':('private','giving p2 $300 cash right before p2 crosses Light Blue or builds on Pink'),'C':('private','leave me without liquidity'),'T':('public','before crossing the Light Blues')}),
 (3,182,{'D':('private','allow p2 to immediately build more houses on Pink'),'C':('private','drain my cash buffer down to $161'),'T':('private','on this turn.')}),
 (3,184,{'D':('private','giving p2 enough cash to either build more houses on Pink'),'C':('private',"wouldn't cover p4's $400-$450 Light Blue rents"),'T':('public','After I pass Connecticut Avenue next turn, we can talk')}),
 (3,418,{'D':('private','lets p4 hotel light blues'),'C':('public','Not paying $500'),'R':('private','Keep cash and GOOJF.')}),
 (3,420,{'D':('private','lets p4 survive a $700 Virginia hit'),'C':('public',"two mortgaged oranges I can't build on")} ),
 (3,506,{'D':('private','no reason to give p2 $400 cash'),'R':('private','build hotels and unmortgage my own monopolies')}),
 (4,323,{'D':('private','would fund jail camping'),'C':('public','$450 for a mortgaged Boardwalk')}),
 (4,329,{'D':('private','$250 gives them $310 survival cash'),'C':('public','$250 for a mortgaged Boardwalk')}),
 (4,331,{'D':('private','$175 gives them $235'),'C':('public','$175 for a mortgaged Boardwalk')}),
 (4,333,{'D':('private','enough to survive Med ($160), luxury tax, and stall.'), 'C':('public',"I'm not paying for a mortgaged Boardwalk.")} ),
 (4,345,{'D':('private','the cash only cushions income tax and stalling'),'C':('public','$150 for a mortgaged Boardwalk')}),
 (5,244,{'D':('private',"completes p1's dangerous orange monopoly"),'R':('private','Keep 3/3/3 greens and orange blockade')}),
 (6,193,{'D':('private',"$300 funds p4's recovery"),'R':('public','My current properties are enough to manage.')}),
 (9,129,{'D':('private','would give p4 two of the three Orange properties'),'R':('private','my key Orange blocker and trade leverage')}),
 (9,137,{'D':('private','would give them the complete Orange monopoly'),'R':('public',"I'm holding onto Tennessee Avenue.")} ),
 (11,258,{'D':('private','Giving mortgaged PA completes their greens'),'R':('private','the kill I already have')}),
 (11,318,{'D':('public','hands you the cash to survive my hotels'),'C':('private',"I can't unmortgage (~$506) or build.")} ),
 (12,156,{'D':('private','directly fund additional houses on Red'),'T':('private','cannot even build on Browns until my turn'),'R':('private','preserve my $1,081 cash for stronger monopolies')}),
 (12,173,{'D':('private','build another house on their Red monopoly or compete with me')}),
 (13,102,{'D':('private','handing them a second monopoly is how I lose'),'R':('private','Keep Park Place')}),
 (13,121,{'D':('public','buys you two more orange houses'),'C':('private','$302 stays liquid.'),'T':('private','Reopen only on my turn at ≤$115')}),
 (13,174,{'D':('private','heavily develop their Yellow monopoly'),'C':('private','drain my cash down to $254'),'R':('private','focus on securing unowned Illinois Avenue')}),
 (13,303,{'D':('public',"I'm not handing over the dark blues plus $800"),'C':('public','$800 for three mortgaged properties')}),
 (13,347,{'D':('public','to keep you in the game.'),'C':('public',"I'm not paying $800")} ),
 (14,101,{'C':('private',"I cannot build ($400 for 1 house each)"),'T':('private','Reopen later near $400 or if p4 is cash-squeezed.')}),
 (15,106,{'C':('public','$120 is still a discount'),'R':('public',"I'll hold Baltic."),'F':('private','Cash stays $8 until someone pays up.')}),
 (15,108,{'C':('public','I need the cash more than a brown set right now.'),'T':('private','Revisit only if I clear the oranges with cash to spare.')}),
 (15,110,{'D':('private',"String p3 so they don't sell Baltic to p4 and fund a dark-blue house."),'C':('private',"which I can't afford."),'T':('private','Revisit only after I clear oranges with surplus cash.')}),
 (15,169,{'D':('public',"I'm not handing you a yellow monopoly"),'C':('private',"can't even even-build one house each")} ),
 (15,173,{'D':('private','Giving Ventnor completes p4 yellows.'),'C':('private','only $333; 1 house each on greens costs $600')}),
 (15,175,{'D':('private','enough for 2 houses each on yellows'),'C':('private','Cannot reach 2 green houses.')}),
 (15,223,{'D':('private','ensures p4 has zero monopolies and zero win condition.')}),
 (15,225,{'D':('private','ensures p4 has zero monopolies and no ability to build houses.')}),
 (15,227,{'D':('private','Refusing to give p4 any monopoly guarantees my win.')}),
 (15,265,{'D':('private','would only help them survive longer.')}),
 (15,267,{'D':('private','would only prolong the game and give them a chance to build.')}),
 (15,269,{'D':('private','would only extend their survival and let them build houses.')}),
 (16,217,{'D':('private','Giving PP completes dark blue for p2'),'C':('private','$543 cannot fund 3 houses ($900) and still survive')}),
 (16,443,{'D':('public','would let you unmortgage New York Avenue and build up Orange')}),
 (17,186,{'C':('public','$260 stands'),'R':('private','I keep the pair'),'F':('public',"Oriental’s mortgage is your problem after the trade")} ),
 (17,248,{'D':('private',"avoid funding p4's light-blue development."),'C':('private','Preserve $134 reserve')}),
 (17,250,{'D':('private',"strengthens p4's liquidity"),'C':('public',"I don't have the spare cash to develop greens.")} ),
 (18,255,{'D':('private',"Pacific completes p4's greens"),'C':('private','Yellow monopoly is useless without build cash'),'R':('private','2/2 Boardwalk is the plan.')}),
 (18,438,{'R':('public',"I'm comfortable with my board as it is.")} ),
 (18,440,{'N':('public','Still a pass. Your roll.')}),
 (18,442,{'N':('public',"That offer's off the table now. Things have changed.")} ),
 (18,457,{'C':('public','Pass at $350. My $225 offer stands')}),
 (18,461,{'C':('public',"I'm not raising my offer, so it stays at $225.")} ),
 (20,278,{'R':('public','New York stays with me. Orange isn\'t for sale.')}),
]


def main():
    offers = json.loads((HERE / 'offers.json').read_text())
    population = {(r['game'], r['decision']): r for r in offers
                  if r['accept_available'] and r['recipient_new_groups'] and r['response'] == 'reject_trade'}
    assert len(CODING) == len(population) == 74
    assert {(g, d) for g, d, _ in CODING} == set(population)
    result = []
    for game, decision, codes in CODING:
        row = population[game, decision]
        evidence = []
        for code, (channel, quote) in codes.items():
            field = 'public_message' if channel == 'public' else 'applied_private_note'
            assert quote in row[field], (game, decision, code, quote)
            evidence.append({'code': code, 'channel': channel, 'quote': quote,
                             'start': row[field].index(quote), 'end': row[field].index(quote) + len(quote)})
        result.append({'game': game, 'decision': decision, 'decision_id': row['decision_id'],
                       'recipient_model': row['recipient_model'], 'completion_cell': row['completion_cell'],
                       'source_run': row['source_run'], 'decision_source_line': row['decision_source_line'],
                       'response_condition': row['response_condition'], 'fallback_used': row['fallback_used'],
                       'author_model': row['author_model'], 'recipient': row['recipient'], 'author': row['author'],
                       'offer': row['offer'], 'request': row['request'],
                       'public_message': row['public_message'], 'applied_private_note': row['applied_private_note'],
                       'recipient_cash_before': row['recipient_cash_before'],
                       'public_available': bool(row['public_message']), 'private_available': bool(row['applied_private_note']),
                       'codes': list(codes), 'evidence': evidence})
    counts = Counter(e['code'] for row in result for e in row['evidence'])
    summary = {'population': 'All acceptance-legal recipient-completing offers followed by direct reject_trade',
               'rows': len(result), 'definitions': DEFINITIONS, 'counts_nonexclusive': dict(counts),
               'private_available': sum(r['private_available'] for r in result),
               'public_available': sum(r['public_available'] for r in result),
               'annotation': 'One model-assisted manual pass of full applied public/private fields; source spans verified. Not independent gold-standard labels.',
               'limits': 'Recorded stated reasons, not verified fact, latent motive, utility or causal influence. Provider summaries not coded. F requires mechanical role contradiction.',
               'offers_sha256': hashlib.sha256((HERE / 'offers.json').read_bytes()).hexdigest(),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'rows_data': result}
    (HERE / 'rejection_reason_coding.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows_data'}, indent=2))


if __name__ == '__main__':
    main()
