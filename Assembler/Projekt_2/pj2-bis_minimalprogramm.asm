; C8205 BIS - Baustein B 1.1/8 "Minimalprogramm" (8-Kanal-Ausfuehrung, R 300-Code)
; Quelle der Anforderungen: C8205-Interpreter-BIS.md (BIS-2.2, BIS-2.2.9, BIS-2.2.10.1)
;
; STUB-STAND (Schritt 0): Gerippe mit allen festen Adressen. Jede Ansprungzelle und das
; Hauptprogramm enthalten nur einen unbedingten Stopp (020 0). Der Stopp zeigt durch die
; Adresse, in welchem Stub der Rechner steht. Die Stubs werden schrittweise durch den
; echten Code ersetzt: entweder beginnt das Unterprogramm direkt auf der Ansprungzelle,
; oder dort steht ein Sprung (000 ziel) auf den eigentlichen Code.
;
; Belegung: 0000 Sprung zum Hauptprogramm (haupt), 0001 Sprung zum Druck von BZ und AC (druck),
; Minimalprogramm ab 0040 (bis 0337).
;
; Die Zellen 0000 und 0001 gehoeren eigentlich dem KEP (Spur 0, 0000 ... 0037):
;   0000 KEP: Sprung nach 0002 (KEP-Anfang)
;   0001 KEP: unbelegt
;   0002 KEP: Sprung nach 0022; 0022 bis 0024 initialisieren das KEP (Zelle 7724 ist die
;        1. Leitadresse, sie wird hier auf 0014 000 gesetzt) und springen zur Eingabe 0030.
; Erst beim Laden des Minimalprogramms mit Hilfe des KEP werden 0000 und 0001 ueberschrieben:
;   0000 -> Sprung nach haupt   (Hauptprogramm, Eingabe mit Kennzeichen; HGR)
;   0001 -> Sprung nach druck   (Druck von BZ und AC; H G M E R)
; Alle anderen Zellen des KEP (0002 ... 0037) bleiben unveraendert, insbesondere 0022.
; Die Adressen sind absolut (kein start-Parameter, Laden mit Hauptleitadresse 0).
;
; Arbeitszellen und Register (Festlegung des Projektinhabers, s. C8205-Interpreter-BIS.md, BIS-A.3):
;  - Fuer das BIS stehen die Spuren 7600, 7640, 7700 und 7740 (Zellen 7600 ... 7777) als Arbeitszellen zur
;    Verfuegung. Arbeitszellen, die als db im Programmbereich liegen, werden mit abs dorthin gelegt; das spart Platz im
;    Kernprogramm, sofern die Zelle nicht durch Weiterlaufen ausgefuehrt wurde (dann bleibt ein Sprung auf sie, so bei
;    dr_rs). Konstanten, die mitgeladen werden muessen, bleiben als dw im Programmbereich.
;  - Die Zellen duerfen auch fuer Befehle mit BAZ B = 4, 5, 6, 7 (G, GX, W, WX) als Zellenfeld benutzt werden,
;    sofern einzelne Zellen nicht anderweitig in Benutzung sind. "In Benutzung" gilt fuer das gesamte
;    BIS-Minimalprogramm (einschliesslich KEP): belegt sind 7600 (dr_rs), 7705, 7706 (kz_xw, kz_xr), 7723, 7724 (KEP),
;    7773 (R1), 7774 (R3), 7776 (R2) und 7777 (Transportzelle) sowie 7554 bis 7563 (s. unten).
;  - Die absoluten Adressen 7554 bis 7563 (Speicherplaetze fuer Ansprungzellen, abs) werden nie verschoben.
;  - Die Register R1, R2, R3 werden von den Programmteilen unterschiedlich genutzt; ihnen ist keine feste
;    Verwendung zugeordnet. Die Verwendung steht jeweils beim Programmteil.
;
;  - NULLSPUR 7640 (Festlegung F1): Die Spur 7640 bis 7677 enthaelt ausschliesslich Nullen und gehoert dem Minimalprogramm
;    (fuer Anwenderprogramme gesperrt). Sie ist die zweite Haelfte der Eingabetabelle kz_tab und wird bei jedem Neustart der
;    Kennzeicheneingabe (kz_neu) mit 441 auf null gesetzt. Jede Kette von Nullzellen, die ein W-Befehl 616 braucht, liegt auf ihr:
;    nz_12 (12 Verschiebungen, ab 7644) und nz_20 (20 Verschiebungen, ab 7674); die Zellen werden in physischer Reihenfolge
;    bis zur Position 37 (Sektor 23) durchlaufen. Die vier Nullzellen im Programmbereich (0306, 0314, 0323, 0331) entfallen.
;    Damit sie auch vor dem ersten Aufruf der Kennzeicheneingabe null ist, nullen Befehlsdruck und Adressendruck sie selbst
;    (441 nullspur am Anfang, je eine Zelle); die Trommeldatei muss dort keine Nullen enthalten.
;  - READ-ONLY-REGEL (Vorgabe des Projektinhabers): Im Bereich 0040 bis 0477 aendert das Programm keine Zelle. Ein Befehl, dessen Adressteil
;    erst zur Laufzeit berechnet wird, wird deshalb nicht im Programmbereich gebaut, sondern in der Arbeitszelle kz_xw (7705) und von
;    dort ausgefuehrt (000 kz_xw). Die Folgezelle kz_xr (7706) enthaelt den Ruecksprung (000 ziel). Sie wird vor jeder Ausfuehrung
;    gesetzt, weil Arbeitszellen nicht mitgeladen werden. Betroffen sind die Eingabetabelle der Kennzeicheneingabe (Schleife ab kz_g)
;    und die Leitadressentabelle (kz_lp). Ausnahme (bleibt): Die Arbeitszellen 7554 bis 7563 (okt_z ... ae_z) liegen unterhalb von 7600.
;
; Feste Ansprungzellen (oktal):
;   053  Befehlsdruck                              (BIS-2.2.10.1)
;   100  Adressendruck                             (BIS-2.2.10.1)
;   262  Eingabe eines Wortes mit Kennzeichen      (BIS-2.2.9)
;   263  Eingabe eines Programmstueckes            (BIS-2.2.9)
;   276  Triadendruck                              (BIS-2.2.10.1)
;   316  Adresseneingabe                           (BIS-2.2.9)
;   022  Druck BZ und AC (Angabe der Quelle): liegt im KEP, bewusst NICHT belegt
;
                start
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                000     druck           ; Zelle 0001: Sprung zum Druck von BZ und AC
;
; ---- ab 0040: Hauptprogramm = Aufruf des Unterprogramms Kennzeicheneingabe -------
; Sprung mit Rueckkehrabsicht (025); das Unterprogramm legt die Rueckkehradresse ab.
; Rueckkehr erfolgt ueber ein Schlusszeichen (BIS-2.2.9); was danach geschieht, ist noch
; festzulegen, bis dahin Stopp.
                equ     040
