; gk_math_op.asm  --  Projekt_Gleitkomma: Gleitkomma-Grundrechenarten (dwg-Format) gk_add, gk_sub, gk_mul, gk_div
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
; Testhauptprogramm ab relativ 02000: Falltabelle fall (34 Faelle, Paare a,b ab 02400), Operationstabelle optab (02300); die Ergebnisse stehen op-weise nacheinander
;   ab 03000: add 03000.., sub, mul, div (34 Zellen je Operation). Der letzte Fall 5/0 beendet den Lauf mit dem kuenstlichen Ueberlauf in gk_div (Halt).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
; Test: Tastenfolge H M+ E M- R (E zaehlt 1 dazu: Start bei 02000).

; ===== UP gk_add, gk_sub, gk_mul, gk_div (dwg-Format) als ein gemeinsames Makro GK_MATH (Assembler/Sourcecode/c82ass.makros, Beschreibung dort); Eingabe R1 (7773) und R2 (7776), Ergebnis im AC; R1, R2 bleiben unveraendert.
; Das Makro erzeugt jeden Teil des Codes nur einmal, auch bei mehreren Aufrufen und gleich mit welchem Parameter: jeder Aufruf legt nur an, was noch fehlt (Einsprung, Kern, gemeinsamer Teil).
                start                ; Zaehlung beginnt bei 0000 (relativ): die UP ab 0000, das Testhauptprogramm ab 02000
                GK_MATH add          ; gk_add: R1 + R2 (erzeugt Kern der Addition und gemeinsamen Teil)
                GK_MATH sub          ; gk_sub: R1 - R2 (nur der Einsprung, der Kern ist schon da)
                GK_MATH mul          ; gk_mul: R1 * R2 (Kern von Multiplikation und Division)
                GK_MATH div          ; gk_div: R1 / R2 (nur der Einsprung)
                GK_MATH alle         ; Wiederholung: erzeugt nichts, denn alle vier UP sind schon da (ein doppelter Code wuerde als doppelte Marke scheitern)
                GK_MATH mul          ; Wiederholung: erzeugt nichts

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

                equ     02300        ; Operationstabelle
optab:          025     gk_add       ; Operation 1: Addition
                025     gk_sub       ; Operation 2: Subtraktion
                025     gk_mul       ; Operation 3: Multiplikation
                025     gk_div       ; Operation 4: Division
optabend:       dw      0            ; Ende

                equ     02400        ; Falltabelle: Paare a, b (dwg)
fall:
                dw      020600000000     ; Fall 1 a  (1)
                dw      020600000000     ; Fall 1 b  (1)
                dw      020700000000     ; Fall 2 a  (1,5)
                dw      021220000000     ; Fall 2 b  (2,25)
                dw      061300000000     ; Fall 3 a  (-3)
                dw      020200000000     ; Fall 3 b  (0,5)
                dw      021740000000     ; Fall 4 a  (7)
                dw      061740000000     ; Fall 4 b  (-7)
                dw      036756326240     ; Fall 5 a  (5E8)
                dw      020640000000     ; Fall 5 b  (1,25 (d gross))
                dw      020600000000     ; Fall 6 a  (1)
                dw      044200662545     ; Fall 6 b  (-3E-8 (Schutzbits))
                dw      020600000000     ; Fall 7 a  (1)
                dw      003600000000     ; Fall 7 b  (2^-26 (Mitte))
                dw      060600000000     ; Fall 8 a  (-1)
                dw      043600000000     ; Fall 8 b  (-2^-26 (Mitte))
                dw      020600000000     ; Fall 9 a  (1)
                dw      043600000000     ; Fall 9 b  (-2^-26)
                dw      017652525253     ; Fall 10 a  (1/3)
                dw      020252525253     ; Fall 10 b  (2/3)
                dw      000000000000     ; Fall 11 a  (0)
                dw      021640000000     ; Fall 11 b  (5)
                dw      006600000000     ; Fall 12 a  (2^-20)
                dw      006600000000     ; Fall 12 b  (2^-20)
                dw      020600000003     ; Fall 13 a  (1,0000001)
                dw      020377777771     ; Fall 13 b  (0,9999999)
                dw      030761100624     ; Fall 14 a  (123456,789)
                dw      055311413702     ; Fall 14 b  (-0,0123)
                dw      076600000000     ; Fall 15 a  (-2^28)
                dw      021300000000     ; Fall 15 b  (3)
                dw      022250315722     ; Fall 16 a  (zufall 1)
                dw      056240604053     ; Fall 16 b  (zufall 1)
                dw      016640637140     ; Fall 17 a  (zufall 2)
                dw      061362423745     ; Fall 17 b  (zufall 2)
                dw      016602146533     ; Fall 18 a  (zufall 3)
                dw      061716256772     ; Fall 18 b  (zufall 3)
                dw      057217722273     ; Fall 19 a  (zufall 4)
                dw      060266610765     ; Fall 19 b  (zufall 4)
                dw      062337130057     ; Fall 20 a  (zufall 5)
                dw      021620036750     ; Fall 20 b  (zufall 5)
                dw      021267273506     ; Fall 21 a  (zufall 6)
                dw      021261522675     ; Fall 21 b  (zufall 6)
                dw      020300000000     ; Fall 22 a  (0,75)
                dw      020300000000     ; Fall 22 b  (0,75)
                dw      020600000000     ; Fall 23 a  (1)
                dw      003200000000     ; Fall 23 b  (2^-27)
                dw      020600000000     ; Fall 24 a  (1)
                dw      001600000000     ; Fall 24 b  (2^-30 (d = 30))
                dw      001600000000     ; Fall 25 a  (2^-30)
                dw      020600000000     ; Fall 25 b  (1 (Tausch))
                dw      021300000000     ; Fall 26 a  (3)
                dw      061740000000     ; Fall 26 b  (-7)
                dw      020200000000     ; Fall 27 a  (0,5)
                dw      020200000000     ; Fall 27 b  (0,5)
                dw      001611340575     ; Fall 28 a  (1E-9)
                dw      037356326240     ; Fall 28 b  (1E9)
                dw      021640000000     ; Fall 29 a  (5)
                dw      020600000000     ; Fall 29 b  (1)
                dw      020600000000     ; Fall 30 a  (1)
                dw      022240000000     ; Fall 30 b  (10)
                dw      020252525253     ; Fall 31 a  (2/3)
                dw      017652525253     ; Fall 31 b  (1/3)
                dw      001600000000     ; Fall 32 a  (2^-30)
                dw      001600000000     ; Fall 32 b  (2^-30 (mul Unterlauf))
                dw      041600000000     ; Fall 33 a  (-2^-30)
                dw      001200000000     ; Fall 33 b  (2^-31)
                dw      021640000000     ; Fall 34 a  (5)
                dw      000000000000     ; Fall 34 b  (0 (div: kuenstlicher FUE))
