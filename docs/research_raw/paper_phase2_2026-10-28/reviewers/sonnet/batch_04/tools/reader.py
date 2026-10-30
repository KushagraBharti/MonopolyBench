#!/usr/bin/env python3
"""Compact reader for MonopolyBench batch_01 (reviewer: claude-sonnet-5-5, effort xhigh).

Renders each assigned decision as bounded plain text.  It only removes EXACT duplicate
representations (system prompt, repeated state, bookkeeping events that equal the applied
action, repeated refusal text) and states each removal in the output.  All distinct text
(public message, private note, tool args, provider reasoning/summary, content, refusal,
validation errors, events) is printed in full.  It makes no labels.

Usage:  reader.py write-chunks OUTDIR [max_chars]      # paginate to chunk files
        reader.py show START END                       # print global indexes [START,END)
"""
import json, os, sys, re, collections

ROOT = '/Users/kushagra/CS-Projects/MonopolyBench'
BATCH = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAN = ROOT + f'/docs/research_raw/paper_phase2_2026-10-28/batches/{BATCH}.json'
BOARD = json.load(open(ROOT + '/contracts/data/board.json'))
SPACES = BOARD['spaces']
IDX2NAME = {s['index']: s['name'] for s in SPACES}
GROUP_ABBR = {'BROWN': 'BR', 'LIGHT_BLUE': 'LB', 'PINK': 'PK', 'ORANGE': 'OR', 'RED': 'RD', 'YELLOW': 'YL',
              'GREEN': 'GR', 'DARK_BLUE': 'DB', 'RAILROAD': 'RR', 'UTILITY': 'UT'}


def key_of(name):
    return re.sub(r'[^A-Z0-9]+', '_', name.upper()).strip('_')


# map engine space keys -> board names / groups
KEY2NAME, KEY2GROUP, GROUPSIZE = {}, {}, collections.Counter()
for s in SPACES:
    if s.get('group'):
        k = key_of(s['name'])
        KEY2NAME[k] = s['name']
        KEY2GROUP[k] = s['group']
        GROUPSIZE[s['group']] += 1
# a few engine keys differ from key_of(name)
EXTRA = {'B_O_RAILROAD': 'B&O Railroad', 'MARVIN_GARDENS': 'Marvin Gardens'}
for k, v in EXTRA.items():
    if k not in KEY2NAME:
        for s in SPACES:
            if s['name'].lower().startswith(('b. & o', 'b&o', 'b & o')) and k == 'B_O_RAILROAD':
                KEY2NAME[k] = s['name']; KEY2GROUP[k] = s['group']
IDX2KEY = {s['index']: key_of(s['name']) for s in SPACES if s.get('group')}
for i, k in list(IDX2KEY.items()):
    if k not in KEY2GROUP:
        pass


def sn(k):
    """short readable name for engine space key"""
    if k is None:
        return 'None'
    n = KEY2NAME.get(k) or k
    n = n.replace(' Avenue', ' Ave').replace(' Place', ' Pl').replace(' Railroad', ' RR').replace('Company', 'Co').replace(' Works', ' Wks')
    return n


def sidx(i):
    k = IDX2KEY.get(i)
    return sn(k) if k else IDX2NAME.get(i, f'#{i}')


def load_units():
    m = json.load(open(ROOT + '/' + MAN.split(ROOT + '/')[1]))
    cache, out = {}, []
    for u in m['units']:
        p = u['packet']
        if p not in cache:
            cache[p] = open(ROOT + '/' + p).readlines()
        out.append((u, json.loads(cache[p][u['packet_line'] - 1])))
    return out


MODEL_SHORT = {'anthropic/claude-opus-5.5': 'Opus', 'openai/gpt-6.1-sol': 'Sol', 'google/gemini-4-argon': 'Argon',
               'x-ai/grok-4.7': 'Grok'}


