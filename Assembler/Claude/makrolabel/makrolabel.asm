; makrolabel.asm - Test der generischen Makro-Labels bei mehr als 26 Aufrufen (Assemblerdokumentation 4)
;#DOK-0001 Test: 30 Aufrufe von ZAEHL und 4 von ZAEHL2, beide mit dem Label ML0001%; fruehere Fassung: Label-Kollision ab dem 27. Aufruf
;#PROT STUFE=2
; ZAEHL: springt ueber eine Zelle (Label ML0001%) und zaehlt zahl um 1 hoch; die uebersprungene Zelle 240 fehler darf nie laufen
ZAEHL:          MACRO
                000     ML0001%      ; Sprung ueber die naechste Zelle
                240     fehler       ; wird uebersprungen (sonst fehler := AC)
ML0001%:        211     zahl         ; AC := zahl
                210     eins         ; AC := zahl + 1
                240     zahl         ; zahl := AC
                MEND
; ZAEHL2: wie ZAEHL, zaehlt aber zahl2
ZAEHL2:         MACRO
                000     ML0001%      ; Sprung ueber die naechste Zelle
                240     fehler       ; wird uebersprungen (sonst fehler := AC)
ML0001%:        211     zahl2        ; AC := zahl2
                210     eins         ; AC := zahl2 + 1
                240     zahl2        ; zahl2 := AC
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
eins:           dw      1            ; Zelle 0001: Konstante 1
zahl:           dw      0            ; Zelle 0002: Zaehler von ZAEHL
zahl2:          dw      0            ; Zelle 0003: Zaehler von ZAEHL2
fehler:         dw      0            ; Zelle 0004: bleibt 0, wenn nur die richtigen Spruenge ausgefuehrt werden
haupt:          ZAEHL                ; Zelle 0005: erste Zelle des ersten Aufrufs
                ZAEHL                ; Aufruf 2 von ZAEHL
                ZAEHL                ; Aufruf 3 von ZAEHL
                ZAEHL                ; Aufruf 4 von ZAEHL
                ZAEHL                ; Aufruf 5 von ZAEHL
                ZAEHL                ; Aufruf 6 von ZAEHL
                ZAEHL                ; Aufruf 7 von ZAEHL
                ZAEHL                ; Aufruf 8 von ZAEHL
                ZAEHL                ; Aufruf 9 von ZAEHL
                ZAEHL                ; Aufruf 10 von ZAEHL
                ZAEHL                ; Aufruf 11 von ZAEHL
                ZAEHL                ; Aufruf 12 von ZAEHL
                ZAEHL                ; Aufruf 13 von ZAEHL
                ZAEHL                ; Aufruf 14 von ZAEHL
                ZAEHL                ; Aufruf 15 von ZAEHL
                ZAEHL                ; Aufruf 16 von ZAEHL
                ZAEHL                ; Aufruf 17 von ZAEHL
                ZAEHL                ; Aufruf 18 von ZAEHL
                ZAEHL                ; Aufruf 19 von ZAEHL
                ZAEHL                ; Aufruf 20 von ZAEHL
                ZAEHL                ; Aufruf 21 von ZAEHL
                ZAEHL                ; Aufruf 22 von ZAEHL
                ZAEHL                ; Aufruf 23 von ZAEHL
                ZAEHL                ; Aufruf 24 von ZAEHL
                ZAEHL                ; Aufruf 25 von ZAEHL
                ZAEHL                ; Aufruf 26 von ZAEHL
                ZAEHL                ; Aufruf 27 von ZAEHL
                ZAEHL                ; Aufruf 28 von ZAEHL
                ZAEHL                ; Aufruf 29 von ZAEHL
                ZAEHL                ; Aufruf 30 von ZAEHL
                ZAEHL2               ; Aufruf 1 von ZAEHL2 (anderes Makro, gleiche Labelnummer ML0001%)
                ZAEHL2               ; Aufruf 2 von ZAEHL2 (anderes Makro, gleiche Labelnummer ML0001%)
                ZAEHL2               ; Aufruf 3 von ZAEHL2 (anderes Makro, gleiche Labelnummer ML0001%)
                ZAEHL2               ; Aufruf 4 von ZAEHL2 (anderes Makro, gleiche Labelnummer ML0001%)
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet. Zellen 0000 bis 0004 sind Sprung und Daten; ab 0005 folgen 34 Aufrufe zu je 5 Zellen = 170 Zellen
; (dezimal). 5 + 170 = 175 dezimal = 0257 oktal: 164 steht auf 0257, der Halt (020) auf 0260, BZ danach 0261.
; zahl = 30 = 036 oktal, zahl2 = 4, fehler = 0; AC = 4 (letzter Aufruf ZAEHL2 speichert den Wert 4).
;#PRUEFE-START
; BZ=0261 AC=00000000004 US=1
; 0002: 00000000036   # zahl: 30 Aufrufe von ZAEHL
; 0003: 00000000004   # zahl2: 4 Aufrufe von ZAEHL2
; 0004: 00000000000   # fehler: keine uebersprungene Zelle wurde ausgefuehrt
;#PRUEFE-ENDE
