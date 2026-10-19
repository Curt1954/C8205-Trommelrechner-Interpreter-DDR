         start  0
; sw_eingabe_lage.asm  --  Eingabeprogramm ueber das Schreibwerk (SW) mit Beruecksichtigung der Zeichenlage KB/GB (SW-Eingabe-003)
;
; Neu gegenueber sw_eingabe_k2.asm (19.10.2026): Auf dem R300 sind ":" (KB) und "(" (GB) DIESELBE Taste (Code 15). Das SW schickt davor
;         Um. KB bzw. Um. GB (eigene Eingaben, Codes 57 und 37). Das Programm geht von KB aus und merkt sich die Lage ueber den Sprung "ziel":
;         Um. KB  -> ziel := "000 hende"   (Code 15 = ":"  beendet die Eingabe und laesst die Ausgabe ablaufen)
;         Um. GB  -> ziel := "000 hklam"   (Code 15 = "("  wird wie jedes andere Zeichen gespeichert)
;         Um. KB und Um. GB selbst werden weiter als Ausgabebefehl gespeichert (die Ausgabe schaltet so wie die Eingabe).
; Zusaetzlicher Ausgabebefehl: vor dem Ablauf der Spur steht "dz $inkb" (Um. KB), damit die Ausgabe sicher in KB beginnt, gleich in welcher
;         Lage die Eingabe endete. Das erste gespeicherte Zeichen bringt sein eigenes Umschaltzeichen mit.
; Ablauf wie bisher: 011 ztab liefert den fertigen Ausgabebefehl; er wird nach 04000 + i gespeichert; ":" in KB schreibt den Stopp an 04000 + i,
;         wählt K2 an und springt nach 04000. Tabelle ztab ab 0400 (64 Zellen, Code = Eingabeadresse).
SPUR:    abs    04000
beginn:  000    anf               ; Zelle 0000: Sprung nach 02000
anf:     030    04600
         equ    02000
anfang:  211    anfbef            ; i := 0 (auch bei Neustart)
         240    gemein
         211    kbsp              ; Lage := KB (auch bei Neustart): Code 15 beendet
         240    ziel
schleife: 011   ztab              ; Eingabe-Halt mit Loeschen: AC := Zelle ztab ODER Eingabeadresse (ohne Sprung)
gemein:  240    SPUR              ; Zeichen: AC (Ausgabebefehl) -> Zelle 04000 + i
         211    gemein
         210    eins              ; i := i + 1
         240    gemein
         000    schleife
eins:    dw     01000             ; 1 in den Adressstellen (Adresse << 9)
anfbef:  dw     04000240          ; Speicherbefehl "240 04000" (Anfangswert von gemein)
stopp:   dw     020               ; unbedingter Stopp
kbsp:    000    hende             ; Datenwort: Sprung nach hende (Lage KB)
gbsp:    000    hklam             ; Datenwort: Sprung nach hklam (Lage GB)
ziel:    000    hende             ; Sprungziel fuer Code 15, je nach Lage (ztab+015 springt hierher)

hende:   211    gemein            ; ":" in KB: AC := Speicherbefehl "240 04000+i"
         240    esp
         211    stopp
         ANWAHL 4500              ; K2 = SW-Ausgabe, der AC bleibt erhalten
esp:     dw     0                 ; wird zu "240 04000+i": Stopp speichern
         dz     $inkb             ; zusaetzlicher Ausgabebefehl: Ausgabe beginnt in KB
         000    SPUR              ; Ausgabebefehle ablaufen lassen, am Ende der Stopp

hklam:   211    w15               ; "(" in GB: normales Zeichen
         000    gemein
w15:     dw     0150030           ; Ausgabebefehl, Ausgabeadresse 0150

h57:     211    kbsp              ; Um. KB: Lage merken ...
         240    ziel
         211    w57               ; ... und das Umschaltzeichen als Ausgabebefehl speichern
         000    gemein
w57:     dw     01170030
h37:     211    gbsp              ; Um. GB: Lage merken ...
         240    ziel
         211    w37
         000    gemein
w37:     dw     0570030
h12:     211    w12               ; Code 12: Leertaste / ZR
         000    gemein
w12:     dw     0320030
h16:     211    w16               ; Code 16: Irrung Satz
         000    gemein
