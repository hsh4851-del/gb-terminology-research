import json, re
from classify import *
data=load()
have={r['id'] for r in json.load(open('cases.json'))}
DPH = r"(청구소송|소송을?당|소장(을|이)?(받|왔|날아|송달)|지급명령(을|이)?(받|왔|날아|송달)|이행권고|고소(를)?당|고소당|고소장(을|이)?(받|접수)|피고|피고소|독촉(을|이|장)?|추심(이|을)?(들어|받|왔|와)|내용증명(을|이)?(받|왔|날아)|청구(가|를)?(들어|받)|갚아야|못내|못냈|안냈|내지못|납부(를)?못|미납(했|하였|한상태|중)|연체(했|하였|중|되))"
out={}
for g in ["도매 및 유통","제조 및 납품업","서비스 및 전문용역","렌탈업"]:
    rows={}
    for k in KW[g]:
        if k not in data: continue
        kk=re.escape(norm(k)); pr=prox_re(k)
        dp=re.compile(rf"{kk}.{{0,40}}{DPH}|{DPH}.{{0,25}}{kk}")
        for q in data[k]:
            if q['_id'] in have: continue
            t=norm(txt(q))
            if (pr.search(t) and DEBTOR.search(t)) or dp.search(t):
                r=rows.setdefault(q['_id'],dict(q,_kws=set())); r['_kws'].add(k)
    rs=sorted(rows.values(),key=lambda r:r['createdAt'] or '')
    for r in rs: r['_kws']=sorted(r['_kws'])
    json.dump([{k:v for k,v in r.items() if k!='ans0'} for r in rs],open(f'dcand_{g}.json','w'),ensure_ascii=False)
    print(g,len(rs))
