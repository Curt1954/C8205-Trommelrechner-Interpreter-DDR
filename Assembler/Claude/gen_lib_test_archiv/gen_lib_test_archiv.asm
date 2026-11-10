; Pruefprogramm der Bibliothek c82gen (Archivmodus)
; ERZEUGT von Assembler/Claude/gen_lib_test_archiv/gen/gen_lib_test_archiv_gen.py -- nicht von Hand aendern, Aenderungen im Generator.
; Belegung: 680 Zellen (Code 378, Daten 302, Literale 0), Grenze 1024.
; Archivmodus (Zelle 0000 = Sprung, nur dbn, benannte Konstanten, zwei Eingabetafeln); der Test laeuft ab Zelle 0000.
; #DOK-0001 Pruefprogramm c82gen: Schieben, UP, Kurzidiome, Felder, Ausgabe, Eingabetafel (Archivmodus)
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/gen_lib_test_archiv.txt
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/gen_lib_test.txt
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/gen_lib_test-sw-ausgabe.txt
; #TASTENFOLGE H SW=1 G R
                start                ; Zaehlung beginnt bei 0000
                000     haupt          ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     pn             ; AC := pn
                616     nz+023         ; AC um 1 Bit zyklisch links
                240     l1             ; l1 := AC
                211     pn             ; AC := pn
                616     nz+06          ; AC um 2 Bit zyklisch links
                240     l2             ; l2 := AC
                211     pn             ; AC := pn
                616     nz+031         ; AC um 3 Bit zyklisch links
                240     l3             ; l3 := AC
                211     pn             ; AC := pn
                616     nz+014         ; AC um 4 Bit zyklisch links
                240     l4             ; l4 := AC
                211     pn             ; AC := pn
                616     nz+037         ; AC um 5 Bit zyklisch links
                240     l5             ; l5 := AC
                211     pn             ; AC := pn
                616     nz+022         ; AC um 6 Bit zyklisch links
                240     l6             ; l6 := AC
                211     pn             ; AC := pn
                616     nz+05          ; AC um 7 Bit zyklisch links
                240     l7             ; l7 := AC
                211     pn             ; AC := pn
                616     nz+030         ; AC um 8 Bit zyklisch links
                240     l8             ; l8 := AC
                211     pn             ; AC := pn
                616     nz+013         ; AC um 9 Bit zyklisch links
                240     l9             ; l9 := AC
                211     pn             ; AC := pn
                616     nz+036         ; AC um 10 Bit zyklisch links
                240     l10            ; l10 := AC
                211     pn             ; AC := pn
                616     nz+021         ; AC um 11 Bit zyklisch links
                240     l11            ; l11 := AC
                211     pn             ; AC := pn
                616     nz+04          ; AC um 12 Bit zyklisch links
                240     l12            ; l12 := AC
                211     pn             ; AC := pn
                616     nz+027         ; AC um 13 Bit zyklisch links
                240     l13            ; l13 := AC
                211     pn             ; AC := pn
                616     nz+012         ; AC um 14 Bit zyklisch links
                240     l14            ; l14 := AC
                211     pn             ; AC := pn
                616     nz+035         ; AC um 15 Bit zyklisch links
                240     l15            ; l15 := AC
                211     pn             ; AC := pn
                616     nz+020         ; AC um 16 Bit zyklisch links
                240     l16            ; l16 := AC
                211     pn             ; AC := pn
                616     nz+03          ; AC um 17 Bit zyklisch links
                240     l17            ; l17 := AC
                211     pn             ; AC := pn
                616     nz+026         ; AC um 18 Bit zyklisch links
                240     l18            ; l18 := AC
                211     pn             ; AC := pn
                616     nz+011         ; AC um 19 Bit zyklisch links
                240     l19            ; l19 := AC
                211     pn             ; AC := pn
                616     nz+034         ; AC um 20 Bit zyklisch links
                240     l20            ; l20 := AC
                211     pn             ; AC := pn
                616     nz+017         ; AC um 21 Bit zyklisch links
                240     l21            ; l21 := AC
                211     pn             ; AC := pn
                616     nz+02          ; AC um 22 Bit zyklisch links
                240     l22            ; l22 := AC
                211     pn             ; AC := pn
                616     nz+025         ; AC um 23 Bit zyklisch links
                240     l23            ; l23 := AC
                211     pn             ; AC := pn
                616     nz+010         ; AC um 24 Bit zyklisch links
                240     l24            ; l24 := AC
                211     pn             ; AC := pn
                616     nz+033         ; AC um 25 Bit zyklisch links
                240     l25            ; l25 := AC
                211     pn             ; AC := pn
                616     nz+016         ; AC um 26 Bit zyklisch links
                240     l26            ; l26 := AC
                211     pn             ; AC := pn
                616     nz+01          ; AC um 27 Bit zyklisch links
                240     l27            ; l27 := AC
                211     pn             ; AC := pn
                616     nz+024         ; AC um 28 Bit zyklisch links
                240     l28            ; l28 := AC
                211     pn             ; AC := pn
                616     nz+07          ; AC um 29 Bit zyklisch links
                240     l29            ; l29 := AC
                211     pn             ; AC := pn
                616     nz+032         ; AC um 30 Bit zyklisch links
                240     l30            ; l30 := AC
                211     pn             ; AC := pn
                616     nz+015         ; AC um 31 Bit zyklisch links
                240     l31            ; l31 := AC
                211     pn             ; AC := pn
                616     nz             ; AC um 32 Bit zyklisch links
                240     l32            ; l32 := AC
                211     pr             ; AC := pr
                612     nz+023         ; AC um 1 Bit nach rechts
                240     r1             ; r1 := AC
                211     pr             ; AC := pr
                612     nz+06          ; AC um 2 Bit nach rechts
                240     r2             ; r2 := AC
                211     pr             ; AC := pr
                612     nz+031         ; AC um 3 Bit nach rechts
                240     r3             ; r3 := AC
                211     pr             ; AC := pr
                612     nz+014         ; AC um 4 Bit nach rechts
                240     r4             ; r4 := AC
                211     pr             ; AC := pr
                612     nz+037         ; AC um 5 Bit nach rechts
                240     r5             ; r5 := AC
                211     pr             ; AC := pr
                612     nz+022         ; AC um 6 Bit nach rechts
                240     r6             ; r6 := AC
                211     pr             ; AC := pr
                612     nz+05          ; AC um 7 Bit nach rechts
                240     r7             ; r7 := AC
                211     pr             ; AC := pr
                612     nz+030         ; AC um 8 Bit nach rechts
                240     r8             ; r8 := AC
                211     pr             ; AC := pr
                612     nz+013         ; AC um 9 Bit nach rechts
                240     r9             ; r9 := AC
                211     pr             ; AC := pr
                612     nz+036         ; AC um 10 Bit nach rechts
                240     r10            ; r10 := AC
                211     pr             ; AC := pr
                612     nz+021         ; AC um 11 Bit nach rechts
                240     r11            ; r11 := AC
                211     pr             ; AC := pr
                612     nz+04          ; AC um 12 Bit nach rechts
                240     r12            ; r12 := AC
                211     pr             ; AC := pr
                612     nz+027         ; AC um 13 Bit nach rechts
                240     r13            ; r13 := AC
                211     pr             ; AC := pr
                612     nz+012         ; AC um 14 Bit nach rechts
                240     r14            ; r14 := AC
                211     pr             ; AC := pr
                612     nz+035         ; AC um 15 Bit nach rechts
                240     r15            ; r15 := AC
                211     pr             ; AC := pr
                612     nz+020         ; AC um 16 Bit nach rechts
                240     r16            ; r16 := AC
                211     pr             ; AC := pr
                612     nz+03          ; AC um 17 Bit nach rechts
                240     r17            ; r17 := AC
                211     pr             ; AC := pr
                612     nz+026         ; AC um 18 Bit nach rechts
                240     r18            ; r18 := AC
                211     pr             ; AC := pr
                612     nz+011         ; AC um 19 Bit nach rechts
                240     r19            ; r19 := AC
                211     pr             ; AC := pr
                612     nz+034         ; AC um 20 Bit nach rechts
                240     r20            ; r20 := AC
                211     pr             ; AC := pr
                612     nz+017         ; AC um 21 Bit nach rechts
                240     r21            ; r21 := AC
                211     pr             ; AC := pr
                612     nz+02          ; AC um 22 Bit nach rechts
                240     r22            ; r22 := AC
                211     pr             ; AC := pr
                612     nz+025         ; AC um 23 Bit nach rechts
                240     r23            ; r23 := AC
                211     pr             ; AC := pr
                612     nz+010         ; AC um 24 Bit nach rechts
                240     r24            ; r24 := AC
                211     pr             ; AC := pr
                612     nz+033         ; AC um 25 Bit nach rechts
                240     r25            ; r25 := AC
                211     pr             ; AC := pr
                612     nz+016         ; AC um 26 Bit nach rechts
                240     r26            ; r26 := AC
                211     pr             ; AC := pr
                612     nz+01          ; AC um 27 Bit nach rechts
                240     r27            ; r27 := AC
                211     pr             ; AC := pr
                612     nz+024         ; AC um 28 Bit nach rechts
                240     r28            ; r28 := AC
                211     pr             ; AC := pr
                612     nz+07          ; AC um 29 Bit nach rechts
                240     r29            ; r29 := AC
                211     pr             ; AC := pr
                612     nz+032         ; AC um 30 Bit nach rechts
                240     r30            ; r30 := AC
                211     pr             ; AC := pr
                612     nz+015         ; AC um 31 Bit nach rechts
                240     r31            ; r31 := AC
                211     pr             ; AC := pr
                612     nz             ; AC um 32 Bit nach rechts
                240     r32            ; r32 := AC
                241     px             ; px := 0, AC := 0
                025     outer          ; Aufruf outer
                211     k_7            ; AC := k_7
                240     px             ; px := AC
                025     inner          ; Aufruf inner
                211     ri             ; AC := ri
                240     rd             ; rd := AC
                211     k_5            ; AC := k_5
                240     x              ; x := AC
                211     k_7            ; AC := k_7
                240     y              ; y := AC
                211     k_m3           ; AC := k_m3
                240     neg            ; neg := AC
                241     cnt            ; cnt := 0, AC := 0
                210     k_1            ; AC := AC + k_1
                240     cnt            ; cnt := AC
                210     k_1            ; AC := AC + k_1
                240     cnt            ; cnt := AC
                210     k_1            ; AC := AC + k_1
                240     cnt            ; cnt := AC
                211     y              ; AC := y
                220     x              ; AC := AC - x
                240     dif            ; dif := AC
                240     dif2           ; dif2 := AC
                211     x              ; AC := x
                330     y              ; AC mit y vergleichen
                140     t_1            ; kleiner oder gleich: weiter bei t_1
                241     c1             ; c1 := 0, AC := 0
                000     w_2            ; weiter bei w_2
