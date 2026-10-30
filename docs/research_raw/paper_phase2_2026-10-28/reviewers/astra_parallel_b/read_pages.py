"""Display original pages with shorter reference paths; never mark coverage.

Only JSON reference-object notation and unreadable signature bytes are shortened.
All readable text, observation values, legal menus and event values remain.
"""
import re
import sys
from pathlib import Path

base = Path(__file__).resolve().parent.parent.parent / 'full_review'
aliases = {'packets':'d','observation':'obs','game_state':'state','action_state':'menu','memory':'mem','public_timeline_last_20':'public20','your_private_thoughts_last_10':'private10','applied_action':'applied','private_thought':'private','public_message':'public','provider_response':'provider','parsed_tool_call':'tool','parsed_tool_calls':'tools','$decoded_json_string':'json'}
print('REFERENCE ALIASES:', aliases)
for page in range(int(sys.argv[2]), int(sys.argv[3])+1):
    text = (base / f'game-{int(sys.argv[1]):02d}' / f'page-{page:04d}.txt').read_text()
    def reference(m):
        return '@' + '/'.join(aliases.get(v,v) for v in m[1].split('/')[1:])
    text = re.sub(r'\{"\$same_as":"([^"]+)"\}', reference, text)
    text = re.sub(r'"signature":"[^"]+"', '"signature":"[non-readable signature bytes, retained in original page]"', text)
    print(text)
