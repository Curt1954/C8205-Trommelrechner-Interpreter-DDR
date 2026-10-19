; C8205 BIS - Adressdruck (8-Kanal-Ausfuehrung, R 300-Code), abgeleitet vom Triadendruck
;
; Das Unterprogramm druckt vom Wort in R1 nur die Adresse: die mittleren 4 Triaden
; (Wortstellen z12 bis z23) als 4 Oktalziffern. Beispiel: Wort 0123 4567 012 -> Ausdruck 4567.
;
; Aenderungen gegenueber dem Triadendruck:
;  1. Vorlauf: R1 wird einmal um 12 Bit zyklisch nach links gedreht (616 ueber die Nullspur 7640 ff.),
;     dadurch steht die oberste Adressziffer (t6) oben. Die Nullspur wird vorher mit 441 geloescht.
;  2. Der Zaehler td_z (konst_7770) enthaelt nur 3 Einsen: nach 4 Ziffern ist er 0, dann Rueckkehr.
; Die Schleife selbst (217/006/006, GX-Auswahl 520, dto-Zellen) bleibt unveraendert an ihren Sektoren.
; Das Wort steht in der Transportzelle 7777 (wie bisher); der Aufrufer waehlt vorher den Kanal an.

                start
                000     haupt    ; Zelle 0000: Sprung zum Hauptprogramm

; ---- Adressdruck (Ansprungzelle 053) ------------------------------------------------------
adressdruck:    equ100  *
                240     td_rs   ; Rueckkehrbefehl sichern
                000     vorlauf ; 12 Bit drehen, Einsen-Spur anlegen (Code auf Spur 0140)
                db      1       ; ungenutzt (Platzhalter, haelt "schleife" auf 0103)
schleife:       217     adr7777      ; das auszugebende Wort als Uebergabe
                006     verschieben
                spa     05
                dto     1
                dto     6
zu_gx:          520     adr7721
konst_7770:     dw      070000000000  ; Zaehler: 3 Einsen = 4 Ziffern
                311     td_z
                170     td_rs
                004     zn      ; td_z := td_z um 1 Bit nach links
                spa     014
                dto     4
verschieben:    006     speichern_r1
                db      1       ; ungenutzt
konst_7:        dw      07      ; Konstante 0000 0000 007 zum Ausblenden
                db      2       ; ungenutzt
                spa     022
                dto     2
                dto     7
speichern_r1:   240     adr7777
                200     konst_7
                000     zu_gx
konst_1:        dw      01      ; Konstante
                spa     030
                dto     0
                dto     5
spur_speich:    440     adr7724 ; AC auf Spur speichern
                211     konst_7770
zn:             240     td_z
                000     schleife
                db      1       ; unbenutzt
                spa     037
                dto     3
adr7721:        abs     07721
adr7724:        abs     07724
adr7777:        abs     07777
r1:             abs     07773
r3:             abs     07774
r2:             abs     07776
td_rs:          abs     07741           ; Adressdruck: Rueckkehrbefehl
td_z:           abs     07720           ; Adressdruck: Zaehler
nullspur:       abs     07640           ; Nullspur (441: alle 32 Zellen := 0)
nz_12:          abs     07644           ; 12 Nullzellen bis Position 37 (616: 12 Linksverschiebungen)

; ---- Vorlauf (freie Spur 0140) ------------------------------------------------------------
                equ     0140
vorlauf:        441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7777         ; AC := Wort
                616     nz_12           ; 12 Bit zyklisch links: Adressziffern stehen oben
                240     adr7777         ; Wort zurueck in die Transportzelle
                211     konst_1         ; AC := 1
                000     spur_speich     ; weiter: Einsen-Spur 7700 ff. anlegen, Zaehler setzen

;
haupt:          equ     02000
                030     04500
                dz      $inkb
                211     beispiel        ; Beispielwort, davon wird die Adresse gedruckt
                240     adr7777
                025     adressdruck
                020     0000
beispiel:       dw      01234567012     ; Adresse = mittlere 4 Ziffern = 4567
