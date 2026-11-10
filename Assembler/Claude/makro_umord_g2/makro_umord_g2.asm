; makro_umord_g2.asm - Test der Makro-Umordnung (Doku 5.6): Gruppe 2 (erste Anweisung equ40 *) und Phase B. Zwei Gruppe-2-Makros
; (M2A n = 012, r = 040; M2B n = 050, r = 0100) und zwei Gruppe-4-Makros (M4A n = 06, M4B n = 04). Aufrufe in der Reihenfolge M2A, M4A, M2B, M4B.
; Original: Kopf 0000 bis 0002, M2A 0040 bis 0051, M4A 0052 bis 0057, M2B (0060 auf 0100 aufgerundet) 0100 bis 0147, M4B 0150 bis 0153, Rest 0154 und 0155, E0 = 0156.
; Mit YES: Zaehler an der Einfuegestelle 0005. Phase B: der Gruppe-2-Block mit dem groessten r zuerst (M2B). Vor ihm wird die Luecke bis 0040 mit Gruppe 4
; gefuellt: M4A (6) auf 0005 bis 0012, M4B (4) auf 0013 bis 0016, danach passt nichts mehr. M2B auf 0040 bis 0107, Zaehler 0110; Luecke bis 0140 ohne Gruppe 4;
; M2A auf 0140 bis 0151, E1 = 0152 < E0 = 0156, uebernommen. Die Marke m2a hat den Zaehler vor dem Aufrunden am neuen Platz: 0110.
;#DOK-0001 Gruppe 2 und Phase B: Gruppe-4-Makros fuellen die Luecke bis zur 040-Grenze (Endadresse 0152 statt 0156)
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
kopf:           da      m2a          ; Zelle 0002: Adresse der Marke am Aufruf von M2A (Wert der Marke mal 01000)

M2A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m2a_da
                $IF     $V(m2a_da) = 0
                $SET    m2a_da 1
                equ40   *                        ; erste Anweisung (Gruppe 2)
                dw      0731                     ; erste Rumpfzelle (Marke fuer den Test)
                db      010                      ; 8 Arbeitszellen
                dw      0732                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M2B:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m2b_da
                $IF     $V(m2b_da) = 0
                $SET    m2b_da 1
                equ40   *                        ; erste Anweisung (Gruppe 2)
                dw      0741                     ; erste Rumpfzelle (Marke fuer den Test)
                db      046                      ; 38 Arbeitszellen
                dw      0742                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4A:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4a_da
                $IF     $V(m4a_da) = 0
                $SET    m4a_da 1
                dw      0701                     ; erste Rumpfzelle (Marke fuer den Test)
                db      04                      ; 4 Arbeitszellen
                dw      0702                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

M4B:            MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL m4b_da
                $IF     $V(m4b_da) = 0
                $SET    m4b_da 1
                dw      0711                     ; erste Rumpfzelle (Marke fuer den Test)
                db      02                      ; 2 Arbeitszellen
                dw      0712                     ; letzte Rumpfzelle (Marke fuer den Test)
                $ENDIF
                MEND

m2a:            M2A                  ; Gruppe 2, n = 012, r = 040
                M4A                  ; Gruppe 4, n = 06
                M2B                  ; Gruppe 2, n = 050, r = 0100
                M4B                  ; Gruppe 4, n = 04
t1:             dw      0111         ; Programmrest, Zelle 1
t2:             dw      0222         ; Programmrest, Zelle 2
ende:           end

; Sollwerte von Hand hergeleitet (Umordnung uebernommen), Halt in 0001, BZ = 0002:
; Rest 0003 und 0004; M4A 0005 und 0012; M4B 0013 und 0016; M2B 0040 und 0107; M2A 0140 und 0151; m2a = 0110, da m2a = 00000110000.
;#PRUEFE-START
; BZ=0002
; 0002: 00000110000   # kopf: da m2a, m2a = 0110 (Zaehler vor dem Aufrunden hinter M2B)
; 0003: 00000000111   # t1: Programmrest rueckt auf 0003
; 0004: 00000000222   # t2
; 0005: 00000000701   # M4A, erste Zelle (Luecke vor M2B)
; 0012: 00000000702   # M4A, letzte Zelle
; 0013: 00000000711   # M4B, erste Zelle
; 0016: 00000000712   # M4B, letzte Zelle
; 0040: 00000000741   # M2B, erste Zelle auf der 040-Grenze
; 0107: 00000000742   # M2B, letzte Zelle
; 0140: 00000000731   # M2A, erste Zelle auf der naechsten 040-Grenze
; 0151: 00000000732   # M2A, letzte Zelle
;#PRUEFE-ENDE