haupt:          025     eingabewortkz   ; Aufruf Eingabe eines Wortes mit Kennzeichen (Ansprungzelle 262)
                020     0               ; STUB Fortsetzung nach der Rueckkehr: AC = Wort, kz_k1 = K1, kz_k2 = K2
;
; ---- Ansprungzellen, aufsteigend nach Adresse ------------------------------------
                equ     053
; ---- Befehlsdruck (Ansprungzelle 053), BIS-2.2.10.1 ----------------------------------------
; Druckt den Befehl in R1 als Adresse (4 Oktalziffern), Zwischenraum und Operationsteil (3 Oktalziffern),
; z. B. 0172 211. Die Wortstellen z0 bis z11 (die oberen 4 Triaden) werden nicht gedruckt.
; Aufruf wie beim Triadendruck (Anwahl durch den Aufrufer, Wert in R1, 025 befehlsdruck). R1 bleibt unveraendert.
; Die Routine nullt zuerst die Nullspur (441 nullspur), dann ist die W-Addition ueber die Nullzellen unabhaengig vom Zustand der Trommel.
; Verfahren: R1 wird um 12 Bit nach links gedreht (1 mal 616 ueber 12 Nullzellen der Nullspur), dadurch stehen die
; Ziffern der Adresse oben. Dann druckt die Schleife des Triadendrucks (Einsprung okt_ein, Zaehler okt_z
; vorbesetzt) 4 Ziffern, es folgt der Zwischenraum und 3 Ziffern. Insgesamt wird R1 um 12 + 12 + 9 = 33
; Bit gedreht, also einmal ganz herum.
befehlsdruck:   240     bd_rs           ; Rueckkehrbefehl sichern (Register 7556)
                441     nullspur        ; Nullspur 7640 bis 7677 := 0 (Gruppenbefehl mit Loeschen, loescht auch den AC)
                dz      $inkb           ; Umschaltung in Kleinbuchstabenlage (Ziffern)
                211     r1              ; AC := Befehl
                616     nz_12           ; 12 Linksverschiebungen (W-Addition ueber die Nullzellen 7644 bis Position 37, Nullspur)
                240     r1              ; R1 := um 12 Bit gedrehter Befehl
                211     bd_za           ; Zaehler fuer 4 Ziffern (3 Einsen)
                240     okt_z
                025     okt_ein         ; Adresse drucken
                dz      $zr             ; Zwischenraum
                211     bd_zb           ; Zaehler fuer 3 Ziffern (2 Einsen)
                240     okt_z
                025     okt_ein         ; Operationsteil drucken
                000     bd_rs           ; Rueckkehr (Zelle bd_rs wird als Befehl ausgefuehrt)
;
                equ     0100
adressendruck:  000     ad_anf          ; Adressendruck (Ansprungzelle 100): Sprung zum Code ab ad_anf (Spur 0240)
;
;
; ---- Triadendruck: Code des Unterprogramms (Spur 0100) ---------------------------------
; Die feste Ansprungzelle 276 (triadendruck) springt hierher.
; Gibt den Inhalt von R1 (33 Bit) als 11 Oktalziffern (Triaden) aus (fuehrende Nullen werden mitgedruckt).
; Aufruf (der Aufrufer waehlt vorher den Ausgabekanal an; wie bei allen Ausgabe-
; unterprogrammen des BIS enthaelt das Unterprogramm keinen Anwahlbefehl):
;                 211   wert              ; auszugebender Wert in den AC
;                 240   r1                ; R1 = Versorgungszelle (BIS-2.2.10)
;                 025   triadendruck      ; Sprung mit Rueckkehrabsicht (Ansprungzelle 276)
; Der Wert wird ueber R1 uebergeben, weil 025 den AC loescht und mit dem Rueckkehr-
; befehl belegt. Danach ist der AC beliebig, R1 bleibt unveraendert.
; Verfahren nach Programmieranleitung 5.17 (Abb. 26), mit GX-Befehl als Ziffernwaehler:
;  1. R1 wird je Ziffer um 3 Bit zyklisch nach links gedreht (217, 006, 006 = Vzl 1+1+1) und
;     zurueckgespeichert. Nach 11 Ziffern (33 Bit) hat R1 wieder den Anfangswert. Die oberste
;     Ziffer steht nach der ersten Drehung unten; maskiert (200 mit 07) ergibt das die Ziffer d.
;  2. Der GX-Befehl 520 zieht von jeder Zelle der Einsen-Spur (physische Positionen 25 bis 35,
;     Spur 0200) den Wert 1 ab, beginnend bei Sektor 21, bis der AC negativ wird: nach d+2 Zellen.
;     Der Folgebefehl wird ohne Wartezeit aus der Spur des Befehlszaehlers (Spur 0100) und der
;     Sektorposition entnommen: Position 30+d (oktal). Dort, auf den physischen Positionen 30 bis 37
;     (logische Sektoren 30 05 22 37 14 31 06 23), liegen die Ausgabebefehle der Ziffern 0 bis 7.
;  3. Nach dem Druck der Ziffer geht es mit der Zelle b+2 des GX-Befehls weiter (Zelle b+1, hier
;     der Ausgabebefehl der Ziffer 4, wird uebersprungen): 311 z / 170 rs / 004 zn / 240 z.
;  4. Der Zaehler z beginnt mit 10 Einsen und wird je Ziffer um 1 Bit nach links geschoben; ist
;     z = 0, ist die 11. Ziffer gedruckt (Vergleicher 3 im Befehl 311) und es folgt die Rueckkehr.
; Die Ziffern erscheinen in Kleinbuchstabenlage (dz $inkb).
; Lage: Die Ausgabebefehle (dto) liegen auf Sektoren, die durch das Verfahren festgelegt sind
; (Sektorpositionen 30 bis 37); die uebrigen Zellen der Spur sind Code und Arbeitszellen. Einsen-
; Spur (Zellen ab 0221) steht auf Spur 0200, R1 ist das Register 7773. Zeitoptimal ist die Anordnung nicht.
                equ     0101
