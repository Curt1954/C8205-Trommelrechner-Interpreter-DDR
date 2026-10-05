; tk-005_US_ST_Transport_AC.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-005_US_ST_Transport_AC.txt
; #DOK-0001 Tastenfolge H G M+ E M- ST R: US ist durch G gesetzt, daher wirkt ST (OR := 240, AR bleibt 0001, US := 0). BZ = 1, AC =
;   00000002000.
; #DOK-0002 Ausgeführt wird BR = 0001 240: ⟨0001⟩ := AC = 00000002000. Phase I holt diese Zelle als Befehl: unbedingter Sprung nach 0002
;   (BAZ 000).
; #DOK-0003 Zelle 0002 (Stopp, Adresse 0020) wird entnommen: BZ = 0002 + 1 = 0003, AR = 0020. AC bleibt 00000002000.
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                equ     01
                020     00010                    ; wird durch den Transport mit AC überschrieben
                020     00020                    ; Stopp 020 mit Adreßteil 0020

                end

; Tastenfolge:
; H G M+ E M- ST R
;
; Prüfungen:
; BZ=0003 AC=00000002000 AR=0020 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0001: 00000002000
; 0002: 00000020020
;
