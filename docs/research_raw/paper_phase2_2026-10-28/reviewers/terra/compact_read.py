#!/usr/bin/env python3
"""Display full decision evidence while suppressing exact copies of text already shown.

Read-only aid: no coverage or judgments are produced. Encrypted blocks are labeled;
the decision, every attempt, events, observation and source provenance remain visible.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PHASE = ROOT / 'docs/research_raw/paper_phase2_2026-10-28'

def out(x):
    print(json.dumps(x, ensure_ascii=False, separators=(',', ':')))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('batch')
    ap.add_argument('index', type=int)
    args = ap.parse_args()
    unit = json.loads((PHASE / 'batches' / (args.batch + '.json')).read_text())['units'][args.index]
    rec = json.loads((ROOT / unit['packet']).read_text().splitlines()[unit['packet_line'] - 1])
    assert rec['decision_id'] == unit['decision_id']
    out({'unit': unit, 'source_run': rec['source_run'], 'source_lines': rec['source_lines']})
    out({'applied_action_record': rec['applied_action_record']})
    events = []
    action = rec['applied_action_record']['action']
    for e in rec['canonical_event_segment']:
        payload = copy.deepcopy(e['payload'])
        for ek, ak in [('message','public_message'), ('thought','private_thought')]:
            if ek in payload and payload[ek] == action.get(ak):
                payload[ek] = {'identical_to_applied_action': ak}
        events.append({'seq':e['seq'],'type':e['type'],'actor':e['actor'],'payload':payload})
    out({'events': events})
    prompt = copy.deepcopy(rec['initial_prompt'])
    # Repeated memory entries are still exposed to this player. Reference only
    # exactly equal entries in the most recent prompt this player actually saw;
    # retain new, altered, and differently ordered entries at their positions.
    actor = rec['applied_action_record']['actor_player_id']
    for prior_unit in reversed(json.loads((PHASE / 'batches' / (args.batch + '.json')).read_text())['units'][:args.index]):
        if prior_unit['game'] != rec['game']:
            break
        prior = json.loads((ROOT / prior_unit['packet']).read_text().splitlines()[prior_unit['packet_line'] - 1])
        if prior['applied_action_record']['actor_player_id'] != actor:
            continue
        old_memory = prior['initial_prompt'].get('payload', {}).get('game_state', {}).get('memory', {})
        memory = prompt.get('payload', {}).get('game_state', {}).get('memory', {})
        for field in ('public_timeline_last_20', 'your_private_thoughts_last_10'):
            previous = old_memory.get(field, [])
            if field in memory:
                memory[field] = {'prior_observation':prior_unit['decision_id'], 'prior_field':field,
                                 'entries_in_order':[{'prior_index':previous.index(entry)} if entry in previous else entry for entry in memory[field]]}
        break
    first = json.loads((ROOT / f"docs/research_raw/paper_phase1_2026-10-28/astra/review_packets/game-{rec['game']:02}-part-001.jsonl").read_text().splitlines()[0])['initial_prompt']
    for i, msg in enumerate(prompt.get('messages', [])):
        if msg.get('role') == 'system' and msg == first.get('messages', [])[i]:
            prompt['messages'][i] = {'role':'system','identical_to_game_first_system_message':True}
    out({'observation':prompt})
    for a in rec['attempts']:
        a = copy.deepcopy(a)
        rp = a.pop('raw_response', None)
        if a.get('prompt') == rec['initial_prompt']:
            a['prompt'] = {'same_as_initial_prompt': True}
        elif isinstance(a.get('prompt'), dict):
            retry_prompt = a['prompt']
            for key in ('payload', 'raw_payload'):
                if key in retry_prompt and retry_prompt[key] == rec['initial_prompt'].get(key):
                    retry_prompt[key] = {'identical_to_initial_prompt':key}
            payload = retry_prompt.get('payload')
            if isinstance(payload, dict) and 'response_instruction' in payload:
                without_instruction = {k:v for k,v in payload.items() if k != 'response_instruction'}
                if without_instruction == rec['initial_prompt'].get('payload'):
                    retry_prompt['payload'] = {'identical_to_initial_payload_except_added_response_instruction':payload['response_instruction']}
        if a.get('parsed_tool_call') in (a.get('parsed_tool_calls') or []):
            a['parsed_tool_call'] = {'identical_to_parsed_tool_calls_entry':True}
        parsed = a.get('parsed_tool_calls') or []
        out({'attempt':a})
        if rp is None:
            continue
        rp = copy.deepcopy(rp)
        for c in rp.get('choices', []):
            m = c.get('message') or {}
            reasoning = m.get('reasoning')
            for d in m.get('reasoning_details') or []:
                if isinstance(d.get('signature'), str):
                    sig = d['signature']
                    d['signature'] = {'sha256':hashlib.sha256(sig.encode()).hexdigest(), 'characters':len(sig), 'note':'non-readable signature'}
                for field in ('summary', 'text'):
                    if d.get(field) is not None and d[field] == reasoning:
                        d[field] = {'identical_to_message_reasoning': True}
            for call in m.get('tool_calls') or []:
                if call.get('function') in parsed:
                    call['function'] = {'identical_to_parsed_tool_calls_entry':True}
            if m.get('content') is not None and m['content'] == a.get('assistant_content'):
                m['content'] = {'identical_to_attempt_assistant_content':True}
        out({'provider_response':rp})
    resolution = copy.deepcopy(rec['resolution'])
    if resolution.get('final_action') == action:
        resolution['final_action'] = {'identical_to_applied_action':True}
    out({'resolution':resolution, 'physical_responses':rec['physical_responses']})

if __name__ == '__main__':
    main()
