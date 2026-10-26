; C8205 Heft 2 Programmierung in Maschinensprache
; Beispiel: 5.16 Umspeichern eines Vektors
;
               start 
               000   go
               equ   02000
go:            000   beginn
aqv:           da    qvektor ; Adrese der ersten Komponente Quellvektor
dqv:           dw    05000   ; Dimension von qvektor gezählz in Adreßeinheiten
azv:           da    zvektor ; Adresse der ersten Komponente Zielvektor
adreinheit:    dw    01000   ; Adresseinheit
spbef:         dw    0240    ; Speicherbefehl
i:             db    1       ; Arbeitszelle für i
beginn:        241   i       ; I:=0
schleife:      210   azv     ; ac:=(azv+i)
               210   spbef   ; ac:=(azv+i)240
               240   genbef  ; Arbeitszelle genbef:= (qzv+i) 240
               211   i       ; ac:=<i>
               210   aqv        ; ac:=qvektor+i
;  251: Laden des Inhaltes einer Speicherstelle, deren Adresse im AC steht in den AC. 
               251   0          ; ac:=<qvektor+i> 
genbef:        db    1          ; hier steht der Befehl 240 (qzv+i)  Speichern
               211   i          ; ac:=<i>
               210   adreinheit ; ac:=i+1
               240   i          ; i:=ac
               330   dqv        ; vergleicher 3, falls i == <dqv>
               170   halt       ; sprung bei gleich
               000   schleife
halt:          164   0001       ;DEBUG Nr. 0023 aktivieren
               020   0          ;halt
qvektor:       dw    1
               dw    2
               dw    3
               dw    4
               dw    5
               equ   02100
zvektor:       db    5
ende:          end


; Sollwerte von Hand hergeleitet. Zielvektor ab 2100 = Quellvektor 1 bis 5 (ab 2027); i = 5 Adresseneinheiten; Halt auf 2026.
;#PRUEFE-START
; BZ=2027 AC=00000005000 US=1
; 2006: 00000005000   # i
; 2027: 00000000001   # Quellvektor unverändert
; 2030: 00000000002
; 2031: 00000000003
; 2032: 00000000004
; 2033: 00000000005
; 2100: 00000000001   # Zielvektor
; 2101: 00000000002
; 2102: 00000000003
; 2103: 00000000004
; 2104: 00000000005
;#PRUEFE-ENDE
