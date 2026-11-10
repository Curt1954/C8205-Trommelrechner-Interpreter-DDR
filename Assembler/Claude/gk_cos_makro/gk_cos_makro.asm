; gk_cos_makro.asm - Test des Einsprungs gk_cos im Makro GK_SIN (c82ass.makros): Kosinus und Sinus mit demselben Code, GK_SIN mehrfach aufgerufen, der Code entsteht nur einmal.
; Aufrufe: GK_SIN dreimal an verschiedenen Stellen des Programms (erzeugt gk_add, gk_sub, gk_mul, gk_sin und gk_cos nur beim ersten Mal). Die Marken gk_sin, gk_cos, gk_add, gk_sub, gk_mul
; duerfen nur einmal vorkommen (sonst Doppeldefinition, rc 16). Speicherbedarf: GK_SIN mit gk_cos 0636 Zellen (0001 bis 0636), Hauptprogramm ab 01000.
; Berechnet cos(x) fuer 10 Werte (dwg) mit gk_cos (x nach gks_x, 025 gk_cos), danach sin(1) mit gk_sin. Sollwerte aus dem bitgenauen Modell gk_modell/gk_sin_modell.py
; (Funktion cos_modell: gleiche Argumentreduktion wie gk_sin, Quadrant um 1 weiter, Vorzeichen von x ohne Wirkung). Vergleich mit der exakten Kosinusfunktion: groesster Fehler dieser Faelle 0,21 Einheiten
; von 2^-26 (absolut). Fall n: Zelle 01500 + n - 1; Zelle 01512 enthaelt sin(1). Der Test belegt auch cos(-1) = cos(1) bitgenau (Zellen 1501 und 1502).
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H M+ E M- R
; Test: Tastenfolge H M+ E M- R (E zaehlt 1 dazu: Start bei 01000).
                start                ; Zaehlung beginnt bei 0000 (relativ)
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm (Hauptprogramm bei 01000)
                GK_SIN               ; erster Aufruf: erzeugt gk_add, gk_sub, gk_mul, gk_sin und gk_cos
                GK_SIN               ; zweiter Aufruf: erzeugt nichts
                equ     01000        ; Hauptprogramm ab relativ 01000
haupt:          211     @fall        ; Zeiger auf die Falltabelle
                240     fz           ; merken
                211     @res         ; Zeiger auf die Ergebniszellen
                240     rz           ; merken
fa_l:           211     fz           ; Zeiger auf x
                251     0            ; AC := x
                240     gks_x        ; Parameter von gk_cos (derselbe wie bei gk_sin)
                025     gk_cos       ; AC := cos(x)
                240     tm           ; Ergebnis merken
                211     rz           ; Zeiger auf die Ergebniszelle
                210     #0240        ; + Speicherbefehl
                240     sp           ; auf die naechste Zelle legen
                211     tm           ; Ergebnis
sp:             db      1            ; Laufzeit: 240 res_i
                ZEIGER_NAECHST rz    ; naechste Ergebniszelle
                ZEIGER_NAECHST fz    ; naechster Fall
                220     @fallend     ; Zeiger - Ende der Falltabelle
                040     fa_l         ; kleiner (negativ): naechster Fall
                GK_SIN               ; dritter Aufruf mitten im Ablauf: erzeugt nichts (und darf nicht in den Ablauf laufen)
                211     x2           ; AC := x = 1
                240     gks_x        ; Parameter von gk_sin
                025     gk_sin       ; AC := sin(1)
                240     esin         ; Ergebnis sin(1)
                020     0            ; Halt
fz:             db      1            ; Zeiger Falltabelle
rz:             db      1            ; Zeiger Ergebniszelle
tm:             db      1            ; Ergebnis (Zwischenspeicher)
x2:             dw      020600000000 ; x = 1 (dwg)
                equ     01400        ; Falltabelle: x (dwg)
fall:
                dw      000000000000     ; Fall x = 0
                dw      020600000000     ; Fall x = 1
                dw      060600000000     ; Fall x = -1
                dw      020200000000     ; Fall x = 0,5
                dw      020711037553     ; Fall x = pi/2
                dw      021311037553     ; Fall x = pi
                dw      021711037553     ; Fall x = 2 pi
                dw      021300000000     ; Fall x = 3
                dw      022240000000     ; Fall x = 10
                dw      023710000000     ; Fall x = 100
fallend:        dw      0            ; Ende
                equ     01500        ; Ergebniszellen: cos(x) je Fall
res:            db      10
esin:           db      1            ; Ergebnis sin(1)
ende:           end                  ; Ende

;#PRUEFE-START
; BZ=1033 US=1
; 1500: 20600000000   # cos(0)
; 1501: 20212242402   # cos(1)
; 1502: 20212242402   # cos(-1)
; 1503: 20340522401   # cos(0,5)
; 1504: 43356751350   # cos(pi/2)
; 1505: 60600000000   # cos(pi)
; 1506: 20600000000   # cos(2 pi)
; 1507: 60375340230   # cos(3)
; 1510: 60326632621   # cos(10)
; 1511: 20334601670   # cos(100)
; 1512: 20327325222   # sin(1)
;#PRUEFE-ENDE
