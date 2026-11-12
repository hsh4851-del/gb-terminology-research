import json, os, subprocess, urllib.parse, sys, time
from concurrent.futures import ThreadPoolExecutor
os.makedirs('raw',exist_ok=True)
def norm(s): return (s or '').replace(' ','').replace('\n','')
def page(kw, offset, limit=50):
    url=("https://www.lawtalk.co.kr/api/qna/question/search?blindFilter=true&filter=answers&keyword="+urllib.parse.quote(kw)+f"&limit={limit}&offset={offset}&sort=accuracy")
    for a in range(6):
        try:
            out=subprocess.run(["curl","-s","--compressed","--max-time","180",url],capture_output=True).stdout
            d=json.loads(out)
            if "questions" not in d: raise ValueError(str(d)[:200])
            break
        except Exception as e: time.sleep(5*(a+1))
    else: return None
    qs=[]
    for q in d["questions"]:
        ans=q.get("answers") or []
        qs.append({"_id":q["_id"],"number":q.get("number"),"slug":q.get("slug"),"title":q.get("title"),"titleOrigin":q.get("titleOrigin"),
          "body":q.get("body"),"createdAt":q.get("createdAt"),"viewCount":q.get("viewCount"),
          "categories":[c["name"] for c in q.get("categories",[])],
          "aikw":(q.get("aiResponse") or {}).get("keywords"),"nans":len(ans),
          "ans0":(ans[0].get("body") if ans and isinstance(ans[0],dict) else None)})
    return qs
def crawl(kw, total, limit=50, stop_empty=999):
    hits=[]; seen=set(); empty=0; off=0; pages=0
    k=norm(kw)
    while off<total:
        qs=page(kw,off,limit); pages+=1
        if qs is None or not qs: break
        m=0
        for q in qs:
            if q["_id"] in seen: continue
            seen.add(q["_id"])
            if k in norm(q["title"])+norm(q["titleOrigin"])+norm(q["body"]):
                hits.append(q); m+=1
        empty = empty+1 if m==0 else 0
        if empty>=stop_empty: break
        off+=limit
    json.dump(hits,open(f'raw/{kw}.json','w'),ensure_ascii=False)
    return kw, len(hits), len(seen), pages
if __name__=="__main__":
    T=json.load(open('totals.json'))
    kws=[l for l in open(sys.argv[1]).read().split("\n") if l] if len(sys.argv)>1 else list(T)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda k: crawl(k,T[k]), kws): print(*r, flush=True)
