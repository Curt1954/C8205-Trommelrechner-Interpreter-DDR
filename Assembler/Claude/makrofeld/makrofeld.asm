; makrofeld.asm - Test der Makro-Felder $DIM, $SET name(i) und $V(name(i)) (Assemblerdokumentation 4.16)
;#DOK-0001 Acht Quadrate in einem Feld berechnen und in umgekehrter Reihenfolge ausgeben
;#PROT STUFE=2
QUADRATE:       MACRO           ; ohne Parameter
                $DIM q 8        ; Feld q mit 8 Elementen, alle 0
                $REPT 8
                $SET q($Z1) $CALC($Z1*$Z1)   ; q(i) = i*i
                $ENDREPT
                $REPT 8
                dw      $V(q(7-$Z1))         ; Elemente von hinten nach vorn
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                QUADRATE             ; Zellen 0001 bis 0010
haupt:          164     0001         ; Zelle 0011: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet: q(i) = i*i, ausgegeben von q(7) bis q(0); Halt auf 0012, BZ danach 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000061   # q(7) = 49
; 0002: 00000000044   # q(6) = 36
; 0003: 00000000031   # q(5) = 25
; 0004: 00000000020   # q(4) = 16
; 0005: 00000000011   # q(3) = 9
; 0006: 00000000004   # q(2) = 4
; 0007: 00000000001   # q(1) = 1
; 0010: 00000000000   # q(0) = 0
;#PRUEFE-ENDE
