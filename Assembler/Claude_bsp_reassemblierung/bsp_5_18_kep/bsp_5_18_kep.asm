; bsp_5_18_kep.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_18_kep.txt
; #DOK-0001 Kleines Eingabeprogramm KEP (Programmieranleitung 5.18, Abb. 27), Eingabe im R 300-Code ueber K0
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kep_eingabe.txt
; #SPEI-0001 3000-3004
; #SPEI-0001 7723-7724
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

m0000:          000     m0002                    ; Sprung zum Programmanfang des KEP
                equ     02
m0002:          000     m0022                    ; Programmanfang
; Erhoehung des Leitbefehls (Abschnitt "Leitbefehl erhoehen")
                equ     014
m0014:          211     m7723                    ; <AC>:=<7723>
                210     m0025                    ; <AC>:=<AC>+1°
m0016:          240     m7723                    ; <7723>:=<AC> = Leitbefehl
                001     m0030                    ; <AC>:=0, Sprung zur Eingabe
                000     m0000                    ; "0" Konstante im R 300-Code
                dw      040000000000             ; "1" Konstante im R 300-Code
m0022:          211     m0037                    ; <AC>:=0014 000
                240     d7724                    ; <7724>:=0014 000
                001     m0030                    ; "ZWR" im FS-Code, <AC>:=0
m0025:          000     m0001                    ; Konstante (Adresseneinheit 1°)
                000     m0000                    ; "0" Konstante im FS-Code
                dw      040000000000             ; "1" Konstante im FS-Code (Zeile im Listing verdruckt, ergaenzt)
m0030:          010     00020                    ; E (0|1|:|.|ZWR), Eingabe-Halt
                006     m0030                    ; <AC>:=Vzl(<AC>), Sprung zur Eingabe
                001     m0030                    ; "ZWR" im R 300-Code, <AC>:=0
                000     m7723                    ; "." im R 300-Code, Sprung zur Ausfuehrung des Leitbefehls
                000     m7723                    ; "." im FS-Code
                000     m0016                    ; ":" im R 300-Code, Leitbefehl speichern
                000     m0016                    ; ":" im FS-Code
m0037:          000     m0014                    ; Konstante 0014 000

                end
m0001:          abs     01
m7723:          abs     07723
d7724:          abs     07724

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3002 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3000: 00000001164
; 3001: 00000000020
; 3002: 00000000005
; 3003: 00000000010
; 3004: 52525252525
; 7723: 00003000000
; 7724: 00000014000
;