t_1:            211     k_1            ; AC := k_1
                240     c1             ; c1 := AC
w_2:            211     x              ; AC := x
                330     y              ; AC mit y vergleichen
                150     t_3            ; groesser oder gleich: weiter bei t_3
                241     c2             ; c2 := 0, AC := 0
                000     w_4            ; weiter bei w_4
t_3:            211     k_1            ; AC := k_1
                240     c2             ; c2 := AC
w_4:            211     x              ; AC := x
                330     y              ; AC mit y vergleichen
                170     t_5            ; gleich: weiter bei t_5
                241     c3             ; c3 := 0, AC := 0
                000     w_6            ; weiter bei w_6
t_5:            211     k_1            ; AC := k_1
                240     c3             ; c3 := AC
w_6:            211     y              ; AC := y
                330     k_7            ; AC mit k_7 vergleichen
                170     t_7            ; gleich: weiter bei t_7
                241     c4             ; c4 := 0, AC := 0
                000     w_8            ; weiter bei w_8
t_7:            211     k_1            ; AC := k_1
                240     c4             ; c4 := AC
w_8:            211     neg            ; AC := neg
                040     t_9            ; AC < 0: weiter bei t_9
                241     c5             ; c5 := 0, AC := 0
                000     w_10           ; weiter bei w_10
