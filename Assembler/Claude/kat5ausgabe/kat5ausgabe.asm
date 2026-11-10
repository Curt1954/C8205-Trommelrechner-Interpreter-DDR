; kat5ausgabe.asm - Hauptprogramm und Makro KAT5AUSGABE / Unterprogramm (Ausgabe kat5-Worte auf dem Schreibwerk)
;
; Hauptprogramm: verwaltet den KB/GB-Zustand des Schreibwerks in der Zelle kbaus (initial 0 = KB, Festlegung 030), traegt deren Adresse in R3 (Register 7774)
;                ein, waehlt Kanal 2 (Schreibwerk) an, traegt die Adresse des kat5-Wortes in R1 (Register 7773) ein und ruft das UP mit 025 auf.
;                Jeder Aufruf gibt genau ein Wort aus. Text 1 = "hallo welt" in zwei Worten (hallo, Leerzeichen und welt; zwei Aufrufe, R1 um 01000 weiter),
;                Text 2 = "a Um.GB b" (ein Wort, Zustand danach GB), Text 3 = "c Um.KB d" (ein Wort, Zustand danach KB).
; UP ausgabe:    (zuerst als Quelltext im Programm getestet, dann unveraendert als Makro uebernommen, gleiche Sollwerte)
;                gibt die Zeichen genau eines kat5-Wortes ab R1 aus (bis zu 5 Zeichen zu 6 Bit, erstes Zeichen links in z3 bis z8, Fuellung 00 rechts, kein z0;
;                Format Assemblerdokumentation 3.3.15). Das Wort ist zu Ende, sobald der Rest 0 ist; das Wort 0 gibt nichts aus.
;                Jedes Zeichen wird ueber die Tabelle im Makro (fertige Ausgabebefehle, Index = kat5-Code) ausgegeben. Das UP gibt keine Umschaltzeichen von selbst aus
;                und liest den Anfangszustand nicht; es zieht die Zelle in R3 nach: Um. GB (kat5 055) setzt sie auf 1, Um. KB (054) auf 0 (beide Zeichen werden auch
;                ausgegeben). R1 und R3 bleiben unveraendert. Rueckkehr mit 025: AC = 0 (der Rest des Wortes ist leer).
; Empfehlung (001): kleinste Startzelle 0000, groesste 7600 minus Programmlaenge (Arbeitsspur 7640 durch SCHIEBE_LI/SCHIEBE_RE), Ausrichtung egal.
;#DOK-0001 KAT5AUSGABE: hallo welt (zwei Worte) / a Um.GB b / c Um.KB d, Zustandsuebergabe in R3
;#SPEI-0001 0001-0012
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5ausgabe
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5ausgabe-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat5    hallo                ; Zelle 0001: Text 1, Wort 1: h a l l o
                kat5    \ welt\              ; Zelle 0002: Text 1, Wort 2: Leerzeichen w e l t (zwischen \ und \, damit das fuehrende Leerzeichen bleibt)
text2:          kat5    a$ingbb              ; Zelle 0003: a, Um. GB, b
text3:          kat5    c$inkbd              ; Zelle 0004: c, Um. KB, d
radr1:          da      text1                ; Zelle 0005: Adresse von Text 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0006: Adresse von Text 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0007: Adresse von Text 3 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0010: KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), initial KB
zw2:            dw      0                    ; Zelle 0011: Zustand nach Text 2 (Pruefung)
rkb:            da      kbaus                ; Zelle 0012: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Text 1, Wort 1
                240     r1                   ; R1 := Adresse von Text 1, Wort 1
                025     ausgabe              ; Aufruf KAT5AUSGABE (Text 1, Wort 1: hallo)
                211     r1                   ; AC := Adresse von Wort 1
                210     #01000               ; plus eine Adresseinheit: Wort 2
                240     r1                   ; R1 := Adresse von Text 1, Wort 2
                025     ausgabe              ; Aufruf (Text 1, Wort 2: Leerzeichen und welt)
                211     radr2                ; AC := Adresse von Text 2
                240     r1                   ; R1 := Adresse von Text 2
                025     ausgabe              ; Aufruf (Text 2, Zustand KB, danach GB)
                211     kbaus                ; AC := Zustand nach Text 2
                240     zw2                  ; zw2 := Zustand nach Text 2
                211     radr3                ; AC := Adresse von Text 3
                240     r1                   ; R1 := Adresse von Text 3
                025     ausgabe              ; Aufruf (Text 3, Zustand GB aus dem Aufruf davor)
                020     0                    ; Halt

; ---- UP KAT5AUSGABE als Makro aus c82ass.makros
ausgabe:        KAT5AUSGABE                  ; UP: Ausgabe eines kat5-Wortes (Tabelle dahinter)
ende:           end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: Leerzeichen = 01, a bis z = 021 bis 052, Um. KB = 054, Um. GB = 055; erstes Zeichen links, 2 Oktalziffern je Zeichen,
; Fuellung 00 rechts, z0 bis z2 = 0, die 11. Ziffer ganz links ist die Ziffer von z0 bis z2 und bleibt 0):
; Text 1, Wort 1 "hallo": h = 030, a = 021, l = 034, l = 034, o = 037 -> 0 30 21 34 34 37 = 03021343437.
; Text 1, Wort 2 " welt": Leerzeichen = 01, w = 047, e = 025, l = 034, t = 044 -> 0 01 47 25 34 44 = 00147253444.
; Text 2: a = 021, Um. GB = 055, b = 022 -> 0 21 55 22 00 00 = 02155220000.   Text 3: c = 023, Um. KB = 054, d = 024 -> 0 23 54 24 00 00 = 02354240000.
; Zellen: text1 0001/0002, text2 0003, text3 0004, radr1 0005, radr2 0006, radr3 0007, kbaus 0010, zw2 0011, rkb 0012, Hauptprogramm 0013 bis 0035 (Halt, 4 Zellen mehr als mit
; Text 1 in einem Aufruf: 211, 210, 240, 025), BZ = 0036.
; Zustand: anfangs 0 (KB). Text 2 enthaelt Um. GB -> kbaus = 1, zw2 = 1. Text 3 enthaelt Um. KB -> kbaus = 0.
; R1 = Adresse von Text 3 = 0004 * 01000 = 04000, R3 = Adresse von kbaus = 0010 * 01000 = 010000 (beide bleiben unveraendert). AC = 0 (Rest des letzten Wortes).
; Schreibwerkausgabe (Start KB): "hallo", " welt", a, Um. GB, B, dann C (Zustand GB), Um. KB, d -> "hallo weltaBCd" (unveraendert gegen das Format davor).
;#PRUEFE-START
; BZ=0036 AC=00000000000
; 0001: 03021343437   # Text 1, Wort 1: h a l l o
; 0002: 00147253444   # Text 1, Wort 2: Leerzeichen w e l t
; 0003: 02155220000   # Text 2: a Um. GB b
; 0004: 02354240000   # Text 3: c Um. KB d
; 0010: 00000000000   # kbaus: nach Um. KB wieder KB
; 0011: 00000000001   # zw2: nach Text 2 GB
; 7773: 00000004000   # R1 = Adresse von Text 3
; 7774: 00000010000   # R3 = Adresse der Zustandszelle
;#PRUEFE-ENDE
