; makrostrsplit.asm - Test der Beispiele SPLIT und ANZAHL und der Ziele Feldelement und lokales Feld (Assemblerdokumentation 4.21)
;#DOK-0001 Test Zeichenketten: Parameter name=wert zerlegen, Buchstaben zaehlen, Zeichenfolge in ein Feld zerlegen und rueckwaerts ausgeben
;#PROT STUFE=2
; SPLIT: trennt den Parameter schluessel=wert; erzeugt die Laenge des Schluessels und den Wert als Zahl (Beispiel 1 aus 4.21)
SPLIT:          MACRO 1
                $INDEX p "$1" "="                 ; Position des Gleichheitszeichens
                $SUBSTR k "$1" 1 $CALC($V(p)-1)   ; Schluessel
                $SUBSTR w "$1" $CALC($V(p)+1)     ; Wert, bis zum Ende
                dw      $V(#k)                    ; Laenge des Schluessels
                dw      $V(w)                     ; Wert als Zahl
                MEND
; ANZAHL: zaehlt die Vorkommen des Buchstabens A im Parameter, ohne Ruecksicht auf Gross-/Kleinschreibung (Beispiel 2 aus 4.21)
ANZAHL:         MACRO 1
                $LOCAL i n t z
                $UPPER t "$1"                     ; t in Grossbuchstaben
                $SET i 1
                $WHILE $V(i) <= $V(#t)
                $SUBSTR z "$V(t)" $V(i) 1         ; ein Zeichen
                $IF $V(z) = A
                $INC n
                $ENDIF
                $INC i
                $ENDWHILE
                dw      $V(n)                     ; Anzahl der A
                MEND
; FELDZ: Ziel ist ein Feldelement (globales Feld f mit 3 Elementen); $VAL liest ein Textelement als Zahl
FELDZ:          MACRO
                $DIM f 3
                $INDEX f(0) "abc=42" "="          ; f(0) = 4
                $SUBSTR f(1) "abc=42" 5           ; f(1) = Text 42
                $VAL f(2) "$V(f(1))"              ; f(2) = Zahl 42
                dw      $V(f(0))                  ; 4
                dw      $V(#f(1))                 ; Textlaenge 2
                dw      $V(f(2))                  ; 42
                MEND
; ZERLEG: zerlegt den Parameter in ein lokales Feld (ein Zeichen je Element, Index als $V(i)) und gibt die Zeichencodes rueckwaerts aus
ZERLEG:         MACRO 1
                $LOCAL f(8) i t o
                $SET t "$1"
                $SET i 0
                $WHILE $V(i) < $V(#t)
                $SUBSTR f($V(i)) "$V(t)" $CALC($V(i)+1) 1   ; Zeichen i+1 in Element i
                $INC i
                $ENDWHILE
                $WHILE $V(i) > 0
                $SET i $CALC($V(i)-1)
                $ORD o "$V(f($V(i)))"             ; Code des Elements
                dw      $V(o)                     ; rueckwaerts ausgegeben
                $ENDWHILE
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                SPLIT   abc=42       ; Zellen 1 und 2: 3, 42
                SPLIT   x=7          ; Zellen 3 und 4: 1, 7
                SPLIT   schluessel=123 ; Zellen 5 und 6: 10, 123
                SPLIT   ab=0         ; Zellen 7 und 8: 2, 0
                ANZAHL  "Banane"     ; Zelle 9: 2
                ANZAHL  "Ananas"     ; Zelle 10: 3
                ANZAHL  "xyz"        ; Zelle 11: 0
                ANZAHL  "AaAa"       ; Zelle 12: 4
                FELDZ                ; Zellen 13 bis 15: 4, 2, 42
                ZERLEG  ABC          ; Zellen 16 bis 18: C B A
                ZERLEG  xy           ; Zellen 19 und 20: y x
haupt:          164     0001         ; Zelle 21: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 22: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal).
; SPLIT: abc=42 -> 3 und 42; x=7 -> 1 und 7; schluessel=123 (Schluessel hat 10 Zeichen) -> 10 und 123; ab=0 -> 2 und 0.
;   Oktal: 3, 52, 1, 7, 12, 173, 2, 0.
; ANZAHL: Banane 2 (A an 2 und 4), Ananas 3, xyz 0, AaAa 4.
; FELDZ: 4, 2, 42 (oktal 4, 2, 52). ZERLEG ABC: C=67, B=66, A=65 (oktal 103, 102, 101); xy: y=121, x=120 (oktal 171, 170).
; haupt = Zelle 21 (oktal 0025), Halt auf Zelle 22 (oktal 0026), BZ danach 0027.
;#PRUEFE-START
; BZ=0027 US=1
; 0001: 00000000003   # SPLIT abc=42: Schluessellaenge
; 0002: 00000000052   # SPLIT abc=42: Wert 42
; 0003: 00000000001   # SPLIT x=7: Schluessellaenge
; 0004: 00000000007   # SPLIT x=7: Wert
; 0005: 00000000012   # SPLIT schluessel=123: Laenge 10
; 0006: 00000000173   # SPLIT schluessel=123: Wert 123
; 0007: 00000000002   # SPLIT ab=0: Schluessellaenge
; 0010: 00000000000   # SPLIT ab=0: Wert 0
; 0011: 00000000002   # ANZAHL Banane
; 0012: 00000000003   # ANZAHL Ananas
; 0013: 00000000000   # ANZAHL xyz
; 0014: 00000000004   # ANZAHL AaAa
; 0015: 00000000004   # FELDZ: f(0), Position des Gleichheitszeichens
; 0016: 00000000002   # FELDZ: Laenge des Textelements f(1)
; 0017: 00000000052   # FELDZ: f(2) = 42
; 0020: 00000000103   # ZERLEG ABC: C
; 0021: 00000000102   # ZERLEG ABC: B
; 0022: 00000000101   # ZERLEG ABC: A
; 0023: 00000000171   # ZERLEG xy: y
; 0024: 00000000170   # ZERLEG xy: x
;#PRUEFE-ENDE
