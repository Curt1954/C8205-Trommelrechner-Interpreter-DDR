; makroopparam.asm - Test: Operation und Operand eines Makros stammen aus den Aufrufparametern (Assemblerdokumentation 4.2)
;#DOK-0001 Test: eine Makrozeile "$1 $2" (Operation aus Parameter) wird erzeugt und nicht verworfen
;#PROT STUFE=2
OP:             MACRO 2
                $1      $2           ; Operation und Operand aus den Parametern
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
wert:           dw      017          ; Zelle 0001: Konstante
erg:            dw      0            ; Zelle 0002: Ergebnis (initialisiert)
haupt:          OP      211 wert     ; Zelle 0003: 211 wert   (AC := wert)
                OP      240 erg      ; Zelle 0004: 240 erg    (erg := AC)
                164     0001         ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet. Wie mini.asm: Zelle 0001 (017) wird nach Zelle 0002 kopiert; Halt auf 0006, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 AC=00000000017 US=1
; 0002: 00000000017   # erg
;#PRUEFE-ENDE
