import json, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from kws import KW
def tot(kw):
    url=("https://www.lawtalk.co.kr/api/qna/question/search?blindFilter=true&filter=answers&keyword="+urllib.parse.quote(kw)+"&limit=1&offset=0&sort=accuracy")
    out=subprocess.run(["curl","-s","--compressed","--max-time","60",url],capture_output=True).stdout
    return json.loads(out)["totalCount"]
allk=[(g,k) for g,ks in KW.items() for k in ks]
with ThreadPoolExecutor(6) as ex: res=list(ex.map(lambda gk: tot(gk[1]), allk))
T={}
for (g,k),t in zip(allk,res): print(g,'|',k,'|',t); T[k]=t
json.dump(T,open('totals.json','w'),ensure_ascii=False)
print(sum(res))