t_9:            211     k_1            ; AC := k_1
                240     c5             ; c5 := AC
w_10:           211     neg            ; AC := neg
                050     t_11           ; AC >= 0: weiter bei t_11
                241     c6             ; c6 := 0, AC := 0
                000     w_12           ; weiter bei w_12
t_11:           211     k_1            ; AC := k_1
                240     c6             ; c6 := AC
w_12:           211     x              ; AC := x
                050     t_13           ; AC >= 0: weiter bei t_13
                241     c7             ; c7 := 0, AC := 0
                000     w_14           ; weiter bei w_14
t_13:           211     k_1            ; AC := k_1
                240     c7             ; c7 := AC
w_14:           211     k_2000         ; AC := k_2000
                240     ix             ; ix := AC
                211     k_123          ; AC := k_123
                240     wv             ; wv := AC
                211     ix             ; AC := Index ix
                210     a_fe           ; AC := Index + Anfangsadresse fe
                210     k_240          ; AC := Befehl 240 fe[Index]
                240     fs_15          ; Befehl auf Zelle fs_15 ablegen
                211     wv             ; AC := wv
fs_15:          dbn     01             ; zur Laufzeit 240 fe[Index]
                211     ix             ; AC := Index ix
                210     a_fe           ; AC := Index + Anfangsadresse fe
                251     0              ; AC := fe[Index] (R-Lesebefehl)
                240     fr             ; fr := AC
                030     04500          ; Kanal K2 anwaehlen
                dtm     Test           ; Text 'Test'
                dz      $wrzl          ; Zeilenschaltung
                211     k_1234         ; AC := k_1234
                240     zahl           ; zahl := AC
                240     po_wert        ; Parameter po_wert
                030     04500          ; Kanal K2 anwaehlen
                dz      $inkb          ; Kleinbuchstabenzustand fuer Ziffern
                025     prt_okt4       ; Aufruf prt_okt4
                dz      $wrzl          ; Zeichen $wrzl
                211     k_5            ; AC := k_5
                240     d5             ; d5 := AC
                240     pz_wert        ; Parameter pz_wert
                025     prt_ziff       ; Aufruf prt_ziff
                dz      $wrzl          ; Zeichen $wrzl
                030     04700          ; Kanal K0 anwaehlen
                025     eing_init_tk   ; Eingabetafel tk waehlen: Aufruf eing_init_tk
