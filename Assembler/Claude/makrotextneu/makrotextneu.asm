; makrotextneu.asm - Test der aufgehobenen Einschraenkungen im Makroprozessor (c82ass ab 1.01-015, Assemblerdokumentation 4.10, 4.12, 4.13, 4.17, 4.21, 4.25)
;#DOK-0001 Test Makrotexte: $V in $P und $LEN, leerer Text, Semikolon im Text, Texte bis 1000 Zeichen
;#PROT STUFE=2
; PAR: $P($V(i)) und $LEN($V(i)) mit der Nummer aus einer Variablen, auch in $CALC, $SET und $IF
PAR:            MACRO 3
                $SET i 1                          ; Laufindex, global
                $WHILE $V(i) <= 3
                dw      $P($V(i))                 ; Parameter Nummer i
                dw      $LEN($V(i))               ; Zeichenzahl des Parameters i
                $SET t $CALC($P($V(i))*2)         ; Doppelte des Parameters
                dw      $V(t)                     ; Doppelte
                $IF $CALC($P($V(i))*2) > 20
                dw      $V(i)                     ; nur wenn das Doppelte ueber 20 liegt: der Index
                $ENDIF
                $INC i
                $ENDWHILE
                MEND
; FELDP: $P($V(i)) als Feldindex in $V(q(...)); lokales Feld q mit 6 Elementen (Index 0 bis 5), q(j) = 7*j
FELDP:          MACRO 3
                $LOCAL q(6) i j
                $SET j 0
                $WHILE $V(j) < 6
                $SET q($V(j)) $CALC(7*$V(j))      ; q(j) = 7*j
                $INC j
                $ENDWHILE
                $SET i 1
                $WHILE $V(i) <= 3
                dw      $V(q($P($V(i))))          ; Element mit dem Index aus dem Parameter i
                $INC i
                $ENDWHILE
                MEND
; DEFP: $P($DEFINED(..)): $DEFINED wird wie $V durch 1 ersetzt, danach loest $P die Nummer auf
DEFP:           MACRO 1+
                $DIM fe 3                         ; Feld fe sichtbar, also $DEFINED(fe) = 1
                dw      $P($DEFINED(fe))          ; Parameter 1
                dw      $P($DEFINED(fe)+1)        ; Parameter 2
                MEND
; INNER und OUTER: verschachtelte Makros, $P($V(n)) und $LEN($V(n)) beziehen sich auf den eigenen Aufruf; n ist global
INNER:          MACRO 2
                dw      $P($V(n))                 ; Parameter n des inneren Aufrufs
                dw      $LEN($V(n))               ; Zeichenzahl des Parameters n des inneren Aufrufs
                MEND
OUTER:          MACRO 3
                $SET n 1
                dw      $P($V(n))                 ; Parameter 1 des aeusseren Aufrufs
                INNER   20 300                    ; innen: Parameter 1 und seine Laenge
                dw      $P($V(n))                 ; nach der Rueckkehr wieder der aeussere Aufruf
                $SET n 2
                INNER   20 300                    ; innen: Parameter 2 und seine Laenge
                dw      $P($V(n))                 ; aussen: Parameter 2
                MEND
