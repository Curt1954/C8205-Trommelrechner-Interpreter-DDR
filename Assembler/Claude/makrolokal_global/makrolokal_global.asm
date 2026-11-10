; makrolokal_global.asm - Test von $GLOBAL mit ;#MAKROLOKAL=1: Werte gehen ueber $GLOBAL nach aussen und bleiben ueber mehrere Aufrufe erhalten (Assemblerdokumentation 4.31)
;#DOK-0001 Test $GLOBAL: globaler Zaehler ohne vorheriges $SET, Ergebnis eines Makros an den Quelltext, lokale Hilfsvariablen verschwinden
;#PROT STUFE=2
;#MAKROLOKAL=1
; NUMMER: globaler Zaehler; $GLOBAL legt ihn mit 0 an, wenn es ihn noch nicht gibt, $INC erhoeht dann die globale Variable
NUMMER:         MACRO
                $GLOBAL zaehler
                $INC zaehler
                dw      $V(zaehler)     ; Zaehlerstand nach der Erhoehung
                MEND
; SUMME: Summe 1 bis $1; i und s sind lokal, das Ergebnis geht ueber die globale Variable gesamt nach aussen
SUMME:          MACRO 1
                $GLOBAL gesamt
                $SET i 1                ; lokal
                $SET s 0                ; lokal
                $WHILE $V(i) <= $1
                $INC s $V(i)
                $INC i
                $ENDWHILE
                $SET gesamt $V(s)       ; global, weil mit $GLOBAL vereinbart
                MEND
                $SET quelltext 1     ; nur damit der Quelltext ausgewertet wird: $V und $DEFINED im Quelltext brauchen eine $-Zeile (Doku 4.1)
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                NUMMER               ; Zelle 0001: 1
                NUMMER               ; Zelle 0002: 2
                SUMME   4            ; kein Code, gesamt := 10
                NUMMER               ; Zelle 0003: 3
                dw      $V(gesamt)   ; Zelle 0004: 10 (der Quelltext liest die globale Variable)
                dw      $DEFINED(s)  ; Zelle 0005: 0 (s war lokal in SUMME und ist weg)
                dw      $DEFINED(gesamt)   ; Zelle 0006: 1
haupt:          164     0001         ; Zelle 0007: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0010: Halt (Zelle 8 dezimal)
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): Zaehlerstaende 1, 2, 3; gesamt = 10 dezimal = 012 oktal;
; $DEFINED(s) = 0, $DEFINED(gesamt) = 1. haupt liegt auf Zelle 7, der Halt auf Zelle 8 (oktal 0010), BZ danach 0011.
;#PRUEFE-START
; BZ=0011 US=1
; 0001: 00000000001   # NUMMER erster Aufruf
; 0002: 00000000002   # NUMMER zweiter Aufruf
; 0003: 00000000003   # NUMMER dritter Aufruf (nach SUMME)
; 0004: 00000000012   # gesamt = 10
; 0005: 00000000000   # $DEFINED(s) = 0
; 0006: 00000000001   # $DEFINED(gesamt) = 1
;#PRUEFE-ENDE
