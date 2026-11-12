import json, re, collections
from classify import norm
from kws import KW
from stats import EXP as CEXP
R=json.load(open('cases.json'))
def T(r): return norm((r.get('titleOrigin') or '')+' '+(r['body'] or ''))
DEXP = {
 "소장·소송을 당함": r"소장|피고|소송을?당|소송이?들어|소송을?걸",
 "지급명령을 받음": r"지급명령",
 "이행권고결정": r"이행권고",
 "이의신청·답변서": r"이의신청|이의제기|답변서",
 "형사 고소를 당함(사기·횡령)": r"고소(를|를당|당|장)|피고소|피의자|경찰조사|경찰출석|횡령|사기죄",
 "독촉·추심 연락": r"독촉|추심|채권추심|신용정보",
 "명의대여·명의도용": r"명의",
 "개인회생·파산·채무조정": r"회생|파산|면책|워크아웃|채무조정|새출발기금",
 "연체·미납 인정": r"연체|미납|못냈|못내|못갚|갚지못|밀려",
 "분할로 갚겠다·합의": r"분할|나눠서|합의|조정",
 "소멸시효": r"소멸시효|시효",
 "위약금·환수·잔여금 청구": r"위약금|환수|잔여|해지금|산출금",
 "억울함·금액 다툼": r"억울|부당|과다|인정하기어렵|인정할수없|금액이맞지|다투",
 "압류(통장·재산)": r"압류",
 "구상금·대위변제": r"구상|대위변제",
}
IND=["도매 및 유통","제조 및 납품업","서비스 및 전문용역","렌탈업","사회적 금융 기관"]
DTH = {
 "도매 및 유통": {"물품대금 소장·지급명령·이행권고를 받음":r"소장|지급명령|이행권고|피고|소송", "명의대여·명의만 빌려준 사업자":r"명의", "폐업·개인회생 후 남은 대금":r"폐업|회생|파산", "사기로 고소당함":r"고소|사기죄|피고소|경찰", "퇴사 직원·영업사원에게 미수금 청구":r"퇴사|영업사원|직원|영업직"},
 "서비스 및 전문용역": {"중개수수료(복비) 청구를 받음":r"중개|복비|부동산", "보험·영업 수수료 환수 청구":r"환수|보험설계|설계사|영업", "용역·작업비 청구 소송을 당함":r"용역|작업비|소장|피고|지급명령", "컨설팅·세무 수수료 다툼":r"컨설팅|세무|정책자금"},
 "렌탈업": {"렌탈사의 횡령·사기 고소":r"횡령|사기", "지급명령·소장·이행권고결정":r"지급명령|소장|이행권고|소송", "위약금·해지 산출금 청구":r"위약금|해지|산출금|잔여", "명의도용·명의대여":r"명의", "렌탈 내구제(렌탈 후 처분)":r"내구제|팔|처분|판매", "채권추심·독촉":r"추심|독촉|채권팀|신용정보|양수", "개인회생·파산·상속":r"회생|파산|상속|한정승인"},
}
out={}
for g in IND:
    out[g]={}
    for side in ["채권자","채무자"]:
        rs=[r for r in R if r['industry']==g and r['side']==side]; n=len(rs)
        if n==0: out[g][side]=dict(n=0); continue
        E = CEXP if side=="채권자" else DEXP
        ex={k:sum(1 for r in rs if re.search(p,T(r))) for k,p in E.items()}
        allterms=sorted({k for ks in KW.values() for k in ks}|{"대금","잔금","잔액","결제대금","정산금","외상","미수금","미지급금","공급대금","거래대금","기성금","계약금","선금","보수","위약금","환수금","렌탈료","렌탈비","중개수수료","복비","구상금","대출금"})
        tm={t:sum(1 for r in rs if norm(t) in T(r)) for t in allterms}
        th=None
        if side=="채무자":
            if g in DTH: th={k:sum(1 for r in rs if re.search(p,T(r))) for k,p in DTH[g].items()}
            elif g=="사회적 금융 기관": th=dict(collections.Counter(r['sub'] for r in rs))
        out[g][side]=dict(n=n,exp=ex,terms={k:v for k,v in sorted(tm.items(),key=lambda x:-x[1]) if v>0},themes=th,
            kw=dict(collections.Counter(k for r in rs for k in r['kws'])))
        print('==',g,side,n,'| exp',{k:v for k,v in sorted(ex.items(),key=lambda x:-x[1])[:9]},'| th',th,'| terms',list(out[g][side]['terms'].items())[:8])
json.dump(out,open('stats2.json','w'),ensure_ascii=False)