okt_loop:       217     r1              ; AC := Vzl(R1): 1. von 3 Verschiebungen
                006     okt_v3          ; 2. Verschiebung (Sprung auf die uebernaechste benutzte Zelle)
                equ     0103
; Einsprung fuer Aufrufer, die den Zaehler okt_z selbst vorbesetzen (Befehlsdruck): Rueckkehr sichern,
; dann Schleife. Kein dz $inkb, der Aufrufer hat die Kleinbuchstabenlage schon eingestellt.
okt_ein:        240     okt_rs          ; Rueckkehrbefehl sichern (Register 7555)
                000     okt_loop
                equ     0105
                dto     1               ; Position 31 (Ziffer 1)
                dto     6               ; Position 36 (Ziffer 6), Sektor 06
                equ     0110
okt_v3:         006     okt_sp          ; 3. Verschiebung
okt_sp:         240     r1              ; R1 := Vzl3(R1) (AC bleibt)
                200     okt_mask        ; AC := Ziffer d (letzte Triade)
okt_gx:         520     okt_e1          ; GX-Subtraktion auf der Einsen-Spur: waehlt den Ausgabebefehl
                dto     4               ; Position 34 (Ziffer 4); beim GX-Befehl die uebersprungene Zelle b+1
                311     okt_z           ; AC := z; Vergleicher 3, falls z = 0
                170     okt_rs          ; z = 0: Rueckkehr (Zelle okt_rs wird als Befehl ausgefuehrt)
                004     okt_zn          ; AC := z um 1 Bit nach links (Verschiebung im Sprungbefehl)
okt_zn:         240     okt_z           ; z := Vl(z)
                000     okt_loop        ; naechste Ziffer
                dto     2               ; Position 32 (Ziffer 2), Sektor 22
                dto     7               ; Position 37 (Ziffer 7), Sektor 23
okt_mask:       dw      07              ; Maske fuer die letzte Triade
okt_z0:         dw      077740000000    ; Anfangswert des Zaehlers: 10 Einsen
bd_za:          dw      070000000000    ; Befehlsdruck: Zaehler fuer 4 Ziffern (3 Einsen)
bd_zb:          dw      060000000000    ; Befehlsdruck: Zaehler fuer 3 Ziffern (2 Einsen)
                dto     0               ; Position 30 (Ziffer 0), Sektor 30
                dto     5               ; Position 35 (Ziffer 5), Sektor 31
okt_anf:        240     okt_rs          ; Rueckkehrbefehl sichern
                dz      $inkb           ; Umschaltung in Kleinbuchstabenlage (Ziffern)
                211     okt_z0          ; Zaehler := 10 Einsen
                240     okt_z
                000     okt_loop        ; Sektor 36; der Sektor 37 danach ist der Ausgabebefehl der Ziffer 3
                dto     3               ; Position 33 (Ziffer 3), Sektor 37
;
; ---- Druck von BZ und AC (Ziel der Zelle 0001; Tastenfolge H G M+ E M- (SP loesen) R) -------
; Ein laufendes Programm wurde unterbrochen (Ueberlauf, Stopp usw.); BZ = b ist der Stand des
; Befehlszaehlers, also die Adresse des als naechsten abzuarbeitenden Befehls. Vorher wurde mit
; H G Ue E der Akkumulatorinhalt nach Zelle 7777 transportiert (Bedienpult 4.2); dabei lief ein
; Schritt, BZ steht danach auf b+1. Das E unter M (Bedienpult 4.3) liefert im AC den Rueckkehr-
; befehl 0000 aaaa 000 mit aaaa = (b+1) + 2 = b + 3.
; Ausgegeben werden (Schreibwerk, Kanal K2, Ausgabe mit dem Triadendruck):
;     BZ 0000bbbb000 AC aaaaaaaaaaa
; BZ ist der um 3 Adresseinheiten verminderte AC, also der Sprungbefehl 0000 bbbb 000. Danach wird der
; AC aus Zelle 7777 zurueckgeholt und dieser Sprungbefehl (000 b) ausgefuehrt: Das Programm
; wird mit dem Befehl b und seinem AC fortgesetzt. Ist der Schalter BS eingerastet, geht der
; Rechner vorher in den bedingten Stopp (Loesen von BS setzt fort).
; Nicht fortsetzbar sind Unterbrechungen in den Programmen Adressendruck, Befehlsdruck und Triadendruck.
; Die Anwahl des Schreibwerks (030 4500) steht hier, weil der Triadendruck keinen Anwahlbefehl enthaelt.
; Der Fortsetzungsbefehl (000 b) liegt in der Arbeitszelle dr_rs (7600, Arbeitsbereich), nicht im Programmbereich;
; er wird mit dem Sprung 000 dr_rs am Ende der Routine angesprungen (frueher: Zelle hinter dem Stopp, db).
                equ     0150
druck:          220     dr_drei         ; AC := AC - 3 Adresseinheiten = Befehl 0000 bbbb 000
                240     dr_rs           ; als Fortsetzungsbefehl merken (Zelle dr_rs wird am Ende ausgefuehrt)
                240     r1              ; R1 := BZ-Wort
                030     04500           ; Anwahl Kanal K2 (Schreibwerk)
                dz      $wrzl           ; neue Zeile
                dtm     \BZ \
                025     triadendruck    ; BZ-Wort drucken
                dz      $zr             ; Zwischenraum
                dtm     \AC \
                211     ac7777          ; AC := gerettete AC-Inhalt (Zelle 7777)
                240     r1
                025     triadendruck    ; AC drucken
                dz      $wrzl           ; Zeilenende
                211     ac7777          ; AC := gerettete AC-Inhalt: das Programm setzt mit seinem AC fort
                060     0               ; bedingter Stopp (bei eingerastetem BS)
                000     dr_rs           ; Fortsetzung: Zelle dr_rs (Arbeitsbereich) wird als Befehl 000 b ausgefuehrt
