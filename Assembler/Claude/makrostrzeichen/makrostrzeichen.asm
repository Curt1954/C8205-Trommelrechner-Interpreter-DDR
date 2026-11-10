; makrostrzeichen.asm - Test von $ORD, $CHR, $VAL und der Verkettung durch $SET (Assemblerdokumentation 4.21)
;#DOK-0001 Test Zeichen und Zahlen: Zeichencode, Zeichen aus Code, Text nach Zahl, Verkettung beim Setzen, Bytezaehlung bei UTF-8
;#PROT STUFE=2
; ORDN: Zeichencode (ASCII) an einer Position; ae mit Umlaut besteht aus den zwei Bytes 195 und 164
ORDN:           MACRO
                $ORD n "A"
                dw      $V(n)                   ; A = 65
                $ORD n "abc" 2
                dw      $V(n)                   ; b = 98
                $ORD n "abc" 3
                dw      $V(n)                   ; c = 99
                $ORD n " "
                dw      $V(n)                   ; Leerzeichen = 32
                $ORD n "~"
                dw      $V(n)                   ; Tilde = 126
                $ORD n "ä"
                dw      $V(n)                   ; erstes Byte des ae mit Umlaut = 195
                $ORD n "ä" 2
                dw      $V(n)                   ; zweites Byte = 164
                MEND
; CHRN: Zeichen aus dem Code; Pruefung ueber Laenge, Vergleich und Rueckwandlung mit $ORD
CHRN:           MACRO 1
                $CHR z 65
                dw      $V(#z)                  ; ein Zeichen: 1
                $STRCMP r "$V(z)" "A"
                dw      $V(r)                   ; gleich A: 0
                $CHR z $CALC(64+33)
                $ORD n "$V(z)"
                dw      $V(n)                   ; Code als Rechenausdruck, 97
                $CHR z 32
                $ORD n "$V(z)"
                dw      $V(n)                   ; Leerzeichen, 32
                dw      $V(#z)                  ; ein Zeichen: 1
                $CHR z 126
                $ORD n "$V(z)"
                dw      $V(n)                   ; Tilde, 126
                $CHR z $1
                $ORD n "$V(z)"
                dw      $V(n)                   ; Code aus dem Parameter, 66
                MEND
; VALN: Text nach Zahl; fuehrende Nullen und Minus sind erlaubt; Rueckweg Zahl nach Text ueber $SET
VALN:           MACRO
                $VAL n "42"
                dw      $V(n)                   ; 42
                $VAL n "0"
                dw      $V(n)                   ; 0
                $VAL n "007"
                dw      $V(n)                   ; 7
                $VAL n "-17"
                $SET m $CALC($V(n)+100)
                dw      $V(m)                   ; -17 + 100 = 83
                $VAL n "-0012"
                $SET m $CALC($V(n)+100)
                dw      $V(m)                   ; -12 + 100 = 88
                $SET n 57
                $SET t "$V(n)"
                dw      $V(#t)                  ; Text 57 hat 2 Zeichen
                $VAL m "$V(t)"
                dw      $V(m)                   ; zurueck zur Zahl 57
                MEND
; VERK: Verkettung durch sofortiges Aufloesen beim $SET; Leerzeichen im Text; UTF-8 zaehlt byteweise
VERK:           MACRO 1
                $SET a "ab"
                $SET b "cd"
                $SET c "$V(a)$V(b)-$1"
                dw      $V(#c)                  ; abcd-xy hat 7 Zeichen
                $SET a "zzz"
                $STRCMP r "$V(c)" "abcd-xy"
                dw      $V(r)                   ; spaetere Aenderung von a aendert c nicht: 0
                $SET m 12
                $SET d "$V(m)$V(m)"
                dw      $V(#d)                  ; 1212 hat 4 Zeichen
                $VAL n "$V(d)"
                dw      $V(n)                   ; Zahl 1212
                $SET s "ein text"
                dw      $V(#s)                  ; Text mit Leerzeichen: 8
                $STRCMP r "$V(s)" "ein text"
                dw      $V(r)                   ; gleich: 0
                $SET u "äö"
                dw      $V(#u)                  ; zwei Umlaute sind 4 Bytes
                $SUBSTR h "äö" 1 2
                dw      $V(#h)                  ; ein Umlaut: 2 Bytes
                $ORD n "$V(h)"
                dw      $V(n)                   ; erstes Byte: 195
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ORDN                 ; Zellen 1 bis 7 (dezimal)
                CHRN    66           ; Zellen 8 bis 14 (dezimal)
                VALN                 ; Zellen 15 bis 21 (dezimal)
                VERK    xy           ; Zellen 22 bis 30 (dezimal)
haupt:          164     0001         ; Zelle 31: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 32: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal).
; ORDN: 65, 98, 99, 32, 126, 195, 164 = oktal 101, 142, 143, 40, 176, 303, 244.
; CHRN: 1, 0, 97, 32, 1, 126, 66 = oktal 1, 0, 141, 40, 1, 176, 102.
; VALN: 42, 0, 7, 83, 88, 2, 57 = oktal 52, 0, 7, 123, 130, 2, 71.
; VERK: 7, 0, 4, 1212, 8, 0, 4, 2, 195 = oktal 7, 0, 4, 2274, 10, 0, 4, 2, 303.
; haupt = Zelle 31 (oktal 0037), Halt auf Zelle 32 (oktal 0040), BZ danach 0041.
;#PRUEFE-START
; BZ=0041 US=1
; 0001: 00000000101   # ORDN: A
; 0002: 00000000142   # ORDN: b
; 0003: 00000000143   # ORDN: c
; 0004: 00000000040   # ORDN: Leerzeichen
; 0005: 00000000176   # ORDN: Tilde
; 0006: 00000000303   # ORDN: erstes Byte des Umlauts
; 0007: 00000000244   # ORDN: zweites Byte des Umlauts
; 0010: 00000000001   # CHRN: Laenge 1
; 0011: 00000000000   # CHRN: gleich A
; 0012: 00000000141   # CHRN: 97 aus $CALC
; 0013: 00000000040   # CHRN: 32
; 0014: 00000000001   # CHRN: Leerzeichen hat Laenge 1
; 0015: 00000000176   # CHRN: 126
; 0016: 00000000102   # CHRN: 66 aus dem Parameter
; 0017: 00000000052   # VALN: 42
; 0020: 00000000000   # VALN: 0
; 0021: 00000000007   # VALN: 007
; 0022: 00000000123   # VALN: -17 + 100 = 83
; 0023: 00000000130   # VALN: -0012 + 100 = 88
; 0024: 00000000002   # VALN: Text 57 hat 2 Zeichen
; 0025: 00000000071   # VALN: 57 zurueck
; 0026: 00000000007   # VERK: abcd-xy
; 0027: 00000000000   # VERK: c nach Aenderung von a unveraendert
; 0030: 00000000004   # VERK: 1212 hat 4 Zeichen
; 0031: 00000002274   # VERK: Zahl 1212
; 0032: 00000000010   # VERK: ein text hat 8 Zeichen
; 0033: 00000000000   # VERK: gleich
; 0034: 00000000004   # VERK: zwei Umlaute 4 Bytes
; 0035: 00000000002   # VERK: ein Umlaut 2 Bytes
; 0036: 00000000303   # VERK: erstes Byte 195
;#PRUEFE-ENDE
