; opt8.asm - Optimierer (Doku Abschnitt 5.2, Abschnitt 3.3.13): ein dw mit Marke, das in begin/bend steht, bleibt (so haelt man zusammengehoerige Zellen fest), das Literal wandert
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     #5           ; Zelle 0001: AC := 5 (Literal l0001, wandert nach 0005)
                210     tab          ; Zelle 0002: AC := AC + (tab) = 5 + 1
                164     0001         ; Zelle 0003: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0004: Halt
                equ10   *            ; Zaehler springt von 0005 auf 0010, Sprungbereich 0005 bis 0007 (drei Zellen)
                dw      9            ; Zelle 0010: Fueller ohne Marke (dw unmittelbar hinter equ10)
                begin                ; Tabelle festhalten
tab:            dw      1            ; Zelle 0011: Tabellenanfang, tab wird nur als ganzer Adressteil benutzt, bleibt aber wegen begin/bend
                dw      2            ; Zelle 0012: Tabellenglied
                dw      3            ; Zelle 0013: Tabellenglied
                bend                 ; Ende der festgehaltenen Tabelle
                end

; Sollwerte von Hand: 5 + 1 = 6; Literal l0001 auf 0005; die Tabelle tab bleibt auf 0011 bis 0013 (ohne begin/bend wuerde tab nach 0006 wandern); Halt auf 0004, BZ danach 0005.
;#PRUEFE-START
; BZ=0005 AC=00000000006 US=1
; 0005: 00000000005   # l0001
; 0011: 00000000001   # tab
; 0012: 00000000002   # Tabellenglied
; 0013: 00000000003   # Tabellenglied
;#PRUEFE-ENDE