dr_drei:        dw      03000           ; 3 Adresseinheiten
;
; Spur 0200: Einsen-Spur fuer den GX-Befehl des Triadendrucks.
; Der GX-Befehl 520 beginnt bei 0221 (physische Position 25) und braucht die Einsen auf den
; physischen Positionen 25 bis 35 (logische Sektoren 21 36 13 30 05 22 37 14 31). Die anderen
; Sektoren der Spur bleiben frei fuer weitere Daten.
                equ     0205
                dw      01              ; Sektor 05 (Position 32)
                equ     0213
                dw      01              ; Sektor 13 (Position 27)
                dw      01              ; Sektor 14 (Position 34)
                equ     0221
okt_e1:         dw      01              ; Sektor 21 (Position 25): Start des GX-Befehls
                dw      01              ; Sektor 22 (Position 32)
                equ     0230
                dw      01              ; Sektor 30 (Position 30)
                dw      01              ; Sektor 31 (Position 35)
                equ     0236
                dw      01              ; Sektor 36 (Position 26)
                dw      01              ; Sektor 37 (Position 33)
;
; ---- Adressendruck: Code des Unterprogramms (Spur 0240) -------------------------------------
; Die feste Ansprungzelle 100 (adressendruck) springt hierher.
; Druckt vom Wort in R1 nur die Wortstellen z12 bis z23 (das Adressfeld, die mittleren 4 Triaden) als
; 4 Oktalziffern, z. B. 0000 bis 7777 (Programmieranleitung, Abschnitt Adressendruck). Die Wortstellen z0 bis z11
; und z24 bis z32 werden nicht gedruckt.
; Aufruf wie bei Triaden- und Befehlsdruck (Anwahl durch den Aufrufer, Wert in R1, 025 adressendruck).
; R1 bleibt unveraendert (BIS-2.2.10): Die Schleife okt_loop dreht R1 beim Druck von 4 Ziffern um 12 Bit,
; dazu kommen 12 Bit Vorbereitung, zusammen 24 Bit und damit nicht ganz herum. R1 wird deshalb in ad_sv
; gerettet und am Ende zurueckgeholt.
; Verfahren: wie im Befehlsdruck wird R1 um 12 Bit nach links gedreht (1 mal 616 ueber die Nullspur),
; dadurch stehen die Adressziffern oben. Dann druckt die Schleife des Triadendrucks (Einsprung okt_ein,
; Zaehler okt_z mit bd_za vorbesetzt) 4 Ziffern.
                equ     0240
ad_anf:         240     ad_rs           ; Rueckkehrbefehl sichern (Register 7557)
                441     nullspur        ; Nullspur 7640 bis 7677 := 0 (Gruppenbefehl mit Loeschen, loescht auch den AC)
                dz      $inkb           ; Umschaltung in Kleinbuchstabenlage (Ziffern)
                211     r1              ; AC := Wert
                240     ad_sv           ; R1 sichern (Register 7560)
                616     nz_12           ; 12 Linksverschiebungen (W-Addition ueber die Nullzellen 7644 bis Position 37, Nullspur)
                240     r1              ; R1 := um 12 Bit gedrehtes Wort, die Adressziffern stehen oben
                211     bd_za           ; Zaehler fuer 4 Ziffern (3 Einsen)
                240     okt_z
                025     okt_ein         ; Adresse drucken (4 Ziffern)
                211     ad_sv           ; R1 zurueckholen
                240     r1
                000     ad_rs           ; Rueckkehr (Zelle ad_rs wird als Befehl ausgefuehrt)
;
                equ     0262
eingabewortkz:  000     kz_anf          ; Eingabe eines Wortes mit Kennzeichen (Ansprungzelle 262): Sprung zum Code ab kz_anf (Spur 0332)
eingabeprogst:  020     0               ; STUB Eingabe eines Programmstueckes (263)

; ---- Adresseneingabe: Code des Unterprogramms (verteilt auf freie Zellen, Lage vorlaeufig) -----------------
; Die feste Ansprungzelle 316 (adresseneingabe) springt nach ae_anf.
; Liest eine maximal achtstellige oktale Adresskonstante ueber den vom Aufrufer angewaehlten Kanal (Anwahl wie bei den
; Ausgabeunterprogrammen durch den Aufrufer, Aufruf mit 025 adresseneingabe). Schlusszeichen ist der Punkt.
; Ergebnis: Die Konstante steht im Akkumulator und belegt die Wortstellen z0 bis z23, rechtsbuendig in den Oktalstellen
; t3 bis t10 (Eingabe 1234. ergibt AC = 0000 1234 000); die Konstante Null braucht nur den Punkt.
; Zeichen: Ziffern 0 bis 7, Punkt (Schlusszeichen), Zwischenraum ZR (Sprung zum Neustart der Kennzeicheneingabe kz_neu).
; Ziffern 8 und 9 sind keine Oktalziffern: HALT (Stopp im Befehl ae_halt). Jede Ziffer ab der neunten wird ignoriert,
; bis das Schlusszeichen kommt (das gilt auch fuer 8 und 9).
; Verfahren (Eingabe-Halt mit Sprung-Umstellung, Kodetabellen 1.5 und 1.8): Der Eingabebefehl 010 ae_tab verknuepft die
; Eingabeadresse des gelesenen Zeichens mit ae_tab. Ziffern (ohne Sprung-Umstellung) lesen die Konstante d * 0100 aus der
; Tabellenzelle und addieren sie zum AC; die Zellen fuer 8 und 9 enthalten 2 hoch 30 (ae_pois), das ist groesser als jeder
; gueltige AC in diesem Moment (hoechstens 7 Ziffern vor einer achten); der Vergleich 330 ae_pois mit Sprung 150 erkennt das.
; Dann drehen drei Sprungbefehle 006 den AC zyklisch um 3 Bit (eine Oktalstelle) nach links. Ein Zaehler ae_z (7 Einsen,
; je Ziffer um 1 Bit nach links geschoben, wie im Triadendruck) zaehlt die Ziffern: Nach der achten (ae_z = 0) geht es in
; die Schleife ae_ign, die jede weitere Ziffer mit Loeschen (011) einliest und verwirft. Der Akkumulator wird dazu in
; ae_sv gehalten; der Punkt holt ihn zurueck (Tabellenzelle ae_tab+033: 211 ae_sv, danach 000 ae_rs).
                equ     0264
