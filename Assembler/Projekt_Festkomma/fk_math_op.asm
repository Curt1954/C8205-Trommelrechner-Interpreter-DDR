; fk_math_op.asm  --  Projekt_Festkomma: Festkomma-Grundrechenarten (dwf-Format) fk_add, fk_sub, fk_mul, fk_div
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
; Testhauptprogramm ab relativ 02000: Aufgabenliste jobs (je Aufgabe 3 Zellen: Aufrufbefehl 025 fk_xxx, a, b; ab 02400, 97 Aufgaben, nach Operationen add, sub, mul, div),
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

                equ     02400        ; Aufgabenliste: je Aufgabe Aufrufbefehl, a, b (dwf)
jobs:
                025     fk_add       ; Aufgabe 1: add
                dw      000000000000     ; Aufgabe 1 a  (0)
                dw      000000000000     ; Aufgabe 1 b  (0)
                025     fk_add       ; Aufgabe 2: add
                dw      060000000000     ; Aufgabe 2 a  (-0.5)
                dw      020000000000     ; Aufgabe 2 b  (0.5)
                025     fk_add       ; Aufgabe 3: add
                dw      020000000000     ; Aufgabe 3 a  (0.5)
                dw      017777777777     ; Aufgabe 3 b  (0.4999999998)
                025     fk_add       ; Aufgabe 4: add
                dw      000000000000     ; Aufgabe 4 a  (0)
                dw      040000000000     ; Aufgabe 4 b  (-1)
                025     fk_add       ; Aufgabe 5: add
                dw      000000000003     ; Aufgabe 5 a  (6.98491931e-10)
                dw      077777777775     ; Aufgabe 5 b  (-6.98491931e-10)
                025     fk_add       ; Aufgabe 6: add
                dw      037777777777     ; Aufgabe 6 a  (0.9999999998)
                dw      040000000001     ; Aufgabe 6 b  (-0.9999999998)
                025     fk_add       ; Aufgabe 7: add
                dw      037777777777     ; Aufgabe 7 a  (0.9999999998)
                dw      000000000000     ; Aufgabe 7 b  (0)
                025     fk_add       ; Aufgabe 8: add
                dw      040000000000     ; Aufgabe 8 a  (-1)
                dw      000000000000     ; Aufgabe 8 b  (0)
                025     fk_add       ; Aufgabe 9: add
                dw      040000000000     ; Aufgabe 9 a  (-1)
                dw      037777777777     ; Aufgabe 9 b  (0.9999999998)
                025     fk_add       ; Aufgabe 10: add
                dw      000000000001     ; Aufgabe 10 a  (2.328306437e-10)
                dw      000000000001     ; Aufgabe 10 b  (2.328306437e-10)
                025     fk_add       ; Aufgabe 11: add
                dw      060000000000     ; Aufgabe 11 a  (-0.5)
                dw      060000000000     ; Aufgabe 11 b  (-0.5)
                025     fk_add       ; Aufgabe 12: add
                dw      020000000000     ; Aufgabe 12 a  (0.5)
                dw      060000000001     ; Aufgabe 12 b  (-0.4999999998)
                025     fk_add       ; Aufgabe 13: add
                dw      015452302553     ; Aufgabe 13 a  (0.4244616877)
                dw      061630160141     ; Aufgabe 13 b  (-0.4438342822)
                025     fk_add       ; Aufgabe 14: add
                dw      073336771145     ; Aufgabe 14 a  (-0.1426399711)
                dw      066050625725     ; Aufgabe 14 b  (-0.3100102048)
                025     fk_add       ; Aufgabe 15: add
                dw      016655224077     ; Aufgabe 15 a  (0.4637017397)
                dw      001257261547     ; Aufgabe 15 b  (0.04195233597)
                025     fk_add       ; Aufgabe 16: add
                dw      015035161423     ; Aufgabe 16 a  (0.4080335542)
                dw      065035354400     ; Aufgabe 16 b  (-0.3419517875)
                025     fk_add       ; Aufgabe 17: add
                dw      067074437560     ; Aufgabe 17 a  (-0.2775535919)
                dw      000344155240     ; Aufgabe 17 b  (0.01392904669)
                025     fk_add       ; Aufgabe 18: add
                dw      074542566672     ; Aufgabe 18 a  (-0.1033488675)
                dw      010700354105     ; Aufgabe 18 b  (0.2773718995)
                025     fk_add       ; Aufgabe 19: add
                dw      013661250667     ; Aufgabe 19 a  (0.370198352)
                dw      060324652105     ; Aufgabe 19 b  (-0.4870097477)
                025     fk_add       ; Aufgabe 20: add
                dw      070601250130     ; Aufgabe 20 a  (-0.2264814172)
                dw      063174250353     ; Aufgabe 20 b  (-0.3986615587)
                025     fk_sub       ; Aufgabe 21: sub
                dw      000000000000     ; Aufgabe 21 a  (0)
                dw      000000000000     ; Aufgabe 21 b  (0)
                025     fk_sub       ; Aufgabe 22: sub
                dw      037777777777     ; Aufgabe 22 a  (0.9999999998)
                dw      037777777777     ; Aufgabe 22 b  (0.9999999998)
                025     fk_sub       ; Aufgabe 23: sub
                dw      040000000000     ; Aufgabe 23 a  (-1)
                dw      040000000000     ; Aufgabe 23 b  (-1)
                025     fk_sub       ; Aufgabe 24: sub
                dw      060000000000     ; Aufgabe 24 a  (-0.5)
                dw      020000000000     ; Aufgabe 24 b  (0.5)
                025     fk_sub       ; Aufgabe 25: sub
                dw      020000000000     ; Aufgabe 25 a  (0.5)
                dw      060000000001     ; Aufgabe 25 b  (-0.4999999998)
                025     fk_sub       ; Aufgabe 26: sub
                dw      000000000000     ; Aufgabe 26 a  (0)
                dw      037777777777     ; Aufgabe 26 b  (0.9999999998)
                025     fk_sub       ; Aufgabe 27: sub
                dw      037777777777     ; Aufgabe 27 a  (0.9999999998)
                dw      000000000001     ; Aufgabe 27 b  (2.328306437e-10)
                025     fk_sub       ; Aufgabe 28: sub
                dw      040000000000     ; Aufgabe 28 a  (-1)
                dw      040000000001     ; Aufgabe 28 b  (-0.9999999998)
                025     fk_sub       ; Aufgabe 29: sub
                dw      000000000007     ; Aufgabe 29 a  (1.629814506e-09)
                dw      077777777767     ; Aufgabe 29 b  (-2.095475793e-09)
                025     fk_sub       ; Aufgabe 30: sub
                dw      015452302553     ; Aufgabe 30 a  (0.4244616877)
                dw      061630160141     ; Aufgabe 30 b  (-0.4438342822)
                025     fk_sub       ; Aufgabe 31: sub
                dw      073336771145     ; Aufgabe 31 a  (-0.1426399711)
                dw      066050625725     ; Aufgabe 31 b  (-0.3100102048)
                025     fk_sub       ; Aufgabe 32: sub
                dw      016655224077     ; Aufgabe 32 a  (0.4637017397)
                dw      001257261547     ; Aufgabe 32 b  (0.04195233597)
                025     fk_sub       ; Aufgabe 33: sub
                dw      015035161423     ; Aufgabe 33 a  (0.4080335542)
                dw      065035354400     ; Aufgabe 33 b  (-0.3419517875)
                025     fk_sub       ; Aufgabe 34: sub
                dw      067074437560     ; Aufgabe 34 a  (-0.2775535919)
                dw      000344155240     ; Aufgabe 34 b  (0.01392904669)
                025     fk_sub       ; Aufgabe 35: sub
                dw      074542566672     ; Aufgabe 35 a  (-0.1033488675)
                dw      010700354105     ; Aufgabe 35 b  (0.2773718995)
                025     fk_sub       ; Aufgabe 36: sub
                dw      013661250667     ; Aufgabe 36 a  (0.370198352)
                dw      060324652105     ; Aufgabe 36 b  (-0.4870097477)
                025     fk_sub       ; Aufgabe 37: sub
                dw      070601250130     ; Aufgabe 37 a  (-0.2264814172)
                dw      063174250353     ; Aufgabe 37 b  (-0.3986615587)
                025     fk_mul       ; Aufgabe 38: mul
                dw      000000000000     ; Aufgabe 38 a  (0)
                dw      000000000005     ; Aufgabe 38 b  (1.164153218e-09)
                025     fk_mul       ; Aufgabe 39: mul
                dw      000000000005     ; Aufgabe 39 a  (1.164153218e-09)
                dw      000000000000     ; Aufgabe 39 b  (0)
                025     fk_mul       ; Aufgabe 40: mul
                dw      020000000000     ; Aufgabe 40 a  (0.5)
                dw      020000000000     ; Aufgabe 40 b  (0.5)
                025     fk_mul       ; Aufgabe 41: mul
                dw      040000000000     ; Aufgabe 41 a  (-1)
                dw      000000000007     ; Aufgabe 41 b  (1.629814506e-09)
                025     fk_mul       ; Aufgabe 42: mul
                dw      000000000007     ; Aufgabe 42 a  (1.629814506e-09)
                dw      040000000000     ; Aufgabe 42 b  (-1)
                025     fk_mul       ; Aufgabe 43: mul
                dw      040000000000     ; Aufgabe 43 a  (-1)
                dw      037777777777     ; Aufgabe 43 b  (0.9999999998)
                025     fk_mul       ; Aufgabe 44: mul
                dw      037777777777     ; Aufgabe 44 a  (0.9999999998)
                dw      037777777777     ; Aufgabe 44 b  (0.9999999998)
                025     fk_mul       ; Aufgabe 45: mul
                dw      000000000001     ; Aufgabe 45 a  (2.328306437e-10)
                dw      020000000000     ; Aufgabe 45 b  (0.5)
                025     fk_mul       ; Aufgabe 46: mul
                dw      000000000001     ; Aufgabe 46 a  (2.328306437e-10)
                dw      060000000000     ; Aufgabe 46 b  (-0.5)
                025     fk_mul       ; Aufgabe 47: mul
                dw      077777777777     ; Aufgabe 47 a  (-2.328306437e-10)
                dw      020000000000     ; Aufgabe 47 b  (0.5)
                025     fk_mul       ; Aufgabe 48: mul
                dw      077777777777     ; Aufgabe 48 a  (-2.328306437e-10)
                dw      060000000000     ; Aufgabe 48 b  (-0.5)
                025     fk_mul       ; Aufgabe 49: mul
                dw      000000000003     ; Aufgabe 49 a  (6.98491931e-10)
                dw      020000000000     ; Aufgabe 49 b  (0.5)
                025     fk_mul       ; Aufgabe 50: mul
                dw      020000000000     ; Aufgabe 50 a  (0.5)
                dw      020000000000     ; Aufgabe 50 b  (0.5)
                025     fk_mul       ; Aufgabe 51: mul
                dw      060000000000     ; Aufgabe 51 a  (-0.5)
                dw      020000000000     ; Aufgabe 51 b  (0.5)
                025     fk_mul       ; Aufgabe 52: mul
                dw      030000000000     ; Aufgabe 52 a  (0.75)
                dw      030000000000     ; Aufgabe 52 b  (0.75)
                025     fk_mul       ; Aufgabe 53: mul
                dw      040000000000     ; Aufgabe 53 a  (-1)
                dw      000000000000     ; Aufgabe 53 b  (0)
                025     fk_mul       ; Aufgabe 54: mul
                dw      037777777777     ; Aufgabe 54 a  (0.9999999998)
                dw      040000000001     ; Aufgabe 54 b  (-0.9999999998)
                025     fk_mul       ; Aufgabe 55: mul
                dw      022216417653     ; Aufgabe 55 a  (0.5711993973)
                dw      015543776206     ; Aufgabe 55 b  (0.4279783084)
                025     fk_mul       ; Aufgabe 56: mul
                dw      056776273720     ; Aufgabe 56 a  (-0.5313496701)
                dw      035715166142     ; Aufgabe 56 b  (0.9344012965)
                025     fk_mul       ; Aufgabe 57: mul
                dw      066234661362     ; Aufgabe 57 a  (-0.3029268417)
                dw      074365076772     ; Aufgabe 57 b  (-0.1100388779)
                025     fk_mul       ; Aufgabe 58: mul
                dw      060375301663     ; Aufgabe 58 a  (-0.4845349968)
                dw      017173627145     ; Aufgabe 58 b  (0.4763058659)
                025     fk_mul       ; Aufgabe 59: mul
                dw      024565375322     ; Aufgabe 59 a  (0.6477963221)
                dw      065117701065     ; Aufgabe 59 b  (-0.3388746853)
                025     fk_mul       ; Aufgabe 60: mul
                dw      033552377326     ; Aufgabe 60 a  (0.8658751748)
                dw      054314527321     ; Aufgabe 60 b  (-0.6125078907)
                025     fk_mul       ; Aufgabe 61: mul
                dw      032266732626     ; Aufgabe 61 a  (0.8236649982)
                dw      046774612246     ; Aufgabe 61 b  (-0.7814471335)
                025     fk_mul       ; Aufgabe 62: mul
                dw      040160643740     ; Aufgabe 62 a  (-0.993114002)
                dw      044671234672     ; Aufgabe 62 b  (-0.8480647965)
                025     fk_mul       ; Aufgabe 63: mul
                dw      062472631613     ; Aufgabe 63 a  (-0.4182861124)
                dw      063457642051     ; Aufgabe 63 b  (-0.3877065086)
                025     fk_mul       ; Aufgabe 64: mul
                dw      053610423337     ; Aufgabe 64 a  (-0.6322913843)
                dw      065336231543     ; Aufgabe 64 b  (-0.3301818736)
                025     fk_mul       ; Aufgabe 65: mul
                dw      002446725154     ; Aufgabe 65 a  (0.08050027024)
                dw      035005105737     ; Aufgabe 65 b  (0.9065635127)
                025     fk_mul       ; Aufgabe 66: mul
                dw      070043324310     ; Aufgabe 66 a  (-0.2478384506)
                dw      050175055314     ; Aufgabe 66 b  (-0.7423651936)
                025     fk_mul       ; Aufgabe 67: mul
                dw      065415701044     ; Aufgabe 67 a  (-0.3272780096)
                dw      075715552036     ; Aufgabe 67 b  (-0.06556963222)
                025     fk_mul       ; Aufgabe 68: mul
                dw      022560326253     ; Aufgabe 68 a  (0.5849864881)
                dw      026003131022     ; Aufgabe 68 b  (0.6876937193)
                025     fk_div       ; Aufgabe 69: div
                dw      000000000000     ; Aufgabe 69 a  (0)
                dw      000000000007     ; Aufgabe 69 b  (1.629814506e-09)
                025     fk_div       ; Aufgabe 70: div
                dw      000000000005     ; Aufgabe 70 a  (1.164153218e-09)
                dw      040000000000     ; Aufgabe 70 b  (-1)
                025     fk_div       ; Aufgabe 71: div
                dw      040000000001     ; Aufgabe 71 a  (-0.9999999998)
                dw      040000000000     ; Aufgabe 71 b  (-1)
                025     fk_div       ; Aufgabe 72: div
                dw      060000000000     ; Aufgabe 72 a  (-0.5)
                dw      020000000000     ; Aufgabe 72 b  (0.5)
                025     fk_div       ; Aufgabe 73: div
                dw      020000000000     ; Aufgabe 73 a  (0.5)
                dw      060000000000     ; Aufgabe 73 b  (-0.5)
                025     fk_div       ; Aufgabe 74: div
                dw      000000000001     ; Aufgabe 74 a  (2.328306437e-10)
                dw      037777777777     ; Aufgabe 74 b  (0.9999999998)
                025     fk_div       ; Aufgabe 75: div
                dw      077777777777     ; Aufgabe 75 a  (-2.328306437e-10)
                dw      037777777777     ; Aufgabe 75 b  (0.9999999998)
                025     fk_div       ; Aufgabe 76: div
                dw      037777777776     ; Aufgabe 76 a  (0.9999999995)
                dw      037777777777     ; Aufgabe 76 b  (0.9999999998)
                025     fk_div       ; Aufgabe 77: div
                dw      020000000000     ; Aufgabe 77 a  (0.5)
                dw      030000000000     ; Aufgabe 77 b  (0.75)
                025     fk_div       ; Aufgabe 78: div
                dw      000000000001     ; Aufgabe 78 a  (2.328306437e-10)
                dw      000000000003     ; Aufgabe 78 b  (6.98491931e-10)
                025     fk_div       ; Aufgabe 79: div
                dw      077777777777     ; Aufgabe 79 a  (-2.328306437e-10)
                dw      000000000003     ; Aufgabe 79 b  (6.98491931e-10)
                025     fk_div       ; Aufgabe 80: div
                dw      000000000003     ; Aufgabe 80 a  (6.98491931e-10)
                dw      000000000007     ; Aufgabe 80 b  (1.629814506e-09)
                025     fk_div       ; Aufgabe 81: div
                dw      020000000000     ; Aufgabe 81 a  (0.5)
                dw      040000000000     ; Aufgabe 81 b  (-1)
                025     fk_div       ; Aufgabe 82: div
                dw      077777777773     ; Aufgabe 82 a  (-1.164153218e-09)
                dw      000000000007     ; Aufgabe 82 b  (1.629814506e-09)
                025     fk_div       ; Aufgabe 83: div
                dw      064531120645     ; Aufgabe 83 a  (-0.3539332363)
                dw      060261674271     ; Aufgabe 83 b  (-0.4891438053)
                025     fk_div       ; Aufgabe 84: div
                dw      014616205016     ; Aufgabe 84 a  (0.3993078503)
                dw      036351414454     ; Aufgabe 84 b  (0.9517532093)
                025     fk_div       ; Aufgabe 85: div
                dw      003476200331     ; Aufgabe 85 a  (0.113174489)
                dw      072151560153     ; Aufgabe 85 b  (-0.1810474147)
                025     fk_div       ; Aufgabe 86: div
                dw      062237000407     ; Aufgabe 86 a  (-0.4277953489)
                dw      023012017016     ; Aufgabe 86 b  (0.594362143)
                025     fk_div       ; Aufgabe 87: div
                dw      021654001306     ; Aufgabe 87 a  (0.5573732122)
                dw      024461736072     ; Aufgabe 87 b  (0.6436727182)
                025     fk_div       ; Aufgabe 88: div
                dw      076475431607     ; Aufgabe 88 a  (-0.04311826662)
                dw      062513071104     ; Aufgabe 88 b  (-0.4172905525)
                025     fk_div       ; Aufgabe 89: div
                dw      070007735012     ; Aufgabe 89 a  (-0.2495158887)
                dw      063366510354     ; Aufgabe 89 b  (-0.391196196)
                025     fk_div       ; Aufgabe 90: div
                dw      014143314507     ; Aufgabe 90 a  (0.3810668753)
                dw      057634054545     ; Aufgabe 90 b  (-0.5060981873)
                025     fk_div       ; Aufgabe 91: div
                dw      073725675144     ; Aufgabe 91 a  (-0.1275714403)
                dw      041673112710     ; Aufgabe 91 b  (-0.9417024981)
                025     fk_div       ; Aufgabe 92: div
                dw      051674520325     ; Aufgabe 92 a  (-0.6916102867)
                dw      035635456337     ; Aufgabe 92 b  (0.9314935727)
                025     fk_div       ; Aufgabe 93: div
                dw      005003353417     ; Aufgabe 93 a  (0.1564611827)
                dw      013773740500     ; Aufgabe 93 b  (0.3747521192)
                025     fk_div       ; Aufgabe 94: div
                dw      062254734212     ; Aufgabe 94 a  (-0.4269451774)
                dw      050003247566     ; Aufgabe 94 b  (-0.7497968995)
                025     fk_div       ; Aufgabe 95: div
                dw      004413177702     ; Aufgabe 95 a  (0.1413116311)
                dw      007406265041     ; Aufgabe 95 b  (0.2347627955)
                025     fk_div       ; Aufgabe 96: div
                dw      002764711075     ; Aufgabe 96 a  (0.09307207097)
                dw      065365421657     ; Aufgabe 96 b  (-0.3287637422)
                025     fk_div       ; Aufgabe 97: div
                dw      010000000000     ; Aufgabe 97 a  (0.25)
                dw      000000000000     ; Aufgabe 97 b  (0)
