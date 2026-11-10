; kat6eingabe_voll.asm - KAT6EINGABE: Eingabeende durch die hoechste Zeichenzahl R2, drei Aufrufe nacheinander
;   Eingabedatei: a b c d e f g | h i j k l | m n   (die Zeichen nach dem Eingabeende bleiben fuer den naechsten Aufruf stehen)
;   Aufruf 1 (R2 = 7): liest a bis g -> Wort abcde (Stoppbit z2), Wort fg mit Stoppbit und z0 (7 Zeichen, zwangsweises Ende).
;   Aufruf 2 (R2 = 5): liest h bis l -> ein volles Wort hijkl mit z0, kein zusaetzliches Endwort (Vielfaches von 5).
;   Aufruf 3 (R2 = 1): liest m -> ein Wort m mit z0, n bleibt ungelesen.
;#DOK-0001 KAT6EINGABE: Eingabeende durch die hoechste Zeichenzahl (7, 5 und 1 Zeichen)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat6eingabe_voll.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          db      2                    ; Zellen 0001 und 0002: Bereich 1 fuer 7 Zeichen = 2 Worte
text2:          db      1                    ; Zelle 0003: Bereich 2 fuer 5 Zeichen = 1 Wort
text3:          db      1                    ; Zelle 0004: Bereich 3 fuer 1 Zeichen = 1 Wort
kbein:          dw      0                    ; Zelle 0005: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr1:          da      text1                ; Zelle 0006: Adresse des Bereichs 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0007: Adresse des Bereichs 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0010: Adresse des Bereichs 3 (Adressfeld)
rkbe:           da      kbein                ; Zelle 0011: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                211     radr1                ; AC := Adresse des Bereichs 1
                240     r1                   ; R1 := Adresse des Bereichs 1
                211     #7                   ; AC := 7
                240     r2                   ; R2 := 7
                025     eingabe              ; Aufruf 1 KAT6EINGABE
                211     radr2                ; AC := Adresse des Bereichs 2
                240     r1                   ; R1 := Adresse des Bereichs 2
                211     #5                   ; AC := 5
                240     r2                   ; R2 := 5
                025     eingabe              ; Aufruf 2 KAT6EINGABE
                211     radr3                ; AC := Adresse des Bereichs 3
                240     r1                   ; R1 := Adresse des Bereichs 3
                211     #1                   ; AC := 1
                240     r2                   ; R2 := 1
                025     eingabe              ; Aufruf 3 KAT6EINGABE
                020     0                    ; Halt

; ---- UP KAT6EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT6EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat6-Text ab R1 ab
                end

; Sollwerte von Hand hergeleitet (a = 021 bis g = 027, h = 030, i = 031, j = 041, k = 042, l = 043, m = 044; erstes Zeichen rechts, Stoppbit links vom letzten Zeichen des Wortes, z0 = 040000000000 am letzten Wort):
; Aufruf 1 (R2 = 7): a b c d e f g -> Wort 1 = e d c b a = 25 24 23 22 21 mit Stoppbit z2 = 12524232221, Wort 2 = g f = 27 26, Stoppbit in Bit 12 (010000), z0 = 40000012726 (zwangsweises Ende nach dem 7. Zeichen).
; Aufruf 2 (R2 = 5): h i j k l      -> Wort = l k j i h = 43 42 41 31 30 mit Stoppbit z2 und z0 = 54342413130 (volles Wort ist das Endwort, kein leeres Wort dahinter).
; Aufruf 3 (R2 = 1): m              -> Wort = m = 44, Stoppbit in Bit 6 (0100), z0 = 40000000144; n wird nicht gelesen.
; R1 = text3 = 0004 * 01000, R2 = 1, R3 = 0005 * 01000, AC = -1.
;#PRUEFE-START
; BZ=0035 AC=77777777777
; 0001: 12524232221   # Aufruf 1, Wort 1: a b c d e
; 0002: 40000012726   # Aufruf 1, Wort 2: f g mit z0
; 0003: 54342413130   # Aufruf 2: h i j k l mit z0
; 0004: 40000000144   # Aufruf 3: m mit z0
; 0005: 00000000000   # kbein
; 7773: 00000004000   # R1: Adresse des Bereichs 3
; 7774: 00000005000   # R3 unveraendert
; 7776: 00000000001   # R2: zuletzt 1
;#PRUEFE-ENDE
