; tk-001_US_H_M_R.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-001_US_H_M_R.txt
; #DOK-0001 Tastenfolge H G M R: nach G steht BR = 0000 000, M ergibt BR = 0000 025 (Sprung mit Rückkehrabsicht), R führt aus.
; #DOK-0002 Phase III gilt als abgelaufen (Originaldokumentation 4.3.2.3, Abb. 19): nur Resultatbehandlung, kein Sichern der
;   Rückkehradresse.
; #DOK-0003 Danach wird der nächste Befehl aus der Zelle AR = 0000 entnommen (Stopp 020 mit Adresse 0005): BZ = 0000 + 1, AR = 0005, AC
;   bleibt 0.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                020     00005                    ; Stopp 020 mit Adreßteil 0005

                end

; Tastenfolge:
; H G M R
;
; Prüfungen:
; BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00000005020
;
