; C8205 BIS - Minimalprogramm v7 (R 300-Code, absolut adressiert ab 0040), Bereich 0040 bis 0377
; #DOK-0001
; v7 = v6 mit versetzten Arbeitszellen kz_a, kz_d, kz_z (Takt-Optimierung der Ziffernschleife, 08.11.2026); Code, Anschluss- und Ansprungzellen unveraendert.
; #SPEI-0001 0000-0000
; #PROT STUFE=2
; #TROMMEL=KEEP
;
; Grundlage: Druckprogramme aus pj2-bis_minimalprogramm_v3.asm (Ansprungzellen 0200 Triadendruck, 0220 Adressdruck,
; 0240 Befehlsdruck unveraendert; das Stueck 'raum' (Leerzeichen) liegt nicht mehr fest auf 0260).
; Neu: Hauptprogramm (BIS-Anfang), Eingabe eines Wortes mit Kennzeichen (0262), Adresseneingabe (0316).
; Eingabe eines Programmstueckes (Ansprungzelle 0263): gleicher Einstieg kz_anf wie die Kennzeicheneingabe; sie enthaelt keine
; Kanalanwahl (Kanal und Hauptleitadresse stellt das Hauptprogramm bzw. das Band ein: H G K1 R, Adresse und Daten vom Lochstreifen).
; Woerter mit K1 = 0 werden ab Hauptleitadresse + Relativadresse fortlaufend gespeichert bis zum Schlusszeichen : oder BM.
; Leitbefehl LB (240 mit Adresse) wird bei jedem Einstieg und nach jeder Aenderung neu gebaut: LB := LA+1 + RA + 0240 (lb_neu).
;
; Zelle 0000: unbedingter Sprung zur Kennzeicheneingabe (eingabewortkz, 0262). Zelle 0001: unbedingter Sprung zum Druck von BZ und AC
; (druck, siehe unten). Zelle 0000 und 0001 gehoeren eigentlich dem KEP (0001 ist dort unbelegt); beim Laden des Minimalprogramms
; werden beide ueberschrieben. Es gibt kein Hauptprogramm: das BIS besteht nur aus den
; Unterprogrammen (Eingabe eines Wortes mit Kennzeichen 0262, Eingabe eines Programmstueckes 0263, Adresseneingabe 0316, Triadendruck 0200,
; Adressdruck 0220, Befehlsdruck 0240) und dem Druck von BZ und AC. Kanal und Aufruf stellt der Aufrufer ein (z. B. H G K1 R).
; Jeder Einstieg 0262/0263 loescht die Nullspur und die Leitadresse 0 (LA := 0), die Adresseneingabe 0316 loescht die Nullspur.
; Hauptleitadresse und Relativadresse haben keinen Anfangswert: sie werden mit '2 1 aaaa .' bzw. '2 .' (RA := 0) gesetzt.
; Die Tasten B und D der Bedienpulttastatur haben keine Wirkung (die Tabellenzellen 0335 und 0355 sind frei).
;
; Zeichen der Bedienpulttastatur: + ZR / : BM 0 1 2 3 4 5 6 7 8 9 B D. Die Zeichen WR, GB, KB und ZV gibt es auf der
; Bedienpulttastatur nicht (sie kommen nur von Lochstreifen bzw. Schreibwerk); deshalb sind sie im BIS-Minimalprogramm
; nicht enthalten. Das Programm prueft nicht, ob andere Zeichen eingegeben werden. '+' ist nicht definiert und wirkt wie die Ziffer 0.
;
; Eingabetabelle kz_tab: Spur 0300 und 0340, 64 Zellen (Offset = Eingabeadresse des Zeichens; die Zellen werden ODER-verknuepft
; angesprochen). Ziffernzellen enthalten den Wert der Ziffer. Zeichen mit Sprung-Umstellung (ZR : . B D BM) fuehren ihre Tabellenzelle als
; Befehl aus. '/' hat keine Sprung-Umstellung; seine Zelle enthaelt 017 (K1 AND 017 = 15). Zwischen den benutzten Tabellenzellen liegt
; weiterer Code (nur Zeichen, die nicht eingegeben werden, treffen diese Zellen).
;
; Wirkung der Kennzeichen (K1 K2, dann Ziffern t10 ... t0, Abschluss mit Punkt (nach der letzten Ziffer, also auch nach 11 Ziffern, muss der Punkt folgen; weitere Ziffern werden ignoriert)):
;   K1 = 0  Wort speichern: K2 = 0 unveraendert, K2 = 1 .. 9: x-te Leitadresse zu t10 ... t3 addieren; Speicherung mit dem Leitbefehl,
;           danach Relativadresse RA + 1000 und Leitbefehl neu (Hauptleitadresse + RA).
;   K1 = 1  Befehl: wie K1 = 0 modifiziert, aber nicht gespeichert, sondern auf Arbeitszelle XW sofort ausgefuehrt; danach Stopp
;           (Zelle XW + 1); Fortsetzung mit R: neues Kennzeichen. K2 = 0 unveraendert.
;   K1 = 2  Adresse (bis 8 Oktalziffern mit Punkt, Adresseneingabe): K2 = 1 .. 9 auf die x-te Leitadresse speichern
;           (K2 = 1: Hauptleitadresse, dabei RA := 0), K2 = 0: Relativadresse RA := Adresse (Speicherung ab Hauptleitadresse + RA).
;   K1 = ZR AC loeschen, neues K1.   K1 = /  bedingter Stopp (Schalter BS), danach neues K1.   K1 = : oder BM  Rueckkehr zum Aufrufer.
;   Andere K1 (3 bis 9, +): ohne Wirkung, neues K1.
;
; Verschiebungen: Der Wiederholungsbefehl 616 ueber die Nullspur 7640 (alle Zellen 0) verschiebt den AC zyklisch um n Bit nach links;
; n haengt vom Startsektor der Adresse ab (Sektor + 13 je Zelle, Ende bei Sektor 23): Sektor 04: 12 Bit (nz_12), Sektor 31: 3 Bit (nz_3),
; Sektor 13: 9 Bit (nz_9). Die Nullspur wird im Hauptprogramm geloescht (441) und von den Druckprogrammen ebenfalls geloescht.
; Die x-te Leitadresse wird mit dem R-Lesebefehl 251 gelesen (Adresse im AC, Adresse 7610 + x, 7610 ist immer 0).
;
; Arbeitszellen: Spur 7600: LB (Leitbefehl) 7600, XW 7602 (+1, +2), RA (Relativadresse) siehe unten (7742), x-te Leitadresse 7610 + x, Kennzeicheneingabe 7630 ... 7634 (kz_rs, kz_k1, kz_k2, kz_k2s, kz_d);
; Lage der Ziffernschleife (Takt-Optimierung 08.11.2026: 256 statt 352 Takte je Ziffer): kz_z 7607 (Sektor 007), kz_a 7763 (Sektor 023), kz_d 7634 (Sektor 034).
; Spur 7740: Rueckkehr der Adresseneingabe 7740, Relativadresse RA 7742. (7700 bis 7737 loescht der Druck, 7640 bis 7677 ist die Nullspur.)