ein_16:         dbn     01             ; Zeichen lesen (Tafel tk): zur Laufzeit 011 <Tafel tk>
                240     z1             ; z1 := AC
ein_17:         dbn     01             ; Zeichen lesen (Tafel tk): zur Laufzeit 011 <Tafel tk>
                240     z2             ; z2 := AC
ein_18:         dbn     01             ; Zeichen lesen (Tafel tk): zur Laufzeit 011 <Tafel tk>
                211     k_777          ; AC := k_777
                240     z3             ; z3 := AC
ja:             211     k_1            ; AC := k_1
                240     z3             ; z3 := AC
                164     0001           ; Diagnoseausgabe (nur im Test)
                020     0              ; Halt
inner:          240     rueck_inner    ; Rueckkehrwort sichern: px = 0: ri := 100, sonst ri := px + 1
                211     px             ; AC := px
                330     k_0            ; AC mit k_0 vergleichen
                170     in_null        ; gleich: weiter bei in_null
                211     px             ; AC := px
                210     k_1            ; AC := AC + k_1
                240     ri             ; ri := AC
                000     rueck_inner    ; Ausgang px <> 0 aus inner
in_null:        211     k_144          ; AC := k_144
                240     ri             ; ri := AC
rueck_inner:    dbn     01             ; Rueckkehrzelle von inner: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
outer:          240     rueck_outer    ; Rueckkehrwort sichern: inner zweimal rufen: px = 0 und px = 5
                241     px             ; px := 0, AC := 0
                025     inner          ; Aufruf inner
                211     ri             ; AC := ri
                240     ra             ; ra := AC
                211     k_5            ; AC := k_5
                240     px             ; px := AC
                025     inner          ; Aufruf inner
                211     ri             ; AC := ri
                240     rb             ; rb := AC
                211     ra             ; AC := ra
                210     rb             ; AC := AC + rb
                240     rs             ; rs := AC
rueck_outer:    dbn     01             ; Rueckkehrzelle von outer: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
prt_ziff:       240     rueck_prt_ziff ; Rueckkehrwort sichern: Ziffer ausgeben
                211     pz_wert        ; AC := Ziffer
                616     nz+013         ; mal 01000 (Adresseneinheiten): AC um 9 Bit zyklisch links
                210     a_pz_tab       ; plus Anfang der Ausgabebefehle
                251     0              ; AC := Ausgabebefehl der Ziffer (R-Lesebefehl)
                240     pz_x           ; Befehl ablegen
pz_x:           dbn     01             ; hier steht der Ausgabebefehl 030 xxxx
rueck_prt_ziff: dbn     01             ; Rueckkehrzelle von prt_ziff: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
prt_okt4:       240     rueck_prt_okt4 ; Rueckkehrwort sichern: Zahl mit 4 Oktalziffern ausgeben
                211     po_wert        ; AC := Zahl
                612     nz+013         ; Ziffer 1 nach unten: AC um 9 Bit nach rechts
                200     k_7            ; Ziffer 1 ausblenden (Maske 7)
                240     pz_wert        ; Ziffer 1
                025     prt_ziff       ; Ziffer 1: Aufruf prt_ziff
                211     po_wert        ; AC := Zahl
                612     nz+022         ; Ziffer 2 nach unten: AC um 6 Bit nach rechts
                200     k_7            ; Ziffer 2 ausblenden (Maske 7)
                240     pz_wert        ; Ziffer 2
                025     prt_ziff       ; Ziffer 2: Aufruf prt_ziff
                211     po_wert        ; AC := Zahl
                612     nz+031         ; Ziffer 3 nach unten: AC um 3 Bit nach rechts
                200     k_7            ; Ziffer 3 ausblenden (Maske 7)
                240     pz_wert        ; Ziffer 3
                025     prt_ziff       ; Ziffer 3: Aufruf prt_ziff
                211     po_wert        ; AC := Zahl
                200     k_7            ; Ziffer 4 ausblenden (Maske 7)
                240     pz_wert        ; Ziffer 4
                025     prt_ziff       ; Ziffer 4: Aufruf prt_ziff
