import json,re
b=json.load(open('/Users/kushagra/CS-Projects/MonopolyBench/contracts/data/board.json'))
def key(name): return re.sub(r'[^A-Z0-9]+','_',name.upper()).strip('_')
SP={}
for s in b['spaces']:
    if s.get('price'):
        SP[key(s['name'])]=s
HC=b['house_cost_by_group']
GROUPS={}
for k,s in SP.items(): GROUPS.setdefault(s.get('group'),[]).append(k)
def mval(k): return SP[k]['price']//2
def hcost(k): return HC.get(SP[k]['group'],0)
