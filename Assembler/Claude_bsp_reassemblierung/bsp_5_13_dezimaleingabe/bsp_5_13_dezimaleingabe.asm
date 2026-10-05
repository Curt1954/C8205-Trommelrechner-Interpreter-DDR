; bsp_5_13_dezimaleingabe.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_13_dezimaleingabe.txt
; #DOK-0001 Dezimaleingabe (Programmieranleitung 5.13), Eingabe der Dezimalzahl 12 mit Schlusszeichen Punkt
; #DOK-0001 Eingabe im R 300-Code ueber Leser 1 (K1); Ziffer d: <AC>:=<AC>+d, dann <AC>:=10*<AC> (W-Befehl 7706 644 und 7706 214,
;   Arbeitsspur 7700); ZWR loescht den AC; Punkt liefert <AC>:=<7706>
; #DOK-0001 erwartet <AC> = 00000000014 (oktal)
; #SPEI-0001 3000-3016
; #SPEI-0001 3033-3035
; #SPEI-0001 7706-7706
; #SPEI-0001 7723-7723
; --leser1 virtuelle_Geraete/Leser1/bsp_5_13_lochstreifen.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Startstück (nicht Teil des Buchprogramms): Anwahl K1 (Leser 1), dann Sprung zum Programmanfang 3012
m0000:          000     m2000                    ; Sprung zum Startstück
                equ     02000
m2000:          030     04600                    ; Anwahl Kanal K1 (Leser 1)
                000     m3012                    ; Sprung zum Programmanfang (Löschen des Akkumulators)

; Programm 5.13
; Konstanten für die einzelnen Dezimalziffern
                equ     03000
                000     m0000                    ; 0000 0000 000
                dw      01                       ; 0000 0000 001
                dw      02                       ; 0000 0000 002
                dw      03                       ; 0000 0000 003
                dw      04                       ; 0000 0000 004
                dw      05                       ; 0000 0000 005
                dw      06                       ; 0000 0000 006
                dw      07                       ; 0000 0000 007
                010     0                        ; 0000 0000 010
                dw      011                      ; 0000 0000 011
m3012:          001     m3013                    ; 3013 001 ; Fortsetzung nach Eingabe von ZWR, <AC>:=0
m3013:          010     03000                    ; 3000 010 ; E (0|1|2|3|4|5|6|7|8|9|ZWR|.)
                644     d7706                    ; 7706 644 ; zweimalige Linksverschiebung, <AC>:=4*<AC>, <7706>:=<AC>
                214     d7706                    ; 7706 214 ; <AC>:=10*<AC>
                000     m3013                    ; 3013 000 ; Sprung zur Eingabe
                equ     03033
                211     d7706                    ; 7706 211 ; Fortsetzung nach Eingabe von ".", <AC>:=eingegebene Dezimalzahl
; Programmfortsetzung (im Buch 3034 ohne Inhalt), hier mit Debug und Stopp
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stopp

                end
d7706:          abs     07706

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3036 AC=00000000014 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 00000000000
; 3011: 00000000011
; 3012: 00003013001
; 3033: 00007706211
; 7706: 00000000014
; 7723: 00000000030
;
