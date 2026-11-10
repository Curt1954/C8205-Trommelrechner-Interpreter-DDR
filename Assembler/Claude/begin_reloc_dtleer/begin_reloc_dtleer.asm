; begin_reloc_dtleer.asm - RELOC-EQU-Block, dessen einzige Anweisung ein leeres dt ist: 0 Zellen, der Block bleibt am Ort (Assemblerdokumentation 5.4)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
                begin   RELOC-EQU        ; Block ohne Zellen: wird nicht verschoben
                equ100  *                ; wirkt dann am Ort: Zaehler auf 0100 aufrunden
                dt      \\               ; leerer Text: keine Zelle
                bend                     ; Ende des leeren Blocks
erg:            dw      0                ; Zelle 0100: Ergebnis
haupt:          211     #7               ; Zelle 0101: AC := Literal 7
                240     erg              ; Zelle 0102: (erg) := AC
                020     0                ; Zelle 0103: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Der Block hat 0 Zellen und bleibt; equ100 * rundet den Zaehler von 0001 auf 0100, erg liegt auf 0100,
; der Halt auf 0103, BZ = 0104; das Literal 7 steht hinter dem Programm (Zelle 0104), der AC enthaelt 7.
;#PRUEFE-START
; BZ=0104 AC=00000000007 US=1
; 0100: 00000000007   # erg
;#PRUEFE-ENDE
