; kat6eingabe_wrzl.asm - KAT6EINGABE: Eingabeende mit WRZL (nicht gespeichert), zwei Aufrufe nacheinander
;   Aufruf 1 (R2 = 12): Eingabe a b c WRZL            -> ein Wort abc mit Stoppbit und z0 (3 Zeichen), die anderen Worte des Bereichs bleiben 0.
;   Aufruf 2 (R2 = 12): Eingabe a b c d e WRZL        -> volles Wort abcde mit Stoppbit ohne z0, danach ein leeres Endwort (nur z0 und Stoppbit in z32), drittes Wort bleibt 0.
;   Beide Aufrufe benutzen dieselbe Zustandszelle kbein (kein Umschaltzeichen: bleibt 0).
;#DOK-0001 KAT6EINGABE: zwei Eingaben mit WRZL beendet (abc, dann abcde mit leerem Endwort)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat6eingabe_wrzl.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          db      3                    ; Zellen 0001 bis 0003: Bereich 1 fuer 12 Zeichen = 3 Worte
text2:          db      3                    ; Zellen 0004 bis 0006: Bereich 2 fuer 12 Zeichen = 3 Worte
kbein:          dw      0                    ; Zelle 0007: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr1:          da      text1                ; Zelle 0010: Adresse des Bereichs 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0011: Adresse des Bereichs 2 (Adressfeld)
rkbe:           da      kbein                ; Zelle 0012: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr1                ; AC := Adresse des Bereichs 1
                240     r1                   ; R1 := Adresse des Bereichs 1
                211     #12                  ; AC := hoechste Zeichenzahl
                240     r2                   ; R2 := 12
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                025     eingabe              ; Aufruf 1 KAT6EINGABE
                211     radr2                ; AC := Adresse des Bereichs 2
                240     r1                   ; R1 := Adresse des Bereichs 2
                025     eingabe              ; Aufruf 2 KAT6EINGABE (R2 und R3 unveraendert)
                020     0                    ; Halt

; ---- UP KAT6EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT6EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat6-Text ab R1 ab
                end

; Sollwerte von Hand hergeleitet (a = 021, b = 022, c = 023, d = 024, e = 025; erstes Zeichen rechts, Stoppbit links vom letzten Zeichen, z0 = 040000000000 am letzten Wort):
; Aufruf 1: a b c WRZL -> Wort 1 = c b a = 23 22 21, Stoppbit in Bit 18 (01000000), z0 -> 40001232221, Worte 2 und 3 bleiben 0 (die Trommel ist leer).
; Aufruf 2: a b c d e WRZL -> Wort 1 = e d c b a = 25 24 23 22 21 mit Stoppbit z2 (010000000000) = 12524232221 ohne z0 (volles Wort),
;           Wort 2 = leeres Endwort: nur das Stoppbit in z32 (1) und z0 = 40000000001, Wort 3 bleibt 0.
; R1 = text2 = 0004 * 01000, R2 = 12, R3 = 0007 * 01000, AC = -1.
;#PRUEFE-START
; BZ=0027 AC=77777777777
; 0001: 40001232221   # Aufruf 1, Wort 1: a b c mit Stoppbit und z0
; 0002: 00000000000   # Aufruf 1, Wort 2 unberuehrt
; 0003: 00000000000   # Aufruf 1, Wort 3 unberuehrt
; 0004: 12524232221   # Aufruf 2, Wort 1: a b c d e (voll, Stoppbit z2, ohne z0)
; 0005: 40000000001   # Aufruf 2, Wort 2: leeres Endwort (Stoppbit z32 und z0)
; 0006: 00000000000   # Aufruf 2, Wort 3 unberuehrt
; 0007: 00000000000   # kbein
; 7773: 00000004000   # R1: Adresse des Bereichs 2
; 7774: 00000007000   # R3 unveraendert
; 7776: 00000000014   # R2 unveraendert
;#PRUEFE-ENDE