ae_anf:         240     ae_rs           ; Rueckkehrbefehl sichern (Register 7561)
                211     ae_z0           ; Zaehleranfang: 7 Einsen
                240     ae_z            ; Zaehler setzen (Register 7563)
                211     ae_tab          ; AC := 0 (Zelle ae_tab, Ziffer 0, enthaelt 0)
                240     ae_sv           ; Konstante := 0 (Register 7562)
ae_loop:        010     ae_tab          ; Eingabe-Halt: Ziffer lesen, AC := AC + d * 0100; ZR oder Punkt: Sprung in die Tabelle
                330     ae_pois         ; Vergleich AC mit 2 hoch 30: ab dort Ziffer 8 oder 9
                150     ae_halt         ; AC >= 2 hoch 30: Ziffer 8 oder 9, HALT
                006     ae_v2           ; Linksverschiebung (zyklisch) 1 von 3
                equ     0275
ae_v2:          006     ae_v3           ; 2 von 3
                equ     0277
ae_v3:          006     ae_zt           ; 3 von 3
;
                equ     0276
triadendruck:   000     okt_anf         ; Triadendruck (Ansprungzelle 276): Sprung zum Code ab okt_anf
;
; Die Nullzellen 0306, 0314, 0323 und 0331 fuer die W-Addition entfallen (die W-Addition laeuft jetzt ueber die Nullspur 7640).
; Auf 0306 und 0314 stehen die beiden letzten Sprungbefehle der Dreifach-Verschiebung des Wortaufbaus (Fortsetzung der Zelle kz_wl).
                equ     0306
kz_w2:          006     kz_w3           ; 2 von 3 (Linksverschiebung, zyklisch)
                equ     0314
kz_w3:          006     kz_wz           ; 3 von 3
                equ     0316
adresseneingabe: 000    ae_anf          ; Adresseneingabe (Ansprungzelle 316): Sprung zum Code ab ae_anf (Spur 0260)
;
; Die Zelle 0320 (frueher Stub kzeingabe) ist frei: Die Kennzeicheneingabe ist die Eingabe eines Wortes mit
; Kennzeichen (Ansprungzelle 262, Code ab kz_anf, Neustart ueber kz_neu).
;
; ---- Adresseneingabe, Fortsetzung (freie Zellen 0256 bis 0261, 0300 bis 0311) ----------------------------------
                equ     0256
ae_z0:          dw      077400000000    ; Zaehleranfang der Adresseneingabe: 7 Einsen (8 Ziffern)
ae_halt:        020     0               ; HALT: Ziffer 8 oder 9 (keine Oktalziffer)
ae_ign:         011     ae_tab          ; ab der 9. Ziffer: Zeichen lesen, AC loeschen (Ziffer wird verworfen); ZR/Punkt wie oben
                000     ae_ign          ; naechstes Zeichen
                equ     0300
ae_zt:          240     ae_sv           ; Konstante sichern (Register 7562)
                311     ae_z            ; AC := Zaehler; Vergleicher 3, falls Zaehler = 0
                170     ae_ign          ; Zaehler = 0: 8 Ziffern gelesen, weitere Ziffern verwerfen
                004     ae_zn           ; AC := Zaehler um 1 Bit nach links
                equ     0307
ae_zn:          240     ae_z            ; Zaehler := Vl(Zaehler)
                211     ae_sv           ; AC := Konstante zurueck
                000     ae_loop         ; naechstes Zeichen
