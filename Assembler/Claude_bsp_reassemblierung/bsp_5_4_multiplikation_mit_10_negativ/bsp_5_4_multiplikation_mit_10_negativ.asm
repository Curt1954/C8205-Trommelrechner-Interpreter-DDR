; bsp_5_4_multiplikation_mit_10_negativ.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_4_multiplikation_mit_10_negativ.txt
; #DOK-0001 Multiplikation mit 10 (Programmieranleitung 5.4), a=-3 (dezimal, Zweierkomplement), erwartet AC=-30 dezimal
; #DOK-0001 3006 644: <AC>:=4a=-12, <3006>:=a=-3, <3023>:=2a=-6 (W-Befehl endet bei Sektor 23); 3006 214: <AC>:=2(4a+a)=10a=-30
; #SPEI-0001 3000-3003
; #SPEI-0001 3006-3006
; #SPEI-0001 3010-3010
; #SPEI-0001 3023-3023
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                211     d3010                    ; <AC>:=a (Vorbereitung: AC muss laut Aufgabe schon a enthalten)
                000     m3000                    ; Sprung zum Programmbeginn der Aufgabe in Zelle 3000
; Programm nach Programmieranleitung 5.4
                equ     03000
m3000:          644     d3006                    ; <AC>:=4a, <3006>:=a, <3023>:=2a
                214     d3006                    ; <AC>:=2(4a+a)=10a
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stop
; Beginn Datenbereich
                equ     03010
d3010:          dw      077777777775             ; a = -3 (Zweierkomplement, 33 Bit)

                end
d3006:          abs     03006

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3004 AC=77777777742 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3006: 77777777775
; 3010: 77777777775
; 3023: 77777777772
;
