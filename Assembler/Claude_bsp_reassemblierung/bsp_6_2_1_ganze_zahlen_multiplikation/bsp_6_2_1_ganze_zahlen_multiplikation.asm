; bsp_6_2_1_ganze_zahlen_multiplikation.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_2_1_ganze_zahlen_multiplikation.txt
; #DOK-0001 Ganze Festkommazahlen: Multiplikation positiver ganzer Zahlen (Programmieranleitung 6.2.1), Zahlenbeispiel des Buches b=101,
;   a=1011 (dual), a*b=110111 (dual; das Buch nennt im Text 10 111, die Tabelle zeigt richtig 0110111)
; #DOK-0001 Programm wie im Buch ab Zelle 3000; a=<3006>, b=<3007>, Arbeitsspur 7700; 7700 444 Transport von a, je Zelle um ein Bit nach
;   links verschoben (a(i)=a*2^i); 7700 472 Teilprodukte b(i)*a(i); 7700 410 Summierung
; #DOK-0001 erwartet <AC> = a*b = 11*5 = 55 (dezimal) = 00000000067 (oktal), das Produkt liegt im Zahlenbereich
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.2.1; Arbeitsspur 7700 (die Zellen der Spur werden vom Gruppenbefehl beschrieben)
                equ     03000
m3000:          211     d3006                    ; 3006 211 ; <AC>:=a
                444     d7700                    ; 7700 444 ; Transport von a, jeweils um ein Bit nach links verschoben, auf alle Zellen der
;                                                Spur
                211     d3007                    ; 3007 211 ; <AC>:=b
                472     d7700                    ; 7700 472 ; Bildung der Teilprodukte P(i)=b(32-i)*a(i)
                410     d7700                    ; 7700 410 ; <AC>:=a*b, Summierung der Teilprodukte
                020     03000                    ; 3000 020 ; unbedingter Stopp
d3006:          dw      013                      ; a
d3007:          dw      05                       ; b

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3006 AC=00000000067 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3006: 00000000013
; 3007: 00000000005
; 7700: 00000000013
; 7715: 00000000000
; 7732: 00000000054
; 7707: 00000000000
; 7724: 00000000000
; 7701: 00000000000
; 7716: 00000000000
; 7733: 00000000000
; 7710: 00000000000
; 7725: 00000000000
; 7702: 00000000000
; 7717: 00000000000
; 7734: 00000000000
; 7711: 00000000000
; 7726: 00000000000
; 7703: 00000000000
; 7720: 00000000000
; 7735: 00000000000
; 7712: 00000000000
; 7727: 00000000000
; 7704: 00000000000
; 7721: 00000000000
; 7736: 00000000000
; 7713: 00000000000
; 7730: 00000000000
; 7705: 00000000000
; 7722: 00000000000
; 7737: 00000000000
; 7714: 00000000000
; 7731: 00000000000
; 7706: 00000000000
; 7723: 00000000000
;
