; makrovariable.asm - Test der Makro-Variablen $SET, $INC und $V(name) im Makro-Praeprozessor (Assemblerdokumentation 4.7)
;#DOK-0001 Test von $SET, $INC (mit Schrittweite) und $V(name), auch in $CALC; die Variable bleibt ueber mehrere Makroaufrufe erhalten
;#PROT STUFE=2
ZINIT:          MACRO
                $SET zahl 0
                MEND
; NUMMER: erzeugt den Zaehlerstand, erhoeht ihn und erzeugt das Zehnfache des neuen Standes
NUMMER:         MACRO
                dw      $V(zahl)        ; Zaehlerstand vor der Erhoehung
                $INC zahl
                dw      $CALC($V(zahl)*10)   ; Zehnfaches des neuen Standes
                MEND
STEP:           MACRO
                $INC zahl 5
                dw      $V(zahl)        ; Zaehlerstand nach Erhoehung um 5
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ZINIT                ; kein Code, zahl := 0
                NUMMER               ; Zellen 0001 und 0002
                NUMMER               ; Zellen 0003 und 0004
                NUMMER               ; Zellen 0005 und 0006
                STEP                 ; Zelle 0007
                STEP                 ; Zelle 0010
haupt:          164     0001         ; Zelle 0011: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0012, BZ danach 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000000   # NUMMER 1: $V(zahl) = 0
; 0002: 00000000012   # $CALC($V(zahl)*10) nach $INC = 1*10
; 0003: 00000000001   # NUMMER 2: 1
; 0004: 00000000024   # 2*10 = 20
; 0005: 00000000002   # NUMMER 3: 2
; 0006: 00000000036   # 3*10 = 30
; 0007: 00000000010   # STEP: 3 + 5 = 8
; 0010: 00000000015   # STEP: 8 + 5 = 13
;#PRUEFE-ENDE
