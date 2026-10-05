; Mini-Beispiel Befehl 065: bedingter Sprung mit Rückkehrabsicht
; SP gesetzt:      wie 025 -> Unterprogramm "up" läuft, erg := 1
; SP nicht gesetzt: AC := 0, kein Sprung -> Unterprogramm läuft nicht, erg bleibt 0
                start
                000     haupt
erg:            dw      0            ; wird vom Unterprogramm auf 1 gesetzt
eins:           dw      1
rueck:          db      1            ; hier steht zur Laufzeit der Rücksprung
haupt:          065     up           ; Aufruf nur, wenn SP gesetzt
                164     0001
                020     0            ; Halt (Rückkehrpunkt bzw. Fortsetzung ohne Aufruf)
up:             240     rueck        ; Rücksprungwort aus AC sichern
                211     eins
                240     erg          ; erg := 1
                000     rueck
ende:           end
