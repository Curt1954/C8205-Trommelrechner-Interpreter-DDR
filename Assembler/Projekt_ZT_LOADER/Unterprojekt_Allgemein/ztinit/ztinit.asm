; ztinit
; ERZEUGT von gen/ztinit_gen.py -- nicht von Hand aendern, Aenderungen im Generator.
; Belegung: 203 Zellen (Code 140, Daten 52, Literale 11), Grenze 3968.
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7240 (7600 minus 203 Zellen, abgerundet), Ausrichtung auf eine 040-Grenze (Tafeln und Spuren liegen relativ zum Start).
; #MACRODATEI1=../../macro_zt_loader.macro
; #DOK-0001 ztinit: alle vier ZT loeschen, Spur 0 von ZT 0 anlegen, ZT 0 am Ende angewaehlt
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
                211     @spuf00        ; AC := Adresse SPUF-00
                240     r1             ; R1 := Adresse SPUF-00
                025     ztinit         ; UP ztinit: alle ZT loeschen, Spur 0 anlegen, ZT 0 angewaehlt: Aufruf ztinit
                211     @spuf00        ; AC := Adresse SPUF-00 (jetzt Spur 0)
                210     #01000000601   ; plus Spurfeld zzz0 = 0100 (Spur 2) und Operationscode 601
                240     nach           ; Ausgabebefehl auf die naechste Zelle
nach:           db      01             ; Laufzeit: Ausgabe auf ZT0 Spur 2 OHNE neue Anwahl
                020     0              ; Halt
