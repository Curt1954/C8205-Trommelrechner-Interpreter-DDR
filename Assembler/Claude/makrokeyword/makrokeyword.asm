; makrokeyword.asm - Test der Schluesselwortparameter (MACRO name=vorgabe; Assemblerdokumentation 4.30, ab c82ass 1.01-025)
;#DOK-0001 Test Schluesselwortparameter: Vorgaben, Schluesselwoerter in beliebiger Reihenfolge und Stelle, Positionsoperanden, leere Vorgabe, Zeichenketten, + und $DEFAULT, $PR, verschachtelter Aufruf
;#PROT STUFE=2
                start                           ; Zaehlung beginnt bei 0000
                000     haupt                   ; Zelle 0000: Sprung zum Hauptprogramm
; SCHIEBE: ein Positionsparameter und zwei Schluesselwoerter; Ausgabe: ziel, anzahl, Richtung (LI = 1, RE = 2), $# (Zahl der Positionsoperanden)
SCHIEBE:        MACRO ziel anzahl=1 richtung=LI
                $PR(richtung) LI RE
                $PR(anzahl)   $TYPZAHL 0 5
                dw      $ziel                   ; Positionsparameter
                dw      $anzahl                 ; Schluesselwort anzahl
                $IF $richtung = LI
                dw      1                       ; Richtung LI
                $ELSE
                dw      2                       ; Richtung RE
                $ENDIF
                dw      $#                      ; Zahl der Positionsoperanden
                MEND                            ; Ende von SCHIEBE
; LEER: Vorgabe leer (text="") und Zeichenketten; Ausgabe: a, n, Laenge von text
LEER:           MACRO a text="" n=2
                dw      $a                      ; Positionsparameter
                dw      $n                      ; Schluesselwort n
                dw      $LEN(text)              ; Zeichenzahl von text
                MEND                            ; Ende von LEER
; PRL: leere Vorgabe wird von $PR nicht geprueft, ein angegebener Wert schon
PRL:            MACRO a text=""
                $PR(text) X Z
                dw      $a                      ; Positionsparameter
                dw      $LEN(text)              ; Zeichenzahl von text
                MEND                            ; Ende von PRL
; ZK: Vorgabe mit Leerzeichen in Anfuehrungszeichen
ZK:             MACRO a t="x y"
                dw      $a                      ; Positionsparameter
                dw      $LEN(t)                 ; Zeichenzahl von t
                MEND                            ; Ende von ZK
; VAR: Schluesselwort und variable Parameterzahl (+); weitere Positionsoperanden hinter den benannten ueber $P(3), $P(4)
VAR:            MACRO a k=4 +
                dw      $a                      ; Positionsparameter
                dw      $k                      ; Schluesselwort k
                dw      $P(3)                   ; erster weiterer Positionsoperand
                dw      $P(4)                   ; zweiter weiterer Positionsoperand
                dw      $#                      ; Zahl der Positionsoperanden
                MEND                            ; Ende von VAR
; DEF: $DEFAULT fuer einen Positionsparameter neben einem Schluesselwort
DEF:            MACRO a b w=3
                $DEFAULT b 8
                dw      $a                      ; Positionsparameter a
                dw      $b                      ; Positionsparameter b oder Vorgabe 8
                dw      $w                      ; Schluesselwort w
                MEND                            ; Ende von DEF
; AUSEN und AUSEN2: Aufruf von SCHIEBE aus einem Makro
AUSEN:          MACRO x
                SCHIEBE $x anzahl=2             ; Positionsoperand aus dem Parameter, Schluesselwort fest
                MEND                            ; Ende von AUSEN
