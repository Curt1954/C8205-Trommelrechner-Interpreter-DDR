; dwf.asm - Test der Anweisung dwf (gebrochene Festkommazahl aus Dezimalbruch, Doku 3.3.20)
; Das Komma steht zwischen z0 und z1; das Wort ist x * 2^32, gerundet (Mitte weg von 0), bei negativem x im Zweierkomplement (33 Bit).
; Zahlenbereich -1 bis 1 - 2^-32; der Bereich wird nach dem Runden geprueft.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
f05:            dwf     0.5                                       ; Zelle 0001: 1/2: nur z1, Wort 20000000000
f025:           dwf     0.25                                      ; Zelle 0002: 1/4: nur z2
f075:           dwf     0.75                                      ; Zelle 0003: z1 und z2
fm05:           dwf     -0.5                                      ; Zelle 0004: Zweierkomplement, z0 = 1
fm1:            dwf     -1                                        ; Zelle 0005: kleinster Wert, nur z0 gesetzt
f0:             dwf     0                                         ; Zelle 0006: Wort 0
f01:            dwf     0.1                                       ; Zelle 0007: 0.1 * 2^32 = 429496729.6, gerundet 429496730
fm01:           dwf     -0.1                                      ; Zelle 0010: Zweierkomplement von 0.1
fmin:           dwf     0.00000000023283064365386962890625        ; Zelle 0011: 2^-32, kleinste positive Zahl
fmax:           dwf     0.99999999976716935634613037109375        ; Zelle 0012: 1 - 2^-32, groesster Wert
ffuehr:         dwf     00.50                                     ; Zelle 0013: fuehrende 0 ist dezimal, wie 0.5
fplus:          dwf     +0.5                                      ; Zelle 0014: Vorzeichen +
fnull2:         dwf     0.0                                       ; Zelle 0015: Wort 0
fnull3:         dwf     -0                                        ; Zelle 0016: keine negative Null: Wort 0
fnull4:         dwf     0.00000000001                             ; Zelle 0017: rundet zu 0: Wort 0
fhalb:          dwf     0.000000000116415321826934814453125       ; Zelle 0020: genau 2^-33, Mitte: weg von 0, Wort 1
fmhalb:         dwf     -0.000000000116415321826934814453125      ; Zelle 0021: Mitte, weg von 0: Wort von -1/2^32
fm1r:           dwf     -1.0000000001                             ; Zelle 0022: rundet auf -1, Bereich erst nach dem Runden geprueft
flang:          dwf     0.50000000000000000000000000000000000000000000000000; Zelle 0023: lange Ziffernfolge, wie 0.5
f0375:          dwf     0.375                                     ; Zelle 0024: z2 und z3
                begin                ; Zelle 0025 bis 0027: dwf zwischen begin und bend
bl1:            dwf     0.125                                     ; Zelle 0025: z3
bl2:            dwf     -0.125                                    ; Zelle 0026: Zweierkomplement
bl3:            dwf     0.0625                                    ; Zelle 0027: z4
                bend
erg:            dw      0                                         ; Zelle 0030: Ergebnis 1
erg2:           dw      0                                         ; Zelle 0031: Ergebnis 2
haupt:          211     fmax                                      ; Zelle 0032: AC := (fmax)
                240     erg                                       ; Zelle 0033: (erg) := AC
                211     dspaet                                    ; Zelle 0034: AC := (dspaet), Vorwaertsreferenz auf eine dwf-Marke
                240     erg2                                      ; Zelle 0035: (erg2) := AC
                164     0001                                      ; Zelle 0036: Diagnoseausgabe (nur im Test)
                020     0                                         ; Zelle 0037: Halt
dspaet:         dwf     0.375                                     ; Zelle 0040: nach dem Code
ende:           end

; Sollwerte aus der exakten Bruchrechnung hergeleitet (Python, Fraction) und mit den Beispielen der Doku verglichen. Halt auf 0037, also BZ = 0040.
; AC zuletzt das Wort von dspaet. erg = Wort von fmax, erg2 = Wort von dspaet.
;#PRUEFE-START
; BZ=0040 AC=14000000000 US=1
; 0001: 20000000000   # f05
; 0002: 10000000000   # f025
; 0003: 30000000000   # f075
; 0004: 60000000000   # fm05
; 0005: 40000000000   # fm1
; 0006: 00000000000   # f0
; 0007: 03146314632   # f01
; 0010: 74631463146   # fm01
; 0011: 00000000001   # fmin
; 0012: 37777777777   # fmax
; 0013: 20000000000   # ffuehr
; 0014: 20000000000   # fplus
; 0015: 00000000000   # fnull2
; 0016: 00000000000   # fnull3
; 0017: 00000000000   # fnull4
; 0020: 00000000001   # fhalb
; 0021: 77777777777   # fmhalb
; 0022: 40000000000   # fm1r
; 0023: 20000000000   # flang
; 0024: 14000000000   # f0375
; 0025: 04000000000   # bl1
; 0026: 74000000000   # bl2
; 0027: 02000000000   # bl3
; 0030: 37777777777   # erg
; 0031: 14000000000   # erg2
; 0040: 14000000000   # dspaet
;#PRUEFE-ENDE
