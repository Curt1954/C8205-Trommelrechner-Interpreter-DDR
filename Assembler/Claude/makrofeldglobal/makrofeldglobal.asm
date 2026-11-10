; makrofeldglobal.asm - Test der Lebensdauer von Makro-Feldern und der erneuten Vereinbarung (Assemblerdokumentation 4.16)
;#DOK-0001 Feldwerte bleiben ueber Makroaufrufe erhalten; $DIM mit gleicher Groesse setzt auf 0 zurueck
;#PROT STUFE=2
GA:             MACRO           ; ohne Parameter
                $DIM g 2        ; Feld g, alle Elemente 0
                $SET g(0) 11    ; g(0) = 11
                MEND
GB:             MACRO           ; ohne Parameter
                $INC g(0) 5     ; Feldwert bleibt ueber die Aufrufe erhalten
                $SET g(1) $V(g(0))   ; g(1) = g(0)
                dw      $V(g(1))        ; g(1)
                dw      $V(g(0))        ; g(0)
                MEND
GC:             MACRO           ; ohne Parameter
                $DIM g 2        ; gleiche Groesse: alle Elemente wieder 0
                dw      $V(g(0))        ; 0
                dw      $V(g(1))        ; 0
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                GA                   ; kein Code
                GB                   ; Zellen 0001 und 0002
                GB                   ; Zellen 0003 und 0004
                GC                   ; Zellen 0005 und 0006
haupt:          164     0001         ; Zelle 0007: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet; Halt auf 0010, BZ danach 0011.
;#PRUEFE-START
; BZ=0011 US=1
; 0001: 00000000020   # GB 1: g(1)
; 0002: 00000000020   # GB 1: g(0) = 11 + 5
; 0003: 00000000025   # GB 2: g(1)
; 0004: 00000000025   # GB 2: g(0) = 16 + 5
; 0005: 00000000000   # GC: g(0) nach neuem $DIM
; 0006: 00000000000   # GC: g(1) nach neuem $DIM
;#PRUEFE-ENDE
