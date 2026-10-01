; Sortierung eindimensionales Array. Anschließend Ausgabe auf SW1

; Algorithmus:
; function SelectionSort(array, length):
;    for i from 0 to length - 1:
;        min_index = i  // Anfangsannahme: Das erste unsortierte Element ist das kleinste
;
;        for j from i + 1 to length - 1:
;             if array[j] < array[min_index]:
;                min_index = j  // Neues Minimum gefunden, Index aktualisieren
;
;        if min_index != i:
;            swap(array[i], array[min_index])  // Kleinstes gefundenes Element nach vorne tauschen
;
;    return array
; _______________________________________________________
;

             start 
             241 i           ; i löschen, damit Programm mehrfach gestartet werden kann.
             TEST      123
             MACHE_ADRESSEINHEIT2 len0 len 9 ; Lade Schleifenbegrenzung (length - 1) von len, verschiebe 9x links
             000 firstEntry

loop1:       211 i           ; Lade i
             210 #01000      ; Addiere 1 Adreßeinheit zu `i`
             240 i           ; Speichere nach i

;;;test1:       abs              loop1+27
;;;test2:       abs              lolo34
; --------------------------------------------------------
; -- Erste Schleife:      for i from 0 to length - 1: 
; --------------------------------------------------------
firstEntry:  211 i           ; Lade i
             330 len         ; Vergleiche mit aktuellem `AC=i`  mir len
             150 ausgabe     ; Falls `i > len`, springe zur Ausgabe des sortieren Array


; --------------------------------------------------------
; -- min_index = i
; --------------------------------------------------------
             240 min_index   ; Setze `min_index = (AC=i)`

; --------------------------------------------------------
; -- Zweite Schleife:  for j from i + 1 to length - 1:
; --------------------------------------------------------
             211 i
             240 j           ; j := i
loop2:       211 j
             210 #01000      ; j := j +1  Adreßliteral @1 geht nicht, das k1k2=01
             240 j           ; Speichere `i + 1` in `j`

             ARRAY_LOAD  afeld_base j         iladebefehl    ;if array[j] < array[min_index]:
             ARRAY_VGL   afeld_base min_index jvglbefehl     ;if array[j] < array[min_index]:

             211 j           ; Lade j
             330 len         ; Vergleiche min_index mit len
             150 m1          ; Falls `min_index > len`, springe zu `m1` beende zweite Schleife

; --------------------------------------------------------
; -- if array[j] < array[min_index]:
; --------------------------------------------------------
iladebefehl: db  1           ; von ARRAY_LOAD: Hier steht der Ladebefehl für `AC := array[j]`
jvglbefehl:  db  1           ; von ARRAY_VGL:  Hier steht der Vergleichsbefehl mit `AC ? array[min_index]`
             170 *+2         ; wenn AC=array[j] <iladebefehl> = array[min_index] <jvglbefehl>, weiter
             150 loop2       ; wenn AC=array[j] <iladebefehl> > array[min_index] <jvglbefehl>, nächster Durchlauf
      
; --------------------------------------------------------
; -- min_index = j
; --------------------------------------------------------
             211 j           ; Lade j in AC bei array[j] < array[min_index]
             240 min_index   ; Speichere j nach min-Index
             000 loop2       ; nächster Durchlauf Schleife 2
; --------------------------------------------------------
; -- Zweite Schleife:                        SCHLEIFENENDE
; --------------------------------------------------------

; --------------------------------------------------------
; -- if min_index != i:
; --------------------------------------------------------
m1:          211 min_index   ; Lade min_index in AC 
             330 i           ; Vergleiche mit i
             170 loop1       ; Springe wenn  AC=min_index == i
 
; --------------------------------------------------------
; -- swap(array[i], array[min_index])
; --------------------------------------------------------
swap:        ARRAY_SWAP  afeld_base i min_index tmp_element
             000 loop1       ; nächster Durchlauf Schleife 1
             WDHL  JA LI KON 5 $ADRESSE
; --------------------------------------------------------
; -- Zweite Schleife:                        SCHLEIFENENDE
; --------------------------------------------------------


; Speicherreservierung
             equ100 *
len0:        dw feld_ende-feld_base  ; Anzahl der Elemente im Array
len:         db 1           ; Länge des Array in Adreßeinheiten umgerechnet
ausgabe:     ANWAHL  SW1O   ; Anwahl Schreibwerk 1 für Output
feld_base:   dto 4172k0     ; Startelement des Arrays, alles Kleinbuchstaben-Ausgabebefehle
feld_ende:   equ *
             020            ; Programm-Ende, Halt-Befehl
afeld_base:  da feld_base   ; Speichert die echte Adresse des Arrays
i:           db 1           ; Laufvariable für äußere Schleife, Anfangswert
j:           db 1           ; Laufvariable für innere Schleife, wird immer berechnet
min_index:   db 1           ; Temporärer Speicher für das Minimum, wird immer berechnet
tmp_element: db 1           ; Hilfsspeicherplatz für ein Arrayelement beim swap
