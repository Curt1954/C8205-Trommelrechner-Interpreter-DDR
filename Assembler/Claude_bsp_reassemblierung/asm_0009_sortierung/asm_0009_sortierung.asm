; asm_0009_sortierung.asm  -  symbolisches Assemblerprogramm zu Testdatei asm_0009_sortierung.txt
; #DOK-0001 Test Programmbeispiel 8: Sortierung von 4 Namen (Unterprogramm SORT + Hauptprogramm)
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                000     haupt
sort:           000     sstart                   ; Nr. 0000  Sprung über Parameter
                equ     04
sstart:         240     sruck                    ; Nr. 0003  Stellung Rücksprung
                001     sinit                    ; Nr. 0004  AC := 0, weiter bei sinit
sinit:          240     si                       ; Nr. 0005  i := 0
                210     eins                     ; Nr. 0006  AC := i + 1
skset:          240     sk                       ; Nr. 0007  k := i + 1
                210     sla                      ; Nr. 0010  AC := k + LA
                210     sbef                     ; Nr. 0011  Aufbau Transportbefehl 240 a(k+1)
                240     sb1                      ; Nr. 0012  ... nach sb1 (Nr. 0024)
                251     0                        ; Nr. 0013  AC := a(k+1)
                240     sh                       ; Nr. 0014  H := a(k+1)
                211     si                       ; Nr. 0015  AC := i
                210     sla                      ; Nr. 0016  AC := i + LA
                210     sbef                     ; Nr. 0017  Aufbau Transportbefehl 240 a(i+1)
                240     sb2                      ; Nr. 0020  ... nach sb2 (Nr. 0026)
                251     0                        ; Nr. 0021  AC := a(i+1)
                330     sh                       ; Nr. 0022  Vergleich a(i+1) mit H
                140     sknext                   ; Nr. 0023  a(i+1) <= H: nicht tauschen
                equ     026
                211     sh                       ; Nr. 0025  AC := H
                equ     030
sknext:         211     sk                       ; Nr. 0027  AC := k
                210     eins                     ; Nr. 0030  AC := k + 1
                330     sn                       ; Nr. 0031  Vergleich mit n
                170     sinext                   ; Nr. 0032  k + 1 = n: innere Schleife fertig
                000     skset                    ; Nr. 0033  sonst k := k + 1
sinext:         211     si                       ; Nr. 0034  AC := i
                210     zwei                     ; Nr. 0035  AC := i + 2
                330     sn                       ; Nr. 0036  Vergleich mit n
                170     sruck                    ; Nr. 0037  i + 2 = n: Sortierung beendet, Rücksprung
                220     eins                     ; Nr. 0040  AC := i + 1
                000     sinit                    ; Nr. 0041  i := i + 1, weiter bei sinit
                equ     047
eins:           dw      01000                    ; Nr. 0046  1 Adresseneinheit
zwei:           dw      02000                    ; Nr. 0047  2 Adresseneinheiten
sbef:           dw      0240                     ; Nr. 0050  Konstante für Befehlsaufbau
haupt:          211     anz                      ; n = 4 Namen
                240     sn
                211     afeld                    ; Anfangsadresse des Feldes
                240     sla
                025     sort                     ; Sortierung aufrufen
                020     0                        ; Halt: Feld ist sortiert
anz:            dw      04000                    ; 4 Adresseneinheiten
afeld:          da      feld
feld:           dw      010021054460             ; HABERL
                dw      013371052070             ; KOREHN
                dw      013300654600             ; KLAUS
                dw      011206050000             ; IHLE

                end
sn:             abs     02
sla:            abs     03
sb1:            abs     025
sb2:            abs     027
sruck:          abs     043
si:             abs     044
sk:             abs     045
sh:             abs     046

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=0060 AC=00000004000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0
; 0062: 10021054460
; 0063: 11206050000
; 0064: 13300654600
; 0065: 13371052070
;
