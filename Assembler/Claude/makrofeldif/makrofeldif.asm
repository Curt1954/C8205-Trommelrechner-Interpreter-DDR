; makrofeldif.asm - Test von $V(name(i)) und $V(@name) in $IF und $ELIF (Assemblerdokumentation 4.16)
;#DOK-0001 Feldzugriffe in den Bedingungen von $IF und $ELIF, auch mit $CALC
;#PROT STUFE=2
IFT:            MACRO           ; ohne Parameter
                $DIM f 3        ; Feld f
                $SET f(0) 5     ; f(0) = 5
                $SET f(1) 9     ; f(1) = 9
                $IF $V(f(0)) < $V(f(1))
                dw      1               ; 5 < 9 gilt
                $ELSE
                dw      2               ; waere falsch
                $ENDIF
                $IF $V(f(1)) = $V(f(0))
                dw      3               ; waere falsch
                $ELIF $CALC($V(f(1))-$V(f(0))) = 4
                dw      4               ; 9 - 5 = 4 gilt
                $ENDIF
                $IF $V(@f) = 3
                dw      5               ; Elementzahl 3
                $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                IFT                  ; Zellen 0001 bis 0003
haupt:          164     0001         ; Zelle 0004: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0005: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0005, BZ danach 0006.
;#PRUEFE-START
; BZ=0006 US=1
; 0001: 00000000001   # 5 < 9
; 0002: 00000000004   # 9 - 5 = 4
; 0003: 00000000005   # Elementzahl 3
;#PRUEFE-ENDE
