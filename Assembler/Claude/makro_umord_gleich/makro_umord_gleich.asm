; makro_umord_gleich.asm - Test der Makro-Umordnung (Doku 5.6, Annahme a): bei gleicher Endadresse bleibt das Original.
; Zwei Gruppe-4-Makros ohne Programmrest, Aufrufe in der Reihenfolge M4B (n = 04), M4A (n = 06). Original: Kopf 0000 und 0001, M4B 0002 bis 0005,
; M4A 0006 bis 0013, E0 = 0014. Die Umordnung ordnete nach n absteigend (M4A zuerst: 0002 bis 0007, M4B 0010 bis 0013), E1 = 0014 = E0: Gleichstand,
; das Original bleibt, M4B steht weiter vor M4A.
;#DOK-0001 Gleichstand der Endadresse: Umordnung verworfen, Reihenfolge der Aufrufe bleibt (M4B vor M4A)
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
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

                M4B                  ; Gruppe 4, n = 04
                M4A                  ; Gruppe 4, n = 06
ende:           end

; Sollwerte von Hand hergeleitet (Original bleibt), Halt in 0001, BZ = 0002:
; M4B 0002 (erste) und 0005 (letzte); M4A 0006 (erste) und 0013 (letzte).
;#PRUEFE-START
; BZ=0002
; 0002: 00000000711   # M4B, erste Zelle: bleibt vorn
; 0005: 00000000712   # M4B, letzte Zelle
; 0006: 00000000701   # M4A, erste Zelle
; 0013: 00000000702   # M4A, letzte Zelle
;#PRUEFE-ENDE
