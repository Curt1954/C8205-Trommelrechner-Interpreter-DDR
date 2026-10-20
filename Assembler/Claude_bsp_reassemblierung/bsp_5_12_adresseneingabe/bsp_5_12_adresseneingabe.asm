; bsp_5_12_adresseneingabe.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_12_adresseneingabe.txt
; #DOK-0001 Adresseneingabe (Programmieranleitung 5.12), Eingabe der Adresse 1234 mit Schlusszeichen Punkt
; #DOK-0001 Eingabe im R 300-Code ueber Leser 1 (K1); 3000 3040 014 liest ein Zeichen, Ziffern werden mit 3 Linksverschiebungen aufgebaut,
;   ZWR (3052) loescht den AC, Punkt (3073) beendet die Eingabe mit einer Rechtsverschiebung
; #DOK-0001 erwartet <AC> = 00001234000
; #SPEI-0001 3000-3003
; #SPEI-0001 3040-3047
; #SPEI-0001 3052-3052
; #SPEI-0001 3073-3073
; --leser1 Test-virtuelleGeraete/Leser1/bsp_5_12_lochstreifen.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Startstück (nicht Teil des Buchprogramms): Anwahl K1 (Leser 1), dann Sprung zum Programmanfang 3052
m0000:          000     m2000                    ; Sprung zum Startstück
                equ     02000
m2000:          030     04600                    ; Anwahl Kanal K1 (Leser 1)
                000     m3052                    ; Sprung zum Programmanfang (Löschen des Akkumulators)

; Programm 5.12
                equ     03000
m3000:          014     m3040                    ; 3040 014 ; Eingabe eines Zeichens, Linksverschiebung
                004     m3002                    ; 3002 004 ; Linksverschiebung
m3002:          004     m3000                    ; 3000 004 ; Linksverschiebung
; Fortsetzung nach der Adresseneingabe (Programmende des Buchprogramms), hier mit Debug und Stopp
m3003:          164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stopp
; Konstanten zur Eingabe der acht verschiedenen Oktalziffern
                equ     03040
m3040:          000     m0000                    ; 0000 0000 000
                dw      0100                     ; 0000 0000 100
                dw      0200                     ; 0000 0000 200
                dw      0300                     ; 0000 0000 300
                dw      0400                     ; 0000 0000 400
                dw      0500                     ; 0000 0000 500
                dw      0600                     ; 0000 0000 600
                dw      0700                     ; 0000 0000 700
; Fortsetzung nach Eingabe von ZWR
                equ     03052
m3052:          001     m3000                    ; 3000 001 ; Löschen des Akkumulators, Programmanfang
; Fortsetzung nach Eingabe von "."
                equ     03073
                002     m3003                    ; 3003 002 ; Übergang zum Programmende, Rechtsverschiebung

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3005 AC=00001234000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 00003040014
; 3040: 00000000000
; 3047: 00000000700
; 3052: 00003000001
; 3073: 00003003002
;
