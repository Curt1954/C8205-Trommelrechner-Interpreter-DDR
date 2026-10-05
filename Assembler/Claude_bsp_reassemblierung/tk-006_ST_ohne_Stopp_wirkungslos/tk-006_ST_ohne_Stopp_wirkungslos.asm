; tk-006_ST_ohne_Stopp_wirkungslos.asm  -  symbolisches Assemblerprogramm zu Testdatei tk-006_ST_ohne_Stopp_wirkungslos.txt
; #DOK-0001 Tastenfolge ST R ohne vorheriges G: Der Rechner steht nicht im Stopp (US = 0, BS = 0), ST ist elektronisch verriegelt und ohne
;   Wirkung.
; #DOK-0002 Der Ablauf beginnt bei Konnektor B mit BZ = 0: Zelle 0000 (Stopp, Adresse 0005) wird entnommen, BZ = 0001, AR = 0005. Zelle 0000
;   bleibt unverändert (bei wirksamem ST würde der Transport sie mit AC = 0 überschreiben).
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start
                020     00005                    ; Stopp 020 mit Adreßteil 0005

                end

; Tastenfolge:
; ST R
;
; Prüfungen:
; BZ=0001 AC=00000000000 AR=0005 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 0000: 00000005020
;
