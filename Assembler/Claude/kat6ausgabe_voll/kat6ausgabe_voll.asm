; kat6ausgabe_voll.asm - Test KAT6AUSGABE: Text mit genau 5 Zeichen (Stoppbit z2 und z0 im vollen Wort), Text ueber mehrere volle Worte mit leerem Endwort (nur z0) und ein Text,
;                       der nur aus einem leeren Endwort besteht (gibt nichts aus). Kein Um. KB/GB, die Zustandszelle bleibt 0.
;#DOK-0001 KAT6AUSGABE: abcde / abcdefghij mit leerem Endwort / leerer Text
;#SPEI-0001 0001-0012
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat6ausgabe_voll
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat6ausgabe_voll-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Startadresse des Textes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat6    abcde                ; Zelle 0001: genau 5 Zeichen, z0 im selben Wort
text2:          dw      012524232221         ; Zelle 0002: abcde ohne z0, mit Stoppbit z2
                dw      014131302726         ; Zelle 0003: fghij ohne z0, mit Stoppbit z2
                dw      040000000001         ; Zelle 0004: leeres Endwort (nur z0 und Stoppbit in z32)
text3:          dw      040000000001         ; Zelle 0005: leerer Text (nur z0 und Stoppbit in z32)
radr1:          da      text1                ; Zelle 0006: Adresse von Text 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0007: Adresse von Text 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0010: Adresse von Text 3 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0011: KB/GB-Zustand (0 = KB), bleibt 0
rkb:            da      kbaus                ; Zelle 0012: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Text 1
                240     r1                   ; R1 := Adresse von Text 1
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 1)
                211     radr2                ; AC := Adresse von Text 2
                240     r1                   ; R1 := Adresse von Text 2
                025     ausgabe              ; Aufruf (Text 2)
                211     radr3                ; AC := Adresse von Text 3
                240     r1                   ; R1 := Adresse von Text 3
                025     ausgabe              ; Aufruf (Text 3, leer)
                020     0                    ; Halt
ausgabe:        KAT6AUSGABE                  ; UP: Ausgabe eines kat6-Textes
ende:           end

; Sollwerte von Hand hergeleitet (a bis i = 021 bis 031, j = 041; erstes Zeichen rechts, 2 Oktalziffern je Zeichen, Stoppbit z2 = 010000000000 im vollen Wort, z0 = 040000000000):
; Text 1: e d c b a = 25 24 23 22 21 mit Stoppbit z2 und z0 -> 52524232221.
; Text 2: Wort 1 abcde = 12524232221; Wort 2: j i h g f = 41 31 30 27 26 mit Stoppbit z2 -> 14131302726; Wort 3: leeres Endwort = Stoppbit z32 und z0 = 40000000001.
; Text 3: nur das leere Endwort 40000000001. Alle drei Texte zusammen: "abcde" + "abcdefghij" + nichts.
; Zellen: text1 0001, text2 0002 bis 0004, text3 0005, radr1 0006, radr2 0007, radr3 0010, kbaus 0011, rkb 0012, Hauptprogramm 0013 bis 0027 (Halt 0027 -> BZ = 0030).
; R1 = Adresse von Text 3 = 0005 * 01000 = 05000; R3 = Adresse von kbaus = 0011 * 01000 = 011000; AC = letztes Textwort von Text 3 = 40000000001.
;#PRUEFE-START
; BZ=0030 AC=40000000001
; 0001: 52524232221
; 0002: 12524232221
; 0003: 14131302726
; 0004: 40000000001
; 0011: 00000000000
; 7773: 00000005000
; 7774: 00000011000
;#PRUEFE-ENDE
