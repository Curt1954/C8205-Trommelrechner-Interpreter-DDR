; makropruef.asm - Test von $TYPSYM, $ERROR und $WARN im Makro-Praeprozessor (Assemblerdokumentation 4.2 und 4.5)
;#DOK-0001 Test der Parameterpruefung $TYPSYM und der Makro-Meldungen $WARN (Warnung bei Aufruf) und $ERROR (im nicht erzeugten Zweig wirkungslos)
;#PROT STUFE=2
; KOPIERE q z: kopiert Zelle q nach Zelle z; beide Parameter muessen Symbole sein ($TYPSYM)
KOPIERE:        MACRO 2
                $PR1 $TYPSYM
                $PR2 $TYPSYM
                $IF $1 = $2
                $ERROR Quelle $1 und Ziel $2 sind dieselbe Zelle
                $ENDIF
                $IF $1 = quelle
                $WARN Die Zelle $1 wird nach $2 kopiert
                $ENDIF
                211     $1              ; AC := Zelle $1
                240     $2              ; Zelle $2 := AC
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
quelle:         dw      5            ; Zelle 0001: Quelle
ziel:           dw      0            ; Zelle 0002: Ziel
haupt:          KOPIERE quelle ziel  ; Zellen 0003 und 0004: Warnung des Makros, kein Fehler
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
ende:           end

; Sollwerte von Hand hergeleitet: ziel (0002) erhaelt den Wert von quelle (5); Halt auf 0006, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 US=1
; 0002: 00000000005   # ziel = quelle = 5
;#PRUEFE-ENDE
