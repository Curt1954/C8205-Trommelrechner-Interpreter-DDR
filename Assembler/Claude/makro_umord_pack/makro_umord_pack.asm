; makro_umord_pack.asm - Test der Makro-Umordnung (Doku 5.6): Packen mit Luecke, Phase A. Ein Gruppe-1-Makro (M1A, n = 040, r = 0100) und drei
; Gruppe-4-Makros (M4A n = 014, M4B n = 010, M4C n = 06; jedes Rumpfende ist ein dw, db steht nur in der Mitte). Aufrufe in der Reihenfolge M4A, M1A, M4B, M4C.
; Original: Kopf 0000 bis 0002, M4A 0003 bis 0016, M1A auf 0100 bis 0137, M4B 0140 bis 0147, M4C 0150 bis 0155, Programmrest 0156 und 0157, E0 = 0160.
; Mit YES: Zaehler an der Einfuegestelle 0005 (Kopf 3 + Rest 2). Phase A: Luecke 0005 bis 0100: das groesste Passende zuerst, M4A (12) -> 0005 bis 0020,
; dann M4B (8) -> 0021 bis 0030, dann M4C (6) -> 0031 bis 0036; Zaehler 0037, nichts passt mehr; M1A auf 0100 bis 0137; E1 = 0140 < E0, uebernommen.
;#DOK-0001 Packen mit Luecke (Phase A): Gruppe-4-Makros fuellen die Luecke vor dem Gruppe-1-Block (Endadresse 0140 statt 0160)
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
kopf:           da      m4a          ; Zelle 0002: Adresse der Marke am Aufruf von M4A (Wert der Marke mal 01000)

M4A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4a_da
                $IF     $V(m4a_da) = 0
                $SET    m4a_da 1
                dw      0701                     ; erste Rumpfzelle (Marke fuer den Test)
                db      012                      ; 012 Arbeitszellen
                dw      0702                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4B:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4b_da
                $IF     $V(m4b_da) = 0
                $SET    m4b_da 1
                dw      0711                     ; erste Rumpfzelle (Marke fuer den Test)
                db      06                      ; 06 Arbeitszellen
                dw      0712                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4C:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4c_da
                $IF     $V(m4c_da) = 0
                $SET    m4c_da 1
                dw      0721                     ; erste Rumpfzelle (Marke fuer den Test)
                db      04                      ; 04 Arbeitszellen
                dw      0722                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M1A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m1a_da
                $IF     $V(m1a_da) = 0
                $SET    m1a_da 1
                equ100  *                        ; erste Anweisung: auf die naechste 0100-Grenze (Gruppe 1)
                dw      0731                     ; erste Rumpfzelle (Marke fuer den Test)
                db      036                      ; 036 Arbeitszellen
                dw      0732                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

m4a:            M4A                  ; Gruppe 4, n = 014
                M1A                  ; Gruppe 1, n = 040
                M4B                  ; Gruppe 4, n = 010
                M4C                  ; Gruppe 4, n = 06
t1:             dw      0111         ; Programmrest, Zelle 1
t2:             dw      0222         ; Programmrest, Zelle 2
ende:           end

; Sollwerte von Hand hergeleitet (Umordnung uebernommen), Halt in 0001, BZ = 0002:
; Rest 0003 und 0004; M4A 0005 (erste) und 0020 (letzte); M4B 0021 und 0030; M4C 0031 und 0036; M1A 0100 und 0137.
; Marke m4a: Zaehler an der neuen Stelle 0005, da m4a = 0005 mal 01000 = 00000005000.
;#PRUEFE-START
; BZ=0002
; 0002: 00000005000   # kopf: da m4a, m4a = 0005
; 0003: 00000000111   # t1: Programmrest rueckt auf 0003
; 0004: 00000000222   # t2
; 0005: 00000000701   # M4A, erste Zelle (Luecke, groesster Gruppe-4-Block zuerst)
; 0020: 00000000702   # M4A, letzte Zelle
; 0021: 00000000711   # M4B, erste Zelle
; 0030: 00000000712   # M4B, letzte Zelle
; 0031: 00000000721   # M4C, erste Zelle
; 0036: 00000000722   # M4C, letzte Zelle
; 0100: 00000000731   # M1A, erste Zelle auf der 0100-Grenze
; 0137: 00000000732   # M1A, letzte Zelle
;#PRUEFE-ENDE
