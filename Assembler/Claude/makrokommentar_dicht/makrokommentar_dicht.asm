; makrokommentar_dicht.asm - Test: "name: MACRO;Kommentar" ohne Leerzeichen in der Makrodatei (Assemblerdokumentation 4.9, ab c82ass 1.01-031)
;#MACRODATEI1=makrokommentar_dicht.macro
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                MKDICHT                 ; Zelle 0001: 1
haupt:          164     0001            ; Zelle 0002: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0003: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Zelle 0001 enthaelt 1.
;#PRUEFE-START
; 0001: 00000000001   # MKDICHT
;#PRUEFE-ENDE
