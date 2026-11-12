import json, re, os, collections
from kws import KW
def norm(s): return re.sub(r'\s+','',s or '')
NP_EXTRA = "|회수|청구"
NP = r"(미지급|못받|받지못|못준|안받|안주|안줘|주지않|지급하지않|지급안|지급을?안|지급(을|이)?(미루|거부|거절|지연|않)|미수|미납|체납|연체|입금(을|이)?(안|하지|않)|떼였|떼먹|떼어먹|안갚|갚지|미결제|결제(를|가)?(안|하지|않|미루)|정산(을|이)?(안|하지|못|않)|미변제|변제하지|받을돈|미정산|체불|밀려|밀린|안들어|안나오|못하고있|미루고|미뤄|안해주|지급받지|받지않)"
# proximity in space-stripped text: keyword then up to 30 chars then NP, or NP then up to 15 chars then keyword
BROAD={"수수료","렌트비","렌탈","미수금","물건값","도매","유통업","판매대금","거래대금","렌트료"}
def prox_re(kw):
    k=re.escape(norm(kw))
    if kw not in BROAD:
        npx=NP[:-2]+NP_EXTRA+")"
        return re.compile(rf"{k}.{{0,30}}{npx}|{npx}.{{0,15}}{k}")
    return re.compile(rf"{k}.{{0,30}}{NP}|{NP}.{{0,15}}{k}")
DEBTOR = re.compile(r"독촉(을|이|장)?(받|왔|와|오)|지급명령(을|이)?(받|왔|날아)|소장(을|이)?(받|왔|날아)|추심(이|을)?(들어|받고|왔|와서|오고)|(제가|저는|저희가).{0,20}(갚아야|갚지못|못갚|연체)|갚을(수|능력|여력)|상환(을|이)?(못|어렵|안됩)|개인회생|파산신청|대출(을|금)?(못갚|연체)|채무자(입니다|인데|로서)|제가채무자")
def txt(q): return (q.get('title') or '')+'\n'+(q.get('body') or '')
def load():
    data={}
    for g,ks in KW.items():
        for k in ks:
            p=f'raw/{k}.json'
            if os.path.exists(p): data[k]=json.load(open(p))
    return data
FIN_INST=["미소금융","햇살론","새희망홀씨","서민금융","서민금융진흥원","사회연대은행","신용협동조합","신협","새마을금고","마이크로크레딧","사회적금융","신용보증재단","소상공인 정책자금","구상금"]
FIN_CTX=re.compile(r"구상|대위변제|지급명령|소장|독촉|추심|연체|미납|압류|상환|갚|변제|보증")
INST_RE=re.compile(r"미소금융|햇살론|새희망홀씨|서민금융|사회연대은행|신용협동조합|신협|새마을금고|마이크로크레딧|사회적금융|신용보증재단|신보|기술보증|소상공인시장진흥공단|소진공|정책자금|지역신용보증|신용보증기금|주택금융공사")
def classify(data):
    out={}
    for g,ks in KW.items():
        rows={}
        for k in ks:
            if k not in data: continue
            if g=="사회적 금융 기관":
                for q in data[k]:
                    t=norm(txt(q))
                    if k=="구상금" and not INST_RE.search(t): continue
                    if FIN_CTX.search(t):
                        r=rows.setdefault(q['_id'],dict(q,_kws=set())); r['_kws'].add(k)
                continue
            pr=prox_re(k)
            for q in data[k]:
                t=norm(txt(q))
                if pr.search(t) and not DEBTOR.search(t):
                    r=rows.setdefault(q['_id'],dict(q,_kws=set())); r['_kws'].add(k)
        out[g]=rows
    return out
if __name__=="__main__":
    data=load(); out=classify(data)
    for g,rows in out.items():
        c=collections.Counter(k for r in rows.values() for k in r['_kws'])
        print(g,len(rows),dict(c))
