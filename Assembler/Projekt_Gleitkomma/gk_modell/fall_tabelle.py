# erzeugt Falltabelle (dw-Zeilen) und Sollwerte aus exakter Bruchrechnung (enc_exact), unabhaengig vom Verfahren
from fractions import Fraction as F
import random, json
from gk_modell import enc_exact, dec
def w(x): return enc_exact(F(x))
FAELLE=[ # (Beschreibung, a, b) a,b als Fraction-Strings
 ("1 und 1",                "1","1"),
 ("1,5 und 2,25",           "3/2","9/4"),
 ("-3 und 0,5",             "-3","1/2"),
 ("7 und -7",               "7","-7"),
 ("5E8 und 1,25 (d gross)",  "500000000","5/4"),
 ("1 und -3E-8 (Schutzbits)","1","-3/100000000"),
 ("1 und 2^-26 (Mitte)",    "1","1/67108864"),
 ("-1 und -2^-26 (Mitte)",  "-1","-1/67108864"),
 ("1 und -2^-26",           "1","-1/67108864"),
 ("1/3 und 2/3",            "1/3","2/3"),
 ("0 und 5",                "0","5"),
 ("2^-20 und 2^-20",        "1/1048576","1/1048576"),
 ("1,0000001 und 0,9999999","10000001/10000000","9999999/10000000"),
 ("123456,789 und -0,0123", "123456789/1000","-123/10000"),
 ("-2^28 und 3",            "-268435456","3"),
]
def zufall():
    r=random.Random(82050); out=[]
    for i in range(6):
        ws=[]
        for _ in range(2):
            e=r.randint(28,36); M=r.getrandbits(26)|(1<<25); sg=r.getrandbits(1)
            ws.append((sg<<32)|(e<<26)|M)
        out.append((f"zufall {i+1}",ws[0],ws[1]))
    return out
def tab():
    z=[];soll={'add':[],'sub':[],'mul':[],'div':[]}
    L=[(t,w(a),w(b)) for t,a,b in FAELLE]+zufall()+[('5 und 0 (div: kuenstlicher FUE)',w('5'),0)]
    for t,wa,wb in L:
        fa,fb=dec(wa),dec(wb)
        z.append((t,wa,wb))
        soll['add'].append(enc_exact(fa+fb)); soll['sub'].append(enc_exact(fa-fb))
        soll['mul'].append(enc_exact(fa*fb))
        soll['div'].append(None if fb==0 else (0 if fa==0 else enc_exact(fa/fb)))
    return z,soll
if __name__=='__main__':
    z,s=tab()
    for t,a,b in z: print(f"                dw      0{a:011o}     ; a = {t.split(' und ')[0] if ' und ' in t else t}")
    for k in s: print(k,[None if v is None else f"{v:011o}" for v in s[k]])
