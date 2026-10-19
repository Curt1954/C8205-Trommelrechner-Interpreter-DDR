         start  0
; r300_eingabe.asm  --  Eingabeprogramm fuer ALLE Zeichen des R300-Codes, die eine Computertaste haben (Version RE-001)
; ERZEUGT von testscripte/r300_eingabe_erzeugen.py - nicht von Hand aendern, sondern das Skript.
;
; Ablauf: Meldung am Schreibwerk (K2); dann K0 anwaehlen (Schalter SW gedrueckt!) und Schleife: Eingabe-Halt 011 ztab,
;         das Ausgabewort des Zeichens in die Spur (ab 03000) schreiben, weiter. KEIN Echo: das SW-Fenster zeigt jedes angenommene
;         Zeichen selbst an (S3-04); zwischen zwei 011 wird K2 nie angewaehlt (S3-13: der Rechner ist rechtzeitig wieder bei 011).
; Tabelle ztab (0400..0477): Wort ztab+Code = Ausgabebefehl des Zeichens (Zeichen ohne Sprung-Umstellung); bei Zeichen MIT
;         Sprung-Umstellung springt der Eingabebefehl auf ztab+Code und fuehrt dort "000 handler" aus.
; Ende:  das Zeichen "Irrung Satz" (keine Taste; nur der TEST-Interpreter sendet es) -> Stopp. Sonst laeuft das Programm bis Netz aus.
; Lage:  Das Programm geht davon aus, dass das Schreibwerk nach der Meldung auf KB steht; das erste getippte Zeichen muss
;         deshalb eine Ziffer oder ein Kleinbuchstabe sein (das SW schickt vor dem ersten Zeichen kein Umschaltzeichen).

beginn:  000    anfang               ; Zelle 0000: Sprung zum Programmanfang
anfang:  ANWAHL 4500                 ; K2 = Schreibwerk-Ausgabe
         dtm    \R300 Eingabe, die Anzeige jeder Taste macht das Fenster\
         dz     $inkb                ; Ausgabelage KB (das erste Eingabezeichen kommt ohne Umschaltzeichen)
         dz     $wrzl
         ANWAHL 4700                 ; K0 (liest die Schalterstellung SW)

schleife: 011   ztab                 ; Eingabe-Halt mit Loeschen: AC := Tabellenwort ztab OR Code (Zeichen ohne Sprung)
gemein:  240    SPURBEGINN           ; Spur: AC (Ausgabewort des Zeichens) -> Spurzelle (Adresse wird je Zeichen um 1 erhoeht)
         211    gemein               ; AC := der Speicherbefehl (Zelle gemein)
         210    eins                 ; + 1 in den Adressstellen
         240    gemein               ; zurueckschreiben
         000    schleife
eins:    dw     01000                ; 1 in den Adressstellen (Adresse << 9)

h75:     211    w75                  ; Tabulator / Tabulator (Code 75): Ausgabewort laden
         000    gemein
