; makroattr.asm - Test der Attributabfragen def, art und zellen im Makro-Praeprozessor (Assemblerdokumentation 4.23)
;#DOK-0001 Test Attributabfragen: def, art, zellen fuer jede Art von Symbol; Argument mit und ohne Klammer, $V(name), Rechnung, $IF, $WHILE, $REPT, $SET, $INC, $P, $TYPZAHL, Symbol aus einem Makro, Marke ohne Befehl
;#PROT STUFE=2
; Jeder Aufruf erzeugt genau ein Wort; hinter E= steht der von Hand hergeleitete Wert (dezimal), in der Reihenfolge der Zellen ab 0001.
; FRAGE_ART, FRAGE_DEF, FRAGE_ZELLEN: je ein Wort mit dem Ergebnis der Abfrage ($1 wird im Ausdruck eingeklammert eingesetzt, Doku 4.2)
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))              ; Art des Symbols
                MEND
FRAGE_DEF:      MACRO 1
                dw      $CALC(def($1))              ; 1, wenn das Symbol vorhanden ist
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))           ; Zellenzahl der Anweisung
                MEND
; ERZEUGE: ein Wort mit der Marke erz_marke; diese Marke kennt der Quelltext nicht (A-11)
ERZEUGE:        MACRO
erz_marke:      dw      99                          ; Marke aus einem Makro
                MEND
; EIN_WORT: Rumpf fuer die Marke auf einem Makroaufruf
EIN_WORT:       MACRO
                dw      55                          ; Wort 55
                MEND
; DIREKT: das Argument steht ohne Klammer und mit einer Klammer im Ausdruck
DIREKT:         MACRO
                dw      $CALC(art(a_abs))           ; ohne Klammer: 1
                dw      $CALC(art((a_equ)))         ; mit einer Klammer: 2
                MEND
; RECHNEN: die Ergebnisse rechnen wie jede andere Zahl (A-04)
RECHNEN:        MACRO
                dw      $CALC(def(a_abs)+def(a_dw)) ; 1 + 1 = 2
                dw      $CALC(zellen(a_db)*2)       ; 5 * 2 = 10
                dw      $CALC(art(a_abs)+art(a_equ)*10) ; 1 + 2 * 10 = 21
                MEND
; MIT_V: der Name steht in einer Textvariablen ($V(name) wird vor der Auswertung aufgeloest, A-02)
MIT_V:          MACRO
                $SET nm "a_db"
                dw      $CALC(zellen($V(nm)))       ; 5
                MEND
; PROBE: Beispiel 1 der Anforderung; DEBUG ist hinter end vereinbart
PROBE:          MACRO
                $IF $CALC(def(DEBUG)) = 1
                dw      63                          ; Probemarke
                $ENDIF
                MEND
; PROBE2: das Gegenstueck; NODEBUG gibt es nicht
PROBE2:         MACRO
                $IF $CALC(def(NODEBUG)) = 1
                dw      77                          ; wird nicht erzeugt
                $ELSE
                dw      78                          ; wird erzeugt
                $ENDIF
                MEND
; MIT_WHILE: $WHILE mit zellen in der Bedingung (a_dbn belegt 3 Zellen)
MIT_WHILE:      MACRO
                $SET i 0
                $WHILE $V(i) < $CALC(zellen(a_dbn))
                dw      $V(i)                       ; 0, 1, 2
                $INC i
                $ENDWHILE
                MEND
; MIT_REPT: Anzahl hinter $REPT aus zellen (3)
MIT_REPT:       MACRO
                $REPT $CALC(zellen(a_dbn))
                dw      $CALC($Z1+10)               ; 10, 11, 12
                $ENDREPT
                MEND
; MIT_SET: $SET und $INC mit Attributabfrage
MIT_SET:        MACRO
                $SET z $CALC(zellen(a_db)+1)
                dw      $V(z)                       ; 5 + 1 = 6
                $INC z $CALC(zellen(a_dbo))
                dw      $V(z)                       ; 6 + 8 = 14
                MEND
; MIT_P: $P(ausdruck) mit def im Ausdruck
MIT_P:          MACRO 2+
                dw      $P(def(nix)+1)              ; def = 0, also Parameter 1
                dw      $P(def(a_abs)+1)            ; def = 1, also Parameter 2
                MEND
