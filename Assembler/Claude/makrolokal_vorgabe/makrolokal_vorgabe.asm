; makrolokal_vorgabe.asm - Test von ;#MAKROLOKAL=1: $SET ohne $LOCAL legt im Makroaufruf eine lokale Variable an (Assemblerdokumentation 4.31)
;#DOK-0001 Test Schalter MAKROLOKAL: SUMME und TABELLE benutzen beide i und s ohne $LOCAL und stoeren sich nicht
;#PROT STUFE=2
;#MAKROLOKAL=1
; SUMME: Summe 1 bis $1 in den (implizit lokalen) Variablen i und s; erzeugt die Summe als Wort
SUMME:          MACRO 1
                $SET i 1                ; lokal, ohne $LOCAL
                $SET s 0                ; lokal
                $WHILE $V(i) <= $1
                $INC s $V(i)
                $INC i
                $ENDWHILE
                dw      $V(s)           ; Summe 1 bis $1
                MEND
; TABELLE: ruft SUMME in einer Schleife ueber ihr eigenes i auf (waere i global, zerstoerte SUMME es)
TABELLE:        MACRO
                $SET i 1                ; lokal, getrennt von dem i in SUMME
                $SET s 100              ; lokal, getrennt von dem s in SUMME
                $WHILE $V(i) <= 4
                SUMME   $V(i)           ; Summe 1 bis i
                $INC i
                $ENDWHILE
                dw      $V(s)           ; bleibt 100, weil SUMME nur sein eigenes s aendert
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TABELLE              ; Zellen 1 bis 5: 1, 3, 6, 10 und 100
haupt:          164     0001         ; Zelle 6: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 7: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): Summen 1, 3, 6, 10 = oktal 1, 3, 6, 12;
; letzte Zelle 100 dezimal = 0144 oktal. haupt liegt auf Zelle 6, der Halt auf Zelle 7, BZ danach 0010.
;#PRUEFE-START
; BZ=0010 US=1
; 0001: 00000000001   # Summe 1 bis 1
; 0002: 00000000003   # Summe 1 bis 2
; 0003: 00000000006   # Summe 1 bis 3
; 0004: 00000000012   # Summe 1 bis 4 = 10
; 0005: 00000000144   # s von TABELLE unveraendert = 100
;#PRUEFE-ENDE
