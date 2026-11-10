; kat5eingabe_voll.asm - KAT5EINGABE: Eingabeende durch das volle Wort (5 Zeichen), drei Aufrufe nacheinander, R1 jeweils um 01000 weiter
;   Eingabedatei: a b c d e | f g h i j | k l m n o   (die Zeichen nach dem Eingabeende bleiben fuer den naechsten Aufruf stehen)
;   Aufruf 1: liest a bis e -> Wort abcde. Aufruf 2: liest f bis j -> Wort fghij. Aufruf 3: liest k bis o -> Wort klmno.
;   Kein Endekennzeichen, kein Endwort: ein volles Wort ist ein fertiges Wort, das UP liest nie ueber das 5. Zeichen hinaus.
;#DOK-0001 KAT5EINGABE: Eingabeende durch das volle Wort (drei Aufrufe mit je 5 Zeichen)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat5eingabe_voll.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      3                    ; Zellen 0001 bis 0003: drei Worte (Aufruf 1 bis 3)
kbein:          dw      0                    ; Zelle 0004: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr:           da      text                 ; Zelle 0005: Adresse des ersten Wortes (Adressfeld)
rkbe:           da      kbein                ; Zelle 0006: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                211     radr                 ; AC := Adresse des ersten Wortes
                240     r1                   ; R1 := Adresse des ersten Wortes
                025     eingabe              ; Aufruf 1 KAT5EINGABE: a b c d e
                211     r1                   ; AC := Adresse des ersten Wortes
                210     #01000               ; plus eine Adresseinheit: zweites Wort
                240     r1                   ; R1 := Adresse des zweiten Wortes
                025     eingabe              ; Aufruf 2 KAT5EINGABE: f g h i j
                211     r1                   ; AC := Adresse des zweiten Wortes
                210     #01000               ; plus eine Adresseinheit: drittes Wort
                240     r1                   ; R1 := Adresse des dritten Wortes
                025     eingabe              ; Aufruf 3 KAT5EINGABE: k l m n o
                020     0                    ; Halt

; ---- UP KAT5EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT5EINGABE                  ; Unterprogramm: liest ein Wort ueber K0 und legt es auf R1 ab
                end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: a bis o = 021 bis 037; erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0):
; Aufruf 1: a b c d e -> 0 21 22 23 24 25 = 02122232425.   Aufruf 2: f g h i j -> 0 26 27 30 31 32 = 02627303132.   Aufruf 3: k l m n o -> 0 33 34 35 36 37 = 03334353637.
; Zellen: text 0001 bis 0003, kbein 0004, radr 0005, rkbe 0006, Hauptprogramm 0007 bis 0025 (Halt) -> BZ = 0026.
; R1 = drittes Wort = 0003 * 01000 = 03000, R3 = 0004 * 01000 = 04000, AC = zuletzt gespeichertes Wort = 03334353637.
;#PRUEFE-START
; BZ=0026 AC=03334353637
; 0001: 02122232425   # Aufruf 1: a b c d e
; 0002: 02627303132   # Aufruf 2: f g h i j
; 0003: 03334353637   # Aufruf 3: k l m n o
; 0004: 00000000000   # kbein
; 7773: 00000003000   # R1: Adresse des dritten Wortes
; 7774: 00000004000   # R3 unveraendert
;#PRUEFE-ENDE
