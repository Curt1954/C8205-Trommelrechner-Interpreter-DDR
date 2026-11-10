; kat6.asm - Test von kat6 (komprimierter Text, 5 Zeichen je Wort, Eingabecode der Kodetabelle, Stoppbit, z0 am letzten Wort), Doku 3.3.18
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
t1:             kat6    hallo welt   ; Zellen 0001 und 0002: Beispiel der Doku, Leerzeichen im Text ohne Backslash
t2:             kat6    10           ; Zelle 0003: Ziffer 0 hat den Code 00, das Stoppbit steht darueber
t3:             kat6    000          ; Zelle 0004: drei Nullen gehen nicht verloren
t4:             kat6    x$ingb=$inkb1$wrzl ; Zellen 0005 und 0006: alle drei Marken, volles erstes Wort
t5:             kat6    a/b          ; Zelle 0007: / hat den Code 061
t6:             kat6    abcde        ; Zelle 0010: genau ein volles Wort, Stoppbit in z2
t7:             kat6    ,%`.-        ; Zelle 0011: , % Akzent . - (Codes 073 074 060 033 040)
t8:             kat6    :+=89        ; Zelle 0012: : + = 8 9 (+ und = haben denselben Code 020)
t9:             kat6    z            ; Zelle 0013: ein einziges Zeichen
t10:            kat6    abcdef       ; Zellen 0014 und 0015: ein Zeichen im zweiten Wort
t11:            kat6    \ a \        ; Zelle 0016: drei Zeichen, fuehrendes und abschliessendes Leerzeichen bleiben
t12:            kat6    a$WRZL       ; Zelle 0017: Marke in Grossbuchstaben wird erkannt
t13:            kat6    $ingb=       ; Zelle 0020: Marke $ingb (037) und = (020), keine Warnung
haupt:          020     0            ; Zelle 0021: Halt
ende:           end

; Sollwerte von Hand aus der Codetabelle der Doku 3.3.18 hergeleitet (6 Bit je Zeichen = 2 Oktalziffern, erstes Zeichen rechts,
; Stoppbit 1 unmittelbar links vom letzten Zeichen des Wortes, z0 = 040000000000 im letzten Wort). Codes: 0 bis 7 = 00 bis 07,
; 8 = 010, 9 = 011, Leerzeichen = 012, : = 015, + und = = 020, a bis i = 021 bis 031, $wrzl = 032, . = 033, $ingb = 037,
; - = 040, j bis r = 041 bis 051, $inkb = 057, Akzent = 060, / = 061, s bis z = 062 bis 071, Komma = 073, % = 074.
; t1: h a l l o = 1 46 43 43 21 30 (volles Wort, Stoppbit z2); Leerzeichen w e l t = 5 63 43 25 66 12 (z0 und Stoppbit z2).
; t2: 1 und 0: Stoppbit in Bit 12 = 010000, dazu 01 und z0: 40000010001. t3: Stoppbit in Bit 18 = 01000000, z0: 40001000000.
; t4: x $ingb = $inkb 1 = 1 01 57 20 37 67; $wrzl = Stoppbit in Bit 6 = 0100 plus 032, z0: 40000000132.
; t5: a / b = Stoppbit in Bit 18: 4 00 01 22 61 21. t6: a b c d e = 5 25 24 23 22 21 (z0 und Stoppbit z2 beide gesetzt).
; t7: Komma % Akzent . - = 5 40 33 60 74 73. t8: : + = 8 9 = 5 11 10 20 20 15. t9: z = 0100 plus 071, z0: 40000000171.
; t10: a b c d e = 1 25 24 23 22 21 (nur Stoppbit z2); f = 0100 plus 026, z0: 40000000126.
; t11: Leerzeichen a Leerzeichen = 012 021 012 und Stoppbit in Bit 18: 4 00 01 12 21 12. t12: a $wrzl = Stoppbit in Bit 12: 4 00 00 13 22 1 (40000013221).
; t13: $ingb = : 037 und 020, Stoppbit in Bit 12: 40000012037.
;#PRUEFE-START
; BZ=0022
; 0001: 14643432130   # t1 (h a l l o, volles Wort ohne z0)
; 0002: 56343256612   # t1 (Leerzeichen w e l t, z0)
; 0003: 40000010001   # t2
; 0004: 40001000000   # t3
; 0005: 10157203767   # t4 (x $ingb = $inkb 1)
; 0006: 40000000132   # t4 ($wrzl, z0)
; 0007: 40001226121   # t5
; 0010: 52524232221   # t6
; 0011: 54033607473   # t7
; 0012: 51110202015   # t8
; 0013: 40000000171   # t9
; 0014: 12524232221   # t10 (a bis e)
; 0015: 40000000126   # t10 (f, z0)
; 0016: 40001122112   # t11
; 0017: 40000013221   # t12
; 0020: 40000012037   # t13
;#PRUEFE-ENDE
