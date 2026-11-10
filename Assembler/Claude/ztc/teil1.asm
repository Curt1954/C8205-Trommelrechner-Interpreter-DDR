; ztc.asm - ZTC: Repository auf einer Zusatztrommel anlegen und ZTD als erstes Programm ablegen (C 8205Z, Format ZT-Repository_Format.md 0.01-005)
; Einsprung: Relativadresse 0 (Zelle 0 springt nach haupt). Start wie ZTL ueber das BIS: H G K0 R, 2 1 aaaa . (Hauptleitadresse), K1 R, dann Sprung auf aaaa.
; Ladeadresse aaaa muss ein Vielfaches von 0100 sein (Eingabetabellen auf 64 Zellen, Spuren auf 32 Zellen); das Programm prueft das selbst.
; Ablauf: Frage Trommel t (0 bis 3) und Zahl der Namenseintraege nn (oktal, Vorgabe 100); Pruefung, dass noch kein Repository besteht;
;   fehlt die Listenkennung auf Spur 0 der Trommel t, Frage J/N und Formatieren; Namensblock und ein Segment fuer ZTD in der Belegungsliste suchen
;   (erste Luecke ab Spur 1 auf Trommel t); ZTD als .obj vom Lochstreifenleser 1 einlesen (Gruppenform 1 + 5, Kennzeichen K2, K1 = 0),
;   Segmente verketten; Namensblock mit dem Eintrag ZTD schreiben; zuletzt Anker und Belegungsliste auf Spur 0 (Uebernahme). Ende: Sprung 0000 000.
; Tastatur K0 (Schreibwerk, Schalter SW), Ausgabe K2, Band K1. Alle Zahlen oktal. Fehler: Klartext, Status nach 07626 (ZTL_STATUS), Ende.
; Arbeitsspuren im Programm: PUF (Pufferspur fuer 601) und LTR (Spur 0 der Trommel); Nullspur NZ fuer Verschiebungen (616/612).
; Annahmen: ZTD-Segmente liegen auf derselben Trommel t wie der Namensblock; unbenutzte Spuren des letzten Segments werden mit 0 geschrieben.

                start                ; relative Zaehlung (K2 = 1)
                000     haupt        ; rel 0000: Einsprung

; ---- Konstanten ----
eins:           dw      1            ; 1
zwei:           dw      2            ; 2
k4:             dw      4            ; 4
k5:             dw      5            ; 5
k7:             dw      7            ; 7
k8:             dw      8            ; 8
k10:            dw      10           ; 10 dezimal
k12:            dw      12           ; 12 dezimal
k15:            dw      15           ; 15 dezimal
k16:            dw      16           ; 16 dezimal
k25:            dw      25           ; 25 dezimal
k32:            dw      32           ; 32 dezimal
k_vorg:         dw      0100         ; Vorgabe nn = 100 oktal
k_j:            dw      0100         ; Tabellenwert J
k_n:            dw      0101         ; Tabellenwert N
k_slash:        dw      040          ; Tabellenwert Schraegstrich
k_240:          dw      0240         ; Operationscode Speichern
k_601:          dw      0601         ; Ausgabe HT -> ZT
k_661:          dw      0661         ; Eingabe ZT -> HT
k_an:           dw      05100030     ; Befehl 5100 030 (Anwahl ZT0); plus t um 15 Bit nach links
k_amask:        dw      077000       ; untere 6 Bit der Adresse
k_adr1:         dw      01000        ; eine Adresseinheit
k_adr6:         dw      06000        ; sechs Adresseinheiten
k_lk:           dw      025147361025 ; LISTENKENNUNG
k_rk:           dw      061350247316 ; REPOSITORY_KENNUNG
k_bk:           dw      034716052613 ; BLOCKKENNUNG
k_c0:           dw      040000000000 ; Belegungsliste: nur Spur 0 belegt
k_name0:        dw      071632412120 ; Name ZTD, Zeichen 1 bis 5 (Z T D ZR ZR)
k_name1:        dw      012121212120 ; Name ZTD, Zeichen 6 bis 10 (ZR)
da_ltr:         da      ltr          ; Adresse Spur LTR
da_puf:         da      puf          ; Adresse Spur PUF
da_tabk:        da      tab_k        ; Adresse Tastaturtabelle
da_pz:          da      pz_tab       ; Adresse Ziffernausgabetabelle
null:           dw      0            ; 0