def j(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def compress_counting(text):
    """Replace long exactly-consecutive integer enumerations ('0.  1.  2. ...') with a verified marker. Other text untouched."""
    import re as _re
    pat = _re.compile(r'(?:\d+\.\s+){40,}\d*\.?')
    def rep(m):
        seg = m.group(0)
        nums = [int(x) for x in _re.findall(r'(\d+)\.', seg)]
        if len(nums) >= 40 and all(nums[i + 1] == nums[i] + 1 for i in range(len(nums) - 1)):
            return f'[COUNTING-RUN verified consecutive integers {nums[0]}..{nums[-1]} ({len(nums)} items) omitted as an exact regular enumeration]'
        return seg
    return pat.sub(rep, text)


def prop_status(o):
    if o.get('mortgaged'):
        return 'm'
    if o.get('hotel'):
        return 'H'
    return str(o.get('houses', 0))


def player_state(p):
    owned = {o['space_key']: prop_status(o) for o in p['holdings']['owned']}
    return {'cash': p['cash'], 'pos': p['position'], 'jail': (p['in_jail'], p['jail_turns']),
            'cards': p['get_out_of_jail_cards'], 'bk': p['bankrupt'], 'own': owned,
            'mort_list': sorted(x['space_key'] for x in p['holdings']['mortgaged'])}


def groups_str(own):
    cnt = collections.Counter(KEY2GROUP.get(k, '?') for k in own)
    parts = []
    for g, c in sorted(cnt.items()):
        t = GROUPSIZE.get(g, '?')
        parts.append(f'{GROUP_ABBR.get(g, g)}{c}/{t}' + ('*' if c == t else ''))
    return ' '.join(parts)


def own_str(own):
    return ', '.join(f'{sn(k)}[{v}]' for k, v in own.items())


def global_state(gs):
    st = {}
    me = gs['you']
    st[me['player_id']] = player_state(me)
    for o in gs['others']:
        st[o['player_id']] = player_state(o)
    return st


def state_full(st, bank):
    lines = []
    for pid in sorted(st):
        s = st[pid]
        lines.append(f"  {pid}: ${s['cash']} @{s['pos']}" + (f" JAIL{s['jail'][1]}" if s['jail'][0] else '') +
                     (f" cards={s['cards']}" if s['cards'] else '') + (' BANKRUPT' if s['bk'] else '') +
                     f" | {own_str(s['own'])} | grp: {groups_str(s['own'])}")
    lines.append(f"  bank: houses={bank['houses_remaining']} hotels={bank['hotels_remaining']} unowned={len(bank['unowned_space_keys'])}")
    return '\n'.join(lines)


def state_diff(prev, st, pb, bank):
    lines = []
    for pid in sorted(st):
        a, b = prev.get(pid), st[pid]
        if a == b:
            continue
        ch = []
        if a['cash'] != b['cash']:
            ch.append(f"cash {a['cash']}->{b['cash']}")
        if a['pos'] != b['pos']:
            ch.append(f"pos {a['pos']}->{b['pos']}")
        if a['jail'] != b['jail']:
            ch.append(f"jail {a['jail']}->{b['jail']}")
        if a['cards'] != b['cards']:
            ch.append(f"cards {a['cards']}->{b['cards']}")
        if a['bk'] != b['bk']:
            ch.append(f"bankrupt {a['bk']}->{b['bk']}")
        for k in b['own']:
            if k not in a['own']:
                ch.append(f"+{sn(k)}[{b['own'][k]}]")
            elif a['own'][k] != b['own'][k]:
                ch.append(f"{sn(k)}[{a['own'][k]}->{b['own'][k]}]")
        for k in a['own']:
            if k not in b['own']:
                ch.append(f"-{sn(k)}")
        if a['own'].keys() != b['own'].keys():
            ch.append('grp: ' + groups_str(b['own']))
        lines.append(f'  {pid}: ' + '; '.join(ch))
    if (pb['houses_remaining'], pb['hotels_remaining']) != (bank['houses_remaining'], bank['hotels_remaining']):
        lines.append(f"  bank houses {pb['houses_remaining']}->{bank['houses_remaining']} hotels {pb['hotels_remaining']}->{bank['hotels_remaining']}")
    return '\n'.join(lines) if lines else '  (no change vs previous decision prompt)'


def tr_side(d):
    parts = []
    if d.get('cash'):
        parts.append(f"${d['cash']}")
    if d.get('get_out_of_jail_cards'):
        parts.append(f"{d['get_out_of_jail_cards']}xJailCard")
    for p in d.get('properties', []):
        parts.append(sn(p))
    return '+'.join(parts) if parts else 'nothing'


def render_scenario(a):
    dt = a['decision_type']
    sc = a['scenario']
    if dt == 'TRADE_RESPONSE_DECISION':
        co = sc['current_offer']
        ia = co['if_you_accept']
        s = (f"offer from {co['from_player_id']} (cp={sc['counterparty_player_id']}) ex={sc['exchange_index']}/{sc['max_exchanges']}: "
             f"you_give[{tr_side(ia['you_give'])}] you_receive[{tr_side(ia['you_receive'])}]")
        if sc.get('history'):
            s += ' HISTORY=' + j(sc['history'])
        extra = {k: v for k, v in sc.items() if k not in ('counterparty_player_id', 'current_offer', 'exchange_index', 'history', 'max_exchanges')}
        if extra:
            s += ' EXTRA=' + j(extra)
        return s
    if dt == 'POST_TURN_ACTION_DECISION':
        o = sc.get('options', {})
        s = ''
        for k in ('buildable_space_keys', 'sellable_building_space_keys', 'mortgageable_space_keys', 'unmortgageable_space_keys'):
            s += f"{k.replace('_space_keys', '')}=[{', '.join(sn(x) for x in o.get(k, []))}] "
        s += f"trade_with={o.get('can_trade_with')} max_ex={o.get('max_trade_exchanges')}"
        extra = {k: v for k, v in o.items() if k not in ('buildable_space_keys', 'sellable_building_space_keys', 'mortgageable_space_keys', 'unmortgageable_space_keys', 'can_trade_with', 'max_trade_exchanges')}
        if extra:
            s += ' OPT_EXTRA=' + j(extra)
        extra2 = {k: v for k, v in sc.items() if k not in ('note', 'options')}
        if extra2:
            s += ' SC_EXTRA=' + j(extra2)
        return s
    if dt == 'LIQUIDATION_DECISION':
        o = sc.get('options', {})
        s = (f"owed ${sc.get('owed_amount')} to {sc.get('owed_to_player_id')} reason={sc.get('reason')} shortfall=${sc.get('shortfall')} "
             f"mortgageable=[{', '.join(sn(x) for x in o.get('mortgageable_space_keys', []))}] sellable_bldg=[{', '.join(sn(x) for x in o.get('sellable_building_space_keys', []))}]")
        extra = {k: v for k, v in sc.items() if k not in ('note', 'options', 'owed_amount', 'owed_to_player_id', 'reason', 'shortfall')}
        if extra:
            s += ' EXTRA=' + j(extra)
        return s
    return j(sc)


def parse_args(raw):
    try:
        d = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        return None, raw
    return d, None


def split_msgs(d):
    pub = d.get('public_message')
    pri = d.get('private_thought')
    rest = {k: v for k, v in d.items() if k not in ('public_message', 'private_thought')}
    return pub, pri, rest


def fmt_trade_args(rest):
    return j(rest)


def render_event(e):
    t, p, a = e['type'], e['payload'], e['actor'].get('player_id')
    def side(x):
        return tr_side(x)
    if t == 'DICE_ROLLED':
        return f"DICE {a} {p['d1']}+{p['d2']}" + (' DOUBLE' if p.get('is_double') else '')
    if t == 'PLAYER_MOVED':
        return f"MOVE {a} {sidx(p['from'])}({p['from']})->{sidx(p['to'])}({p['to']})" + (' passedGO' if p.get('passed_go') else '')
    if t == 'CASH_CHANGED':
        return f"CASH {p['player_id']} {p['delta']:+d} {p['reason']}"
    if t == 'RENT_PAID':
        return f"RENT {p['from_player_id']}->{p['to_player_id']} ${p['amount']} on {sidx(p['space_index'])}"
    if t == 'PROPERTY_PURCHASED':
        return f"BUY {p['player_id']} {sidx(p['space_index'])} ${p['price']}"
    if t in ('HOUSE_BUILT', 'HOUSE_SOLD', 'HOTEL_BUILT', 'HOTEL_SOLD'):
        return f"{t} {p['player_id']} {sidx(p['space_index'])} count={p.get('count')}"
    if t in ('PROPERTY_MORTGAGED', 'PROPERTY_UNMORTGAGED'):
        return f"{t} {p['player_id']} {sidx(p['space_index'])} ${p['amount']}"
    if t == 'PROPERTY_TRANSFERRED':
        return f"TRANSFER {sidx(p['space_index'])} {p['from_player_id']}->{p['to_player_id']} mortgaged={p['mortgaged']}"
    if t.startswith('TRADE_'):
        ini, cp = p['initiator_player_id'], p['counterparty_player_id']
        if t in ('TRADE_PROPOSED', 'TRADE_COUNTERED'):
            other = cp if a == ini else ini
            return (f"{t} ex={p['exchange_index']} by {a} to {other} (thread initiator={ini}): "
                    f"{a} gives [{side(p['offer'])}] and requests [{side(p['request'])}]")
        auth = ini if a == cp else cp
        return (f"{t} ex={p['exchange_index']} by {a} of offer authored by {auth} (thread initiator={ini}): "
                f"{auth} gives [{side(p['offer'])}] and requests [{side(p['request'])}]")
    if t == 'AUCTION_STARTED':
        return f"AUCTION_STARTED {p['property_space']} by {p['initiator_player_id']}"
    if t == 'AUCTION_BID_PLACED':
        return f"AUCTION_BID {p['bidder_player_id']} ${p['bid_amount']} on {p['property_space']}"
    if t == 'AUCTION_PLAYER_DROPPED':
        return f"AUCTION_DROP {p['player_id']} on {p['property_space']}"
    if t == 'AUCTION_ENDED':
        return f"AUCTION_ENDED {p['property_space']} {p['reason']} winner={p.get('winner_player_id')} bid={p.get('winning_bid')}"
    if t == 'CARD_DRAWN':
        return f"CARD {a} {p['deck_type']} {p['card_id']}"
    if t == 'SENT_TO_JAIL':
        return f"JAIL {p['player_id']} {p['reason']}"
    return f"{t} actor={a} {j(p)}"


def render_decision(gidx, u, r, ctx):
    """ctx: per-game mutable dict with 'prev_state','prev_bank','tl' (player->last window),'printed','n'"""
    g = r['game']
    pl = r['initial_prompt']['payload']
    gs = pl['game_state']
    ac = pl['action_state']
    did = r['decision_id']
    num = did.rsplit('-', 1)[1]
    pid = r['player_id']
    names = {gs['you']['player_id']: gs['you']['name']}
    for o in gs['others']:
        names[o['player_id']] = o['name']
    lines = []
    ctx['n'] += 1
    st = global_state(gs)
    bank = gs['bank']
    header = (f"### G{g}#{num} [idx{gidx}] T{r['turn_index']} {pid}={MODEL_SHORT.get(r['model'], r['model'])} {r['decision_type']}"
              f"  src={os.path.basename(u['packet'])}:{u['packet_line']} segEv={r['source_lines']['event_segment_start']}-{r['source_lines']['event_segment_end']}")
    lines.append(header)
    # state
    if ctx['prev_state'] is None or ctx['n'] % 20 == 1:
        lines.append('STATE(full): ' + ' | '.join(f'{k}={v}' for k, v in sorted(names.items())))
        lines.append(state_full(st, bank))
    else:
        lines.append('STATE(diff vs previous decision prompt):')
        lines.append(state_diff(ctx['prev_state'], st, ctx['prev_bank'], bank))
    ctx['prev_state'], ctx['prev_bank'] = st, bank
    # menu
    lines.append(f"MENU actions={ac['available_actions']} {render_scenario(ac)}")
    # memory / exposure
    mem = gs['memory']
    tl = mem['public_timeline_last_20']
    prevtl = ctx['tl'].get(pid)
    newn = None
    if prevtl is not None:
        ov = 0
        for k in range(min(len(prevtl), len(tl)), 0, -1):
            if prevtl[-k:] == tl[:k]:
                ov = k; break
        new = tl[ov:]
        gap = (ov == 0 and len(prevtl) > 0 and len(tl) >= 20)
    else:
        new, gap = tl, False
    ctx['tl'][pid] = tl
    refs = []
    for ent in new:
        if ent.get('message'):
            txt = ent['message']
            if txt in ctx['printed']:
                refs.append(f"T{ent['turn_index']} {ent['player_id']} {ent['event_type']}->{ctx['printed'][txt]}")
            else:
                refs.append(f"T{ent['turn_index']} {ent['player_id']} {ent['event_type']} MSG(not previously printed)={txt!r}")
    lines.append(f"PROMPT-MEMORY timeline_window={len(tl)} new_since_own_last_prompt={len(new)}{' POSSIBLE-GAP' if gap else ''} private_notes_window={len(mem['your_private_thoughts_last_10'])}"
                 + (f" new-msgs: {'; '.join(refs)}" if refs else ''))
    if r['decision_type'] == 'TRADE_RESPONSE_DECISION':
        cp = ac['scenario']['counterparty_player_id']
        cand = [e for e in tl if e['event_type'] in ('TRADE_PROPOSED', 'TRADE_COUNTERED') and e['player_id'] == cp]
        if cand:
            e = cand[-1]
            lines.append(f"OFFER-MSG-IN-PROMPT: T{e['turn_index']} {e['player_id']} {e['event_type']} action={e['action']!r} message={e['message']!r}")
        else:
            lines.append('OFFER-MSG-IN-PROMPT: none found in timeline window')
    # attempts
    aa = r['applied_action_record']['action']
    ap_pub, ap_pri = aa.get('public_message'), aa.get('private_thought')
    ap_rest = aa.get('args')
    sm = r['resolution']['sequence_meta']
    lines.append(f"ATTEMPTS n={len(r['attempts'])} resolution: retry_used={r['resolution']['retry_used']} fallback_used={r['resolution']['fallback_used']} fallback_reason={r['resolution']['fallback_reason']} cond={sm['response_condition']} returned_model={sm['returned_model']} model_fallback={sm['model_fallback_used']}")
    selected = None
    for a in r['attempts']:
        ai = a['attempt_index_zero_based']
        raw = a['raw_response']
        msg = raw['choices'][0]['message'] if raw and raw.get('choices') else {}
        usage = (raw or {}).get('usage') or {}
        rt = ((usage.get('completion_tokens_details') or {}).get('reasoning_tokens'))
        s = f" a{ai} [{a['response_condition']}] outcome={a['outcome']}"
        if a.get('reason'):
            s += f" reason={a['reason']}"
        if a.get('error_type'):
            s += f" err_type={a['error_type']}"
        if a.get('error_message'):
            s += f" err_msg={a['error_message']!r}"
        if a['validation_errors']:
            s += f" validation_errors={a['validation_errors']}"
        s += f" rt={rt}"
        lines.append(s)
        ptc = a.get('parsed_tool_call')
        if ptc:
            d, bad = parse_args(ptc['arguments'])
            if d is None:
                lines.append(f"   tool={ptc['name']} UNPARSEABLE args={bad!r}")
            else:
                pub, pri, rest = split_msgs(d)
                same = (ptc['name'] == aa['action'] and pub == ap_pub and pri == ap_pri and rest == ap_rest)
                if len(a['parsed_tool_calls'] or []) > 1:
                    lines.append(f"   NOTE multiple tool calls: {len(a['parsed_tool_calls'])}")
                if same:
                    lines.append(f"   tool={ptc['name']} args={j(rest)} == applied action (public/private text identical to APPLIED below)")
                    selected = ai
                else:
                    lines.append(f"   tool={ptc['name']} args={j(rest)} public={pub!r} private={pri!r}  [DIFFERS from applied]")
        elif raw is None:
            lines.append('   no raw response (null)')
        else:
            if msg.get('refusal'):
                rf = msg['refusal']
                key = ('refusal', rf)
                if key in ctx['printed']:
                    lines.append(f"   refusal text = {ctx['printed'][key]}")
                else:
                    ctx['printed'][key] = f'refusal text first printed at G{g}#{num}'
                    lines.append(f"   refusal={rf!r}")
            else:
                lines.append(f"   no tool call; message-fields={sorted(k for k in msg)}; refusal={msg.get('refusal')!r}")
        if msg.get('content'):
            lines.append(f"   content={compress_counting(msg['content'])!r}")
        rsn = msg.get('reasoning')
        rd = msg.get('reasoning_details') or []
        texts = []
        opaque = []
        for x in rd:
            if x.get('type') == 'reasoning.text':
                texts.append(('text', x.get('text')))
            elif x.get('type') == 'reasoning.summary':
                texts.append(('summary', x.get('summary')))
            elif x.get('type') == 'reasoning.encrypted':
                d = x.get('data') or {}
                opaque.append(f"encrypted({x.get('format')},chars={d.get('serialized_characters')})")
            else:
                opaque.append(f"other:{x.get('type')}")
        def ptxt(label, tx):
            lines.append(f"   {label}:")
            for ln in tx.strip().split('\n'):
                if ln.strip():
                    lines.append('      | ' + ln)
        if rsn:
            dup = any(t[1] == rsn for t in texts)
            if dup:
                ptxt(f"provider-{texts[0][0]} (reasoning field == reasoning_details {texts[0][0]})", rsn)
                for kind, tx in texts:
                    if tx != rsn:
                        ptxt(f"provider-{kind} (distinct detail)", tx)
            else:
                ptxt("provider-reasoning-field", rsn)
                for kind, tx in texts:
                    ptxt(f"provider-{kind} (detail)", tx)
        else:
            for kind, tx in texts:
                ptxt(f"provider-{kind}", tx)
        if opaque:
            lines.append('   opaque: ' + ', '.join(opaque))
    # applied
    lines.append(f"APPLIED action={aa['action']} args={j(ap_rest)} valid={r['applied_action_record']['decision_meta']['valid']} err={r['applied_action_record']['decision_meta']['error']} selected_attempt={selected}")
    lines.append(f"  public: {ap_pub!r}")
    lines.append(f"  private: {ap_pri!r}")
    if ap_pub:
        ctx['printed'].setdefault(ap_pub, f'G{g}#{num}')
    # events
    evs = r['canonical_event_segment']
    out = []
    post = False
    bk = 0
    for e in evs:
        t = e['type']
        p = e['payload']
        if t == 'LLM_DECISION_REQUESTED':
            if p.get('decision_id') != did:
                out.append(f"  {e['seq']} (next) REQUESTED {p.get('decision_id','').rsplit('-',1)[1]} {p.get('player_id')} {p.get('decision_type')}")
            else:
                bk += 1
            continue
        if t == 'LLM_DECISION_RESPONSE':
            if p.get('decision_id') == did and p.get('action_name') == aa['action'] and p.get('valid') is True and not p.get('error'):
                bk += 1
            else:
                out.append(f"  {e['seq']} RESPONSE-EVENT MISMATCH {j(p)}")
            out.append('  -- response applied --')
            continue
        if t == 'LLM_PUBLIC_MESSAGE':
            if p.get('decision_id') == did and p.get('message') == ap_pub and p.get('player_id') == pid:
                bk += 1
            else:
                out.append(f"  {e['seq']} PUBLIC-EVENT DIFFERS {j(p)}")
            continue
        if t == 'LLM_PRIVATE_THOUGHT':
            if p.get('decision_id') == did and p.get('thought') == ap_pri and p.get('player_id') == pid:
                bk += 1
            else:
                out.append(f"  {e['seq']} PRIVATE-EVENT DIFFERS {j(p)}")
            continue
        out.append(f"  {e['seq']} T{e['turn_index']} {render_event(e)}")
    lines.append(f"EVENTS ({len(evs)} in segment; {bk} bookkeeping LLM_* events equal to applied fields, omitted):")
    lines.extend(out)
    return '\n'.join(lines)


def all_rendered():
    units = load_units()
    ctxs = {}
    res = []
    for gi, (u, r) in enumerate(units):
        g = r['game']
        ctx = ctxs.setdefault(g, {'prev_state': None, 'prev_bank': None, 'tl': {}, 'printed': {}, 'n': 0})
        res.append((gi, g, r['decision_id'], render_decision(gi, u, r, ctx)))
    return res


if __name__ == '__main__':
    cmd = sys.argv[1]
    rend = all_rendered()
    if cmd == 'show':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        for gi, g, did, txt in rend[a:b]:
            print(txt)
            print()
    elif cmd == 'write-from':
        a = int(sys.argv[2]); mx = int(sys.argv[3]); outfn = sys.argv[4]
        cur, n = [], 0
        end = a
        for gi, g, did, txt in rend[a:]:
            if cur and (n + len(txt) > mx or g != rend[a][1]):
                break
            cur.append(txt); n += len(txt) + 2; end = gi + 1
        open(outfn, 'w').write('\n\n'.join(cur) + '\n')
        print('idx', a, 'to', end, '(exclusive);', n, 'chars;', end - a, 'decisions; game', rend[a][1])
    elif cmd == 'write-chunks':
        out = sys.argv[2]
        mx = int(sys.argv[3]) if len(sys.argv) > 3 else 40000
        os.makedirs(out, exist_ok=True)
        cur, curlen, ci, start = [], 0, 0, 0
        index = []
        for gi, g, did, txt in rend:
            if cur and (curlen + len(txt) > mx or g != rend[start][1]):
                fn = f'{out}/chunk_{ci:03d}.txt'
                open(fn, 'w').write('\n\n'.join(cur) + '\n')
                index.append({'chunk': ci, 'file': fn, 'start_idx': start, 'end_idx': gi, 'game': rend[start][1], 'chars': curlen})
                ci += 1; cur, curlen, start = [], 0, gi
            cur.append(txt); curlen += len(txt) + 2
        if cur:
            fn = f'{out}/chunk_{ci:03d}.txt'
            open(fn, 'w').write('\n\n'.join(cur) + '\n')
            index.append({'chunk': ci, 'file': fn, 'start_idx': start, 'end_idx': len(rend), 'game': rend[start][1], 'chars': curlen})
        json.dump(index, open(out + '/index.json', 'w'), indent=0)
        print(len(index), 'chunks;', sum(i['chars'] for i in index), 'chars total')
