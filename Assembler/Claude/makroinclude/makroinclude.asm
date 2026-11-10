; makroinclude.asm - Test von $INCLUDE im Makrorumpf (Assemblerdokumentation 4.14)
;#DOK-0001 Makro INCTEST bindet teil/a.inc ein, diese bindet b.inc ein (relativ zur jeweiligen Datei)
;#MACRODATEI1=macro_inc.macro
;#PROT STUFE=2
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                INCTEST 5               ; Zellen 0001 bis 0004: 5, 10, 15, 105
haupt:          164     0001            ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet (dw dezimal, Sollwerte oktal); Halt auf 0006, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 US=1
; 0001: 00000000005   # $1 = 5
; 0002: 00000000012   # 5*2 = 10 = 012 (a.inc)
; 0003: 00000000017   # 5*3 = 15 = 017 (b.inc)
; 0004: 00000000151   # 5+100 = 105 = 0151
;#PRUEFE-ENDE
