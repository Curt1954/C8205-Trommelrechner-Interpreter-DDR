; makrowhilelabel.asm - Test der lokalen Labels (name%) und von $LOCAL im Rumpf von $WHILE (Assemblerdokumentation 4.19 und 4.20)
;#DOK-0001 Test lokale Labels und $LOCAL im Rumpf einer $WHILE-Schleife (je Durchlauf ein eigenes Label, $LOCAL erneut vereinbart)
;#PROT STUFE=2
; WA: Label und Sprung im Rumpf (3 Durchlaeufe), dazu ein Label hinter der Schleife, auf das der Rumpf nicht springt
WA:             MACRO
                $SET i 0
                $WHILE $V(i) < 3
schl%:          dw      1                       ; Label des Durchlaufs
                000     schl%                   ; Sprung auf das Label des eigenen Durchlaufs
                $INC i
                $ENDWHILE
                000     ende%                   ; Sprung auf ein Label hinter der Schleife
ende%:          dw      077                     ; Label ausserhalb des Rumpfes (wie bisher)
                MEND
; WB: Sprung vorwaerts auf ein Label im Rumpf (2 Durchlaeufe), das Label steht hinter dem Sprung
WB:             MACRO
                $SET i 0
                $WHILE $V(i) < 2
                000     vor%                    ; Sprung vorwaerts im selben Durchlauf
                dw      1                       ; uebersprungenes Wort
vor%:           dw      2                       ; Ziel des Sprungs
                $INC i
                $ENDWHILE
                MEND
; WC: zwei geschachtelte Schleifen, inn% in der inneren, aus% in der aeusseren (Zusatz je umschliessender Schleife, aeussere zuerst)
WC:             MACRO
                $SET a 0
                $WHILE $V(a) < 2
                $SET b 0
                $WHILE $V(b) < 2
inn%:           dw      $CALC($V(a)*10+$V(b))   ; Zehner a, Einer b
                000     inn%                    ; Sprung auf das Label des inneren Durchlaufs
                $INC b
                $ENDWHILE
aus%:           dw      077                     ; Label im Rumpf der aeusseren Schleife
                000     aus%                    ; Sprung auf das Label des aeusseren Durchlaufs
                $INC a
                $ENDWHILE
                MEND
; WD: $REPT im Rumpf von $WHILE: der Zusatz von $REPT (Z1) steht vor dem Zusatz des Durchlaufs
WD:             MACRO
                $SET i 0
                $WHILE $V(i) < 2
                $REPT 2
r%:             dw      $Z1                     ; Zaehler von $REPT
                000     r%                      ; Sprung auf das Label dieser Wiederholung
                $ENDREPT
                $INC i
                $ENDWHILE
                MEND
; SPR: Sprung auf das als Parameter uebergebene Label
SPR:            MACRO 1
                000     $1                      ; Sprung auf das uebergebene Label
                MEND
; WE: das Label des Durchlaufs wird als Parameter an ein verschachtelt aufgerufenes Makro uebergeben
WE:             MACRO
                $SET i 0
                $WHILE $V(i) < 2
tag%:           dw      5                       ; Label des Durchlaufs
                SPR     tag%                    ; Aufruf mit dem fertigen Label des Durchlaufs
                $INC i
                $ENDWHILE
                MEND
; WF: $LOCAL im Rumpf: Variable t und Feld fe(2) beginnen in jedem Durchlauf neu mit 0
WF:             MACRO
                $SET i 0
                $WHILE $V(i) < 3
                $LOCAL t fe(2)
                $INC t
                $INC t
                $SET fe(0) $CALC($V(fe(0))+1)
                $SET fe(1) $V(i)
                dw      $CALC($V(t)*100+$V(fe(0))*10+$V(fe(1)))   ; t, fe(0), fe(1) hintereinander
                $INC i
                $ENDWHILE
                MEND
; WG: ein lokales Feld mit je Durchlauf anderer Anzahl (2, 3, 4) wird neu angelegt
WG:             MACRO
                $SET i 0
                $WHILE $V(i) < 3
                $LOCAL g($CALC($V(i)+2))
                dw      $V(@g)                  ; Anzahl der Elemente
                $INC i
                $ENDWHILE
                MEND
; WH: ein lokales Feld mit gleicher Anzahl wird bei erneuter Vereinbarung auf 0 gesetzt
WH:             MACRO
                $SET i 0
                $WHILE $V(i) < 2
                $LOCAL h(2)
                dw      $V(h(1))                ; nach der Vereinbarung immer 0
                $SET h(1) 9
                $INC i
                $ENDWHILE
                MEND
                start                           ; Zaehlung beginnt bei 0000
                000     haupt                   ; Zelle 0000: Sprung zum Hauptprogramm
                WA                              ; Zellen 0001 bis 0010
                WB                              ; Zellen 0011 bis 0016
                WC                              ; Zellen 0017 bis 0032
                WD                              ; Zellen 0033 bis 0042
                WE                              ; Zellen 0043 bis 0046
                WF                              ; Zellen 0047 bis 0051
                WG                              ; Zellen 0052 bis 0054
                WH                              ; Zellen 0055 und 0056
