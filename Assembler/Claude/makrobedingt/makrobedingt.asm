; makrobedingt.asm - Test: bedingte Assemblierung ueber ein Hilfsmakro und im Quelltext (Assemblerdokumentation 4.1, Beispiel TESTTEIL)
;#DOK-0001 Bedingte Assemblierung ueber Hilfsmakro: Schalter per def (vereinbart und nicht vereinbart), Schalter als Parameter (1 und 0), $IF im Quelltext (falsche Bedingung), Marke auf der Aufrufzeile
;#PROT STUFE=2
; Fall A: TESTTEIL ist das Beispiel der Doku (Schalter DEBUG, hinter end vereinbart): fuenf Anweisungen entstehen.
; Fall B: TESTAUS fragt nach AUS, das nirgends vereinbart ist: es entsteht nichts.
; Fall C und D: TESTPAR hat den Schalter als Parameter: bei 1 entstehen fuenf Anweisungen, bei 0 nichts.
; Fall E: ein $IF im normalen Quelltext wirkt wie im Makro (c82ass ab 1.01-008): bei falscher Bedingung entsteht die Anweisung dahinter nicht.
TESTTEIL:       MACRO                   ; Fall A: Schalter ueber def, Beispiel der Doku
                $IF $CALC(def(DEBUG)) = 1
                240     merk                    ; Akkumulator sichern
                211     zaehler                 ; Zaehler laden
                210     eins                    ; um 1 erhoehen
                240     zaehler                 ; Zaehler zurueckspeichern
                211     merk                    ; Akkumulator wiederherstellen
                $ENDIF
                MEND                            ; Ende von TESTTEIL
TESTAUS:        MACRO                   ; Fall B: wie TESTTEIL, aber Schalter AUS ist nicht vereinbart; Zaehler zb
                $IF $CALC(def(AUS)) = 1
                240     merk                    ; Akkumulator sichern
                211     zb                      ; Zaehler laden
                210     eins                    ; um 1 erhoehen
                240     zb                      ; Zaehler zurueckspeichern
                211     merk                    ; Akkumulator wiederherstellen
                $ENDIF
                MEND                            ; Ende von TESTAUS
TESTPAR:        MACRO 2                 ; Fall C und D: Parameter 1 ist der Schalter, Parameter 2 der Zaehler
                $IF $1 = 1
                240     merk                    ; Akkumulator sichern
                211     $2                      ; Zaehler laden
                210     eins                    ; um 1 erhoehen
                240     $2                      ; Zaehler zurueckspeichern
                211     merk                    ; Akkumulator wiederherstellen
                $ENDIF
                MEND                            ; Ende von TESTPAR
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
wert:           dw      017             ; Zelle 0001: Konstante, der Akkumulator soll sie behalten
merk:           dw      0               ; Zelle 0002: Merkzelle fuer den Akkumulator
zaehler:        dw      0               ; Zelle 0003: Zaehler Fall A (soll 1 werden)
zb:             dw      0               ; Zelle 0004: Zaehler Fall B (bleibt 0)
zc:             dw      0               ; Zelle 0005: Zaehler Fall C (soll 1 werden)
zd:             dw      0               ; Zelle 0006: Zaehler Fall D (bleibt 0)
ze:             dw      0               ; Zelle 0007: Fall E (bleibt 0)
eins:           dw      1               ; Zelle 0010: Konstante 1
haupt:          211     wert            ; Zelle 0011: Akkumulator laden (017)
                TESTTEIL                ; Zellen 0012 bis 0016: Fall A, DEBUG ist vereinbart
ohne:           TESTAUS                 ; keine Zelle: Fall B; die Marke ohne bleibt und hat die Adresse 0017
                TESTPAR 1 zc            ; Zellen 0017 bis 0023: Fall C, Schalter 1
                TESTPAR 0 zd            ; keine Zelle: Fall D, Schalter 0
                $IF $CALC(def(AUS)) = 1 ; Fall E: im Quelltext ausgewertet, AUS ist nicht vereinbart, die Bedingung ist falsch
                240     ze              ; entsteht nicht (sonst stuende hier ze := Akkumulator 017)
                $ENDIF                  ; Fall E: Ende der Bedingung, keine Zelle
                164     0001            ; Zelle 0024: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0025: Halt
ende:           end
DEBUG:          abs     1               ; Schalter fuer TESTTEIL; ohne diese Zeile entfiele Fall A

; Sollwerte von Hand hergeleitet. Akkumulator := 017 (Zelle 0011). A und C sichern ihn in merk (017), erhoehen ihren
; Zaehler von 0 auf 1 und stellen den Akkumulator wieder her; B und D erzeugen nichts (Zaehler bleiben 0).
; Fall E erzeugt nichts (AUS nicht vereinbart): ze bleibt 0, 164 0001 liegt auf 0024, der Halt auf 0025, BZ danach 0026.
; Zellen 0012, 0016, 0017 und 0023 legen die Lage fest: 240 merk, 211 merk, 240 merk, 211 merk; 0024 und 0025: 164 0001 und 020.
;#PRUEFE-START
; BZ=0026 AC=00000000017 US=1
; 0002: 00000000017   # merk
; 0003: 00000000001   # zaehler (Fall A)
; 0004: 00000000000   # zb (Fall B)
; 0005: 00000000001   # zc (Fall C)
; 0006: 00000000000   # zd (Fall D)
; 0007: 00000000000   # ze (Fall E): bleibt 0, 240 ze entsteht nicht
; 0012: 00000002240   # Fall A: 240 merk
; 0016: 00000002211   # Fall A: 211 merk
; 0017: 00000002240   # Fall C: 240 merk
; 0023: 00000002211   # Fall C: 211 merk
; 0024: 00000001164   # Fall E: hier steht schon 164 0001, nichts davor
; 0025: 00000000020   # Halt 020 auf 0025
;#PRUEFE-ENDE
