; bsp_6_1_3_quadrierung_dicht.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_1_3_quadrierung_dicht.txt
; #DOK-0001 Zahlwort Festkomma vorn: Quadrierung einer positiven Zahl (Programmieranleitung 6.1.3), x mit voller Stellenzahl; das Ergebnis
;   weicht durch die Rundung um weniger als eine Einheit der letzten Stelle vom exakten Quadrat ab
; #DOK-0001 Programm nach 6.1.1 ab Zelle 3000; x=<3006>, Konstante 2^-1 in <3007>, Arbeitsspur 7700; 7700 440 Transport von x auf alle
;   Zellen, 7700 472 Teilprodukte, 7700 412 Summierung
; #DOK-0001 Das Buch nennt im Programm die Adressen 3005/3006 (Laden von x und der Konstanten) und die Summierung 7700 212; das sind
;   Satzfehler. Gemeint sind 3006 211, 3007 211 und 7700 412 (wie in 6.1.1).
; #DOK-0001 erwartet <AC> = x*x = 34046006623 (oktal)
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.1.3; Arbeitsspur 7700 (die Zellen der Spur werden vom Gruppenbefehl beschrieben)
                equ     03000
m3000:          211     d3006                    ; 3006 211 ; <AC>:=x
                440     d7700                    ; 7700 440 ; Transport von x auf alle Zellen einer Spur
                472     d7700                    ; 7700 472 ; Bildung der Teilprodukte P(i)=x(i)*x fuer i=32,...,1
                211     d3007                    ; 3007 211 ; <AC>:=2^-1 (Rundung des Resultats)
                412     d7700                    ; 7700 412 ; <AC>:=x*x, Summierung der Teilprodukte
                020     03000                    ; 3000 020 ; unbedingter Stopp
d3006:          dw      035762104535             ; x
d3007:          dw      020000000000             ; Konstante 2000 0000 000 (= 2^-1)

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3006 AC=34046006623 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3006: 35762104535
; 3007: 20000000000
; 7700: 35762104535
; 7715: 00000000000
; 7732: 35762104535
; 7707: 35762104535
; 7724: 35762104535
; 7701: 00000000000
; 7716: 35762104535
; 7733: 00000000000
; 7710: 35762104535
; 7725: 00000000000
; 7702: 00000000000
; 7717: 35762104535
; 7734: 00000000000
; 7711: 00000000000
; 7726: 00000000000
; 7703: 35762104535
; 7720: 00000000000
; 7735: 00000000000
; 7712: 00000000000
; 7727: 35762104535
; 7704: 00000000000
; 7721: 00000000000
; 7736: 35762104535
; 7713: 35762104535
; 7730: 35762104535
; 7705: 35762104535
; 7722: 35762104535
; 7737: 35762104535
; 7714: 00000000000
; 7731: 35762104535
; 7706: 35762104535
; 7723: 35762104535
;