ztinit:         ZTINIT                 ; Unterprogramm ztinit (Makro aus macro_zt_loader.macro)
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
                db      020            ; SPUF-00 auf die Spurgrenze
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
; BZ=0116 US=1
; 0240: 52525252525   # spuf00
; 0241: 00000000000   # spuf00+1
; 0242: 00000000000   # spuf00+2
; 0243: 00000000000   # spuf00+3
; 0244: 00000000000   # spuf00+4
; 0245: 00000000000   # spuf00+5
; 0246: 00000000000   # spuf00+6
; 0247: 00000000000   # spuf00+7
; 0250: 00000000000   # spuf00+8
; 0251: 00000000000   # spuf00+9
; 0252: 00000000000   # spuf00+10
; 0253: 00000000000   # spuf00+11
; 0254: 00000000000   # spuf00+12
; 0255: 00000000000   # spuf00+13
; 0256: 00000000000   # spuf00+14
; 0257: 00000000000   # spuf00+15
; 0260: 00000000001   # spuf00+16
; 0261: 00000000000   # spuf00+17
; 0262: 00000000000   # spuf00+18
; 0263: 00000000040   # spuf00+19
; 0264: 00000000000   # spuf00+20
; 0265: 00000000000   # spuf00+21
; 0266: 00000000000   # spuf00+22
; 0267: 00000000000   # spuf00+23
; 0270: 00000000000   # spuf00+24
; 0271: 00000000000   # spuf00+25
; 0272: 00000000000   # spuf00+26
; 0273: 00000000000   # spuf00+27
; 0274: 00000000000   # spuf00+28
; 0275: 00000000000   # spuf00+29
; 0276: 00000000000   # spuf00+30
; 0277: 00000000000   # spuf00+31
; ZT-Zellen-Pruefung:
; 0-0000: 52525252525   # ZT0 Spur 0
; 0-0001: 00000000000   # ZT0 Spur 0
; 0-0002: 00000000000   # ZT0 Spur 0
; 0-0003: 00000000000   # ZT0 Spur 0
; 0-0004: 00000000000   # ZT0 Spur 0
; 0-0005: 00000000000   # ZT0 Spur 0
; 0-0006: 00000000000   # ZT0 Spur 0
; 0-0007: 00000000000   # ZT0 Spur 0
; 0-0010: 00000000000   # ZT0 Spur 0
; 0-0011: 00000000000   # ZT0 Spur 0
; 0-0012: 00000000000   # ZT0 Spur 0
; 0-0013: 00000000000   # ZT0 Spur 0
; 0-0014: 00000000000   # ZT0 Spur 0
; 0-0015: 00000000000   # ZT0 Spur 0
; 0-0016: 00000000000   # ZT0 Spur 0
; 0-0017: 00000000000   # ZT0 Spur 0
; 0-0020: 00000000001   # ZT0 Spur 0
; 0-0021: 00000000000   # ZT0 Spur 0
; 0-0022: 00000000000   # ZT0 Spur 0
; 0-0023: 00000000040   # ZT0 Spur 0
; 0-0024: 00000000000   # ZT0 Spur 0
; 0-0025: 00000000000   # ZT0 Spur 0
; 0-0026: 00000000000   # ZT0 Spur 0
; 0-0027: 00000000000   # ZT0 Spur 0
; 0-0030: 00000000000   # ZT0 Spur 0
; 0-0031: 00000000000   # ZT0 Spur 0
; 0-0032: 00000000000   # ZT0 Spur 0
; 0-0033: 00000000000   # ZT0 Spur 0
; 0-0034: 00000000000   # ZT0 Spur 0
; 0-0035: 00000000000   # ZT0 Spur 0
; 0-0036: 00000000000   # ZT0 Spur 0
; 0-0037: 00000000000   # ZT0 Spur 0
; 3-7740: 00000000000   # geloescht
; 3-7741: 00000000000   # geloescht
; 3-7745: 00000000000   # geloescht
; 3-7761: 00000000000   # geloescht
; 3-7762: 00000000000   # geloescht
; 3-7767: 00000000000   # geloescht
; 3-7777: 00000000000   # geloescht
; 3-3740: 00000000000   # geloescht
; 3-3741: 00000000000   # geloescht
; 3-3745: 00000000000   # geloescht
; 3-3761: 00000000000   # geloescht
; 3-3762: 00000000000   # geloescht
; 3-3767: 00000000000   # geloescht
; 3-3777: 00000000000   # geloescht
; 2-4000: 00000000000   # geloescht
; 2-4001: 00000000000   # geloescht
; 2-4005: 00000000000   # geloescht
; 2-4021: 00000000000   # geloescht
; 2-4022: 00000000000   # geloescht
; 2-4027: 00000000000   # geloescht
; 2-4037: 00000000000   # geloescht
; 1-0000: 00000000000   # geloescht
; 1-0001: 00000000000   # geloescht
; 1-0005: 00000000000   # geloescht
; 1-0021: 00000000000   # geloescht
; 1-0022: 00000000000   # geloescht
; 1-0027: 00000000000   # geloescht
; 1-0037: 00000000000   # geloescht
; 0-0040: 00000000000   # geloescht
; 0-0041: 00000000000   # geloescht
; 0-0045: 00000000000   # geloescht
; 0-0061: 00000000000   # geloescht
; 0-0062: 00000000000   # geloescht
; 0-0067: 00000000000   # geloescht
; 0-0077: 00000000000   # geloescht
; 0-7740: 00000000000   # geloescht
; 0-7741: 00000000000   # geloescht
; 0-7745: 00000000000   # geloescht
; 0-7761: 00000000000   # geloescht
; 0-7762: 00000000000   # geloescht
; 0-7767: 00000000000   # geloescht
; 0-7777: 00000000000   # geloescht
; 0-0100: 52525252525   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0101: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0102: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0103: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0104: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0105: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0106: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0107: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0110: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0111: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0112: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0113: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0114: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0115: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0116: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0117: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0120: 00000000001   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0121: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0122: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0123: 00000000040   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0124: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0125: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0126: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0127: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0130: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0131: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0132: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0133: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0134: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0135: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0136: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 0-0137: 00000000000   # ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)
; 1-0040: 00000000000   # nie beschrieben
; 3-0000: 00000000000   # nie beschrieben
; 0-0140: 00000000000   # nie beschrieben
;#PRUEFE-ENDE
