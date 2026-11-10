; makrovarrept.asm - Test von $V(name) in $REPT (Assemblerdokumentation 4.3 und 4.7)
;#DOK-0001 Test von $V in $REPT: Anzahl aus Makro-Variable (Stand zu Beginn des Aufrufs), auch in $CALC
;#PROT STUFE=2
SETN:           MACRO 1
                $SET n $1
                MEND
; FELD: erzeugt n Worte 1, 2, ... n (n = Stand der Variablen zu Beginn des Aufrufs), danach n := n + 1
FELD:           MACRO
                $REPT $V(n)
                dw      $CALC($Z1+1)    ; Wort Nummer Durchlauf+1
                $ENDREPT
                $INC n
                MEND
; REST: erzeugt n-3 Worte 077 (Ausdruck mit $CALC und $V in der Anzahl)
REST:           MACRO
                $REPT $CALC($V(n)-3)
                dw      077             ; Auffuellwort
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                SETN    2            ; n := 2
                FELD                 ; n=2: Zellen 0001, 0002 = 1, 2; danach n=3
                FELD                 ; n=3: Zellen 0003 bis 0005 = 1, 2, 3; danach n=4
                REST                 ; n=4: n-3 = 1 Wort: Zelle 0006 = 077
haupt:          164     0001         ; Zelle 0007: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet: 2 Worte (1, 2), 3 Worte (1, 2, 3), 1 Wort 077; haupt auf 0007, Halt auf 0010, BZ danach 0011.
;#PRUEFE-START
; BZ=0011 US=1
; 0001: 00000000001   # erstes FELD, Wort 1
; 0002: 00000000002   # erstes FELD, Wort 2
; 0003: 00000000001   # zweites FELD, Wort 1
; 0004: 00000000002   # zweites FELD, Wort 2
; 0005: 00000000003   # zweites FELD, Wort 3
; 0006: 00000000077   # REST: 4-3 = 1 Wort
;#PRUEFE-ENDE
