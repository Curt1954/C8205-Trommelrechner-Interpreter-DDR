; kat4ausgabe_g.asm - Test des Projektmakros KAT4AUSGABE_G (macro_zt_loader.macro): kat4-Text auf dem Schreibwerk, Startadresse in R1 = 7773,
;                     KB/GB-Zustand in der GLOBALEN Zelle KBGB = 7775 (0 = KB, 1 = GB), keine Uebergabe per R3
; Empfehlung (001): kleinste Startzelle 0000, groesste 7700 minus Programmlaenge, Ausrichtung egal (Testprogramm ab 0000).
; Hauptprogramm: setzt KBGB := 0 (KB), waehlt K2 (Schreibwerk) an und ruft das UP viermal auf (der Text beginnt immer in KB):
;   Text 1 = a Um.GB b          (KBGB vorher 0, danach 1)
;   Text 2 = c Um.KB d          (KBGB vorher 1: das UP gibt zuerst Um. KB aus; danach 0)
;   Text 3 = c Um.GB d          (KBGB vorher 0, danach 1)
;   Text 4 = a b Um.GB c | d    (zwei Woerter; KBGB vorher 1: Um. KB zuerst; danach 1)
;#MACRODATEI1=../../macro_zt_loader.macro
;#DOK-0001 KAT4AUSGABE_G: vier Texte, globaler KB/GB-Zustand KBGB (7775) wird gelesen und nachgefuehrt
;#SPEI-0001 0001-0014
;#PROT STUFE=2
;#TROMMEL=LEER
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat4ausgabe_g
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat4ausgabe_g-sw-ausgabe.txt

r1:             abs     07773        ; Register 1: Startadresse des Textes (Adressfeld)
kbgb:           abs     07775        ; globale KB/GB-Zelle des Projekts (0 = KB, 1 = GB)

                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
text1:          dw      040014427461 ; Zelle 0001: a (061), Um. GB (057), b (062), z0
text2:          dw      040015047443 ; Zelle 0002: c (043), Um. KB (0117), d (064), z0
text3:          dw      040015027443 ; Zelle 0003: c (043), Um. GB (057), d (064), z0
text4a:         dw      004313631061 ; Zelle 0004: a (061), b (062), Um. GB (057), c (043), kein z0
text4b:         dw      040000000064 ; Zelle 0005: d (064), z0
radr1:          da      text1        ; Zelle 0006: Adresse von Text 1 (Adressfeld)
radr2:          da      text2        ; Zelle 0007: Adresse von Text 2 (Adressfeld)
radr3:          da      text3        ; Zelle 0010: Adresse von Text 3 (Adressfeld)
radr4:          da      text4a       ; Zelle 0011: Adresse von Text 4 (Adressfeld)
zw1:            dw      0            ; Zelle 0012: KBGB nach Text 1 (Pruefung)
zw2:            dw      0            ; Zelle 0013: KBGB nach Text 2 (Pruefung)
zw3:            dw      0            ; Zelle 0014: KBGB nach Text 3 (Pruefung)
haupt:          241     kbgb         ; KBGB := 0 (Anfangszustand KB)
                ANWAHL  K2           ; Kanal 2 = Schreibwerk
                211     radr1        ; AC := Adresse von Text 1
                240     r1           ; R1 := Adresse von Text 1
                025     ausgabe      ; Aufruf KAT4AUSGABE_G (Text 1)
                211     kbgb         ; AC := KBGB nach Text 1
                240     zw1          ; zw1 := KBGB nach Text 1
                211     radr2        ; AC := Adresse von Text 2
                240     r1           ; R1 := Adresse von Text 2
                025     ausgabe      ; Aufruf (Text 2, KBGB = GB aus Text 1)
                211     kbgb         ; AC := KBGB nach Text 2
                240     zw2          ; zw2 := KBGB nach Text 2
                211     radr3        ; AC := Adresse von Text 3
                240     r1           ; R1 := Adresse von Text 3
                025     ausgabe      ; Aufruf (Text 3)
                211     kbgb         ; AC := KBGB nach Text 3
                240     zw3          ; zw3 := KBGB nach Text 3
                211     radr4        ; AC := Adresse von Text 4
                240     r1           ; R1 := Adresse von Text 4
                025     ausgabe      ; Aufruf (Text 4, KBGB = GB aus Text 3)
                020     0            ; Halt
ausgabe:        KAT4AUSGABE_G        ; Unterprogramm (Makro aus macro_zt_loader.macro)
ende:           end

; Sollwerte von Hand hergeleitet (Kodetabelle 1, kat4-Zeichen = Ausgabeadresse / 8, erstes Zeichen rechts, je 8 Bit, z0 = 040000000000):
; Zeichencodes: a = 061, b = 062, c = 043, d = 064, Um. GB = 057, Um. KB = 0117.
; Text 1 = 061 + 057 * 0400 + 062 * 0200000 + z0 = 040014427461 (wie in kat4ausgabe.asm); Text 2 = 040015047443 (ebenso);
; Text 3 = 043 + 057 * 0400 + 064 * 0200000 + z0 = 040015027443 (wie Text 2, nur 057 statt 0117 im mittleren Byte);
; Text 4, Wort 1 = 061 + 062 * 0400 + 057 * 0200000 + 043 * 0100000000 = 004313631061 (ohne z0), Wort 2 = 064 + z0 = 040000000064.
; Ablauf und Zustand (KBGB): Start 0 (KB).
;   Text 1: KBGB = 0, nichts vorweg; a, Um. GB (KBGB := 1), b -> Ausgabe "aB"; KBGB = 1  -> zw1 = 1.
;   Text 2: KBGB = 1: das UP gibt zuerst Um. KB aus (KBGB := 0); c, Um. KB (KBGB := 0), d -> "cd"; KBGB = 0  -> zw2 = 0.
;   Text 3: KBGB = 0, nichts vorweg; c, Um. GB (KBGB := 1), d -> "cD"; KBGB = 1  -> zw3 = 1.
;   Text 4: KBGB = 1: zuerst Um. KB (KBGB := 0); a, b, Um. GB (KBGB := 1), c, d -> "abCD"; KBGB = 1.
; Schreibwerkausgabe insgesamt: aBcdcDabCD (die Umschaltzeichen selbst erscheinen nicht).
; Adressen: Text 1 bis 4 liegen auf 0001, 0002, 0003, 0004 -> Adressfeld 01000, 02000, 03000, 04000; R1 = Adresse von Text 4 = 00000004000.
; Hauptprogramm 0015 bis 0041 (23 Befehle: 0015 bis 0040 sind 22 Zellen, 0041 Halt), Halt in 0041, BZ = 0042.
;#PRUEFE-START
; BZ=0042
; 0012: 00000000001   # zw1: nach Text 1 GB
; 0013: 00000000000   # zw2: nach Text 2 KB
; 0014: 00000000001   # zw3: nach Text 3 GB
; 7773: 00000004000   # R1 = Adresse von Text 4
; 7775: 00000000001   # KBGB nach Text 4: GB
;#PRUEFE-ENDE
