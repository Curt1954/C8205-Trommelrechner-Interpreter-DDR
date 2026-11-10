
; ---- Unterprogramm zt_anw: Zusatztrommel zt_t (0 bis 3) anwaehlen (Befehl 5k00 030, k = t + 1) ----
zt_anw:         240     zw_r         ; Rueckkehr sichern
                211     zt_t         ; t
                616     nz+035       ; um 15 Bit nach links
                210     k_an         ; plus Befehl 5100 030
                240     zw_x         ; Befehl ablegen
zw_x:           db      1            ; hier steht 5k00 030
                000     zw_r         ; zurueck
; ---- zt_ausf: Befehl zzz0 bbbb 601/661 aus zc_spur, zc_adr, zc_op bilden und ausfuehren ----
zt_ausf:        240     za_r         ; Rueckkehr sichern
                211     zc_spur      ; Spur
                616     nz+016       ; um 26 Bit nach links (zzz0)
                210     zc_adr       ; plus Adresse der HT-Spur
                210     zc_op        ; plus 0601 oder 0661
                240     za_x         ; Befehl ablegen
za_x:           db      1            ; hier steht der ZT-Befehl
                000     za_r         ; zurueck
zt_lies_ltr:    240     zl_r         ; Rueckkehr sichern
                211     da_ltr       ; Adresse LTR
                240     zc_adr       ; merken
                211     k_661        ; Eingabe ZT -> HT
                240     zc_op        ; merken
                025     zt_ausf      ; ausfuehren
                000     zl_r         ; zurueck
zt_schr_ltr:    240     zs_r         ; Rueckkehr sichern
                211     da_ltr       ; Adresse LTR
                240     zc_adr       ; merken
                211     k_601        ; Ausgabe HT -> ZT
                240     zc_op        ; merken
                025     zt_ausf      ; ausfuehren
                000     zs_r         ; zurueck
zt_schr_puf:    240     zp_r         ; Rueckkehr sichern
                211     da_puf       ; Adresse PUF
                240     zc_adr       ; merken
                211     k_601        ; Ausgabe HT -> ZT
                240     zc_op        ; merken
                025     zt_ausf      ; ausfuehren
                000     zp_r         ; zurueck

; ---- sp_such: su_n aufeinanderfolgende freie Spuren in der Belegungsliste LTR suchen; Ergebnis su_res (erste Spur, 0 = keine) ----
sp_such:        240     su_r         ; Rueckkehr sichern
                241     su_lauf      ; Folge := 0
                240     su_s         ; Spur := 0
                240     su_res       ; Ergebnis := 0
                211     ltr+0        ; Wort 0
                240     su_w         ; merken
                025     su_wort      ; 32 Spuren pruefen
                311     su_res       ; gefunden?
                170     su_w1        ; nein: weiter
                000     su_r         ; ja: zurueck
su_w1:          211     ltr+1        ; Wort 1
                240     su_w         ; merken
                025     su_wort      ; pruefen
                311     su_res       ; gefunden?
                170     su_w2        ; nein
                000     su_r         ; ja
su_w2:          211     ltr+2        ; Wort 2
                240     su_w         ; merken
                025     su_wort      ; pruefen
                311     su_res       ; gefunden?
                170     su_w3        ; nein
                000     su_r         ; ja
su_w3:          211     ltr+3        ; Wort 3
                240     su_w         ; merken
                025     su_wort      ; pruefen
                000     su_r         ; zurueck
su_wort:        240     sw_r         ; Rueckkehr sichern
                211     k32          ; 32 Bits
                240     su_zb        ; Zaehler
su_bit:         211     su_w         ; Wort
                040     su_bel       ; z0 = 1: Spur belegt
                211     su_lauf      ; Folge
                210     eins         ; plus 1
                240     su_lauf      ; merken
                220     su_n         ; minus gesuchte Zahl
                330     null         ; gleich 0?
                170     su_fund      ; ja: gefunden
                000     su_next      ; weiter
su_bel:         241     su_lauf      ; Folge := 0
su_next:        215     su_w         ; Wort um 1 Bit nach links
                240     su_w         ; merken
                211     su_s         ; Spur
                210     eins         ; plus 1
                240     su_s         ; merken
                211     su_zb        ; Zaehler
                220     eins         ; minus 1
                240     su_zb        ; merken
                330     null         ; gleich 0?
                170     sw_r         ; ja: Wort fertig, zurueck
                000     su_bit       ; naechstes Bit
su_fund:        211     su_s         ; aktuelle Spur (letzte der Folge)
                220     su_n         ; minus Zahl
                210     eins         ; plus 1 = erste Spur
                240     su_res       ; Ergebnis
                000     sw_r         ; zurueck