; TYPT: $TYPZAHL mit einer Attributabfrage im Parameter und in der Obergrenze
TYPT:           MACRO 1
                $PR1 $TYPZAHL 1 zellen(a_db)
                dw      $CALC($1)                   ; Parameter art(a_equ)+3 = 5
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0: Sprung zum Hauptprogramm
                ERZEUGE              ; E=99
                FRAGE_ART a_abs      ; E=1
                FRAGE_ART a_equ      ; E=2
                FRAGE_ART a_equd     ; E=2
                FRAGE_ART a_equs     ; E=2
                FRAGE_ART a_stern    ; E=3
                FRAGE_ART a_lbl      ; E=3
                FRAGE_ART a_e10      ; E=3
                FRAGE_ART a_e40      ; E=3
                FRAGE_ART a_e100     ; E=3
                FRAGE_ART a_spa      ; E=3
                FRAGE_ART a_befehl   ; E=4
                FRAGE_ART a_dw       ; E=4
                FRAGE_ART a_da       ; E=4
                FRAGE_ART a_dz       ; E=4
                FRAGE_ART a_db       ; E=4
                FRAGE_ART a_dbn      ; E=4
                FRAGE_ART a_dt       ; E=4
                FRAGE_ART a_kat4     ; E=4
                FRAGE_ART a_allein   ; E=4
                FRAGE_ART a_mk       ; E=4
                FRAGE_ART ende       ; E=4
                FRAGE_ART nix        ; E=0
                FRAGE_ART erz_marke  ; E=0
                FRAGE_ART a_ld       ; E=4
                FRAGE_ART opname     ; E=0
                FRAGE_DEF a_abs      ; E=1
                FRAGE_DEF a_dw       ; E=1
                FRAGE_DEF a_allein   ; E=1
                FRAGE_DEF a_mk       ; E=1
                FRAGE_DEF ende       ; E=1
                FRAGE_DEF nix        ; E=0
                FRAGE_DEF erz_marke  ; E=0
                FRAGE_DEF opname     ; E=0
                FRAGE_ZELLEN a_db    ; E=5
                FRAGE_ZELLEN a_dbo   ; E=8
                FRAGE_ZELLEN a_dbn   ; E=3
                FRAGE_ZELLEN a_dbno  ; E=6
                FRAGE_ZELLEN a_dbk   ; E=4
                FRAGE_ZELLEN a_befehl ; E=1
                FRAGE_ZELLEN a_dw    ; E=1
                FRAGE_ZELLEN a_da    ; E=1
                FRAGE_ZELLEN a_dz    ; E=1
                FRAGE_ZELLEN a_ld    ; E=1
                DIREKT               ; E=1,2
                RECHNEN              ; E=2,10,21
                MIT_V                ; E=5
                PROBE                ; E=63
                PROBE2               ; E=78
                MIT_WHILE            ; E=0,1,2
                MIT_REPT             ; E=10,11,12
                MIT_SET              ; E=6,14
                MIT_P 41 42          ; E=41,42
                TYPT art(a_equ)+3    ; E=5
