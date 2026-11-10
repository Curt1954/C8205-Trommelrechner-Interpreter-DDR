; gk_trigonomie_sin.asm  --  Projekt_Gleitkomma: Sinusfunktion gk_sin im dwg-Format (Gleitkomma, 26-Bit-Mantisse)
; Stand 08.11.2026. Der Code von gk_sin steht seit 08.11.2026 im Makro GK_SIN (Assembler/Sourcecode/c82ass.makros); dieses Programm ruft es einmal auf und enthaelt das Testhauptprogramm.
; Der Aufruf von GK_SIN erzeugt denselben Code wie der frueher hier stehende Text (Objektdatei byteweise gleich). Konstanten und Sollwerte aus gk_modell/gk_sin_modell.py.
;
; Format dwg (wie gk_math_op): z0 Vorzeichen, z1..z6 Exponent e+32, z7..z32 Mantisse M (2^25 <= M < 2^26), Wert = +-M/2^26 * 2^e; die Zahl 0 ist das Wort 0.
; Aufruf (Festlegung 031: gk_sin ruft UP auf, ist also nicht unterste Ebene und uebergibt deshalb ueber einen Parameterblock, nicht ueber R1):
;   x (dwg, Bogenmass) nach gks_x (Zelle gk_sin+1) legen, dann  025 gk_sin ;  Ergebnis sin(x) im AC (dwg). gks_x bleibt unveraendert.
;   Zerstoert: AC, eigene Arbeitszellen (gks_*), R1 (7773), R2 (7776) und die Arbeitsspur 7640 bis 7677 (durch gk_add, gk_sub, gk_mul). R3 bleibt unberuehrt.
;   gk_sin ruft gk_add, gk_sub und gk_mul auf (Makro GK_MATH, das GK_SIN selbst aufruft). Die Rueckkehr laeuft ueber die eigene Zelle gks_rueck (Festlegungen 009, 010).
; ANNAHMEN (offen, bitte bestaetigen): A1 Bereich |x| < 4096 * pi/2 (rund 6433, n = 0 bis 4095 Viertelkreise); ausserhalb ein kuenstlicher Ueberlauf (AC := 2^32-1, + 1, Halt beim
;   naechsten Befehl), wie bei gk_div durch 0 und beim Exponentenueberlauf in gk_math_op (A4, A9). Grund: die Argumentreduktion rechnet mit 3 Teilkonstanten von pi/2.
;   A2 Fehler im Bereich hoechstens etwa 2 Einheiten der letzten Mantissenstelle (Modell gegen exakte Reihe, 20000 Zufallsfaelle: groesster Fehler 1,7 Einheiten);
;   sin(x) ist fuer das auf dwg gerundete x gemeint (nicht fuer das ungerundete mathematische x: sin(pi) liefert daher -2,78E-8, nicht 0).
;   A3 sin(0) = 0 (Wort 0); sehr kleine x: sin(x) = x (Ergebnis gleich dem Argument). A4 Ergebniswort -0 gibt es nicht: ein Ergebnis 0 bleibt das Wort 0.
; VERFAHREN: a = |x|; Vorzeichen merken. t = a * 2/pi; w = t + 2^25 (die Addition von 2^25 rundet t auf eine ganze Zahl n, die Mantisse von w ist 2^25 + n, n = w - 2^25).
;   Bereichspruefung n < 4096 am Wort w. nf = w - 2^25 (n als dwg-Zahl, exakt). Quadrant q = n mod 4 = die unteren 2 Bit von w.
;   Reduktion nach Cody und Waite: r = ((a - n*P1) - n*P2) - n*P3 mit pi/2 = P1 + P2 + P3; P1 und P2 haben nur 13 Mantissenbit, so dass n*P1 und n*P2 exakt sind; |r| <= pi/4 (+ Rundung).
;   y = r*r. q gerade: sin r = r * S(y), S nach Horner mit 5 Koeffizienten (1/9!, -1/7!, 1/5!, -1/3!, 1); q ungerade: cos r = K(y) nach Horner mit 6 Koeffizienten (-1/10!, 1/8!, -1/6!, 1/4!, -1/2!, 1).
;   Horner: p := Koeffizient 1; fuer jeden weiteren: p := p*y + Koeffizient. Ergebnis sin(a) = +S bei q = 0, +K bei 1, -S bei 2, -K bei 3; Vorzeichen insgesamt = (q >> 1) + Vorzeichen von x (mod 2).
;   Zum Vorzeichenwechsel eines Wortes ungleich 0 wird z0 gesetzt oder geloescht.
; Speicher (Festlegung 001): ohne Testhauptprogramm etwa 0300 Zellen ab 0000 (GK_MATH add, sub, mul und gk_sin); Empfehlung: Anfang auf eine 040-Grenze, spaeter beliebig verschiebbar (alle Spruenge relativ).
; Testhauptprogramm ab relativ 02000: Falltabelle fall (23 Faelle, ab 02400), Ergebnisse ab 03000 (Fall n in Zelle 03000 + n - 1). Der letzte Fall (7000) endet mit dem kuenstlichen Ueberlauf (Halt).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
; Test: Tastenfolge H M+ E M- R (E zaehlt 1 dazu: Start bei 02000).

                start                ; Zaehlung beginnt bei 0000 (relativ)
                GK_SIN               ; Makro GK_SIN (c82ass.makros): gk_add, gk_sub, gk_mul und gk_sin, jeder Teil nur einmal erzeugt

