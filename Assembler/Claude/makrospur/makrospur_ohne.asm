; makrospur_ohne.asm - Gegenstueck zu makrospur.asm: dieselben Zeilen, aber $TRACE, $NOTE und $DUMP als Kommentar (Assemblerdokumentation 4.24)
;#DOK-0001 Test ohne Fehlersuche im Makro: $TRACE, $NOTE und $DUMP beobachten nur und aendern den erzeugten Code nicht (Gegenstueck makrospur, hier ohne diese Zeilen)
;#PROT STUFE=2
; SUMME: Summe 1 bis $1 in den lokalen Variablen i und s; $TRACE ON verfolgt den Aufruf, $NOTE meldet je Durchlauf, $DUMP zeigt den Stand
SUMME:          MACRO 1
;               $TRACE ON
                $LOCAL i s
                $SET i 1
                $WHILE $V(i) <= $1
                $INC s $V(i)
;               $NOTE i=$V(i) s=$V(s)
                $INC i
                $ENDWHILE
;               $DUMP
                dw      $V(s)                   ; Summe 1 bis $1
                MEND
; TABELLE: ruft SUMME fuer 1 bis 3 (die Spur wird in SUMME eingeschaltet, nicht hier)
TABELLE:        MACRO
                $LOCAL i
                $SET i 1
                $WHILE $V(i) <= 3
                SUMME   $V(i)                   ; Summe 1 bis i
                $INC i
                $ENDWHILE
                MEND
; FELDTEXT: globales Feld q und globaler Text t; Spur im ganzen Aufruf, $DUMP mit Zielen
FELDTEXT:       MACRO
;               $TRACE ON
                $DIM q 4
                $SET q(2) 9
                $SET t "abc"
                $UPPER u "$V(t)"
;               $DUMP q(2) t u
                dw      $V(q(2))                ; q(2) = 9
                MEND
; ZWEIG: $IF und $ELSE mit $EXIT; bei $1 = 0 endet das Makro ohne Code
ZWEIG:          MACRO 1
;               $TRACE ON
                $IF $1 = 0
                $EXIT
                $ELSE
;               $NOTE nicht null: $1
                $ENDIF
                dw      $1                      ; Parameter
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TABELLE              ; Zellen 1 bis 3: 1, 3, 6
                FELDTEXT             ; Zelle 4: 9
                ZWEIG   0            ; kein Code ($EXIT)
                ZWEIG   5            ; Zelle 5: 5
haupt:          164     0001         ; Zelle 6: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 7: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): Summen 1, 3, 6 = oktal 1, 3, 6.
; FELDTEXT erzeugt q(2) = 9 dezimal = 011 oktal. ZWEIG 0 erzeugt nichts, ZWEIG 5 erzeugt 5.
; Halt auf Zelle 7, BZ danach 0010 (oktal).
;#PRUEFE-START
; BZ=0010 US=1
; 0001: 00000000001   # SUMME 1
; 0002: 00000000003   # SUMME 2
; 0003: 00000000006   # SUMME 3
; 0004: 00000000011   # FELDTEXT: q(2) = 9
; 0005: 00000000005   # ZWEIG 5 (ZWEIG 0 erzeugt nichts)
;#PRUEFE-ENDE
