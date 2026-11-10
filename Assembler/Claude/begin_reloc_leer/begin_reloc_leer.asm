; begin_reloc_leer.asm - begin ohne Wirkung: RELOC-EQU ohne equ100/equ40 (keine Meldung), FILL allein, Schluesselwoerter mit gemischter
; Schreibweise und ein Block mit 0 Zellen (wird nicht verschoben, sein equ100 * wirkt am Ort). Assemblerdokumentation 5.4.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     t1               ; Zelle 0002: AC := (t1)
                210     t2               ; Zelle 0003: AC := AC + (t2)
                210     t3               ; Zelle 0004: AC := AC + (t3)
                240     erg              ; Zelle 0005: (erg) := AC
                020     0                ; Zelle 0006: Halt
                begin   RELOC-EQU        ; ohne equ100/equ40: bleibt am Ort, keine Meldung
t1:             dw      1                ; Zelle 0007
                bend                     ; Ende
                begin   fill             ; FILL allein, klein geschrieben: wirkungslos
t2:             dw      2                ; Zelle 0010
                bend                     ; Ende
                begin   Reloc-Equ        ; Block mit 0 Zellen: wird nicht verschoben
blk0:           equ100  *                ; wirkt am Ort: Zaehler auf die naechste 0100-Grenze
                bend                     ; Ende
t3:             dw      4                ; Zelle 0100 (hinter dem leeren Block)
ende:           end

; Sollwerte von Hand hergeleitet: t1 auf 0007 (Wert 1), t2 auf 0010 (Wert 2); der leere Block bleibt, sein equ100 * rueckt den Zaehler von 0011
; auf 0100, dort steht t3 (Wert 4). Summe 1 + 2 + 4 = 7. Halt auf 0006, BZ = 0007. Keine Literale, nichts im Bereich ab 07600 abwaerts.
;#PRUEFE-START
; BZ=0007 AC=00000000007 US=1
; 0001: 00000000007   # erg
; 0007: 00000000001   # t1
; 0010: 00000000002   # t2
; 0100: 00000000004   # t3
; 7500: 00000000000   # nichts verschoben
;#PRUEFE-ENDE
