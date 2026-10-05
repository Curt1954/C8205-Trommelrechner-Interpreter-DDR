; bsp_5_3_ausblendung_adressstellen.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_3_ausblendung_adressstellen.txt
; #DOK-0001 Ausblendung der Adressstellen (Programmieranleitung 5.3): Adressteil a des Befehls in Zelle 3000 nach Zelle 3002
; #DOK-0001 Befehl in 3000: beliebige Bits 5252, a=5103, BAZ=523; Konstante in 3001: 0000 7777 000; erwartet <3002> = 0000 5103 000
; #SPEI-0001 3000-3002
; #SPEI-0001 3003-3007
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

m0000:          000     m3003                    ; Sprung zum Programmbeginn der Aufgabe in Zelle 3003
; Datenbereich der Aufgabe
                equ     03000
d3000:          dw      052525103523             ; Befehl: beliebige Bits 5252, Adressteil a=5103, BAZ=523
m3001:          000     m7777                    ; Konstante 0000 7777 000 (Maske fuer den Adressteil)
m3002:          000     m0000                    ; Ergebniszelle fuer a
; Programm nach Programmieranleitung 5.3
m3003:          211     d3000                    ; <AC>:=a BAZ (ganzes Wort der Zelle 3000)
                200     m3001                    ; <AC>:=a (Konjunktion mit Maske, Adressteil bleibt)
                240     m3002                    ; <3002>:=a
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stop

                end
m7777:          abs     07777

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3010 AC=00005103000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 52525103523
; 3001: 00007777000
; 3002: 00005103000
;
