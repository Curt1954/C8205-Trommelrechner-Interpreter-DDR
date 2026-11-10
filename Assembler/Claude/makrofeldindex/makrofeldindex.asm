; makrofeldindex.asm - Test des Index als Rechenausdruck mit $V, $P, $# und Parametern (Assemblerdokumentation 4.16)
;#DOK-0001 Index mit Feldzugriff, $P, $# und Parameter; Zuweisung von Element zu Element
;#PROT STUFE=2
IDX:            MACRO 2         ; zwei Parameter
                $DIM z 4        ; Zeiger-Feld
                $SET z(0) 3     ; z(0) = 3
                $SET z(1) 2     ; z(1) = 2
                $SET z(2) 1     ; z(2) = 1
                $SET z(3) 0     ; z(3) = 0
                $DIM w 4        ; Wert-Feld
                $REPT 4
                $SET w($Z1) $CALC($Z1*10)   ; w(i) = 10*i
                $ENDREPT
                dw      $V(w($V(z(0))))     ; Feldzugriff im Index: w(3)
                dw      $V(w($1))           ; Parameter $1 = 2: w(2)
                dw      $V(w($P(2)))        ; $P(2) = 1: w(1)
                dw      $V(w($#-2))         ; $# = 2: w(0)
                dw      $V(w($V(z($V(z(3))))))   ; zweifach geschachtelt: z(3) = 0, z(0) = 3, w(3)
                $SET w(1) $V(w(2))          ; Zuweisung aus einem anderen Element
                dw      $V(w(1))            ; 20
                $SET w(0) $CALC($V(w(1))+1)   ; $CALC mit Feldzugriff als Wert
                dw      $V(w(0))            ; 21
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                IDX     2 1          ; Zellen 0001 bis 0007
haupt:          164     0001         ; Zelle 0010: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0011: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0011, BZ danach 0012.
;#PRUEFE-START
; BZ=0012 US=1
; 0001: 00000000036   # w(z(0)) = w(3)
; 0002: 00000000024   # w($1) = w(2)
; 0003: 00000000012   # w($P(2)) = w(1)
; 0004: 00000000000   # w($#-2) = w(0)
; 0005: 00000000036   # w(z(z(3))) = w(3)
; 0006: 00000000024   # w(1) := w(2)
; 0007: 00000000025   # w(0) := w(1) + 1 = 21
;#PRUEFE-ENDE
