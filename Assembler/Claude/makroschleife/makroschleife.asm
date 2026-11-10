; makroschleife.asm - Test der Schleife $REPT/$ENDREPT und der geschachtelten Bedingung $IF/$ELIF/$ELSE/$ENDIF im Makro-Praeprozessor
;                     (Assemblerdokumentation 4.3 und 4.4)
;#DOK-0001 Test der Makro-Schleife und der geschachtelten Bedingungen: Zaehler $Z1/$Z2, Schleifen im $IF, $IF im $IF, $ELSE, Klammern, bis zu acht Bedingungsbloecke
;#PROT STUFE=2
; Schleife mit Zaehler: acht Worte, Wort k = k mal Parameter
TAB8:           MACRO 1
                $REPT 8
                dw      $CALC($Z1*$1)   ; Wort $Z1: Zaehler mal Schrittweite
                $ENDREPT
                MEND
; Zwei geschachtelte Schleifen: aussen $Z1 = 0..2, innen $Z2 = 0..1; Wort = 10*$Z1 + $Z2
MATRIX:         MACRO
                $REPT 3
                $REPT 2
                dw      $CALC($Z1*10+$Z2)   ; Zeile $Z1, Spalte $Z2
                $ENDREPT
                $ENDREPT
                MEND
; Geschachteltes $IF mit $ELSE: Vorzeichen zweier Parameter (1 = beide positiv, 2 = nur der erste, 3 = nur der zweite, 4 = keiner)
IFN:            MACRO 2
                $IF $1 > 0
                  $IF $2 > 0
                dw      1               ; beide positiv
                  $ELSE
                dw      2               ; nur der erste positiv
                  $ENDIF
                $ELSE
                  $IF $2 > 0
                dw      3               ; nur der zweite positiv
                  $ELSE
                dw      4               ; keiner positiv
                  $ENDIF
                $ENDIF
                MEND
; $IF, $ELIF und $ELSE nebeneinander
KLASSE:         MACRO 1
                $IF $1 = 0
                dw      100             ; null
                $ELIF $1 = 1
                dw      101             ; eins
                $ELSE
                dw      102             ; sonst
                $ENDIF
                MEND
; Schleife mit Anzahl aus dem Parameter und $IF im Rumpf: gerader Zaehler -> Zaehler, ungerader -> Zaehler + 100
MISCH:          MACRO 1
                $REPT $1
                $IF $CALC($Z1%2) = 0
                dw      $Z1             ; gerader Zaehler
                $ELSE
                dw      $CALC($Z1+100)  ; ungerader Zaehler plus 100
                $ENDIF
                $ENDREPT
                MEND
; Klammern: (p1 = 1 oder p2 = 1) und p3 = 1
KL:             MACRO 3
                $IF ( $1 = 1 | $2 = 1 ) & $3 = 1
                dw      1               ; Bedingung erfuellt
                $ELSE
                dw      0               ; Bedingung nicht erfuellt
                $ENDIF
                MEND
; sechs Bedingungsbloecke mit ODER
SECHS:          MACRO 1
                $IF $1 = 1 | $1 = 2 | $1 = 3 | $1 = 4 | $1 = 5 | $1 = 6
                dw      1               ; Wert 1 bis 6
                $ELSE
                dw      0               ; anderer Wert
                $ENDIF
                MEND
; Vergleichszeichen !=
UNGL:           MACRO 1
                $IF $1 != 0
                dw      1               ; ungleich null
                $ELSE
                dw      0               ; gleich null
                $ENDIF
                MEND
; Labels mit Zaehler (w0, w1, w2) in der Schleife; Schleife mit null Durchlaeufen erzeugt nichts
LABELS:         MACRO
                $REPT 3
w$Z1:           dw      $CALC($Z1+7)    ; Label w$Z1 mit dem Wert 7 plus Zaehler
                $ENDREPT
                $REPT 0
                dw      99              ; nie erzeugt
                $ENDREPT
                MEND
; Code aus einer Schleife: der Aufruf erzeugt n mal "210 eins" (AC := AC + 1)
ADDIERE:        MACRO 1
                $REPT $1
                210     eins            ; AC := AC + 1 (Durchlauf $Z1)
                $ENDREPT
                MEND
; Generisches Label in der Schleife: jeder Durchlauf erhaelt sein eigenes Label (ML0001%_0, _1, _2); Sprung zur naechsten Zelle
SPRUENGE:       MACRO
                $REPT 3
                000     ML0001%         ; Sprung zur naechsten Zelle (Durchlauf $Z1)
