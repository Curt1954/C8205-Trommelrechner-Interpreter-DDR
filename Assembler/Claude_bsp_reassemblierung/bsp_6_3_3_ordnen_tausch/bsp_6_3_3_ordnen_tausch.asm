; bsp_6_3_3_ordnen_tausch.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_6_3_3_ordnen_tausch.txt
; #DOK-0001 Gleitkommazahlen (Programmieranleitung 6.3): Ordnen eines Zahlenpaares nach dem Betrag (6.3.3), |b|>|a|, Tausch
; #DOK-0001 Format: z0 = Vorzeichen der Mantisse, z1...z6 = Maschinenexponent e'=e+32, z7...z32 = Mantissenbetrag m1...m26 (0,5 <= |m| < 1);
;   z = m*2^e
; #DOK-0001 Programm wie im Buch ab Zelle 3002; a=<3000>, b=<3001>; der Betragsvergleich |b|<=|a| ist als Ganzzahlvergleich der Betraege
;   moeglich (Exponent steht vor der Mantisse, z0=0 nach Rechtsverschiebung); der Wiederholungsbefehl 3006 642 wirkt auf die Zellen 3006 und
;   3023 (Sektor 06 und 23 liegen physisch nebeneinander)
; #DOK-0001 erwartet: Tausch (|b|>|a|); <3000> = 61740000000, <3001> = 21300000000, V1=0 V2=1, <AC> = 21300000000
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m3002                    ; Sprung zum Programmanfang der Aufgabe (Programm beginnt in Zelle 3002, 3000/3001
;                                                enthalten a und b)
; Programm 6.3.3; Arbeitszelle 3006, Betrag von a in 3023
                equ     03002
m3002:          215     d3000                    ; 3000 215 ; <AC>:=Vl(a)
                642     d3006                    ; 3006 642 ; W-Befehl (Zellen 3006 und 3023): <3006>:=Vl(a), <3023>:=|a|
                215     d3001                    ; 3001 215 ; <AC>:=Vl(b)
                002     m3007                    ; 3007 002 ; <AC>:=|b| (Sprung ueber die Arbeitszelle 3006)
                equ     03007
m3007:          330     d3023                    ; 3023 330 ; Vergleicher 1, falls |b|<=|a|
                140     m3017                    ; 3017 140 ; Pruefen, ob |b|<=|a| (Vergleichersprung 1)
                211     d3000                    ; 3000 211 ; <AC>:=a
                240     d3006                    ; 3006 240 ; <3006>:=a
                211     d3001                    ; 3001 211 ; <AC>:=b
                240     d3000                    ; 3000 240 ; <3000>:=b
                211     d3006                    ; 3006 211 ; <AC>:=a
                240     d3001                    ; 3001 240 ; <3001>:=a
m3017:          020     03002                    ; 3002 020 ; unbedingter Stopp
                equ     03000
d3000:          dw      021300000000             ; a = +0.75*2^2
d3001:          dw      061740000000             ; b = -0.875*2^3

                end
d3006:          abs     03006
d3023:          abs     03023

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3020 AC=21300000000 AR=3002 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=1
; 3000: 61740000000
; 3001: 21300000000
; 3006: 21300000000
; 3023: 21300000000
;
