                start
                000     maximum         ; Sprung zum Programmanfang (Zelle 0000)
; Ermittlung des Maximums von drei Zahlen (pj2, Objektdatei-Vorgabe)
; Original-Objektdatei: Kennzeichen 01 = Programmladeadresse, 02 = Datenladeadresse, 00 = absolut.
; Der Assembler kennt kein Kennzeichen 02: Programm (ab 3000) und Daten (ab 3020) liegen hier
; beide im verschieblichen Teil und werden mit equ auf die Testadressen gelegt.
                equ     03000
maximum:        211     a               ; M:=a
                330     b               ; M>=b ?
                150     nachb           ; Sprung, wenn M>=b
                211     b               ; M:=b
nachb:          330     c               ; M>=c ?
                150     nachc           ; Sprung, wenn M>=c
                211     c               ; M:=c
nachc:          240     r2              ; M -> R2 (absolute Adresse, Kennzeichen 00)
                021     stoppnr         ; Stopp (Adreßteil 1111 absolut)
                equ     03020
; Daten (Fall "b ist das Maximum"). Andere Fälle: a/b/c = 0300/0100/0200, 0100/0200/0300, 0200/0200/0200
a:              dw      0100
b:              dw      0300
c:              dw      0200
                end
r2:             abs     07776           ; Register R2
stoppnr:        abs     01111           ; Stoppnummer

; Sollwerte von Hand hergeleitet. Fall b ist das Maximum (a=0100, b=0300, c=0200): R2 = 0300; Stopp 021 löscht AC, AR = 1111.
;#PRUEFE-START
; BZ=3011 AC=00000000000 AR=1111 US=1
; 3020: 00000000100   # a
; 3021: 00000000300   # b
; 3022: 00000000200   # c
; 7776: 00000000300   # R2 = Maximum
;#PRUEFE-ENDE
