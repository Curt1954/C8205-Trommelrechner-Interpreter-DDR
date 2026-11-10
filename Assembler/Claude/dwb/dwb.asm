; dwb.asm - Test der Anweisung dwb (Wert als Bitfolge aus 0 und 1, 1 bis 33 Stellen, Doku 3.3.19)
; Die Ziffernfolge ist immer dual (auch mit fuehrender 0), rechtsbuendig im Wort; letzte Ziffer = z32, bei 33 Stellen erste Ziffer = z0.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
d5:             dwb     101          ; Zelle 0001: Wort 5
d5f:            dwb     0000101      ; Zelle 0002: ebenso 5 (fuehrende Nullen zaehlen als Stellen)
d15:            dwb     1111         ; Zelle 0003: Wort 15 = 017 oktal
d64:            dwb     001000000    ; Zelle 0004: 9 Stellen, Wort 64 = 0100 oktal
d0:             dwb     0            ; Zelle 0005: Wort 0
dz0:            dwb     100000000000000000000000000000000   ; Zelle 0006: 33 Stellen, nur z0 = 1: 40000000000
dalt:           dwb     101010101010101010101010101010101   ; Zelle 0007: 33 Stellen, abwechselnd, z0 = 1: 52525252525
dvoll:          dwb     111111111111111111111111111111111   ; Zelle 0010: alle 33 Bit: 77777777777
d2:             dwb     10           ; Zelle 0011: Wort 2
d2f:            dwb     010          ; Zelle 0012: ebenfalls 2 (nicht oktal gelesen, sonst 8)
                begin                ; Zelle 0013 bis 0015: dwb zwischen begin und bend
bl1:            dwb     1            ; Zelle 0013: Wort 1
bl2:            dwb     10           ; Zelle 0014: Wort 2
bl3:            dwb     11           ; Zelle 0015: Wort 3
                bend
erg:            dw      0            ; Zelle 0016: Ergebnis 1
erg2:           dw      0            ; Zelle 0017: Ergebnis 2
haupt:          211     dvoll        ; Zelle 0020: AC := (dvoll) = 77777777777
                240     erg          ; Zelle 0021: (erg) := AC
                211     dspaet       ; Zelle 0022: AC := (dspaet), Vorwaertsreferenz auf eine dwb-Marke
                240     erg2         ; Zelle 0023: (erg2) := AC
                164     0001         ; Zelle 0024: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0025: Halt
dspaet:         dwb     1100         ; Zelle 0026: Wort 12 = 014 oktal, nach dem Code
ende:           end

; Sollwerte von Hand hergeleitet (Bitfolge rechtsbuendig, je drei Bit eine Oktalziffer). Halt auf 0025, also BZ = 0026.
; AC zuletzt 12 (dspaet). erg = alle 33 Bit gesetzt, erg2 = 12.
;#PRUEFE-START
; BZ=0026 AC=00000000014 US=1
; 0001: 00000000005   # d5
; 0002: 00000000005   # d5f
; 0003: 00000000017   # d15
; 0004: 00000000100   # d64
; 0005: 00000000000   # d0
; 0006: 40000000000   # dz0
; 0007: 52525252525   # dalt
; 0010: 77777777777   # dvoll
; 0011: 00000000002   # d2
; 0012: 00000000002   # d2f
; 0013: 00000000001   # bl1
; 0014: 00000000002   # bl2
; 0015: 00000000003   # bl3
; 0016: 77777777777   # erg
; 0017: 00000000014   # erg2
; 0026: 00000000014   # dspaet
;#PRUEFE-ENDE
