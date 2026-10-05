; 0015-030.asm  -  symbolisches Assemblerprogramm zu Testdatei 0015-030.txt
; #DOK-0015 Test Ausgabebefehl
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                equ     01
                000     m7240
                equ     07240
m7240:          030     04500
                030     02720
                030     00570
                030     01210
                030     01170
                030     00610
                030     00700
                030     01110
                030     00320
                030     00010
                030     00310
                030     00070
                030     00020
                164     00015
                020     0
; Beginn Datenbereich

                end

; Tastenfolge:
; H G M-drücken E M-loslassen R
;
; Prüfungen:
; BZ=7257 AC=00000002000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
;
