; makro_stolperfallen.asm - Regressionsprogramm zu c82ass 1.01-031: vier ehemalige Stolperfallen im Makroformat
; (1) "name: MACRO;Kommentar" ohne Leerzeichen, (2) "$INC n ; Kommentar", (3) Marke aus einem Parameter ("$1: abs 5"),
; (4) $IF mit & und | ohne Klammern: & bindet staerker als |.
m1:             MACRO;Kommentar ohne Leerzeichen hinter MACRO
                dw      7            ; Konstante 7
                MEND
m2:             MACRO 0
                $SET n 1
                $INC n ; Kommentar mit Leerzeichen, kein Ausdruck: n wird um 1 erhoeht
                $INC n
                dw      $V(n)        ; 3
                MEND
m3:             MACRO 1
$1:             abs     5 ; Marke aus dem Parameter
                MEND
m4:             MACRO 0
                $SET a 1
                $SET b 0
                $SET c 0
                $IF $V(a) = 1 | $V(b) = 1 & $V(c) = 1
                dw      1            ; a=1 | (b=1 & c=1) ist wahr; von links nach rechts waere es falsch gewesen
                $ELSE
                dw      2
                $ENDIF
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                m1                   ; Zelle 0001: 7
                m2                   ; Zelle 0002: 3
                m3      x1           ; erzeugt nur das Symbol x1 = 5, keine Zelle
                dw      x1           ; Zelle 0003: 5
                m4                   ; Zelle 0004: 1
haupt:          164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet: 7, 3, 5, 1 in den Zellen 0001 bis 0004.
;#PRUEFE-START
; 0001: 00000000007
; 0002: 00000000003
; 0003: 00000000005
; 0004: 00000000001
;#PRUEFE-ENDE
