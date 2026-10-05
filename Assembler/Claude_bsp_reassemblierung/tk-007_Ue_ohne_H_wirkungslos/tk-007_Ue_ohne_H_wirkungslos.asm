; tk-007_Ue_ohne_H_wirkungslos.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-007_Ue_ohne_H_wirkungslos.txt
; #DOK-0001 Tastenfolge Ü R ohne Schalter H: Ü wirkt nur bei gesetztem H und ist hier ohne Wirkung.
; #DOK-0002 Der Ablauf beginnt bei Konnektor B mit BZ = 0: Zelle 0000 (Stopp, Adresse 0005): BZ = 0001, AR = 0005. Zelle 7777 bleibt 555
;   (bei wirksamem Ü würde sie mit AC = 0 überschrieben).
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                020     00005                    ; Stopp 020 mit Adreßteil 0005
                equ     07777
                dw      0555                     ; darf unverändert bleiben

                end

; Tastenfolge:
; Ü R
;
; Prüfungen:
; BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00000005020
; 7777: 00000000555
;
