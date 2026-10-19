; C8205 BIS - Druckprogramme fuer Oktalziffern (8-Kanal-Ausfuehrung, R 300-Code)
;
; Eine gemeinsame Druckschleife (Spur 0100) und drei Einstiege mit eigener Vorbereitung (Spur 0200 ff.).
; Das auszugebende Wort steht in der Transportzelle 7777; der Aufrufer waehlt vorher den Ausgabekanal an
; (030 04500) und schaltet auf Ziffernlage (dz $inkb). Aufruf mit 025 <einstieg>, Rueckkehr ueber td_rs.
;
;   Einstieg       Zelle  Hauptprogramm  Ziffern  druckt vom Wort 0123 4567 012
;   triadendruck   0200   02000          11       alle Triaden                0123 4567 012
;   adressdruck    0220   02100           4       die mittleren 4 Triaden     4567
;   befehlsdruck   0240   02200           7       die unteren 7 Triaden       4567 012
;
; Nach jeder 4. Ziffer wird ein Leerzeichen gedruckt, aber nur, wenn noch eine Ziffer folgt.
;
; Test: #STARTE 2000, #STARTE 2100 oder #STARTE 2200 (Zelle 0000 springt nach 2000).
;
; Fallunterscheidung (Vorbereitung im jeweiligen Einstieg):
;   1. Rueckkehrbefehl nach td_rs sichern.
;   2. adress-/befehlsdruck: Nullspur loeschen (441) und R1 um 12 Bit nach links drehen (616 ueber
;      die Nullspur), damit die ersten 4 Triaden nicht gedruckt werden.
;   3. Einsen-Spur 7700 ff. anlegen (AC := 1, 440 speichert auf alle 32 Zellen der Spur).
;   4. Zaehler td_z setzen (n-1 Einsen fuer n Ziffern). Das muss nach 440 geschehen, weil td_z (7720)
;      auf der Einsen-Spur liegt. Dann Sprung in die gemeinsame Schleife.
; Die Schleife dreht R1 je Ziffer um 3 Bit (217, 006, 006), blendet mit 200 die unterste Triade aus
; und setzt sie mit dem GX-Befehl 520 auf der Einsen-Spur in die Auswahl einer dto-Zelle um (Ziffer 0
; bis 7). Sie bricht ab, wenn der Zaehler td_z, der je Ziffer um 1 Bit nach links geschoben wird, 0 ist.
; Gruppenzaehler td_g (7717): 3 Einsen, wird je Ziffer um 1 Bit nach links geschoben. Nach der Rueckkehrpruefung
; (td_z = 0: letzte Ziffer, kein Leerzeichen) wird td_g geprueft: td_g = 0 heisst, die 4. Ziffer einer Gruppe ist
; gedruckt, dann folgt ein Leerzeichen (dz $zr) und td_g wird neu mit 3 Einsen belegt.
; Gedreht wird bei triadendruck und befehlsdruck insgesamt 33 Bit (Wort in 7777 danach unveraendert),
; beim adressdruck 12 + 4*3 = 24 Bit (Wort in 7777 danach um 12 Bit gedreht).

                start
                000     haupt1          ; Zelle 0000: Sprung zum ersten Hauptprogramm

; ---- gemeinsame Druckschleife: Spur 0100 ---------------------------------------------------
; Die dto-Zellen (Ausgabebefehl der Ziffer d) liegen auf den Sektoren, die der GX-Befehl 520
; ansteuert (Sektoren 30 05 22 37 14 31 06 23 fuer die Ziffern 0 bis 7).
                equ100  *
gruppe:         311     td_g            ; AC := Gruppenzaehler; Vergleicher 3, falls td_g = 0
                170     raum            ; td_g = 0: 4 Ziffern gedruckt, Leerzeichen ausgeben
                004     zg              ; AC := td_g um 1 Bit nach links
schleife:       217     adr7777      ; das auszugebende Wort als Uebergabe
                006     verschieben
                spa     05
                dto     1
                dto     6
zu_gx:          520     adr7721
konst_t:        dw      077740000000  ; Zaehler triadendruck: 10 Einsen = 11 Ziffern (liegt hier, die Zelle wird uebersprungen)
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
zg:             240     td_g            ; td_g := td_g um 1 Bit nach links
                000     schleife        ; naechste Ziffer
zn:             240     td_z
                000     gruppe          ; Gruppenzaehler pruefen
                db      1       ; unbenutzt
                spa     037
                dto     3

; ---- Einstiege mit Vorbereitung: Spur 0200 ff. ----------------------------------------------
; triadendruck: alle 11 Triaden
                equ     0200
triadendruck:   240     td_rs           ; Rueckkehrbefehl sichern
                211     konst_1
                440     adr7724         ; Einsen-Spur anlegen
                211     konst_t         ; Zaehler: 11 Ziffern
                240     td_z
                211     konst_4         ; Gruppenzaehler: 4 Ziffern
                240     td_g
                000     schleife

; adressdruck: mittlere 4 Triaden (12 Bit drehen, 4 Ziffern)
                equ     0220
adressdruck:    240     td_rs           ; Rueckkehrbefehl sichern
                441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7777         ; AC := Wort
                616     nz_12           ; 12 Bit zyklisch links
                240     adr7777         ; Wort zurueck in die Transportzelle
                211     konst_1
                440     adr7724         ; Einsen-Spur anlegen
                211     konst_4         ; Zaehler: 4 Ziffern
                240     td_z
                240     td_g            ; Gruppenzaehler (wird bei 4 Ziffern nie 0)
                000     schleife
konst_4:        dw      070000000000    ; 3 Einsen = 4 Ziffern (Zaehler und Gruppenzaehler)

; befehlsdruck: untere 7 Triaden (12 Bit drehen, 7 Ziffern)
                equ     0240
befehlsdruck:   240     td_rs           ; Rueckkehrbefehl sichern
                441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7777         ; AC := Wort
                616     nz_12           ; 12 Bit zyklisch links
                240     adr7777         ; Wort zurueck in die Transportzelle
                211     konst_1
                440     adr7724         ; Einsen-Spur anlegen
                211     konst_b         ; Zaehler: 7 Ziffern
                240     td_z
                211     konst_4         ; Gruppenzaehler: 4 Ziffern
                240     td_g
                000     schleife
konst_b:        dw      077000000000    ; Zaehler: 6 Einsen = 7 Ziffern

; Leerzeichen nach 4 Ziffern (Sprung aus der Druckschleife, Zelle 0101)
                equ     0260
raum:           dz      $zr             ; Leerzeichen ausgeben
                211     konst_4         ; Gruppenzaehler neu: 4 Ziffern
                240     td_g
                000     schleife

; ---- gemeinsame Adressen und Arbeitszellen -------------------------------------------------
adr7721:        abs     07721
adr7724:        abs     07724
adr7777:        abs     07777
td_rs:          abs     07741           ; Rueckkehrbefehl
td_z:           abs     07720           ; Zaehler
td_g:           abs     07717           ; Gruppenzaehler (kein Sektor des GX-Befehls, vgl. Sektoren 21 36 13 30 05 22 37 14 31 06 23)
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
beisp_1:        dw      01234567012     ; alle 11 Triaden: 0123 4567 012

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
beisp_3:        dw      01234567012     ; untere 7 Triaden: 4567 012
