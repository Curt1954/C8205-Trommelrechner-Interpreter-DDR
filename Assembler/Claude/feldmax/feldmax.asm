; feldmax -- Summe und Maximum eines Feldes aus 8 Zahlen
; ERZEUGT von Assembler/Claude/feldmax/gen/feldmax_gen.py -- nicht von Hand aendern, Aenderungen im Generator.
; Belegung: 38 Zellen (Code 23, Daten 12, Literale 3), Grenze 128.
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7532 (7600 minus 38 Zellen), Ausrichtung egal.
                start                ; Zaehlung beginnt bei 0000
                241     summe          ; summe := 0, AC := 0
                241     i              ; i := 0, AC := 0
                210     @feld          ; AC := Index + Anfangsadresse feld
                251     0              ; AC := feld[Index] (R-Lesebefehl)
                240     max            ; max := AC
schl:           211     i              ; AC := Index i
                210     @feld          ; AC := Index + Anfangsadresse feld
                251     0              ; AC := feld[Index] (R-Lesebefehl)
                240     wert           ; wert := AC
                210     summe          ; AC := AC + summe
                240     summe          ; summe := AC
                211     wert           ; wert <= max: max bleibt
                330     max            ; wert <= max: max bleibt
                140     weiter         ; wert <= max: max bleibt
                240     max            ; max := wert
weiter:         211     i              ; AC := i
                210     #01000         ; AC := AC + 01000
                240     i              ; i := AC
                330     #010000        ; i = n (in Adresseneinheiten): fertig
                170     fertig         ; i = n (in Adresseneinheiten): fertig
                000     schl           ; weiter bei schl
fertig:         164     0001           ; Diagnoseausgabe (nur im Test)
                020     0              ; Halt: Ergebnis in summe und max
                begin                  ; Feld feld (zusammengehoerige Worte)
feld:           dw      07             ; feld[0] = 7
                dw      -03            ; feld[1] = -3
                dw      014            ; feld[2] = 12
                dw      05             ; feld[3] = 5
                dw      -011           ; feld[4] = -9
                dw      014            ; feld[5] = 12
                dw      0              ; feld[6] = 0
                dw      04             ; feld[7] = 4
                bend                   ; Ende Feld feld
summe:          db      01             ; Arbeitszelle summe
max:            db      01             ; Arbeitszelle max
i:              db      01             ; Arbeitszelle i
wert:           db      01             ; Arbeitszelle wert
                end                  ; Programmende

; Sollwerte aus dem Python-Modell des Generators (unabhaengig vom Assemblerprogramm).
;#PRUEFE-START
; BZ=0027 US=1
; 0037: 00000000034   # summe
; 0040: 00000000014   # max
;#PRUEFE-ENDE
