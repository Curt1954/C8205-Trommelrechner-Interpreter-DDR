; kat6eingabe_um.asm - KAT6EINGABE: Um. GB / Um. KB werden gespeichert, gezaehlt und ziehen die Zustandszelle (R3) nach
;   Eingabedatei: Um. GB a : | Um. KB b :
;   Aufruf 1 (Zustandszelle kb1, anfangs 0 = KB): Um. GB, a, : -> kb1 = 1 (GB).
;   Aufruf 2 (Zustandszelle kb2, anfangs 1 = GB): Um. KB, b, : -> kb2 = 0 (KB). kb1 bleibt unveraendert.
;#DOK-0001 KAT6EINGABE: Um. GB und Um. KB ziehen die Zustandszelle nach (zwei Aufrufe mit zwei Zellen)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat6eingabe_um.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          db      1                    ; Zelle 0001: Bereich 1 fuer 3 Zeichen = 1 Wort
text2:          db      1                    ; Zelle 0002: Bereich 2 fuer 3 Zeichen = 1 Wort
kb1:            dw      0                    ; Zelle 0003: Zustand der Eingabe 1, anfangs KB
kb2:            dw      1                    ; Zelle 0004: Zustand der Eingabe 2, anfangs GB
radr1:          da      text1                ; Zelle 0005: Adresse des Bereichs 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0006: Adresse des Bereichs 2 (Adressfeld)
rkb1:           da      kb1                  ; Zelle 0007: Adresse der Zustandszelle 1 (Adressfeld)
rkb2:           da      kb2                  ; Zelle 0010: Adresse der Zustandszelle 2 (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     #3                   ; AC := 3
                240     r2                   ; R2 := 3
                211     radr1                ; AC := Adresse des Bereichs 1
                240     r1                   ; R1 := Adresse des Bereichs 1
                211     rkb1                 ; AC := Adresse der Zustandszelle 1
                240     r3                   ; R3 := Adresse der Zustandszelle 1
                025     eingabe              ; Aufruf 1 KAT6EINGABE
                211     radr2                ; AC := Adresse des Bereichs 2
                240     r1                   ; R1 := Adresse des Bereichs 2
                211     rkb2                 ; AC := Adresse der Zustandszelle 2
                240     r3                   ; R3 := Adresse der Zustandszelle 2
                025     eingabe              ; Aufruf 2 KAT6EINGABE
                020     0                    ; Halt

; ---- UP KAT6EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT6EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat6-Text ab R1 ab
                end

; Sollwerte von Hand hergeleitet (Um. GB = 037, Um. KB = 057, a = 021, b = 022, : = 015; erstes Zeichen rechts, Stoppbit in Bit 18, z0 = 040000000000):
; Aufruf 1: Um. GB, a, : -> 15 21 37 mit Stoppbit in Bit 18 (01000000) und z0 -> 40001152137; kb1 = 1 (GB).
; Aufruf 2: Um. KB, b, : -> 15 22 57 mit Stoppbit in Bit 18 und z0 -> 40001152257; kb2 = 0 (KB). kb1 bleibt 1. R1 = text2 = 0002 * 01000, R2 = 3, R3 = kb2 = 0004 * 01000, AC = -1.
;#PRUEFE-START
; BZ=0027 AC=77777777777
; 0001: 40001152137   # Aufruf 1: Um. GB a : mit Stoppbit und z0
; 0002: 40001152257   # Aufruf 2: Um. KB b : mit Stoppbit und z0
; 0003: 00000000001   # kb1: Um. GB gesehen
; 0004: 00000000000   # kb2: Um. KB gesehen
; 7773: 00000002000   # R1: Adresse des Bereichs 2
; 7774: 00000004000   # R3: Adresse der Zustandszelle 2
; 7776: 00000000003   # R2 unveraendert
;#PRUEFE-ENDE