haupt:          164     0001                    ; Zelle 0057: Diagnoseausgabe (nur im Test)
                020     0                       ; Zelle 0060: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Adressen oktal; ein Sprung 000 <ziel> ergibt die Zelle <ziel>*01000, also Zieladresse und drei Nullen):
; Zelle 0000 springt auf haupt = 0057, also 57000.
; WA: Durchlauf 0: schl_0 = 0001 (dw 1), 0002 springt dorthin = 1000; Durchlauf 1: schl_1 = 0003, 0004 = 3000; Durchlauf 2: schl_2 = 0005, 0006 = 5000;
;     0007 springt auf ende = 0010 = 10000; 0010 = 077.
; WB: Durchlauf 0: 0011 springt auf vor_0 = 0013 = 13000, 0012 = 1, 0013 = 2; Durchlauf 1: 0014 springt auf vor_1 = 0016 = 16000, 0015 = 1, 0016 = 2.
; WC: a=0,b=0: 0017 = 0, 0020 = 17000; a=0,b=1: 0021 = 1, 0022 = 21000; aus_0: 0023 = 077, 0024 = 23000;
;     a=1,b=0: 0025 = 10 dezimal = 012, 0026 = 25000; a=1,b=1: 0027 = 11 dezimal = 013, 0030 = 27000; aus_1: 0031 = 077, 0032 = 31000.
; WD: i=0: Z1=0: 0033 = 0, 0034 = 33000; Z1=1: 0035 = 1, 0036 = 35000; i=1: Z1=0: 0037 = 0, 0040 = 37000; Z1=1: 0041 = 1, 0042 = 41000.
; WE: Durchlauf 0: tag_0 = 0043 (dw 5), 0044 = 43000; Durchlauf 1: tag_1 = 0045 (dw 5), 0046 = 45000.
; WF: t = 2 und fe(0) = 1 in jedem Durchlauf (Neubeginn mit 0), fe(1) = i: 2*100 + 1*10 + i = 210, 211, 212 dezimal = 322, 323, 324 oktal.
; WG: Anzahlen 2, 3, 4. WH: zweimal 0 (ohne Neubeginn waere der zweite Wert 9).
; Halt auf 0060, BZ danach 0061.
;#PRUEFE-START
; BZ=0061 US=1
; 0000: 00000057000   # Sprung auf haupt
; 0001: 00000000001   # WA schl_0
; 0002: 00000001000   # WA Sprung auf 0001
; 0003: 00000000001   # WA schl_1
; 0004: 00000003000   # WA Sprung auf 0003
; 0005: 00000000001   # WA schl_2
; 0006: 00000005000   # WA Sprung auf 0005
; 0007: 00000010000   # WA Sprung auf ende = 0010
; 0010: 00000000077   # WA ende
; 0011: 00000013000   # WB Sprung auf vor_0 = 0013
; 0012: 00000000001   # WB uebersprungenes Wort
; 0013: 00000000002   # WB vor_0
; 0014: 00000016000   # WB Sprung auf vor_1 = 0016
; 0015: 00000000001   # WB uebersprungenes Wort
; 0016: 00000000002   # WB vor_1
; 0017: 00000000000   # WC a=0 b=0 inn_0_0
; 0020: 00000017000   # WC Sprung auf 0017
; 0021: 00000000001   # WC a=0 b=1 inn_0_1
; 0022: 00000021000   # WC Sprung auf 0021
; 0023: 00000000077   # WC aus_0
; 0024: 00000023000   # WC Sprung auf 0023
; 0025: 00000000012   # WC a=1 b=0 inn_1_0 (10 dezimal)
; 0026: 00000025000   # WC Sprung auf 0025
; 0027: 00000000013   # WC a=1 b=1 inn_1_1 (11 dezimal)
; 0030: 00000027000   # WC Sprung auf 0027
; 0031: 00000000077   # WC aus_1
; 0032: 00000031000   # WC Sprung auf 0031
; 0033: 00000000000   # WD i=0 Z1=0
; 0034: 00000033000   # WD Sprung auf 0033
; 0035: 00000000001   # WD i=0 Z1=1
; 0036: 00000035000   # WD Sprung auf 0035
; 0037: 00000000000   # WD i=1 Z1=0
; 0040: 00000037000   # WD Sprung auf 0037
; 0041: 00000000001   # WD i=1 Z1=1
; 0042: 00000041000   # WD Sprung auf 0041
; 0043: 00000000005   # WE tag_0
; 0044: 00000043000   # WE Sprung auf 0043 (Label als Parameter)
; 0045: 00000000005   # WE tag_1
; 0046: 00000045000   # WE Sprung auf 0045 (Label als Parameter)
; 0047: 00000000322   # WF Durchlauf 0: 210 dezimal
; 0050: 00000000323   # WF Durchlauf 1: 211 dezimal
; 0051: 00000000324   # WF Durchlauf 2: 212 dezimal
; 0052: 00000000002   # WG Anzahl 2
; 0053: 00000000003   # WG Anzahl 3
; 0054: 00000000004   # WG Anzahl 4
; 0055: 00000000000   # WH Durchlauf 0
; 0056: 00000000000   # WH Durchlauf 1 (Elemente auf 0 gesetzt)
;#PRUEFE-ENDE