rueck_prt_okt4: dbn     01             ; Rueckkehrzelle von prt_okt4: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
eing_init_tk:   240     rueck_eing_init_tk ; Rueckkehrwort sichern: Eingabetafel tk waehlen
                211     a_tk_a         ; AC := Adresse Tafel A
                200     k_40000        ; Adressbit 040 von Tafel A (Ladeadresse ist Vielfaches von 040)
                330     k_0            ; Bit 0 ?
                170     wa_19          ; ja: Tafel A liegt auf Vielfachem von 0100 (Ladeadresse ist Vielfaches von 0100)
                211     a_tk_b         ; nein: AC := Adresse Tafel B
                210     k_11           ; plus Operationscode 011
                000     sp_20          ; weiter
wa_19:          211     a_tk_a         ; AC := Adresse Tafel A
                210     k_11           ; plus Operationscode 011
sp_20:          240     ein_16         ; Eingabebefehl auf Stelle ein_16
                240     ein_17         ; Eingabebefehl auf Stelle ein_17
                240     ein_18         ; Eingabebefehl auf Stelle ein_18
rueck_eing_init_tk:dbn     01             ; Rueckkehrzelle von eing_init_tk: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
pn:             dw      -020765432107  ; Muster mit Vorzeichenbit
pr:             dw      07123456701    ; Muster positiv
l1:             dbn     01             ; Ergebnis links 1
l2:             dbn     01             ; Ergebnis links 2
l3:             dbn     01             ; Ergebnis links 3
l4:             dbn     01             ; Ergebnis links 4
                begin                  ; Eingabetafel tk
tk_a:           dw      077            ; 00 : Wert
                dw      077            ; 01 : Wert
                dw      02             ; 02 2: Wert
                dw      077            ; 03 : Wert
                dw      077            ; 04 : Wert
                dw      077            ; 05 : Wert
                dw      077            ; 06 : Wert
                dw      077            ; 07 : Wert
                dw      077            ; 10 : Wert
                dw      077            ; 11 : Wert
                dw      077            ; 12 : Wert
                dw      077            ; 13 : Wert
                dw      077            ; 14 : Wert
                dw      077            ; 15 : Wert
                dw      077            ; 16 : Wert
                dw      077            ; 17 : Wert
                dw      077            ; 20 : Wert
                000     ja             ; 21 A: Sprung
                dw      077            ; 22 : Wert
                dw      077            ; 23 : Wert
                dw      077            ; 24 : Wert
                dw      077            ; 25 : Wert
                dw      077            ; 26 : Wert
                dw      077            ; 27 : Wert
                dw      077            ; 30 : Wert
                dw      077            ; 31 : Wert
                dw      077            ; 32 : Wert
                dw      077            ; 33 : Wert
                dw      077            ; 34 : Wert
                dw      077            ; 35 : Wert
                dw      077            ; 36 : Wert
                dw      077            ; 37 : Wert
                dw      077            ; 40 : Wert
                dw      077            ; 41 : Wert
                dw      077            ; 42 : Wert
                dw      077            ; 43 : Wert
                dw      077            ; 44 : Wert
                dw      077            ; 45 : Wert
                dw      077            ; 46 : Wert
                dw      077            ; 47 : Wert
                dw      077            ; 50 : Wert
                dw      077            ; 51 : Wert
                dw      077            ; 52 : Wert
                dw      077            ; 53 : Wert
                dw      077            ; 54 : Wert
                dw      077            ; 55 : Wert
                dw      077            ; 56 : Wert
                dw      077            ; 57 : Wert
                dw      077            ; 60 : Wert
                dw      077            ; 61 : Wert
                dw      077            ; 62 : Wert
                dw      077            ; 63 : Wert
                dw      077            ; 64 : Wert
                dw      077            ; 65 : Wert
                dw      077            ; 66 : Wert
                dw      077            ; 67 : Wert
                dw      077            ; 70 : Wert
                dw      077            ; 71 : Wert
                dw      077            ; 72 : Wert
                dw      077            ; 73 : Wert
                dw      077            ; 74 : Wert
                dw      077            ; 75 : Wert
                dw      077            ; 76 : Wert
                dw      077            ; 77 : Wert
                bend                   ; Ende Eingabetafel tk
