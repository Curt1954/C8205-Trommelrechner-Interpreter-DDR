; tk-003_US_Ue_R.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-003_US_Ue_R.txt
; #DOK-0001 Tastenfolge H G Ü R: BR = 7777 240 (Transport ⟨7777⟩ := AC), R führt aus (Start bei Knoten 19).
; #DOK-0002 AC = 0 wird nach 7777 übertragen (vorbelegter Wert 555 wird überschrieben). Danach Phase I mit BZ = 0: Zelle 0000 (Stopp,
;   Adresse 0005): BZ = 0001, AR = 0005.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                020     00005                    ; Stopp 020 mit Adreßteil 0005
                equ     07777
                dw      0555                     ; wird durch den Transport mit AC=0 überschrieben

                end

; Tastenfolge:
; H G Ü R
;
; Prüfungen:
; BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00000005020
; 7777: 00000000000
;