haupt:          164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
a_befehl:       020     0            ; Marke auf einem Befehl
a_dw:           dw      7            ; Marke auf dw
a_da:           da      a_dw         ; Marke auf da
a_dz:           dz      $wrzl        ; Marke auf dz
a_db:           db      5            ; 5 Zellen, Dezimalzahl
a_dbo:          db      010          ; 8 Zellen, Oktalzahl
a_dbn:          dbn     3            ; 3 Zellen, auf 0 gesetzt
a_dbno:         dbn     06           ; 6 Zellen, Oktalzahl
a_dbk:          db      4            ; 4 Zellen, mit Kommentar
a_dt:           dt      abc          ; Marke auf dt
a_kat4:         kat4    abcd         ; Marke auf kat4
a_allein:                            ; Marke allein auf einer Zeile
a_mk:           EIN_WORT             ; Marke auf einem Makroaufruf
a_ld:           .LD     a_dw         ; Marke auf einem markierten Namen (3.3.17)
opname:         opsym   123          ; Marke einer opsym-Zeile ist kein Symbol
ende:           end
a_abs:          abs     5            ; abs-Symbol
a_equ:          equ     07640        ; equ mit Oktalzahl
a_equd:         equ     100          ; equ mit Dezimalzahl
a_equs:         equ     a_abs+3      ; equ mit einem weiteren Symbol
a_stern:        equ     *            ; Adresse
a_lbl:          equ     a_dw+1       ; equ mit Label im Ausdruck
DEBUG:          abs     1            ; Schalter fuer PROBE
a_e10:          equ10   *            ; auf Vielfaches von 010
a_e40:          equ40   *            ; auf Vielfaches von 040
a_e100:         equ100  *            ; auf Vielfaches von 0100
a_spa:          spa     020          ; Sektoradresse
; Sollwerte von Hand hergeleitet (Zellen ab 0001 in Aufrufreihenfolge, Werte dezimal in den E=-Marken; hier oktal). 63 Woerter.
;#PRUEFE-START
; BZ=0102 US=1
; 0001: 00000000143   # ERZEUGE
; 0002: 00000000001   # FRAGE_ART a_abs
; 0003: 00000000002   # FRAGE_ART a_equ
; 0004: 00000000002   # FRAGE_ART a_equd
; 0005: 00000000002   # FRAGE_ART a_equs
; 0006: 00000000003   # FRAGE_ART a_stern
; 0007: 00000000003   # FRAGE_ART a_lbl
; 0010: 00000000003   # FRAGE_ART a_e10
; 0011: 00000000003   # FRAGE_ART a_e40
; 0012: 00000000003   # FRAGE_ART a_e100
; 0013: 00000000003   # FRAGE_ART a_spa
; 0014: 00000000004   # FRAGE_ART a_befehl
; 0015: 00000000004   # FRAGE_ART a_dw
; 0016: 00000000004   # FRAGE_ART a_da
; 0017: 00000000004   # FRAGE_ART a_dz
; 0020: 00000000004   # FRAGE_ART a_db
; 0021: 00000000004   # FRAGE_ART a_dbn
; 0022: 00000000004   # FRAGE_ART a_dt
; 0023: 00000000004   # FRAGE_ART a_kat4
; 0024: 00000000004   # FRAGE_ART a_allein
; 0025: 00000000004   # FRAGE_ART a_mk
; 0026: 00000000004   # FRAGE_ART ende
; 0027: 00000000000   # FRAGE_ART nix
; 0030: 00000000000   # FRAGE_ART erz_marke
; 0031: 00000000004   # FRAGE_ART a_ld
; 0032: 00000000000   # FRAGE_ART opname
; 0033: 00000000001   # FRAGE_DEF a_abs
; 0034: 00000000001   # FRAGE_DEF a_dw
; 0035: 00000000001   # FRAGE_DEF a_allein
; 0036: 00000000001   # FRAGE_DEF a_mk
; 0037: 00000000001   # FRAGE_DEF ende
; 0040: 00000000000   # FRAGE_DEF nix
; 0041: 00000000000   # FRAGE_DEF erz_marke
; 0042: 00000000000   # FRAGE_DEF opname
; 0043: 00000000005   # FRAGE_ZELLEN a_db
; 0044: 00000000010   # FRAGE_ZELLEN a_dbo
; 0045: 00000000003   # FRAGE_ZELLEN a_dbn
; 0046: 00000000006   # FRAGE_ZELLEN a_dbno
; 0047: 00000000004   # FRAGE_ZELLEN a_dbk
; 0050: 00000000001   # FRAGE_ZELLEN a_befehl
; 0051: 00000000001   # FRAGE_ZELLEN a_dw
; 0052: 00000000001   # FRAGE_ZELLEN a_da
; 0053: 00000000001   # FRAGE_ZELLEN a_dz
; 0054: 00000000001   # FRAGE_ZELLEN a_ld
; 0055: 00000000001   # DIREKT
; 0056: 00000000002   # DIREKT
; 0057: 00000000002   # RECHNEN
; 0060: 00000000012   # RECHNEN
; 0061: 00000000025   # RECHNEN
; 0062: 00000000005   # MIT_V
; 0063: 00000000077   # PROBE
; 0064: 00000000116   # PROBE2
; 0065: 00000000000   # MIT_WHILE
; 0066: 00000000001   # MIT_WHILE
; 0067: 00000000002   # MIT_WHILE
; 0070: 00000000012   # MIT_REPT
; 0071: 00000000013   # MIT_REPT
; 0072: 00000000014   # MIT_REPT
; 0073: 00000000006   # MIT_SET
; 0074: 00000000016   # MIT_SET
; 0075: 00000000051   # MIT_P 41 42
; 0076: 00000000052   # MIT_P 41 42
; 0077: 00000000005   # TYPT art(a_equ)+3
;#PRUEFE-ENDE
