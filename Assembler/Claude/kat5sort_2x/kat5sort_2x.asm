; kat5sort_2x: Mehrfachaufruf von KAT5SORT, der Rumpf darf nur einmal entstehen (zwei Felder, ein UP)
                start                 ; Zaehlung beginnt bei 0000
haupt:          .LD     @fa           ; AC := Adresse des Feldes A
                .STO    sort+1        ; Parameter 1 (Zelle Marke+1)
                .LD     #03           ; AC := 3 (Anzahl der Worte)
                .STO    sort+2        ; Parameter 2 (Zelle Marke+2)
                025     sort          ; Feld A sortieren
                .LD     @fb           ; AC := Adresse des Feldes B
                .STO    sort+1        ; Parameter 1
                .LD     #02           ; AC := 2 (Anzahl der Worte)
                .STO    sort+2        ; Parameter 2
                025     sort          ; Feld B sortieren (derselbe Rumpf)
                .STOP   0             ; Halt
fa:             dw      03            ; A[0] = 3
                dw      01            ; A[1] = 1
                dw      02            ; A[2] = 2
fb:             dw      07            ; B[0] = 7
                dw      05            ; B[1] = 5
sort:           KAT5SORT              ; erster Aufruf: erzeugt den Rumpf
                KAT5SORT              ; zweiter Aufruf: erzeugt nichts (Mehrfachspeicherung unterbunden)
                KAT5SORT              ; dritter Aufruf: erzeugt nichts
ende:           end                   ; Programmende

;#PRUEFE-START
; BZ=0013 US=1
; 0013: 00000000001   # fa+0
; 0014: 00000000002   # fa+1
; 0015: 00000000003   # fa+2
; 0016: 00000000005   # fb+0
; 0017: 00000000007   # fb+1
;#PRUEFE-ENDE
