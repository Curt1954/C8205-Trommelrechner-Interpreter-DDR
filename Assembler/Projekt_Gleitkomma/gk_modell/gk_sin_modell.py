# Bitgenaues Modell des UP gk_sin (Projekt_Gleitkomma/gk_trigonomie_sin.asm) auf Grundlage von gk_modell (gk_add, gk_sub, gk_mul).
# Zweck: Konstanten der Tabellen und Sollwerte des Testlaufs; Vergleich gegen die exakte Sinusfunktion (Reihe mit 60 Dezimalstellen).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gk_modell import dec, enc_exact, addm, subm, mulm
from fractions import Fraction as F
from decimal import Decimal, getcontext
getcontext().prec = 80
PI_D = Decimal('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899')
PI = F(PI_D); HP = PI/2
MASK26 = (1 << 26) - 1
def kuerze(x, bits):                          # auf 'bits' Mantissenbits abschneiden (Cody-Waite)
    e = 0; a = abs(x)
    while a >= 1: a /= 2; e += 1
    while a < F(1, 2): a *= 2; e -= 1
    return F(int(a*(1 << bits)), 1 << bits) * F(2)**e
P1 = kuerze(HP, 13); P2 = kuerze(HP-P1, 13); P3 = enc_exact(HP-P1-P2)
PW = [enc_exact(P1), enc_exact(P2), P3]            # pi/2 = P1 + P2 + P3 (P1, P2 mit 13 Bit, damit n*P1, n*P2 fuer n < 4096 exakt sind)
C2PI = enc_exact(2/PI)                             # 2/pi
C225 = enc_exact(F(2**25))                         # 2^25: Additionskonstante, rundet auf ganze Zahlen
W0 = (58 << 26) + (1 << 25)                        # Wort von 2^25 (Exponent 58, Mantisse 2^25)
fakt = lambda n: F(__import__('math').factorial(n))
SINT = [enc_exact(c) for c in (1/fakt(9), -1/fakt(7), 1/fakt(5), -1/fakt(3), F(1))]               # sin r = r * S(r^2), S ab hoechster Potenz
COST = [enc_exact(c) for c in (-1/fakt(10), 1/fakt(8), -1/fakt(6), 1/fakt(4), -1/fakt(2), F(1))]  # cos r = C(r^2)
def sin_modell(x, kos=False):
    """liefert das Ergebniswort oder 'FUE'; kos=True: Kosinus (Einsprung gk_cos: |x|, Vorzeichen von x ohne Wirkung, Quadrant q + 1)"""
    neg = 0 if kos else x >> 32; a = x & 0o37777777777
    t = mulm(a, C2PI)
    w = addm(t, C225)
    if w - W0 - 4096 >= 0 or w < W0: return 'FUE'
    q = (w + (1 if kos else 0)) & 3
    nf = subm(w, C225)
    r = a
    for p in PW:
        r = subm(r, mulm(nf, p))
    y = mulm(r, r)
    tab = COST if q & 1 else SINT
    p = tab[0]
    for c in tab[1:]:
        p = addm(mulm(p, y), c)
    res = p if q & 1 else mulm(p, r)
    if ((q >> 1) + neg) & 1 and res != 0: res ^= 1 << 32
    return res
def cos_modell(x):
    """Kosinus wie gk_cos: gleiche Argumentreduktion wie gk_sin, Quadrant um 1 weiter, Vorzeichen von x ohne Wirkung"""
    return sin_modell(x, True)
if __name__ == '__main__':
    import random
    def ex(x):                                      # exakter Sinus (Taylorreihe, hohe Genauigkeit), gerundet als dwg
        v = Decimal(dec(x).numerator)/Decimal(dec(x).denominator)
        k = int(v/(PI_D*2)); v -= k*2*PI_D
        s = Decimal(0); term = v; n = 1
        while abs(term) > Decimal(10)**-70:
            s += term; term = -term*v*v/((n+1)*(n+2)); n += 2
        return s
    rng = random.Random(8205); worst = 0; wx = None
    for i in range(20000):
        e = rng.choice([rng.randint(20, 40), rng.randint(32, 45)])
        x = (rng.getrandbits(1) << 32) | (e << 26) | (rng.getrandbits(26) | (1 << 25))
        if rng.random() < 0.05: x = 0
        if abs(dec(x)) >= 6000: continue                 # Bereich des Modells: |x| < 4096*pi/2, Pruefung hier bis 6000
        r = sin_modell(x)
        if r == 'FUE': continue
        exv = ex(x); got = dec(r)
        err = abs(F(got) - F(exv)) if exv != 0 else abs(F(got))
        ulp = F(1, 1 << 26) * (F(2)**(((r >> 26) & 63)-32)) if r else F(1, 1 << 58)
        u = float(err/ulp) if r else float(err*(1 << 58))
        if u > worst: worst = u; wx = (x, float(dec(x)), r, float(got), float(exv))
    print('groesster Fehler in Einheiten der letzten Stelle:', worst, wx)
    # Kosinus (gk_cos): gleiche Pruefung gegen die exakte Kosinusreihe
    def exc(x):
        v = Decimal(dec(x).numerator)/Decimal(dec(x).denominator)
        k = int(v/(PI_D*2)); v -= k*2*PI_D
        s = Decimal(0); term = Decimal(1); n = 0
        while abs(term) > Decimal(10)**-70:
            s += term; term = -term*v*v/((n+1)*(n+2)); n += 2
        return s
    rng = random.Random(8206); worst = 0; wx = None
    for i in range(20000):
        e = rng.choice([rng.randint(20, 40), rng.randint(32, 45)])
        x = (rng.getrandbits(1) << 32) | (e << 26) | (rng.getrandbits(26) | (1 << 25))
        if rng.random() < 0.05: x = 0
        if abs(dec(x)) >= 6000: continue
        r = cos_modell(x)
        if r == 'FUE': continue
        exv = exc(x); got = dec(r)
        err = abs(F(got) - F(exv)) if exv != 0 else abs(F(got))
        ulp = F(1, 1 << 26) * (F(2)**(((r >> 26) & 63)-32)) if r else F(1, 1 << 58)
        u = float(err/ulp) if r else float(err*(1 << 58))
        if u > worst: worst = u; wx = (x, float(dec(x)), r, float(got), float(exv))
    print('Kosinus: groesster Fehler in Einheiten der letzten Stelle:', worst, wx)