;
;
; ---- Eingabe eines Wortes mit Kennzeichen (Ansprungzelle 262), BIS-2.2.2 bis BIS-2.2.5 ------------------------------
; Aufruf: Der Aufrufer waehlt den Eingabekanal an (z. B. 030 4600), dann 025 eingabewortkz.
; Eingegeben wird K1 K2 und danach das Wort. Zugelassen sind nur K1 = 0, 1, 2 und K2 = 0 bis 9 (Ziffern). Jedes andere Zeichen
; (auch ZR, Punkt, Schraegstrich, Buchstaben, die Ziffern 3 bis 9 als K1) ist unzulaessig und fuehrt ohne Meldung zum Sprung auf 0000
; (Festlegung F2, BIS-2.2.2): Dort steht der Sprung zum Hauptprogramm, der die Eingabe mit neuem K1 aufruft; kz_neu baut die Tabelle neu auf.
; Dasselbe gilt fuer eine unzulaessige Ziffer 8 oder 9 (F3) und fuer die 12. Ziffer eines Wortes. Wegen des Sprungs auf 0000 gibt es fuer den
; Aufrufer keine Rueckkehr im Fehlerfall, er sieht nur den Neustart.
; K1 = 0, 1 (Wort, Befehl): bis 11 Oktalziffern t10 ... t0, Schlusszeichen Punkt. Der AC enthaelt danach das Wort; bei K2 = 1 bis 9 ist
;   zu den Oktalstellen t3 bis t10 die K2-te Leitadresse addiert (Adressenaenderung), bei K2 = 0 nicht. Rueckkehr mit 000 kz_rs. Die
;   Kennzeichen stehen als K1 * 01000 in kz_k1 und K2 * 01000 in kz_k2 (der Aufrufer speichert bzw. fuehrt aus).
; K1 = 2 (Leitadresse): bis 8 Oktalziffern ueber das Unterprogramm Adresseneingabe (025 adresseneingabe, Ansprungzelle 316). Die Adresse
;   (t3 bis t10) wird in die Leitadressentabelle la_tab gespeichert. Es gibt keine Rueckkehr, es folgt die Eingabe eines neuen K1.
; Leitadressentabelle (oberhalb 7600, Arbeitsbereich): zehn aufeinanderfolgende Zellen ab la_tab = 7724 (oktal gezaehlt bis 7735). 7724 ist die
;   Hauptleitadresse (K2 = 1), 7725 bis 7734 sind die 2. bis 9. Leitadresse (K2 = 2 bis 9), 7735 die Relativadresse (K2 = 0).
;   Zelle fuer K2 = la_tab + (K2 - 1) mod 10. Die Zellen 7725, 7730 und 7731 stehen in der BIS-Dokumentation unter den noch nicht geklaerten
;   festen Zellen; ihre Lage in der Tabelle haengt nur von der Konstanten c_la (Adressteil la_tab) ab.
; Eingabetabelle (Verfahren wie bei der Adresseneingabe, Eingabe-Halt 011 mit Sprung-Umstellung): 64 Zellen auf der Arbeitsspur 7600 bis 7677
;   (kz_tab). Sie wird bei jedem Neustart durch Kopieren aufgebaut statt im Programmbereich zu liegen: Zwei Gruppenbefehle 441 (Transport mit
;   Loeschen) belegen alle 64 Zellen mit null; die zweite Haelfte (7640 bis 7677) ist zugleich die Nullspur und bleibt null. Danach werden die
;   Zellen der Ziffern 0 bis 9 von einer Schleife mit einem zur Laufzeit gebauten Transportbefehl in der Arbeitszelle kz_xw NEGATIV kodiert:
;   Zelle d = (d - 10) * 01000 (-10 ... -1 Adresseinheiten). Dadurch gilt ohne weiteren Code:
;   - jedes gueltige Datum (Ziffer) ist negativ, jedes ungueltige Datum (Buchstabe ohne Sprung-Umstellung, liest die Nullzelle) ist >= 0,
;   - jedes Zeichen mit Sprung-Umstellung (ZR, Punkt, :, / usw.) fuehrt die Nullzelle als Befehl 000 0000 aus und springt nach 0000.
;   Die Gueltigkeitspruefung ist ein Vergleich (330) des Rohwertes mit einer Tabellenzelle und ein Sprung 150 nach 0000: K1 gegen Zelle 3
;   (Fehler ab Rohwert >= -7 Einheiten), K2 mit 050 (Fehler ab Rohwert >= 0), Wortziffer gegen Zelle 010 (Fehler ab >= -2 Einheiten). Danach holt
;   210 c_zehn den Wert d * 01000 zurueck. Konstanten stehen nicht mehr in der Tabelle (c_unit, c_two, c_zehn). Fuer das Wort ersetzt der Code ab 0364 die
;   Tabellenzelle des Punktes (Offset 033) durch den Sprung c_pkt (000 kz_wend). Die Zelle 7600 der Tabelle ist zugleich dr_rs (Druck von BZ und AC); dr_rs wird nur kurz benutzt und bei
;   jedem Neustart der Tabelle wieder ueberschrieben (Ausnahme: wird die Eingabe mit H unterbrochen und BZ/AC gedruckt, ist 0 bis zum
;   naechsten Neustart unzulaessig).
; Wortaufbau: Die Ziffer d * 01000 wird zur Wortsumme kz_kw addiert, dann wird kz_kw um 3 Bit zyklisch nach links gedreht (3 mal 006). Nach n Ziffern
;   steht das Wort um 12 Bit zyklisch nach links gedreht in kz_kw (die 33 Bit sind ein Ring, 11 Ziffern passen genau); der Punkt dreht es mit
;   217 und 616 nz_20 (zusammen 1 + 20 = 21 Bit) in die richtige Lage zurueck. Zaehler kz_z wie in der Adresseneingabe (10 Einsen, 11 Ziffern).
; Die Lage der Teile ist auf freie Zellen verteilt (0042 bis 0045, 0140 bis 0147, 0177 bis 0203, 0206 bis 0212, 0215 bis 0220, 0223 bis 0225,
; 0306, 0314, 0324 bis 0330, 0331 bis 0377); Konstanten stehen auf einzelnen freien Zellen (0304, 0305, 0312, 0313, 0315, 0317, 0320, 0321, 0322).
;
; Zellen 0331 bis 0377: Hauptteil (Aufbau der Tabelle, K1, K2, Verteiler, Anfang der Wortschleife)
; Aufbau der Ziffernzellen (Schleife kz_g): kz_xw enthaelt den Transportbefehl 240 kz_tab+d fuer die Zelle der Ziffer d. Je Durchlauf wird
; er um eine Adresseneinheit weitergezaehlt, mit c_xend (Befehl fuer die Zelle 10) verglichen und mit 000 kz_xw ausgefuehrt; die Folgezelle
; kz_xr (000 kz_g) fuehrt zur Schleife zurueck. Der Anfangswert c_x0 zeigt eine Zelle vor die Ziffer 0, die erste Weiterzaehlung ergibt Ziffer 0.
                equ     0331
kz_anf:         240     kz_rs           ; Rueckkehrbefehl sichern (Arbeitszelle 7700)
kz_neu:         441     kz_tab          ; Gruppenbefehl mit Loeschen: Spur 7600 (32 Zellen) := 0 (Neustart der Eingabe)
                441     kz_tab+040      ; Spur 7640 (32 Zellen) := 0: die Nullspur (Befehl 000 0000 = Sprung nach 0000)
                211     c_xr            ; AC := Sprung 000 kz_g
                240     kz_xr           ; Folgezelle von kz_xw := 000 kz_g (Arbeitszelle 7706)
                211     c_x0            ; AC := Transportbefehl 240 kz_tab-1 (eine Zelle vor Ziffer 0)
                240     kz_xw           ; kz_xw := Anfangswert (Arbeitszelle 7705)
kz_g:           211     kz_xw           ; AC := Transportbefehl der letzten Ziffernzelle
                210     c_unit          ; naechste Zelle (eine Adresseneinheit)
                240     kz_xw           ; kz_xw := Transportbefehl fuer die Zelle der Ziffer d (AC bleibt)
                330     c_xend          ; Vergleich mit dem Befehl fuer die Zelle 10
                150     kz_k1l          ; AC >= Befehl fuer Zelle 10: Ziffern 0 bis 9 fertig, K1 lesen
                200     c_msk           ; AC := d * 01000 (die unteren 6 Bit der Adresse, 7600 hat dort Nullen)
                220     c_zehn          ; AC := (d - 10) * 01000: Ziffernzellen negativ, ungueltige Zellen null
                000     kz_xw           ; Ausfuehrung des Transportbefehls in der Arbeitszelle, danach 000 kz_g (Zelle kz_xr)