fallend:       dw      0            ; Ende

                equ     03000        ; Ergebniszellen: add, sub, mul, div je 34 Zellen
res:            db      136

; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)

; Sollwerte aus exakter Bruchrechnung (gk_modell.enc_exact), nicht aus dem Verfahren. Fall n, Operation o: Zelle 03000 + (o-1)*34 + (n-1).
;#PRUEFE-START
; BZ=0201 AC=40000000000 FUE=1 US=0   # Halt im kuenstlichen Ueberlauf von gk_div (Fall 5/0), BZ = Adresse des Befehls hinter dem 210 in gk_fue + 1
; 3000: 21200000000   # add Fall 1
; 3001: 21360000000   # add Fall 2
; 3002: 61240000000   # add Fall 3
; 3003: 00000000000   # add Fall 4
; 3004: 36756326240   # add Fall 5
; 3005: 20377777776   # add Fall 6
; 3006: 20600000001   # add Fall 7
; 3007: 60600000001   # add Fall 8
; 3010: 20377777777   # add Fall 9
; 3011: 20600000000   # add Fall 10
; 3012: 21640000000   # add Fall 11
; 3013: 07200000000   # add Fall 12
; 3014: 21200000000   # add Fall 13
; 3015: 30761100616   # add Fall 14
; 3016: 76377777777   # add Fall 15
; 3017: 22247614312   # add Fall 16
; 3020: 61355406762   # add Fall 17
; 3021: 61714235305   # add Fall 18
; 3022: 60332575444   # add Fall 19
; 3023: 62227110473   # add Fall 20
; 3024: 21664407202   # add Fall 21
; 3025: 20700000000   # add Fall 22
; 3026: 20600000000   # add Fall 23
; 3027: 20600000000   # add Fall 24
; 3030: 20600000000   # add Fall 25
; 3031: 61600000000   # add Fall 26
; 3032: 20600000000   # add Fall 27
; 3033: 37356326240   # add Fall 28
; 3034: 21700000000   # add Fall 29
; 3035: 22260000000   # add Fall 30
; 3036: 20600000000   # add Fall 31
; 3037: 02200000000   # add Fall 32
; 3040: 41200000000   # add Fall 33
; 3041: 21640000000   # add Fall 34
; 3042: 00000000000   # sub Fall 1
; 3043: 60300000000   # sub Fall 2
; 3044: 61340000000   # sub Fall 3
; 3045: 22340000000   # sub Fall 4
; 3046: 36756326240   # sub Fall 5
; 3047: 20600000001   # sub Fall 6
; 3050: 20377777777   # sub Fall 7
; 3051: 60377777777   # sub Fall 8
; 3052: 20600000001   # sub Fall 9
; 3053: 57652525253   # sub Fall 10
; 3054: 61640000000   # sub Fall 11
; 3055: 00000000000   # sub Fall 12
; 3056: 05320000000   # sub Fall 13
; 3057: 30761100632   # sub Fall 14
; 3060: 76600000000   # sub Fall 15
; 3061: 22251017332   # sub Fall 16
; 3062: 21367440730   # sub Fall 17
; 3063: 21720300457   # sub Fall 18
; 3064: 20222624306   # sub Fall 19
; 3065: 62623463622   # sub Fall 20
; 3066: 16666430440   # sub Fall 21
; 3067: 00000000000   # sub Fall 22
; 3070: 20600000000   # sub Fall 23
; 3071: 20600000000   # sub Fall 24
; 3072: 60600000000   # sub Fall 25
; 3073: 22240000000   # sub Fall 26
; 3074: 00000000000   # sub Fall 27
; 3075: 77356326240   # sub Fall 28
; 3076: 21600000000   # sub Fall 29
; 3077: 62220000000   # sub Fall 30
; 3100: 17652525253   # sub Fall 31
; 3101: 00000000000   # sub Fall 32
; 3102: 41700000000   # sub Fall 33
; 3103: 21640000000   # sub Fall 34
; 3104: 20600000000   # mul Fall 1
; 3105: 21330000000   # mul Fall 2
; 3106: 60700000000   # mul Fall 3
; 3107: 63304000000   # mul Fall 4
; 3110: 37225005744   # mul Fall 5
; 3111: 44200662545   # mul Fall 6
; 3112: 03600000000   # mul Fall 7
; 3113: 03600000000   # mul Fall 8
; 3114: 43600000000   # mul Fall 9
; 3115: 17343434344   # mul Fall 10
; 3116: 00000000000   # mul Fall 11
; 3117: 00000000000   # mul Fall 12
; 3120: 20377777777   # mul Fall 13
; 3121: 65675641137   # mul Fall 14
; 3122: 77300000000   # mul Fall 15
; 3123: 57723377757   # mul Fall 16
; 3124: 57630265645   # mul Fall 17
; 3125: 57721707175   # mul Fall 18
; 3126: 16715370741   # mul Fall 19
; 3127: 63373131044   # mul Fall 20
; 3130: 21776404724   # mul Fall 21
; 3131: 20220000000   # mul Fall 22
; 3132: 03200000000   # mul Fall 23
; 3133: 01600000000   # mul Fall 24
; 3134: 01600000000   # mul Fall 25
; 3135: 62650000000   # mul Fall 26
; 3136: 17600000000   # mul Fall 27
; 3137: 20600000000   # mul Fall 28
; 3140: 21640000000   # mul Fall 29
; 3141: 22240000000   # mul Fall 30
; 3142: 17343434344   # mul Fall 31
; 3143: 00000000000   # mul Fall 32
; 3144: 00000000000   # mul Fall 33
; 3145: 00000000000   # mul Fall 34
; 3146: 20600000000   # div Fall 1
; 3147: 20252525253   # div Fall 2
; 3150: 61700000000   # div Fall 3
; 3151: 60600000000   # div Fall 4
; 3152: 36676570200   # div Fall 5
; 3153: 74776240253   # div Fall 6
; 3154: 35600000000   # div Fall 7
; 3155: 35600000000   # div Fall 8
; 3156: 75600000000   # div Fall 9
; 3157: 20200000000   # div Fall 10
; 3160: 00000000000   # div Fall 11
; 3161: 20600000000   # div Fall 12
; 3162: 20600000007   # div Fall 13
; 3163: 74231117105   # div Fall 14
; 3164: 75652525253   # div Fall 15
; 3165: 64606054231   # div Fall 16
; 3166: 55651570653   # div Fall 17
; 3167: 55241421562   # div Fall 18
; 3170: 17311445706   # div Fall 19
; 3171: 61306225353   # div Fall 20
; 3172: 20604070246   # div Fall 21
; 3173: 20600000000   # div Fall 22
; 3174: 36200000000   # div Fall 23
; 3175: 37600000000   # div Fall 24
; 3176: 01600000000   # div Fall 25
; 3177: 57733333333   # div Fall 26
; 3200: 20600000000   # div Fall 27
; 3201: 00000000000   # div Fall 28
; 3202: 21640000000   # div Fall 29
; 3203: 16714631463   # div Fall 30
; 3204: 21200000000   # div Fall 31
; 3205: 20600000000   # div Fall 32
; 3206: 61200000000   # div Fall 33
;#PRUEFE-ENDE
