; makrolokal.asm - Test von $LOCAL, lokale Makro-Variablen (Assemblerdokumentation 4.20)
;#DOK-0001 Test lokale Variablen: eigener Zaehler im verschachtelten Makro, Ueberdeckung einer globalen, Neubeginn je Aufruf, $EXIT, $LOCAL im $IF
;#PROT STUFE=2
; GINIT: setzt die globalen Variablen g = 7 und x = 9 (global, bleiben ueber alle Aufrufe erhalten)
GINIT:          MACRO
                $SET g 7
                $SET x 9
                MEND
; SUMME: Summe 1 bis $1 in den lokalen Variablen i und s (s beginnt mit 0); erzeugt die Summe als Wort
SUMME:          MACRO 1
                $LOCAL i s
                $SET i 1
                $WHILE $V(i) <= $1
                $INC s $V(i)
                $INC i
                $ENDWHILE
                dw      $V(s)                   ; Summe 1 bis $1
                MEND
; TABELLE: ruft SUMME in seiner eigenen Schleife ueber das lokale i auf (ohne $LOCAL zerstoert SUMME dieses i)
TABELLE:        MACRO
                $LOCAL i
                $SET i 1
                $WHILE $V(i) <= 4
                SUMME   $V(i)                   ; Summe 1 bis i
                $INC i
                $ENDWHILE
                MEND
; UEBER: vor $LOCAL gilt die globale g (7), danach die lokale g (100); die globale bleibt unberuehrt
UEBER:          MACRO
                dw      $V(g)                   ; globale g
                $LOCAL g
                $SET g 100
                dw      $V(g)                   ; lokale g
                MEND
; ZAEHL: die lokale Variable n beginnt in jedem Aufruf mit 0, beide Aufrufe erzeugen 2
ZAEHL:          MACRO
                $LOCAL n
                $INC n
                $INC n
                dw      $V(n)                   ; immer 2
                MEND
; FRUEHL: lokale x ueberdeckt die globale x; bei $1 = 0 endet das Makro mit $EXIT ohne Code
FRUEHL:         MACRO 1
                $LOCAL x
                $SET x $1
                $IF $V(x) = 0
                $EXIT
                $ENDIF
                dw      $V(x)                   ; lokale x
                MEND
; BEDING: $LOCAL nur im erzeugten Zweig des $IF (bei $1 = 0 entfaellt alles)
BEDING:         MACRO 1
                $IF $1 > 0
                $LOCAL t
                $SET t $CALC($1*2)
                dw      $V(t)                   ; doppelter Parameter
                $ENDIF
                MEND
; GLOB: die globalen g und x sind nach allen Aufrufen unveraendert
GLOB:           MACRO
                dw      $V(g)                   ; global g = 7
                dw      $V(x)                   ; global x = 9
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                GINIT                ; kein Code
                TABELLE              ; Zellen 1 bis 4: 1, 3, 6, 10
                UEBER                ; Zellen 5 und 6: 7, 100
                ZAEHL                ; Zelle 7: 2
                ZAEHL                ; Zelle 8: 2
                FRUEHL 0             ; kein Code ($EXIT)
                FRUEHL 5             ; Zelle 9: 5
                BEDING 3             ; Zelle 10: 6
                BEDING 0             ; kein Code
                GLOB                 ; Zellen 11 und 12: 7, 9
haupt:          164     0001         ; Zelle 13: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 14: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): Summen 1, 3, 6, 10 = oktal 1, 3, 6, 12.
; UEBER: 7 und 100 dezimal = 0144 oktal. ZAEHL 2 und 2. FRUEHL 5 erzeugt 5, BEDING 3 erzeugt 6. GLOB: 7 und 9 dezimal = 011 oktal.
; Halt auf Zelle 14 dezimal = 0016 (oktal), BZ danach 0017.
;#PRUEFE-START
; BZ=0017 US=1
; 0001: 00000000001   # Summe 1 bis 1
; 0002: 00000000003   # Summe 1 bis 2
; 0003: 00000000006   # Summe 1 bis 3
; 0004: 00000000012   # Summe 1 bis 4 = 10
; 0005: 00000000007   # UEBER: globale g
; 0006: 00000000144   # UEBER: lokale g = 100
; 0007: 00000000002   # ZAEHL erster Aufruf
; 0010: 00000000002   # ZAEHL zweiter Aufruf
; 0011: 00000000005   # FRUEHL 5 (FRUEHL 0 erzeugt nichts)
; 0012: 00000000006   # BEDING 3 (BEDING 0 erzeugt nichts)
; 0013: 00000000007   # GLOB: g unveraendert
; 0014: 00000000011   # GLOB: x unveraendert = 9
;#PRUEFE-ENDE
