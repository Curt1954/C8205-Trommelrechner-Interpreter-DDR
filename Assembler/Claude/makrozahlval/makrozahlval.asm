; makrozahlval.asm - Test von $VALO (Text nach Zahl, oktal) neben $VAL und $IF (Assemblerdokumentation 4.22)
;#DOK-0001 Test $VALO: Ziffernfolgen, Grenzen, Beispiele 2 und 3, Rundreise, $VAL und $IF unveraendert
;#PROT STUFE=2
; VALOK: $VALO liest oktal: mit und ohne fuehrende Nullen, negativ, Null, groesste Zahl (Z-10, Z-11, E-04)
VALOK:          MACRO
                $VALO n "17"
                dw      $V(n)                   ; 17 oktal = 15
                $VALO n "017"
                dw      $V(n)                   ; 017 = 15
                $VALO n "00017"
                dw      $V(n)                   ; 00017 = 15
                $VALO n "0"
                dw      $V(n)                   ; 0
                $VALO n "-17"
                dw      $CALC($V(n)+100)        ; -15 + 100 = 85
                $VALO n "7"
                dw      $V(n)                   ; 7
                $VALO n "777"
                dw      $V(n)                   ; 777 oktal = 511
                $VALO n "0777777777777777777777"
                dw      $CALC($V(n)/01000000000000000000)    ; 2^63-1 geteilt durch 2^54 = 511 (ganzzahlig)
                $VALO n "777777777777777777777"
                dw      $CALC($V(n)-9223372036854775800) ; 2^63-1 minus (2^63-8) = 7
                MEND
; OKTSUMME: zwei Oktalzahlen ohne fuehrende 0 aus einem Parameter addieren (Beispiel 2): 15 + 17 = 32
OKTSUMME:       MACRO 1
                $INDEX p "$1" " "               ; Position des Leerzeichens
                $SUBSTR a "$1" 1 $CALC($V(p)-1) ; erste Zahl als Text
                $SUBSTR b "$1" $CALC($V(p)+1)   ; zweite Zahl als Text
                $VALO x "$V(a)"                 ; oktal gelesen
                $VALO y "$V(b)"
                dw      $CALC($V(x)+$V(y))      ; Summe 32
                MEND
; RUNDE: Rundreise Zahl, Oktaltext, Zahl (Beispiel 3, Z-13)
RUNDE:          MACRO
                $SET n 15
                $SET t "$CALCO($V(n))"          ; Text 017
                $VALO r "$V(t)"                 ; oktal zurueck
                $VAL s "$V(t)"                  ; dezimal (bisheriges Verhalten)
                dw      $V(#t)                  ; 3
                dw      $V(r)                   ; 15
                dw      $V(s)                   ; 17
                MEND
; UNVER: $VAL, $SET und $IF lesen die Ziffernfolge 017 wie bisher (Z-14, E-07, Tabelle in 4.22)
UNVER:          MACRO
                $SET c "017"
                $VAL d "$V(c)"
                dw      $V(d)                   ; $VAL liest dezimal: 17
                $SET m $V(c)
                dw      $V(m)                   ; Ausdruck liest oktal: 15
                $IF $V(c) = 17
                dw      1                       ; $IF liest dezimal: 17 ist wahr
                $ELSE
                dw      0
                $ENDIF
                $IF $V(c) = 15
                dw      1
                $ELSE
                dw      0                       ; 15 ist unwahr
                $ENDIF
                $VAL d "-0012"
                dw      $CALC($V(d)+100)        ; Bestand makrostrzeichen: -12 + 100 = 88
                MEND
; RUNDEN: Rundreise fuer n = 0 bis 100 in beiden Schreibweisen ($CALCO und $CALCO5) und fuer 2^63-1 (Z-13)
RUNDEN:         MACRO
                $SET ok 0
                $SET n 0
                $WHILE $V(n) <= 100
                $SET t "$CALCO($V(n))"
                $VALO r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $SET t "$CALCO5($V(n))"
                $VALO r "$V(t)"
                $IF $V(r) = $V(n)
                $INC ok
                $ENDIF
                $INC n
                $ENDWHILE
                dw      $V(ok)                  ; 101 Werte, je zwei Pruefungen: 202
                $SET g 9223372036854775807
                $SET t "$CALCO($V(g))"          ; 0 und 21 Siebenen
                dw      $V(#t)                  ; 22 Zeichen
                $VALO r "$V(t)"
                $SET d $CALC($V(r)-$V(g))
                dw      $V(d)                   ; gleiche Zahl zurueck: Unterschied 0
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                VALOK                ; Zellen 1 bis 9 (dezimal)
                OKTSUMME "17 21"     ; Zelle 10
                RUNDE                ; Zellen 11 bis 13
                UNVER                ; Zellen 14 bis 18
                RUNDEN               ; Zellen 19 bis 21
haupt:          164     0001         ; Zelle 22: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 23: Halt
ende:           end
; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal); haupt = Zelle 22 (oktal 0026), Halt in Zelle 23, BZ danach 0030.
;#PRUEFE-START
; BZ=0030 US=1
; 0001: 00000000017   # VALOK: 17 oktal
; 0002: 00000000017   # VALOK: 017
; 0003: 00000000017   # VALOK: 00017
; 0004: 00000000000   # VALOK: 0
; 0005: 00000000125   # VALOK: -17 + 100
; 0006: 00000000007   # VALOK: 7
; 0007: 00000000777   # VALOK: 777 oktal
; 0010: 00000000777   # VALOK: groesste Zahl durch 2^54
; 0011: 00000000007   # VALOK: groesste Zahl minus 2^63-8
; 0012: 00000000040   # OKTSUMME: 15 + 17
; 0013: 00000000003   # RUNDE: Text 017 hat 3 Zeichen
; 0014: 00000000017   # RUNDE: $VALO
; 0015: 00000000021   # RUNDE: $VAL dezimal
; 0016: 00000000021   # UNVER: $VAL 017 dezimal
; 0017: 00000000017   # UNVER: $SET liest oktal
; 0020: 00000000001   # UNVER: $IF 017 = 17 wahr
; 0021: 00000000000   # UNVER: $IF 017 = 15 unwahr
; 0022: 00000000130   # UNVER: -0012 + 100
; 0023: 00000000312   # RUNDEN: 202 gelungene Rundreisen
; 0024: 00000000026   # RUNDEN: 2^63-1 hat 22 Zeichen
; 0025: 00000000000   # RUNDEN: Unterschied 0
;#PRUEFE-ENDE