kz_k1l:         011     kz_tab          ; K1 lesen (AC := Zelle des Zeichens, Sprung-Zeichen: Zelle 0 = Sprung nach 0000)
                330     kz_tab+3        ; Vergleich mit der Zelle der Ziffer 3 (-7 Adresseinheiten)
                150     0               ; AC >= Zelle 3 (null, 3 bis 9 oder Buchstabe): kein K1 = 0, 1, 2: Sprung nach 0000
                210     c_zehn          ; AC := K1 * 01000
                240     kz_k1           ; K1 * 01000 merken (Arbeitszelle 7701)
                011     kz_tab          ; K2 lesen
                050     0               ; AC >= 0 (Zelle null): keine Ziffer, Sprung nach 0000
                210     c_zehn          ; AC := K2 * 01000
                240     kz_k2           ; K2 * 01000 merken (Arbeitszelle 7702)
                211     kz_k1
                330     c_two           ; K1 = 2?
                170     kz_la           ; K1 = 2: Leitadresse
                211     okt_z0          ; Zaehler: 10 Einsen (11 Ziffern)
                240     kz_z            ; (Arbeitszelle 7704)
                211     kz_tab+040      ; AC := 0 (Nullspur)
                240     kz_kw           ; Wortsumme := 0 (Arbeitszelle 7703)
                211     c_pkt           ; AC := Sprung 000 kz_wend
                240     kz_tab+033      ; Tabellenzelle des Punktes := Sprung zum Wortende
kz_wl:          011     kz_tab          ; Ziffer lesen: AC := (d - 10) * 01000
                330     kz_tab+010      ; Vergleich mit der Zelle der Ziffer 8 (-2 Adresseinheiten)
                150     0               ; Ziffer 8, 9 oder anderes Zeichen (Zelle null): Sprung nach 0000
                210     c_zehn          ; AC := d * 01000
                210     kz_kw           ; AC := Wortsumme + d * 01000
                006     kz_w2           ; Linksverschiebung (zyklisch) 1 von 3 (2 und 3 von 3 auf 0306 und 0314)
;
; Zellen 0140 bis 0147: Rest der Wortschleife
                equ     0140
kz_wz:          240     kz_kw           ; Wortsumme := gedrehte Summe
                311     kz_z            ; AC := Zaehler; Vergleicher 3, falls Zaehler = 0
                170     kz_ign          ; 11 Ziffern gelesen: nur noch der Punkt ist zulaessig
                004     kz_zn           ; AC := Zaehler um 1 Bit nach links
kz_zn:          240     kz_z            ; Zaehler := Vl(Zaehler)
                000     kz_wl           ; naechstes Zeichen
kz_ign:         011     kz_tab          ; weiteres Zeichen: Punkt springt nach kz_wend, alles andere ist ein Fehler
                000     0               ; Ziffer oder Buchstabe: Fehler, Sprung nach 0000
;
; Wortende (Punkt gelesen), verteilt auf die Zellen 0177 bis 0203, 0324 bis 0330 und 0042 bis 0051: K2 = 0: nichts addieren; K2 = 1 bis 9: Leitadresse K2 addieren
                equ     0177
kz_wend:        211     kz_k2           ; AC := K2 * 01000
                330     c_unit          ; Vergleich mit 1 * 01000
                150     kz_wm           ; K2 >= 1: Leitadresse holen
                240     kz_v            ; K2 = 0: AC = 0, Zuschlag := 0
                000     kz_wr
                equ     0324
kz_wm:          220     c_unit          ; AC := (K2 - 1) * 01000
                210     c_la            ; AC := Transportbefehl auf die Leitadresse K2: Adressteil = la_tab + K2 - 1
                251     0               ; R-Lesebefehl: AC := Inhalt der durch den Adressteil des AC genannten Zelle
                240     kz_v            ; Zuschlag := Leitadresse K2
                000     kz_wr
                equ     042
kz_wr:          217     kz_kw           ; AC := Vzl(Wortsumme), 1 von 21 Bit
                616     nz_20           ; 20 Linksverschiebungen (W-Addition ueber die Nullzellen 7674 bis Position 37, Nullspur); AC = Wort
                210     kz_v            ; Adressenaenderung: AC := Wort + Zuschlag
                000     kz_rs           ; Rueckkehr zum Aufrufer, AC = Wort (K1 in kz_k1, K2 in kz_k2)
;
; K1 = 2: Zelle der Leitadressentabelle bestimmen, dann Adresse einlesen und speichern
                equ     0206
kz_la:          211     kz_k2           ; AC := K2 * 01000
                220     c_unit          ; AC := (K2 - 1) * 01000
                050     kz_lp           ; K2 >= 1: Zelle la_tab + K2 - 1
                210     c_zehn          ; K2 = 0: Zelle la_tab + 9 (Relativadresse)
                000     kz_lp
; Der Transportbefehl auf die Leitadressenzelle wird in der Arbeitszelle kz_xw gebaut (Read-only-Regel). Nach der Adresseneingabe fuehrt der
; Sprung 000 kz_xw ihn aus; die Folgezelle kz_xr enthaelt 000 kz_neu (die ZR-Zelle ae_zr der Adresseneingabe-Tabelle dient als Konstante).
                equ     0215
kz_lp:          210     c_la            ; AC := Transportbefehl auf die Leitadressenzelle
                240     kz_xw           ; Transportbefehl 240 la_tab+K2-1 in die Arbeitszelle (7705)
                211     ae_zr           ; AC := Sprung 000 kz_neu (Zelle ae_zr wird nur gelesen)
                000     kz_lq           ; weiter auf 0223 (0221 und 0222 gehoeren der Einsen-Spur)
                equ     0223
kz_lq:          240     kz_xr           ; Folgezelle von kz_xw := 000 kz_neu (Arbeitszelle 7706)
                025     adresseneingabe ; Adresse einlesen (AC = Adresse in t3 bis t10); ZR bricht nach kz_neu ab
                000     kz_xw           ; Leitadressenzelle K2 := Adresse (Befehl in kz_xw), danach 000 kz_neu: neues K1, keine Rueckkehr
;
; Konstanten auf einzelnen freien Zellen
                equ     0304
c_two:          dw      02000           ; 2 Adresseinheiten (Vergleichswert K1 = 2; ersetzt den frueheren Fehlersprung c_err)
c_x0:           240     kz_tab-1        ; Anfangswert des Transportbefehls in kz_xw (eine Zelle vor Ziffer 0)
                equ     0312
c_msk:          dw      077000          ; Maske fuer die unteren 6 Adressbit
c_unit:         dw      01000           ; eine Adresseneinheit
                equ     0315
