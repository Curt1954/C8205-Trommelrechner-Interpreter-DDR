; makro_umord_g1.asm - Test der Makro-Umordnung (Doku 5.6): ein Makro der Gruppe 1 (erste Anweisung equ100 *) mitten im Programm.
; Das Makro G1UP hat $SPEC TYP=M und beginnt mit equ100 *; sein Rumpf ist 6 Zellen lang (dw-Konstanten 0701 bis 0706).
; Ohne Umordnung laege der Rumpf auf 0100 bis 0105 und der Programmrest dahinter (0106 bis 0111, Ende 0112).
; Mit ;#MAKROUMORDNEN=YES wandert der Rumpf hinter end: Programmrest 0003 bis 0006, der Rumpf auf 0100 bis 0105, Ende 0106 (kleiner, also uebernommen).
; Die Marke g1 am Aufruf steht auf der vom Makroaufruf erzeugten Zeile "g1 equ *" mit dem Zaehlerstand vor dem Aufrunden und wandert mit dem Block:
; sie hat danach den Wert 0007 (Zaehler hinter dem Programmrest), vorher 0003. Die Zelle am haelt da g1 (Adresse mal 01000).
;#DOK-0001 Makro der Gruppe 1 mitten im Programm wird hinter end verlegt (Umordnung uebernommen, Endadresse 0106 statt 0112)
;#MAKROUMORDNEN=YES
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

; Sollwerte von Hand hergeleitet (Umordnung uebernommen):
; Kopf 0000 bis 0002 (3 Zellen), Programmrest 0003 bis 0006 (4 Zellen), Zaehler 0007 am Ende; g1 = 0007 (Zaehler vor dem Aufrunden),
; da g1 = 0007 mal 01000 = 00000007000; Rumpf ab 0100 (aufgerundet): 0100 bis 0105. Halt in 0001, BZ = 0002.
;#PRUEFE-START
; BZ=0002
; 0002: 00000007000   # am: da g1, g1 = 0007 hinter dem Programmrest
; 0003: 00000000111   # t1: Programmrest rueckt auf 0003
; 0004: 00000000222   # t2
; 0005: 00000000333   # t3
; 0006: 00000000444   # t4
; 0100: 00000000701   # Rumpfzelle 1 auf der 0100-Grenze
; 0101: 00000000702   # Rumpfzelle 2
; 0102: 00000000703   # Rumpfzelle 3
; 0103: 00000000704   # Rumpfzelle 4
; 0104: 00000000705   # Rumpfzelle 5
; 0105: 00000000706   # Rumpfzelle 6
;#PRUEFE-ENDE
