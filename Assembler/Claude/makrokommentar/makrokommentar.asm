; makrokommentar.asm - Test: Kommentar hinter MACRO in der Makrodatei (Assemblerdokumentation 4.9, ab c82ass 1.01-007)
;#DOK-0001 Kommentar hinter MACRO: ohne Parameter, mit Zahl, ohne Leerzeichen vor dem Semikolon, variable Zahl, Tabulatoren; zum Vergleich im Quelltext
;#MACRODATEI1=makrokommentar.macro
;#PROT STUFE=2
QNULL:          MACRO   ; Quelltext: Kommentar hinter MACRO (gilt dort schon immer)
                dw      21              ; Wort 21 dezimal (025 oktal)
                MEND                    ; Ende von QNULL
QZWEI:          MACRO 2 ; Quelltext: Kommentar hinter der Parameterzahl
                dw      $1+$2           ; Summe der beiden Parameter
                MEND                    ; Ende von QZWEI
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                MKNULL                  ; Zelle 0001: 11 dezimal = 013 oktal
                MKZWEI  3 4             ; Zelle 0002: 3+4 = 7
                MKDICHT 3 4             ; Zelle 0003: 3*4 = 12 dezimal = 014 oktal
                MKVAR   5               ; Zelle 0004: 5
                MKVAR   6 7 8           ; Zelle 0005: 6 (bei 1+ sind weitere Parameter zulaessig)
                MKTAB   1 2 3           ; Zelle 0006: 1+2+3 = 6
                QNULL                   ; Zelle 0007: 21 dezimal = 025 oktal
                QZWEI   10 20           ; Zelle 0010: 10+20 = 30 dezimal = 036 oktal
haupt:          164     0001            ; Zelle 0011: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zeilen dezimal, hier oktal); Halt auf 0012, BZ danach 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000013   # MKNULL
; 0002: 00000000007   # MKZWEI
; 0003: 00000000014   # MKDICHT
; 0004: 00000000005   # MKVAR
; 0005: 00000000006   # MKVAR
; 0006: 00000000006   # MKTAB
; 0007: 00000000025   # QNULL
; 0010: 00000000036   # QZWEI
;#PRUEFE-ENDE
