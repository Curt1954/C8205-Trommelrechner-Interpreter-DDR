; makrocalc.asm - Test der Rechenausdruecke $CALC / $CALCO und der Bereichspruefung $PRx $TYPZAHL im Makro-Praeprozessor
;                 (Assemblerdokumentation 4.2) sowie von SCHIEBE_LI / SCHIEBE_RE mit Ausdruck als Parameter
;#DOK-0001 Test der Rechenausdruecke im Makro: Rangfolge, Parameter als Ausdruck, $IF mit $CALC, oktale Ausgabe, SCHIEBE_* mit Ausdruck
;#PROT STUFE=2
; Makro mit zwei Parametern: dw (p1*p2)+1, Parameter duerfen selbst Ausdruecke sein (werden eingeklammert)
ZAHL:           MACRO 2
$PR1 $TYPZAHL 0 100
$PR2 $TYPZAHL 0 100
                dw      $CALC($1*$2+1)   ; Produkt der Parameter plus 1
                MEND
; Makro mit oktaler Ausgabe: dw p1 + p2*03, das Ergebnis erscheint oktal mit fuehrender 0
OKT:            MACRO 2
                dw      $CALCO($1+$2*03)   ; Summe aus p1 und dreimal p2, oktal
                MEND
; Makro ohne Parameter: Operatoren Rest, Schieben, ODER, Klammern, Komplement, UND, Oktalzahl
MISC:           MACRO
                dw      $CALC(100%7)       ; Rest: 100 mod 7 = 2
                dw      $CALC(1<<5|3)      ; Schieben vor ODER: (1<<5)|3 = 35
                dw      $CALC((2+3)*(4-1)) ; Klammern: 15
                dw      $CALCO(~0&077)     ; Komplement und UND: 63
                dw      $CALC(010+10)      ; Oktal- und Dezimalzahl: 8 + 10 = 18
                MEND
; Makro mit $IF auf einem Rechenausdruck: Rest durch 2 gleich 0 liefert 0, sonst 1
PARI:           MACRO 1
$PR1 $TYPZAHL 0 1000
      $IF  $CALC($1%2)  =  0
                dw      0                ; gerade
      $ELIF  $CALC($1%2)  =  1
                dw      1                ; ungerade
      $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
z1:             ZAHL    3  4         ; Zelle 0001: 3*4+1 = 13
z2:             ZAHL    1+2  5       ; Zelle 0002: (1+2)*5+1 = 16 (Parameter als Ausdruck)
z3:             OKT     010  2       ; Zelle 0003: 8+2*3 = 14
                MISC                 ; Zellen 0004 bis 0010: fuenf Werte
p1:             PARI    7+2          ; Zelle 0011: 9 ist ungerade, also 1
p2:             PARI    4            ; Zelle 0012: 4 ist gerade, also 0
erg1:           dw      0            ; Zelle 0013: Ergebnis SCHIEBE_LI
erg2:           dw      0            ; Zelle 0014: Ergebnis SCHIEBE_RE
eins:           dw      1            ; Zelle 0015: Konstante 1
bit31:          dw      020000000000 ; Zelle 0016: 2 hoch 31
haupt:          211     eins         ; AC := 1
                SCHIEBE_LI 2+1       ; 3 mal links (Parameter als Ausdruck): AC := 8
                240     erg1         ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 4*2       ; 8 mal rechts: AC := 2 hoch 23
                240     erg2         ; Ergebnis ablegen
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet (siehe Kommentar je Zelle); Halt auf 0026, BZ danach 0027.
;#PRUEFE-START
; BZ=0027 US=1
; 0001: 00000000015   # z1 = 3*4+1 = 13
; 0002: 00000000020   # z2 = (1+2)*5+1 = 16
; 0003: 00000000016   # z3 = 8+2*3 = 14
; 0004: 00000000002   # 100 mod 7 = 2
; 0005: 00000000043   # (1<<5)|3 = 35
; 0006: 00000000017   # (2+3)*(4-1) = 15
; 0007: 00000000077   # ~0&077 = 63
; 0010: 00000000022   # 010+10 = 18
; 0011: 00000000001   # PARI 9
; 0012: 00000000000   # PARI 4
; 0013: 00000000010   # 1 mal 2 hoch 3 = 8
; 0014: 00040000000   # 2 hoch 31 durch 2 hoch 8 = 2 hoch 23
;#PRUEFE-ENDE
