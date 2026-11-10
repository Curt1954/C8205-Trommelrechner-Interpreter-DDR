; makroattr2.asm - Randfaelle und Mischfaelle der Attributabfragen def, art, zellen (Assemblerdokumentation 4.23)
;#DOK-0001 Test Attributabfragen, Randfaelle: equ-Ketten bis 15 Stufen, equ *, Namenslaenge 32, Parameter als Ausdruck, $CALCO/$CALCO4, $CALC im Text von $SET, $REPT, Operation aus Parameter, $V(i) im Namensteil, Symbole hinter end nach Literalen
;#PROT STUFE=2
; Jeder Aufruf erzeugt genau ein Wort; hinter E= steht der von Hand hergeleitete Wert (dezimal), in der Reihenfolge der Zellen ab 0001.
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))              ; Art des Symbols
                MEND
FRAGE_DEF:      MACRO 1
                dw      $CALC(def($1))              ; 1, wenn das Symbol vorhanden ist
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))           ; Zellenzahl der Anweisung
                MEND
WERT:           MACRO 1
                dw      $CALC($1)                   ; Wert des Ausdrucks
                MEND
DOPPELT:        MACRO 1
                dw      $CALC(2*$1)                 ; $1 wird im Ausdruck eingeklammert eingesetzt (4.2)
                MEND
; CO: $CALCO und $CALCOn mit zellen (tab hat 10 Zellen: oktal 012)
CO:             MACRO
                dw      $CALCO(zellen(tab))         ; 012 = 10
                dw      $CALCO4(zellen(tab))        ; 0012 = 10
                MEND
