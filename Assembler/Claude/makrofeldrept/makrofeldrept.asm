; makrofeldrept.asm - Test von $V(name(i)) in der Anzahl von $REPT (Assemblerdokumentation 4.16)
;#DOK-0001 Anzahl in $REPT aus Feldelement, auch mit $CALC; der Stand gilt zu Beginn des Makroaufrufs
;#PROT STUFE=2
SETR:           MACRO           ; ohne Parameter
                $DIM r 2        ; Feld r
                $SET r(0) 3     ; r(0) = 3
                $SET r(1) 2     ; r(1) = 2
                MEND
USER:           MACRO           ; ohne Parameter
                $REPT $V(r(1))  ; Anzahl aus dem Feld: Stand zu Beginn des Aufrufs
                dw      7               ; zweimal
                $ENDREPT
                $REPT $V(r(0))
                dw      $Z1             ; 0, 1, 2
                $ENDREPT
                $REPT $CALC($V(r(0))-1)
                dw      9               ; zweimal
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                SETR                 ; kein Code
                USER                 ; Zellen 0001 bis 0007
haupt:          164     0001         ; Zelle 0010: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0011: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0011, BZ danach 0012.
;#PRUEFE-START
; BZ=0012 US=1
; 0001: 00000000007   # erste Wiederholung
; 0002: 00000000007   # zweite Wiederholung
; 0003: 00000000000   # $Z1 = 0
; 0004: 00000000001   # $Z1 = 1
; 0005: 00000000002   # $Z1 = 2
; 0006: 00000000011   # 3 - 1 = 2 mal
; 0007: 00000000011   # zweite Wiederholung
;#PRUEFE-ENDE
