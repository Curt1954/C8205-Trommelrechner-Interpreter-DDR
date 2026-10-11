                start
                000     euklid          ; Sprung zum Programmanfang (Zelle 0000)
; Bestimmung des groessten gemeinsamen Teilers zweier natuerlicher Zahlen nach dem Euklidschen Algorithmus (pj2)
; Objektdatei-Vorgabe: Kennzeichen 01 = Programm, 02 = Daten (a, b), 00 = absolut (t, Stoppnummer).
; Der Assembler kennt kein Kennzeichen 02: Programm (ab 3000) und Daten (ab 3020) werden mit equ gelegt.
; Die Hilfszelle c liegt wie in der Vorlage programmrelativ hinter dem Stopp (relativ 0015).
                equ     03000
euklid:         211     a               ; ac:=a
                330     b               ; a = b ?
                170     ende            ; Sprung bei gleich (Vergleicher 3)
                140     vcspei          ; a < b ?  (gleich ist schon erledigt) -> c:=a
                220     b               ; ac:=a-b
vcspei:         240     c               ; c:=a / c:=a-b
                211     b               ; ac:=b
                240     a               ; a:=b
                211     c               ; ac:=c
                240     b               ; b:=c
                000     euklid          ; Schleife
ende:           240     t               ; t:=a
                021     stoppnr         ; Stopp
c:              db      1               ; Hilfszelle c (in der Vorlage nicht belegt, wird vor dem Lesen beschrieben)
                equ     03020
; Daten: a=060 (48), b=044 (36), ggT = 014 (12)
a:              dw      060
b:              dw      044
                end
t:              abs     07774           ; Ergebnis t
stoppnr:        abs     01111           ; Stoppnummer