; ---- sp_mark: Spuren mk_von bis mk_von + mk_n - 1 in der Belegungsliste LTR als belegt eintragen ----
sp_mark:        240     mk_r         ; Rueckkehr sichern
                211     mk_von       ; von
                210     mk_n         ; plus Anzahl
                240     mk_bis       ; bis (ausschliesslich)
                241     mk_s         ; Spur := 0
                211     ltr+0        ; Wort 0
                240     mk_alt       ; merken
                025     mk_wort      ; umbauen
                211     mk_neu       ; neues Wort
                240     ltr+0        ; zurueck
                211     ltr+1        ; Wort 1
                240     mk_alt       ; merken
                025     mk_wort      ; umbauen
                211     mk_neu       ; neues Wort
                240     ltr+1        ; zurueck
                211     ltr+2        ; Wort 2
                240     mk_alt       ; merken
                025     mk_wort      ; umbauen
                211     mk_neu       ; neues Wort
                240     ltr+2        ; zurueck
                211     ltr+3        ; Wort 3
                240     mk_alt       ; merken
                025     mk_wort      ; umbauen
                211     mk_neu       ; neues Wort
                240     ltr+3        ; zurueck
                000     mk_r         ; zurueck
mk_wort:        240     mw_r         ; Rueckkehr sichern
                241     mk_neu       ; neues Wort := 0
                211     k32          ; 32 Bits
                240     mk_zb        ; Zaehler
mk_bit:         241     mk_b         ; Bit := 0
                211     mk_alt       ; altes Wort
                040     mk_b1        ; z0 = 1: schon belegt
                211     mk_s         ; Spur
                220     mk_von       ; minus von
                040     mk_nb        ; kleiner: nicht im Bereich
                211     mk_s         ; Spur
                220     mk_bis       ; minus bis
                050     mk_nb        ; nicht kleiner: nicht im Bereich
mk_b1:          211     eins         ; Bit := 1
                240     mk_b         ; merken
mk_nb:          215     mk_neu       ; neues Wort um 1 Bit nach links
                210     mk_b         ; plus Bit
                240     mk_neu       ; merken
                215     mk_alt       ; altes Wort um 1 Bit nach links
                240     mk_alt       ; merken
                211     mk_s         ; Spur
                210     eins         ; plus 1
                240     mk_s         ; merken
                211     mk_zb        ; Zaehler
                220     eins         ; minus 1
                240     mk_zb        ; merken
                330     null         ; gleich 0?
                170     mk_we        ; ja: fertig
                000     mk_bit       ; naechstes Bit
mk_we:          215     mk_neu       ; letztes Bit z32 bleibt 0
                240     mk_neu       ; merken
                000     mw_r         ; zurueck

; ---- d_zeile: Zeile von der Tastatur lesen (Ziffern, J, N), Ende mit ZR, Zeilenschaltung oder Punkt ----
; Ergebnis: d_acc (oktale Zahl), d_ziff (Zahl der Ziffern), d_jn (1 = J, 2 = N), d_bad (1 = ungueltiges Zeichen)
d_zeile:        240     d_r          ; Rueckkehr sichern
                241     d_acc        ; Zahl := 0
                240     d_ziff       ; Ziffern := 0
                240     d_jn         ; J/N := 0
                240     d_bad        ; ungueltig := 0
d_lies:         011     tab_k        ; Zeichen lesen: AC := Tabellenwert oder Sprung (d_end, d_lies)
                240     d_v          ; merken
                220     k8           ; minus 8
                040     d_zif        ; kleiner 8: oktale Ziffer
                211     d_v          ; Wert
                330     k_j          ; J?
                170     d_isj        ; ja
                330     k_n          ; N?
                170     d_isn        ; ja
d_ung:          211     eins         ; ungueltig := 1
                240     d_bad        ; merken
                000     d_lies       ; weiter lesen
d_isj:          211     eins         ; J/N := 1
                240     d_jn         ; merken
                000     d_lies       ; weiter
d_isn:          211     zwei         ; J/N := 2
                240     d_jn         ; merken
                000     d_lies       ; weiter
d_zif:          211     d_ziff       ; Ziffern
                210     eins         ; plus 1
                240     d_ziff       ; merken
                220     k5           ; minus 5
                050     d_ung        ; mehr als 4 Ziffern: ungueltig
                211     d_acc        ; Zahl
                616     nz+031       ; mal 8
                210     d_v          ; plus Ziffer
                240     d_acc        ; merken
                000     d_lies       ; weiter
d_end:          000     d_r          ; Ende der Zeile: zurueck