; LEER: leerer Text aus $SET, $SUBSTR (Start Laenge+1, Anzahl 0, leerer Quelltext), leere Variable als Teil eines Textes
LEER:           MACRO
                $SET t ""                         ; leerer Text
                dw      $V(#t)                    ; Laenge 0
                $SUBSTR z "abc" 4                 ; Start 4 = Laenge+1: leerer Rest
                dw      $V(#z)                    ; Laenge 0
                $SUBSTR z "abc" 2 0               ; Anzahl 0: leerer Text
                dw      $V(#z)                    ; Laenge 0
                $SUBSTR z "" 1                    ; leerer Quelltext
                dw      $V(#z)                    ; Laenge 0
                $SUBSTR y "ab$V(t)cd" 3 2         ; ab, leerer Text, cd: Zeichen 3 und 4
                dw      $V(#y)                    ; Laenge 2
                $SUBSTR w "$V(t)" 1               ; leere Variable als Quelltext
                dw      $V(#w)                    ; Laenge 0
                $IF $V(#z) = 0
                dw      1                         ; z ist leer
                $ENDIF
                MEND
; SEMI: Semikolon im Text und als Zeichen ($CHR 59); ein Semikolon im Text beginnt keinen Kommentar
SEMI:           MACRO
                $SET s "a;b"                      ; Text mit Semikolon
                dw      $V(#s)                    ; Laenge 3
                $INDEX p "$V(s)" ";"              ; Position des Semikolons
                dw      $V(p)                     ; 2
                $UPPER u "$V(s)x"                 ; A;BX
                $INDEX p "$V(u)" "BX"             ; Position von BX
                dw      $V(p)                     ; 3
                $CHR c 59                         ; das Zeichen Semikolon
                dw      $V(#c)                    ; Laenge 1
                $ORD o "$V(c)"                    ; Zeichencode
                dw      $V(o)                     ; 59
                $SET d "$V(s)$V(c)$V(s)"          ; a;b;a;b
                dw      $V(#d)                    ; Laenge 7
                $INDEX p "$V(d)" "b;a"            ; Suchtext mit Semikolon
                dw      $V(p)                     ; 3
                MEND
; LANG: Texte ueber 255 Zeichen (bis 1000) in $SET und in den Zeichenkettenfunktionen
LANG:           MACRO
                $SET a "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789" ; 100 Ziffern
                $SET b "$V(a)$V(a)$V(a)"          ; 300 Zeichen
                dw      $V(#b)                    ; 300
                $SET c "$V(b)$V(b)$V(b)"          ; 900 Zeichen
                dw      $V(#c)                    ; 900
                $SET e "$V(c)$V(a)"               ; 1000 Zeichen: die Grenze
                dw      $V(#e)                    ; 1000
                $SUBSTR z "$V(c)" 899             ; die letzten zwei Zeichen von c
                dw      $V(#z)                    ; 2
                $SUBSTR z "$V(e)" 995 4           ; vier Ziffern ab Zeichen 995
                $VAL v "$V(z)"                    ; als Zahl 4567
                dw      $V(v)                     ; 4567
                $INDEX p "$V(e)" "90"             ; erste Stelle von 90
                dw      $V(p)                     ; 10
                $SET f "$V(c)xyz"                 ; 903 Zeichen
                dw      $V(#f)                    ; 903
                $INDEX p "$V(f)" "xyz"            ; Position hinter den 900 Ziffern
                dw      $V(p)                     ; 901
                $UPPER u "$V(f)"                  ; Grossbuchstaben, 903 Zeichen
                $INDEX p "$V(u)" "XYZ"            ; gleiche Position
                dw      $V(p)                     ; 901
                dw      $V(#u)                    ; 903
                MEND
                start                             ; Zaehlung beginnt bei 0000
                000     haupt                     ; Zelle 0000: Sprung zum Hauptprogramm
                PAR     7 11 13                   ; Zellen 0001 bis 0013 (11 Zellen)
                FELDP   2 4 5                     ; Zellen 0014 bis 0016
                DEFP    5 9                       ; Zellen 0017 und 0020
                OUTER   7 11 13                   ; Zellen 0021 bis 0027
                LEER                              ; Zellen 0030 bis 0036
                SEMI                              ; Zellen 0037 bis 0045
                LANG                              ; Zellen 0046 bis 0057
haupt:          164     0001                      ; Zelle 0060: Diagnoseausgabe (nur im Test)
                020     0                         ; Zelle 0061: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal; dw-Operanden sind dezimal).
; PAR 7 11 13: i=1: 7, 1, 14, (14 nicht ueber 20); i=2: 11, 2, 22, 2; i=3: 13, 2, 26, 3. Oktal: 7,1,16, 13,2,26,2, 15,2,32,3.
; FELDP 2 4 5: q(2)=14, q(4)=28, q(5)=35, oktal 16, 34, 43. DEFP 5 9: $DEFINED(fe)=1, also P(1)=5 und P(2)=9, oktal 5, 11.
; OUTER 7 11 13: 7; INNER 20 300 mit n=1: 20, 2; wieder aussen 7; INNER mit n=2: 300, 3; aussen P(2)=11. Oktal: 7,24,2,7,454,3,13.
; LEER: 0,0,0,0,2,0,1. SEMI: Laenge 3, Position 2, Position 3 (A;BX), Laenge 1, Code 59 (oktal 73), Laenge 7, Position 3.
; LANG: 300 (454), 900 (1604), 1000 (1750), 2, 4567 (10727), 10 (12), 903 (1607), 901 (1605), 901 (1605), 903 (1607).
; haupt = Zelle 48 (oktal 0060), Halt auf Zelle 0061, BZ danach 0062.
;#PRUEFE-START
; BZ=0062 US=1
; 0001: 00000000007   # PAR i=1: P(1)
; 0002: 00000000001   # PAR i=1: Laenge von P(1)
; 0003: 00000000016   # PAR i=1: Doppelte 14
; 0004: 00000000013   # PAR i=2: P(2)
; 0005: 00000000002   # PAR i=2: Laenge von P(2)
; 0006: 00000000026   # PAR i=2: Doppelte 22
; 0007: 00000000002   # PAR i=2: Index, weil 22 ueber 20
; 0010: 00000000015   # PAR i=3: P(3)
; 0011: 00000000002   # PAR i=3: Laenge von P(3)
; 0012: 00000000032   # PAR i=3: Doppelte 26
; 0013: 00000000003   # PAR i=3: Index, weil 26 ueber 20
; 0014: 00000000016   # FELDP: q(2)
; 0015: 00000000034   # FELDP: q(4)
; 0016: 00000000043   # FELDP: q(5)
; 0017: 00000000005   # DEFP: $P($DEFINED(fe))
; 0020: 00000000011   # DEFP: $P($DEFINED(fe)+1)
; 0021: 00000000007   # OUTER: P(1) aussen
; 0022: 00000000024   # OUTER: INNER P(1) = 20
; 0023: 00000000002   # OUTER: INNER Laenge von P(1)
; 0024: 00000000007   # OUTER: nach der Rueckkehr aussen P(1)
; 0025: 00000000454   # OUTER: INNER P(2) = 300
; 0026: 00000000003   # OUTER: INNER Laenge von P(2)
; 0027: 00000000013   # OUTER: P(2) aussen
; 0030: 00000000000   # LEER: $SET t "" Laenge
; 0031: 00000000000   # LEER: $SUBSTR Start hinter dem Ende
; 0032: 00000000000   # LEER: $SUBSTR Anzahl 0
; 0033: 00000000000   # LEER: $SUBSTR leerer Quelltext
; 0034: 00000000002   # LEER: ab, leer, cd: Laenge 2
; 0035: 00000000000   # LEER: leere Variable als Quelltext
; 0036: 00000000001   # LEER: $IF auf leeren Text
; 0037: 00000000003   # SEMI: Laenge von a;b
; 0040: 00000000002   # SEMI: Position des Semikolons
; 0041: 00000000003   # SEMI: Position von BX in A;BX
; 0042: 00000000001   # SEMI: $CHR 59 Laenge
; 0043: 00000000073   # SEMI: $ORD = 59
; 0044: 00000000007   # SEMI: Laenge von a;b;a;b
; 0045: 00000000003   # SEMI: Position von b;a
; 0046: 00000000454   # LANG: Laenge 300
; 0047: 00000001604   # LANG: Laenge 900
; 0050: 00000001750   # LANG: Laenge 1000
; 0051: 00000000002   # LANG: $SUBSTR Rest ab 899
; 0052: 00000010727   # LANG: $VAL 4567
; 0053: 00000000012   # LANG: $INDEX 90 = 10
; 0054: 00000001607   # LANG: Laenge 903
; 0055: 00000001605   # LANG: $INDEX xyz = 901
; 0056: 00000001605   # LANG: $INDEX XYZ = 901
; 0057: 00000001607   # LANG: Laenge 903 nach $UPPER
;#PRUEFE-ENDE
