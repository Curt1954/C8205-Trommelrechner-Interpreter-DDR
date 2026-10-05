; tk-002_US_M_nach_E_AC_Linksverschiebung.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-002_US_M_nach_E_AC_Linksverschiebung.txt
; #DOK-0001 Tastenfolge H G M+ E M- M R: Nach G und einem E unter M gilt BZ = 1, AR = 1 und AC = 00000002000 (BZ+1 im Adreßfeld).
; #DOK-0002 Das M-Antippen stellt BR = 0001 025 auf. Phase III gilt als abgelaufen: nur die Resultatbehandlung (Linksverschiebung) wirkt auf
;   den AC: 2000 -> 4000.
; #DOK-0003 Die Sprungoperation (AC := AC v Vr<BZ>) darf NICHT ablaufen (sonst AC = 00000005000). Nächster Befehl aus Zelle AR = 0001 (Stopp
;   mit Adresse 0010): BZ = 0002, AR = 0010.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                equ     01
                020     00010                    ; Stopp 020 mit Adreßteil 0010

                end

; Tastenfolge:
; H G M+ E M- M R
;
; Prüfungen:
; BZ=0002 AC=00000004000 AR=0010 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0001: 00000010020
;
