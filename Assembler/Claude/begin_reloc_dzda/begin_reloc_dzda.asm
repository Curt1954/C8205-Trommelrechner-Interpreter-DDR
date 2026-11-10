; begin_reloc_dzda.asm - Block mit begin RELOC-EQU, der dz, da und dw enthaelt: dz und da zaehlen je eine Zelle (Assemblerdokumentation 3.3.12, 5.4)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
erg:            dw      0                ; Zelle 0001: Ergebnis
haupt:          211     z1               ; Zelle 0002: AC := Wort der Zelle z1
                240     erg              ; Zelle 0003: (erg) := AC
                020     0                ; Zelle 0004: Halt
                begin   RELOC-EQU        ; Block X: Gruppe 1
blkx:           equ100  *                ; erste Anweisung: Gruppe 1
z1:             dz      $wrzl            ; erste Zelle des Blocks
                da      erg              ; zweite Zelle: Adresse von erg
                dw      5                ; dritte Zelle
                bend                     ; Ende Block X
ende:           end

; Sollwerte von Hand hergeleitet: Der Block belegt 3 Zellen, aufgerundet auf 0100; Anfang 07600 - 0100 = 07500.
; z1 = dz $wrzl = 00002720030 (Ausgabeadresse 2720). da erg: erg liegt auf Zelle 1, um 9 Bit verschoben = 00000001000. dw 5 = 5.
; Halt auf Zelle 0004, BZ = 0005; der AC enthaelt das Wort von z1.
;#PRUEFE-START
; BZ=0005 AC=00002720030 US=1
; 0001: 00002720030   # erg
; 7500: 00002720030   # z1, Anfang des Blocks
; 7501: 00000001000   # da erg
; 7502: 00000000005   # dw 5
;#PRUEFE-ENDE