AUSEN2:         MACRO x
                SCHIEBE 5 anzahl=$x             ; Schluesselwortwert aus dem Parameter
                MEND                            ; Ende von AUSEN2
                SCHIEBE 7                       ; 0001-0004 = 7, 1, 1, 1 (nur Vorgaben)
                SCHIEBE 7 anzahl=3              ; 0005-0010 = 7, 3, 1, 1
                SCHIEBE 7 richtung=RE           ; 0011-0014 = 7, 1, 2, 1
                SCHIEBE richtung=RE anzahl=4 6  ; 0015-0020 = 6, 4, 2, 1 (Schluesselwoerter vor dem Positionsoperanden, vertauscht)
                SCHIEBE 5 anzahl=2 richtung=LI  ; 0021-0024 = 5, 2, 1, 1 (beide angegeben)
                SCHIEBE 7 richtung="LI"         ; 0025-0030 = 7, 1, 1, 1 (Wert in Anfuehrungszeichen)
                LEER    5                       ; 0031-0033 = 5, 2, 0
                LEER    5 text=X n=3            ; 0034-0036 = 5, 3, 1
                LEER    4 text=Z n=7            ; 0037-0041 = 4, 7, 1
                LEER    3 text=""               ; 0042-0044 = 3, 2, 0 (leerer Wert im Aufruf)
                PRL     1                       ; 0045-0046 = 1, 0 (leere Vorgabe, $PR prueft nicht)
                PRL     2 text=Z                ; 0047-0050 = 2, 1 (angegebener Wert erfuellt $PR)
                ZK      1                       ; 0051-0052 = 1, 3 (Vorgabe "x y")
                ZK      2 t="p q r"             ; 0053-0054 = 2, 5
                VAR     1 2 3                   ; 0055-0061 = 1, 4, 2, 3, 3
                VAR     6 k=9 7 8               ; 0062-0066 = 6, 9, 7, 8, 3
                DEF     1                       ; 0067-0071 = 1, 8, 3
                DEF     1 2 w=9                 ; 0072-0074 = 1, 2, 9
                DEF     w=5 1                   ; 0075-0077 = 1, 8, 5
                AUSEN   7                       ; 0100-0103 = 7, 2, 1, 1
                AUSEN2  4                       ; 0104-0107 = 5, 4, 1, 1
haupt:          020     0                       ; Halt
ende:           end

; Sollwerte von Hand hergeleitet (siehe Kommentare der Aufrufe); 71 Zellen 0001 bis 0107, Halt auf 0110 oktal, BZ danach 0111
;#PRUEFE-START
; BZ=0111 US=1
; 0001: 00000000007
; 0002: 00000000001
; 0003: 00000000001
; 0004: 00000000001
; 0005: 00000000007
; 0006: 00000000003
; 0007: 00000000001
; 0010: 00000000001
; 0011: 00000000007
; 0012: 00000000001
; 0013: 00000000002
; 0014: 00000000001
; 0015: 00000000006
; 0016: 00000000004
; 0017: 00000000002
; 0020: 00000000001
; 0021: 00000000005
; 0022: 00000000002
; 0023: 00000000001
; 0024: 00000000001
; 0025: 00000000007
; 0026: 00000000001
; 0027: 00000000001
; 0030: 00000000001
; 0031: 00000000005
; 0032: 00000000002
; 0033: 00000000000
; 0034: 00000000005
; 0035: 00000000003
; 0036: 00000000001
; 0037: 00000000004
; 0040: 00000000007
; 0041: 00000000001
; 0042: 00000000003
; 0043: 00000000002
; 0044: 00000000000
; 0045: 00000000001
; 0046: 00000000000
; 0047: 00000000002
; 0050: 00000000001
; 0051: 00000000001
; 0052: 00000000003
; 0053: 00000000002
; 0054: 00000000005
; 0055: 00000000001
; 0056: 00000000004
; 0057: 00000000002
; 0060: 00000000003
; 0061: 00000000003
; 0062: 00000000006
; 0063: 00000000011
; 0064: 00000000007
; 0065: 00000000010
; 0066: 00000000003
; 0067: 00000000001
; 0070: 00000000010
; 0071: 00000000003
; 0072: 00000000001
; 0073: 00000000002
; 0074: 00000000011
; 0075: 00000000001
; 0076: 00000000010
; 0077: 00000000005
; 0100: 00000000007
; 0101: 00000000002
; 0102: 00000000001
; 0103: 00000000001
; 0104: 00000000005
; 0105: 00000000004
; 0106: 00000000001
; 0107: 00000000001
;#PRUEFE-ENDE
