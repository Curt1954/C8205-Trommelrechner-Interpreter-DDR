; symbolliteral2.asm - Symbol-Literal !<symbolname> und der Optimierer (Anforderungen_Symbolliteral.md, ab c82ass 1.03-005)
; equ40 * laesst die Zellen 0002 bis 0037 frei. Der Optimierer setzt dorthin die Literale in Tabellenreihenfolge:
; #5 (l0001) auf 0002, !hilf auf 0003, #7 (l0002) auf 0004. Das Symbol-Literal zaehlt nicht bei den Namen l0001, l0002.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
                equ40   *                ; Zaehler 0002 -> 0040, Luecke 0002 bis 0037
haupt:          211     #5               ; Zelle 0040: AC := 5
                240     !hilf            ; Zelle 0041: (hilf) := 5
                211     #7               ; Zelle 0042: AC := 7
                210     !hilf            ; Zelle 0043: AC := AC + (hilf) = 12 (dezimal) = 014 oktal
                240     erg              ; Zelle 0044: (erg) := AC
                164     0001             ; Zelle 0045: Diagnoseausgabe (nur im Test)
                020     0                ; Zelle 0046: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Halt auf 0046, BZ danach 0047; erg = 5 + 7 = 014 oktal; hilf (0003) enthaelt 5.
;#PRUEFE-START
; BZ=0047 AC=00000000014 US=1
; 0001: 00000000014   # erg
; 0002: 00000000005   # l0001
; 0003: 00000000005   # hilf
; 0004: 00000000007   # l0002
;#PRUEFE-ENDE