LB:             abs     07600           ; Leitbefehl (240 mit Adresse), Folgezelle LB1 enthaelt den Ruecksprung
LB1:            abs     07601
XW:             abs     07602           ; Arbeitszelle fuer sofort auszufuehrende Befehle; XW1 Stopp, XW2 Sprung zurueck
XW1:            abs     07603
XW2:            abs     07604
RA:             abs     07742           ; Relativadresse (Wert = Adresse * 01000), Anfangswert 0, nach jedem gespeicherten Wort + 01000
LA:             abs     07610           ; x-te Leitadresse auf LA + x (x = 1 .. 9), Wert = Adresse * 01000; LA selbst ist 0
kz_rs:          abs     07630           ; Ruecksprungbefehl zum Aufrufer
kz_k1:          abs     07631
kz_k2:          abs     07632
kz_k2s:         abs     07633           ; Wert der K2-ten Leitadresse
kz_a:           abs     07763           ; akkumulierte Zahl (Sektor 023; Lage nach Takt-Optimierung der Ziffernschleife, frueher 7634)
kz_d:           abs     07634           ; letzte Ziffer (Sektor 034; frueher 7635)
kz_z:           abs     07607           ; Zaehler (Einsen, je Ziffer um 1 Bit nach links) (Sektor 007; frueher 7636)
ae_rs:          abs     07740           ; Ruecksprungbefehl der Adresseneingabe
dr_rs:          abs     07743           ; Druck von BZ und AC: Fortsetzungsbefehl 000 b (wird am Ende ausgefuehrt)
dr_ac:          abs     07744           ; Druck von BZ und AC: gesicherter AC des unterbrochenen Programms (7777 wird vom Druck benutzt)