w16:     dw     0160030
h32:     211    w32               ; Code 32: SatzMarke / WRZL
         000    gemein
w32:     dw     02720030
h33:     211    w33               ; Code 33: . / !
         000    gemein
w33:     dw     0730030
h40:     211    w40               ; Code 40: - / Dreieck
         000    gemein
w40:     dw     01000030
h60:     211    w60               ; Code 60: ` / ;
         000    gemein
w60:     dw     01600030
h72:     211    w72               ; Code 72: BM
         000    gemein
w72:     dw     03520030
h73:     211    w73               ; Code 73: , / ?
         000    gemein
w73:     dw     01530030
h75:     211    w75               ; Code 75: Tabulator
         000    gemein
w75:     dw     01550030

         equ    0400              ; Tabelle ztab
ztab:    dw     0200030         ; 00: 0 / #
         dw     010030             ; 01: 1 / <
         dw     020030             ; 02: 2 / "
         dw     0230030            ; 03: 3 / ≈
         dw     040030             ; 04: 4 / [
         dw     0250030            ; 05: 5 / >
         dw     0260030            ; 06: 6 / '
         dw     070030             ; 07: 7 / ≋
         dw     0100030            ; 10: 8 / ~
         dw     0310030            ; 11: 9 / ]
         000    h12                ; 12: Leertaste / ZWR (Sprung-Umstellung)
         dw     0                  ; 13: unbelegt
         dw     0                  ; 14: unbelegt
         000    ziel               ; 15: : / ( (Sprung-Umstellung, Ziel je nach Lage)
         000    h16                ; 16: Irrung Satz / Irrung Satz (Sprung-Umstellung)
         dw     0                  ; 17: unbelegt
         dw     0400030            ; 20: + / =
         dw     0610030            ; 21: a / A
         dw     0620030            ; 22: b / B
         dw     0430030            ; 23: c / C
         dw     0640030            ; 24: d / D
         dw     0450030            ; 25: e / E
         dw     0460030            ; 26: f / F
         dw     0670030            ; 27: g / G
         dw     0700030            ; 30: h / H
         dw     0510030            ; 31: i / I
         000    h32                ; 32: SatzMarke / WRZL (Sprung-Umstellung)
         000    h33                ; 33: . / ! (Sprung-Umstellung)
         dw     0                  ; 34: unbelegt
         dw     0                  ; 35: unbelegt
         dw     0                  ; 36: unbelegt
         000    h37                ; 37: Um. GB / Um. GB (Sprung-Umstellung)
         000    h40                ; 40: - / △ (Sprung-Umstellung)
         dw     01210030           ; 41: j / J
         dw     01220030           ; 42: k / K
         dw     01030030           ; 43: l / L
         dw     01240030           ; 44: m / M
         dw     01050030           ; 45: n / N
         dw     01060030           ; 46: o / O
         dw     01270030           ; 47: p / P
         dw     01300030           ; 50: q / Q
         dw     01110030           ; 51: r / R
         dw     01120030           ; 52: WR / WR
         dw     0                  ; 53: unbelegt
         dw     0                  ; 54: unbelegt
         dw     0                  ; 55: unbelegt
         dw     03770030           ; 56: Irrung Zeichen / Irrung Zeichen
         000    h57                ; 57: Um. KB / Um. KB (Sprung-Umstellung)
         000    h60                ; 60: ` / ; (Sprung-Umstellung)
         dw     01410030           ; 61: / / )
         dw     01420030           ; 62: s / S
         dw     01630030           ; 63: t / T
         dw     01440030           ; 64: u / U
         dw     01650030           ; 65: v / V
         dw     01660030           ; 66: w / W
         dw     01470030           ; 67: x / X
         dw     01500030           ; 70: y / Y
         dw     01710030           ; 71: z / Z
         000    h72                ; 72: ZV / BM (Sprung-Umstellung)
         000    h73                ; 73: , / ? (Sprung-Umstellung)
         dw     01740030           ; 74: % / *
         000    h75                ; 75: Tabulator / Tabulator (Sprung-Umstellung)
         dw     0                  ; 76: unbelegt
         dw     01770030           ; 77: Transport (Relikt) / Transport (Relikt)