jobsend:       dw      0            ; Ende

                equ     03100        ; Ergebniszellen: eine je Aufgabe, in der Reihenfolge der Liste
res:            db      97

; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)

; Sollwerte aus exakter Bruchrechnung (Fraction in fk_math_op_gen.py), nicht aus dem Verfahren. Aufgabe i: Zelle 03100 + (i-1).
;#PRUEFE-START
; BZ=0155 AC=40000000000 FUE=1 US=0   # Halt im kuenstlichen Ueberlauf von fk_div (Aufgabe 97, 0,25 / 0), BZ = fkm_fue + 3
; 3100: 00000000000   # add Aufgabe 1
; 3101: 00000000000   # add Aufgabe 2
; 3102: 37777777777   # add Aufgabe 3
; 3103: 40000000000   # add Aufgabe 4
; 3104: 00000000000   # add Aufgabe 5
; 3105: 00000000000   # add Aufgabe 6
; 3106: 37777777777   # add Aufgabe 7
; 3107: 40000000000   # add Aufgabe 8
; 3110: 77777777777   # add Aufgabe 9
; 3111: 00000000002   # add Aufgabe 10
; 3112: 40000000000   # add Aufgabe 11
; 3113: 00000000001   # add Aufgabe 12
; 3114: 77302462714   # add Aufgabe 13
; 3115: 61407617072   # add Aufgabe 14
; 3116: 20134505646   # add Aufgabe 15
; 3117: 02072536023   # add Aufgabe 16
; 3120: 67440615020   # add Aufgabe 17
; 3121: 05443142777   # add Aufgabe 18
; 3122: 74206122774   # add Aufgabe 19
; 3123: 53775520503   # add Aufgabe 20
; 3124: 00000000000   # sub Aufgabe 21
; 3125: 00000000000   # sub Aufgabe 22
; 3126: 00000000000   # sub Aufgabe 23
; 3127: 40000000000   # sub Aufgabe 24
; 3130: 37777777777   # sub Aufgabe 25
; 3131: 40000000001   # sub Aufgabe 26
; 3132: 37777777776   # sub Aufgabe 27
; 3133: 77777777777   # sub Aufgabe 28
; 3134: 00000000020   # sub Aufgabe 29
; 3135: 33622122412   # sub Aufgabe 30
; 3136: 05266143220   # sub Aufgabe 31
; 3137: 15375742330   # sub Aufgabe 32
; 3140: 27777605023   # sub Aufgabe 33
; 3141: 66530262320   # sub Aufgabe 34
; 3142: 63642212565   # sub Aufgabe 35
; 3143: 33334376562   # sub Aufgabe 36
; 3144: 05404777555   # sub Aufgabe 37
; 3145: 00000000000   # mul Aufgabe 38
; 3146: 00000000000   # mul Aufgabe 39
; 3147: 10000000000   # mul Aufgabe 40
; 3150: 77777777771   # mul Aufgabe 41
; 3151: 77777777771   # mul Aufgabe 42
; 3152: 40000000001   # mul Aufgabe 43
; 3153: 37777777776   # mul Aufgabe 44
; 3154: 00000000001   # mul Aufgabe 45
; 3155: 77777777777   # mul Aufgabe 46
; 3156: 77777777777   # mul Aufgabe 47
; 3157: 00000000001   # mul Aufgabe 48
; 3160: 00000000002   # mul Aufgabe 49
; 3161: 10000000000   # mul Aufgabe 50
; 3162: 70000000000   # mul Aufgabe 51
; 3163: 22000000000   # mul Aufgabe 52
; 3164: 00000000000   # mul Aufgabe 53
; 3165: 40000000002   # mul Aufgabe 54
; 3166: 07645177061   # mul Aufgabe 55
; 3167: 60071343755   # mul Aufgabe 56
; 3170: 01042107457   # mul Aufgabe 57
; 3171: 70472623373   # mul Aufgabe 58
; 3172: 70763265704   # mul Aufgabe 59
; 3173: 57016520511   # mul Aufgabe 60
; 3174: 53316332774   # mul Aufgabe 61
; 3175: 32747007446   # mul Aufgabe 62
; 3176: 05141017326   # mul Aufgabe 63
; 3177: 06534403277   # mul Aufgabe 64
; 3200: 02253534736   # mul Aufgabe 65
; 3201: 05706337627   # mul Aufgabe 66
; 3202: 00537457245   # mul Aufgabe 67
; 3203: 14677111765   # mul Aufgabe 68
; 3204: 00000000000   # div Aufgabe 69
; 3205: 77777777773   # div Aufgabe 70
; 3206: 37777777777   # div Aufgabe 71
; 3207: 40000000000   # div Aufgabe 72
; 3210: 40000000000   # div Aufgabe 73
; 3211: 00000000001   # div Aufgabe 74
; 3212: 77777777777   # div Aufgabe 75
; 3213: 37777777777   # div Aufgabe 76
; 3214: 25252525253   # div Aufgabe 77
; 3215: 12525252525   # div Aufgabe 78
; 3216: 65252525253   # div Aufgabe 79
; 3217: 15555555556   # div Aufgabe 80
; 3220: 60000000000   # div Aufgabe 81
; 3221: 51111111111   # div Aufgabe 82
; 3222: 27117054237   # div Aufgabe 83
; 3223: 15331716513   # div Aufgabe 84
; 3224: 53776150032   # div Aufgabe 85
; 3225: 50757416216   # div Aufgabe 86
; 3226: 33553255224   # div Aufgabe 87
; 3227: 03234743402   # div Aufgabe 88
; 3230: 24322131061   # div Aufgabe 89
; 3231: 47717521426   # div Aufgabe 90
; 3232: 04253413660   # div Aufgabe 91
; 3233: 50173227722   # div Aufgabe 92
; 3234: 15270324366   # div Aufgabe 93
; 3235: 22161222365   # div Aufgabe 94
; 3236: 23206051463   # div Aufgabe 95
; 3237: 66741571131   # div Aufgabe 96
;#PRUEFE-ENDE
