; makrodefined.asm - Test von $DEFINED und $MDEFINED (Assemblerdokumentation 4.25)
;#DOK-0001 Existenzabfrage: Variable, Feld, Feldelement, lokal/Ueberdeckung, Makro aus Quelltext, Projektdatei und c82ass.makros
;#MACRODATEI1=makrodefined.macro
;#PROT STUFE=2
DFVAR:          MACRO                   ; Variablen und Felder (global)
                $SET glob 5             ; einfache Variable glob = 5
                $DIM fe 3               ; Feld fe mit 3 Elementen (0 bis 2)
                $SET fe(1) 9            ; Element 1 gesetzt
                dw      $DEFINED(glob)          ; 1  Variable gesetzt
                dw      $DEFINED(nixda)         ; 0  Name unbekannt, kein Fehler
                dw      $DEFINED(fe)            ; 1  Feld sichtbar
                dw      $DEFINED(@fe)           ; 1  Feld
                dw      $DEFINED(@glob)         ; 0  einfache Variable ist kein Feld
                dw      $DEFINED(@nixda)        ; 0  Name unbekannt
                dw      $DEFINED(fe(2))         ; 1  letztes Element
                dw      $DEFINED(fe(3))         ; 0  Index ausserhalb, kein Fehler
                dw      $DEFINED(fe(1+1))       ; 1  Index als Rechenausdruck
                dw      $DEFINED(glob(0))       ; 0  glob ist kein Feld
                MEND                    ; Ende von DFVAR
DFLOK:          MACRO                   ; lokale Variable und lokales Feld
                dw      $DEFINED(lok)           ; 0  vor $LOCAL
                $LOCAL lok loks(2)      ; lokale Variable lok, lokales Feld loks mit 2 Elementen
                dw      $DEFINED(lok)           ; 1  lokal vereinbart, ohne $SET
                dw      $DEFINED(@loks)         ; 1  lokales Feld
                dw      $DEFINED(loks(1))       ; 1  Element 1
                dw      $DEFINED(loks(2))       ; 0  ausserhalb
                dw      $DEFINED(@lok)          ; 0  lok ist kein Feld
                dw      $V(lok)                 ; 0  Wert einer lokalen Variable ohne $SET
                DFLOKIN                 ; aufgerufenes Makro sieht die lokalen nicht
                MEND                    ; Ende von DFLOK
DFLOKIN:        MACRO                   ; aus DFLOK aufgerufen
                dw      $DEFINED(lok)           ; 0  lokale Variable des Aufrufers unsichtbar
                dw      $DEFINED(loks(0))       ; 0  lokales Feld des Aufrufers unsichtbar
                dw      $DEFINED(glob)          ; 1  globale Variable sichtbar
                MEND                    ; Ende von DFLOKIN
DFVERD:         MACRO                   ; lokal verdeckt global
                dw      $V(glob)                ; 5  globaler Wert
                $LOCAL glob             ; lokale Variable gleichen Namens
                dw      $V(glob)                ; 0  die lokale verdeckt die globale
                $SET glob 8             ; setzt nur die lokale
                dw      $V(glob)                ; 8  lokaler Wert
                $LOCAL fe               ; lokale einfache Variable gleichen Namens wie das globale Feld
                dw      $DEFINED(fe)            ; 1  lokale Variable
                dw      $DEFINED(@fe)           ; 0  das globale Feld ist verdeckt
                dw      $DEFINED(fe(0))         ; 0  ebenso das Element
                dw      $DEFINED(lok)           ; 0  die lokale von DFLOK ist mit dessen Ende verschwunden
                MEND                    ; Ende von DFVERD
DFAUSD:         MACRO                   ; $V im Argument, Klammer, $CALC, $IF, $ELIF
                dw      $V(glob)                ; 5  globale Variable unberuehrt
                dw      $DEFINED(@fe)           ; 1  globales Feld wieder sichtbar
                $SET i 2                ; Laufzahl 2
                dw      $DEFINED(a$V(i))        ; 0  a2 ist noch nicht gesetzt
                $SET a2 1               ; setzt a2
                dw      $DEFINED(a$V(i))        ; 1  jetzt gesetzt
                dw      $DEFINED((a2))          ; 1  Klammer um das ganze Argument
                dw      $DEFINED(fe($V(i)))     ; 1  Element 2 des Feldes fe
                $SET i 3                ; Laufzahl 3
                dw      $DEFINED(fe($V(i)))     ; 0  Element 3 gibt es nicht
                dw      $CALC($DEFINED(glob)+$DEFINED(a2)+$DEFINED(nixda))   ; 2  1+1+0
                $IF $DEFINED(a2) = 1
                dw      11                      ; erzeugt: a2 vorhanden
                $ELIF $DEFINED(a2) = 0
                dw      12                      ; nicht erzeugt
                $ENDIF
                $IF $DEFINED(nixda) = 1
                dw      21                      ; nicht erzeugt
                $ELIF $DEFINED(a2) = 1
                dw      22                      ; erzeugt: der ELIF-Zweig
                $ENDIF
                MEND                    ; Ende von DFAUSD