l5:             dbn     01             ; Ergebnis links 5
l6:             dbn     01             ; Ergebnis links 6
l7:             dbn     01             ; Ergebnis links 7
l8:             dbn     01             ; Ergebnis links 8
l9:             dbn     01             ; Ergebnis links 9
l10:            dbn     01             ; Ergebnis links 10
l11:            dbn     01             ; Ergebnis links 11
l12:            dbn     01             ; Ergebnis links 12
l13:            dbn     01             ; Ergebnis links 13
l14:            dbn     01             ; Ergebnis links 14
l15:            dbn     01             ; Ergebnis links 15
l16:            dbn     01             ; Ergebnis links 16
l17:            dbn     01             ; Ergebnis links 17
l18:            dbn     01             ; Ergebnis links 18
l19:            dbn     01             ; Ergebnis links 19
l20:            dbn     01             ; Ergebnis links 20
l21:            dbn     01             ; Ergebnis links 21
l22:            dbn     01             ; Ergebnis links 22
l23:            dbn     01             ; Ergebnis links 23
l24:            dbn     01             ; Ergebnis links 24
l25:            dbn     01             ; Ergebnis links 25
l26:            dbn     01             ; Ergebnis links 26
l27:            dbn     01             ; Ergebnis links 27
l28:            dbn     01             ; Ergebnis links 28
l29:            dbn     01             ; Ergebnis links 29
l30:            dbn     01             ; Ergebnis links 30
l31:            dbn     01             ; Ergebnis links 31
l32:            dbn     01             ; Ergebnis links 32
r1:             dbn     01             ; Ergebnis rechts 1
r2:             dbn     01             ; Ergebnis rechts 2
r3:             dbn     01             ; Ergebnis rechts 3
r4:             dbn     01             ; Ergebnis rechts 4
                begin                  ; Eingabetafel tk
tk_b:           dw      077            ; 00 : Wert
                dw      077            ; 01 : Wert
                dw      02             ; 02 2: Wert
                dw      077            ; 03 : Wert
                dw      077            ; 04 : Wert
                dw      077            ; 05 : Wert
                dw      077            ; 06 : Wert
                dw      077            ; 07 : Wert
                dw      077            ; 10 : Wert
                dw      077            ; 11 : Wert
                dw      077            ; 12 : Wert
                dw      077            ; 13 : Wert
                dw      077            ; 14 : Wert
                dw      077            ; 15 : Wert
                dw      077            ; 16 : Wert
                dw      077            ; 17 : Wert
                dw      077            ; 20 : Wert
                000     ja             ; 21 A: Sprung
                dw      077            ; 22 : Wert
                dw      077            ; 23 : Wert
                dw      077            ; 24 : Wert
                dw      077            ; 25 : Wert
                dw      077            ; 26 : Wert
                dw      077            ; 27 : Wert
                dw      077            ; 30 : Wert
                dw      077            ; 31 : Wert
                dw      077            ; 32 : Wert
                dw      077            ; 33 : Wert
                dw      077            ; 34 : Wert
                dw      077            ; 35 : Wert
                dw      077            ; 36 : Wert
                dw      077            ; 37 : Wert
                dw      077            ; 40 : Wert
                dw      077            ; 41 : Wert
                dw      077            ; 42 : Wert
                dw      077            ; 43 : Wert
                dw      077            ; 44 : Wert
                dw      077            ; 45 : Wert
                dw      077            ; 46 : Wert
                dw      077            ; 47 : Wert
                dw      077            ; 50 : Wert
                dw      077            ; 51 : Wert
                dw      077            ; 52 : Wert
                dw      077            ; 53 : Wert
                dw      077            ; 54 : Wert
                dw      077            ; 55 : Wert
                dw      077            ; 56 : Wert
                dw      077            ; 57 : Wert
                dw      077            ; 60 : Wert
                dw      077            ; 61 : Wert
                dw      077            ; 62 : Wert
                dw      077            ; 63 : Wert
                dw      077            ; 64 : Wert
                dw      077            ; 65 : Wert
                dw      077            ; 66 : Wert
                dw      077            ; 67 : Wert
                dw      077            ; 70 : Wert
                dw      077            ; 71 : Wert
                dw      077            ; 72 : Wert
                dw      077            ; 73 : Wert
                dw      077            ; 74 : Wert
                dw      077            ; 75 : Wert
                dw      077            ; 76 : Wert
                dw      077            ; 77 : Wert
                bend                   ; Ende Eingabetafel tk
