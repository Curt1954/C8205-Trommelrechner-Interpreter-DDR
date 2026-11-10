; ztinit_vor
; ERZEUGT von gen/ztinit_vor_gen.py -- nicht von Hand aendern, Aenderungen im Generator.
; Belegung: 138 Zellen (Code 86, Daten 42, Literale 10), Grenze 3968.
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7340 (7600 minus 138 Zellen, abgerundet), Ausrichtung auf eine 040-Grenze (Tafeln und Spuren liegen relativ zum Start).
; #MACRODATEI1=../../macro_zt_loader.macro
; #DOK-0001 ztinit_vor: nur die Vorbelegung der Zusatztrommeln, ztinit wird nicht aufgerufen
; #SPEI-0001 0001-0001
; #PROT STUFE=2
; #ZTROMMEL=LEER
                start                ; Zaehlung beginnt bei 0000
                211     @spuf00        ; ZT3 Spur 127 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT3 Spur 127 mit spuf00 belegen: Pufferspur merken
                211     #03            ; ZT3 Spur 127 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT3 Spur 127 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT3 Spur 127 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #0177          ; ZT3 Spur 127 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT3 Spur 127 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT3 Spur 127 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT3 Spur 127 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT3 Spur 127 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT3 Spur 63 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT3 Spur 63 mit spuf00 belegen: Pufferspur merken
                211     #03            ; ZT3 Spur 63 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT3 Spur 63 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT3 Spur 63 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #077           ; ZT3 Spur 63 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT3 Spur 63 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT3 Spur 63 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT3 Spur 63 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT3 Spur 63 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT2 Spur 64 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT2 Spur 64 mit spuf00 belegen: Pufferspur merken
                211     #02            ; ZT2 Spur 64 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT2 Spur 64 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT2 Spur 64 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #0100          ; ZT2 Spur 64 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT2 Spur 64 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT2 Spur 64 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT2 Spur 64 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT2 Spur 64 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT1 Spur 0 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT1 Spur 0 mit spuf00 belegen: Pufferspur merken
                211     #01            ; ZT1 Spur 0 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT1 Spur 0 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT1 Spur 0 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #0             ; ZT1 Spur 0 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT1 Spur 0 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT1 Spur 0 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT1 Spur 0 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT1 Spur 0 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT0 Spur 1 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT0 Spur 1 mit spuf00 belegen: Pufferspur merken
                211     #0             ; ZT0 Spur 1 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT0 Spur 1 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT0 Spur 1 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #01            ; ZT0 Spur 1 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT0 Spur 1 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT0 Spur 1 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT0 Spur 1 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT0 Spur 1 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT0 Spur 127 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT0 Spur 127 mit spuf00 belegen: Pufferspur merken
                211     #0             ; ZT0 Spur 127 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT0 Spur 127 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT0 Spur 127 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #0177          ; ZT0 Spur 127 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT0 Spur 127 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT0 Spur 127 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT0 Spur 127 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT0 Spur 127 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                211     @spuf00        ; ZT0 Spur 0 mit spuf00 belegen: AC := Adresse der Pufferspur spuf00
                240     zc_adr         ; ZT0 Spur 0 mit spuf00 belegen: Pufferspur merken
                211     #0             ; ZT0 Spur 0 mit spuf00 belegen: AC := Trommel t
                240     zt_t           ; ZT0 Spur 0 mit spuf00 belegen: Trommel merken
                025     zt_anw         ; ZT0 Spur 0 mit spuf00 belegen: ZT anwaehlen: Aufruf zt_anw
                211     #0             ; ZT0 Spur 0 mit spuf00 belegen: AC := Spur
                240     zc_spur        ; ZT0 Spur 0 mit spuf00 belegen: Spur merken
                211     #0601          ; ZT0 Spur 0 mit spuf00 belegen: AC := Operationscode 601 (HT -> ZT)
                240     zc_op          ; ZT0 Spur 0 mit spuf00 belegen: Operationscode merken
                025     zt_ausf        ; ZT0 Spur 0 mit spuf00 belegen: Spur uebertragen: Aufruf zt_ausf
                020     0              ; Halt
zt_anw:         240     rueck_zt_anw   ; Rueckkehrwort sichern: Zusatztrommel zt_t anwaehlen (5k00 030, k = t + 1; 5100 = ZT0 bis 5400 = ZT3)
                211     zt_t           ; AC := t
                646     07675          ; um 15 Bit nach links: AC um 15 Bit zyklisch links
                210     #05100030      ; plus Befehl 5100 030
                240     zw_x           ; Befehl ablegen
zw_x:           db      01             ; hier steht 5k00 030
rueck_zt_anw:   db      01             ; Rueckkehrzelle von zt_anw: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
zt_ausf:        240     rueck_zt_ausf  ; Rueckkehrwort sichern: Befehl zzz0 bbbb 601/661 aus zc_spur, zc_adr und zc_op bilden und ausfuehren
                211     zc_spur        ; AC := Spur
                646     07656          ; um 26 Bit nach links (zzz0): AC um 26 Bit zyklisch links
                210     zc_adr         ; plus Adresse der Pufferspur
                210     zc_op          ; plus Operationscode
                240     za_x           ; Befehl ablegen