; Absolute Adressen, kein Basisanteil: Leitadresse 00 (Assemblerdokumentation 3.3.12)
;#; LEITADRESSE 00
                start
                equ     0000
                000     eingabewortkz   ; Zelle 0000: Sprung zur Eingabe eines Wortes mit Kennzeichen (Einstieg 0262)
                equ     0001
                000     druck           ; Zelle 0001: Sprung zum Druck von BZ und AC

; ---- Ansprungzellen ---------------------------------------------------------------------------------
                equ     0262
eingabewortkz:  000     kz_anf          ; Eingabe eines Wortes mit Kennzeichen
eingabeprogst:  000     kz_anf          ; Eingabe eines Programmstueckes (Regie bei der Kennzeicheneingabe)
                equ     0316
adresseneingabe: 000    ae_anf          ; Adresseneingabe (Offset 016 gehoert keinem zugelassenen Zeichen)

; ---- Eingabetabelle kz_tab (Spur 0300 und 0340) ----------------------------------------------------
                equ     0300
kz_tab:         dw      0               ; Ziffer 0
tb_1:           dw      01
tb_2:           dw      02
                dw      03
                dw      04
                dw      05
                dw      06
tb_7:           dw      07
                dw      010             ; Ziffer 8
                dw      011             ; Ziffer 9
tb_zr:          000     kz_neu          ; ZR (012): neues Kennzeichen
                equ     0315
                000     kz_rs           ; ':' (015): Schlusszeichen, Rueckkehr zum Aufrufer
                equ     0320
                dw      0               ; '+' (020): nicht definiert, wirkt wie Ziffer 0
                equ     0333
                000     pt_end          ; '.' (033)
                equ     0361
tb_sl:          dw      017             ; '/' (061): keine Sprung-Umstellung, K1 AND 017 = 15
                equ     0372
                000     kz_rs           ; BM (072): Schlusszeichen, Rueckkehr zum Aufrufer

; ---- Adressen und Arbeitszellen des Druckteils -------------------------------------------------
adr7721:        abs     07721
adr7724:        abs     07724
adr7773:        abs     07773           ; R1: Uebergabezelle der Druckprogramme (BIS-2.2.10), wird nicht veraendert
adr7777:        abs     07777           ; interne Arbeitszelle des Drucks (Wort wird hier verschoben)
td_rs:          abs     07741           ; Rueckkehrbefehl
td_z:           abs     07760           ; Zaehler (Sektor 20 wie bisher, aber auf Spur 7740: die Einsen-Spur 7700-7737 (440 adr7724) wuerde ihn ueberschreiben,
                                        ; weil er vor dem Anlegen der Einsen gesetzt wird)
td_g:           abs     07717           ; Gruppenzaehler (kein Sektor des GX-Befehls)
nullspur:       abs     07640           ; Nullspur (441: alle 32 Zellen := 0)
nz_12:          abs     07644           ; 616: 12 Linksverschiebungen (Sektor 04)
nz_3:           abs     07671           ; 616:  3 Linksverschiebungen (Sektor 31)
nz_9:           abs     07653           ; 616:  9 Linksverschiebungen (Sektor 13)

