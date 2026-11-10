#!/usr/bin/env python3
"""gk_math_op_gen.py -- erzeugt Assembler/Projekt_Gleitkomma/gk_math_op.asm (reiner Python-Generator, kein c82gen).
Die vier UP kommen aus dem Makro GK_MATH (c82ass.makros); hier stehen nur die Aufrufe (Text UP); erzeugt werden Falltabelle, Ergebniszellen und der ;#PRUEFE-Block.
Sollwerte nur aus enc_exact (exakte Bruchrechnung, gk_modell/gk_modell.py), nicht aus dem Verfahren.
Aufruf (Projektstamm): python3 -I Assembler/Projekt_Gleitkomma/gen/gk_math_op_gen.py
"""
import os, sys
from fractions import Fraction as F
hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', 'gk_modell'))
from gk_modell import enc_exact, dec
import fall_tabelle as ft

EXTRA = [  # (Beschreibung, a, b) - Zusatzfaelle (Fraction-Strings)
 ("0,75 und 0,75", "3/4", "3/4"),
 ("1 und 2^-27", "1", "1/134217728"),
 ("1 und 2^-30 (d = 30)", "1", "1/1073741824"),
 ("2^-30 und 1 (Tausch)", "1/1073741824", "1"),
 ("3 und -7", "3", "-7"),
 ("0,5 und 0,5", "1/2", "1/2"),
 ("1E-9 und 1E9", "1/1000000000", "1000000000"),
 ("5 und 1", "5", "1"),
 ("1 und 10", "1", "10"),
 ("2/3 und 1/3", "2/3", "1/3"),
 ("2^-30 und 2^-30 (mul Unterlauf)", "1/1073741824", "1/1073741824"),
 ("-2^-30 und 2^-31", "-1/1073741824", "1/2147483648"),
]
def w(x): return enc_exact(F(x))
def faelle():
    L = [(t, w(a), w(b)) for t, a, b in ft.FAELLE] + ft.zufall()
    L += [(t, w(a), w(b)) for t, a, b in EXTRA]
    L.append(('5 und 0 (div: kuenstlicher FUE)', w('5'), 0))
    return L

UP = r'''
; ===== UP gk_add, gk_sub, gk_mul, gk_div (dwg-Format) als ein gemeinsames Makro GK_MATH (Assembler/Sourcecode/c82ass.makros, Beschreibung dort); Eingabe R1 (7773) und R2 (7776), Ergebnis im AC; R1, R2 bleiben unveraendert.
; Das Makro erzeugt jeden Teil des Codes nur einmal, auch bei mehreren Aufrufen und gleich mit welchem Parameter: jeder Aufruf legt nur an, was noch fehlt (Einsprung, Kern, gemeinsamer Teil).
                start                ; Zaehlung beginnt bei 0000 (relativ): die UP ab 0000, das Testhauptprogramm ab 02000
                GK_MATH add          ; gk_add: R1 + R2 (erzeugt Kern der Addition und gemeinsamen Teil)
                GK_MATH sub          ; gk_sub: R1 - R2 (nur der Einsprung, der Kern ist schon da)
                GK_MATH mul          ; gk_mul: R1 * R2 (Kern von Multiplikation und Division)
                GK_MATH div          ; gk_div: R1 / R2 (nur der Einsprung)
                GK_MATH alle         ; Wiederholung: erzeugt nichts, denn alle vier UP sind schon da (ein doppelter Code wuerde als doppelte Marke scheitern)
                GK_MATH mul          ; Wiederholung: erzeugt nichts
'''

