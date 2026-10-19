; C8205 BIS - Baustein B 1.1/8 "Minimalprogramm" (8-Kanal-Ausfuehrung, R 300-Code)
;
```
Die Ziffern werden nicht angesprungen. Der Sprung steckt im Gruppenbefehl 520 (GX-Subtraktion) an Zelle 0107. 

1. spa und dto sind keine Maschinenbefehle

Beide sind Assembleranweisungen:

spa 05 setzt den Zuordnungszähler auf Sektor 05 der Spur, hier also auf Zelle 0105.
dto 1 legt dort das Wort 0000 0010 030 ab. Das ist der Befehl 030 (Ausgabe) mit der Ausgabeadresse 0010, also das Zeichen „1“. dto fügt dabei keine Umschaltzeichen ein.

Die Zellen 0105, 0106, 0114, 0122, 0123, 0130, 0131 und 0137 sind also acht kleine Einzelbefehle „drucke Ziffer d“. Sie liegen verstreut in den freien Zellen der Spur 0100–0137. Im Listing steht dazwischen kein Sprung auf sie.

2. Die Auswahl macht 520 adr7721

Die Schleife arbeitet so:

Vorbereitung: 440 adr7724 schreibt AC = 1 in alle 32 Zellen der Spur 7700–7737.
Jeder Durchlauf schiebt R1 über 217, 006 und 006 um 3 Bit weiter. Im Trace verdoppelt sich AC bei jedem dieser Schritte.
200 konst_7 blendet die unterste Triade aus, AC enthält dann die Ziffer d (0 bis 7).
000 zu_gx springt nach 0107 zu 520 adr7721.
Der GX-Befehl subtrahiert nacheinander die Zellen der Spur ab Sektor 021, jeweils 1. Er bricht ab, sobald AC negativ wird, also nach d+1 Subtraktionen. Wie viele Schritte er macht, hängt damit von der Ziffer ab.
Nach dem Abbruch wird der nächste Befehl sofort entnommen. Die Spur kommt vom Befehlszähler (0100–0137), der Sektor vom Abbruchsektor. Der Zählerstand wirkt damit wie ein Index.

Wegen der Trommelverschachtelung (siehe C8205-Interpreter-Magnettrommel.md) schreitet jeder Subtraktionsschritt in der logischen Sektoradresse um +015 oktal fort. Die Zielsektoren der Ziffern ergeben sich deshalb als 030 + 15·d (mod 040):

Ziffer	0	1	2	3	4	5	6	7
Sektor	030	05	022	037	014	031	06	023

Das sind genau die spa-Werte in deinem Listing.

3. Warum es nicht in die Nachbarziffer weiterläuft

Der ausgewählte Befehl wird nur einmal ausgeführt, der Befehlszähler läuft nicht durch die dto-Zellen. Im Trace folgt auf BR=7721 520 der Befehl BR=0200 030 (die „0“). Danach steht BZ=0111, es geht also direkt bei 311 td_z weiter.

Der 520 ersetzt damit den Befehl in Zelle 0110, die gar nicht ausgeführt wird. Dort liegt die Konstante 077740000000, die nur als Datenwort für 211 konst_7774 dient. So bleiben 0105 und 0106 trotz Nachbarschaft getrennt: Wird „1“ gedruckt, wird „6“ nicht mitgedruckt.

Die Abläufe um den GX-Befehl stehen in C8205-Interpreter-Befehlsliste.md, Abschnitt 4.1.6.
```
 
                start
                000     haupt    ; Zelle 0000: Sprung zum Hauptprogramm
                
; ---- Befehlsdruck (Ansprungzelle 053), BIS-2.2.10.1 ----------------------------------------
; Druckt den Befehl in R1 als Adresse (4 Oktalziffern), Zwischenraum und Operationsteil (3 Oktalziffern),
; z. B. 0172 211. Die Wortstellen z0 bis z11 (die oberen 4 Triaden) werden nicht gedruckt.
triadendruck:   equ100  *
                240     td_rs   ; Rueckkehrbefehl sichern 
                211     konst_1  
                000     spur_speich
schleife:       217     adr7777      ; das auszugebende Wort als Übergabe in R1
                006     verschieben
                spa     05
                dto     1
                dto     6
zu_gx:          520     adr7721
konst_7774:     dw      077740000000
                311     td_z
                170     td_rs
                004     zn      ; bd_z := bd_z + 1
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
                211     konst_7774
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
td_rs:          abs     07741           ; Triadendruck: Rueckkehrbefehl
td_z:           abs     07720           ; Triadendruck z

;
;
haupt:          equ     02000
                030     04500
                dz      $inkb
                211     #64
                240     adr7777
                025     triadendruck
                020     0000

