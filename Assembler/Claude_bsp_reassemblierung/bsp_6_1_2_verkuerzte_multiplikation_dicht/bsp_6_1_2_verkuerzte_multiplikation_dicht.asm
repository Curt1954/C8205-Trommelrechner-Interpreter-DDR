; bsp_6_1_2_verkuerzte_multiplikation_dicht.asm  -  symbolisches Assemblerprogramm zu Testdatei
;   bsp_6_1_2_verkuerzte_multiplikation_dicht.txt
; #DOK-0001 Zahlwort Festkomma vorn: verkuerzte Multiplikation positiver Zahlen (Programmieranleitung 6.1.2), x und a mit voller Stellenzahl
; #DOK-0001 Programm wie im Buch ab Zelle 3000; x=<3007>, a=<3010>, Maske <3011>=3777 7777 777, Arbeitsspur 7700; der Verfahrensfehler ist
;   stets negativ und kleiner als 2^-27
; #DOK-0001 erwartet <AC> = x*a = 25761027721 (oktal), Verfahrensfehler stets negativ, kleiner als 2^-27
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.1.2; Arbeitsspur 7700 (die Zellen der Spur werden vom Gruppenbefehl beschrieben)
                equ     03000
m3000:          211     d3007                    ; 3007 211 ; <AC>:=x
                440     d7700                    ; 7700 440 ; Speicherung von x in alle Zellen der Arbeitsspur
                211     d3011                    ; 3011 211 ; <AC>:=3777 7777 777
                462     d7700                    ; 7700 462 ; höchste Bits von x als mögliche Teilprodukte ausblenden
                211     d3010                    ; 3010 211 ; <AC>:=a
                432     d7700                    ; 7700 432 ; Abbau des Faktors a und gleichzeitig Aufbau des Produkts in AC
                020     03000                    ; 3000 020 ; unbedingter Stopp
d3007:          dw      035762104535             ; x
d3010:          dw      027351646213             ; a
d3011:          dw      037777777777             ; Maske zur Erzeugung der Teilprodukte

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3007 AC=25761027721 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3007: 35762104535
; 3010: 27351646213
; 3011: 37777777777
; 7700: 00000000000
; 7715: 20000000000
; 7732: 30000000000
; 7707: 34000000000
; 7724: 34000000000
; 7701: 35000000000
; 7716: 35400000000
; 7733: 35600000000
; 7710: 35700000000
; 7725: 35740000000
; 7702: 35760000000
; 7717: 35760000000
; 7734: 35760000000
; 7711: 35762000000
; 7726: 35762000000
; 7703: 35762000000
; 7720: 35762000000
; 7735: 35762100000
; 7712: 35762100000
; 7727: 35762100000
; 7704: 35762100000
; 7721: 35762104000
; 7736: 35762104000
; 7713: 35762104000
; 7730: 35762104400
; 7705: 35762104400
; 7722: 35762104500
; 7737: 35762104500
; 7714: 35762104520
; 7731: 35762104530
; 7706: 35762104534
; 7723: 35762104534
;
