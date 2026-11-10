; makroparamvar.asm - Test der variablen Parameterzahl "MACRO n+" und $P(i) im Makro-Praeprozessor (Assemblerdokumentation 4.13)
;#DOK-0001 Test von MACRO 1+ (mindestens ein Parameter, beliebig viele weitere), $P(i) mit $Z1, $# und in $CALC, auch mit mehr als 9 Parametern
;#PROT STUFE=2
; LISTE a [b ...]: erzeugt Anzahl, danach alle Parameter, dann erster + letzter und $1 * 2
LISTE:          MACRO 1+
                dw      $#              ; Zahl der uebergebenen Parameter
                $REPT $#
                dw      $P($Z1+1)       ; Parameter Nummer $Z1+1
                $ENDREPT
                dw      $CALC($P(1)+$P($#))   ; erster plus letzter Parameter
                dw      $CALC($1*2)     ; fester Parameter $1 mal 2
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                LISTE   5            ; Zellen 0001 bis 0004: ein Parameter
                LISTE   3 4 7        ; Zellen 0005 bis 0012: drei Parameter
                LISTE   1 2 3 4 5 6 7 8 9 10 11   ; Zellen 0013 bis 0030: elf Parameter (mehr als $9)
haupt:          164     0001         ; Zelle 0031: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0032: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zahlen im dw sind dezimal, die Sollwerte oktal); Halt auf 0032, BZ danach 0033.
;#PRUEFE-START
; BZ=0033 US=1
; 0001: 00000000001   # Anzahl: 1
; 0002: 00000000005   # Parameter 1 = 5
; 0003: 00000000012   # 5+5 = 10 = 012
; 0004: 00000000012   # 5*2 = 10 = 012
; 0005: 00000000003   # Anzahl: 3
; 0006: 00000000003   # Parameter 1 = 3
; 0007: 00000000004   # Parameter 2 = 4
; 0010: 00000000007   # Parameter 3 = 7
; 0011: 00000000012   # 3+7 = 10 = 012
; 0012: 00000000006   # 3*2 = 6
; 0013: 00000000013   # Anzahl: 11 = 013
; 0014: 00000000001   # Parameter 1
; 0015: 00000000002   # Parameter 2
; 0016: 00000000003   # Parameter 3
; 0017: 00000000004   # Parameter 4
; 0020: 00000000005   # Parameter 5
; 0021: 00000000006   # Parameter 6
; 0022: 00000000007   # Parameter 7
; 0023: 00000000010   # Parameter 8
; 0024: 00000000011   # Parameter 9
; 0025: 00000000012   # Parameter 10 (nur mit $P erreichbar)
; 0026: 00000000013   # Parameter 11 (nur mit $P erreichbar)
; 0027: 00000000014   # 1+11 = 12 = 014
; 0030: 00000000002   # 1*2 = 2
;#PRUEFE-ENDE
