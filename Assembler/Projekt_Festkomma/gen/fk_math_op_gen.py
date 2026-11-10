#!/usr/bin/env python3
"""fk_math_op_gen.py -- erzeugt Assembler/Projekt_Festkomma/fk_math_op.asm (reiner Python-Generator, kein c82gen).
Vier Festkomma-UP fk_add, fk_sub, fk_mul, fk_div (dwf-Format) als Makro FK_MATH (c82ass.makros) analog zu gk_math_op (Projekt_Gleitkomma) plus Testhauptprogramm.
Sollwerte nur aus der exakten Bruchrechnung (Fraction), nicht aus dem Verfahren.
Aufruf (Projektstamm): python3 -I Assembler/Projekt_Festkomma/gen/fk_math_op_gen.py
"""
import os, random
from fractions import Fraction as F
hier = os.path.dirname(os.path.abspath(__file__))
M33 = (1 << 33) - 1
LO, HI = -(1 << 32), (1 << 32) - 1          # Wortbereich (Zweierkomplement, 33 Bit); Wert = Wort / 2^32

def rnd(q):                                   # Rundung auf ganze Zahl, Mitte weg von 0
    s = -1 if q < 0 else 1
    q = abs(q)
    return s * ((q.numerator * 2 + q.denominator) // (2 * q.denominator))

def soll(op, a, b):                           # a, b als Worte (ganze Zahlen); None = Ueberlauf
    if op == 'add': r = a + b
    elif op == 'sub': r = a - b
    elif op == 'mul': r = rnd(F(a * b, 1 << 32))
    else:
        if b == 0: return None
        r = rnd(F(a * (1 << 32), b))
    return r if LO <= r <= HI else None

def fall_listen():
    R = random.Random(8205)
    h = 1 << 31
    A = [(0, 0), (-h, h), (h, h - 1), (0, -1 << 32), (3, -3), (HI, -HI), (HI, 0), (-1 << 32, 0), (-1 << 32, HI),
         (1, 1), (-h, -h), (h, -h + 1)]
    S = [(0, 0), (HI, HI), (-1 << 32, -1 << 32), (-h, h), (h, -h + 1), (0, HI), (HI, 1), (-1 << 32, -HI), (7, -9)]
    M = [(0, 5), (5, 0), (1 << 32 - 1, 1 << 32 - 1), (-1 << 32, 7), (7, -1 << 32), (-1 << 32, HI), (HI, HI), (1, h), (1, -h), (-1, h),
         (-1, -h), (3, h), (h, h), (-h, h), (3 << 30, 3 << 30), (-1 << 32, 0), (HI, -HI)]
    D = [(0, 7), (5, -1 << 32), (-HI, -1 << 32), (-h, h), (h, -h), (1, HI), (-1, HI), (HI - 1, HI), (h, 3 << 30), (1, 3), (-1, 3),
         (3, 7), (1 << 31, -1 << 32), (-5, 7)]
    for _ in range(8):
        a, b = R.randrange(-h + 1, h), R.randrange(-h + 1, h); A.append((a, b)); S.append((a, b))
    for _ in range(14):
        M.append((R.randrange(LO, HI + 1), R.randrange(LO, HI + 1)))
    for _ in range(14):
        b = R.choice((-1, 1)) * R.randrange(2, HI)
        a = R.choice((-1, 1)) * R.randrange(0, abs(b))
        D.append((a, b))
    return [('add', A), ('sub', S), ('mul', M), ('div', D)]

def ws(x): return '0%011o' % (x & M33)

KOPF = '''; fk_math_op.asm  --  Projekt_Festkomma: Festkomma-Grundrechenarten (dwf-Format) fk_add, fk_sub, fk_mul, fk_div
; ERZEUGT von Assembler/Projekt_Festkomma/gen/fk_math_op_gen.py (Aenderungen nur dort; .py und .asm zusammen liefern).
; Stand 08.11.2026. Siehe Datei aufgabe. Analog zu Projekt_Gleitkomma/gk_math_op.asm: die vier UP kommen aus dem Makro FK_MATH (Assembler/Sourcecode/c82ass.makros), hier stehen nur die Aufrufe und das Testhauptprogramm.
;
; Format dwf (wie fk_ausgabe): Wort = x * 2^32, Zweierkomplement 33 Bit, Komma zwischen z0 und z1, Bereich -1 (Wort 040000000000) bis 1 - 2^-32 (Wort 037777777777).
; Aufruf:  R1 (Zelle 7773) und R2 (Zelle 7776) laden, dann  025 fk_add | fk_sub | fk_mul | fk_div ;  Ergebnis im AC (dwf), R1 und R2 bleiben unveraendert.
;   fk_add: R1 + R2   fk_sub: R1 - R2   fk_mul: R1 * R2   fk_div: R1 / R2.  Die Rueckkehr laeuft ueber die gemeinsame Zelle fkm_rueck (Festlegung 010).
;   Die UP rufen kein weiteres UP auf (unterste Ebene, Festlegung 031). Zerstoert: AC, eigene Arbeitszellen, die Arbeitsspur 7640 bis 7677 (nur fk_mul). R3 bleibt unberuehrt.
; ANNAHMEN (offen, bitte bestaetigen):
;   D1 Ueberlauf (Ergebnis ausserhalb -1 bis 1 - 2^-32): bei fk_add und fk_sub, und bei fk_mul mit (-1) * (-1) und fk_div mit b = -1, a = -1, erzeugt die Maschine selbst den
;      Ueberlauf (FUE, Halt beim naechsten Befehl).  D2 Division durch 0 (auch 0/0) und Quotient mit Betrag >= 1 (|a| >= |b|, ausser a = -b: dann -1): kuenstlicher Ueberlauf
;      (AC := 2^32-1, + 1, Halt beim naechsten Befehl) wie bei gk_div (A4).  D3 Rundung bei fk_mul und fk_div: Mitte weg von 0 (Betrag), die Ergebnisse stimmen bitgenau mit der
;      exakten Bruchrechnung ueberein (Sollwerte der Tests).  D4 Das Ergebnis der Division a/b mit a = -b ist -1 (Wort 040000000000), mit a = b Ueberlauf.
; VERFAHREN: Addition und Subtraktion: ein Befehl (210, 220).  Multiplikation und Division: Betraege und Vorzeichenmerker sg; die Faelle 0 und -1 vorab (a * (-1) = -a, a / (-1) = -a);
;   Multiplikation: Betraege 32 Bit, Gruppenbefehle 440, 472, 412 auf 7640 (Programmieranleitung 6.1.1) mit Rundungskonstante 2^31 (halbe letzte Stelle);
;   Division: 32 Schritte bitweise (t = |b| - r; r >= t: Bit 1, r := r - t; sonst Bit 0, r := 2r; so bleibt jeder Wert unter 2^32), ein 33. Schritt ergibt das Rundungsbit; Ergebnis dann mit Vorzeichen.
; Testhauptprogramm ab relativ 02000: Aufgabenliste jobs (je Aufgabe 3 Zellen: Aufrufbefehl 025 fk_xxx, a, b; ab 02400, %d Aufgaben, nach Operationen add, sub, mul, div),
;   Ergebnisse in derselben Reihenfolge ab 03100 (eine Zelle je Aufgabe). Die letzte Aufgabe 0,25 / 0 beendet den Lauf mit dem kuenstlichen Ueberlauf in fk_div (Halt).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
; Test: Tastenfolge H M+ E M- R (E zaehlt 1 dazu: Start bei 02000).

; ===== UP fk_add, fk_sub, fk_mul, fk_div (dwf-Format) als ein gemeinsames Makro FK_MATH (Assembler/Sourcecode/c82ass.makros, Beschreibung dort); Eingabe R1 (7773) und R2 (7776), Ergebnis im AC.
; Das Makro erzeugt jeden Teil des Codes nur einmal, auch bei mehreren Aufrufen und gleich mit welchem Parameter: jeder Aufruf legt nur an, was noch fehlt (Einsprung, Kern, gemeinsamer Teil).
                start                ; Zaehlung beginnt bei 0000 (relativ): die UP ab 0000, das Testhauptprogramm ab 02000
                FK_MATH add          ; fk_add: R1 + R2 (erzeugt den Einsprung und den gemeinsamen Teil)
                FK_MATH sub          ; fk_sub: R1 - R2 (nur der Einsprung)
                FK_MATH mul          ; fk_mul: R1 * R2 (Kern von Multiplikation und Division)
                FK_MATH div          ; fk_div: R1 / R2 (nur der Einsprung)
                FK_MATH alle         ; Wiederholung: erzeugt nichts, denn alle vier UP sind schon da (ein doppelter Code wuerde als doppelte Marke scheitern)
                FK_MATH mul          ; Wiederholung: erzeugt nichts
'''

HAUPT = '''
; ===== TESTHAUPTPROGRAMM, relativ ab 02000. Fuer den Routinebetrieb den Abschnitt bis 'ENDE TESTHAUPTPROGRAMM' entfernen.
                equ     02000        ; relative Adresse 02000
haupt:          211     @jobs        ; Zeiger auf die Aufgabenliste
                240     jz           ; merken
                211     @res         ; Zeiger auf die Ergebniszellen
                240     rz           ; merken
job_l:          211     jz           ; Zeiger auf den Aufrufbefehl
                251     0            ; AC := Aufrufbefehl (025 fk_xxx)
                240     cl           ; in die Aufrufzelle
                ZEIGER_NAECHST jz    ; Zeiger auf a
                211     jz           ; Zeiger
                251     0            ; AC := a
                240     r1           ; nach R1
                ZEIGER_NAECHST jz    ; Zeiger auf b
                211     jz           ; Zeiger
                251     0            ; AC := b
                240     r2           ; nach R2
cl:             db      1            ; Laufzeit: 025 fk_xxx, AC := Ergebnis
                240     tm           ; Ergebnis merken
                211     rz           ; Zeiger auf die Ergebniszelle
                210     #0240        ; + Speicherbefehl
                240     sp           ; auf die naechste Zelle legen
                211     tm           ; Ergebnis
sp:             db      1            ; Laufzeit: 240 res_i
                ZEIGER_NAECHST rz    ; naechste Ergebniszelle
                ZEIGER_NAECHST jz    ; naechste Aufgabe
                211     jz           ; Zeiger
                220     @jobsend     ; Zeiger - Ende der Aufgabenliste
                040     job_l        ; kleiner (negativ): naechste Aufgabe
                020     0            ; Halt (nicht erreicht: die letzte Aufgabe 0,25 / 0 endet im FUE-Halt)
jz:             db      1            ; Zeiger Aufgabenliste
rz:             db      1            ; Zeiger Ergebniszelle
tm:             db      1            ; Ergebnis (Zwischenspeicher)
'''

def bauen(bz_fue):
    gruppen = fall_listen()
    jobs, erg = [], []
    for op, L in gruppen:
        for a, b in L:
            r = soll(op, a, b)
            if r is None: raise SystemExit('Ueberlauf in %s %d %d: Fall aendern' % (op, a, b))
            jobs.append((op, a, b)); erg.append(r)
    n = len(jobs)
    jobs.append(('div', 1 << 30, 0))        # letzte Aufgabe: Division durch 0, kuenstlicher FUE (Halt)
    txt = KOPF % (n + 1) + HAUPT
    txt += '\n                equ     02400        ; Aufgabenliste: je Aufgabe Aufrufbefehl, a, b (dwf)\njobs:\n'
    for i, (op, a, b) in enumerate(jobs):
        v = lambda x: '%.10g' % (x / 2.0**32)
        txt += '                025     fk_%s       ; Aufgabe %d: %s\n' % (op, i + 1, op)
        txt += '                dw      %s     ; Aufgabe %d a  (%s)\n' % (ws(a), i + 1, v(a))
        txt += '                dw      %s     ; Aufgabe %d b  (%s)\n' % (ws(b), i + 1, v(b))
    txt += 'jobsend:       dw      0            ; Ende\n'
    txt += '\n                equ     03100        ; Ergebniszellen: eine je Aufgabe, in der Reihenfolge der Liste\nres:            db      %d\n' % (n + 1)
    txt += '''
; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)

; Sollwerte aus exakter Bruchrechnung (Fraction in fk_math_op_gen.py), nicht aus dem Verfahren. Aufgabe i: Zelle 03100 + (i-1).
;#PRUEFE-START
'''
    txt += '; BZ=%04o AC=40000000000 FUE=1 US=0   # Halt im kuenstlichen Ueberlauf von fk_div (Aufgabe %d, 0,25 / 0), BZ = fkm_fue + 3\n' % (bz_fue, n + 1)
    for i, r in enumerate(erg):
        txt += '; %04o: %s   # %s Aufgabe %d\n' % (0o3100 + i, ws(r)[1:], jobs[i][0], i + 1)
    txt += ';#PRUEFE-ENDE\n'
    return txt

if __name__ == '__main__':
    BZ_FUE = 0o155   # fkm_fue (0152 laut fk_math_op.sym) + 3
    ziel = os.path.join(hier, '..', 'fk_math_op.asm')
    open(ziel, 'w', encoding='utf-8', newline='\n').write(bauen(BZ_FUE))
    print('geschrieben', os.path.normpath(ziel))