; ---- Variable ----
t:              dw      0            ; Trommel 0 bis 3
nn:             dw      0            ; Zahl der Namenseintraege
nblk:           dw      0            ; Spuren des Namensblocks
sb:             dw      0            ; erste Spur des Namensblocks
sg_erst:        dw      0            ; erste Spur des ersten ZTD-Segments
sg_spur:        dw      0            ; erste Spur des laufenden Segments
sg_neu:         dw      0            ; erste Spur des naechsten Segments
sg_i:           dw      0            ; Spur im Segment 0 bis 16
sc_u:           dw      0            ; Trommelzaehler der Suche nach vorhandenem Repository
bl_i:           dw      0            ; Spurzaehler beim Schreiben des Namensblocks
zt_t:           dw      0            ; Trommel fuer zt_anw
zc_spur:        dw      0            ; Spur fuer 601/661
zc_adr:         dw      0            ; Adressfeld der HT-Spur
zc_op:          dw      0            ; Operationscode
su_n:           dw      0            ; gesuchte Zahl freier Spuren
su_res:         dw      0            ; Ergebnis: erste Spur oder 0
su_lauf:        dw      0            ; Laenge der laufenden freien Folge
su_s:           dw      0            ; Spurzaehler
su_w:           dw      0            ; Wort der Belegungsliste (wird geschoben)
su_zb:          dw      0            ; Bitzaehler
mk_von:         dw      0            ; erste zu belegende Spur
mk_n:           dw      0            ; Anzahl
mk_bis:         dw      0            ; erste Spur hinter dem Bereich
mk_s:           dw      0            ; Spurzaehler
mk_alt:         dw      0            ; altes Listenwort (wird geschoben)
mk_neu:         dw      0            ; neues Listenwort
mk_b:           dw      0            ; neues Bit
mk_zb:          dw      0            ; Bitzaehler
d_acc:          dw      0            ; Dialog: Zahl
d_ziff:         dw      0            ; Dialog: Zahl der Ziffern
d_jn:           dw      0            ; Dialog: 1 = J, 2 = N
d_bad:          dw      0            ; Dialog: ungueltiges Zeichen
d_v:            dw      0            ; Dialog: Tabellenwert
bw_stufe:       dw      0            ; Band: 0 K1, 1 K2, 2 Ziffern
bw_ende:        dw      0            ; Band: 1 = Schlusszeichen /
bw_k1:          dw      0            ; Band: K1
bw_k2:          dw      0            ; Band: K2
bw_wert:        dw      0            ; Band: Wortwert
bw_cnt:         dw      0            ; Band: Zahl der Ziffern
bw_v:           dw      0            ; Band: Tabellenwert
pk_cnt:         dw      0            ; Worte in der Pufferspur
pk_g5:          dw      0            ; Worte in der Gruppe
pk_ptr:         dw      0            ; Adressfeld der naechsten Wortzelle
pk_kwptr:       dw      0            ; Adressfeld der Kennungszelle der Gruppe
pk_kwacc:       dw      0            ; Kennzeichen der Gruppe
pk_len:         dw      0            ; Zahl der Programmworte L
fl_more:        dw      0            ; 1 = es folgen weitere Worte
pz_wert:        dw      0            ; auszugebende Ziffer
po_wert:        dw      0            ; auszugebende dreistellige Zahl
st_zelle:       dw      0            ; (frei)
; Rueckkehrzellen der Unterprogramme (enthalten zur Laufzeit 000 <Rueckkehradresse>)
zw_r:           dw      0
za_r:           dw      0
zl_r:           dw      0
zs_r:           dw      0
zp_r:           dw      0
su_r:           dw      0
sw_r:           dw      0
mk_r:           dw      0
mw_r:           dw      0
d_r:            dw      0
bw_r:           dw      0
pr_r:           dw      0
pi_r:           dw      0
fl_r:           dw      0
pz_r:           dw      0
po_r:           dw      0

; ---- Hauptprogramm ----
haupt:          211     da_tabk      ; AC := Adresse der Tastaturtabelle
                200     k_amask      ; untere 6 Adressbits
                330     null         ; gleich 0?
                170     h_ok         ; ja: Ladeadresse ist Vielfaches von 0100
                030     04500        ; Kanal K2 (Schreibwerk)
                dtm     LADEADRESSE KEIN VIELFACHES VON 100
                dz      $wrzl        ; Zeilenschaltung
                211     k_13         ; Status 13 (oktal)
                000     f_ende       ; Ende mit Status
