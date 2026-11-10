; kat5ausgabe_voll.asm - Test KAT5AUSGABE: Wort mit genau 5 Zeichen (kein Rest, kein Endekennzeichen), zwei volle Worte hintereinander (R1 um 01000 weiter)
;                       und das Wort 0, das nichts ausgibt. Kein Um. KB/GB, die Zustandszelle bleibt 0.
;#DOK-0001 KAT5AUSGABE: abcde / abcde fghij (zwei volle Worte) / Wort 0
;#SPEI-0001 0001-0011
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5ausgabe_voll
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5ausgabe_voll-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat5    abcde                ; Zelle 0001: genau 5 Zeichen
text2:          kat5    abcde                ; Zelle 0002: wieder abcde, erstes von zwei vollen Worten
                kat5    fghij                ; Zelle 0003: zweites volles Wort
text3:          dw      0                    ; Zelle 0004: Wort 0, gibt nichts aus
radr1:          da      text1                ; Zelle 0005: Adresse von Text 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0006: Adresse von Text 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0007: Adresse von Text 3 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0010: KB/GB-Zustand (0 = KB), bleibt 0
rkb:            da      kbaus                ; Zelle 0011: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Text 1
                240     r1                   ; R1 := Adresse von Text 1
                025     ausgabe              ; Aufruf KAT5AUSGABE (Text 1: abcde)
                211     radr2                ; AC := Adresse von Text 2
                240     r1                   ; R1 := Adresse von Text 2
                025     ausgabe              ; Aufruf (Text 2, Wort 1: abcde)
                211     r1                   ; AC := Adresse von Wort 1
                210     #01000               ; plus eine Adresseinheit: Wort 2
                240     r1                   ; R1 := Adresse von Wort 2
                025     ausgabe              ; Aufruf (Text 2, Wort 2: fghij)
                211     radr3                ; AC := Adresse von Text 3
                240     r1                   ; R1 := Adresse von Text 3
                025     ausgabe              ; Aufruf (Text 3: Wort 0, nichts)
                020     0                    ; Halt
ausgabe:        KAT5AUSGABE                  ; UP: Ausgabe eines kat5-Wortes
ende:           end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: a bis j = 021 bis 032; erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0):
; abcde: a 21, b 22, c 23, d 24, e 25 -> 0 21 22 23 24 25 = 02122232425.   fghij: f 26, g 27, h 30, i 31, j 32 -> 0 26 27 30 31 32 = 02627303132.
; Ausgabe: "abcde" + "abcde" + "fghij" + nichts = "abcdeabcdefghij" (unveraendert gegen das Format davor).
; Zellen: text1 0001, text2 0002/0003, text3 0004, radr1 0005, radr2 0006, radr3 0007, kbaus 0010, rkb 0011, Hauptprogramm 0012 bis 0032 (Halt, 17 Zellen) -> BZ = 0033.
; R1 = Adresse von Text 3 = 0004 * 01000 = 04000; R3 = Adresse von kbaus = 0010 * 01000 = 010000; AC = 0 (Wort 0 hat den Rest 0).
;#PRUEFE-START
; BZ=0033 AC=00000000000
; 0001: 02122232425   # Text 1: abcde
; 0002: 02122232425   # Text 2, Wort 1: abcde
; 0003: 02627303132   # Text 2, Wort 2: fghij
; 0004: 00000000000   # Text 3: Wort 0
; 0010: 00000000000   # kbaus
; 7773: 00000004000   # R1 = Adresse von Text 3
; 7774: 00000010000   # R3 = Adresse der Zustandszelle
;#PRUEFE-ENDE
