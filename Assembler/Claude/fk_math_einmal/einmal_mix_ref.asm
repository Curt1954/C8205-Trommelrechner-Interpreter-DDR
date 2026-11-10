; einmal_mix_ref.asm - Test des Makros FK_MATH (Assembler/Sourcecode/c82ass.makros): Multiplikation zuerst, dann gemischt mit Wiederholungen (Fassung ohne Wiederholungen)
; Die UP werden nur einmal erzeugt, auch wenn FK_MATH mehrfach und mit verschiedenen Parametern steht; die Wiederholungen erzeugen nichts
; (ein doppelter Code scheiterte schon an der doppelten Marke). Gegenprobe: einmal_vergleich.sh vergleicht .obj und .sym mit der Fassung ohne Wiederholungen.
; Rechnet a = 0,25 und b = 0,375 (dwf): add 0,625, sub -0,125, mul 3/32, div 2/3; die Worte stehen von Hand hergeleitet im Pruefblock.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung ueber die Daten zum Hauptprogramm
wa:             dw      010000000000     ; Zelle 0001: a = 0,25 (2^30)
wb:             dw      014000000000     ; Zelle 0002: b = 0,375 (3 * 2^29)
res_add:        dw      0            ; Ergebnis add
res_sub:        dw      0            ; Ergebnis sub
res_mul:        dw      0            ; Ergebnis mul
res_div:        dw      0            ; Ergebnis div
r1:             abs     07773        ; Register R1 (nur Bezug)
r2:             abs     07776        ; Register R2 (nur Bezug)
haupt:          211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     fk_add       ; Aufruf fk_add, Ergebnis im AC
                240     res_add      ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     fk_sub       ; Aufruf fk_sub, Ergebnis im AC
                240     res_sub      ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     fk_mul       ; Aufruf fk_mul, Ergebnis im AC
                240     res_mul      ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     fk_div       ; Aufruf fk_div, Ergebnis im AC
                240     res_div      ; Ergebnis ablegen
                020     0            ; Halt
; ---- UP aus dem Makro FK_MATH, hinter dem Hauptprogramm (der Ablauf laeuft nicht hinein)
                FK_MATH mul       ; erster Aufruf: Einsprung fk_mul, Kern von mul/div, gemeinsamer Teil
                FK_MATH add       ; Einsprung fk_add
                FK_MATH alle      ; ergaenzt nur die Einspruenge fk_sub und fk_div
                FK_MATH alle      ; ergaenzt die Einspruenge fk_add und fk_sub
ende:           end                  ; Ende

; Sollwerte von Hand hergeleitet: a = 2^30, b = 3 * 2^29 (Wort = x * 2^32): add 5 * 2^29 = 024000000000, sub -2^29 = 077740000000 (Zweierkomplement 33 Bit), mul 3 * 2^27 = 003000000000, div 2/3 * 2^32 = 2863311531 = 025252525253.
;#PRUEFE-START
; BZ=0040 US=1
; 0003: 24000000000   # add
; 0004: 74000000000   # sub
; 0005: 03000000000   # mul
; 0006: 25252525253   # div
;#PRUEFE-ENDE
