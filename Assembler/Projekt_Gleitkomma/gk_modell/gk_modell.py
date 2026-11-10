# Modell der vier UP gk_add, gk_sub, gk_mul, gk_div (dwg-Format) gegen exakte Bruchrechnung
import random
from fractions import Fraction as F
MASK26=(1<<26)-1
def dec(w):
    if w==0: return F(0)
    s=-1 if w>>32 else 1
    e=((w>>26)&63)-32; m=w&MASK26
    return s*F(m,1<<26)*(F(2)**e)
def enc_exact(x):
    """exakt gerundete dwg-Zahl (Mitte weg von 0); None bei Ueberlauf, 0 bei Unterlauf"""
    if x==0: return 0
    s=1 if x<0 else 0; a=abs(x)
    e=0
    while a>=1: a/=2; e+=1
    while a<F(1,2): a*=2; e-=1
    M=int((a*(1<<26))+F(1,2))      # floor(a*2^26+1/2), Mitte nach oben (Betrag)
    if M==1<<26: M=1<<25; e+=1
    ep=e+32
    if ep<0: return 0
    if ep>63: return None
    return (s<<32)|(ep<<26)|M
def pack(sg,ee,M):
    if M==1<<26: M=1<<25; ee+=1
    if ee<0: return 0
    if ee>63: return None
    return (sg<<32)|(ee<<26)|M
def addm(xa,xb):
    if xa==0: return xb
    if xb==0: return xa
    aa=xa&0xFFFFFFFF; bb=xb&0xFFFFFFFF
    if bb>aa: xa,xb=xb,xa; aa,bb=bb,aa
    ea=aa>>26; eb=bb>>26
    A5=(aa&MASK26)<<5; B5=(bb&MASK26)<<5
    cnt=ea-eb; st=0
    while cnt>0:
        st+=B5&1; B5>>=1; cnt-=1
    if st: B5|=1
    sa=xa>>32; sbn=xb>>32
    R=A5+B5 if sa==sbn else A5-B5
    if R==0: return 0
    ee=ea
    if R>=1<<31: R>>=1; ee+=1
    else:
        while R<1<<30: R<<=1; ee-=1
    R+=16
    if R>=1<<31: R=1<<30; ee+=1
    return pack(sa,ee,R>>5)
def subm(xa,xb):
    if xb!=0: xb^=1<<32
    return addm(xa,xb)
def mulm(xa,xb):
    if xa==0 or xb==0: return 0
    sg=(xa>>32)^(xb>>32)
    ea=(xa>>26)&63; eb=(xb>>26)&63; Ma=xa&MASK26; Mb=xb&MASK26
    ee=ea+eb-32
    Z2=((Ma<<6)*(Mb<<2))>>32          # Gruppenbefehl ohne Rundung: floor(a*b/2^32)
    if Z2>=1<<27: M=(Z2+2)>>2
    else: M=(Z2+1)>>1; ee-=1
    return pack(sg,ee,M)
def divm(xa,xb):
    if xb==0: return 'FUE'
    if xa==0: return 0
    sg=(xa>>32)^(xb>>32)
    ea=(xa>>26)&63; eb=(xb>>26)&63; Ma=xa&MASK26; Mb=xb&MASK26
    ee=ea-eb+32
    r=Ma; Y=0
    for k in range(28):
        if k>0: r<<=1
        if r>=Mb: r-=Mb; Y=2*Y+1
        else: Y=2*Y
    if Y>=1<<27: M=(Y+2)>>2; ee+=1
    else: M=(Y+1)>>1
    return pack(sg,ee,M)
def rnd_word(rng):
    if rng.random()<0.05: return 0
    s=rng.getrandbits(1)
    if rng.random()<0.5: e=rng.randint(28,36)
    else: e=rng.randint(0,63)
    M=rng.getrandbits(26)|(1<<25)
    if rng.random()<0.2: M=(1<<25)|(rng.getrandbits(3)<<(rng.randint(0,24)))  # Sonderformen
    M&=MASK26; M|=1<<25
    return (s<<32)|(e<<26)|M
if __name__=='__main__':
    rng=random.Random(8205); bad={}
    N=300000
    for i in range(N):
        a=rnd_word(rng); b=rnd_word(rng)
        if rng.random()<0.3:   # nahe beieinander (Ausloeschung, Gleichheit)
            b=a if rng.random()<0.3 else (a&~MASK26)|(rng.getrandbits(26)|(1<<25))
            if rng.random()<0.5 and b!=0: b^=1<<32
        for name,f,g in (('add',addm,lambda x,y:x+y),('sub',subm,lambda x,y:x-y),('mul',mulm,lambda x,y:x*y),('div',divm,None)):
            if name=='div':
                if dec(b)==0: ex='FUE'
                else: ex=enc_exact(dec(a)/dec(b)) if dec(a)!=0 else 0
            else: ex=enc_exact(g(dec(a),dec(b)))
            got=f(a,b)
            if got!=ex: bad.setdefault(name,[]).append((a,b,got,ex))
    for n in ('add','sub','mul','div'):
        l=bad.get(n,[]); print(n,'Abweichungen:',len(l), l[:3])
