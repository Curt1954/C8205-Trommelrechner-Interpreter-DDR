; begin_reloc_text.asm - RELOC-EQU-Bloecke mit dt, dtm, dto, kat4 werden verschoben; der Assembler zaehlt ihre Zellen selbst (Assemblerdokumentation 3.3.12, 5.4)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
t0:             dt      =                ; Zellen 0001 und 0002: Umschaltzeichen und =; danach hat sich der KB/GB-Zustand der Textzaehlung geaendert
                begin   RELOC-EQU FILL   ; Block A (Gruppe 1): kommt dicht unter 07600; Literale duerfen in die Luecke dahinter
                equ100  *                ; Rasterung 0100
ba:             dt      1                ; im geaenderten Zustand zwei Zellen (Umschaltzeichen, Ziffer 1)
                dt      1                ; eine Zelle
                kat4    1                ; eine Zelle
                bend                     ; Ende von Block A: 4 Zellen 07500 bis 07503, Luecke ab 07504
                begin   RELOC-EQU        ; Block B (Gruppe 2): kommt darunter
                equ40   *                ; Rasterung 040
bb:             dto     1                ; eine Zelle: dto setzt kein Umschaltzeichen
                dtm     1                ; zwei Zellen: dtm setzt immer das Umschaltzeichen
                bend                     ; Ende von Block B: 3 Zellen, Anfang 07500 - 040 = 07440
erg:            dw      0                ; Zelle 0003: Ergebnis 1
erg2:           dw      0                ; Zelle 0004: Ergebnis 2
haupt:          211     ba               ; Zelle 0005: AC := erstes Wort von Block A
                240     erg              ; Zelle 0006: (erg) := AC
                211     #5               ; Zelle 0007: AC := Literal 5 (der Assembler legt es in die Luecke von Block A)
                240     erg2             ; Zelle 0010: (erg2) := AC
                020     0                ; Zelle 0011: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Kodetabelle, Abschnitt 3.3.5): dt = setzt zuerst das Umschaltzeichen $ingb (Ausgabeadresse 0570), dann = (0400);
; danach verlangt die Ziffer 1 das Umschaltzeichen $inkb (1170) und die Ziffer (0010): Block A hat 4 Zellen (waeren es 3, laege das Literal auf 07503).
; Wort = 0000 <Ausgabeadresse> 030. kat4 1: Code 001 mit z0 = 1 gleich 40000000001. Halt auf Zelle 0011, BZ = 0012.
;#PRUEFE-START
; BZ=0012 AC=00000000005 US=1
; 0001: 00000570030   # dt =: Umschaltzeichen GB
; 0002: 00000400030   # dt =: Zeichen =
; 0003: 00001170030   # erg: erstes Wort von Block A (Umschaltzeichen KB)
; 0004: 00000000005   # erg2: Literal 5
; 7500: 00001170030   # Block A: Umschaltzeichen KB
; 7501: 00000010030   # Block A: Ziffer 1
; 7502: 00000010030   # Block A: dt 1
; 7503: 40000000001   # Block A: kat4 1
; 7504: 00000000005   # Literal 5 in der Luecke hinter Block A
; 7440: 00000010030   # Block B: dto 1
; 7441: 00001170030   # Block B: dtm 1, Umschaltzeichen KB
; 7442: 00000010030   # Block B: dtm 1, Ziffer 1
;#PRUEFE-ENDE
