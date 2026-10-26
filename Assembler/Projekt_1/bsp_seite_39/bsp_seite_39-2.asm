; C8205 Heft 2 Programmierung in Maschinensprache
; #DOK-0001 Summieren eines Vektors
; #SPEI-0001 2020-2021
; #PROT STUFE=2
; #TROMMEL=KEEP                # Trommel unveraendert (Stand des vorigen Laufs), ausdruecklich
; Beispiel: Seite 39, Summierung eines Vektors
;
               start 
               000   beginn     ;
               equ   02000      ;
adr_a:         da    a          ; Adrese der ersten Komponente Vektor
adr_b:         da    b          ; Adresse der letzten Komponente Vektor
beginn:        241   zelle_s    ; s:=0
               211   adr_a
schleife:      240   zelle_i    ; i:=a
               251   0000    
               210   zelle_s    ; summe := summe + Speicher[i]
               240   zelle_s    ; s:=summe
               211   zelle_i     
               210   adr_1      ; i:=i+1
               330   adr_b      
               140   schleife
               211   zelle_s    ; AC:=Summe
halt:          164   0001       ; DEBUG Nr. 0001 aktivieren
               020   0          ; halt
adr_1:         dw    0001000    ; eine Adreßeinheit
zelle_i:       db    1
zelle_s:       db    1
a:             dw    100
               dw    101
               dw    200
b:             dw    55
ende:          end


; Sollwerte von Hand hergeleitet. Summe 100+101+200+55 (dezimal) = 456 = 0710 oktal; i endet bei der Adresse von b (2025 in den Adressstellen).
;#PRUEFE-START
; BZ=2017 AC=00000000710 US=1
; 2020: 00002025000   # zelle_i
; 2021: 00000000710   # zelle_s
;#PRUEFE-ENDE