; ---- gemeinsame Druckschleife: Spur 0100 ---------------------------------------------------
; Die dto-Zellen (Ausgabebefehl der Ziffer d) liegen auf den Sektoren, die der GX-Befehl 520
; ansteuert (Sektoren 30 05 22 37 14 31 06 23 fuer die Ziffern 0 bis 7).
                equ     0100
gruppe:         311     td_g            ; AC := Gruppenzaehler; Vergleicher 3, falls td_g = 0
                170     raum            ; td_g = 0: 4 Ziffern gedruckt, Leerzeichen ausgeben
                004     zg              ; AC := td_g um 1 Bit nach links
schleife:       217     adr7777         ; das auszugebende Wort als Uebergabe
                006     verschieben
                spa     05
                dto     1
                dto     6
zu_gx:          520     adr7721
konst_t:        dw      077740000000    ; Zaehler triadendruck: 10 Einsen = 11 Ziffern
                311     td_z
                170     td_rs
                004     zn              ; td_z := td_z um 1 Bit nach links
                spa     014
                dto     4
verschieben:    006     speichern_r1
                equ     0117            ; (Zelle 0116 gehoert c_inc, keine Doppelbelegung)
konst_4:        dw      070000000000    ; 3 Einsen = 4 Ziffern (Zaehler und Gruppenzaehler)
                equ     0122            ; (Zelle 0120 gehoert kz_sl, keine Doppelbelegung)
                spa     022
                dto     2
                dto     7
speichern_r1:   240     adr7777
                200     tb_7
                000     zu_gx
konst_b:        dw      077000000000    ; 6 Einsen = 7 Ziffern (Befehlsdruck)
                spa     030
                dto     0
                dto     5
zg:             240     td_g            ; td_g := td_g um 1 Bit nach links
                000     schleife        ; naechste Ziffer
zn:             240     td_z
                000     gruppe          ; Gruppenzaehler pruefen
                equ     0137            ; (Zelle 0136 gehoert c_stop, keine Doppelbelegung)
                spa     037
                dto     3

; ---- Einstiege mit Vorbereitung ----------------------------------------------------------------
; Adressdruck und Befehlsdruck sind Sonderfaelle des Triadendrucks (Wort 12 Bit links gedreht, dann nur 4 bzw. 7 Ziffern), der Adressdruck
; wiederum ein Sonderfall des Befehlsdrucks (nur der Zaehler td_z ist anders). Alle drei uebernehmen das Wort aus R1 (7773) und ueberlassen
; das Drucken der gemeinsamen Schleife (schleife, Spur 0100).
; triadendruck: alle 11 Triaden
                equ     0200
triadendruck:   240     td_rs           ; Rueckkehrbefehl sichern
                211     konst_t         ; Zaehler: 11 Ziffern
                240     td_z
                211     adr7773         ; AC := Wort aus R1 (7773), R1 bleibt unveraendert
                240     adr7777         ; Arbeitskopie, hier wird weiter verschoben
                000     td_gem          ; weiter wie beim Befehlsdruck (ohne Drehung)

; adressdruck: mittlere 4 Triaden (12 Bit drehen, 4 Ziffern)
                equ     0220
adressdruck:    240     td_rs           ; Rueckkehrbefehl sichern
                211     konst_4         ; Zaehler: 4 Ziffern
                000     td_dreh         ; weiter wie beim Befehlsdruck

; befehlsdruck: untere 7 Triaden (12 Bit drehen, 7 Ziffern)
                equ     0240
befehlsdruck:   240     td_rs           ; Rueckkehrbefehl sichern
                211     konst_b         ; Zaehler: 7 Ziffern
td_dreh:        240     td_z            ; Zaehler sichern (441 loescht den AC)
                441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     adr7773         ; AC := Wort aus R1 (7773), R1 bleibt unveraendert
                616     nz_12           ; 12 Bit zyklisch links
                240     adr7777         ; Wort in die Transportzelle
td_gem:         211     tb_1
                440     adr7724         ; Einsen-Spur anlegen
                211     konst_4         ; Gruppenzaehler: 4 Ziffern
                240     td_g
                000     schleife

