"""Build reference metadata; author 'and others' is intentional, never invented."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=[
 ('L01','vending','Backlund, Axel and Petersson, Lukas','2.1-2.5;3.2;3.5','economic'),
 ('L02','vending2','{Andon Labs}','Improvements;operation;scoring;system prompt','economic'),
 ('L03','vending_arena','{Andon Labs}','Introduction;rounds8-9,13-14','economic'),
 ('L04','arena_paper','Li, Zeyuan and Petersson, Lukas and Acquisti, Alessandro and Bakker, Michiel A.','2;4;6;App A,D,F','social'),
 ('L05','agentmonopoly','Wu, Changshun and Li, Mengyu and Marsault, Mathis and Huang, Xiaowei and Cheng, Chih-Hong','3-5;limitations;App A','economic'),
 ('L06','agentmonopoly_repo','{SuELS-Group}','README Architecture;Key Features;Specific Rules;Experiments','software'),
 ('L07','finboard','Hu, Xuesi and Wang, Peng and others','2-4;App C,E','economic'),
 ('L08','cattle','Müller, Robert and Müller, Clemens','3.1-3.3;4.3-4.6;App B-D','economic'),
 ('L09','dece','Zhang, Fengrui and Li, Xiang and others','3-5;App A.3,C,G','economic'),
 ('L10','sotopia','Zhou, Xuhui and Zhu, Hao and others','2-3;5.2;App C,D','social'),
 ('L11','concordia','Vezhnevets, Alexander Sasha and Agapiou, John P. and others','2.1-2.3;4.3','social'),
 ('L12','negotiationarena','Bianchi, Federico and Chia, Patrick John and Yuksekgonul, Mert and Tagliabue, Jacopo and Jurafsky, Dan and Zou, James','2-5;App D.3','social'),
 ('L13','machiavelli','Pan, Alexander and Chan, Jun Shern and Zou, Andy and Li, Nathaniel and Basart, Steven and Woodside, Thomas and Zhang, Hanlin and Emmons, Scott and Hendrycks, Dan','2.2-2.5;4-5','social'),
 ('L14','cheap_talk','Shi, Jerick and Zhang, Terry Jingcheng and Jin, Zhijing and Conitzer, Vincent','3-4;App A','social'),
 ('L15','when_agents_lie','Shi, Jerick and Zhang, Terry Jingcheng and Schölkopf, Bernhard and Conitzer, Vincent and Jin, Zhijing','3;App A,E,F','social'),
 ('L16','commitment_standing','Wei, Lan and Shen, Bingyu and Tang, Jiaqi and Lu, Qing and Huang, Kuan and Xu, Meng and Li, Miles Q. and Hu, Bin and Li, Boyang','2-6;App D','social'),
 ('L17','empty_commitments','Tang, Jiaqi and Wei, Lan and Shen, Bingyu and Li, Boyang','2-4','social'),
 ('L18','agentcompany','Xu, Frank F. and Song, Yufan and Li, Boxuan and others','2-4;6','validity'),
 ('L19','agentbench','Liu, Xiao and Yu, Hao and Zhang, Hanchen and others','3-4;3.4;4.3','validity'),
 ('L20','webarena','Zhou, Shuyan and Xu, Frank F. and Zhu, Hao and others','2-3;5.2;App A.2','validity'),
 ('L21','osworld','Xie, Tianbao and Zhang, Danyang and Chen, Jixuan and others','2.2-2.4;3.2;5','validity'),
 ('L22','taubench','Yao, Shunyu and Shinn, Noah and Razavi, Pedram and Narasimhan, Karthik','3-5;App B','validity'),
 ('L23','agentdojo','Debenedetti, Edoardo and Zhang, Jie and Balunovic, Mislav and Beurer-Kellner, Luca and Fischer, Marc and Tramèr, Florian','3-4;App B','validity'),
 ('L24','mlebench','Chan, Jun Shern and Chowdhury, Neil and Jaffe, Oliver and others','2-4;6;App A.3','validity'),
 ('L25','metr','Kwa, Thomas and West, Ben and Becker, Joel and others','3-4;8.1;author FAQ','validity'),
 ('L26','agentboard','Ma, Chang and Zhang, Junlei and Zhu, Zhihao and others','3.3;4.5;5.3;6','validity'),
 ('L27','hal','Kapoor, Sayash and Stroebl, Benedikt and others','2-4;App A7.2','validity'),
 ('L28','agents_that_matter','Kapoor, Sayash and Stroebl, Benedikt and Siegel, Zachary S. and Nadgir, Nitya and Narayanan, Arvind','2;4-6','validity'),
 ('L29','empty_commitments_v2','Tang, Jiaqi and Shen, Bingyu and Wei, Lan and Lu, Qing and Ololade, Bethel and Galvis, Danny and Li, Miles Q. and Hu, Bin and Li, Boyang','2-5;App E','social'),
]

def main():
    source={r['key']:r for r in json.loads((ROOT/'source_manifest.json').read_text())}
    rows=[]; bib=[]
    for lid,key,authors,sections,group in DATA:
        r=source[key];url=r['requested_url'];version=re.search(r'/(\d{4}\.\d{4,5}v\d+)',url)
        version=version.group(1) if version else None
        year='20'+version[:2] if version else ('2025' if key in ['vending2','vending_arena'] else '2026')
        title=r['title'].removesuffix(' | Andon Labs').replace('GitHub - ','').replace(' · GitHub','')
        if key=='mlebench':title='MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering'
        if key=='sotopia':title='SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents'
        if key=='dece':title='A Unified Arena for LLM Agents across Diverse Eurogames'
        if key=='cheap_talk':title='Cheap Talk, Empty Promise: Frontier LLMs easily break public promises for self-interest'
        if key=='commitment_standing':title="Who May Release an Agent's Promise? Standing over Commitments in Multi-Party Chat"
        if key=='empty_commitments':title='Empty Commitments: When Agents Promise What Their Runtime Cannot Deliver'
        typ='arxiv_manuscript' if version else ('software_documentation' if 'repo' in key else 'author_evaluation_page')
        heading=next(line[4:] for line in (ROOT/'literature.md').read_text().splitlines() if line.startswith('### '+lid+'.'))
        anchor=re.sub(r'[^\w\- ]','',heading.lower()).replace(' ','-')
        citation_key='empty_commitments_v1' if key=='empty_commitments' else key
        row={'id':lid,'key':key,'citation_key':citation_key,'title':title,'authors_bibtex':authors,'url':url,'version':version,
             'source_type':typ,'sections_inspected':sections.split(';'),'family':group,
             'status':'primary_methods_inspected','text_sha256':r['text_sha256'],
             'local_source':r['text_path'],'comparison_location':f'literature.md#{anchor}',
             'absence_claim_status':'No repository-wide or exclusive-absence claim verified',
             'publication_status':'ArXiv version inspected; proceedings status not independently checked'}
        if key in ['machiavelli','negotiationarena']:
            row['publication_status']='ICML proceedings independently checked'
            row['proceedings_url']=f'https://proceedings.mlr.press/v{202 if key=="machiavelli" else 235}/{"pan23a" if key=="machiavelli" else "bianchi24a"}.html'
        rows.append(row)
        fields={'title':'{'+title+'}','author':authors,'year':year,'url':url,
                'note':f'Inspected {version or "author page/software documentation"}; accessed 2026-10-29; sections {sections}'}
        if version:fields.update(eprint=version,archivePrefix='arXiv')
        bib.append('@misc{'+citation_key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}\n')
    for key in ['metr_page','hal_about','hal_repo']:
        r=source[key];rows.append({'id':key,'key':key,'url':r['requested_url'],'source_type':'author_page_or_software',
                                 'status':'supplementary_primary_check','text_sha256':r['text_sha256'],
                                 'local_source':r['text_path']})
    (ROOT/'comparison.json').write_text(json.dumps({'checked_date':'2026-10-29','scope':'Bounded comparisons in literature.md; not an exclusive-novelty proof','entries':rows},indent=2,ensure_ascii=False)+'\n')
    (ROOT/'references.bib').write_text('\n'.join(bib))
    print(f'{len(DATA)} bibliography records; {len(rows)} comparison records')

if __name__=='__main__':main()
