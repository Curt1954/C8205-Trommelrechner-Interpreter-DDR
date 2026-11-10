; makro_umord_g1_nein.asm - Gegenprobe zu makro_umord_g1: ;#MAKROUMORDNEN=NO, alles bleibt an seiner Stelle. Test der Makro-Umordnung (Doku 5.6): ein Makro der Gruppe 1 (erste Anweisung equ100 *) mitten im Programm.
; Das Makro G1UP hat $SPEC TYP=M und beginnt mit equ100 *; sein Rumpf ist 6 Zellen lang (dw-Konstanten 0701 bis 0706).
; Mit ;#MAKROUMORDNEN=NO bleibt alles stehen: der Rumpf liegt auf 0100 bis 0105 und der Programmrest dahinter (0106 bis 0111, Ende 0112).
; Mit =YES (Test makro_umord_g1) wanderte der Rumpf hinter end: Programmrest 0003 bis 0006, der Rumpf auf 0100 bis 0105, Ende 0106 (kleiner, also uebernommen).
; Die Marke g1 am Aufruf steht auf der vom Makroaufruf erzeugten Zeile "g1 equ *" mit dem Zaehlerstand vor dem Aufrunden; ohne Umordnung bleibt sie bei 0003,
; mit =YES wanderte sie mit dem Block auf 0007 (Zaehler hinter dem Programmrest). Die Zelle am haelt da g1 (Adresse mal 01000).
;#DOK-0001 Gruppe-1-Makro mit ;#MAKROUMORDNEN=NO: Rumpf und Programmrest bleiben an ihrer Stelle (Endadresse 0112)
;#MAKROUMORDNEN=NO
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (das UP wird nicht aufgerufen, nur erzeugt)
am:             da      g1           ; Zelle 0002: Adresse der Marke am Aufruf (Wert der Marke mal 01000)

G1UP:           MACRO
                $SPEC   TYP=M CLASS=UMORD ACTION=None
                $GLOBAL g1up_da                  ; Rumpf schon erzeugt? (0 = nein)
                $IF     $V(g1up_da) = 0
                $SET    g1up_da 1                ; ab jetzt gilt: Rumpf ist da
                equ100  *                        ; erste Anweisung: auf die naechste 0100-Grenze (Gruppe 1)
                dw      0701                     ; Rumpfzelle 1
                dw      0702                     ; Rumpfzelle 2
                dw      0703                     ; Rumpfzelle 3
                dw      0704                     ; Rumpfzelle 4
                dw      0705                     ; Rumpfzelle 5
                dw      0706                     ; Rumpfzelle 6
                $ENDIF                           ; Ende von: Rumpf nur beim ersten Aufruf
                MEND

g1:             G1UP                 ; Aufruf mit Marke: erzeugt den Rumpf (Gruppe 1, 6 Zellen)
t1:             dw      0111         ; Programmrest, Zelle 1
t2:             dw      0222         ; Programmrest, Zelle 2
t3:             dw      0333         ; Programmrest, Zelle 3
t4:             dw      0444         ; Programmrest, Zelle 4
ende:           end

; Sollwerte von Hand hergeleitet (keine Umordnung, Original): Kopf 0000 bis 0002, g1 = 0003 (Zaehler vor dem Aufrunden), da g1 = 0003 mal 01000 = 00000003000,
; Rumpf 0100 bis 0105 (equ100 * rundet 0003 auf 0100 auf), Programmrest dahinter 0106 bis 0111. Halt in 0001, BZ = 0002.
;#PRUEFE-START
; BZ=0002
; 0002: 00000003000   # am: da g1, g1 = 0003 vor dem Aufrunden
; 0100: 00000000701   # Rumpfzelle 1 auf der 0100-Grenze
; 0105: 00000000706   # Rumpfzelle 6
; 0106: 00000000111   # t1: Programmrest hinter dem Rumpf
; 0107: 00000000222   # t2
; 0110: 00000000333   # t3
; 0111: 00000000444   # t4
;#PRUEFE-ENDE
