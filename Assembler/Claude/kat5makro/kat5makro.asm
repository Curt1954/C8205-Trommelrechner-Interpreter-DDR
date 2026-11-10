; kat5makro.asm - Test: kat5 im Makro (Marke $wrzl im Makrotext, Text als Aufrufparameter), Doku 3.3.15 und 4
;#PROT STUFE=2
ZEILE:          MACRO 0
                kat5    ab$wrzl      ; Text mit Marke fest im Makro
                MEND
TXT:            MACRO 1
                kat5    $1           ; Text aus dem Aufrufparameter
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
m1:             ZEILE                ; Zelle 0001: a, b, $wrzl
m2:             TXT     welt         ; Zelle 0002: w e l t
haupt:          020     0            ; Zelle 0003: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Codes nach Doku 3.3.15: a = 021, b = 022, $wrzl = 053, w = 047, e = 025, l = 034, t = 044;
; erstes Zeichen links in z3 bis z8, 2 Oktalziffern je Zeichen, Fuellung 00 rechts, z0 bis z2 = 0).
; m1: a b $wrzl = 0 21 22 53 00 00 = 02122530000. m2: w e l t = 0 47 25 34 44 00 = 04725344400.
;#PRUEFE-START
; BZ=0004
; 0001: 02122530000   # m1
; 0002: 04725344400   # m2
;#PRUEFE-ENDE