; ===== TESTHAUPTPROGRAMM, relativ ab 02000. Fuer den Routinebetrieb den Abschnitt bis 'ENDE TESTHAUPTPROGRAMM' entfernen.
                equ     02000        ; relative Adresse 02000
haupt:          .LD     @fall        ; Zeiger auf die Falltabelle
                .STO    fz           ; merken
                .LD     @res         ; Zeiger auf die Ergebniszellen
                .STO    rz           ; merken
fa_l:           .LD     fz           ; Zeiger auf x
                .LDR    0            ; AC := x
                .STO    gks_x        ; Parameter von gk_sin
                025     gk_sin       ; AC := sin(x)
                .STO    tm           ; Ergebnis merken
                .LD     rz           ; Zeiger auf die Ergebniszelle
                .ADD    #0240        ; + Speicherbefehl
                .STO    sp           ; auf die naechste Zelle legen
                .LD     tm           ; Ergebnis
sp:             db      1            ; Laufzeit: 240 res_i
                ZEIGER_NAECHST rz    ; naechste Ergebniszelle
                ZEIGER_NAECHST fz    ; naechster Fall
                .SUB    @fallend     ; Zeiger - Ende der Falltabelle
                .JNEG   fa_l         ; kleiner (negativ): naechster Fall
                .STOP   0            ; Halt (nicht erreicht: der letzte Fall endet im FUE-Halt in gks_fue)
fz:             db      1            ; Zeiger Falltabelle
rz:             db      1            ; Zeiger Ergebniszelle
tm:             db      1            ; Ergebnis (Zwischenspeicher)

                equ     02400        ; Falltabelle: x (dwg)
fall:
                dw      000000000000     ; Fall 1  x = 0
                dw      020600000000     ; Fall 2  x = 1
                dw      060600000000     ; Fall 3  x = -1
                dw      020200000000     ; Fall 4  x = 0,5
                dw      020711037553     ; Fall 5  x = pi/2
                dw      021311037553     ; Fall 6  x = pi
                dw      021711037553     ; Fall 7  x = 2 pi
                dw      021300000000     ; Fall 8  x = 3
                dw      061240000000     ; Fall 9  x = -2,5
                dw      022240000000     ; Fall 10  x = 10
                dw      023710000000     ; Fall 11  x = 100
                dw      025372000000     ; Fall 12  x = 1000
                dw      013603044672     ; Fall 13  x = 0,001
                dw      010247613261     ; Fall 14  x = 1E-5
                dw      026634200000     ; Fall 15  x = 5000
                dw      066673400000     ; Fall 16  x = -6000
                dw      020311037553     ; Fall 17  x = pi/4
                dw      016714631463     ; Fall 18  x = 0,1
                dw      021740000000     ; Fall 19  x = 7
                dw      006600000000     ; Fall 20  x = 2^-20
                dw      001611340575     ; Fall 21  x = 1E-9
                dw      026710755343     ; Fall 22  x = 4094*pi/2 (n = 4094, Rand des Bereichs)
                dw      026732600000     ; Fall 23  x = 7000 (n >= 4096: kuenstlicher Ueberlauf)
fallend:        dw      0            ; Ende

                equ     03000        ; Ergebniszellen: sin(x) je Fall
res:            db      23

; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende

; Sollwerte aus dem bitgenauen Modell gk_modell/gk_sin_modell.py (Verfahren mit gk_modell.addm, subm, mulm); Abweichung des Modells von der exakten Sinusfunktion siehe A2.
; Fall n: Zelle 03000 + n - 1.
;#PRUEFE-START
; BZ=0575 AC=40000000000 FUE=1 US=0   # Halt im kuenstlichen Ueberlauf von gk_sin (Fall 7000), BZ = Adresse des Befehls hinter dem .ADD in gks_fue + 1
; 3000: 00000000000   # Fall 1: sin(0)
; 3001: 20327325222   # Fall 2: sin(1)
; 3002: 60327325222   # Fall 3: sin(-1)
; 3003: 17765356417   # Fall 4: sin(0,5)
; 3004: 20600000000   # Fall 5: sin(pi/2)
; 3005: 43756751350   # Fall 6: sin(pi)
; 3006: 04356751350   # Fall 7: sin(2 pi)
; 3007: 17220403416   # Fall 8: sin(3)
; 3010: 60231152742   # Fall 9: sin(-2,5)
; 3011: 60213211737   # Fall 10: sin(10)
; 3012: 60201502267   # Fall 11: sin(100)
; 3013: 20323534603   # Fall 12: sin(1000)
; 3014: 13603044664   # Fall 13: sin(0,001)
; 3015: 10247613261   # Fall 14: sin(1E-5)
; 3016: 60374726571   # Fall 15: sin(5000)
; 3017: 17732774066   # Fall 16: sin(-6000)
; 3020: 20265011716   # Fall 17: sin(pi/4)
; 3021: 16714352731   # Fall 18: sin(0,1)
; 3022: 20250140431   # Fall 19: sin(7)
; 3023: 06600000000   # Fall 20: sin(2^-20)
; 3024: 01611340575   # Fall 21: sin(1E-9)
; 3025: 51311455556   # Fall 22: sin(4094*pi/2)
;#PRUEFE-ENDE
