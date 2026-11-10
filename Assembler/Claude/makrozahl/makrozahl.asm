; makrozahl.asm - Test von $CALC, $CALCO, $CALCOn im Text von $SET und in Textargumenten (Assemblerdokumentation 4.22)
;#DOK-0001 Test Rechenausdruecke im Text: Oktaltext aus Variable, Parameter, gemischt, Textargumente der Zeichenkettenfunktionen, Feldelement, lokale Variable, Marken mit Oktalnummer
;#PROT STUFE=2
; TAB3: drei Woerter mit Marken, deren Name die Nummer in Oktalschreibung traegt (Beispiel 1, Z-01 mit Variable im $CALCO)
TAB3:           MACRO
                $LOCAL i nm
                $SET i 7
                $WHILE $V(i) <= 9
                $SET nm "$CALCO2($V(i))"        ; Oktaltext der Breite 2: 007, 010, 011
z$V(nm):        dw      $V(i)                   ; Marke z007, z010, z011
                $INC i
                $ENDWHILE
                MEND
; TXTSET: $CALC, $CALCO, $CALCOn im Text von $SET mit Konstante, Variable, Parameter und gemischt (Z-01); n = 15; Parameter 8, $CALC(2+5), 4
TXTSET:         MACRO 3
                $SET n 15
                $SET t "$CALCO($V(n))"          ; Variable: Text 017
                dw      $V(#t)                  ; 3 Zeichen
                $STRCMP r "$V(t)" "017"
                dw      $V(r)                   ; gleich: 0
                $SET t "$CALC($V(n)+1)"         ; Text 16
                dw      $V(#t)                  ; 2 Zeichen
                $VAL v "$V(t)"
                dw      $V(v)                   ; 16
                $SET t "x$CALCO4($V(n))y"       ; x00017y, Breite 4 mit fuehrender 0
                dw      $V(#t)                  ; 1 + 5 + 1 = 7 Zeichen
                $SET t "$CALCO($1+$V(n))"       ; Parameter 8 und Variable: 23 = 027 oktal
                dw      $V(#t)                  ; 3 Zeichen
                $STRCMP r "$V(t)" "027"
                dw      $V(r)                   ; gleich: 0
                $SET t "$2"                     ; Parameter $CALC(2+5) wird im Text zu 7
                dw      $V(#t)                  ; 1 Zeichen
                $VAL v "$V(t)"
                dw      $V(v)                   ; 7
                $SET t "$CALC($V(n)+$3)"        ; Variable und Parameter: 15 + 4 = 19
                $VAL v "$V(t)"
                dw      $V(v)                   ; 19
                dw      $V(#t)                  ; 2 Zeichen
                $SET t "ab$V(n)"                ; ohne $CALC bleibt der Text gleich: ab15
                dw      $V(#t)                  ; 4 Zeichen
                $STRCMP r "$V(t)" "ab15"
                dw      $V(r)                   ; gleich: 0
                $SET t "$CALC(0-$V(n))"         ; negatives Ergebnis -15
                dw      $V(#t)                  ; 3 Zeichen
                $VAL v "$V(t)"
                dw      $CALC($V(v)+100)        ; -15 + 100 = 85
                MEND
; TXTARG: $CALC, $CALCO in den Textargumenten der Zeichenkettenfunktionen (Z-02); n = 15
TXTARG:         MACRO
                $SET n 15
                $STRCMP r "$CALCO($V(n))" "017"
                dw      $V(r)                   ; 017 gleich 017: 0
                $STRCMP r "$CALCO($V(n)+1)" "017"
                dw      $V(r)                   ; 020 gegen 017: 1
                $SUBSTR s "$CALCO($V(n))" 2 2   ; Zeichen 2 und 3 von 017: 17
                dw      $V(#s)                  ; 2 Zeichen
                $VAL v "$V(s)"
                dw      $V(v)                   ; dezimal gelesen: 17
                $VALO v "$V(s)"
                dw      $V(v)                   ; oktal gelesen: 15
                $INDEX p "$CALCO($V(n))" "7"
                dw      $V(p)                   ; die 7 steht an Position 3
                $UPPER u "a$CALC(1+$V(n))"      ; a16 wird A16
                $STRCMP r "$V(u)" "A16"
                dw      $V(r)                   ; gleich: 0
                $LOWER u "X$CALC(1+1)"          ; X2 wird x2
                $STRCMP r "$V(u)" "x2"
                dw      $V(r)                   ; gleich: 0
                $ORD o "$CALC(60+$V(n))"        ; Text 75, erstes Zeichen 7 hat den Code 55
                dw      $V(o)                   ; 55
                MEND
; FELDLOK: Ziel als Feldelement und als lokale Variable (Z-01, 4.17 und 4.20); n = 15
FELDLOK:        MACRO
                $LOCAL loc
                $DIM f 3
                $SET n 15
                $SET f(1) "$CALCO($V(n))"       ; Feldelement: Text 017
                dw      $V(#f(1))               ; 3 Zeichen
                $VALO v "$V(f(1))"
                dw      $V(v)                   ; 15
                $SET f(2) "$CALC($V(n)+$V(@f))" ; Elementzahl 3: 15 + 3 = 18
                dw      $V(#f(2))               ; 2 Zeichen
                $VAL v "$V(f(2))"
                dw      $V(v)                   ; 18
                $SET loc "$CALCO($V(n)*2)"      ; lokale Variable: 30 = 036 oktal
                dw      $V(#loc)                ; 3 Zeichen
                $VALO v "$V(loc)"
                dw      $V(v)                   ; 30
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TAB3                 ; Zellen 1 bis 3 (dezimal)
                TXTSET  8 $CALC(2+5) 4   ; Zellen 4 bis 18 (dezimal)
                TXTARG               ; Zellen 19 bis 27 (dezimal)
                FELDLOK              ; Zellen 28 bis 33 (dezimal)
                dw      z010-z007    ; Zelle 34: Marken aus TAB3 liegen eine Zelle auseinander
                dw      z011-z007    ; Zelle 35: und zwei Zellen
haupt:          164     0001         ; Zelle 36: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 37: Halt
ende:           end
; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal); haupt = Zelle 36 (oktal 0044), Halt in Zelle 37, BZ danach 0046.
;#PRUEFE-START
; BZ=0046 US=1
; 0001: 00000000007   # TAB3: Wort 7 (Marke z007)
; 0002: 00000000010   # TAB3: Wort 8 (Marke z010)
; 0003: 00000000011   # TAB3: Wort 9 (Marke z011)
; 0004: 00000000003   # TXTSET: 017 hat 3 Zeichen
; 0005: 00000000000   # TXTSET: Text gleich 017
; 0006: 00000000002   # TXTSET: 16 hat 2 Zeichen
; 0007: 00000000020   # TXTSET: 16
; 0010: 00000000007   # TXTSET: x00017y hat 7 Zeichen
; 0011: 00000000003   # TXTSET: 027 aus Parameter und Variable hat 3 Zeichen
; 0012: 00000000000   # TXTSET: Text gleich 027
; 0013: 00000000001   # TXTSET: Parameter $CALC(2+5) ergibt 1 Zeichen
; 0014: 00000000007   # TXTSET: Parameter $CALC(2+5) ergibt 7
; 0015: 00000000023   # TXTSET: Variable plus Parameter 15 + 4
; 0016: 00000000002   # TXTSET: 19 hat 2 Zeichen
; 0017: 00000000004   # TXTSET: ab15 ohne $CALC hat 4 Zeichen
; 0020: 00000000000   # TXTSET: Text gleich ab15
; 0021: 00000000003   # TXTSET: -15 hat 3 Zeichen
; 0022: 00000000125   # TXTSET: -15 + 100
; 0023: 00000000000   # TXTARG: 017 gleich 017
; 0024: 00000000001   # TXTARG: 020 groesser als 017
; 0025: 00000000002   # TXTARG: Teilstring 17 hat 2 Zeichen
; 0026: 00000000021   # TXTARG: $VAL liest 17 dezimal
; 0027: 00000000017   # TXTARG: $VALO liest 17 oktal
; 0030: 00000000003   # TXTARG: die 7 steht an Position 3
; 0031: 00000000000   # TXTARG: $UPPER a16 gleich A16
; 0032: 00000000000   # TXTARG: $LOWER X2 gleich x2
; 0033: 00000000067   # TXTARG: Code der Ziffer 7
; 0034: 00000000003   # FELDLOK: Feldelement 017 hat 3 Zeichen
; 0035: 00000000017   # FELDLOK: Feldelement oktal gelesen
; 0036: 00000000002   # FELDLOK: Feldelement 18 hat 2 Zeichen
; 0037: 00000000022   # FELDLOK: Feldelement 15 + 3
; 0040: 00000000003   # FELDLOK: lokale Variable 036 hat 3 Zeichen
; 0041: 00000000036   # FELDLOK: lokale Variable oktal gelesen
; 0042: 00000000001   # Marken: z010 - z007
; 0043: 00000000002   # Marken: z011 - z007
;#PRUEFE-ENDE