r5:             dbn     01             ; Ergebnis rechts 5
r6:             dbn     01             ; Ergebnis rechts 6
r7:             dbn     01             ; Ergebnis rechts 7
r8:             dbn     01             ; Ergebnis rechts 8
r9:             dbn     01             ; Ergebnis rechts 9
r10:            dbn     01             ; Ergebnis rechts 10
r11:            dbn     01             ; Ergebnis rechts 11
r12:            dbn     01             ; Ergebnis rechts 12
r13:            dbn     01             ; Ergebnis rechts 13
r14:            dbn     01             ; Ergebnis rechts 14
r15:            dbn     01             ; Ergebnis rechts 15
r16:            dbn     01             ; Ergebnis rechts 16
r17:            dbn     01             ; Ergebnis rechts 17
r18:            dbn     01             ; Ergebnis rechts 18
r19:            dbn     01             ; Ergebnis rechts 19
r20:            dbn     01             ; Ergebnis rechts 20
r21:            dbn     01             ; Ergebnis rechts 21
r22:            dbn     01             ; Ergebnis rechts 22
r23:            dbn     01             ; Ergebnis rechts 23
r24:            dbn     01             ; Ergebnis rechts 24
r25:            dbn     01             ; Ergebnis rechts 25
r26:            dbn     01             ; Ergebnis rechts 26
r27:            dbn     01             ; Ergebnis rechts 27
r28:            dbn     01             ; Ergebnis rechts 28
r29:            dbn     01             ; Ergebnis rechts 29
r30:            dbn     01             ; Ergebnis rechts 30
r31:            dbn     01             ; Ergebnis rechts 31
r32:            dbn     01             ; Ergebnis rechts 32
k_7:            dw      07             ; Konstante 7
px:             dbn     01             ; Zelle px
ri:             dbn     01             ; Zelle ri
ra:             dbn     01             ; Zelle ra
rb:             dbn     01             ; Zelle rb
rs:             dbn     01             ; Zelle rs
rd:             dbn     01             ; Zelle rd
k_5:            dw      05             ; Konstante 5
k_m3:           dw      -03            ; Konstante -3
k_1:            dw      01             ; Konstante 1
x:              dbn     01             ; Zelle x
y:              dbn     01             ; Zelle y
neg:            dbn     01             ; Zelle neg
cnt:            dbn     01             ; Zelle cnt
dif:            dbn     01             ; Zelle dif
dif2:           dbn     01             ; Zelle dif2
c1:             dbn     01             ; Sprungergebnis c1
c2:             dbn     01             ; Sprungergebnis c2
c3:             dbn     01             ; Sprungergebnis c3
c4:             dbn     01             ; Sprungergebnis c4
c5:             dbn     01             ; Sprungergebnis c5
c6:             dbn     01             ; Sprungergebnis c6
c7:             dbn     01             ; Sprungergebnis c7
                begin                  ; Feld fe (zusammengehoerige Worte)
fe:             dw      013            ; Feld[0] = 11
                dw      026            ; Feld[1] = 22
                dw      041            ; Feld[2] = 33
                dw      054            ; Feld[3] = 44
                bend                   ; Ende Feld fe
k_2000:         dw      02000          ; Konstante 1024
k_123:          dw      0123           ; Konstante 83
a_fe:           da      fe             ; Anfangsadresse von fe
k_240:          dw      0240           ; Konstante 160
ix:             dbn     01             ; Zelle ix
wv:             dbn     01             ; Zelle wv
fr:             dbn     01             ; Zelle fr
k_1234:         dw      01234          ; Konstante 668
po_wert:        dbn     01             ; auszugebende Zahl
pz_wert:        dbn     01             ; auszugebende Ziffer
zahl:           dbn     01             ; auszugebende Zahl
d5:             dbn     01             ; auszugebende Ziffer
k_777:          dw      0777           ; Konstante 511
z1:             dbn     01             ; Eingabeergebnis z1
z2:             dbn     01             ; Eingabeergebnis z2
z3:             dbn     01             ; Eingabeergebnis z3
k_0:            dw      0              ; Konstante 0
k_144:          dw      0144           ; Konstante 100
a_pz_tab:       da      pz_tab         ; Anfangsadresse von pz_tab
a_tk_a:         da      tk_a           ; Anfangsadresse von tk_a
a_tk_b:         da      tk_b           ; Anfangsadresse von tk_b
k_11:           dw      011            ; Konstante 9
k_40000:        dw      040000         ; Konstante 16384
                dbn     022            ; Nullspur auf Spurgrenze
