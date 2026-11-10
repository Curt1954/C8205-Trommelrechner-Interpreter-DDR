; makrostrcode.asm - Test der Zeichenkettenfunktionen im Ablauf des Makros: Parameter, $IF-Zweige, $REPT, lokale Ziele, Grenzen (Assemblerdokumentation 4.21)
;#DOK-0001 Test Zeichenketten im Makroablauf: $1 und $CALC in Zahlen, inaktive Zweige, Wechsel Zahl/Text, lokales Ziel, Text mit 200 Zeichen
;#PROT STUFE=2
; ZAHL: Zahlenargumente aus $1 und $CALC; $1 = 3 gibt Start 3 mit 4 Zeichen (CDEF), danach der Rest ab 6 (FGH)
ZAHL:           MACRO 1
                $SUBSTR z "ABCDEFGH" $1 $CALC($1+1)
                dw      $V(#z)                  ; CDEF hat 4 Zeichen
                $ORD n "$V(z)"
                dw      $V(n)                   ; C = 67
                $SUBSTR z "ABCDEFGH" $CALC($1*2)
                dw      $V(#z)                  ; FGH hat 3 Zeichen
                MEND
; ZWEIG: im nicht erzeugten Zweig steht ein ungueltiger Aufruf; er darf nicht ausgefuehrt werden
ZWEIG:          MACRO 1
                $IF $1 = 1
                $CHR z 66
                $ORD n "$V(z)"
                dw      $V(n)                   ; B = 66
                $ELSE
                $CHR z 300
                $ENDIF
                dw      7                       ; immer erzeugt
                MEND
; ZWEIG2: bei $1 = 2 gilt nur der $ELIF-Zweig; $IF- und $ELSE-Zweig enthalten Fehler und bleiben unausgefuehrt
ZWEIG2:         MACRO 1
                $IF $1 = 1
                $SUBSTR z "abc" 9
                $ELIF $1 = 2
                $UPPER z "ok"
                dw      $V(#z)                  ; OK hat 2 Zeichen
                $ELSE
                $VAL z "12a"
                $ENDIF
                dw      8                       ; immer erzeugt
                MEND
; ARTW: das Ziel w wechselt die Art: Zahl 5, dann Text x, dann Zahl 9, dann $INC
ARTW:           MACRO
                $SET w 5
                $UPPER w "x"
                dw      $V(#w)                  ; Text X hat 1 Zeichen
                $VAL w "9"
                dw      $V(w)                   ; Zahl 9
                $INC w
                dw      $V(w)                   ; Zahl 10
                MEND
; SETZ: setzt die globale Textvariable z auf gg (kein Code)
SETZ:           MACRO
                $SET z "gg"
                MEND
; LOK: lokale Variable z und lokales Feld f als Ziel; die globale z bleibt unberuehrt
LOK:            MACRO
                $LOCAL z f(2)
                $UPPER z "lokal"
                dw      $V(#z)                  ; lokale z: LOKAL hat 5 Zeichen
                $SUBSTR f(1) "xyz" 2 2
                dw      $V(#f(1))               ; lokales Feldelement: YZ hat 2 Zeichen
                MEND
; PRUEFZ: die globale z ist unveraendert gg
PRUEFZ:         MACRO
                dw      $V(#z)                  ; globale z hat 2 Zeichen
                MEND
; GLEICH: Vergleich von Texten mit Leerzeichen ueber $STRCMP und $IF
GLEICH:         MACRO
                $SET x "ein text"
                $STRCMP r "$V(x)" "ein text"
                $IF $V(r) = 0
                dw      11                      ; gleich
                $ELSE
                dw      22                      ; ungleich
                $ENDIF
                $STRCMP r "$V(x)" "ein  text"
                $IF $V(r) = 0
                dw      33                      ; gleich
                $ELSE
                dw      44                      ; ungleich (zwei Leerzeichen)
                $ENDIF
                MEND
; REPTD: die Funktionen laufen in der Reihenfolge der erzeugten Zeilen auch im $REPT (Zaehler $Z1)
REPTD:          MACRO
                $REPT 3
                $SUBSTR z "ABC" $CALC($Z1+1) 1
                $ORD n "$V(z)"
                dw      $V(n)                   ; A, B, C = 65, 66, 67
                $ENDREPT
                MEND
; LANG: Text mit genau 200 Zeichen (Grenze) durch Verdoppeln; die Zeile bleibt unter 255 Zeichen
LANG:           MACRO
                $SET s "0123456789"
                $SET s "$V(s)$V(s)"
                $SET s "$V(s)$V(s)"
                $SET u "$V(s)"
                $SET s "$V(s)$V(s)"
                $SET s "$V(s)$V(s)"
                $SET t "$V(s)$V(u)"
                dw      $V(#t)                  ; 160 + 40 = 200
                $SUBSTR z "$V(t)" 198 3
                $VAL n "$V(z)"
                dw      $V(n)                   ; letzte drei Zeichen 789
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ZAHL    3            ; Zellen 1 bis 3 (dezimal)
                ZWEIG   1            ; Zellen 4 und 5
                ZWEIG2  2            ; Zellen 6 und 7
                ARTW                 ; Zellen 8 bis 10
                SETZ                 ; kein Code
                LOK                  ; Zellen 11 und 12
                PRUEFZ               ; Zelle 13
                GLEICH               ; Zellen 14 und 15
                $UPPER q "abc"       ; ausserhalb eines Makros uebergangen, kein Code
                REPTD                ; Zellen 16 bis 18
                LANG                 ; Zellen 19 und 20
haupt:          164     0001         ; Zelle 21: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 22: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal).
; ZAHL 3: 4 Zeichen, C = 67, 3 Zeichen = oktal 4, 103, 3. ZWEIG 1: B = 66 und 7 = oktal 102, 7. ZWEIG2 2: 2 und 8 = oktal 2, 10.
; ARTW: 1, 9, 10 = oktal 1, 11, 12. LOK: 5 und 2. PRUEFZ: 2. GLEICH: 11 und 44 = oktal 13, 54. REPTD: 65, 66, 67 = oktal 101, 102, 103.
; LANG: 200 = oktal 310; 789 = oktal 1425.
; haupt = Zelle 21 (oktal 0025), Halt auf Zelle 22 (oktal 0026), BZ danach 0027.
;#PRUEFE-START
; BZ=0027 US=1
; 0001: 00000000004   # ZAHL: CDEF hat 4 Zeichen
; 0002: 00000000103   # ZAHL: C = 67
; 0003: 00000000003   # ZAHL: FGH hat 3 Zeichen
; 0004: 00000000102   # ZWEIG: B = 66
; 0005: 00000000007   # ZWEIG: Zeile nach dem $ENDIF
; 0006: 00000000002   # ZWEIG2: OK hat 2 Zeichen
; 0007: 00000000010   # ZWEIG2: Zeile nach dem $ENDIF (8)
; 0010: 00000000001   # ARTW: Text X
; 0011: 00000000011   # ARTW: Zahl 9
; 0012: 00000000012   # ARTW: Zahl 10 nach $INC
; 0013: 00000000005   # LOK: lokale z
; 0014: 00000000002   # LOK: lokales Feldelement
; 0015: 00000000002   # PRUEFZ: globale z unveraendert
; 0016: 00000000013   # GLEICH: gleich = 11
; 0017: 00000000054   # GLEICH: zwei Leerzeichen = ungleich = 44
; 0020: 00000000101   # REPTD: A
; 0021: 00000000102   # REPTD: B
; 0022: 00000000103   # REPTD: C
; 0023: 00000000310   # LANG: 200 Zeichen
; 0024: 00000001425   # LANG: 789
;#PRUEFE-ENDE