h_ok:           030     04500        ; Kanal K2
                dtm     ZTC
                dz      $wrzl        ; Zeilenschaltung
; -- Frage Trommel
a_t:            030     04500        ; Kanal K2
                dtm     TROMMEL (0-3)?
                dz      $wrzl        ; Zeilenschaltung
                030     04700        ; Kanal K0 (Tastatur)
                025     d_zeile      ; Eingabe lesen
                311     d_bad        ; ungueltiges Zeichen?
                170     a_t1         ; nein
                000     a_t          ; ja: neu fragen
a_t1:           311     d_jn         ; J oder N getippt?
                170     a_t2         ; nein
                000     a_t          ; ja: neu fragen
a_t2:           211     d_ziff       ; Zahl der Ziffern
                330     eins         ; genau eine?
                170     a_t3         ; ja
                000     a_t          ; nein: neu fragen
a_t3:           211     d_acc        ; Wert
                220     k4           ; minus 4
                040     a_t4         ; kleiner 4: gueltig
                000     a_t          ; sonst neu fragen
a_t4:           211     d_acc        ; Trommel
                240     t            ; merken
; -- Frage nn
a_nn:           030     04500        ; Kanal K2
                dtm     EINTRAEGE (OKTAL, VORGABE 100)?
                dz      $wrzl        ; Zeilenschaltung
                030     04700        ; Kanal K0
                025     d_zeile      ; Eingabe lesen
                311     d_bad        ; ungueltig?
                170     a_n1         ; nein
                000     a_nn         ; ja: neu fragen
a_n1:           311     d_jn         ; J oder N?
                170     a_n2         ; nein
                000     a_nn         ; ja: neu fragen
a_n2:           311     d_ziff       ; keine Ziffer: Vorgabe
                170     a_n3         ; ja
                211     d_acc        ; Wert
                330     null         ; null ist nicht erlaubt
                170     a_nn         ; neu fragen
                240     nn           ; nn := Wert
                000     a_n4         ; weiter
a_n3:           211     k_vorg       ; Vorgabe 100 oktal
                240     nn           ; nn := Vorgabe
; -- Suche nach vorhandenem Repository auf ZT0 bis ZT3
a_n4:           241     sc_u         ; u := 0
sc_next:        211     sc_u         ; u
                240     zt_t         ; Trommel u
                025     zt_anw       ; anwaehlen
                241     zc_spur      ; Spur 0
                025     zt_lies_ltr  ; Spur 0 lesen
                211     ltr+4        ; Zelle 4
                330     k_lk         ; Listenkennung?
                170     sc_lk        ; ja: Repository-Kennung pruefen
sc_weiter:      211     sc_u         ; u
                210     eins         ; u + 1
                240     sc_u         ; merken
                220     k4           ; minus 4
                040     sc_next      ; noch eine Trommel
                000     sc_ende      ; fertig
sc_lk:          211     ltr+5        ; Zelle 5
                330     k_rk         ; Repository-Kennung?
                170     f_vorh       ; ja: Repository vorhanden
                000     sc_weiter    ; nein: naechste Trommel
; -- Spur 0 der Trommel t lesen
sc_ende:        211     t            ; Trommel t
                240     zt_t         ; fuer zt_anw
                025     zt_anw       ; anwaehlen
                241     zc_spur      ; Spur 0
                025     zt_lies_ltr  ; lesen
                211     ltr+4        ; Zelle 4
                330     k_lk         ; Listenkennung?
                170     f_ok         ; ja: formatiert
                030     04500        ; Kanal K2
                dtm     TROMMEL
                dz      $zr          ; Zwischenraum
                dz      $inkb        ; Kleinbuchstabenlage (Ziffern)
                211     t            ; Trommel
                240     pz_wert      ; als Ziffer
                025     prt_ziff     ; ausgeben
                dz      $zr          ; Zwischenraum
                dtm     UNFORMATIERT. LISTE ANLEGEN (J/N)?
                dz      $wrzl        ; Zeilenschaltung
                dtm     ACHTUNG: FREMDDATEN GEHEN VERLOREN
                WRZL                 ; Zeilenschaltung, K0 angewaehlt
                025     d_zeile      ; Antwort lesen
                211     d_jn         ; 1 = J
                330     eins         ; J?
                170     f_form       ; ja: formatieren
                030     04500        ; Kanal K2
                dtm     ABGEBROCHEN
                dz      $wrzl        ; Zeilenschaltung
                211     k_14         ; Status 14 (oktal)
                000     f_ende       ; Ende