DFSCHL:         MACRO                   ; $WHILE, $REPT, Marke, Kommentar
                $DIM wq 4               ; Feld mit den Elementen 0 bis 3
                $SET w 0                ; Zaehler
                $WHILE $DEFINED(wq($V(w))) = 1
                $INC w
                $ENDWHILE
                dw      $V(w)                   ; 4  vier Elemente vorhanden
                $REPT $DEFINED(glob)+2
                dw      7                       ; dreimal: 1+2
                $ENDREPT
                $SET neu 1              ; neu wird erst hier gesetzt
                $REPT $DEFINED(neu)
                dw      99                      ; nicht erzeugt: Stand zu Beginn des Aufrufs, neu fehlte da
                $ENDREPT
M$DEFINED(glob): dw     9                       ; Marke M1; $DEFINED(glob) im Kommentar und $MDEFINED(KB)
                MEND                    ; Ende von DFSCHL
MDFTEST:        MACRO                   ; Makros
                dw      $MDEFINED(HOOK)         ; 1  Makro im Quelltext
                dw      $MDEFINED(PROJHOOK)     ; 1  Makro in der Projektdatei
                dw      $MDEFINED(KB)           ; 1  Makro aus c82ass.makros
                dw      $MDEFINED(NIXMAK)       ; 0  unbekannt, kein Fehler
                dw      $MDEFINED(SPAET)        ; 1  Makro erst hinter dem Aufruf definiert
                dw      $MDEFINED(BEIDE)        ; 1  in Quelltext und Datei, zaehlt einmal
                dw      $MDEFINED(glob)         ; 0  Variable ist kein Makro
                dw      $MDEFINED(dw)           ; 0  Anweisung ist kein Makro
                dw      $MDEFINED(haupt)        ; 0  Symbol des Quelltexts ist kein Makro
                dw      $MDEFINED(MDFTEST)      ; 1  das laufende Makro selbst
                dw      $MDEFINED(kb)           ; 0  Kleinschreibung zaehlt
                MEND                    ; Ende von MDFTEST
SIEBEN:         MACRO                   ; Beispiel 1 aus 4.25
                $SET zaehl 7
                MEND                    ; Ende von SIEBEN
VORGABE:        MACRO                   ; Beispiel 1 aus 4.25
                $IF $DEFINED(zaehl) = 0
                $SET zaehl 100
                $ENDIF
                dw      $V(zaehl)               ; 100 oder der vorher gesetzte Wert
                MEND                    ; Ende von VORGABE
VORGABEB:       MACRO                   ; wie VORGABE mit der Variablen zb, die niemand vorher setzt
                $IF $DEFINED(zb) = 0
                $SET zb 100
                $ENDIF
                dw      $V(zb)                  ; 100
                MEND                    ; Ende von VORGABEB
HOOK:           MACRO                   ; das Makro, das PRUEFUNG aufruft
                dw      77                      ; Wort 77 dezimal
                MEND                    ; Ende von HOOK
PRUEFUNG:       MACRO                   ; Beispiel 2 aus 4.25, HOOK gibt es
                $IF $MDEFINED(HOOK) = 1
                HOOK                            ; nur, wenn es das Makro HOOK gibt
                $ENDIF
                dw      7                       ; in jedem Fall
                MEND                    ; Ende von PRUEFUNG
PRUEFUNG2:      MACRO                   ; Beispiel 2 aus 4.25, das Makro HOOKNIX gibt es nicht
                $IF $MDEFINED(HOOKNIX) = 1
                HOOKNIX                         ; nicht erzeugt, der Name muss nicht bekannt sein
                $ENDIF
                dw      7                       ; in jedem Fall
                MEND                    ; Ende von PRUEFUNG2
