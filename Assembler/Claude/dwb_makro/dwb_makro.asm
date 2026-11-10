; dwb_makro.asm - dwb im Makro-Praeprozessor: art, def und zellen einer dwb-Marke (Assemblerdokumentation 4.23, 3.3.19)
; FRAGE_ART, FRAGE_DEF, FRAGE_ZELLEN: je ein Wort mit dem Ergebnis der Abfrage
FRAGE_ART:      MACRO 1
                dw      $CALC(art($1))              ; Art des Symbols
                MEND
FRAGE_DEF:      MACRO 1
                dw      $CALC(def($1))              ; 1, wenn das Symbol vorhanden ist
                MEND
FRAGE_ZELLEN:   MACRO 1
                dw      $CALC(zellen($1))           ; Zellenzahl der Anweisung
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
w_dwb:          dwb     1011         ; Zelle 0001: Wort 11 = 013 oktal
                FRAGE_ART    w_dwb   ; Zelle 0002: art = 4 (Marke einer anderen Zeile)
                FRAGE_DEF    w_dwb   ; Zelle 0003: def = 1
                FRAGE_ZELLEN w_dwb   ; Zelle 0004: zellen = 1 (dwb belegt eine Zelle)
haupt:          164     0001         ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet: dwb 1011 = 8+2+1 = 11 = 013 oktal; art 4, def 1, zellen 1. Halt auf 0006, also BZ = 0007.
;#PRUEFE-START
; BZ=0007 US=1
; 0001: 00000000013   # w_dwb
; 0002: 00000000004   # FRAGE_ART w_dwb
; 0003: 00000000001   # FRAGE_DEF w_dwb
; 0004: 00000000001   # FRAGE_ZELLEN w_dwb
;#PRUEFE-ENDE
