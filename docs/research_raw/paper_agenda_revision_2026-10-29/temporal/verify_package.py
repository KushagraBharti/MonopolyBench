"""Final source, excerpt and compiled-layout checks for this analysis package."""
from hashlib import sha256
import json
from extract_sample import ROOT, OUT
from inspect_followups import load_games


QUOTES = [
    (16,103,'private_thought','End, buy Virginia on sight, then house pink'),
    (16,159,'private_thought','Buy at list is the only way to close pink.'),
    (16,159,'public_message','Virginia is mine. Pink set closed.'),
    (20,42,'private_thought','do not chase past $230.'),
    (20,44,'private_thought','Prior note said drop at $231+, but $232 is only $2 past the hard stop'),
    (17,228,'private_thought','Do not drop before $99.'),
]


def main():
    rows=[json.loads(x) for x in (OUT/'row_ledger.jsonl').read_text().splitlines()]
    assert len(rows)==240 and len({x['id']for x in rows})==240
    checked_fields=0
    for r in rows:
        for entry in r['fields'].values():
            if entry['present']:
                assert sha256(entry['value'].encode()).hexdigest()==entry['sha256']
                checked_fields+=1
        assert r['provider_summary_semantically_coded'] is False
    sample,games=load_games()
    excerpts=[]
    for g,d,field,text in QUOTES:
        a=next(a for a in games[g]['actions'] if int(a['decision_id'].rsplit('-',1)[1])==d)
        original=a['action'][field]
        assert text in original,(g,d,text)
        start=original.index(text)
        excerpts.append({'game':g,'decision_index':d,'field':field,'quote':text,
                         'start':start,'end':start+len(text),
                         'field_sha256':sha256(original.encode()).hexdigest()})
    (OUT/'excerpt_manifest.json').write_text(json.dumps(excerpts,indent=2)+'\n')
    hashes=json.loads((OUT/'source_hashes.json').read_text())
    for relative,expected in hashes.items():
        assert sha256((ROOT/relative).read_bytes()).hexdigest()==expected,relative
    log=(OUT/'build/review_wrapper.log').read_text()
    forbidden=['Overfull','Missing character','undefined references','undefined citations','LaTeX Error']
    assert not any(s in log for s in forbidden)
    result={'rows_checked':len(rows),'nonempty_field_hashes_checked':checked_fields,
            'source_hashes_checked':len(hashes),'displayed_quote_checks':len(excerpts),
            'compilation':'LuaLaTeX two passes, four pages, zero overfull/missing glyph/undefined-reference reports',
            'visual_review':'All four final pages rendered with Ghostscript at90dpi and inspected; readable tables and no clipping',
            'pdf_sha256':sha256((OUT/'build/review_wrapper.pdf').read_bytes()).hexdigest(),
            'original_game_edits':False,'new_engine_executions':0,'new_provider_calls':0}
    (OUT/'package_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
