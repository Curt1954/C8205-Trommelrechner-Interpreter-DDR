; C8205 BIS - Druckprogramme fuer Oktalziffern (8-Kanal-Ausfuehrung, R 300-Code)
;
; Drei Unterprogramme in einer Datei. Das auszugebende Wort steht in der Transportzelle 7777,
; der Aufrufer waehlt vorher den Ausgabekanal an (030 04500) und schaltet auf Ziffernlage (dz $inkb).
; Jedes Unterprogramm liegt auf einer eigenen Spur, weil der GX-Befehl 520 den Folgebefehl (die
; dto-Zellen der Ziffern) aus der Spur des Befehlszaehlers entnimmt:
;
;   Spur   Unterprogramm   Hauptprogramm   druckt vom Wort 0123 4567 012
;   0100   triadendruck    02000           alle 11 Triaden            01234567012
;   0200   adressdruck     02100           die mittleren 4 Triaden    4567
;   0300   befehlsdruck    02200           die unteren 7 Triaden      4567012
;
; Test: #STARTE 2000, #STARTE 2100 oder #STARTE 2200 (Zelle 0000 springt nach 2000).
;
; Verfahren: R1 wird je Ziffer um 3 Bit gedreht (217, 006, 006), mit 200 auf die unterste Triade
; ausgeblendet und mit dem GX-Befehl 520 auf der Einsen-Spur 7700 ff. als Index in die dto-Zellen
; (Ausgabebefehle der Ziffern 0 bis 7) umgesetzt. Der Zaehler td_z (n-1 Einsen, je Ziffer um 1 Bit
; nach links) bestimmt die Anzahl der Ziffern. Adress- und Befehlsdruck drehen vorher R1 einmal um
; 12 Bit (616 ueber die Nullspur 7640 ff.), damit die ersten 4 Triaden nicht gedruckt werden.
; Gedreht wird bei triadendruck und befehlsdruck insgesamt 33 Bit (Wort in 7777 danach unveraendert),
; beim adressdruck 12 + 4*3 = 24 Bit (Wort in 7777 danach um 12 Bit gedreht).

                start
                000     haupt1          ; Zelle 0000: Sprung zum ersten Hauptprogramm

; ---- triadendruck: Spur 0100 ---------------------------------------------------------------
                equ     00100
triadendruck:   240     td_rs   ; Rueckkehrbefehl sichern
                211     t_konst_1
                000     t_spur_speich
t_schleife:     217     adr7777      ; das auszugebende Wort als Uebergabe
                006     t_verschieben
                spa     05
                dto     1
                dto     6
t_zu_gx:        520     adr7721
t_konst_z:      dw      077740000000  ; Zaehler: 10 Einsen = 11 Ziffern
                311     td_z
                170     td_rs
                004     t_zn      ; td_z := td_z um 1 Bit nach links
                spa     014
                dto     4
t_verschieben:  006     t_speichern_r1
                db      1       ; ungenutzt
t_konst_7:      dw      07      ; Maske fuer die unterste Triade
                db      2       ; ungenutzt
                spa     022
                dto     2
                dto     7
t_speichern_r1: 240     adr7777
                200     t_konst_7
                000     t_zu_gx
t_konst_1:      dw      01      ; Konstante
                spa     030
                dto     0
                dto     5
t_spur_speich:  440     adr7724 ; AC auf Spur speichern
                211     t_konst_z
t_zn:           240     td_z
                000     t_schleife
                db      1       ; unbenutzt
                spa     037
                dto     3

; ---- adressdruck: Spur 0200 (Vorlauf auf 0240) ---------------------------------------------
                equ     00200
adressdruck:    240     td_rs   ; Rueckkehrbefehl sichern
                000     a_vorlauf ; 12 Bit drehen, dann Einsen-Spur anlegen (Code auf Spur 00240)
                db      1       ; ungenutzt (haelt die Schleife auf Sektor 03)
a_schleife:     217     adr7777      ; das auszugebende Wort als Uebergabe
                006     a_verschieben
                spa     05
                dto     1
                dto     6
a_zu_gx:        520     adr7721
a_konst_z:      dw      070000000000  ; Zaehler: 3 Einsen = 4 Ziffern
                311     td_z
                170     td_rs
                004     a_zn      ; td_z := td_z um 1 Bit nach links
                spa     014
                dto     4
a_verschieben:  006     a_speichern_r1
                db      1       ; ungenutzt
