; kat4ausgabe.asm - Test des Makros KAT4AUSGABE (Ausgabe kat4-Text auf dem Schreibwerk, Startadresse in R1 = 7773, KB/GB-Zustand per R3 = 7774)
; Empfehlung (001): kleinste Startzelle 0000, groesste 7700 minus Programmlaenge, Ausrichtung egal (Testprogramm ab 0000).
; Hauptprogramm: verwaltet den KB/GB-Zustand des Schreibwerks in der Zelle kbaus (initial 0 = KB, Festlegung 030), traegt deren Adresse
;                in R3 ein und ruft das UP zweimal auf: Text 1 = a Um.GB b (Zustand danach GB), Text 2 = c Um.KB d (Zustand danach KB).
;#DOK-0001 KAT4AUSGABE: a Um.GB b / c Um.KB d, Zustandsuebergabe in R3
;#SPEI-0001 0001-0006
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat4ausgabe
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat4ausgabe_zustand-sw-ausgabe.txt

r1:             abs     07773        ; Register 1: Startadresse des Textes (Adressfeld)
r3:             abs     07774        ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
text1:          dw      040014427461 ; Zelle 0001: a (061), Um. GB (057), b (062), z0
text2:          dw      040015047443 ; Zelle 0002: c (043), Um. KB (0117), d (064), z0
radr1:          da      text1        ; Zelle 0003: Adresse von Text 1 (Adressfeld)
radr2:          da      text2        ; Zelle 0004: Adresse von Text 2 (Adressfeld)
kbaus:          dw      0            ; Zelle 0005: KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), initial KB
zw1:            dw      0            ; Zelle 0006: Zustand nach Text 1 (Pruefung)
rkb:            da      kbaus        ; Zelle 0007: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb          ; Zelle 0010: AC := Adresse der Zustandszelle
                240     r3           ; R3 := Adresse der Zustandszelle
                211     radr1        ; AC := Adresse von Text 1
                240     r1           ; R1 := Adresse von Text 1
                ANWAHL  K2           ; Kanal 2 = Schreibwerk
                025     ausgabe      ; Aufruf KAT4AUSGABE (Text 1)
                211     kbaus        ; AC := Zustand nach Text 1
                240     zw1          ; zw1 := Zustand nach Text 1
                211     radr2        ; AC := Adresse von Text 2
                240     r1           ; R1 := Adresse von Text 2
                025     ausgabe      ; Aufruf KAT4AUSGABE (Text 2, Zustand GB aus dem ersten Aufruf)
                020     0            ; Halt
ausgabe:        KAT4AUSGABE          ; Unterprogramm
ende:           end

; Sollwerte von Hand hergeleitet (Kodetabelle 1, kat4-Zeichen = Ausgabeadresse / 8, erstes Zeichen rechts, z0 = 040000000000):
; Text 1: a = 061, Um. GB = 057, b = 062 -> 061 + 057 * 0400 + 062 * 0200000 (je 8 Bit) = 040014427461 (Wort mit z0).
; Text 2: c = 043, Um. KB = 0117, d = 064 -> 040015047443 (Wort mit z0).
; Halt in 0023 (Hauptprogramm 0010 bis 0023, oktal), BZ = 0024.
; Zustand: anfangs 0 (KB). Text 1 enthaelt Um. GB -> kbaus = 1, zw1 = 1. Text 2 enthaelt Um. KB -> kbaus = 0.
; R1 = Adresse von Text 2 = 0002 * 01000 = 02000, R3 = 0005 * 01000 = 05000 (beide bleiben unveraendert).
; Schreibwerkausgabe (Start KB): a, Um. GB, B, dann C (Zustand GB), Um. KB, d -> "aBCd".
;#PRUEFE-START
; BZ=0024
; 0001: 40014427461   # Text 1
; 0002: 40015047443   # Text 2
; 0005: 00000000000   # kbaus: nach Um. KB wieder KB
; 0006: 00000000001   # zw1: nach Text 1 GB
; 7773: 00000002000   # R1 = Adresse von Text 2
; 7774: 00000005000   # R3 = Adresse der Zustandszelle
;#PRUEFE-ENDE