c_xend:         240     kz_tab+012      ; Transportbefehl fuer die Zelle 10 (Ende der Schleife kz_g)
                equ     0317
c_pkt:          000     kz_wend         ; Sprung des Punktes zum Wortende
                equ     0320
c_xr:           000     kz_g            ; Folgezelle kz_xr der Schleife kz_g: Ruecksprung zur Schleife
                equ     0321
c_zehn:         dw      012000          ; 10 Adresseneinheiten
c_la:           240     la_tab          ; Transportbefehl auf la_tab; Adressteil + K2 * 01000
;
; ---- Eingabetabelle der Adresseneingabe (Spur 0400): ae_tab, 64 Zellen, die Eingabeadresse wird ODER-verknuepft ----
; Die Quelle (BIS-2.2.12.3) nennt fuer das Minimalprogramm samt Konstantenspur und Ansprungprogramm die Plaetze
; 40 bis 437. Die Tabelle liegt daher auf 0400, nicht im Block 0000 bis 0337. Benutzt werden nur die Zellen
; fuer die Ziffern 0 bis 7 (Offset 0 bis 7), 8 und 9 (Offset 010 und 011, Haltmarke), ZR (Offset 012) und den
; Punkt (Offset 033, zwei Zellen: 0433 wird als Befehl ausgefuehrt, danach 0434).
                equ     0400
ae_tab:         dw      0               ; Ziffer 0
                dw      0100            ; Ziffer 1 (1 * 0100)
                dw      0200            ; Ziffer 2
                dw      0300            ; Ziffer 3
                dw      0400            ; Ziffer 4
                dw      0500            ; Ziffer 5
                dw      0600            ; Ziffer 6
                dw      0700            ; Ziffer 7
ae_pois:        dw      010000000000    ; Ziffer 8: 2 hoch 30, Haltmarke (keine Oktalziffer)
                dw      010000000000    ; Ziffer 9: 2 hoch 30, Haltmarke
ae_zr:          000     kz_neu          ; ZR (Offset 012): Sprung zum Neustart der Kennzeicheneingabe (neues K1); auch Konstante fuer kz_xr (kz_lq)
                equ     0433
                211     ae_sv           ; Punkt (Offset 033): AC := Konstante
                000     ae_rs           ; Rueckkehr zum Aufrufer, AC = Konstante
ende:           end
ac7777:         abs     07777           ; Transportzelle fuer den AC (HGUE E), absolut
; Register (feste Arbeitszellen, absolut; Vorgabe des Projektinhabers). Die Register haben keine feste Verwendung; jeder
; Programmteil nennt bei sich, wofuer er sie benutzt. R1 ist beim Aufruf der Ausgabeunterprogramme die Uebergabezelle fuer
; das auszugebende Wort (BIS-2.2.10). Die Register liegen im Systembereich, nicht im Programmbereich.
r1:             abs     07773           ; Register R1 (Ausgabe: Uebergabezelle des auszugebenden Wortes)
r2:             abs     07776           ; Register R2
r3:             abs     07774           ; Register R3
; Arbeitszellen 7554 bis 7563 (von allen Teilen des Minimalprogramms benutzbar, Angabe des Projektinhabers)
okt_z:          abs     07554           ; Triadendruck: Zaehler (Einsen, wird nach links geschoben)
okt_rs:         abs     07555           ; Triadendruck: Rueckkehrbefehl
bd_rs:          abs     07556           ; Befehlsdruck: Rueckkehrbefehl
ad_rs:          abs     07557           ; Adressendruck: Rueckkehrbefehl
ad_sv:          abs     07560           ; Adressendruck: Sicherung von R1
ae_rs:          abs     07561           ; Adresseneingabe: Rueckkehrbefehl
ae_sv:          abs     07562           ; Adresseneingabe: Konstante (Sicherung des AC)
ae_z:           abs     07563           ; Adresseneingabe: Ziffernzaehler
; Nullspur 7640 bis 7677 (nur Nullen, Festlegung F1): Anfaenge der Nullzellenketten fuer die W-Befehle 616
nullspur:       abs     07640           ; Anfang der Nullspur (Gruppenbefehl 441: alle 32 Zellen := 0)
nz_12:          abs     07644           ; Position 24: 12 Zellen bis Position 37 (Befehlsdruck, Adressendruck)
nz_20:          abs     07674           ; Position 14: 20 Zellen bis Position 37 (Wortaufbau kz_wr: 217 = 1 Bit, 616 = 20 Bit)
; Arbeitszellen im Arbeitsbereich 7600 bis 7777 (Spuren 7600, 7640, 7700, 7740)
dr_rs:          abs     07600           ; Druck von BZ und AC: Fortsetzungsbefehl 000 b (Ziel des Sprungs 000 dr_rs am Ende)
; Arbeitszellen der Kennzeicheneingabe (Arbeitsbereich 7600 bis 7777)
kz_tab:         abs     07600           ; Eingabetabelle (64 Zellen 7600 bis 7677, Offset = Eingabeadresse); 7600 ist zugleich dr_rs
kz_rs:          abs     07700           ; Kennzeicheneingabe: Rueckkehrbefehl
kz_k1:          abs     07701           ; Kennzeicheneingabe: K1 * 01000 (Ergebnis fuer den Aufrufer)
kz_k2:          abs     07702           ; Kennzeicheneingabe: K2 * 01000 (Ergebnis fuer den Aufrufer)
kz_kw:          abs     07703           ; Kennzeicheneingabe: Wortsumme
kz_z:           abs     07704           ; Kennzeicheneingabe: Ziffernzaehler
kz_xw:          abs     07705           ; Kennzeicheneingabe: zur Laufzeit gebauter Transportbefehl (Ziffernzelle bzw. Leitadressenzelle), Ausfuehrung mit 000 kz_xw
kz_xr:          abs     07706           ; Kennzeicheneingabe: Folgezelle von kz_xw, Sprungbefehl 000 ziel (kz_g bzw. kz_neu), vor der Ausfuehrung gesetzt
kz_v:           abs     07707           ; Kennzeicheneingabe: Zuschlag (Leitadresse K2) beim Wortende
la_tab:         abs     07724           ; Leitadressentabelle (10 Zellen): 7724 Hauptleitadresse (K2 = 1), 7725 bis 7734 (K2 = 2 bis 9), 7735 Relativadresse (K2 = 0)
