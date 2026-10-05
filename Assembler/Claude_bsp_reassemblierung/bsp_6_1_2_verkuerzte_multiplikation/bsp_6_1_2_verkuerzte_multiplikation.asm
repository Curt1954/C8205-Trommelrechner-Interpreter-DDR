; bsp_6_1_2_verkuerzte_multiplikation.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_1_2_verkuerzte_multiplikation.txt
; #DOK-0001 Zahlwort Festkomma vorn: verkuerzte Multiplikation positiver Zahlen (Programmieranleitung 6.1.2), Zahlenbeispiel des Buches
;   a=0,110101 x=0,111001 (dual, auf 33 Bit erweitert)
; #DOK-0001 Programm wie im Buch ab Zelle 3000; x=<3007>, a=<3010>, Maske <3011>=3777 7777 777, Arbeitsspur 7700; 7700 440 Speicherung von
;   x, 7700 462 Ausblendung der Teilprodukte, 7700 432 Abbau von a und Aufbau des Produkts
; #DOK-0001 erwartet <AC> = x*a = 27464000000 (oktal), Verfahrensfehler stets negativ, kleiner als 2^-27
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
d3007:          dw      034400000000             ; x
d3010:          dw      032400000000             ; a
d3011:          dw      037777777777             ; Maske zur Erzeugung der Teilprodukte

                end
d7700:          abs     07700

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3007 AC=27464000000 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3007: 34400000000
; 3010: 32400000000
; 3011: 37777777777
; 7700: 00000000000
; 7715: 20000000000
; 7732: 30000000000
; 7707: 34000000000
; 7724: 34000000000
; 7701: 34000000000
; 7716: 34400000000
; 7733: 34400000000
; 7710: 34400000000
; 7725: 34400000000
; 7702: 34400000000
; 7717: 34400000000
; 7734: 34400000000
; 7711: 34400000000
; 7726: 34400000000
; 7703: 34400000000
; 7720: 34400000000
; 7735: 34400000000
; 7712: 34400000000
; 7727: 34400000000
; 7704: 34400000000
; 7721: 34400000000
; 7736: 34400000000
; 7713: 34400000000
; 7730: 34400000000
; 7705: 34400000000
; 7722: 34400000000
; 7737: 34400000000
; 7714: 34400000000
; 7731: 34400000000
; 7706: 34400000000
; 7723: 34400000000
;
