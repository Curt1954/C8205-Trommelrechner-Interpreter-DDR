; makrovorgabe.asm - Test der Vorgabewerte $DEFAULT und der Parameteranzahl $# im Makro-Praeprozessor (Assemblerdokumentation 4.6)
;#DOK-0001 Test von $DEFAULT (fehlende Parameter am Ende erhalten Vorgabewerte) und $# (Zahl der uebergebenen Parameter, auch in $CALC und $REPT)
;#PROT STUFE=2
; LADE a [b [c]]: b hat die Vorgabe 5, c die Vorgabe 0; erzeugt Anzahl, b, c, a + Anzahl und Anzahl Worte 077
LADE:           MACRO 3
                $DEFAULT 2 5
                $DEFAULT 3 0
                dw      $#              ; Zahl der uebergebenen Parameter
                dw      $2              ; zweiter Parameter (oder Vorgabe)
                dw      $3              ; dritter Parameter (oder Vorgabe)
                dw      $CALC($1+$#)    ; erster Parameter plus Anzahl
                $REPT $#
                dw      077             ; je uebergebenem Parameter ein Wort
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                LADE    10           ; Zellen 0001 bis 0005: ein Parameter
                LADE    10 6         ; Zellen 0006 bis 0013: zwei Parameter
                LADE    10 6 7       ; Zellen 0014 bis 0022: drei Parameter
haupt:          164     0001         ; Zelle 0023: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0024: Halt
ende:           end

; Sollwerte von Hand hergeleitet (siehe Kommentar je Zelle); Halt auf 0024, BZ danach 0025.
;#PRUEFE-START
; BZ=0025 US=1
; 0001: 00000000001   # Anzahl uebergeben: 1
; 0002: 00000000005   # Vorgabe $2 = 5
; 0003: 00000000000   # Vorgabe $3 = 0
; 0004: 00000000013   # $1+$# = 10+1 = 11 = 013
; 0005: 00000000077   # $REPT $# = 1 Wort
; 0006: 00000000002   # Anzahl: 2
; 0007: 00000000006   # $2 uebergeben = 6
; 0010: 00000000000   # Vorgabe $3 = 0
; 0011: 00000000014   # 10+2 = 12 = 014
; 0012: 00000000077   # Wort 1 von 2
; 0013: 00000000077   # Wort 2 von 2
; 0014: 00000000003   # Anzahl: 3
; 0015: 00000000006   # $2 = 6
; 0016: 00000000007   # $3 = 7
; 0017: 00000000015   # 10+3 = 13 = 015
; 0020: 00000000077   # Wort 1 von 3
; 0021: 00000000077   # Wort 2 von 3
; 0022: 00000000077   # Wort 3 von 3
;#PRUEFE-ENDE
