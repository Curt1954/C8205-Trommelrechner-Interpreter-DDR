; tk-004_US_Ue_Transport_AC.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-004_US_Ue_Transport_AC.txt
; #DOK-0001 Tastenfolge H G M+ E M- Ü R: Nach dem E unter M gilt BZ = 1, AR = 1, AC = 00000002000. Ü stellt AR = 7777 und OR = 240 ein.
; #DOK-0002 Ausgeführt wird BR = 7777 240: ⟨7777⟩ := AC = 00000002000, AC und danach der Befehlsablauf bei BZ = 1 unverändert.
; #DOK-0003 Zelle 0001 (Stopp, Adresse 0010) wird entnommen: BZ = 0002, AR = 0010.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                equ     01
                020     00010                    ; Stopp 020 mit Adreßteil 0010
                equ     07777
                dw      0555                     ; wird mit AC überschrieben

                end

; Tastenfolge:
; H G M+ E M- Ü R
;
; Prüfungen:
; BZ=0002 AC=00000002000 AR=0010 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0001: 00000010020
; 7777: 00000002000
;
