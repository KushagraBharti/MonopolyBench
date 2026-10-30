"""Freeze primary HTML sources for this review; no game/provider calls."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import urllib.request
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
ARXIV = {
    'vending':'2502.15840v1', 'agentmonopoly':'2610.29330v2',
    'finboard':'2605.27896v1', 'cattle':'2605.14537v1',
    'sotopia':'2310.11667v1', 'concordia':'2312.03664v1',
    'agentcompany':'2412.14161v1', 'agentbench':'2308.03688v1',
    'webarena':'2307.13854v1', 'osworld':'2404.07972v1',
    'taubench':'2406.12045v1', 'agentdojo':'2406.13352v1',
    'mlebench':'2410.07095v1', 'metr':'2503.14499v1',
    'negotiationarena':'2402.05863v1', 'machiavelli':'2304.03279v1',
    'agentboard':'2401.13178v1', 'hal':'2510.11977v1',
    'dece':'2610.35773v1', 'cheap_talk':'2604.04782v1',
    'when_agents_lie':'2607.05132v1', 'commitment_standing':'2610.21203v1',
    'empty_commitments':'2610.01045v1', 'agents_that_matter':'2407.01502v1',
    'empty_commitments_v2':'2610.01045v2', 'arena_paper':'2608.14825v3',
}
URLS = {k:f'https://arxiv.org/html/{v}' for k,v in ARXIV.items()}
URLS.update(vending2='https://andonlabs.com/evals/vending-bench-2',
            vending_arena='https://andonlabs.com/evals/vending-bench-arena',
            hal_about='https://hal.cs.princeton.edu/about',
            metr_page='https://metr.org/time-horizons/',
            agentmonopoly_repo='https://github.com/SuELS-Group/Agent_Monopoly',
            hal_repo='https://github.com/princeton-pli/hal-harness')

def fetch(item):
    key, url = item
    out = {'key':key,'requested_url':url,'arxiv_version':ARXIV.get(key),
           'accessed_utc':datetime.now(timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'MonopolyBench literature audit (research)'})
        with urllib.request.urlopen(req,timeout=55) as r:
            raw=r.read(); out.update(final_url=r.url,status=r.status)
        soup=BeautifulSoup(raw,'html.parser')
        for t in soup(['script','style','nav']): t.decompose()
        out['title']=soup.title.get_text(' ',strip=True) if soup.title else ''
        out['authors']=[t.get('content') for t in soup.select('meta[name="citation_author"]')]
        out['raw_sha256']=sha256(raw).hexdigest()
        text=soup.get_text('\n',strip=True)
        (ROOT/'sources'/f'{key}.txt').write_text(text)
        out['text_sha256']=sha256(text.encode()).hexdigest()
        out['text_path']=f'sources/{key}.txt';out['characters']=len(text)
        out['headings']=[t.get_text(' ',strip=True) for t in soup.select('h1,h2,h3,h4')]
    except Exception as e: out.update(status='failed',error=str(e))
    return out

if __name__=='__main__':
    (ROOT/'sources').mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool: rows=list(pool.map(fetch,URLS.items()))
    (ROOT/'source_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows: print(r['key'],r['status'],r.get('characters'),r.get('title',r.get('error')))
