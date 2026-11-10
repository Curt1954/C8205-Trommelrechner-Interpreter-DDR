; makrosymbol2.asm - Test: von Makros erzeugte abs- und equ-Symbole in $CALC eines anderen Makros
;                    (Assemblerdokumentation 4.18, c82ass ab 1.01-011); der Quelltext hat keine $-Zeile (Pass 0 ohne Vorabauswertung)
;#DOK-0001 Test: BREITE erzeugt breite2=12, TIEFE tief=7, QUAD q1 bis q3 in $WHILE, LAGE lagem=0100 und spurm=lagem+020
;#PROT STUFE=2
BREITE:         MACRO   1
breite2:        abs     $1                          ; Zahlensymbol, Wert = Parameter 1 (hier der Ausdruck 3*4)
                MEND
TIEFE:          MACRO   1
tief:           abs     $1                          ; Zahlensymbol, Wert = Parameter 1
                MEND
LAGE:           MACRO
lagem:          equ     0100                        ; equ mit Zahlenwert 64 (setzt den Befehlszaehler, 3.3.8)
spurm:          equ     lagem+020                   ; verweist auf ein equ des Makros: 64+16 = 80
                MEND
QUAD:           MACRO   1
                $SET    i 1
                $WHILE  $V(i) <= $1
q$V(i):         abs     $CALC($V(i)*$V(i))          ; q1 = 1, q2 = 4, q3 = 9
                $INC    i
                $ENDWHILE
                MEND
N1:             MACRO
                dw      $CALC(breite2*2)            ; 12*2 = 24
                MEND
N2:             MACRO
                dw      $CALC(spurm-lagem)          ; 80-64 = 16
                dw      $CALCO4(spurm)              ; 80 oktal 0120
                dw      $CALC(art(lagem))           ; equ mit Zahlenwert: 2
                MEND
N3:             MACRO
                dw      $CALC(q1+q2+q3)             ; 1+4+9 = 14
                MEND
N4:             MACRO
                dw      $CALC(tief+1)               ; 7+1 = 8
                MEND
OUTER:          MACRO
                TIEFE   7                           ; erzeugt tief im aeusseren Makro ...
                N4                                  ; ... und das verschachtelte Makro N4 liest es
                MEND
N5:             MACRO
                dw      $CALC(art(breite2))         ; abs mit Zahlenwert: 1
                dw      $CALC(def(gibtsnicht))      ; nicht vorhanden: 0
                MEND
N6:             MACRO
                $REPT   breite2/4                   ; 12/4 = 3 Durchlaeufe
                dw      $CALC($Z1+breite2)          ; 12, 13, 14
                $ENDREPT
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                BREITE  3*4          ; erzeugt breite2 = 12 (keine Zelle)
                QUAD    3            ; erzeugt q1 bis q3 (keine Zelle)
                N1                   ; Zelle 0001
                N3                   ; Zelle 0002
                OUTER                ; Zelle 0003
                N5                   ; Zellen 0004 und 0005
                N6                   ; Zellen 0006 bis 0010
                dw      breite2      ; Zelle 0011: das erzeugte Symbol ist auch im Programm ein Symbol
haupt:          020     0            ; Zelle 0012: Halt
                LAGE                 ; erzeugt lagem und spurm; die beiden equ setzen den Befehlszaehler auf 0100, dann 0120
                N2                   ; Zellen 0120 bis 0122
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0012, BZ danach 0013.
; 12*2=24=030; 1+4+9=14=016; 7+1=8=010; art(breite2)=1, def(gibtsnicht)=0; $Z1+12: 12=014, 13=015, 14=016; breite2=12=014;
; 80-64=16=020; $CALCO4(80)=0120; art(lagem)=2 (equ).
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000030   # breite2*2 = 24
; 0002: 00000000016   # q1+q2+q3 = 14
; 0003: 00000000010   # tief+1 = 8 (aus dem verschachtelten Makro)
; 0004: 00000000001   # art(breite2) = 1
; 0005: 00000000000   # def(gibtsnicht) = 0
; 0006: 00000000014   # $REPT breite2/4, Durchlauf 0: 12
; 0007: 00000000015   # Durchlauf 1: 13
; 0010: 00000000016   # Durchlauf 2: 14
; 0011: 00000000014   # dw breite2 = 12
; 0120: 00000000020   # spurm-lagem = 16
; 0121: 00000000120   # $CALCO4(spurm) = 0120
; 0122: 00000000002   # art(lagem) = 2
;#PRUEFE-ENDE
