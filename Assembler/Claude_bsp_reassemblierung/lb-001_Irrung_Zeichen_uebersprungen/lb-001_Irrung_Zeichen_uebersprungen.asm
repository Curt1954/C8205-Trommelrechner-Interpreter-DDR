; lb-001_Irrung_Zeichen_uebersprungen.asm  -  symbolisches Assemblerprogramm zu Testdatei lb-001_Irrung_Zeichen_uebersprungen.txt
; #DOK-0001 Lochbandeingabe: Anwahl K1, ein Eingabe-Halt, unbedingter Stopp
; --leser1 virtuelle_Geraete/Leser1/lb-001_irrung_zeichen_dann_1.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     go
                equ     02000
go:             030     04600                    ; Anwahl Kanal 1 (Leser 1)
                010     0                        ; Eingabe-Halt 1. Art
                020     0                        ; unbedingter Stopp
                equ     01
                dw      01                       ; Konstante 1: Inhalt der Zelle (Adreßteil 0000 v Eingabeadresse 01), den die Eingabe der
;                                                Ziffer 1 zum AC addiert

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2003 AC=00000000001 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
