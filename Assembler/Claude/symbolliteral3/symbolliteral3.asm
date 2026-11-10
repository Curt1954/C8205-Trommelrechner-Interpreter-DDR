; symbolliteral3.asm - Symbol-Literal !<symbolname> hinter da und als Text hinter dt (Anforderungen_Symbolliteral.md, ab c82ass 1.03-005)
; da !zg schreibt die Adresse der Arbeitszelle zg in die Zelle 0001; derselbe Name in 240 !zg meint dieselbe Zelle. Bei dt ist !ab Text, kein Literal.
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
zeiger:         da      !zg              ; Zelle 0001: Adresse der Arbeitszelle zg
haupt:          211     #5               ; Zelle 0002: AC := 5 (Literal l0001; das Symbol-Literal zg zaehlt nicht mit)
                240     !zg              ; Zelle 0003: (zg) := 5
                164     0001             ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0                ; Zelle 0005: Halt
ende:           end

; Sollwerte von Hand hergeleitet: Tabellenreihenfolge zg (0006), l0001 (0007); Halt auf 0005, BZ danach 0006.
;#PRUEFE-START
; BZ=0006 AC=00000000005 US=1
; 0006: 00000000005   # zg
; 0007: 00000000005   # l0001
;#PRUEFE-ENDE