; ---- '2 .' (Punkt statt K2) = 20 00000000000: Adresse 0 mit K2 = 0, also Relativadresse RA := 0 -------------------
; Der Punkt anstelle von K2 springt ueber pt_end (K1 = 2) nach ae_end und von dort ueber ae_rs. Diese Zelle setzt sonst nur ae_anf; hier
; wird sie vor dem Lesen von K2 auf c_a2n (Sprung nach kz_ra0: RA := 0, Leitbefehl neu) gestellt. Wird statt K2 eine Ziffer gelesen,
; ruft kz_a2 die Adresseneingabe auf, und ae_anf setzt ae_rs neu.
                equ     0174
k2_vor:         211     c_a2n           ; Rueckkehrbefehl fuer den Punkt statt K2
                240     ae_rs
                011     kz_tab          ; K2 lesen (Ziffer: weiter bei kz_a2c; Punkt: ae_end -> ae_rs = c_a2n)
                000     kz_a2c
                equ     0260
c_a2n:          000     kz_ra0          ; Befehl fuer ae_rs: RA := 0

; ---- Code der Eingabeprogramme (vom Platzierungsskript auf freie Zellen verteilt) ------------------
                equ     0051
kz_k2r:         011     kz_tab          ; K2 lesen
                200     tb_sl
                240     kz_k2
                616     nz_9            ; K2 * 01000 (9 Bit nach links)
                210     c_la            ; Adresse der K2-ten Leitadresse (LA+0 ist 0)
                251     0               ; AC := Inhalt dieser Zelle (R-Lesebefehl)
                240     kz_k2s
                equ     0060
kz_dig:         211     konst_t           ; Wort: 11 Ziffern
                240     kz_z
                equ     0062
kz_i:           211     kz_tab          ; Zahl := 0
                240     kz_a
                equ     0064
kz_dl:          011     kz_tab          ; Ziffer lesen; Punkt: Sprung ueber die Tabellenzelle nach pt_end
                240     kz_d
                211     kz_a
                616     nz_3            ; mal 8
                210     kz_d
                240     kz_a
                311     kz_z            ; Zaehler = 0 ?
                170     pt_wait         ; ja: letzte Ziffer gelesen, auf den Punkt warten (weitere Ziffern werden ignoriert)
                004     kz_zn
kz_zn:          240     kz_z
                000     kz_dl
                equ     0077
c_lb0:          dw      0240          ; Anfangswert des Leitbefehls
                equ     0116
c_inc:          dw      01000         ; Leitbefehl + 1
                equ     0120
kz_sl:          060     0               ; / : bedingter Stopp (Schalter BS)
                000     kz_neu
                equ     0136
c_stop:         dw      020           ; Stoppbefehl
                equ     0140
raum:           dz      $zr             ; Leerzeichen ausgeben
                211     konst_4         ; Gruppenzaehler neu: 4 Ziffern
                240     td_g
                000     schleife
                equ     0210
kz_exec:        211     c_stop
                240     XW1             ; Stopp hinter dem Befehl
                211     tb_zr
                240     XW2             ; danach (R): neues Kennzeichen
                211     kz_a
                240     XW
                211     kz_tab          ; AC := 0
                000     XW
                equ     0366
pt_end:         211     kz_k1           ; Ende der Ziffern (Punkt, auch nach der letzten Ziffer)
                330     tb_2
                170     ae_end          ; K1 = 2: Adresse
                000     kz_wend
                equ     0265
kz_neu:         011     kz_tab          ; K1 lesen (ZR u.a.: Sprung ueber die Tabellenzelle)
                200     tb_sl           ; AND 017
                240     kz_k1
                330     tb_1
                140     kz_k2i          ; K1 = 0 oder 1 (vorher Wort und Leitadresse loeschen)
                330     tb_2
                170     kz_a2           ; K1 = 2
                330     tb_sl
                170     kz_sl           ; K1 = /
                000     kz_neu          ; sonst ohne Wirkung
                equ     0277
dr_drei:        dw      03000           ; Druck BZ und AC: 3 Adresseinheiten
                equ     0313
