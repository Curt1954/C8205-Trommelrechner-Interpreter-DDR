; C8205 Heft 2 Programmierung in Maschinensprache
; #DOK-0001  Summieren eines Vektors Beispiel 2 von Seite 40
; #SPEI-0001 0000-0000
; #PROT STUFE=2
; #TROMMEL=KEEP                # Trommel unveraendert (Stand des vorigen Laufs), ausdruecklich
; Beispiel: Seite 40, Summierung eines Vektors
;
               start 
               000   beginn     ;
               equ   02000      ;
adr_a:         da    a          ; Adrese der ersten Komponente Vektor
adr_b:         da    b          ; Adresse der letzten Komponente Vektor
beginn:        241   zelle_s    ; s:=0
               211   adr_a
               210   lesebef
schleife:      240   beliebig  ; Lesebefehl
               330   adr_b  
beliebig:      db    1
               210   zelle_s    ; summe := summe + speicher    
               240   zelle_s
               150   halt
               211   beliebig  ; Lesebefehl
               210   adr_1      ; Lesebefehl Adresse erhöhen
               000   schleife
halt:          164   0001       ; DEBUG Nr. 0001 aktivieren
               020   0          ; halt
adr_1:         dw    0001000    ; eine Adreßeinheit
zelle_s:       db    1
lesebef:       dw    0211
a:             dw    100
               dw    101
               dw    200
b:             dw    55
ende:          end


; Sollwerte von Hand hergeleitet. Summe 100+101+200+55 (dezimal) = 456 = 0710 oktal; Halt auf 2017.
;#PRUEFE-START
; BZ=2020 AC=00000000710 US=1
; 2021: 00000000710   # zelle_s
;#PRUEFE-ENDE
