; makrolokalfeld.asm - Test lokaler Felder mit $LOCAL name(anzahl) (Assemblerdokumentation 4.20)
;#DOK-0001 Test lokale Felder: Anzahl aus Parameter, Neubeginn je Aufruf, Ueberdeckung eines globalen Felds gleichen Namens
;#PROT STUFE=2
; GFELD: globales Feld q mit 3 Elementen, q(0) = 42
GFELD:          MACRO
                $DIM q 3
                $SET q(0) 42
                MEND
; FELDER: lokales Feld q mit $1 Elementen (ueberdeckt das globale q), q(k) = k*k; erzeugt die Quadrate in umgekehrter Reihenfolge
FELDER:         MACRO 1
                $LOCAL q($1) k
                $SET k 0
                $WHILE $V(k) < $1
                $SET q($V(k)) $CALC($V(k)*$V(k))
                $INC k
                $ENDWHILE
                $SET k 0
                $WHILE $V(k) < $1
                dw      $V(q($1-1-$V(k)))       ; Quadrat, von hinten
                $INC k
                $ENDWHILE
                MEND
; GAUS: das globale Feld q ist nach den Aufrufen von FELDER unveraendert (q(0) = 42, Anzahl 3)
GAUS:           MACRO
                dw      $V(q(0))                ; 42
                dw      $V(@q)                  ; Anzahl der Elemente des globalen Felds
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                GFELD                ; kein Code
                FELDER 4             ; Zellen 1 bis 4: 9, 4, 1, 0
                FELDER 2             ; Zellen 5 und 6: 1, 0 (neues Feld mit 2 Elementen, kein Konflikt der Groesse)
                GAUS                 ; Zellen 7 und 8: 42, 3
haupt:          164     0001         ; Zelle 9: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 10: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): FELDER 4: q = 0, 1, 4, 9, von hinten 9, 4, 1, 0
; (9 dezimal = 011 oktal). FELDER 2: q = 0, 1, von hinten 1, 0. GAUS: 42 dezimal = 052 oktal und 3.
; Halt auf Zelle 10 dezimal = 0012 (oktal), BZ danach 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000011   # q(3) = 9
; 0002: 00000000004   # q(2) = 4
; 0003: 00000000001   # q(1) = 1
; 0004: 00000000000   # q(0) = 0
; 0005: 00000000001   # FELDER 2: q(1)
; 0006: 00000000000   # FELDER 2: q(0)
; 0007: 00000000052   # globales q(0) = 42
; 0010: 00000000003   # Anzahl des globalen Felds
;#PRUEFE-ENDE
