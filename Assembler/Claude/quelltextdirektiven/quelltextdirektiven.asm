; quelltextdirektiven.asm - Test: $-Direktiven im normalen Quelltext, ausserhalb eines Makros (Assemblerdokumentation 4.1, c82ass ab 1.01-008)
;#DOK-0001 $SET, $INC, $V (in Marke, Operation, Operand, $CALC), $IF/$ELIF/$ELSE mit def, verschachteltes $IF, $REPT mit $Z1 und Marke, $REPT 0, $WHILE, Makroaufruf nach $SET, Kommentar mit $V( bleibt Text
;#PROT STUFE=2
; Alle Direktivzeilen stehen im normalen Quelltext und erzeugen selbst keine Zelle; die Zeilen dazwischen werden uebersetzt.
; Fall A: $SET, $INC (mit und ohne Schrittweite), $V im Operanden und in $CALC (Zellen 0001 bis 0003).
; Fall B: $V in der Marke (m4), Zelle 0004.
; Fall C bis F: $IF wahr, $ELIF wahr, $ELSE, verschachteltes $IF mit $V (je eine Zelle 0005 bis 0010).
; Fall G und H: $REPT 3 mit $Z1 und Marke w$Z1 (Zellen 0011 bis 0013), $REPT 0 (nichts).
; Fall I: $WHILE mit $INC, Quadrate bis 30 (Zellen 0014 bis 0020, dezimal 1 4 9 16 25).
; Fall J: Hilfsmakro NUM im Quelltext, aufgerufen nach $SET (Zellen 0021 bis 0023: 1, 2, 6).
; Fall K: Kommentar mit $V( bleibt Text (Zelle 0024). Fall L: $V in Operand und Operation (Zellen 0027 bis 0032).
NUM:            MACRO                   ; Hilfsmakro: erzeugt den Stand von z und erhoeht z um 1
                dw      $V(z)           ; Stand von z
; naechste Zeile: $INC ohne Ausdruck steht ohne Kommentar (ein Kommentar dahinter ergibt einen Fehler, auch im Makro)
                $INC    z
                MEND                    ; Ende von NUM
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                $SET    n 3             ; Fall A: n := 3
a1:             dw      $V(n)           ; Zelle 0001: 3
                $INC    n 2             ; n := 5
a2:             dw      $V(n)           ; Zelle 0002: 5
; naechste Zeile: $INC n ohne Ausdruck erhoeht n um 1 (n := 6)
                $INC    n
a3:             dw      $CALC($V(n)*2)  ; Zelle 0003: 12 dezimal = 014 oktal
                $SET    k 4             ; Fall B: k := 4
m$V(k):         dw      7               ; Zelle 0004: Marke m4, Wert 7
                $IF     $CALC(def(DEBUG)) = 1   ; Fall C: DEBUG ist vereinbart, wahr
                dw      1               ; Zelle 0005: 1
                $ELSE                   ; Fall C: nicht erzeugt
                dw      2               ; entsteht nicht
                $ENDIF                  ; Ende Fall C
                $IF     $CALC(def(AUS)) = 1     ; Fall D: AUS ist nicht vereinbart, falsch
                dw      4               ; entsteht nicht
                $ELIF   $CALC(def(DEBUG)) = 1   ; Fall D: wahr
                dw      5               ; Zelle 0006: 5
                $ELSE                   ; Fall D: nicht erzeugt
                dw      6               ; entsteht nicht
                $ENDIF                  ; Ende Fall D
                $IF     $CALC(def(AUS)) = 1     ; Fall E: falsch
                dw      4               ; entsteht nicht
                $ELIF   $CALC(def(AUS2)) = 1    ; Fall E: ebenfalls falsch
                dw      5               ; entsteht nicht
                $ELSE                   ; Fall E: erzeugt
                dw      6               ; Zelle 0007: 6
                $ENDIF                  ; Ende Fall E
                $IF     $V(n) = 6       ; Fall F: n ist 6, wahr
                $IF     $V(n) > 9       ; innen falsch
                dw      1               ; entsteht nicht
                $ELSE                   ; innen: erzeugt
                dw      4               ; Zelle 0010: 4
                $ENDIF                  ; Ende des inneren $IF
                $ELSE                   ; aussen: nicht erzeugt
                dw      5               ; entsteht nicht
                $ENDIF                  ; Ende Fall F
                $REPT   3               ; Fall G: dreimal, $Z1 zaehlt 0, 1, 2
w$Z1:           dw      $CALC($Z1+1)    ; Zellen 0011 bis 0013: w0 = 1, w1 = 2, w2 = 3
                $ENDREPT                ; Ende Fall G
                $REPT   0               ; Fall H: nullmal
                dw      7               ; entsteht nicht
                $ENDREPT                ; Ende Fall H
                $SET    i 1             ; Fall I: i := 1
                $WHILE  $CALC($V(i)*$V(i)) <= 30        ; solange das Quadrat hoechstens 30 ist
                dw      $CALC($V(i)*$V(i))      ; Zellen 0014 bis 0020: 1, 4, 9, 16, 25 dezimal
; naechste Zeile: $INC i erhoeht i um 1
                $INC    i
                $ENDWHILE               ; Ende Fall I
                $SET    z 1             ; Fall J: z := 1
                NUM                     ; Zelle 0021: 1, danach z = 2
                NUM                     ; Zelle 0022: 2, danach z = 3
                $SET    z 6             ; z := 6
                NUM                     ; Zelle 0023: 6, danach z = 7
; Fall K: $V(nichtda) in dieser Kommentarzeile darf keinen Fehler ausloesen
                dw      7               ; Zelle 0024: 7, Kommentar mit $V(nichtda) und $CALC(1+1) bleibt Text
erg:            dw      0               ; Zelle 0025: Ergebnis aus Fall L (soll 3 werden)
erg2:           dw      0               ; Zelle 0026: zweites Ergebnis (soll 7 werden)
                $SET    j 2             ; Fall L: j := 2
                $SET    op 240          ; op := 240 (Operationscode speichern)
haupt:          211     w$V(j)          ; Zelle 0027: AC := w2 = 3, Operand mit $V
ausg:           $V(op)  erg             ; Zelle 0030: Operation mit $V, ergibt 240 erg
                211     m4              ; Zelle 0031: AC := m4 = 7, die Marke aus Fall B
                240     erg2            ; Zelle 0032: erg2 := 7
                164     0001            ; Zelle 0033: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0034: Halt
ende:           end
DEBUG:          abs     1               ; Schalter fuer die Faelle C und D

; Sollwerte von Hand hergeleitet (vor dem ersten Lauf): n = 3, 5, 6 -> Zellen 3, 5 und 6*2 = 12 dezimal = 014 oktal.
; Die Zelle einer Anweisung ist Adresse*01000 + Operationscode: haupt = 0027 -> 000 haupt = 27000; 211 w2 (w2 = 0013) = 13211;
; 240 erg (erg = 0025) = 25240; 211 m4 (m4 = 0004) = 4211; 240 erg2 (erg2 = 0026) = 26240; 164 0001 = 1164; 020 0 = 20.
; Nach dem Lauf: erg = 3 (w2), erg2 = 7 (m4), AC = 7, der Halt steht auf 0034, BZ danach 0035.
;#PRUEFE-START
; BZ=0035 AC=00000000007 US=1
; 0000: 00000027000   # 000 haupt
; 0001: 00000000003   # Fall A: n = 3
; 0002: 00000000005   # Fall A: n = 5
; 0003: 00000000014   # Fall A: $CALC(6*2) = 12 dezimal = 014 oktal
; 0004: 00000000007   # Fall B: Marke m4
; 0005: 00000000001   # Fall C: wahr
; 0006: 00000000005   # Fall D: $ELIF-Zweig
; 0007: 00000000006   # Fall E: $ELSE-Zweig
; 0010: 00000000004   # Fall F: verschachtelt, innen $ELSE
; 0011: 00000000001   # Fall G: w0
; 0012: 00000000002   # Fall G: w1
; 0013: 00000000003   # Fall G: w2 (Fall H dahinter erzeugt nichts)
; 0014: 00000000001   # Fall I: 1
; 0015: 00000000004   # Fall I: 4
; 0016: 00000000011   # Fall I: 9 dezimal = 011 oktal
; 0017: 00000000020   # Fall I: 16 dezimal = 020 oktal
; 0020: 00000000031   # Fall I: 25 dezimal = 031 oktal
; 0021: 00000000001   # Fall J: erster Aufruf von NUM
; 0022: 00000000002   # Fall J: zweiter Aufruf
; 0023: 00000000006   # Fall J: Aufruf nach $SET z 6
; 0024: 00000000007   # Fall K: Zeile mit $V( im Kommentar
; 0025: 00000000003   # erg
; 0026: 00000000007   # erg2
; 0027: 00000013211   # 211 w2 (Operand aus $V)
; 0030: 00000025240   # 240 erg (Operation aus $V)
; 0031: 00000004211   # 211 m4
; 0032: 00000026240   # 240 erg2
; 0033: 00000001164   # 164 0001
; 0034: 00000000020   # Halt 020 auf 0034
;#PRUEFE-ENDE