ML0001%:        210     eins            ; AC := AC + 1
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TAB8    3            ; Zellen 0001 bis 0010: 0, 3, 6, ... 21
                MATRIX               ; Zellen 0011 bis 0016: 0, 1, 10, 11, 20, 21
                IFN     1  1         ; Zelle 0017
                IFN     1  0         ; Zelle 0020
                IFN     0  1         ; Zelle 0021
                IFN     0  0         ; Zelle 0022
                KLASSE  0            ; Zelle 0023
                KLASSE  1            ; Zelle 0024
                KLASSE  5            ; Zelle 0025
                MISCH   5            ; Zellen 0026 bis 0032: 0, 101, 2, 103, 4
                KL      1  0  1      ; Zelle 0033
                KL      0  0  1      ; Zelle 0034
                KL      0  1  1      ; Zelle 0035
                KL      1  1  0      ; Zelle 0036
                SECHS   6            ; Zelle 0037
                SECHS   7            ; Zelle 0040
                UNGL    0            ; Zelle 0041
                UNGL    5            ; Zelle 0042
                LABELS               ; Zellen 0043 bis 0045: 7, 8, 9
eins:           dw      1            ; Zelle 0046: Konstante 1
erg1:           dw      0            ; Zelle 0047: Ergebnis der Code-Schleife
erg2:           dw      0            ; Zelle 0050: Ergebnis mit den Labels w1 und w2
erg3:           dw      0            ; Zelle 0051: Ergebnis der Schleife mit Labels
haupt:          211     eins         ; AC := 1
                ADDIERE 3            ; dreimal AC := AC + 1, also AC := 4
                240     erg1         ; Ergebnis ablegen
                211     w1           ; AC := 8 (Label aus der Schleife)
                210     w2           ; AC := 8 + 9 = 17
                240     erg2         ; Ergebnis ablegen
                211     eins         ; AC := 1
                SPRUENGE             ; dreimal Sprung und AC := AC + 1, also AC := 4
                240     erg3         ; Ergebnis ablegen
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet (siehe Kommentar je Zelle); Halt auf 0073, BZ danach 0074.
;#PRUEFE-START
; BZ=0074 US=1
; 0001: 00000000000   # TAB8 3: Wort 0 = 0
; 0002: 00000000003   # Wort 1 = 3
; 0003: 00000000006   # Wort 2 = 6
; 0004: 00000000011   # Wort 3 = 9
; 0005: 00000000014   # Wort 4 = 12
; 0006: 00000000017   # Wort 5 = 15
; 0007: 00000000022   # Wort 6 = 18
; 0010: 00000000025   # Wort 7 = 21
; 0011: 00000000000   # MATRIX: 10*0+0
; 0012: 00000000001   # 10*0+1
; 0013: 00000000012   # 10*1+0 = 10
; 0014: 00000000013   # 10*1+1 = 11
; 0015: 00000000024   # 10*2+0 = 20
; 0016: 00000000025   # 10*2+1 = 21
; 0017: 00000000001   # IFN 1 1: beide positiv
; 0020: 00000000002   # IFN 1 0: nur der erste
; 0021: 00000000003   # IFN 0 1: nur der zweite
; 0022: 00000000004   # IFN 0 0: keiner
; 0023: 00000000144   # KLASSE 0: 100
; 0024: 00000000145   # KLASSE 1: 101
; 0025: 00000000146   # KLASSE 5: 102
; 0026: 00000000000   # MISCH 5: Zaehler 0 gerade -> 0
; 0027: 00000000145   # Zaehler 1 ungerade -> 101
; 0030: 00000000002   # Zaehler 2 gerade -> 2
; 0031: 00000000147   # Zaehler 3 ungerade -> 103
; 0032: 00000000004   # Zaehler 4 gerade -> 4
; 0033: 00000000001   # KL 1 0 1: (1|0)&1 = 1
; 0034: 00000000000   # KL 0 0 1: (0|0)&1 = 0
; 0035: 00000000001   # KL 0 1 1: (0|1)&1 = 1
; 0036: 00000000000   # KL 1 1 0: (1|1)&0 = 0
; 0037: 00000000001   # SECHS 6: im Bereich 1..6
; 0040: 00000000000   # SECHS 7: ausserhalb
; 0041: 00000000000   # UNGL 0: gleich null
; 0042: 00000000001   # UNGL 5: ungleich null
; 0043: 00000000007   # LABELS: w0 = 7
; 0044: 00000000010   # w1 = 8
; 0045: 00000000011   # w2 = 9
; 0047: 00000000004   # ADDIERE 3: 1 + 3 = 4
; 0050: 00000000021   # w1 + w2 = 8 + 9 = 17 (oktal 021)
; 0051: 00000000004   # SPRUENGE: 1 + 3 = 4 (drei Durchlaeufe mit eigenem Label)
;#PRUEFE-ENDE