c_jg:           000     kz_gesp         ; Sprung nach kz_gesp
                equ     0317
c_az:           dw      077400000000  ; 7 Einsen = 8 Ziffern
                equ     0321
kz_wend:        211     kz_a
                210     kz_k2s          ; plus Leitadresse (K2 = 0: plus 0)
                240     kz_a
                211     kz_k1
                330     tb_1
                170     kz_exec         ; K1 = 1: Befehl ausfuehren
                equ     0327
kz_sp:          211     c_jg            ; K1 = 0: ueber den Leitbefehl speichern
                240     LB1
                211     kz_a
                000     LB
                equ     0334
c_la:           dw      07610000      ; Adresse LA (Leitadresse 0), in die Adressstelle geschoben
                equ     0336
kz_a2:          000     k2_vor          ; K1 = 2: K2 lesen (Vorbereitung fuer '2 .', siehe k2_vor)
kz_a2c:         200     tb_sl
                240     kz_k2
                025     adresseneingabe ; Adresse nach AC
                240     kz_a
                211     kz_k2
                330     kz_tab          ; K2 = 0 ?
                170     kz_rel
                equ     0346
                000     kz_ck           ; K2 = 1 (Hauptleitadresse) gesondert pruefen (AC = K2)
                equ     0347
kz_a2b:         ; K2 * 01000 steht im AC (616 in kz_ck)
                210     c_xs            ; Befehl 240 LA+K2
                240     XW
                211     tb_zr           ; danach neues Kennzeichen
                240     XW1
                211     kz_a
                000     XW
                equ     0356
ae_end:         211     kz_a            ; Adresse in t3 ... t10
                616     nz_9
                000     ae_rs
                equ     0362
kz_rel:         211     kz_a            ; K2 = 0: Relativadresse := eingegebene Adresse
                240     RA
                000     lb_neu          ; Leitbefehl neu bauen
                equ     0044
ae_anf:         240     ae_rs
                441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                211     c_az            ; 8 Ziffern
                240     kz_z
                000     ae_k            ; K1 := 2 setzen (auch bei Aufruf aus einem Programm)
                equ     0373
kz_gesp:        211     RA              ; Relativadresse + 1000 (naechste Zelle)
                210     c_inc
                240     RA
                000     lb_neu          ; Leitbefehl neu bauen
                equ     0040
kz_anf:         240     kz_rs           ; Rueckkehrbefehl zum Aufrufer sichern (Eingabe Wort mit Kennzeichen und Programmstueck)
                441     nullspur        ; Nullspur := 0 (loescht auch den AC)
                240     LA              ; Leitadresse 0 := 0
                000     lb_neu          ; Leitbefehl bauen
                equ     0144
lb_neu:         211     LA+1            ; Hauptleitadresse
                210     RA              ; plus Relativadresse
                210     c_lb0           ; plus 240 = Abspeicherbefehl (Leitbefehl)
                240     LB
                000     kz_neu          ; K1 lesen
kz_ck:          330     tb_1            ; AC = K2: K2 = 1 ?
                170     kz_hla          ; ja: neue Hauptleitadresse
                616     nz_9            ; K2 * 01000 (9 Bit nach links)
                000     kz_a2b          ; Leitadresse K2 speichern
kz_hla:         211     kz_a            ; K2 = 1: eingegebene Adresse
                240     LA+1            ; ist die neue Hauptleitadresse
kz_ra0:         211     kz_tab          ; AC := 0 (auch Einsprung bei '2 .': RA := 0)
                240     RA              ; Relativadresse := 0
                000     lb_neu          ; Leitbefehl neu bauen
kz_k2i:         211     kz_tab          ; AC := 0: bei '0 .' oder '1 .' (Punkt statt K2) ist das Wort 0
                240     kz_a
                240     kz_k2s
                000     kz_k2r          ; K2 lesen
pt_wait:        011     kz_tab          ; alle Ziffern gelesen: weitere Ziffern ueberlesen, Punkt beendet (Sprung nach pt_end)
                000     pt_wait
