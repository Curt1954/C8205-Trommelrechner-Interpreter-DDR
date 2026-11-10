; makroadr_zyklus.asm - adr/abstand mit Zyklus: das Makro WEIT waehlt die Form nach dem Abstand, den es selbst beeinflusst
; Abstand anf bis ende mit kurzer Form (1 Wort) = 6, mit langer Form (2 Woerter) = 7; beides groesser als 5: die lange Form ist stabil
WEIT:           MACRO 2
                $IF $CALC(abstand($1,$2)) > 5
                dw      021                         ; lange Form, erstes Wort
                dw      022                         ; lange Form, zweites Wort
                $ELSE
                dw      011                         ; kurze Form
                $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          164     0001         ; Zelle 0001: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0002: Halt
anf:            dw      0            ; Zelle 0003
                WEIT    anf ende     ; Zellen 0004 und 0005 (lange Form)
                db      4            ; Zellen 0006 bis 0011 oktal 0011 (vier Zellen: dezimal 6 bis 9)
ende:           dw      9            ; Zelle 0012 oktal (dezimal 10)
                end

; Sollwerte von Hand hergeleitet. Probelauf 1 (Wert 0): kurze Form, Abstand 6; Lauf 2 (6 > 5): lange Form, Abstand 7; Lauf 3 (7 > 5): lange Form, Tabelle gleich Lauf 2 = Konvergenz.
; Ergebnis: Zellen 4 und 5 = 021 und 022, vier Zellen db 4 auf dezimal 6 bis 9, ende auf dezimal 10 = 012 oktal mit Wert 9 = 011. Halt auf Zelle 0002, also BZ = 0003.
;#PRUEFE-START
; BZ=0003 US=1
; 0004: 00000000021   # WEIT, lange Form, erstes Wort
; 0005: 00000000022   # WEIT, lange Form, zweites Wort
; 0012: 00000000011   # ende
;#PRUEFE-ENDE
