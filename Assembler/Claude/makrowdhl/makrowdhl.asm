; makrowdhl.asm - Test: mehrere !$wdhl-Zeilen in einem Makro (Assemblerdokumentation 4.16)
;#DOK-0001 Test: Makro ZWEISCHIEB (zwei Zeilen neue Form) und ZWEIALT (zwei Zeilen alte Form) aus macro_wdhl.macro
;#PROT STUFE=2
;#MACRODATEI1=macro_wdhl.macro
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
einsen:         dw      077777777777 ; Zelle 0001: alle 33 Bits auf 1
zw:             dw      0            ; Zelle 0002: Zwischenergebnis (initialisiert)
erg1:           dw      0            ; Zelle 0003: Ergebnis 1 (initialisiert)
erg2:           dw      0            ; Zelle 0004: Ergebnis 2 (initialisiert)
haupt:          211     einsen       ; Zelle 0005: AC := alle Bits 1
                440     02000        ; Zelle 0006: alle 32 Zellen der Spur 2000 := AC (alle Bits 1)
                ZWEISCHIEB 3 2 02000 zw ; Zellen 0007 bis 0011: 3-fach links, zw sichern, 2-fach links
                240     erg1         ; Zelle 0012: erg1 := AC
                211     einsen       ; Zelle 0013: AC := alle Bits 1
                ZWEIALT NE LI KON 3 02000 ; Zellen 0014 und 0015: zweimal 3-fach links
                240     erg2         ; Zelle 0016: erg2 := AC
                020     0            ; Zelle 0017: Halt
ende:           end

; Sollwerte von Hand hergeleitet. Die Spur 2000 enthält 32 mal "alle Bits 1"; die Konjunktion lässt den AC unverändert,
; jede der n Wiederholungen schiebt den AC um ein Bit nach links (33 Bit, nicht zyklisch, von rechts mit 0 aufgefüllt).
; zw: 3 Verschiebungen = Bits 3 bis 32 gesetzt = 77777777770; erg1: 3 + 2 = 5 Verschiebungen = 77777777740;
; erg2: 3 + 3 = 6 Verschiebungen = 77777777700 (auch der AC am Ende). Halt auf Zelle 0017, BZ danach 0020.
;#PRUEFE-START
; BZ=0020 AC=77777777700 US=1
; 0002: 77777777770   # zw
; 0003: 77777777740   # erg1
; 0004: 77777777700   # erg2
;#PRUEFE-ENDE
