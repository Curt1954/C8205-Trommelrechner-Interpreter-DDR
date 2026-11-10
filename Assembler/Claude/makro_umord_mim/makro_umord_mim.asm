; makro_umord_mim.asm - Test der Makro-Umordnung (Doku 5.6, Annahme 98): Makro im Makro. OUTER (Gruppe 1, equ100 *) ruft in seinem Rumpf INNER (Gruppe 4) auf.
; Der innere Rumpf gehoert zum Block des aeusseren Aufrufs und wandert mit ihm; der zweite Aufruf von INNER hinter OUTER erzeugt nichts und bleibt.
; OUTER: dw, INNER (dw, 4 mal db, dw = 6 Zellen), dw: n = 010. Original: Kopf 0000 bis 0002, OUTER (0003 auf 0100 aufgerundet) 0100 bis 0107, Rest 0110 und 0111, E0 = 0112.
; Mit YES: Rest 0003 und 0004, Zaehler 0005 (Marke outer), Block 0100 bis 0107, E1 = 0110 < E0, uebernommen: ein einziger Block.
;#DOK-0001 Makro im Makro: der innere Rumpf wandert mit dem aeusseren Block (Endadresse 0110 statt 0112)
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
kopf:           da      outer        ; Zelle 0002: Adresse der Marke am Aufruf von OUTER (Wert der Marke mal 01000)

INNER:          MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL inner_da
                $IF     $V(inner_da) = 0
                $SET    inner_da 1
                dw      0711                     ; erste Rumpfzelle (Marke fuer den Test)
                db      04                      ; 4 Arbeitszellen
                dw      0712                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

OUTER:          MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL outer_da
                $IF     $V(outer_da) = 0
                $SET    outer_da 1
                equ100   *                        ; erste Anweisung (Gruppe 1)
                dw      0701                     ; erste Rumpfzelle (Marke fuer den Test)
                INNER                  ; innerer Aufruf (Makro im Makro): sein Rumpf gehoert zum Block des aeusseren
                dw      0702                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

outer:          OUTER                ; Gruppe 1: erzeugt auch den Rumpf von INNER, n = 010
                INNER                ; zweiter Aufruf von INNER: erzeugt nichts
t1:             dw      0111         ; Programmrest, Zelle 1
t2:             dw      0222         ; Programmrest, Zelle 2
ende:           end

; Sollwerte von Hand hergeleitet (Umordnung uebernommen), Halt in 0001, BZ = 0002:
; Rest 0003 und 0004; outer = 0005, da outer = 00000005000; OUTER erste Zelle 0100, INNER 0101 bis 0106, OUTER letzte Zelle 0107; hinter 0107 steht nichts.
;#PRUEFE-START
; BZ=0002
; 0002: 00000005000   # kopf: da outer, outer = 0005 (Zaehler vor dem Aufrunden am neuen Platz)
; 0003: 00000000111   # t1: Programmrest rueckt auf 0003
; 0004: 00000000222   # t2
; 0100: 00000000701   # OUTER, erste Zelle
; 0101: 00000000711   # INNER, erste Zelle (im Block von OUTER)
; 0106: 00000000712   # INNER, letzte Zelle
; 0107: 00000000702   # OUTER, letzte Zelle
; 0110: 00000000000   # hinter dem Block steht nichts (Endadresse 0110)
; 0111: 00000000000   # (im Original stuende hier t2)
;#PRUEFE-ENDE
