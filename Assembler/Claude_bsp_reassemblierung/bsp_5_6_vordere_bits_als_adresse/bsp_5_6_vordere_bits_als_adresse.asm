; bsp_5_6_vordere_bits_als_adresse.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_6_vordere_bits_als_adresse.txt
; #DOK-0001 Vordere Bits als Adresse (Programmieranleitung 5.6): <3000> = a1a2a3a4 xxxx xxx, a1a2a3a4 = 4000 als Adresse interpretiert
; #DOK-0001 2001 3000 211: <AC>:=a1a2a3a4 xxxx xxx; 2002 3004 642: W-Befehl, 12 Zellen der Spur 3000 (Sektor 04 bis 23), je Zelle Transport
;   und Rechtsverschiebung, AC:=0000 a1a2a3a4 xxx
; #DOK-0001 2003 0000 251: R-Lesebefehl, <AC>:=<a1a2a3a4>, also <4000>; erwartet AC = 01234567012
; #SPEI-0001 3000-3037
; #SPEI-0001 4000-4000
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

                000     m2001                    ; Sprung zum Programmbeginn der Aufgabe in Zelle 2001
; Programm nach Programmieranleitung 5.6 (nach 2001 verlegt, weil der W-Befehl die Zellen 3004 ff. überschreibt)
                equ     02001
m2001:          211     d3000                    ; <AC>:=a1a2a3a4 xxxx xxx
                642     d3004                    ; <AC>:=0000 a1a2a3a4 xxx (W-Befehl bis Sektor 23)
                251     0                        ; <AC>:=<a1a2a3a4>
                164     00001                    ; DEBUG Nr. 0001
                020     0                        ; unbedingter Stop
; Datenbereich
                equ     03000
d3000:          dw      040002461357             ; a1a2a3a4 = 4000, xxxx xxx = 2461357
                equ     04000
                dw      01234567012              ; Zelle, auf die a1a2a3a4 zeigt

                end
d3004:          abs     03004

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=2006 AC=01234567012 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 40002461357
; 3004: 40002461357
; 3005: 01000051427
; 3006: 00020001230
; 3013: 04000246135
; 3014: 00100005142
; 3021: 20001230567
; 3022: 00400024613
; 3023: 00010000514
; 3030: 02000123056
; 3031: 00040002461
; 3036: 10000514273
; 3037: 00200012305
; 4000: 01234567012
;
