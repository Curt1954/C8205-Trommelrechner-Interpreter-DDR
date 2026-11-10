; ztd_stub.asm - Pruefling fuer ZTL: ersetzt ZTD in den Tests (kein echtes ZTD). Einsprung: Relativadresse 0000.
; ZTL startet es mit dem Sprungwort 000 <Dienst von ZTL> im AC. Das Stueck sichert es, setzt aus einer Auftragstabelle
; (absolute Zellen 1100 ff., je Zeile 8 Zellen) die Uebergabezellen von ZTL, ruft den Dienst (025) und traegt die Ergebnisse in die Zeile ein.
; Zeile: +0 ZTL_LAGE, +1 ZTL_LAENGE, +2 Hauptleitadresse (Adresswort), +3 ZTL_GRENZE (Adresswort), +4 Status (Ergebnis),
;   +5 ZTL_PUFFER (Ergebnis), +6 RA nach dem Laden (Ergebnis), +7 1 = gueltige Zeile, 0 = Ende der Tabelle.
; Die Leitadressen 2 bis 9 (7612 bis 7621) werden vor dem ersten Aufruf aus den Zellen 1300 bis 1307 uebernommen.
; Danach Halt (020).
                start                ; Zaehlung beginnt bei 0000 (relativ)
anfang:         000     haupt        ; rel 0000: Einsprung
dz:             dw      0            ; hier steht das Sprungwort 000 dienst
jp:             dw      0            ; Adresswort der laufenden Auftragszeile
c1e:            dw      01000        ; 1 Zelle in Adresseneinheiten
c2e:            dw      02000        ; 2 Zellen
c3e:            dw      03000        ; 3 Zellen
c4e:            dw      04000        ; 4 Zellen
c5e:            dw      05000        ; 5 Zellen
c6e:            dw      06000        ; 6 Zellen
c7e:            dw      07000        ; 7 Zellen
c10e:           dw      010000       ; 8 Zellen: naechste Zeile
c240:           dw      0240         ; Befehlscode 240
c0:             dw      0            ; 0
la2:            abs     01300        ; Leitadressen 2 bis 9 (Vorgabe fuer die Tests)
adr7612:        abs     07612        ; 2. Leitadresse
adr7613:        abs     07613        ; 3.
adr7614:        abs     07614        ; 4.
adr7615:        abs     07615        ; 5.
adr7616:        abs     07616        ; 6.
adr7617:        abs     07617        ; 7.
adr7620:        abs     07620        ; 8.
adr7621:        abs     07621        ; 9.
adr7611:        abs     07611        ; Hauptleitadresse
adr7622:        abs     07622        ; ZTL_LAGE
adr7623:        abs     07623        ; ZTL_LAENGE
adr7624:        abs     07624        ; ZTL_PUFFER
adr7625:        abs     07625        ; ZTL_GRENZE
adr7626:        abs     07626        ; ZTL_STATUS
adr7742:        abs     07742        ; RA
atab:           dw      01100000     ; Adresswort der Auftragstabelle (1100)
la3:            abs     01301        ; Zelle 1301
la4:            abs     01302
la5:            abs     01303
la6:            abs     01304
la7:            abs     01305
la8:            abs     01306
la9:            abs     01307
haupt:          240     dz           ; Sprungwort von ZTL sichern
                211     la2          ; Leitadressen 2 bis 9 uebernehmen
                240     adr7612
                211     la3
                240     adr7613
                211     la4
                240     adr7614
                211     la5
                240     adr7615
                211     la6
                240     adr7616
                211     la7
                240     adr7617
                211     la8
                240     adr7620
                211     la9
                240     adr7621
                211     atab         ; erste Zeile
                240     jp
zeile:          211     jp           ; +7: Zeile gueltig?
                210     c7e
                251     0
                330     c0
                170     fertig       ; 0: Ende der Tabelle
                211     jp           ; +0 Lage
                251     0
                240     adr7622
                211     jp           ; +1 Laenge
                210     c1e
                251     0
                240     adr7623
                211     jp           ; +2 Hauptleitadresse
                210     c2e
                251     0
                240     adr7611
                241     adr7742      ; RA := 0
                211     jp           ; +3 Grenze
                210     c3e
                251     0
                240     adr7625
                025     dz           ; Dienst von ZTL aufrufen
                211     jp           ; +4 := Status
                210     c4e
                210     c240
                240     g1
                211     adr7626
g1:             dw      0            ; hier steht zur Laufzeit 240 <Zeile +4>
                211     jp           ; +5 := Puffer
                210     c5e
                210     c240
                240     g2
                211     adr7624
g2:             dw      0            ; hier steht zur Laufzeit 240 <Zeile +5>
                211     jp           ; +6 := RA
                210     c6e
                210     c240
                240     g3
                211     adr7742
g3:             dw      0            ; hier steht zur Laufzeit 240 <Zeile +6>
                211     jp           ; naechste Zeile
                210     c10e
                240     jp
                000     zeile
fertig:         020     0            ; Halt
ende:           end
