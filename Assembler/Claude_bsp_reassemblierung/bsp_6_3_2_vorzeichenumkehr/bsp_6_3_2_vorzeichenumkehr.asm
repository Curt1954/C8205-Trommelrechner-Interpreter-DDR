; bsp_6_3_2_vorzeichenumkehr.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_3_2_vorzeichenumkehr.txt
; #DOK-0001 Gleitkommazahlen (Programmieranleitung 6.3): Vorzeichenumkehr (6.3.2), x=-16 (Ueberlauf bei der Addition wird durch den
;   Ueberlaufsprung geloescht)
; #DOK-0001 Format: z0 = Vorzeichen der Mantisse, z1...z6 = Maschinenexponent e'=e+32, z7...z32 = Mantissenbetrag m1...m26 (0,5 <= |m| < 1);
;   z = m*2^e
; #DOK-0001 Programm wie im Buch ab Zelle 3000; x=<7777>; Addition der Konstante 4000 0000 000 kehrt z0 um; bei x<0 entsteht dabei
;   Ueberlauf, der durch den Ueberlaufsprung 3004 geloescht wird; bei x=0 springt 3002 (Vergleicher 3) direkt zum Stopp
; #DOK-0001 erwartet <AC> = -x = 22600000000 (oktal) = +0.5*2^5; Vergleicher V1=1 V2=0, FUE=0
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3000                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3000)
; Programm 6.3.2
                equ     03000
m3000:          211     d7777                    ; 7777 211 ; <AC>:=x
                340     d7777                    ; 7777 340 ; Vergleicher 3, falls x=0 (Vgl 1: x<0, Vgl 2: x>0)
                170     m3005                    ; 3005 170 ; Vergleichersprung 3: Pruefen, ob x=0
                210     d3006                    ; 3006 210 ; <AC>:=x+4000 0000 000 (Vorzeichen z0 umgekehrt; Ueberlauf bei x<0)
                070     m3005                    ; 3005 070 ; Ueberlaufsprung (loescht den Ueberlauf, verhindert den Halt)
m3005:          020     03000                    ; 3000 020 ; unbedingter Stopp
d3006:          dw      040000000000             ; Konstante 4000 0000 000 (nur z0)
                equ     07777
d7777:          dw      062600000000             ; x = -0.5*2^5

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3006 AC=22600000000 AR=3000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=1 V2=0
; 3006: 40000000000
; 7777: 62600000000
;