f_form:         441     ltr          ; Spur 0 := 0
                211     k_c0         ; nur Spur 0 belegt
                240     ltr+0        ; Zelle 0
                211     k_lk         ; Listenkennung
                240     ltr+4        ; Zelle 4
                241     zc_spur      ; Spur 0
                025     zt_schr_ltr  ; schreiben
; -- Namensblock und Segment fuer ZTD suchen
f_ok:           211     nn           ; nn
                612     nz+031       ; durch 8
                210     eins         ; plus 1 = Spurzahl des Blocks
                240     nblk         ; merken
                240     su_n         ; gesucht
                025     sp_such      ; Luecke suchen
                311     su_res       ; 0 = nicht gefunden
                170     f_voll       ; Trommel voll
                211     su_res       ; erste Spur
                240     sb           ; merken
                240     mk_von       ; belegen
                211     nblk         ; Anzahl
                240     mk_n         ; belegen
                025     sp_mark      ; Belegungsliste ergaenzen
                211     k16          ; 16 Spuren
                240     su_n         ; gesucht
                025     sp_such      ; suchen
                311     su_res       ; 0 = nicht gefunden
                170     f_voll       ; Trommel voll
                211     su_res       ; erste Spur des Segments
                240     sg_spur      ; laufendes Segment
                240     sg_erst      ; erstes Segment
                240     mk_von       ; belegen
                211     k16          ; 16 Spuren
                240     mk_n         ; belegen
                025     sp_mark      ; Belegungsliste ergaenzen
                241     sg_i         ; Spur im Segment := 0
                240     pk_len       ; L := 0
; -- ZTD vom Lochstreifen einlesen
                030     04500        ; Kanal K2
                dtm     ZTD-LOCHSTREIFEN IN LESER 1 LEGEN
                dz      $wrzl        ; Zeilenschaltung
                030     04600        ; Kanal K1 (Leser 1)
                441     puf          ; Pufferspur := 0
                025     pk_init      ; Packzaehler
rd_loop:        025     band_wort    ; ein Wort oder Ende lesen
                211     bw_ende      ; Schlusszeichen?
                330     eins         ; gleich 1?
                170     rd_ende      ; ja
                311     bw_k1        ; K1 gleich 0?
                170     rd_k1        ; ja
                000     f_k7         ; nein: Kennzeichen unzulaessig
rd_k1:          211     pk_cnt       ; Worte in der Spur
                330     k25          ; Spur voll?
                170     rd_voll      ; ja
rd_put:         025     put_roh      ; Wort ablegen
                211     pk_len       ; L
                210     eins         ; L + 1
                240     pk_len       ; merken
                000     rd_loop      ; naechstes Wort
rd_voll:        211     eins         ; weitere Worte folgen
                240     fl_more      ; merken
                025     flush        ; Spur schreiben
                000     rd_put       ; Wort ablegen
rd_ende:        311     pk_len       ; kein Wort gelesen?
                170     f_lochfehl   ; Lochstreifen fehlerhaft
                241     fl_more      ; kein weiteres Wort
                025     flush        ; letzte Spur schreiben
zf_loop:        211     sg_i         ; Spur im Segment
                330     k16          ; Segment voll?
                170     zf_ende      ; ja
                211     sg_spur      ; erste Spur des Segments
                210     sg_i         ; plus Spur im Segment
                240     zc_spur      ; Spur
                025     zt_schr_puf  ; Nullspur schreiben (Pufferspur ist 0)
                211     sg_i         ; naechste Spur
                210     eins         ; plus 1
                240     sg_i         ; merken
                000     zf_loop      ; weiter