; ---- band_wort: ein Wort der .obj von Leser 1 lesen (K1 K2 Ziffern Punkt) oder das Schlusszeichen / ----
; Ergebnis: bw_ende (1 = Schlusszeichen), bw_k1, bw_k2, bw_wert
band_wort:      240     bw_r         ; Rueckkehr sichern
                241     bw_stufe     ; Stufe 0: K1 erwartet
                240     bw_ende      ; kein Ende
                240     bw_k1        ; K1 := 0
                240     bw_k2        ; K2 := 0
                240     bw_wert      ; Wert := 0
                240     bw_cnt       ; Ziffern := 0
bw_lies:        011     tab_b        ; Zeichen lesen: AC := Tabellenwert oder Sprung (b_pkt, b_skip, b_fehl)
                240     bw_v         ; merken
                311     bw_stufe     ; Stufe 0?
                170     bw_s0        ; ja
                211     bw_stufe     ; Stufe
                330     eins         ; Stufe 1?
                170     bw_s1        ; ja
                211     bw_v         ; Stufe 2: Ziffer 0 bis 7
                220     k8           ; minus 8
                050     b_fehl       ; keine oktale Ziffer
                211     bw_cnt       ; Ziffern
                210     eins         ; plus 1
                240     bw_cnt       ; merken
                220     k12          ; minus 12
                050     b_fehl       ; mehr als 11 Ziffern
                211     bw_wert      ; Wert
                616     nz+031       ; mal 8
                210     bw_v         ; plus Ziffer
                240     bw_wert      ; merken
                000     bw_lies      ; weiter
bw_s0:          211     bw_v         ; Stufe 0: K1 oder Schlusszeichen
                330     k_slash      ; Schlusszeichen?
                170     bw_slash     ; ja
                220     k10          ; minus 10
                050     b_fehl       ; keine Ziffer
                211     bw_v         ; K1
                240     bw_k1        ; merken
                211     eins         ; Stufe := 1
                240     bw_stufe     ; merken
                000     bw_lies      ; weiter
bw_s1:          211     bw_v         ; Stufe 1: K2
                220     k10          ; minus 10
                050     b_fehl       ; keine Ziffer
                211     bw_v         ; K2
                240     bw_k2        ; merken
                211     zwei         ; Stufe := 2
                240     bw_stufe     ; merken
                000     bw_lies      ; weiter
bw_slash:       211     eins         ; Ende := 1
                240     bw_ende      ; merken
                000     bw_r         ; zurueck
b_pkt:          311     bw_stufe     ; Punkt: Stufe 0?
                170     b_fehl       ; ja: Fehler (Punkt ohne K1)
                000     bw_r         ; Wort vollstaendig, zurueck
b_skip:         000     bw_lies      ; Zeichen ueberlesen

; ---- pk_init: Packzaehler fuer eine neue Programmspur ----
pk_init:        240     pi_r         ; Rueckkehr sichern
                211     da_puf       ; Adresse PUF
                240     pk_kwptr     ; Kennungszelle der Gruppe 0
                210     k_adr1       ; plus 1 Zelle
                240     pk_ptr       ; erste Wortzelle
                241     pk_cnt       ; Worte := 0
                240     pk_g5        ; Gruppe := 0
                240     pk_kwacc     ; Kennzeichen := 0
                000     pi_r         ; zurueck

; ---- put_roh: Wort bw_wert mit Kennzeichen bw_k2 in die Pufferspur ablegen ----
put_roh:        240     pr_r         ; Rueckkehr sichern
                211     pk_ptr       ; Adressfeld der Zelle
                210     k_240        ; plus Speicherbefehl
                240     pr_x         ; Befehl ablegen
                211     bw_wert      ; Wort
pr_x:           db      1            ; hier steht 240 puf+zelle
                211     pk_ptr       ; Zelle
                210     k_adr1       ; plus 1
                240     pk_ptr       ; merken
                211     pk_kwacc     ; Kennzeichen
                616     nz+022       ; um 6 Bit nach links
                210     bw_k2        ; plus K2
                240     pk_kwacc     ; merken
                211     pk_cnt       ; Worte
                210     eins         ; plus 1
                240     pk_cnt       ; merken
                211     pk_g5        ; Gruppe
                210     eins         ; plus 1
                240     pk_g5        ; merken
                330     k5           ; Gruppe voll?
                170     pr_grp       ; ja
                000     pr_r         ; zurueck
pr_grp:         211     pk_kwptr     ; Kennungszelle
                210     k_240        ; plus Speicherbefehl
                240     pr_y         ; Befehl ablegen
                211     pk_kwacc     ; Kennzeichen
                616     nz+031       ; mal 8 (z30 bis z32 = 0)