ae_k:           211     tb_2            ; K1 := 2: der Punkt beendet die Adresseneingabe (pt_end -> ae_end)
                240     kz_k1
                000     kz_i
                equ     0377
c_xs:           dw      07610240      ; Befehl 240 LA

; ---- Druck von BZ und AC (Ziel der Zelle 0001; Tastenfolge H G Ue E G M+ E M- R) -----------------------------------
; Ein laufendes Programm wurde unterbrochen (Ueberlauf, Stopp usw.); BZ = b ist der Stand des Befehlszaehlers, also die Adresse
; des als naechsten abzuarbeitenden Befehls. Vorher wurde mit H G Ue E der Akkumulatorinhalt nach Zelle 7777 transportiert
; (Bedienpult 4.2); dabei lief ein Schritt, BZ steht danach auf b+1. Das E unter M (Bedienpult 4.3) liefert im AC den Rueckkehr-
; befehl 0000 aaaa 000 mit aaaa = (b+1) + 2 = b + 3. Ausgegeben werden (Schreibwerk, Kanal K2, mit dem Triadendruck 0200) in einer Zeile,
; durch ein Leerzeichen getrennt, zuerst BZ und dann der AC (ohne Bezeichnungen, dafuer fehlt im Bereich 0040 bis 0377 der Platz):
;     0000 bbbb 000 aaaa aaaa aaa
; BZ ist der um 3 Adresseinheiten verminderte AC, also der Sprungbefehl 0000 bbbb 000. Danach wird der AC zurueckgeholt und dieser
; Sprungbefehl (000 b) ausgefuehrt: das Programm wird mit dem Befehl b und seinem AC fortgesetzt. Ist der Schalter BS eingerastet,
; geht der Rechner vorher in den bedingten Stopp (Loesen von BS setzt fort).
; Zelle 7777 ist die Uebergabezelle des Triadendrucks und wird dabei veraendert; der AC des Programms wird deshalb zuerst in dr_ac
; gesichert. Der Fortsetzungsbefehl liegt in dr_rs. Beide Zellen liegen auf der Spur 7740 (der Druck beschreibt nur 7700 bis 7737).
; Nicht fortsetzbar sind Unterbrechungen im Triadendruck, Adressdruck und Befehlsdruck (td_rs und die Zaehler werden ueberschrieben).
; Die Anwahl des Schreibwerks (030 4500) steht hier, weil der Triadendruck keinen Anwahlbefehl enthaelt.
; Der Code liegt in drei Stuecken (druck ab 0223, dr_c ab 0206, dr_ende ab 0254), die Konstante dr_drei bei 0277.
                equ     0223
druck:          220     dr_drei         ; AC := AC - 3 Adresseinheiten = Befehl 0000 bbbb 000
                240     dr_rs           ; als Fortsetzungsbefehl merken
                240     adr7773         ; und als BZ-Wort in die Uebergabezelle R1 des Triadendrucks
                211     adr7777         ; AC := gerettete AC-Inhalt (Zelle 7777)
                240     dr_ac           ; sichern (7777 wird vom Triadendruck benutzt)
                030     04500           ; Anwahl Kanal K2 (Schreibwerk)
                dz      $wrzl           ; neue Zeile
                dz      $inkb           ; Kleinbuchstabenlage (Ziffern)
                025     triadendruck    ; BZ-Wort drucken
                dz      $zr             ; Zwischenraum
                211     dr_ac
                240     adr7773         ; AC als Uebergabe in R1
                000     dr_c            ; weiter beim zweiten Stueck
                equ     0206
dr_c:           025     triadendruck    ; AC drucken
                000     dr_ende         ; weiter beim dritten Stueck
                equ     0254
dr_ende:        dz      $wrzl           ; Zeilenende
                211     dr_ac           ; AC := gerettete AC-Inhalt: das Programm setzt mit seinem AC fort
                060     0               ; bedingter Stopp (bei eingerastetem BS)
                000     dr_rs           ; Fortsetzung: Zelle dr_rs wird als Befehl 000 b ausgefuehrt

                end