a_konst_7:      dw      07      ; Maske fuer die unterste Triade
                db      2       ; ungenutzt
                spa     022
                dto     2
                dto     7
a_speichern_r1: 240     adr7777
                200     a_konst_7
                000     a_zu_gx
a_konst_1:      dw      01      ; Konstante
                spa     030
                dto     0
                dto     5
a_spur_speich:  440     adr7724 ; AC auf Spur speichern
                211     a_konst_z
a_zn:           240     td_z
                000     a_schleife
                db      1       ; unbenutzt
                spa     037
                dto     3

                equ     00240
a_vorlauf:      441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7777         ; AC := Wort
                616     nz_12           ; 12 Bit zyklisch links: die zu druckenden Ziffern stehen oben
                240     adr7777         ; Wort zurueck in die Transportzelle
                211     a_konst_1       ; AC := 1
                000     a_spur_speich

; ---- befehlsdruck: Spur 0300 (Vorlauf auf 0340) --------------------------------------------
                equ     00300
befehlsdruck:   240     td_rs   ; Rueckkehrbefehl sichern
                000     b_vorlauf ; 12 Bit drehen, dann Einsen-Spur anlegen (Code auf Spur 00340)
                db      1       ; ungenutzt (haelt die Schleife auf Sektor 03)
b_schleife:     217     adr7777      ; das auszugebende Wort als Uebergabe
                006     b_verschieben
                spa     05
                dto     1
                dto     6
b_zu_gx:        520     adr7721
b_konst_z:      dw      077000000000  ; Zaehler: 6 Einsen = 7 Ziffern
                311     td_z
                170     td_rs
                004     b_zn      ; td_z := td_z um 1 Bit nach links
                spa     014
                dto     4
b_verschieben:  006     b_speichern_r1
                db      1       ; ungenutzt
b_konst_7:      dw      07      ; Maske fuer die unterste Triade
                db      2       ; ungenutzt
                spa     022
                dto     2
                dto     7
b_speichern_r1: 240     adr7777
                200     b_konst_7
                000     b_zu_gx
b_konst_1:      dw      01      ; Konstante
                spa     030
                dto     0
                dto     5
b_spur_speich:  440     adr7724 ; AC auf Spur speichern
                211     b_konst_z
b_zn:           240     td_z
                000     b_schleife
                db      1       ; unbenutzt
                spa     037
                dto     3

                equ     00340
b_vorlauf:      441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7777         ; AC := Wort
                616     nz_12           ; 12 Bit zyklisch links: die zu druckenden Ziffern stehen oben
                240     adr7777         ; Wort zurueck in die Transportzelle
                211     b_konst_1       ; AC := 1
                000     b_spur_speich

; ---- gemeinsame Adressen und Arbeitszellen -------------------------------------------------
adr7721:        abs     07721
adr7724:        abs     07724
adr7777:        abs     07777
td_rs:          abs     07741           ; Rueckkehrbefehl
td_z:           abs     07720           ; Zaehler
nullspur:       abs     07640           ; Nullspur (441: alle 32 Zellen := 0)
nz_12:          abs     07644           ; 12 Nullzellen bis Position 37 (616: 12 Linksverschiebungen)

; ---- Hauptprogramme -----------------------------------------------------------------------
haupt1:         equ     02000
                030     04500           ; Kanal K2 (Schreibwerk) anwaehlen
                dz      $inkb           ; Kleinbuchstabenlage (Ziffern)
                211     beisp_1
                240     adr7777
                025     triadendruck
                020     0000            ; Stopp
beisp_1:        dw      01234567012     ; alle 11 Triaden: 01234567012

haupt2:         equ     02100
                030     04500           ; Kanal K2 (Schreibwerk) anwaehlen
                dz      $inkb           ; Kleinbuchstabenlage (Ziffern)
                211     beisp_2
                240     adr7777
                025     adressdruck
                020     0000            ; Stopp
beisp_2:        dw      01234567012     ; mittlere 4 Triaden: 4567

haupt3:         equ     02200
                030     04500           ; Kanal K2 (Schreibwerk) anwaehlen
                dz      $inkb           ; Kleinbuchstabenlage (Ziffern)
                211     beisp_3
                240     adr7777
                025     befehlsdruck
                020     0000            ; Stopp
beisp_3:        dw      01234567012     ; untere 7 Triaden: 4567012
