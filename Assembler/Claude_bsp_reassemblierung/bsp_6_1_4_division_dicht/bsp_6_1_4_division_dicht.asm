; bsp_6_1_4_division_dicht.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_1_4_division_dicht.txt
; #DOK-0001 Zahlwort Festkomma vorn: Division positiver Zahlen (Programmieranleitung 6.1.4), a und b mit voller Stellenzahl
; #DOK-0001 Programm wie im Buch ab Zelle 3000; a=<3010>, b=<3011>, Maske <3012>=7777 7777 777, Arbeitsspur 7700; 7700 440 Transport von b/2
;   auf alle Zellen, 7700 454 Abschneiden der niedrigsten Bits von b, 7700 436 Divisionsvorgang (bedingte Addition/Subtraktion mit zyklischer
;   Linksverschiebung)
; #DOK-0001 Voraussetzung 0 <= a < b < 1; <AC> = 0 beim Start (3000 212 rechnet <AC>:=<AC>+b mit Rechtsverschiebung). Die Quotientenziffern
;   z1...z32 stehen nach 32 Schritten in z1...z32 des AC; z0 ist das zuletzt zyklisch verschobene Vorzeichen des Rests.
; #DOK-0001 erwartet <AC> = 71026033723 (oktal), Fehler gegenueber a/b kleiner als 2^-26
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.1.4; Arbeitsspur 7700 (die Zellen der Spur werden vom Gruppenbefehl beschrieben)
                equ     03000
m3000:          212     d3011                    ; 3011 212 ; <AC>:=2^-1*b
                440     d7700                    ; 7700 440 ; Transport von 2^-1*b auf alle Zellen der Arbeitsspur
                211     d3012                    ; 3012 211 ; <AC>:=7777 7777 777
                454     d7700                    ; 7700 454 ; niedrige Bits von b in den Zellen der Arbeitsspur loeschen
                221     d3010                    ; 3010 221 ; <AC>:=-a
                210     d3011                    ; 3011 210 ; <AC>:=b-a
                436     d7700                    ; 7700 436 ; <AC>:=+-q (Divisionsvorgang)
                020     03000                    ; 3000 020 ; unbedingter Stopp
d3010:          dw      027351646213             ; a
d3011:          dw      035762104535             ; b
d3012:          dw      037777777777             ; Maske zum Abschneiden der niedrigsten Bits von b

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3010 AC=71026033723 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3010: 27351646213
; 3011: 35762104535
; 3012: 37777777777
; 7700: 16771042256
; 7715: 16771042256
; 7732: 16771042254
; 7707: 16771042250
; 7724: 16771042240
; 7701: 16771042240
; 7716: 16771042200
; 7733: 16771042200
; 7710: 16771042000
; 7725: 16771042000
; 7702: 16771042000
; 7717: 16771040000
; 7734: 16771040000
; 7711: 16771040000
; 7726: 16771040000
; 7703: 16771000000
; 7720: 16771000000
; 7735: 16771000000
; 7712: 16771000000
; 7727: 16770000000
; 7704: 16770000000
; 7721: 16770000000
; 7736: 16760000000
; 7713: 16740000000
; 7730: 16700000000
; 7705: 16600000000
; 7722: 16400000000
; 7737: 16000000000
; 7714: 16000000000
; 7731: 14000000000
; 7706: 10000000000
; 7723: 00000000000
;
