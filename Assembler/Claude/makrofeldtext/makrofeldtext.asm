; makrofeldtext.asm - Test der Textelemente von Makro-Feldern und $V(#name(i)), $V(@name) (Assemblerdokumentation 4.16)
;#DOK-0001 Textelemente, Wechsel zwischen Text und Zahl, $INC auf Feldelement, $V(#t(i)) und $V(@t)
;#PROT STUFE=2
TXT:            MACRO           ; ohne Parameter
                $DIM t 3        ; drei Elemente
                $SET t(0) "ab"  ; Text mit zwei Zeichen
                $SET t(1) "12"  ; Text, der als Zahl lesbar ist
                $SET t(2) 7     ; Zahl
                dw      $V(#t(0))       ; Zeichenzahl 2
                dw      $V(#t(1))       ; Zeichenzahl 2
                dw      $V(t(1))        ; Text 12 als Operand
                dw      $V(t(2))        ; Zahl 7
                $SET t(2) "hallo"       ; Element wechselt von Zahl zu Text
                dw      $V(#t(2))       ; Zeichenzahl 5
                $SET t(0) 4     ; Element wechselt von Text zu Zahl
                dw      $V(t(0))        ; 4
                $INC t(0) 3     ; Zahlenelement um 3 erhoehen
                dw      $V(t(0))        ; 7
                dw      $V(@t)          ; Elementzahl 3
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TXT                  ; Zellen 0001 bis 0010
haupt:          164     0001         ; Zelle 0011: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0012, BZ danach 0013.
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000002   # Zeichenzahl von t(0)
; 0002: 00000000002   # Zeichenzahl von t(1)
; 0003: 00000000014   # Text 12 als Zahl
; 0004: 00000000007   # t(2) = 7
; 0005: 00000000005   # t(2) = hallo hat 5 Zeichen
; 0006: 00000000004   # t(0) als Zahl 4
; 0007: 00000000007   # 4 + 3
; 0010: 00000000003   # Elementzahl
;#PRUEFE-ENDE
