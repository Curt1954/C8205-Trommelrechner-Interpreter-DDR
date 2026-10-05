; tk-008_US_Ue_E_Einzelschritt.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-008_US_Ue_E_Einzelschritt.txt
; #DOK-0001 Tastenfolge H G Ü E: BR = 7777 240. E (ohne M) führt Phase IV (⟨7777⟩ := AC = 0), Phase I, Phase II (Zelle 0000) und Phase III
;   aus und hält vor Knoten 19.
; #DOK-0002 Der Stop-Befehl 020 aus Zelle 0000 ist damit nur entnommen, nicht ausgeführt: BZ = 0001, AR = 0005. US bleibt 1 aus G (nur ST
;   oder R löschen es). Halt bei gesetztem H.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                020     00005                    ; Stopp 020 mit Adreßteil 0005
                equ     07777
                dw      0555                     ; wird mit AC=0 überschrieben

                end

; Tastenfolge:
; H G Ü E
;
; Prüfungen:
; BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00000005020
; 7777: 00000000000
;
