; gk_sin_makro.asm - Test des Makros GK_SIN (c82ass.makros): mehrfach aufgerufen, der Code entsteht nur einmal.
; Aufrufe: GK_MATH mul (vorher, wird von GK_SIN nicht doppelt erzeugt), dann GK_SIN dreimal an verschiedenen Stellen des Programms.
; Die Marken gk_sin, gk_add, gk_sub, gk_mul duerfen nur einmal vorkommen (sonst Doppeldefinition, rc 16); der Speicherbedarf
; ist der von GK_SIN allein (Kontrolle: Zelle 0003 ist die erste Zelle von GK_MATH add, vor dem Hauptprogramm bei 01000).
; Berechnet sin(1), sin(-1) und sin(0,5) (dwg) mit gk_sin; Sollwerte wie im Test gk_trigonomie_sin (Faelle 2, 3, 4).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
                start                ; Zaehlung beginnt bei 0000 (relativ)
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm (Hauptprogramm bei 01000)
                GK_MATH mul          ; erster Aufruf von GK_MATH: erzeugt gk_mul samt Kern und gemeinsamem Teil
                GK_SIN               ; erster Aufruf von GK_SIN: erzeugt gk_add, gk_sub (gk_mul gibt es schon) und gk_sin
                GK_SIN               ; zweiter Aufruf: erzeugt nichts
                equ     01000        ; Hauptprogramm ab relativ 01000
haupt:          211     x1           ; AC := x = 1
                240     gks_x        ; Parameter von gk_sin
                025     gk_sin       ; AC := sin(1)
                240     e1           ; Ergebnis 1
                GK_SIN               ; dritter Aufruf mitten im Ablauf: erzeugt nichts (und darf nicht in den Ablauf laufen)
                211     x2           ; AC := x = -1
                240     gks_x        ; Parameter von gk_sin
                025     gk_sin       ; AC := sin(-1)
                240     e2           ; Ergebnis 2
                211     x3           ; AC := x = 0,5
                240     gks_x        ; Parameter von gk_sin
                025     gk_sin       ; AC := sin(0,5)
                240     e3           ; Ergebnis 3
                020     0            ; Halt
x1:             dw      020600000000 ; x = 1 (dwg)
x2:             dw      060600000000 ; x = -1 (dwg)
x3:             dw      020200000000 ; x = 0,5 (dwg)
e1:             dw      0            ; Ergebnis sin(1)
e2:             dw      0            ; Ergebnis sin(-1)
e3:             dw      0            ; Ergebnis sin(0,5)
ende:           end                  ; Ende

; Sollwerte aus dem Test gk_trigonomie_sin (Faelle 2, 3, 4, bitgenaues Modell gk_modell/gk_sin_modell.py).
;#PRUEFE-START
; BZ=1015 AC=17765356417 US=1   # Halt auf 1014 nach dem dritten Aufruf von gk_sin; AC = sin(0,5)
; 1020: 20327325222   # e1 = sin(1)
; 1021: 60327325222   # e2 = sin(-1)
; 1022: 17765356417   # e3 = sin(0,5)
;#PRUEFE-ENDE
