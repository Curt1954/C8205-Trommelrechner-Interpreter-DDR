; kat5eingabe_um.asm - KAT5EINGABE: Um. GB / Um. KB werden gespeichert, gezaehlt und ziehen die Zustandszelle (R3) nach
;   Eingabedatei: Um. GB a b c d | Um. KB e f g h
;   Aufruf 1 (Zustandszelle kb1, anfangs 0 = KB): Um. GB, a, b, c, d (5 Zeichen, das Umschaltzeichen zaehlt mit) -> kb1 = 1 (GB).
;   Aufruf 2 (Zustandszelle kb2, anfangs 1 = GB): Um. KB, e, f, g, h (5 Zeichen) -> kb2 = 0 (KB). kb1 bleibt unveraendert.
;#DOK-0001 KAT5EINGABE: Um. GB und Um. KB ziehen die Zustandszelle nach (zwei Aufrufe mit zwei Zellen)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat5eingabe_um.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          db      1                    ; Zelle 0001: Wort 1 (Aufruf 1)
text2:          db      1                    ; Zelle 0002: Wort 2 (Aufruf 2)
kb1:            dw      0                    ; Zelle 0003: Zustand der Eingabe 1, anfangs KB
kb2:            dw      1                    ; Zelle 0004: Zustand der Eingabe 2, anfangs GB
radr1:          da      text1                ; Zelle 0005: Adresse des Wortes 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0006: Adresse des Wortes 2 (Adressfeld)
rkb1:           da      kb1                  ; Zelle 0007: Adresse der Zustandszelle 1 (Adressfeld)
rkb2:           da      kb2                  ; Zelle 0010: Adresse der Zustandszelle 2 (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr1                ; AC := Adresse des Wortes 1
                240     r1                   ; R1 := Adresse des Wortes 1
                211     rkb1                 ; AC := Adresse der Zustandszelle 1
                240     r3                   ; R3 := Adresse der Zustandszelle 1
                025     eingabe              ; Aufruf 1 KAT5EINGABE
                211     radr2                ; AC := Adresse des Wortes 2
                240     r1                   ; R1 := Adresse des Wortes 2
                211     rkb2                 ; AC := Adresse der Zustandszelle 2
                240     r3                   ; R3 := Adresse der Zustandszelle 2
                025     eingabe              ; Aufruf 2 KAT5EINGABE
                020     0                    ; Halt

; ---- UP KAT5EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT5EINGABE                  ; Unterprogramm: liest ein Wort ueber K0 und legt es auf R1 ab
                end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: Um. KB = 054, Um. GB = 055, a = 021, b = 022, c = 023, d = 024, e = 025, f = 026, g = 027, h = 030;
; erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0):
; Aufruf 1: Um. GB a b c d -> 0 55 21 22 23 24 = 05521222324, kb1 := 1.
; Aufruf 2: Um. KB e f g h -> 0 54 25 26 27 30 = 05425262730, kb2 := 0 (war 1). kb1 bleibt 1.
; Zellen: text1 0001, text2 0002, kb1 0003, kb2 0004, radr1 0005, radr2 0006, rkb1 0007, rkb2 0010, Hauptprogramm 0011 bis 0024 (Halt) -> BZ = 0025.
; R1 = text2 = 0002 * 01000 = 02000, R3 = kb2 = 0004 * 01000 = 04000, AC = zuletzt gespeichertes Wort = 05425262730.
;#PRUEFE-START
; BZ=0025 AC=05425262730
; 0001: 05521222324   # Aufruf 1: Um. GB a b c d
; 0002: 05425262730   # Aufruf 2: Um. KB e f g h
; 0003: 00000000001   # kb1: GB nach Um. GB
; 0004: 00000000000   # kb2: KB nach Um. KB (anfangs 1)
; 7773: 00000002000   # R1: Adresse des Wortes 2
; 7774: 00000004000   # R3: Adresse der Zustandszelle 2
;#PRUEFE-ENDE
