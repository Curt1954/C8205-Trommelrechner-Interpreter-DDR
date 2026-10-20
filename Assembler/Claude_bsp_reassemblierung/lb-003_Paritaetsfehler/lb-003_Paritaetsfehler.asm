; lb-003_Paritaetsfehler.asm  -  symbolisches Assemblerprogramm zu Testdatei lb-003_Paritaetsfehler.txt
; #DOK-0001 Lochbandeingabe: Anwahl K1, ein Eingabe-Halt, unbedingter Stopp
; --leser1 Test-virtuelleGeraete/Leser1/lb-003_paritaetsfehler.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     go
                equ     02000
go:             030     04600                    ; Anwahl Kanal 1 (Leser 1)
                010     0                        ; Eingabe-Halt 1. Art
                020     0                        ; unbedingter Stopp

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2002 AC=00000000000 AR=0000 FE=1 FUE=0 BS=0 US=0 E=1 A=0 V1=0 V2=0
;