pr_y:           db      1            ; hier steht 240 puf+kennungszelle
                211     pk_kwptr     ; Kennungszelle
                210     k_adr6       ; plus 6 Zellen
                240     pk_kwptr     ; naechste Gruppe
                211     pk_ptr       ; Wortzelle
                210     k_adr1       ; plus 1 (Kennungszelle ueberspringen)
                240     pk_ptr       ; merken
                241     pk_g5        ; Gruppe := 0
                240     pk_kwacc     ; Kennzeichen := 0
                000     pr_r         ; zurueck

; ---- flush: Pufferspur als Programmspur schreiben; fl_more = 1: weitere Worte folgen ----
flush:          240     fl_r         ; Rueckkehr sichern
fl_pad:         311     pk_g5        ; Gruppe voll oder leer?
                170     fl_pad_ok    ; ja
                241     bw_wert      ; Fuellwort 0
                240     bw_k2        ; Kennzeichen 0
                025     put_roh      ; ablegen
                000     fl_pad       ; weiter
fl_pad_ok:      211     sg_i         ; Spur im Segment
                330     k15          ; 16. Spur?
                170     fl_letzte    ; ja: Verkettung
fl_wr:          211     sg_spur      ; erste Spur des Segments
                210     sg_i         ; plus Spur im Segment
                240     zc_spur      ; Spur
                025     zt_schr_puf  ; schreiben
                211     sg_i         ; Spur im Segment
                210     eins         ; plus 1
                240     sg_i         ; merken
                330     k16          ; Segment voll?
                170     fl_seg       ; ja
fl_neu:         441     puf          ; Pufferspur := 0
                025     pk_init      ; Packzaehler
                000     fl_r         ; zurueck
fl_seg:         311     fl_more      ; weitere Worte?
                170     fl_neu       ; nein: sg_i bleibt 16
                211     sg_neu       ; naechstes Segment
                240     sg_spur      ; wird laufendes Segment
                241     sg_i         ; Spur im Segment := 0
                000     fl_neu       ; weiter
fl_letzte:      311     fl_more      ; weitere Worte?
                170     fl_wr        ; nein: Verkettung 0
                211     k16          ; 16 Spuren
                240     su_n         ; gesucht
                025     sp_such      ; suchen
                311     su_res       ; 0 = nicht gefunden
                170     f_voll       ; Trommel voll
                211     su_res       ; erste Spur
                240     sg_neu       ; neues Segment
                240     mk_von       ; belegen
                211     k16          ; 16 Spuren
                240     mk_n         ; belegen
                025     sp_mark      ; Belegungsliste ergaenzen
                211     t            ; Trommel
                616     nz+005       ; mal 0200
                210     sg_neu       ; plus Spur
                240     puf+036      ; Verkettung in Zelle 36
                000     fl_wr        ; Spur schreiben

; ---- prt_ziff: Ziffer pz_wert (0 bis 7) im Kleinbuchstabenzustand ausgeben ----
prt_ziff:       240     pz_r         ; Rueckkehr sichern
                211     pz_wert      ; Ziffer
                616     nz+013       ; mal 01000 (Adresseinheiten)
                210     da_pz        ; plus Tabelle
                251     0            ; AC := Ausgabebefehl der Ziffer
                240     pz_x         ; Befehl ablegen
pz_x:           db      1            ; hier steht der Ausgabebefehl
                000     pz_r         ; zurueck
; ---- prt_okt3: dreistellige Oktalzahl po_wert ausgeben ----
prt_okt3:       240     po_r         ; Rueckkehr sichern
                211     po_wert      ; Zahl
                612     nz+022       ; durch 64
                200     k7           ; untere 3 Bit
                240     pz_wert      ; Ziffer
                025     prt_ziff     ; ausgeben
                211     po_wert      ; Zahl
                612     nz+031       ; durch 8
                200     k7           ; untere 3 Bit
                240     pz_wert      ; Ziffer
                025     prt_ziff     ; ausgeben
                211     po_wert      ; Zahl
                200     k7           ; untere 3 Bit
                240     pz_wert      ; Ziffer
                025     prt_ziff     ; ausgeben
                000     po_r         ; zurueck
pz_tab:         dto     0            ; Ziffer 0
                dto     1            ; Ziffer 1
                dto     2            ; Ziffer 2
                dto     3            ; Ziffer 3
                dto     4            ; Ziffer 4
                dto     5            ; Ziffer 5
                dto     6            ; Ziffer 6
                dto     7            ; Ziffer 7

                equ100  *            ; Tabellen auf Vielfaches von 0100
