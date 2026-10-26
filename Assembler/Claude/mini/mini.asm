; mini.asm - Minimalbeispiel: Zelle 0001 (017 oktal) nach Zelle 0002 kopieren
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
wert:           dw      017          ; Zelle 0001: Konstante
erg:            dw      0            ; Zelle 0002: Ergebnis (initialisiert)
haupt:          211     wert         ; AC := (wert)   laden
                240     erg          ; (erg) := AC    speichern
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet. Zelle 0001 (017) wird nach Zelle 0002 kopiert; Halt auf 0006.
;#PRUEFE-START
; BZ=0007 AC=00000000017 US=1
; 0002: 00000000017   # erg
;#PRUEFE-ENDE