w75:     dw     01550030
h15:     211    w15                  ; : / ( (Code 15): Ausgabewort laden
         000    gemein
w15:     dw     0150030
h57:     211    w57                  ; Um. KB / Um. KB (Code 57): Ausgabewort laden
         000    gemein
w57:     dw     01170030
h37:     211    w37                  ; Um. GB / Um. GB (Code 37): Ausgabewort laden
         000    gemein
w37:     dw     0570030
h60:     211    w60                  ; ` / ; (Code 60): Ausgabewort laden
         000    gemein
w60:     dw     01600030
h32:     211    w32                  ; SatzMarke / WRZL (Code 32): Ausgabewort laden
         000    gemein
w32:     dw     02720030
h73:     211    w73                  ; , / ? (Code 73): Ausgabewort laden
         000    gemein
w73:     dw     01530030
h33:     211    w33                  ; . / ! (Code 33): Ausgabewort laden
         000    gemein
w33:     dw     0730030
h40:     211    w40                  ; - / △ (Code 40): Ausgabewort laden
         000    gemein
w40:     dw     01000030
h12:     211    w12                  ; Leertaste / ZR (Code 12): Ausgabewort laden
         000    gemein
w12:     dw     0320030
h16:     020    0                    ; Irrung Satz (Code 16): Ende (nur im TEST-Lauf)

; ---- Tabelle ztab (0400..0477) ----
         equ    0400                  ; Tabelle auf 0400 (64 Worte, Code = Eingabeadresse)
ztab:    dw     0200030       ; 00: 0 / #
         dw     010030       ; 01: 1 / <
         dw     020030       ; 02: 2 / "
         dw     0230030       ; 03: 3 / ≈
         dw     040030       ; 04: 4 / [
         dw     0250030       ; 05: 5 / >
         dw     0260030       ; 06: 6 / '
         dw     070030       ; 07: 7 / ≋
         dw     0100030       ; 10: 8 / ~
         dw     0310030       ; 11: 9 / ]
         000    h12                 ; 12: Leertaste / ZR (Sprung-Umstellung)
         dw     0                    ; 13: unbelegt
         dw     0                    ; 14: unbelegt
         000    h15                 ; 15: : / ( (Sprung-Umstellung)
         000    h16                 ; 16: Irrung Satz / Irrung Satz (Sprung-Umstellung)
         dw     0                    ; 17: unbelegt
         dw     0400030       ; 20: + / =
         dw     0610030       ; 21: a / A
         dw     0620030       ; 22: b / B
         dw     0430030       ; 23: c / C
         dw     0640030       ; 24: d / D
         dw     0450030       ; 25: e / E
         dw     0460030       ; 26: f / F
         dw     0670030       ; 27: g / G
         dw     0700030       ; 30: h / H
         dw     0510030       ; 31: i / I
         000    h32                 ; 32: SatzMarke / WRZL (Sprung-Umstellung)
         000    h33                 ; 33: . / ! (Sprung-Umstellung)
         dw     0                    ; 34: unbelegt
         dw     0                    ; 35: unbelegt
         dw     0                    ; 36: unbelegt
         000    h37                 ; 37: Um. GB / Um. GB (Sprung-Umstellung)
         000    h40                 ; 40: - / △ (Sprung-Umstellung)
         dw     01210030       ; 41: j / J
         dw     01220030       ; 42: k / K
         dw     01030030       ; 43: l / L
         dw     01240030       ; 44: m / M
         dw     01050030       ; 45: n / N
         dw     01060030       ; 46: o / O
         dw     01270030       ; 47: p / P
         dw     01300030       ; 50: q / Q
         dw     01110030       ; 51: r / R
         dw     01120030       ; 52: WR / WR
         dw     0                    ; 53: unbelegt
         dw     0                    ; 54: unbelegt
         dw     0                    ; 55: unbelegt
         dw     0                    ; 56: unbelegt
         000    h57                 ; 57: Um. KB / Um. KB (Sprung-Umstellung)
         000    h60                 ; 60: ` / ; (Sprung-Umstellung)
         dw     01410030       ; 61: / / )
         dw     01420030       ; 62: s / S
         dw     01630030       ; 63: t / T
         dw     01440030       ; 64: u / U
         dw     01650030       ; 65: v / V
         dw     01660030       ; 66: w / W
         dw     01470030       ; 67: x / X
         dw     01500030       ; 70: y / Y
         dw     01710030       ; 71: z / Z
         dw     0                    ; 72: BM/ZV: keine Taste, nicht behandelt (Zelle wuerde als Sprung nach 0000 laufen)
         000    h73                 ; 73: , / ? (Sprung-Umstellung)
         dw     01740030       ; 74: % / *
         000    h75                 ; 75: Tabulator / Tabulator (Sprung-Umstellung)
         dw     0                    ; 76: unbelegt
         dw     0                    ; 77: unbelegt

SPURBEGINN: abs  03000
