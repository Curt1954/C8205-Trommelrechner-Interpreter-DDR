; makro_umord_vergroessert.asm - Test der Makro-Umordnung (Doku 5.6): die Umordnung gilt nur, wenn die Endadresse kleiner wird.
; Ein Gruppe-4-Makro (M4A, n = 06) steht vor einem festen Sprung (equ 0100) mit zwei Datenzellen. Original: Kopf 0000 und 0001, M4A 0002 bis 0007,
; Daten 0100 und 0101, E0 = 0102. Hinter end laege M4A hinter den Daten (0102 bis 0107), E1 = 0110 > E0: Folge der Endadresse-Regel (Doku 5.6, Festlegung 4),
; die Umordnung wird verworfen und das Original bleibt.
;#DOK-0001 Vergroesserung der Endadresse (fester Sprung): Umordnung verworfen, Rumpf bleibt auf 0002
;#MAKROUMORDNEN=YES
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (das UP wird nicht aufgerufen, nur erzeugt)
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

m4a:            M4A                  ; Gruppe 4, n = 06
                equ     0100         ; fester Sprung: Datenbereich auf 0100
d1:             dw      0111         ; Datenzelle 1
d2:             dw      0222         ; Datenzelle 2
ende:           end

; Sollwerte von Hand hergeleitet (Original bleibt), Halt in 0001, BZ = 0002:
; M4A 0002 (erste) und 0007 (letzte), Daten 0100 und 0101; hinter den Daten (0102) steht nichts.
;#PRUEFE-START
; BZ=0002
; 0002: 00000000701   # M4A, erste Zelle: bleibt am Aufruf
; 0007: 00000000702   # M4A, letzte Zelle
; 0100: 00000000111   # d1: fester Sprung
; 0101: 00000000222   # d2
; 0102: 00000000000   # hinter den Daten steht nichts (M4A waere sonst hier)
;#PRUEFE-ENDE
