; kat5eingabe_wrzl.asm - KAT5EINGABE: Eingabeende mit WRZL (nicht gespeichert), drei Aufrufe nacheinander, R1 jeweils um 01000 weiter
;   Eingabedatei: a b c WRZL | a b c d e WRZL
;   Aufruf 1: Eingabe a b c WRZL            -> Wort abc (3 Zeichen, links, Fuellung 00 rechts), WRZL wird nicht gespeichert.
;   Aufruf 2: Eingabe a b c d e             -> volles Wort abcde, das UP endet nach dem 5. Zeichen; das folgende WRZL bleibt fuer den naechsten Aufruf stehen.
;   Aufruf 3: liest sofort WRZL             -> Wort 0 (kein Zeichen), ueberschreibt die vorbelegte Zelle.
;   Alle Aufrufe benutzen dieselbe Zustandszelle kbein (kein Umschaltzeichen: bleibt 0).
;#DOK-0001 KAT5EINGABE: Eingabe mit WRZL beendet (abc), volles Wort abcde, danach WRZL sofort (Wort 0)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat5eingabe_wrzl.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          db      1                    ; Zelle 0001: Wort fuer Aufruf 1
text2:          db      1                    ; Zelle 0002: Wort fuer Aufruf 2
text3:          dw      0777                 ; Zelle 0003: Wort fuer Aufruf 3, vorbelegt mit 0777 (muss durch Wort 0 ueberschrieben werden)
kbein:          dw      0                    ; Zelle 0004: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr:           da      text1                ; Zelle 0005: Adresse des ersten Wortes (Adressfeld)
rkbe:           da      kbein                ; Zelle 0006: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                211     radr                 ; AC := Adresse des ersten Wortes
                240     r1                   ; R1 := Adresse des ersten Wortes
                025     eingabe              ; Aufruf 1 KAT5EINGABE: a b c WRZL
                211     r1                   ; AC := Adresse des ersten Wortes
                210     #01000               ; plus eine Adresseinheit: zweites Wort
                240     r1                   ; R1 := Adresse des zweiten Wortes
                025     eingabe              ; Aufruf 2 KAT5EINGABE: a b c d e
                211     r1                   ; AC := Adresse des zweiten Wortes
                210     #01000               ; plus eine Adresseinheit: drittes Wort
                240     r1                   ; R1 := Adresse des dritten Wortes
                025     eingabe              ; Aufruf 3 KAT5EINGABE: WRZL sofort
                020     0                    ; Halt

; ---- UP KAT5EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT5EINGABE                  ; Unterprogramm: liest ein Wort ueber K0 und legt es auf R1 ab
                end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: a = 021, b = 022, c = 023, d = 024, e = 025; erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0):
; Aufruf 1: a b c WRZL -> a b c, Fuellung 00 rechts: 0 21 22 23 00 00 = 02122230000 (WRZL nicht gespeichert).
; Aufruf 2: a b c d e -> 0 21 22 23 24 25 = 02122232425 (voll, WRZL bleibt stehen).
; Aufruf 3: WRZL als erste Taste -> Wort 0 = 00000000000, die Vorbelegung 0777 ist ueberschrieben.
; Zellen: text1 0001, text2 0002, text3 0003, kbein 0004, radr 0005, rkbe 0006, Hauptprogramm 0007 bis 0025 (Halt) -> BZ = 0026.
; R1 = drittes Wort = 0003 * 01000 = 03000, R3 = 0004 * 01000 = 04000, AC = zuletzt gespeichertes Wort = 0.
;#PRUEFE-START
; BZ=0026 AC=00000000000
; 0001: 02122230000   # Aufruf 1: a b c (WRZL beendet)
; 0002: 02122232425   # Aufruf 2: a b c d e (voll)
; 0003: 00000000000   # Aufruf 3: Wort 0 (vorbelegte Zelle ueberschrieben)
; 0004: 00000000000   # kbein
; 7773: 00000003000   # R1: Adresse des dritten Wortes
; 7774: 00000004000   # R3 unveraendert
;#PRUEFE-ENDE