def bauen(L=None):
    if L is None: L = faelle()
    n = len(L)
    soll = {'add': [], 'sub': [], 'mul': [], 'div': []}
    for t, wa, wb in L:
        fa, fb = dec(wa), dec(wb)
        soll['add'].append(enc_exact(fa+fb)); soll['sub'].append(enc_exact(fa-fb)); soll['mul'].append(enc_exact(fa*fb))
        soll['div'].append(None if fb == 0 else (0 if fa == 0 else enc_exact(fa/fb)))
    for k in soll:
        for i, v in enumerate(soll[k]):
            if v is None and not (k == 'div' and i == n-1):
                raise SystemExit('Ueberlauf im Fall %d (%s): Fall aendern' % (i+1, k))
    RES = 0o3000
    BZ_FUE = 0o201   # gkm_fue + 3 (aus gk_math_op.sym); aendert sich mit der Lage der UP (Makro GK_MATH)
    kopf = '''; gk_math_op.asm  --  Projekt_Gleitkomma: Gleitkomma-Grundrechenarten (dwg-Format) gk_add, gk_sub, gk_mul, gk_div
; ERZEUGT von Assembler/Projekt_Gleitkomma/gen/gk_math_op_gen.py (Aenderungen nur dort; .py und .asm zusammen liefern).
; Stand 08.11.2026. Siehe Datei aufgabe.
;
; Format dwg (wie gk_ausgabe): z0 Vorzeichen, z1..z6 Exponent e+32, z7..z32 Mantisse M (2^25 <= M < 2^26), Wert = +-M/2^26 * 2^e; die Zahl 0 ist das Wort 0.
; Aufruf:  R1 (Zelle 7773) und R2 (Zelle 7776) laden, dann  025 gk_add | gk_sub | gk_mul | gk_div ;  Ergebnis im AC (dwg), R1 und R2 bleiben unveraendert.
;   gk_add: R1 + R2   gk_sub: R1 - R2   gk_mul: R1 * R2   gk_div: R1 / R2.  Die Rueckkehr laeuft ueber die gemeinsame Zelle gk_rueck (Festlegung 010).
;   Die UP rufen kein weiteres UP auf (unterste Ebene, R1/R2 ueberschreibt niemand). Zerstoert: AC, eigene Arbeitszellen, die Arbeitsspur 7640 bis 7677. R3 bleibt unberuehrt.
; ANNAHMEN (vom Inhaber am 08.11.2026 bestaetigt: A4, A8, A9, A10 und der Aufruf mit 025): A4 Division durch 0 erzeugt kuenstlich FUE (AC := 2^32-1, + 1, Halt beim naechsten Befehl; auch 0/0).
;   A8 Exponentenunterlauf (Ergebnis kleiner als 2^-33): Ergebnis 0.  A9 Exponentenueberlauf (Ergebnis >= 2^31): kuenstlicher FUE wie bei Division durch 0.
;   A10 Rundung: Mitte weg von 0 (Betrag); die Ergebnisse stimmen bitgenau mit der exakten Bruchrechnung ueberein (Modell gk_modell/gk_modell.py, je 300000 Zufallsfaelle ohne Abweichung).
; VERFAHREN: Addition/Subtraktion: Null-Faelle; Betraege vergleichen, ggf. tauschen; Mantissen mit 5 Schutzbits, die kleinere mit Klebebit nach rechts angleichen;
;   gleiche Vorzeichen addieren, sonst subtrahieren; normieren; Rundung (R+16)>>5.  Multiplikation: Z = floor(Ma*Mb/2^24) mit Gruppenbefehlen (440, 472, 412 auf 7640).
;   Division: 28 Schritte bitweise (Rest/Divisor).  Mantisse Z bzw. Y wird gemeinsam gerundet (mq), dann gepackt (gk_pk).
; Testhauptprogramm ab relativ 02000: Falltabelle fall (%d Faelle, Paare a,b ab 02400), Operationstabelle optab (02300); die Ergebnisse stehen op-weise nacheinander
;   ab 03000: add 03000.., sub, mul, div (%d Zellen je Operation). Der letzte Fall 5/0 beendet den Lauf mit dem kuenstlichen Ueberlauf in gk_div (Halt).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
; Test: Tastenfolge H M+ E M- R (E zaehlt 1 dazu: Start bei 02000).
''' % (n, n)
    haupt = '''
; ===== TESTHAUPTPROGRAMM, relativ ab 02000. Fuer den Routinebetrieb den Abschnitt bis 'ENDE TESTHAUPTPROGRAMM' entfernen.
                equ     02000        ; relative Adresse 02000
haupt:          211     @optab       ; Zeiger auf die Operationstabelle
                240     oz           ; merken
                211     @res         ; Zeiger auf die Ergebniszellen
                240     rz           ; merken
op_l:           211     oz           ; Zeiger
                251     0            ; AC := Aufrufbefehl (025 gk_xxx)
                240     cl           ; in die Aufrufzelle
                211     @fall        ; Zeiger auf die Falltabelle
                240     fz           ; merken
fa_l:           211     fz           ; Zeiger auf a
                251     0            ; AC := a
                240     r1           ; nach R1
                211     fz           ; Zeiger
                210     #01000       ; auf b
                251     0            ; AC := b
                240     r2           ; nach R2
cl:             db      1            ; Laufzeit: 025 gk_xxx, AC := Ergebnis
                240     tm           ; Ergebnis merken
                211     rz           ; Zeiger auf die Ergebniszelle
                210     #0240        ; + Speicherbefehl
                240     sp           ; auf die naechste Zelle legen
                211     tm           ; Ergebnis
sp:             db      1            ; Laufzeit: 240 res_i
                ZEIGER_NAECHST rz    ; naechste Ergebniszelle
                ZEIGER_NAECHST fz    ; a weiter
                ZEIGER_NAECHST fz    ; b weiter
                211     fz           ; Zeiger
                220     @fallend     ; Zeiger - Ende der Falltabelle
                040     fa_l         ; kleiner (negativ): naechster Fall
                ZEIGER_NAECHST oz    ; naechste Operation
                211     oz           ; Zeiger
                220     @optabend    ; Zeiger - Ende der Operationstabelle
                040     op_l         ; kleiner (negativ): naechste Operation
                020     0            ; Halt (nicht erreicht: der letzte Fall 5/0 endet im FUE-Halt)
oz:             db      1            ; Zeiger Operationstabelle
rz:             db      1            ; Zeiger Ergebniszelle
fz:             db      1            ; Zeiger Falltabelle
tm:             db      1            ; Ergebnis (Zwischenspeicher)
'''
    tab = '\n                equ     02300        ; Operationstabelle\noptab:          025     gk_add       ; Operation 1: Addition\n                025     gk_sub       ; Operation 2: Subtraktion\n                025     gk_mul       ; Operation 3: Multiplikation\n                025     gk_div       ; Operation 4: Division\noptabend:       dw      0            ; Ende\n'
    tab += '\n                equ     02400        ; Falltabelle: Paare a, b (dwg)\nfall:\n'
    for i, (t, wa, wb) in enumerate(L):
        tt = t.split(' und ')
        tab += '                dw      0%011o     ; Fall %d a  (%s)\n' % (wa, i+1, tt[0])
        tab += '                dw      0%011o     ; Fall %d b  (%s)\n' % (wb, i+1, tt[1] if len(tt) > 1 else t)
    tab += 'fallend:       dw      0            ; Ende\n'
    tab += '\n                equ     0%o        ; Ergebniszellen: add, sub, mul, div je %d Zellen\nres:            db      %d\n' % (RES, n, 4*n)
    tab += '''
; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)

; Sollwerte aus exakter Bruchrechnung (gk_modell.enc_exact), nicht aus dem Verfahren. Fall n, Operation o: Zelle 03000 + (o-1)*%d + (n-1).
;#PRUEFE-START
''' % n
    pr = '; BZ=%04o AC=40000000000 FUE=1 US=0   # Halt im kuenstlichen Ueberlauf von gk_div (Fall 5/0), BZ = Adresse des Befehls hinter dem 210 in gk_fue + 1\n' % BZ_FUE
    for oi, k in enumerate(('add', 'sub', 'mul', 'div')):
        for i, v in enumerate(soll[k]):
            if v is None: continue
            pr += '; %04o: %011o   # %s Fall %d\n' % (RES + oi*n + i, v, k, i+1)
    pr += ';#PRUEFE-ENDE\n'
    return kopf + UP + haupt + tab + pr, n, soll

if __name__ == '__main__':
    txt, n, soll = bauen()
    ziel = os.path.join(hier, '..', 'gk_math_op.asm')
    open(ziel, 'w', encoding='utf-8', newline='\n').write(txt)
    print('geschrieben', os.path.normpath(ziel), n, 'Faelle')
