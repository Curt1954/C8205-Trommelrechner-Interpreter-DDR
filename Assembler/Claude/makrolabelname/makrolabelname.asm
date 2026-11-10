; makrolabelname.asm - Test der lesbaren lokalen Labels im Makro (Assemblerdokumentation 4.3, c82ass ab 1.00-064)
;#DOK-0001 Test: Labels der Form name% (statt ML0001%) in Makros: einfacher Sprung, Namen ende% und weiterende% in einem Makro, Schleife mit $REPT, Label als Parameter eines verschachtelten Makros
;#PROT STUFE=2
; ZAEHL: springt ueber eine Zelle (Label weiter%) und zaehlt zahl um 1 hoch; die uebersprungene Zelle 240 fehler darf nie laufen
ZAEHL:          MACRO
                000     weiter%      ; Sprung ueber die naechste Zelle
                240     fehler       ; wird uebersprungen (sonst fehler := AC)
weiter%:        211     zahl         ; AC := zahl
                210     eins         ; AC := zahl + 1
                240     zahl         ; zahl := AC
                MEND
; PAAR: zwei Labels, deren eines mit dem Namen des anderen endet (ende% und weiterende%); zaehlt zahl2 um 1 hoch
PAAR:           MACRO
                000     weiterende%  ; Sprung auf die dritte Zelle; enthaelt ende% als Wortende, das nicht ersetzt werden darf
ende%:          240     fehler       ; wird uebersprungen
weiterende%:    211     zahl2        ; AC := zahl2
                210     eins         ; AC := zahl2 + 1
                240     zahl2        ; zahl2 := AC
                MEND
; SCHLEIFE: drei Durchlaeufe mit dem Label naechst% (je Durchlauf _0, _1, _2); zaehlt zahl3 um 3 hoch
SCHLEIFE:       MACRO
                $REPT 3
                000     naechst%     ; Sprung ueber die naechste Zelle
                240     fehler       ; wird uebersprungen
naechst%:       211     zahl3        ; AC := zahl3
                210     eins         ; AC := zahl3 + 1
                240     zahl3        ; zahl3 := AC
                $ENDREPT
                MEND
; SPRUNG: springt auf den Parameter und ueberspringt dabei eine Zelle
SPRUNG:         MACRO 1
                000     $1           ; Sprung auf das uebergebene Label
                240     fehler       ; wird uebersprungen
                MEND
; AUSSEN: uebergibt sein lokales Label ziel% an SPRUNG; zaehlt zahl4 um 1 hoch
AUSSEN:         MACRO
                SPRUNG  ziel%        ; verschachtelter Aufruf mit dem lokalen Label als Parameter
ziel%:          211     zahl4        ; AC := zahl4
                210     eins         ; AC := zahl4 + 1
                240     zahl4        ; zahl4 := AC
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
eins:           dw      1            ; Zelle 0001: Konstante 1
zahl:           dw      0            ; Zelle 0002: Zaehler von ZAEHL
zahl2:          dw      0            ; Zelle 0003: Zaehler von PAAR
zahl3:          dw      0            ; Zelle 0004: Zaehler von SCHLEIFE
zahl4:          dw      0            ; Zelle 0005: Zaehler von AUSSEN
fehler:         dw      0            ; Zelle 0006: bleibt 0, wenn nur die richtigen Spruenge ausgefuehrt werden
haupt:          ZAEHL                ; Zelle 0007: erster Aufruf von ZAEHL
                ZAEHL                ; zweiter Aufruf von ZAEHL (eigene Buchstaben fuer weiter%)
                PAAR                 ; erster Aufruf von PAAR
                PAAR                 ; zweiter Aufruf von PAAR
                SCHLEIFE             ; erster Aufruf von SCHLEIFE
                SCHLEIFE             ; zweiter Aufruf von SCHLEIFE
                AUSSEN               ; erster Aufruf von AUSSEN
                AUSSEN               ; zweiter Aufruf von AUSSEN
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet. Zellen 0000 bis 0006 sind Sprung und Daten, ab 0007 folgen die Aufrufe:
; 2 mal ZAEHL (je 5 Zellen) + 2 mal PAAR (je 5) + 2 mal SCHLEIFE (je 15) + 2 mal AUSSEN (je 5) = 10 + 10 + 30 + 10 = 60 Zellen (dezimal).
; 7 + 60 = 67 dezimal = 0103 oktal: 164 steht auf 0103, der Halt (020) auf 0104, BZ danach 0105.
; zahl = 2, zahl2 = 2, zahl3 = 6, zahl4 = 2, fehler = 0; AC = 2 (der letzte Aufruf AUSSEN speichert zahl4 = 2).
;#PRUEFE-START
; BZ=0105 AC=00000000002 US=1
; 0002: 00000000002   # zahl: 2 Aufrufe von ZAEHL
; 0003: 00000000002   # zahl2: 2 Aufrufe von PAAR
; 0004: 00000000006   # zahl3: 2 Aufrufe von SCHLEIFE mit je 3 Durchlaeufen
; 0005: 00000000002   # zahl4: 2 Aufrufe von AUSSEN
; 0006: 00000000000   # fehler: keine uebersprungene Zelle wurde ausgefuehrt
;#PRUEFE-ENDE
