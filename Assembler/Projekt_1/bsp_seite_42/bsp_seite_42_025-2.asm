; C8205 Heft 2 Programmierung in Maschinensprache
; #DOK-0001  Unterprogrammtechnik,  Sprung mit Rückkehrabsicht, 025
; #SPEI-0001 2012-2027
; #SPEI-0002 2012-2016
; #PROT STUFE=2
; #TROMMEL=KEEP                # Trommel unveraendert (Stand des vorigen Laufs), ausdruecklich
; Seite 42, Sprung mir Rückkehrabsicht 025, Unterprogramme
;
               start 
               000   beginn     ;
               equ   02000      ;
beginn:        ANWAHL SW1O
               dz    $ingb
               211   z_a
               240   up+1
               025   up
               211   z_b
               240   up+1
               025   up               
               211   z_c
               240   up+1
               025   up
halt:          164   0001       ; DEBUG Nr. 0001 aktivieren
               020   0          ; halt
z_a:           dto   A
z_b:           dto   B
z_c:           dto   C
up:            240   zum_rs
               db    1   ; das auszugebende zeichen
zum_rs:        db    1   ; der Ruecksprung
nix:           dw    0777
ende:          end

