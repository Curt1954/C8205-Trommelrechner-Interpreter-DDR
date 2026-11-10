; makro_umord_zweiter.asm - Test der Makro-Umordnung (Doku 5.6, Annahme j): der zweite Packversuch. Der Programmrest beginnt mit equ10 *; sein Zaehlerstand
; haengt davon ab, ob die Rumpfbloecke davor stehen. Original: Kopf 0000 bis 0002, M1A (equ100 *, n = 010) 0100 bis 0107, M4B (n = 010) 0110 bis 0117,
; M4A (n = 070) 0120 bis 0207, equ10 * ohne Luecke, Rest 0210 und 0211, E0 = 0212.
; Schaetzung des Zaehlers an der Einfuegestelle: 0212 minus die herausgenommenen Zellen (0003 bis 0210 = 0205) = 0005. Wirklich: Kopf 3 Zellen, equ10 * auf 0010,
; Rest 0010 und 0011, Zaehler 0012. Mit der Schaetzung 0005 passte M4A (n = 070) in die Luecke bis 0100 (59 Zellen), mit dem genauen Wert 0012 nicht (54 Zellen).
; Erster Versuch (Schaetzung): M4A, M1A, M4B, M4A reicht dann bis 0101, M1A rundet auf 0200 auf, E1 = 0220 > E0: wuerde verworfen.
; Zweiter Versuch (genau): Luecke 0012 bis 0100 nimmt M4B (0012 bis 0021), dann M1A 0100 bis 0107, M4A (Phase C) 0110 bis 0177, E1 = 0200 < E0 = 0212, uebernommen.
;#DOK-0001 Zweiter Packversuch mit dem genauen Zaehler (equ10 * im Programmrest): uebernommen mit Endadresse 0200 statt 0212
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
kopf:           da      m4a          ; Zelle 0002: Adresse der Marke am Aufruf von M4A (Wert der Marke mal 01000)

M1A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m1a_da
                $IF     $V(m1a_da) = 0
                $SET    m1a_da 1
                equ100   *                        ; erste Anweisung (Gruppe 1)
                dw      0731                     ; erste Rumpfzelle (Marke fuer den Test)
                db      06                      ; 6 Arbeitszellen
                dw      0732                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4B:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4b_da
                $IF     $V(m4b_da) = 0
                $SET    m4b_da 1
                dw      0711                     ; erste Rumpfzelle (Marke fuer den Test)
                db      06                      ; 6 Arbeitszellen
                dw      0712                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4a_da
                $IF     $V(m4a_da) = 0
                $SET    m4a_da 1
                dw      0701                     ; erste Rumpfzelle (Marke fuer den Test)
                db      066                      ; 54 Arbeitszellen
                dw      0702                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

                M1A                  ; Gruppe 1, n = 010
                M4B                  ; Gruppe 4, n = 010
m4a:            M4A                  ; Gruppe 4, n = 070
                equ10   *            ; Ausrichtung: der Zaehlerstand hinter dem Kopf haengt davon ab, ob die Bloecke davor stehen
t1:             dw      0111         ; Programmrest, Zelle 1
t2:             dw      0222         ; Programmrest, Zelle 2
ende:           end

; Sollwerte von Hand hergeleitet (Umordnung uebernommen), Halt in 0001, BZ = 0002:
; Rest nach equ10 *: 0010 und 0011; M4B 0012 bis 0021; M1A 0100 bis 0107; M4A 0110 bis 0177; m4a = 0110, da m4a = 00000110000; hinter 0177 steht nichts.
;#PRUEFE-START
; BZ=0002
; 0002: 00000110000   # kopf: da m4a, m4a = 0110 (Zaehler vor M4A im zweiten Versuch)
; 0010: 00000000111   # t1: Programmrest auf der 010-Grenze
; 0011: 00000000222   # t2
; 0012: 00000000711   # M4B, erste Zelle (Luecke vor M1A)
; 0021: 00000000712   # M4B, letzte Zelle
; 0100: 00000000731   # M1A, erste Zelle
; 0107: 00000000732   # M1A, letzte Zelle
; 0110: 00000000701   # M4A, erste Zelle (Phase C, hinter M1A)
; 0177: 00000000702   # M4A, letzte Zelle
; 0200: 00000000000   # hinter M4A steht nichts (Endadresse 0200)
;#PRUEFE-ENDE
