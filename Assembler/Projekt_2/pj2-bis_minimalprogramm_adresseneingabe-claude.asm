; C8205 BIS - Adresseneingabe: Eingabe der Zeichen 0 bis 7 und Punkt (8-Kanal-Ausfuehrung, R 300-Code)
;
; Das Unterprogramm liest ueber den vom Aufrufer angewaehlten Kanal eine Oktalzahl mit bis zu 8 Ziffern.
; Schlusszeichen ist der Punkt. Aufruf: Der Aufrufer waehlt den Eingabekanal an (030 04600, Leser 1),
; dann 025 adresseneingabe. Rueckkehr mit der Konstanten im Akkumulator.
;
;   Eingabe        Ergebnis im AC (z0 bis z23, rechtsbuendig in den Oktalstellen t3 bis t10)
;   1234.          0000 1234 000
;   12345670.      1234 5670 000
;   .              0000 0000 000   (die Konstante Null braucht nur den Punkt)
;
;   Unterprogramm   Spur 0300 (Ansprungzelle 0300)
;   Hauptprogramm   02400
;   Eingabetabelle  Spur 0700 (64 Zellen, muss auf einer durch 64 teilbaren Adresse beginnen)
;
; Test: #STARTE 2400 und --leser1 <Lochstreifen>, z. B. Test-virtuelleGeraete/Leser1/pj2-bis_adresseneingabe_8stellig.txt.
; Zelle 0000 springt nach 2400.
;
; Zeichen:
;   0 bis 7   Ziffer, wird als Oktalstelle angehaengt
;   Punkt     Schlusszeichen, Rueckkehr zum Aufrufer
;   8, 9      keine Oktalziffer: HALT (Stopp im Befehl ae_halt)
;   ab der 9. Ziffer werden weitere Ziffern gelesen und verworfen, bis der Punkt kommt (auch 8 und 9)
;   andere Zeichen mit Sprung-Umstellung (z. B. ZR): Die Tabellenzelle ist 0 und fuehrt als Befehl den Sprung
;   nach 0000 (Hauptprogramm) aus; andere Zeichen ohne Sprung-Umstellung lesen den Wert 0 (wie die Ziffer 0).
;
; Verfahren (Eingabe-Halt mit Sprung-Umstellung): Der Eingabebefehl 010 ae_tab verknuepft die Eingabeadresse des
; gelesenen Zeichens mit ae_tab und liest die Tabellenzelle: Ziffern (ohne Sprung-Umstellung) liefern die Konstante
; d * 0100, die zum AC addiert wird. Dann drehen drei Sprungbefehle 006 den AC zyklisch um 3 Bit (eine Oktalstelle)
; nach links. Die Zellen fuer 8 und 9 enthalten 2 hoch 30 (ae_pois), das ist groesser als jeder gueltige AC in diesem
; Moment (hoechstens 7 Ziffern vor einer achten); der Vergleich 330 ae_pois mit dem Sprung 150 erkennt das.
; Ein Zaehler ae_z (7 Einsen, je Ziffer um 1 Bit nach links geschoben, wie im Druck) zaehlt die Ziffern: Nach der
; achten (ae_z = 0) geht es in die Schleife ae_ign, die jede weitere Ziffer mit Loeschen (011) einliest und
; verwirft. Der Akkumulator wird dazu in ae_sv gehalten; der Punkt holt ihn zurueck (Tabellenzelle ae_tab + 033).

                start
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm

; ---- Adresseneingabe: Unterprogramm auf Spur 0300 ------------------------------------------------
                equ     0300
adresseneingabe: 240    ae_rs           ; Rueckkehrbefehl sichern (Arbeitszelle 7756)
                211     ae_z0           ; Zaehleranfang: 7 Einsen
                240     ae_z            ; Zaehler setzen (Arbeitszelle 7760)
                211     ae_tab          ; AC := 0 (Zelle ae_tab, Ziffer 0, enthaelt 0)
                240     ae_sv           ; Konstante := 0 (Arbeitszelle 7757)
ae_loop:        010     ae_tab          ; Eingabe-Halt: Ziffer lesen, AC := AC + d * 0100; Punkt/ZR: Sprung in die Tabelle
                330     ae_pois         ; Vergleich AC mit 2 hoch 30: ab dort Ziffer 8 oder 9
                150     ae_halt         ; AC >= 2 hoch 30: Ziffer 8 oder 9, HALT
                006     ae_v2           ; Linksverschiebung (zyklisch) 1 von 3
ae_v2:          006     ae_v3           ; 2 von 3
ae_v3:          006     ae_zt           ; 3 von 3
ae_zt:          240     ae_sv           ; Konstante sichern (Arbeitszelle 7757)
                311     ae_z            ; AC := Zaehler; Vergleicher 3, falls Zaehler = 0
                170     ae_ign          ; Zaehler = 0: 8 Ziffern gelesen, weitere Ziffern verwerfen
                004     ae_zn           ; AC := Zaehler um 1 Bit nach links
ae_zn:          240     ae_z            ; Zaehler := Vl(Zaehler)
                211     ae_sv           ; AC := Konstante zurueck
                000     ae_loop         ; naechstes Zeichen
ae_z0:          dw      077400000000    ; Zaehleranfang: 7 Einsen (8 Ziffern)
ae_halt:        020     0               ; HALT: Ziffer 8 oder 9 (keine Oktalziffer)
ae_ign:         011     ae_tab          ; ab der 9. Ziffer: Zeichen lesen, AC loeschen (Ziffer wird verworfen); Punkt wie oben
                000     ae_ign          ; naechstes Zeichen

; ---- Eingabetabelle: Spur 0700, 64 Zellen, die Eingabeadresse wird ODER-verknuepft ---------------
; Benutzt werden nur die Zellen fuer die Ziffern 0 bis 7 (Offset 0 bis 7), 8 und 9 (Offset 010 und 011, Haltmarke)
; und den Punkt (Offset 033, zwei Zellen: 0733 wird als Befehl ausgefuehrt, danach 0734). Alle anderen Zellen der
; Spur bleiben null: Zeichen mit Sprung-Umstellung springen nach 0000, die uebrigen lesen den Wert 0.
                equ     0700
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
                equ     0733
                211     ae_sv           ; Punkt (Offset 033): AC := Konstante
                000     ae_rs           ; Rueckkehr zum Aufrufer, AC = Konstante

; ---- gemeinsame Adressen und Arbeitszellen -------------------------------------------------
ae_rs:          abs     07756           ; Adresseneingabe: Rueckkehrbefehl
ae_sv:          abs     07757           ; Adresseneingabe: Konstante (Sicherung des AC)
ae_z:           abs     07760           ; Adresseneingabe: Ziffernzaehler
r1:             abs     07773           ; Register R1

; ---- Hauptprogramm -------------------------------------------------------------------------------
haupt:          equ     02400
                030     04600           ; Kanal K1 (Leser 1) anwaehlen
                025     adresseneingabe ; Zeichen 0 bis 7 und Punkt einlesen
                240     r1              ; R1 := eingelesene Konstante
                020     0000            ; Stopp (AC = R1 = Konstante)
