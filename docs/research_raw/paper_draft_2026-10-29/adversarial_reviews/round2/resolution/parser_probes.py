"""Document reviewed parser boundaries without changing the reviewed module."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
path = HERE.parents[1] / 'audit_conditions.py'
spec = importlib.util.spec_from_file_location('reviewed_conditions', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = [
    ('valid_top_level', '{"name":"end_turn"}', ('end_turn', 'json_name')),
    ('valid_nested_function', '{"function":{"name":"end_turn"}}', (None, 'no_named_call')),
    ('valid_action_key', '{"action":"end_turn"}', (None, 'no_named_call')),
    ('empty_content', '', (None, 'unparsed')),
    ('malformed_nested_name', 'prefix {"function":{"name":"end_turn"}}', ('end_turn', 'malformed_explicit_name')),
    ('multiple_different_names', '{"name":"end_turn"}{"name":"propose_trade"}', (None, 'unparsed')),
    ('repeated_same_name', '{"name":"end_turn"}{"name":"end_turn"}', ('end_turn', 'malformed_explicit_name')),
    ('semantic_argument_prose', '{"public_message":"I will build houses."}', (None, 'no_named_call')),
]
results = []
for label, content, expected in cases:
    actual = module.content_name(content)
    assert actual == expected, (label, actual, expected)
    results.append({'label': label, 'content': content, 'result': actual})
(HERE / 'parser_probe_results.json').write_text(json.dumps(results, indent=2) + '\n')
print(f'{len(results)} parser boundary probes passed')
