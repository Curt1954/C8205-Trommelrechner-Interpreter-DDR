; makrozellen.asm - Test: Zellenzahl eines mehrzeiligen Blocks, zellen(von,bis) im Makro (Assemblerdokumentation 4.23, c82ass ab 1.01-012);
;                   der Quelltext hat keine $-Zeile (Pass 0 ohne Vorabauswertung)
;#DOK-0001 Test: PAAR liefert zellen(von,bis) und den echten Abstand bis-von; FOLGE erzeugt so viele Woerter wie der Block Zellen hat; SCHALTER, DREI
;#PROT STUFE=2
PAAR:           MACRO   2
                dw      $CALC(zellen($1,$2))        ; Zellenzahl des Blocks in Pass 0 ($1,$2 werden eingeklammert eingesetzt)
                dw      $2-$1                       ; echter Abstand der beiden Marken nach Pass 2: muss gleich sein
                MEND
FOLGE:          MACRO   2
                $REPT   $CALC(zellen($1,$2))        ; Tabellenlaenge aus mehreren Zeilen: so viele Woerter wie der Block Zellen hat
                dw      $Z1                         ; 0, 1, 2, ...
                $ENDREPT
                MEND
SCHALTER:       MACRO
                $IF     $CALC(zellen(tab_a,tab_e)) > 8
                dw      1                           ; Block groesser als 8 Zellen
                $ELSE
                dw      0
                $ENDIF
                MEND
DREI:           MACRO
                dw      $CALC(zellen(b_von,b_bis)-zellen(tab_a,tab_e))   ; 11-9 = 2
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                PAAR    tab_a tab_e  ; Zellen 0001 und 0002: Block A, 9 Zellen
                PAAR    b_von b_bis  ; Zellen 0003 und 0004: Block B, 11 Zellen
                PAAR    c_von c_bis  ; Zellen 0005 und 0006: Block C, 0 Zellen
                PAAR    tab_a b_von  ; Zellen 0007 und 0010: Block A samt tab_e, 10 Zellen
                PAAR    marke_allein tab_e ; Zellen 0011 und 0012: nur eine Marke allein und abs, 0 Zellen
                FOLGE   tab_a tab_e  ; Zellen 0013 bis 0023: 9 Woerter 0 bis 8
                SCHALTER             ; Zelle 0024
                DREI                 ; Zelle 0025
haupt:          020     0            ; Zelle 0026: Halt
; Block A: db 5 (5 Zellen), zwei dw (2), zwei Befehle (2); die Kommentarzeile, die Marke allein und das abs zaehlen nicht
tab_a:          db      5            ; 5 Zellen
                dw      1            ; 1 Zelle
                dw      2            ; 1 Zelle
; Kommentarzeile im Block: null Zellen
                211     0            ; 1 Zelle
                240     0            ; 1 Zelle
marke_allein:                        ; Marke allein: null Zellen
w_abs:          abs     7            ; abs belegt keine Zelle
tab_e:          dw      3            ; hier endet Block A (diese Zeile zaehlt nicht mehr)
; Block B: dbn 3 (3 Zellen), da (1), db 06 (6 Zellen, oktal), dw (1)
b_von:          dbn     3            ; 3 Zellen
                da      tab_a        ; 1 Zelle
                db      06           ; 6 Zellen
                dw      1            ; 1 Zelle
b_bis:          dw      0            ; hier endet Block B
; Block C: nur eine Marke allein und ein abs, null Zellen
c_von:                               ; Marke allein
w_abs2:         abs     3            ; abs
c_bis:          dw      0            ; hier endet Block C
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0026, BZ danach 0027.
; Block A: 5+1+1+1+1 = 9; Block B: 3+1+6+1 = 11 = 013; Block C: 0; tab_a bis b_von: 9 + tab_e (dw 3) = 10 = 012; marke_allein bis tab_e: 0.
; Der echte Abstand (zweites Wort jedes PAAR) ist gleich. FOLGE: Zaehler 0 bis 8. SCHALTER: 9 > 8 -> 1. DREI: 11-9 = 2.
;#PRUEFE-START
; BZ=0027 US=1
; 0001: 00000000011   # zellen(tab_a,tab_e) = 9
; 0002: 00000000011   # Abstand tab_e-tab_a = 9
; 0003: 00000000013   # zellen(b_von,b_bis) = 11
; 0004: 00000000013   # Abstand = 11
; 0005: 00000000000   # zellen(c_von,c_bis) = 0
; 0006: 00000000000   # Abstand = 0
; 0007: 00000000012   # zellen(tab_a,b_von) = 10
; 0010: 00000000012   # Abstand = 10
; 0011: 00000000000   # zellen(marke_allein,tab_e) = 0
; 0012: 00000000000   # Abstand = 0
; 0013: 00000000000   # FOLGE Durchlauf 0
; 0014: 00000000001   # Durchlauf 1
; 0015: 00000000002   # Durchlauf 2
; 0016: 00000000003   # Durchlauf 3
; 0017: 00000000004   # Durchlauf 4
; 0020: 00000000005   # Durchlauf 5
; 0021: 00000000006   # Durchlauf 6
; 0022: 00000000007   # Durchlauf 7
; 0023: 00000000010   # Durchlauf 8
; 0024: 00000000001   # SCHALTER: 9 > 8
; 0025: 00000000002   # DREI: 11-9
;#PRUEFE-ENDE