BEIDE:          MACRO                   ; ersetzt BEIDE der Projektdatei
                dw      62                      ; Wort 62 dezimal
                MEND                    ; Ende von BEIDE
                start                   ; Zaehlung beginnt bei 0000
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm
                DFVAR                   ; Zellen 0001 bis 0012
                DFLOK                   ; Zellen 0013 bis 0024
                DFVERD                  ; Zellen 0025 bis 0033
                DFAUSD                  ; Zellen 0034 bis 0045
                DFSCHL                  ; Zellen 0046 bis 0052
                MDFTEST                 ; Zellen 0053 bis 0065
                SIEBEN                  ; keine Zelle
                VORGABE                 ; Zelle 0066
                VORGABE                 ; Zelle 0067
                VORGABEB                ; Zelle 0070
                VORGABEB                ; Zelle 0071
                PRUEFUNG                ; Zellen 0072 und 0073
                PRUEFUNG2               ; Zelle 0074
                PROJHOOK                ; Zelle 0075
                BEIDE                   ; Zelle 0076
haupt:          164     0001            ; Zelle 0077: Diagnoseausgabe (nur im Test)
                020     0               ; Zelle 0100: Halt
SPAET:          MACRO                   ; Makro hinter den Aufrufen definiert
                dw      3
                MEND                    ; Ende von SPAET
ende:           end

; Sollwerte von Hand hergeleitet (Makros einzeln durchgerechnet, Zeilen dezimal, hier oktal); Halt auf 0100, BZ danach 0101.
;#PRUEFE-START
; BZ=0101 US=1
; 0001: 00000000001   # DFVAR
; 0002: 00000000000   # DFVAR
; 0003: 00000000001   # DFVAR
; 0004: 00000000001   # DFVAR
; 0005: 00000000000   # DFVAR
; 0006: 00000000000   # DFVAR
; 0007: 00000000001   # DFVAR
; 0010: 00000000000   # DFVAR
; 0011: 00000000001   # DFVAR
; 0012: 00000000000   # DFVAR
; 0013: 00000000000   # DFLOK
; 0014: 00000000001   # DFLOK
; 0015: 00000000001   # DFLOK
; 0016: 00000000001   # DFLOK
; 0017: 00000000000   # DFLOK
; 0020: 00000000000   # DFLOK
; 0021: 00000000000   # DFLOK
; 0022: 00000000000   # DFLOKIN
; 0023: 00000000000   # DFLOKIN
; 0024: 00000000001   # DFLOKIN
; 0025: 00000000005   # DFVERD
; 0026: 00000000000   # DFVERD
; 0027: 00000000010   # DFVERD
; 0030: 00000000001   # DFVERD
; 0031: 00000000000   # DFVERD
; 0032: 00000000000   # DFVERD
; 0033: 00000000000   # DFVERD
; 0034: 00000000005   # DFAUSD
; 0035: 00000000001   # DFAUSD
; 0036: 00000000000   # DFAUSD
; 0037: 00000000001   # DFAUSD
; 0040: 00000000001   # DFAUSD
; 0041: 00000000001   # DFAUSD
; 0042: 00000000000   # DFAUSD
; 0043: 00000000002   # DFAUSD
; 0044: 00000000013   # DFAUSD
; 0045: 00000000026   # DFAUSD
; 0046: 00000000004   # DFSCHL
; 0047: 00000000007   # DFSCHL
; 0050: 00000000007   # DFSCHL
; 0051: 00000000007   # DFSCHL
; 0052: 00000000011   # DFSCHL
; 0053: 00000000001   # MDFTEST
; 0054: 00000000001   # MDFTEST
; 0055: 00000000001   # MDFTEST
; 0056: 00000000000   # MDFTEST
; 0057: 00000000001   # MDFTEST
; 0060: 00000000001   # MDFTEST
; 0061: 00000000000   # MDFTEST
; 0062: 00000000000   # MDFTEST
; 0063: 00000000000   # MDFTEST
; 0064: 00000000001   # MDFTEST
; 0065: 00000000000   # MDFTEST
; 0066: 00000000007   # VORGABE
; 0067: 00000000007   # VORGABE
; 0070: 00000000144   # VORGABEB
; 0071: 00000000144   # VORGABEB
; 0072: 00000000115   # PRUEFUNG
; 0073: 00000000007   # PRUEFUNG
; 0074: 00000000007   # PRUEFUNG2
; 0075: 00000000051   # PROJHOOK
; 0076: 00000000076   # BEIDE
;#PRUEFE-ENDE