; TX: $CALC im Text von $SET und in Textargumenten (4.22)
TX:             MACRO
                $SET t "$CALC(zellen(tab))"
                dw      $V(#t)                      ; Text 10: 2 Zeichen
                $VAL v "$V(t)"
                dw      $V(v)                       ; 10
                $STRCMP r "$CALC(art(tab))" "4"
                dw      $V(r)                       ; 4 gleich 4: 0
                MEND
; PE: Parameter ist ein Ausdruck mit Attributfunktion; $REPT $1, $IF $CALC($1)
PE:             MACRO 1
                $REPT $1
                dw      $Z1                         ; 0, 1
                $ENDREPT
                $IF $CALC($1) = 2
                dw      22                          ; erzeugt
                $ENDIF
                MEND
; SO: Operation aus Parameter (4.15)
SO:             MACRO 2
                $1      $2
                MEND
; AB: Attributabfrage in einem Makro, das ueber SO aufgerufen wird
AB:             MACRO 1
                dw      $CALC(zellen(tab)+def(tab)*100+art(tab)*1000)   ; 10 + 100 + 4000 = 4110
                MEND
; Makro ruft Makro auf; das innere fragt
INNEN:          MACRO 1
                dw      $CALC(zellen($1))           ; 10
                MEND
AUSSEN:         MACRO 1
                INNEN   $1
                MEND
; SUCHE: Zahlvariable im Namensteil ($V(i) wird vor der Auswertung aufgeloest, A-02)
SUCHE:          MACRO
                $SET i 1
                $WHILE $V(i) <= 3
                dw      $CALC(def(sym$V(i)))        ; sym1: 1, sym2: 0, sym3: 1
                $INC i
                $ENDWHILE
                $SET k 2
                dw      $CALC(art(sym$V(k)))        ; sym2 gibt es nicht: 0
                $SET k 3
                dw      $CALC(zellen(tab$V(k)))     ; tab3 hat 3 Zellen
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0: Sprung zum Hauptprogramm
                FRAGE_ART ka0                           ; E=1
                FRAGE_ART ka1                           ; E=2
                FRAGE_ART ka14                          ; E=2
                FRAGE_ART ka15                          ; E=2
                FRAGE_ART ka16                          ; E=3
                FRAGE_ART ka17                          ; E=3
                FRAGE_DEF ka17                          ; E=1
                WERT ka15                               ; E=3
                WERT ka1                                ; E=3
                FRAGE_ART kb0                           ; E=3
                FRAGE_ART kb1                           ; E=3
                FRAGE_ART kb2                           ; E=3
                FRAGE_DEF kb2                           ; E=1
                FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=2
                FRAGE_DEF nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn; E=1
                WERT nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn   ; E=5
                FRAGE_ZELLEN nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd; E=3
                FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd; E=4
                DOPPELT art(a_equ)+1                    ; E=6
                DOPPELT 2*3                             ; E=12
                DOPPELT zellen(a_db)+art(a_abs)         ; E=12
                WERT art(a_abs)+art(a_equ)*10           ; E=21
                CO                                      ; E=10,10
                TX                                      ; E=2,10,0
                PE      zellen(a2)                      ; E=0,1,22
                SO      AB 0                            ; E=4110
                AUSSEN  tab                             ; E=10
                SUCHE                                   ; E=1,0,1,0,3
                FRAGE_ART l0001                         ; E=0
                FRAGE_DEF l0001                         ; E=0
                FRAGE_ART h_abs                         ; E=1
                FRAGE_ART h_equ                         ; E=2
                FRAGE_ART h_stern                       ; E=3
                FRAGE_DEF h_abs                         ; E=1
                WERT h_abs+h_equ                        ; E=12
                FRAGE_ART erg                           ; E=4
                FRAGE_ZELLEN erg                        ; E=1
haupt:          211     #5           ; AC := 5 (Literal l0001)
                210     #7           ; AC := AC + 7 (Literal l0002)
                240     erg          ; erg := AC = 12
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
a_db:           db      5            ; 5 Zellen
tab:            db      012          ; 10 Zellen (oktal)
a2:             dbn     2            ; 2 Zellen
tab3:           db      3             ; 3 Zellen
erg:            dw      0            ; Ergebnis der Rechnung
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd:  db      3 ; Name mit 32 Zeichen auf db
ende:           end
a_abs:          abs     5
a_equ:          equ     07640
ka0:            abs     3
ka1:            equ     ka0
ka2:            equ     ka1
ka3:            equ     ka2
ka4:            equ     ka3
ka5:            equ     ka4
ka6:            equ     ka5
ka7:            equ     ka6
ka8:            equ     ka7
ka9:            equ     ka8
ka10:           equ     ka9
ka11:           equ     ka10
ka12:           equ     ka11
ka13:           equ     ka12
ka14:           equ     ka13
ka15:           equ     ka14
ka16:           equ     ka15
ka17:           equ     ka16
kb0:            equ     *
kb1:            equ     kb0
kb2:            equ     kb1
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn:  equ     5
sym1:           abs     1
sym3:           equ     sym1+2
h_abs:          abs     5
h_equ:          equ     h_abs+2
h_stern:        equ     *
; Sollwerte von Hand hergeleitet (Zellen ab 0001 in Aufrufreihenfolge, Werte dezimal in den E=-Marken; hier oktal). 46 Woerter.
;#PRUEFE-START
; BZ=0064 AC=00000000014 US=1
; 0001: 00000000001   # FRAGE_ART ka0
; 0002: 00000000002   # FRAGE_ART ka1
; 0003: 00000000002   # FRAGE_ART ka14
; 0004: 00000000002   # FRAGE_ART ka15
; 0005: 00000000003   # FRAGE_ART ka16
; 0006: 00000000003   # FRAGE_ART ka17
; 0007: 00000000001   # FRAGE_DEF ka17
; 0010: 00000000003   # WERT ka15
; 0011: 00000000003   # WERT ka1
; 0012: 00000000003   # FRAGE_ART kb0
; 0013: 00000000003   # FRAGE_ART kb1
; 0014: 00000000003   # FRAGE_ART kb2
; 0015: 00000000001   # FRAGE_DEF kb2
; 0016: 00000000002   # FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
; 0017: 00000000001   # FRAGE_DEF nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
; 0020: 00000000005   # WERT nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
; 0021: 00000000003   # FRAGE_ZELLEN nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd
; 0022: 00000000004   # FRAGE_ART nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnd
; 0023: 00000000006   # DOPPELT art(a_equ)+1
; 0024: 00000000014   # DOPPELT 2*3
; 0025: 00000000014   # DOPPELT zellen(a_db)+art(a_abs)
; 0026: 00000000025   # WERT art(a_abs)+art(a_equ)*10
; 0027: 00000000012   # CO
; 0030: 00000000012   # CO
; 0031: 00000000002   # TX
; 0032: 00000000012   # TX
; 0033: 00000000000   # TX
; 0034: 00000000000   # PE zellen(a2)
; 0035: 00000000001   # PE zellen(a2)
; 0036: 00000000026   # PE zellen(a2)
; 0037: 00000010016   # SO AB 0
; 0040: 00000000012   # AUSSEN tab
; 0041: 00000000001   # SUCHE
; 0042: 00000000000   # SUCHE
; 0043: 00000000001   # SUCHE
; 0044: 00000000000   # SUCHE
; 0045: 00000000003   # SUCHE
; 0046: 00000000000   # FRAGE_ART l0001
; 0047: 00000000000   # FRAGE_DEF l0001
; 0050: 00000000001   # FRAGE_ART h_abs
; 0051: 00000000002   # FRAGE_ART h_equ
; 0052: 00000000003   # FRAGE_ART h_stern
; 0053: 00000000001   # FRAGE_DEF h_abs
; 0054: 00000000014   # WERT h_abs+h_equ
; 0055: 00000000004   # FRAGE_ART erg
; 0056: 00000000001   # FRAGE_ZELLEN erg
; 0110: 00000000014   # erg = 5 + 7 (Literale #5 und #7; erg liegt nach haupt (47), 4 weiteren Codezellen, a_db 5, tab 10, a2 2, tab3 3 Zellen: 46+26 = 72 = 0110)
;#PRUEFE-ENDE