za_x:           db      01             ; hier steht der ZT-Befehl
rueck_zt_ausf:  db      01             ; Rueckkehrzelle von zt_ausf: zur Laufzeit 000 <Rueckkehradresse> (Festlegung 010)
r1:             abs     07773          ; Register 1: Adresse von SPUF-00 fuer ztinit
zt_t:           db      01             ; Trommel
zc_spur:        db      01             ; Spur
zc_op:          db      01             ; Operationscode
zc_adr:         db      01             ; Adresse der Pufferspur
                db      06             ; SPUF-00 auf die Spurgrenze
                begin                  ; Feld spuf00 (zusammengehoerige Worte)
spuf00:         dw      0111           ; spuf00[0] = 73
                dw      0222           ; spuf00[1] = 146
                dw      0              ; spuf00[2] = 0
                dw      0              ; spuf00[3] = 0
                dw      0              ; spuf00[4] = 0
                dw      0777           ; spuf00[5] = 511
                dw      0              ; spuf00[6] = 0
                dw      0              ; spuf00[7] = 0
                dw      0              ; spuf00[8] = 0
                dw      0              ; spuf00[9] = 0
                dw      0              ; spuf00[10] = 0
                dw      0              ; spuf00[11] = 0
                dw      0              ; spuf00[12] = 0
                dw      0              ; spuf00[13] = 0
                dw      0              ; spuf00[14] = 0
                dw      0              ; spuf00[15] = 0
                dw      0              ; spuf00[16] = 0
                dw      0444           ; spuf00[17] = 292
                dw      0666           ; spuf00[18] = 438
                dw      0              ; spuf00[19] = 0
                dw      0              ; spuf00[20] = 0
                dw      0              ; spuf00[21] = 0
                dw      0              ; spuf00[22] = 0
                dw      0555           ; spuf00[23] = 365
                dw      0              ; spuf00[24] = 0
                dw      0              ; spuf00[25] = 0
                dw      0              ; spuf00[26] = 0
                dw      0              ; spuf00[27] = 0
                dw      0              ; spuf00[28] = 0
                dw      0              ; spuf00[29] = 0
                dw      0              ; spuf00[30] = 0
                dw      0333           ; spuf00[31] = 219
                bend                   ; Ende Feld spuf00
                end                  ; Programmende

; Sollwerte aus dem Python-Modell des Generators (unabhaengig vom Assemblerprogramm).
;#PRUEFE-START
; BZ=0107 US=1
; ZT-Zellen-Pruefung:
; 3-7740: 00000000111   # vorbelegt
; 3-7741: 00000000222   # vorbelegt
; 3-7745: 00000000777   # vorbelegt
; 3-7761: 00000000444   # vorbelegt
; 3-7762: 00000000666   # vorbelegt
; 3-7767: 00000000555   # vorbelegt
; 3-7777: 00000000333   # vorbelegt
; 3-3740: 00000000111   # vorbelegt
; 3-3741: 00000000222   # vorbelegt
; 3-3745: 00000000777   # vorbelegt
; 3-3761: 00000000444   # vorbelegt
; 3-3762: 00000000666   # vorbelegt
; 3-3767: 00000000555   # vorbelegt
; 3-3777: 00000000333   # vorbelegt
; 2-4000: 00000000111   # vorbelegt
; 2-4001: 00000000222   # vorbelegt
; 2-4005: 00000000777   # vorbelegt
; 2-4021: 00000000444   # vorbelegt
; 2-4022: 00000000666   # vorbelegt
; 2-4027: 00000000555   # vorbelegt
; 2-4037: 00000000333   # vorbelegt
; 1-0000: 00000000111   # vorbelegt
; 1-0001: 00000000222   # vorbelegt
; 1-0005: 00000000777   # vorbelegt
; 1-0021: 00000000444   # vorbelegt
; 1-0022: 00000000666   # vorbelegt
; 1-0027: 00000000555   # vorbelegt
; 1-0037: 00000000333   # vorbelegt
; 0-0040: 00000000111   # vorbelegt
; 0-0041: 00000000222   # vorbelegt
; 0-0045: 00000000777   # vorbelegt
; 0-0061: 00000000444   # vorbelegt
; 0-0062: 00000000666   # vorbelegt
; 0-0067: 00000000555   # vorbelegt
; 0-0077: 00000000333   # vorbelegt
; 0-7740: 00000000111   # vorbelegt
; 0-7741: 00000000222   # vorbelegt
; 0-7745: 00000000777   # vorbelegt
; 0-7761: 00000000444   # vorbelegt
; 0-7762: 00000000666   # vorbelegt
; 0-7767: 00000000555   # vorbelegt
; 0-7777: 00000000333   # vorbelegt
; 0-0000: 00000000111   # vorbelegt
; 0-0001: 00000000222   # vorbelegt
; 0-0005: 00000000777   # vorbelegt
; 0-0021: 00000000444   # vorbelegt
; 0-0022: 00000000666   # vorbelegt
; 0-0027: 00000000555   # vorbelegt
; 0-0037: 00000000333   # vorbelegt
; 1-0040: 00000000000   # nie beschrieben
; 3-0000: 00000000000   # nie beschrieben
; 0-0100: 00000000000   # nie beschrieben
;#PRUEFE-ENDE
