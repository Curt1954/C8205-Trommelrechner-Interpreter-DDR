; einmal_sub_ref.asm - Test des Makros GK_MATH (Assembler/Sourcecode/c82ass.makros): Subtraktion zuerst, Einspruenge spaeter einzeln, mit Wiederholungen (Fassung ohne Wiederholungen, nur Vergleich)
; Die UP werden nur einmal erzeugt, auch wenn GK_MATH mehrfach und mit verschiedenen Parametern steht; die Wiederholungen erzeugen nichts
; (ein doppelter Code scheiterte schon an der doppelten Marke). Gegenprobe: einmal_vergleich.sh vergleicht .obj und .sym mit der Fassung ohne Wiederholungen.
; Rechnet a = 3 und b = 2 (dwg): add 5, sub 1, mul 6, div 1,5; die Worte stehen von Hand hergeleitet im Pruefblock.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung ueber die Daten zum Hauptprogramm
wa:             dw      021300000000     ; Zelle 0001: a = 3
wb:             dw      021200000000     ; Zelle 0002: b = 2
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
                025     gk_add       ; Aufruf gk_add, Ergebnis im AC
                240     res_add       ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     gk_sub       ; Aufruf gk_sub, Ergebnis im AC
                240     res_sub       ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     gk_mul       ; Aufruf gk_mul, Ergebnis im AC
                240     res_mul       ; Ergebnis ablegen
                211     wa           ; AC := a
                240     r1           ; R1 := a
                211     wb           ; AC := b
                240     r2           ; R2 := b
                025     gk_div       ; Aufruf gk_div, Ergebnis im AC
                240     res_div       ; Ergebnis ablegen
                020     0            ; Halt
; ---- UP aus dem Makro GK_MATH, hinter dem Hauptprogramm (der Ablauf laeuft nicht hinein)
                GK_MATH sub          ; erster Aufruf
                GK_MATH div          ; Einsprung gk_div
                GK_MATH add          ; Einsprung gk_add
                GK_MATH mul          ; Einsprung gk_mul
ende:           end                  ; Ende

; Sollwerte von Hand hergeleitet: a = 3/4*2^2, b = 1/2*2^2, Wort = (e+32)*2^26 + M; 5 = 5/8*2^3, 1 = 1/2*2^1, 6 = 3/4*2^3, 1,5 = 3/4*2^1.
;#PRUEFE-START
; BZ=0040 US=1
; 0003: 21640000000   # add
; 0004: 20600000000   # sub
; 0005: 21700000000   # mul
; 0006: 20700000000   # div
;#PRUEFE-ENDE
