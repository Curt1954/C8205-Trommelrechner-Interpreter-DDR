; makrolokal_ohne.asm - dasselbe Muster wie makrolokal_quelltext, aber ohne ;#MAKROLOKAL=1: Verhalten wie bisher, $GLOBAL ohne sichtbare Wirkung (Assemblerdokumentation 4.31)
;#DOK-0001 Test Vorgabe ohne Schalter: Variablen sind global, $SET im Makro ueberschreibt die globale Variable, $GLOBAL legt nur eine fehlende mit 0 an
;#PROT STUFE=2
; LIES: liest die globale Variable basis
LIES:           MACRO
                dw      $V(basis)       ; globaler Wert
                MEND
; SCHREIB: $GLOBAL ist ohne Schalter ueberfluessig, das $SET wirkt ohnehin global
SCHREIB:        MACRO
                $GLOBAL basis
                $SET basis $CALC($V(basis)+1)
                MEND
; VERDECKT: ohne Schalter ueberschreibt $SET die globale Variable
VERDECKT:       MACRO
                $SET basis 1
                dw      $V(basis)       ; 1 (global)
                MEND
; INKR: erhoeht die globale Variable
INKR:           MACRO
                $INC basis
                MEND
; NEU: $GLOBAL legt eine noch fehlende globale Variable mit 0 an
NEU:            MACRO
                $GLOBAL neu
                dw      $V(neu)         ; 0
                MEND
                $SET basis 40        ; im Quelltext: global
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                LIES                 ; Zelle 0001: 40
                SCHREIB              ; kein Code, basis := 41
                VERDECKT             ; Zelle 0002: 1, die globale basis ist jetzt 1
                INKR                 ; kein Code, basis := 2
                dw      $V(basis)    ; Zelle 0003: 2
                LIES                 ; Zelle 0004: 2
                NEU                  ; Zelle 0005: 0
haupt:          164     0001         ; Zelle 0006: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0007: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Adressen und Werte oktal): 40 dezimal = 050. Ohne Schalter bleibt VERDECKT nicht lokal: basis = 1, INKR = 2.
; Halt auf Zelle 7, BZ danach 0010.
;#PRUEFE-START
; BZ=0010 US=1
; 0001: 00000000050   # LIES: 40
; 0002: 00000000001   # VERDECKT: global basis = 1
; 0003: 00000000002   # Quelltext: basis = 2 (VERDECKT hat die globale ueberschrieben)
; 0004: 00000000002   # LIES: 2
; 0005: 00000000000   # NEU: neu = 0
;#PRUEFE-ENDE
