; daten.inc - Datenteil zu quelltextinclude.asm (mit $INCLUDE eingebunden, Zellen 0001 bis 0005)
wert:           dw      017          ; Zelle 0001: Konstante 017
erg:            dw      0            ; Zelle 0002: Ergebnis
eins:           dw      1            ; Zelle 0003: Konstante 1
rueck:          db      1            ; Zelle 0004: Rueckkehrwort der Unterprogramme (Laufzeit: 000 <Rueckkehradresse>)
                $SET    n 3          ; $-Zeile in der eingebundenen Datei: Variable n := 3
drei:           dw      $V(n)        ; Zelle 0005: Konstante 3 aus der Variablen n
