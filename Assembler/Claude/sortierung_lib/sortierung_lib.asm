; sortierung -- 4 Namen aufsteigend ordnen (UP sort, Parameter sn und sla)
; ERZEUGT von Assembler/Claude/sortierung_lib/gen/sortierung_lib_gen.py -- nicht von Hand aendern, Aenderungen im Generator.
; Belegung: 52 Zellen (Code 38, Daten 9, Literale 5), Grenze 64.
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7514 (7600 minus 52 Zellen), Ausrichtung egal.
                start                ; Zaehlung beginnt bei 0000
                211     #04000         ; AC := 04000
                240     sn             ; sn := AC
                211     @feld          ; AC := Adresse feld
                240     sla            ; sla := AC
                025     sort           ; Aufruf sort
                020     0              ; Halt: Feld ist sortiert
sort:           240     rueck_sort     ; Rueckkehrwort sichern
                001     sinit          ; AC := 0, weiter
sinit:          240     si             ; i := 0
                210     #01000         ; AC := i + 1
skset:          240     sk             ; k := i + 1
                210     sla            ; AC := AC + sla
                210     #0240          ; Befehl 240 a(k+1) bauen
                240     sb1            ; sb1 := AC
                251     0              ; AC := a(k+1)
                240     sh             ; H := a(k+1)
                211     si             ; AC := si
                210     sla            ; AC := AC + sla
                210     #0240          ; Befehl 240 a(i+1) bauen
                240     sb2            ; sb2 := AC
                251     0              ; AC := a(i+1)
                330     sh             ; AC mit sh vergleichen
                140     sknext         ; a(i+1) <= H: nicht tauschen
sb1:            db      01             ; zur Laufzeit 240 a(k+1)
                211     sh             ; AC := sh
sb2:            db      01             ; zur Laufzeit 240 a(i+1)
sknext:         211     sk             ; AC := sk
                210     #01000         ; AC := AC + 01000
                330     sn             ; AC mit sn vergleichen
                170     sinext         ; k + 1 = n: innere Schleife fertig
                000     skset          ; weiter bei skset
sinext:         211     si             ; AC := si
                210     #02000         ; AC := i + 2
                330     sn             ; AC mit sn vergleichen
                170     rueck_sort     ; i + 2 = n: Rueckkehr
                220     #01000         ; AC := i + 1
                000     sinit          ; weiter bei sinit
rueck_sort:     db      01             ; Rueckkehrzelle von sort: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
sn:             db      01             ; Zelle sn
sla:            db      01             ; Zelle sla
si:             db      01             ; Zelle si
sk:             db      01             ; Zelle sk
sh:             db      01             ; Zelle sh
                begin                  ; Feld feld (zusammengehoerige Worte)
feld:           dw      010021054460   ; Name[0] = 1078221104
                dw      013371052070   ; Name[1] = 1541690424
                dw      013300654600   ; Name[2] = 1526946176
                dw      011206050000   ; Name[3] = 1243107328
                bend                   ; Ende Feld feld
                end                  ; Programmende

; Sollwerte aus dem Python-Modell des Generators (unabhaengig vom Assemblerprogramm).
;#PRUEFE-START
; BZ=0006 US=1
; 0053: 10021054460   # feld+0
; 0054: 11206050000   # feld+1
; 0055: 13300654600   # feld+2
; 0056: 13371052070   # feld+3
;#PRUEFE-ENDE