; -- Namensblock schreiben
zf_ende:        030     04500        ; Kanal K2
                441     puf          ; Pufferspur := 0
                211     k_bk         ; Blockkennung
                240     puf+0        ; Wort 0
                211     nn           ; nn
                240     puf+2        ; Wort 2
                211     eins         ; ein belegter Eintrag
                240     puf+3        ; Wort 3
                211     k_name0      ; Name ZTD
                240     puf+4        ; Eintrag 0, Name 1 bis 5
                211     k_name1      ; Rest des Namens
                240     puf+5        ; Eintrag 0, Name 6 bis 10
                211     pk_len       ; L
                240     puf+6        ; Eintrag 0, Laenge
                211     t            ; Trommel
                616     nz+005       ; mal 0200
                210     sg_erst      ; plus Spur des ersten Segments
                240     puf+7        ; Eintrag 0, Lagewort
                211     sb           ; erste Spur des Blocks
                240     zc_spur      ; Spur
                025     zt_schr_puf  ; schreiben
                441     puf          ; Pufferspur := 0
                211     eins         ; i := 1
                240     bl_i         ; merken
bl_loop:        211     bl_i         ; i
                220     nblk         ; minus Spurzahl
                050     bl_ende      ; i >= Spurzahl: fertig
                211     sb           ; erste Spur
                210     bl_i         ; plus i
                240     zc_spur      ; Spur
                025     zt_schr_puf  ; Nullspur schreiben
                211     bl_i         ; i
                210     eins         ; i + 1
                240     bl_i         ; merken
                000     bl_loop      ; weiter
; -- Anker und Belegungsliste auf Spur 0
bl_ende:        211     k_rk         ; Repository-Kennung
                240     ltr+5        ; Zelle 5
                211     eins         ; Formatversion 1
                240     ltr+6        ; Zelle 6
                211     sb           ; Spur des ersten Namensblocks
                240     ltr+7        ; Zelle 7
                241     zc_spur      ; Spur 0
                025     zt_schr_ltr  ; schreiben (Uebernahme)
                030     04500        ; Kanal K2
                dtm     REPOSITORY ANGELEGT, TROMMEL
                dz      $zr          ; Zwischenraum
                dz      $inkb        ; Kleinbuchstabenlage (Ziffern)
                211     t            ; Trommel
                240     pz_wert      ; als Ziffer
                025     prt_ziff     ; ausgeben
                dtm     , BLOCK AB SPUR
                dz      $zr          ; Zwischenraum
                dz      $inkb        ; Kleinbuchstabenlage
                211     sb           ; Spur des Blocks
                240     po_wert      ; ausgeben
                025     prt_okt3     ; dreistellig
                dtm     , ZTD AB SPUR
                dz      $zr          ; Zwischenraum
                dz      $inkb        ; Kleinbuchstabenlage
                211     sg_erst      ; Spur des ersten Segments
                240     po_wert      ; ausgeben
                025     prt_okt3     ; dreistellig
                dz      $wrzl        ; Zeilenschaltung
                241     st_zelle     ; (frei)
                000     f_ende       ; Ende mit Status 0 (AC = 0)
; -- Fehler
f_vorh:         030     04500        ; Kanal K2
                dtm     REPOSITORY VORHANDEN
                dz      $wrzl        ; Zeilenschaltung
                211     k_12         ; Status 12 (oktal)
                000     f_ende       ; Ende
f_voll:         030     04500        ; Kanal K2
                dtm     TROMMELN VOLL
                dz      $wrzl        ; Zeilenschaltung
                211     k_6          ; Status 6
                000     f_ende       ; Ende
f_k7:           030     04500        ; Kanal K2
                dtm     KENNZEICHEN UNZULAESSIG
                dz      $wrzl        ; Zeilenschaltung
                211     k7           ; Status 7
                000     f_ende       ; Ende
b_fehl:
f_lochfehl:     030     04500        ; Kanal K2
                dtm     LOCHSTREIFEN FEHLERHAFT
                dz      $wrzl        ; Zeilenschaltung
                211     k_11         ; Status 11 (oktal)
f_ende:         240     07626        ; Status nach ZTL_STATUS
                030     04700        ; Kanal K0
                000     0000         ; Sprung 0000 000 (BIS)
k_6:            dw      6            ; Status 6
k_11:           dw      011          ; Status 11 (oktal)
k_12:           dw      012          ; Status 12 (oktal)
k_13:           dw      013          ; Status 13 (oktal)
k_14:           dw      014          ; Status 14 (oktal)
