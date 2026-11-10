; kat5_sort1: Sortier-UP (Makro KAT5SORT, Rel 0000) und Hauptprogramm, erzeugt von gen/kat5_sort1_gen.py
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5_sort1
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5_sort1-sw-ausgabe.txt
;#TESTBASIS 02000 haupt
r1:             abs     07773                ; Register 1: Adresse des Wortes fuer KAT5AUSGABE (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle fuer KAT5AUSGABE (Adressfeld)
                start                 ; Zaehlung beginnt bei 0000
kat5_sort1:     KAT5SORT              ; UP KAT5SORT (Rumpf aus c82ass.makros, Zelle 0000 bis 0065); Parameter auf Marke+1 und Marke+2

; ==========================================================
;   RELATIVE START-ADRESSE DES HAUPTPROGRAMMS:  0066
;   BIS: Leitadresse 21 2000 .   Start: 10 2066 000 .
; ==========================================================

haupt:          .LD     @feld         ; AC := Adresse des Feldes
                .STO    kat5_sort1+1  ; Parameter 1 eintragen (Zelle Marke+1)
                .LD     #024          ; AC := 20 (Anzahl der Texte)
                .STO    kat5_sort1+2  ; Parameter 2 eintragen (Zelle Marke+2)
                025     kat5_sort1    ; Aufruf des Unterprogramms
                .LD     @kbaus        ; AC := Adresse der KB/GB-Zelle des Schreibwerks
                .STO    r3            ; R3 := Adresse der Zustandszelle (Festlegung 030)
                ANWAHL  K2            ; Kanal 2 = Schreibwerk anwaehlen
                .LD     @init         ; AC := Adresse des Wortes Zeilenschaltung + Um. KB
                .STO    r1            ; R1 := Adresse von init
                025     ausgabe       ; neue Zeile und Um. KB drucken (das BIS laesst das Schreibwerk auf GB)
                .LD     @feld         ; AC := Adresse des (sortierten) Feldes
                .STO    pa            ; pa := Adresse des ersten Textes
                .LD     #024          ; AC := 20 (Anzahl der Texte)
                .STO    pz            ; pz := Zaehler der noch zu druckenden Texte
pl:             .LD     pa            ; AC := Adresse des aktuellen Textes
                .STO    r1            ; R1 := Adresse des Textes
                025     ausgabe       ; Text drucken (KAT5AUSGABE)
                .LD     @zeil         ; AC := Adresse des Wortes Zeilenschaltung
                .STO    r1            ; R1 := Adresse von zeil
                025     ausgabe       ; Zeilenschaltung drucken
                .LD     pa            ; AC := Adresse des aktuellen Textes
                .ADD    #01000        ; AC := Adresse des naechsten Textes (eine Adresseinheit weiter)
                .STO    pa            ; pa := Adresse des naechsten Textes
                .LD     pz            ; AC := Zaehler
                .SUB    #01           ; AC := Zaehler - 1
                .STO    pz            ; pz := AC
                .CMP    #0            ; AC mit 0 vergleichen
                .JVG3   halt          ; Zaehler = 0: alle Texte gedruckt, Halt
                .JMP    pl            ; sonst naechster Text
halt:           .STOP   0             ; Halt: Feld ist sortiert und gedruckt
feld:           kat5    w             ; Text[0] = w, Wort 04700000000
                kat5    8k            ; Text[1] = 8k, Wort 01733000000
                kat5    6z            ; Text[2] = 6z, Wort 01552000000
                kat5    r             ; Text[3] = r, Wort 04200000000
                kat5    x             ; Text[4] = x, Wort 05000000000
                kat5    1qy6          ; Text[5] = 1qy6, Wort 01041511500
                kat5    kuva          ; Text[6] = kuva, Wort 03345462100
                kat5    6             ; Text[7] = 6, Wort 01500000000
                kat5    41            ; Text[8] = 41, Wort 01310000000
                kat5    mvy           ; Text[9] = mvy, Wort 03546510000
                kat5    nma           ; Text[10] = nma, Wort 03635210000
                kat5    h             ; Text[11] = h, Wort 03000000000
                kat5    ga            ; Text[12] = ga, Wort 02721000000
                kat5    b5xb          ; Text[13] = b5xb, Wort 02214502200
                kat5    fy            ; Text[14] = fy, Wort 02651000000
                kat5    4wh           ; Text[15] = 4wh, Wort 01347300000
                kat5    qk            ; Text[16] = qk, Wort 04133000000
                kat5    m             ; Text[17] = m, Wort 03500000000
                kat5    4u9           ; Text[18] = 4u9, Wort 01345200000
                kat5    5g            ; Text[19] = 5g, Wort 01427000000
zeil:           kat5    $wrzl         ; Wort Zeilenschaltung (kat5 053), steht hinter dem Feld
init:           kat5    $wrzl$inkb    ; Wort Zeilenschaltung und Um. KB (kat5 053, 054): Anfang des Drucks
kbaus:          dw      0             ; KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), anfangs KB (Festlegung 030)
pa:             db      01            ; Arbeitszelle pa: Adresse des aktuellen Textes beim Drucken
pz:             db      01            ; Arbeitszelle pz: Zaehler beim Drucken
ausgabe:        KAT5AUSGABE              ; UP KAT5AUSGABE (Rumpf aus c82ass.makros, Tabelle dahinter)
ende:           end                   ; Programmende

;#PRUEFE-START
; BZ=2125 US=1
; 2125: 01041511500   # feld+0
; 2126: 01310000000   # feld+1
; 2127: 01345200000   # feld+2
; 2130: 01347300000   # feld+3
; 2131: 01427000000   # feld+4
; 2132: 01500000000   # feld+5
; 2133: 01552000000   # feld+6
; 2134: 01733000000   # feld+7
; 2135: 02214502200   # feld+8
; 2136: 02651000000   # feld+9
; 2137: 02721000000   # feld+10
; 2140: 03000000000   # feld+11
; 2141: 03345462100   # feld+12
; 2142: 03500000000   # feld+13
; 2143: 03546510000   # feld+14
; 2144: 03635210000   # feld+15
; 2145: 04133000000   # feld+16
; 2146: 04200000000   # feld+17
; 2147: 04700000000   # feld+18
; 2150: 05000000000   # feld+19
;#PRUEFE-ENDE
