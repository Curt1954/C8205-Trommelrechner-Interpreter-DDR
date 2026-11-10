; kat6ausgabe.asm - Hauptprogramm und Makro KAT6AUSGABE / Unterprogramm (Ausgabe eines kat6-Textes auf dem Schreibwerk)
;
; Hauptprogramm: verwaltet den KB/GB-Zustand des Schreibwerks in der Zelle kbaus (initial 0 = KB, Festlegung 030), traegt deren Adresse in R3 (Register 7774)
;                ein, waehlt Kanal 2 (Schreibwerk) an, traegt die Adresse des kat6-Textes in R1 (Register 7773) ein und ruft das UP mit 025 auf.
;                Text 1 = "hallo welt" (2 Worte), Text 2 = "a Um.GB b" (Zustand danach GB), Text 3 = "c Um.KB d" (Zustand danach KB).
; UP ausgabe:    (zuerst als Quelltext im Programm getestet, dann unveraendert als Makro uebernommen, gleiche Sollwerte)
;                gibt den kat6-Text ab R1 aus (5 Zeichen je Wort zu 6 Bit im Eingabecode, erstes Zeichen rechts, Stoppbit ueber dem letzten Zeichen, z0 am letzten Wort; Format Assemblerdokumentation 3.3.18).
;                Jedes Zeichen wird ohne Tabelle durch Maskieren und Schieben in seinen Ausgabebefehl umgesetzt (Ausgabeadresse = ((Code UND 017) + 2 mal (Code UND 060)) mal 8). Das UP gibt keine Umschaltzeichen von selbst aus
;                und liest den Anfangszustand nicht; es zieht die Zelle in R3 nach: Um. GB (kat6 037) setzt sie auf 1, Um. KB (057) auf 0 (beide Zeichen werden auch
;                ausgegeben). R1 und R3 bleiben unveraendert. Rueckkehr mit 025: AC = letztes Textwort (mit z0).
; Empfehlung (001): kleinste Startzelle 0000, groesste 7600 minus Programmlaenge (Arbeitsspur 7640 durch SCHIEBE_LI/SCHIEBE_RE), Ausrichtung egal.
;#DOK-0001 KAT6AUSGABE: hallo welt / a Um.GB b / c Um.KB d, Zustandsuebergabe in R3
;#SPEI-0001 0001-0010
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat6ausgabe
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat6ausgabe-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Startadresse des Textes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat6    hallo welt           ; Zellen 0001 und 0002: Text 1
text2:          kat6    a$ingbb              ; Zelle 0003: a, Um. GB, b
text3:          kat6    c$inkbd              ; Zelle 0004: c, Um. KB, d
radr1:          da      text1                ; Zelle 0005: Adresse von Text 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0006: Adresse von Text 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0007: Adresse von Text 3 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0010: KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), initial KB
zw2:            dw      0                    ; Zelle 0011: Zustand nach Text 2 (Pruefung)
rkb:            da      kbaus                ; Zelle 0012: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Text 1
                240     r1                   ; R1 := Adresse von Text 1
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 1)
                211     radr2                ; AC := Adresse von Text 2
                240     r1                   ; R1 := Adresse von Text 2
                025     ausgabe              ; Aufruf (Text 2, Zustand KB, danach GB)
                211     kbaus                ; AC := Zustand nach Text 2
                240     zw2                  ; zw2 := Zustand nach Text 2
                211     radr3                ; AC := Adresse von Text 3
                240     r1                   ; R1 := Adresse von Text 3
                025     ausgabe              ; Aufruf (Text 3, Zustand GB aus dem zweiten Aufruf)
                020     0                    ; Halt

; ---- UP KAT6AUSGABE als Makro aus c82ass.makros
ausgabe:        KAT6AUSGABE                  ; UP: Ausgabe eines kat6-Textes (Zellen ab 0032)
ende:           end

; Sollwerte von Hand hergeleitet (kat6-Codes: a bis i = 021 bis 031, j bis r = 041 bis 051, s bis z = 062 bis 071, Leerzeichen 012, Um. GB 037, Um. KB 057; erstes Zeichen rechts, 6 Bit = 2 Oktalziffern je Zeichen,
; Stoppbit 1 links vom letzten Zeichen des Wortes, z0 = 040000000000 am letzten Wort):
; Text 1 "hallo welt": h a l l o = 1 46 43 43 21 30 (volles Wort, Stoppbit z2); Leerzeichen w e l t = 5 63 43 25 66 12 (z0 und Stoppbit z2) -> 14643432130 und 56343256612.
; Text 2: a = 21, Um. GB = 37, b = 22, Stoppbit in Bit 18, z0 -> 40001223721.   Text 3: c = 23, Um. KB = 57, d = 24, Stoppbit in Bit 18, z0 -> 40001245723.
; Zellen: text1 0001/0002, text2 0003, text3 0004, radr1 bis radr3 0005 bis 0007, kbaus 0010, zw2 0011, rkb 0012, Hauptprogramm 0013 bis 0031 (Halt), BZ = 0032.
; Zustand: anfangs 0 (KB). Text 2 enthaelt Um. GB -> kbaus = 1, zw2 = 1. Text 3 enthaelt Um. KB -> kbaus = 0.
; R1 = Adresse von Text 3 = 0004 * 01000 = 04000, R3 = Adresse von kbaus = 0010 * 01000 = 010000 (beide bleiben unveraendert). AC = letztes Textwort von Text 3.
; Schreibwerkausgabe (Start KB): "hallo welt", a, Um. GB, B, dann C (Zustand GB), Um. KB, d -> "hallo weltaBCd".
;#PRUEFE-START
; BZ=0032 AC=40001245723
; 0001: 14643432130   # Text 1, Wort 1: h a l l o
; 0002: 56343256612   # Text 1, Wort 2: Leerzeichen w e l t, z0
; 0003: 40001223721   # Text 2
; 0004: 40001245723   # Text 3
; 0010: 00000000000   # kbaus: nach Um. KB wieder KB
; 0011: 00000000001   # zw2: nach Text 2 GB
; 7773: 00000004000   # R1 = Adresse von Text 3
; 7774: 00000010000   # R3 = Adresse der Zustandszelle
;#PRUEFE-ENDE
