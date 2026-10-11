                start
                000     euklid          ; Sprung zum Programmanfang (Zelle 0000)
; TESTPROGRAMM: absichtlicher Fehler, Programm ueberschreibt den mit equ angelegten Datenbereich.
; Wie pj2_ggt_euklid.asm, aber die Daten a und b liegen mit equ 03012 zu frueh:
; das Programm belegt 3000 bis 3014, die Daten sollen ab 3012 liegen.
; Erwartet: der Assembler meldet die Adressen 3012 und 3013 als doppelt belegt (Rueckgabewert 16).
; Behebung: equ 03020 (wie in pj2_ggt_euklid.asm).
                equ     03000
euklid:         211     a               ; ac:=a
                330     b               ; a = b ?
                170     ende            ; Sprung bei gleich
                140     vcspei          ; a < b ? -> c:=a
                220     b               ; ac:=a-b
vcspei:         240     c               ; c:=a / c:=a-b
                211     b               ; ac:=b
                240     a               ; a:=b
                211     c               ; ac:=c
                240     b               ; b:=c
                000     euklid          ; Schleife
ende:           240     t               ; t:=a
                021     stoppnr         ; Stopp
c:              db      1               ; Hilfszelle c (db belegt nichts, wird nicht geprueft)
                equ     03012           ; FEHLER: liegt noch im Programm (3000 bis 3014)
a:              dw      060
b:              dw      044
                end
t:              abs     07774           ; Ergebnis t
stoppnr:        abs     01111           ; Stoppnummer

