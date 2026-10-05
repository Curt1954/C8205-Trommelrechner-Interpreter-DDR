; bsp_6_3_1_betragsbildung.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_3_1_betragsbildung.txt
; #DOK-0001 Gleitkommazahlen (Programmieranleitung 6.3): Betragsbildung (6.3.1), Beispiel des Buches z=-16 = -0,5*2^5 (1 100101 100...0)
; #DOK-0001 Format: z0 = Vorzeichen der Mantisse, z1...z6 = Maschinenexponent e'=e+32, z7...z32 = Mantissenbetrag m1...m26 (0,5 <= |m| < 1);
;   z = m*2^e
; #DOK-0001 Programm wie im Buch ab Zelle 3000; x=<7777>; 7777 215 bildet Vl(x), 3002 002 schiebt zurueck: |x| mit z0=0
; #DOK-0001 erwartet <AC> = |x| = 22600000000 (oktal) = +0.5*2^5
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.3.1
                equ     03000
m3000:          215     d7777                    ; 7777 215 ; <AC>:=Vl(x), Linksverschiebung (Vorzeichen z0 faellt heraus)
                002     m3002                    ; 3002 002 ; <AC>:=|x|, Rechtsverschiebung (Sprung zur naechsten Zelle)
m3002:          020     03000                    ; 3000 020 ; unbedingter Stopp
                equ     07777
d7777:          dw      062600000000             ; x = -0.5*2^5

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3003 AC=22600000000 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 7777: 62600000000
;