nz:             dbn     040            ; Nullspur nz: 32 Zellen 0 (Operanden der Schiebebefehle 612 und 616)
pz_tab:         dto     0              ; Ausgabebefehl Ziffer 0
                dto     1              ; Ausgabebefehl Ziffer 1
                dto     2              ; Ausgabebefehl Ziffer 2
                dto     3              ; Ausgabebefehl Ziffer 3
                dto     4              ; Ausgabebefehl Ziffer 4
                dto     5              ; Ausgabebefehl Ziffer 5
                dto     6              ; Ausgabebefehl Ziffer 6
                dto     7              ; Ausgabebefehl Ziffer 7
                end                  ; Programmende

; Sollwerte aus dem Python-Modell des Generators (unabhaengig vom Assemblerprogramm).
;#PRUEFE-START
; BZ=0466 US=1
; 0574: 36024713563   # l1
; 0575: 74051627346   # l2
; 0576: 70123456715   # l3
; 0577: 60247135633   # l4
; 0700: 40516273467   # l5
; 0701: 01234567157   # l6
; 0702: 02471356336   # l7
; 0703: 05162734674   # l8
; 0704: 12345671570   # l9
; 0705: 24713563360   # l10
; 0706: 51627346740   # l11
; 0707: 23456715701   # l12
; 0710: 47135633602   # l13
; 0711: 16273467405   # l14
; 0712: 34567157012   # l15
; 0713: 71356336024   # l16
; 0714: 62734674051   # l17
; 0715: 45671570123   # l18
; 0716: 13563360247   # l19
; 0717: 27346740516   # l20
; 0720: 56715701234   # l21
; 0721: 35633602471   # l22
; 0722: 73467405162   # l23
; 0723: 67157012345   # l24
; 0724: 56336024713   # l25
; 0725: 34674051627   # l26
; 0726: 71570123456   # l27
; 0727: 63360247135   # l28
; 0730: 46740516273   # l29
; 0731: 15701234567   # l30
; 0732: 33602471356   # l31
; 0733: 67405162734   # l32
; 0734: 03451627340   # r1
; 0735: 01624713560   # r2
; 0736: 00712345670   # r3
; 0737: 00345162734   # r4
; 1040: 00162471356   # r5
; 1041: 00071234567   # r6
; 1042: 00034516273   # r7
; 1043: 00016247135   # r8
; 1044: 00007123456   # r9
; 1045: 00003451627   # r10
; 1046: 00001624713   # r11
; 1047: 00000712345   # r12
; 1050: 00000345162   # r13
; 1051: 00000162471   # r14
; 1052: 00000071234   # r15
; 1053: 00000034516   # r16
; 1054: 00000016247   # r17
; 1055: 00000007123   # r18
; 1056: 00000003451   # r19
; 1057: 00000001624   # r20
; 1060: 00000000712   # r21
; 1061: 00000000345   # r22
; 1062: 00000000162   # r23
; 1063: 00000000071   # r24
; 1064: 00000000034   # r25
; 1065: 00000000016   # r26
; 1066: 00000000007   # r27
; 1067: 00000000003   # r28
; 1070: 00000000001   # r29
; 1071: 00000000000   # r30
; 1072: 00000000000   # r31
; 1073: 00000000000   # r32
; 1076: 00000000010   # ri
; 1077: 00000000144   # ra
; 1100: 00000000006   # rb
; 1101: 00000000152   # rs
; 1102: 00000000010   # rd
; 1110: 77777777775   # neg
; 1111: 00000000003   # cnt
; 1112: 00000000002   # dif
; 1113: 00000000002   # dif2
; 1114: 00000000001   # c1
; 1115: 00000000000   # c2
; 1116: 00000000000   # c3
; 1117: 00000000001   # c4
; 1120: 00000000001   # c5
; 1121: 00000000000   # c6
; 1122: 00000000001   # c7
; 1123: 00000000013   # fe+0
; 1124: 00000000026   # fe+1
; 1125: 00000000123   # fe+2
; 1126: 00000000054   # fe+3
; 1135: 00000000123   # fr
; 1144: 00000000002   # z1
; 1145: 00000000077   # z2
; 1146: 00000000001   # z3
;#PRUEFE-ENDE
