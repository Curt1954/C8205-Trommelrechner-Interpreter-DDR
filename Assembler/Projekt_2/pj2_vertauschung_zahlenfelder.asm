                start
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
; Vertauschung zweier Zahlenfelder (pj2, Objektdatei-Vorgabe, Bilder "Vertauschung zweier Zahlenfelder")
; Original-Objektdatei: Kennzeichen 01 = Programmladeadresse P, 00 = absolut (Konstanten).
; Das Unterprogramm steht hier mit P = 3000. Die Zellen 0000 bis 0042 (relativ zu P) entsprechen
; Zelle fuer Zelle dem Vorgabebild; hinter jeder Zeile steht die Originalzeile.
; Aufruf: 025 vertausch (Sprung mit Rueckkehrabsicht), AC vorher loeschen. Der Rueckkehrbefehl
; RS landet im AC, 0004 sichert ihn nach 0036, das Unterprogramm endet dort mit dem Sprung zurueck.
; Parameter (im Bild "0." = vom Aufrufer zu versorgen; hier im Quelltext mit da vorbelegt):
;   0001 = Adresse a0 (erste Komponente Feld a), 0002 = Adresse b0, 0003 = Adresse an (letzte Komponente a).
; Ablauf: Die Befehle der Schleife (0017, 0021, 0022, 0024) werden zur Laufzeit mit den Adressen
; a_i und b_i gebildet; 0027 bis 0032 zaehlen a_i weiter, 0033/0034 bilden b_i+1; der Sprung 0035
; nach 0014 speichert den neuen Befehl b_i+1 (211) ein und bildet dort b_i+1 (240).
                equ     02000           ; Hauptprogramm ab 2000
haupt:          211     null            ; AC := 0 (RS darf nicht verfaelscht werden)
                025     vertausch       ; Sprung mit Rueckkehrabsicht
halt:           164     0001            ; DEBUG Nr. 0001
                020     0               ; Halt
null:           dw      0
                equ     03000           ; Programmladeadresse P des Unterprogramms
vertausch:      000     anfang          ; 0000 01  4 000.  RS
a0adr:          da      feld_a          ; 0001 0.          >a0<   (Parameter)
b0adr:          da      feld_b          ; 0002 0.          >b0<   (Parameter)
anadr:          da      a_ende          ; 0003 0.          >an<   (Parameter)
anfang:         240     rs              ; 0004 01 36 240.  RS-Sicherung
                211     a0adr           ; 0005 01  1 211.  >a0<
                210     k211            ; 0006 01 41 210.  >a0< 211
                240     a_ld            ; 0007 01 17 240.   "   >a_i< := >a0<
                210     k027            ; 0010 01 40 210.  >a0< 240
                240     a_st            ; 0011 01 22 240.   "
                211     b0adr           ; 0012 01  2 211.  >b0<
                210     k211            ; 0013 01 41 210.  >b0< 211
b_neu:          240     b_ld            ; 0014 01 21 240.  >b_i< 211   >b_i< := >b0<
                210     k027            ; 0015 01 40 210.  >b_i< 240
                240     b_st            ; 0016 01 24 240.   "
a_ld:           dw      0               ; 0017 0.           a_i        (zur Laufzeit: >a_i< 211)
                240     c               ; 0020 01 42 240.   "          c := a_i
b_ld:           dw      0               ; 0021 0.           b_i        (zur Laufzeit: >b_i< 211)
a_st:           dw      0               ; 0022 0.           "          a_i := b_i (zur Laufzeit: >a_i< 240)
                211     c               ; 0023 01 42 211.  a_i
b_st:           dw      0               ; 0024 0.           "          b_i := c (zur Laufzeit: >b_i< 240)
                211     a_ld            ; 0025 01 17 211.  >a_i< 211
                330     anadr           ; 0026 01  3 330.   "          Vergleich >a_i< mit >an<
                210     eine_ae         ; 0027 01 37 210.  >a_i<+1o 211   >a_i< := >a_i<+1o
                240     a_ld            ; 0030 01 17 240.   "
                210     k027            ; 0031 01 40 210.  >a_i<+1o 240
                240     a_st            ; 0032 01 22 240.   "
                211     b_ld            ; 0033 01 21 211.  >b_i< 211   >b_i< := >b_i<+1o
                210     eine_ae         ; 0034 01 37 210.  >b_i<+1o 211
                140     b_neu           ; 0035 01 14 140.   "          >a_i< <= >an< ?
rs:             dw      0               ; 0036 0.           "  RS
eine_ae:        dw      01000           ; 0037 00  1 000.  1o  (eine Adresseinheit)
k027:           dw      027             ; 0040 00  0 027.  Konstante f. Bef.-Umrechnung
k211:           dw      0211            ; 0041 00  0 211.  Konstante f. Befehlsbildung
c:              dw      0               ; 0042 0.          Arbeitsspeicher c
; Testdaten: Feld a und Feld b mit je 5 Komponenten (Daten, nicht Teil des Vorgabebildes)
                equ     03100
feld_a:         dw      0101
                dw      0102
                dw      0103
                dw      0104
a_ende:         dw      0105            ; letzte Komponente von a (>an<)
                equ     03200
feld_b:         dw      0201
                dw      0202
                dw      0203
                dw      0204
b_ende:         dw      0205
                end
