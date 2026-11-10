; kat5_sort2_makro: Sortier-UP (Makro KAT5SORT2, Rel 0000) fuer Paare (kat5, Wert) und Hauptprogramm, erzeugt von gen/kat5_sort2_makro_gen.py
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5_sort2_makro
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5_sort2_makro-sw-ausgabe.txt
;#TESTBASIS 02000 haupt
r1:             abs     07773                ; Register 1: Adresse des Wortes fuer KAT5AUSGABE (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle fuer KAT5AUSGABE (Adressfeld)
                start                 ; Zaehlung beginnt bei 0000
sort2:          KAT5SORT2              ; UP KAT5SORT2 (Rumpf aus c82ass.makros, Zelle 0000 bis 0104); Parameter auf Marke+1 und Marke+2

; ==========================================================
;   RELATIVE START-ADRESSE DES HAUPTPROGRAMMS:  0105
;   BIS: Leitadresse 21 2000 .   Start: 10 2105 000 .
; ==========================================================

haupt:          .LD     @feld         ; AC := Adresse des Feldes
                .STO    sort2+1       ; Parameter 1 eintragen (Zelle Marke+1)
                .LD     #024          ; AC := 20 (Anzahl der Paare)
                .STO    sort2+2       ; Parameter 2 eintragen (Zelle Marke+2)
                025     sort2         ; Aufruf des Unterprogramms
                .LD     @kbaus        ; AC := Adresse der KB/GB-Zelle des Schreibwerks
                .STO    r3            ; R3 := Adresse der Zustandszelle (Festlegung 030)
                ANWAHL  K2            ; Kanal 2 = Schreibwerk anwaehlen
                .LD     @init         ; AC := Adresse des Wortes Zeilenschaltung + Um. KB
                .STO    r1            ; R1 := Adresse von init
                025     ausgabe       ; neue Zeile und Um. KB drucken (das BIS laesst das Schreibwerk auf GB)
                .LD     @feld         ; AC := Adresse des (sortierten) Feldes
                .STO    pa            ; pa := Adresse des ersten Textes
                .LD     #024          ; AC := 20 (Anzahl der Paare)
                .STO    pz            ; pz := Zaehler der noch zu druckenden Texte
pl:             .LD     pa            ; AC := Adresse des aktuellen Textes
                .STO    r1            ; R1 := Adresse des Textes
                025     ausgabe       ; Text drucken (KAT5AUSGABE)
                .LD     @zeil         ; AC := Adresse des Wortes Zeilenschaltung
                .STO    r1            ; R1 := Adresse von zeil
                025     ausgabe       ; Zeilenschaltung drucken
                .LD     pa            ; AC := Adresse des aktuellen Textes
                .ADD    #02000        ; AC := Adresse des naechsten Textes (ein Paar = zwei Adresseinheiten weiter)
                .STO    pa            ; pa := Adresse des naechsten Textes
                .LD     pz            ; AC := Zaehler
                .SUB    #01           ; AC := Zaehler - 1
                .STO    pz            ; pz := AC
                .CMP    #0            ; AC mit 0 vergleichen
                .JVG3   halt          ; Zaehler = 0: alle Texte gedruckt, Halt
                .JMP    pl            ; sonst naechster Text
halt:           .STOP   0             ; Halt: Feld ist sortiert und gedruckt
feld:           kat5    uikxf         ; Paar[0] kat5 = uikxf, Wort 04531335026
                dw      0451          ; Paar[0] Wert = 0451
                kat5    hhi1h         ; Paar[1] kat5 = hhi1h, Wort 03030311030
                dw      0502          ; Paar[1] Wert = 0502
                kat5    1y            ; Paar[2] kat5 = 1y, Wort 01051000000
                dw      0445          ; Paar[2] Wert = 0445
                kat5    fu            ; Paar[3] kat5 = fu, Wort 02645000000
                dw      0570          ; Paar[3] Wert = 0570
                kat5    8pre          ; Paar[4] kat5 = 8pre, Wort 01740422500
                dw      0702          ; Paar[4] Wert = 0702
                kat5    w             ; Paar[5] kat5 = w, Wort 04700000000
                dw      0552          ; Paar[5] Wert = 0552
                kat5    lh17c         ; Paar[6] kat5 = lh17c, Wort 03430101623
                dw      0550          ; Paar[6] Wert = 0550
                kat5    d0n           ; Paar[7] kat5 = d0n, Wort 02407360000
                dw      0644          ; Paar[7] Wert = 0644
                kat5    r29pd         ; Paar[8] kat5 = r29pd, Wort 04211204024
                dw      022           ; Paar[8] Wert = 0022
                kat5    z             ; Paar[9] kat5 = z, Wort 05200000000
                dw      0674          ; Paar[9] Wert = 0674
                kat5    rns           ; Paar[10] kat5 = rns, Wort 04236430000
                dw      0457          ; Paar[10] Wert = 0457
                kat5    7             ; Paar[11] kat5 = 7, Wort 01600000000
                dw      026           ; Paar[11] Wert = 0026
                kat5    pzh           ; Paar[12] kat5 = pzh, Wort 04052300000
                dw      0161          ; Paar[12] Wert = 0161
                kat5    due           ; Paar[13] kat5 = due, Wort 02445250000
                dw      0375          ; Paar[13] Wert = 0375
                kat5    mk4z          ; Paar[14] kat5 = mk4z, Wort 03533135200
                dw      0571          ; Paar[14] Wert = 0571
                kat5    f4            ; Paar[15] kat5 = f4, Wort 02613000000
                dw      0726          ; Paar[15] Wert = 0726
                kat5    x0            ; Paar[16] kat5 = x0, Wort 05007000000
                dw      0373          ; Paar[16] Wert = 0373
                kat5    yv11f         ; Paar[17] kat5 = yv11f, Wort 05146101026
                dw      0414          ; Paar[17] Wert = 0414
                kat5    2x65          ; Paar[18] kat5 = 2x65, Wort 01150151400
                dw      0723          ; Paar[18] Wert = 0723
                kat5    ces           ; Paar[19] kat5 = ces, Wort 02325430000
                dw      0337          ; Paar[19] Wert = 0337
zeil:           kat5    $wrzl         ; Wort Zeilenschaltung (kat5 053), steht hinter dem Feld
init:           kat5    $wrzl$inkb    ; Wort Zeilenschaltung und Um. KB (kat5 053, 054): Anfang des Drucks
kbaus:          dw      0             ; KB/GB-Zustand des Schreibwerks (0 = KB, 1 = GB), anfangs KB (Festlegung 030)
pa:             db      01            ; Arbeitszelle pa: Adresse des aktuellen Textes beim Drucken
pz:             db      01            ; Arbeitszelle pz: Zaehler beim Drucken
ausgabe:        KAT5AUSGABE              ; UP KAT5AUSGABE (Rumpf aus c82ass.makros, Tabelle dahinter)
ende:           end                   ; Programmende

;#PRUEFE-START
; BZ=2144 US=1
; 2144: 01051000000   # feld+0 kat5 1y
; 2145: 00000000445   # feld+1 Wert zu 1y
; 2146: 01150151400   # feld+2 kat5 2x65
; 2147: 00000000723   # feld+3 Wert zu 2x65
; 2150: 01600000000   # feld+4 kat5 7
; 2151: 00000000026   # feld+5 Wert zu 7
; 2152: 01740422500   # feld+6 kat5 8pre
; 2153: 00000000702   # feld+7 Wert zu 8pre
; 2154: 02325430000   # feld+8 kat5 ces
; 2155: 00000000337   # feld+9 Wert zu ces
; 2156: 02407360000   # feld+10 kat5 d0n
; 2157: 00000000644   # feld+11 Wert zu d0n
; 2160: 02445250000   # feld+12 kat5 due
; 2161: 00000000375   # feld+13 Wert zu due
; 2162: 02613000000   # feld+14 kat5 f4
; 2163: 00000000726   # feld+15 Wert zu f4
; 2164: 02645000000   # feld+16 kat5 fu
; 2165: 00000000570   # feld+17 Wert zu fu
; 2166: 03030311030   # feld+18 kat5 hhi1h
; 2167: 00000000502   # feld+19 Wert zu hhi1h
; 2170: 03430101623   # feld+20 kat5 lh17c
; 2171: 00000000550   # feld+21 Wert zu lh17c
; 2172: 03533135200   # feld+22 kat5 mk4z
; 2173: 00000000571   # feld+23 Wert zu mk4z
; 2174: 04052300000   # feld+24 kat5 pzh
; 2175: 00000000161   # feld+25 Wert zu pzh
; 2176: 04211204024   # feld+26 kat5 r29pd
; 2177: 00000000022   # feld+27 Wert zu r29pd
; 2200: 04236430000   # feld+28 kat5 rns
; 2201: 00000000457   # feld+29 Wert zu rns
; 2202: 04531335026   # feld+30 kat5 uikxf
; 2203: 00000000451   # feld+31 Wert zu uikxf
; 2204: 04700000000   # feld+32 kat5 w
; 2205: 00000000552   # feld+33 Wert zu w
; 2206: 05007000000   # feld+34 kat5 x0
; 2207: 00000000373   # feld+35 Wert zu x0
; 2210: 05146101026   # feld+36 kat5 yv11f
; 2211: 00000000414   # feld+37 Wert zu yv11f
; 2212: 05200000000   # feld+38 kat5 z
; 2213: 00000000674   # feld+39 Wert zu z
;#PRUEFE-ENDE
