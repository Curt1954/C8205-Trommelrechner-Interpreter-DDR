; bsp_5_17_oktaldruck.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_17_oktaldruck.txt
; #DOK-0001 Oktaldruck (Programmieranleitung 5.17, Abb. 26): Inhalt der Zelle 7777 in Triadenschreibweise drucken, <7777> = 70123456701
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe
; #SPEI-0001 3020-3020
; #SPEI-0001 7777-7777
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Startstück (nicht Teil des Buchprogramms): Das Schreibwerk muss vor dem Druck auf Kleinbuchstaben (KB) stehen;
; sein Zustand nach dem Einschalten ist zufällig. Daher Anwahl K2, Umschaltung auf KB, dann Sprung zum Programmanfang 3000.
                000     m3100                    ; Sprung zum Startstück
                equ     03100
m3100:          030     04500                    ; Anwahl Kanal K2 (Schreibwerk-Ausgabe)
                030     01170                    ; Umschaltung auf KB
                000     m3000                    ; Sprung zum Programmanfang

; Zu druckender Wert (Aufgabe: Inhalt der Zelle a = 7777), Oktalziffern 7 0 1 2 3 4 5 6 7 0 1
                equ     07777
d7777:          dw      070123456701             ; Zelle a = 7777, Testwert

; Programm 5.17 (Abb. 26), Spur 3000; Arbeitsspur 7700
                equ     03000
m3000:          030     04500                    ; Programmanfang, Anwahl 2
                211     d3027                    ; <AC>:=0000 0000 001
                000     m3032                    ; Sprung nach 3032
m3003:          217     d7777                    ; <AC>:=Vzl2(a), 1. Teil
                006     m3015                    ; <AC>:=Vzl2(a), 2. Teil
                030     00010                    ; Druck "1"
                030     00260                    ; Druck "6"
m3007:          520     d7721                    ; GX-Subtraktion zur Bestimmung der zu druckenden Oktalziffer
d3010:          dw      077740000000             ; Konstante
                311     d3020                    ; <AC>:=z; Vergleicher 3, falls z=0
                170     m3036                    ; Prüfen, ob z=0
                004     m3034                    ; z:=Vl(z) (im Listing als "z:=z+1" gedruckt, Ablaufplan: z:=Vl(z))
                030     00040                    ; Druck "4"
m3015:          006     m3024
; 3016: frei
                equ     03017
d3017:          dw      07                       ; Konstante zum Ausblenden der letzten Triade
; 3020: Arbeitszelle für z
; 3021: frei
                equ     03022
                030     00020                    ; Druck "2"
                030     00070                    ; Druck "7"
m3024:          240     d7777                    ; a:=Vzl3(a)
                200     d3017                    ; <AC>:=t
                000     m3007
d3027:          dw      01                       ; Konstante
                030     00200                    ; Druck "0"
                030     00250                    ; Druck "5"
m3032:          440     d7724
                211     d3010                    ; <AC>:=7774 0000 000
m3034:          240     d3020                    ; <3020>:=z
                000     m3003
m3036:          020     03001                    ; unbedingter Stop; Programmende
                030     00230                    ; Druck "3"

                end
d3020:          abs     03020
d7721:          abs     07721
d7724:          abs     07724

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3037 AC=00000000000 AR=3001 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=1 V2=1
; 3020: 00000000000
; 7777: 70123456701
; --pruefe-sw-ausgabe bsp_5_17_oktaldruck-sw-ausgabe.txt
;
