; einmal_add_ref.asm - Test des Makros FK_MATH (Assembler/Sourcecode/c82ass.makros): nur fk_add: weder Subtraktion noch Multiplikation noch Division im Speicher (Fassung ohne Wiederholungen)
; Die UP werden nur einmal erzeugt, auch wenn FK_MATH mehrfach und mit verschiedenen Parametern steht; die Wiederholungen erzeugen nichts
; (ein doppelter Code scheiterte schon an der doppelten Marke). Gegenprobe: einmal_vergleich.sh vergleicht .obj und .sym mit der Fassung ohne Wiederholungen.
; Rechnet a = 0,25 und b = 0,375 (dwf): add 0,625, sub -0,125, mul 3/32, div 2/3; die Worte stehen von Hand hergeleitet im Pruefblock.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung ueber die Daten zum Hauptprogramm
wa:             dw      010000000000     ; Zelle 0001: a = 0,25 (2^30)
wb:             dw      014000000000     ; Zelle 0002: b = 0,375 (3 * 2^29)
res_add:        dw      0            ; Ergebnis add
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)
haupt:          211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     fk_add       ; Aufruf fk_add, Ergebnis im AC
                240     res_add      ; Ergebnis ablegen
                020     0            ; Halt
; ---- UP aus dem Makro FK_MATH, hinter dem Hauptprogramm (der Ablauf laeuft nicht hinein)
                FK_MATH add       ; erster Aufruf: Einsprung fk_add, gemeinsamer Teil
ende:           end                  ; Ende

; Sollwerte von Hand hergeleitet: a = 2^30, b = 3 * 2^29 (Wort = x * 2^32): add 5 * 2^29 = 024000000000, sub -2^29 = 077740000000 (Zweierkomplement 33 Bit), mul 3 * 2^27 = 003000000000, div 2/3 * 2^32 = 2863311531 = 025252525253.
;#PRUEFE-START
; BZ=0013 US=1
; 0003: 24000000000   # add
;#PRUEFE-ENDE
