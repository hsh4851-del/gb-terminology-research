import json, re, collections
from classify import norm
from kws import KW
R=json.load(open('cases.json'))
def T(r): return norm((r['title'] or '')+(r['body'] or ''))
EXP = {
 # 상황 묘사 표현
 "미지급": r"미지급", "못 받고 있다/받지 못했다": r"못받|받지못|못받았|지급받지못", "미수(금)": r"미수", "미납": r"미납", "연체": r"연체", "체불": r"체불",
 "차일피일·계속 미룸": r"미루|미뤄|차일피일|지연", "연락두절·잠수": r"연락(이)?두절|잠수|연락(이|을|도)?(안|되지않|받지않)|전화(를|도)?(안|받지)", 
 "준다준다·곧 주겠다": r"준다준다|주겠다|준다고|주기로|갚겠다", "돈이 없다·사정이 어렵다": r"돈이없|자금사정|사정이어렵|형편|경영난|경영악화|돈없",
 "폐업": r"폐업", "부도·파산·회생": r"부도|파산|회생", "떼였다·먹튀": r"떼였|떼먹|떼어먹|먹튀",
 # 문제가 된 증빙
 "계약서 없음·구두계약": r"계약서(가|는|를)?(없|미작성|작성하지|안썼|쓰지)|구두(로|계약|상)", "세금계산서": r"세금계산서|계산서", "거래명세서·발주서·견적서": r"거래명세|발주서|발주|견적서", "카톡·문자·녹취": r"카톡|카카오톡|문자|녹취|녹음",
 # 원하는 조치
 "내용증명": r"내용증명", "지급명령": r"지급명령", "소액소송·민사소송": r"소액|민사소송|소송", "가압류·압류": r"가압류|압류", "강제집행·재산명시": r"강제집행|재산명시|재산조회|추심명령", "사기 고소(형사)": r"사기|고소|형사", "공증·각서·지불각서": r"공증|각서|지불확인|지급약정|차용증", "지연이자·지연손해금": r"지연이자|지연손해금|이자", "대표자 개인책임": r"대표(자|이사)?개인|개인책임|대표에게",
}
IND=["도매 및 유통","렌탈업","제조 및 납품업","서비스 및 전문용역","사회적 금융 기관"]
out={}
for g in (IND if __name__=="__main__" else []):
    rs=[r for r in R if r['industry']==g and r['side']=='채권자'] or [r for r in R if r['industry']==g and r['side']=='채무자']
    n=len(rs)
    ex={k:sum(1 for r in rs if re.search(p,T(r))) for k,p in EXP.items()}
    kwc=collections.Counter(k for r in rs for k in r['kws'])
    yrs=collections.Counter(r['date'][:4] for r in rs)
    # money-term usage: count every KW term (any industry) appearing in texts
    allterms=sorted({k for ks in KW.values() for k in ks}|{"대금","잔금","잔액","결제대금","정산금","외상","미수금","미지급금","공급대금","거래대금","기성금","계약금","선금","보수"})
    tm={t:sum(1 for r in rs if norm(t) in T(r)) for t in allterms}
    out[g]=dict(n=n,exp=ex,kw=dict(kwc),years=dict(sorted(yrs.items())),terms={k:v for k,v in sorted(tm.items(),key=lambda x:-x[1]) if v>0})
    print('=====',g,n); print(' years',dict(sorted(yrs.items()))); print(' kw',dict(kwc.most_common()))
    print(' exp',{k:f"{v}({v*100//n}%)" for k,v in ex.items()})
    print(' terms',list(out[g]['terms'].items())[:22])
json.dump(out,open('stats.json','w'),ensure_ascii=False)
