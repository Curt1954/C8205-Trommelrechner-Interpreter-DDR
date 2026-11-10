; makrolokal_quelltext.asm - Test von ;#MAKROLOKAL=1 mit einer Variablen aus dem Quelltext: Lesen und $INC ohne, Schreiben mit $GLOBAL (Assemblerdokumentation 4.31)
;#DOK-0001 Test Quelltext-Variable: $SET im Quelltext ist global; ein Makro liest sie ohne $GLOBAL, schreibt sie nur mit $GLOBAL; $SET ohne $GLOBAL verdeckt sie
;#PROT STUFE=2
;#MAKROLOKAL=1
; LIES: liest die globale Variable basis ohne $GLOBAL
LIES:           MACRO
                dw      $V(basis)       ; globaler Wert
                MEND
; SCHREIB: $GLOBAL macht das $SET zur Zuweisung an die globale Variable
SCHREIB:        MACRO
                $GLOBAL basis
                $SET basis $CALC($V(basis)+1)
                MEND
; VERDECKT: $SET ohne $GLOBAL legt eine lokale Variable an, die die globale verdeckt
VERDECKT:       MACRO
                $SET basis 1
                dw      $V(basis)       ; 1 (lokal)
                MEND
; INKR: $INC ohne $GLOBAL erhoeht die globale Variable, wenn es keine lokale gibt
INKR:           MACRO
                $INC basis
                MEND
                $SET basis 40        ; im Quelltext ausserhalb von Makros: global
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                LIES                 ; Zelle 0001: 40
                SCHREIB              ; kein Code, basis := 41
                VERDECKT             ; Zelle 0002: 1, die globale bleibt 41
                INKR                 ; kein Code, basis := 42
                dw      $V(basis)    ; Zelle 0003: 42
                LIES                 ; Zelle 0004: 42
haupt:          164     0001         ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Adressen und Werte oktal): 40 dezimal = 050; 42 dezimal = 052. Halt auf Zelle 6, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 US=1
; 0001: 00000000050   # LIES: 40
; 0002: 00000000001   # VERDECKT: lokale basis = 1
; 0003: 00000000052   # Quelltext: basis = 42 (40, SCHREIB 41, INKR 42)
; 0004: 00000000052   # LIES: 42
;#PRUEFE-ENDE
