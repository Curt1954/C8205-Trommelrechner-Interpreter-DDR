; dwfg_makro.asm - dwf und dwg im Makro-Praeprozessor: art, def und zellen einer dwf- und einer dwg-Marke (Assemblerdokumentation 4.23, 3.3.20, 3.3.21)
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
w_dwf:          dwf     0.5          ; Zelle 0001: Wort 20000000000
w_dwg:          dwg     16           ; Zelle 0002: Wort 22600000000
                FRAGE_ART    w_dwf   ; Zelle 0003: art = 4 (Marke einer anderen Zeile)
                FRAGE_DEF    w_dwf   ; Zelle 0004: def = 1
                FRAGE_ZELLEN w_dwf   ; Zelle 0005: zellen = 1 (dwf belegt eine Zelle)
                FRAGE_ART    w_dwg   ; Zelle 0006: art = 4
                FRAGE_DEF    w_dwg   ; Zelle 0007: def = 1
                FRAGE_ZELLEN w_dwg   ; Zelle 0010: zellen = 1 (dwg belegt eine Zelle)
haupt:          164     0001         ; Zelle 0011: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet: dwf 0.5 = z1 = 020000000000 oktal; dwg 16 = 0.5 * 2^5, e' = 37 = 045 oktal, Mantisse 2^25:
; (045 << 26) + 2^25 = 22600000000 oktal (Beispiel der Doku 3.3.21); art 4, def 1, zellen 1. Halt auf 0012, also BZ = 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 20000000000   # w_dwf
; 0002: 22600000000   # w_dwg
; 0003: 00000000004   # FRAGE_ART w_dwf
; 0004: 00000000001   # FRAGE_DEF w_dwf
; 0005: 00000000001   # FRAGE_ZELLEN w_dwf
; 0006: 00000000004   # FRAGE_ART w_dwg
; 0007: 00000000001   # FRAGE_DEF w_dwg
; 0010: 00000000001   # FRAGE_ZELLEN w_dwg
;#PRUEFE-ENDE
