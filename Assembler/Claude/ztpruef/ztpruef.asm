; ztpruef.asm - Test der Testmarke #ZTROMMEL und der ZT-Zellen-Pruefung (Interpreter 0.95-014, Assembler 1.00-056)
; Das Programm gibt die HT-Spur 0040 (Zellen 0040 bis 0077, Sektoren 00 bis 37) auf ZT2 Spur 0 (ZT-Zellen 0000 bis 0037) aus
; (Anwahl 5300 030, Befehl 601 mit zzz0 = 0000, bbbb = Adresse der Spur). Danach Halt auf 0004.
;#ZTROMMEL=LEER
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                dbn     1            ; Zelle 0001: frei
                dbn     1            ; Zelle 0002: frei
haupt:          030     05300        ; Zelle 0003: Anwahl der Zusatztrommel ZT2 (5300 030 = 5k00 mit k = 3)
                601     spur         ; Ausgabe HT-Spur (Adresse spur) auf ZT2 Spur 0
                020     0            ; Halt
                dbn     031          ; Fuellung bis Zelle 0037
                dbn     1            ; Zelle 0037
spur:           dw      0111         ; Zelle 0040: Sektor 00 der Spur (ZT-Zelle 0000)
                dw      0222         ; Zelle 0041: Sektor 01
                dbn     036          ; Zellen 0042 bis 0077: Rest der Spur = 0
ende:           end

; Sollwerte von Hand hergeleitet: Befehle 0003 (030), 0004 (601), 0005 (020): Halt auf 0005, danach BZ = 0006 (wie mini: Halt auf 0006 -> BZ 0007).
; ZT2 Zelle 0000 = 0111, Zelle 0001 = 0222, Zelle 0002 = 0 (Rest der Spur), Zelle 0040 (Spur 1) = 0 (nicht beschrieben); ZT0 Zelle 0000 = 0 (nach LEER).
;#PRUEFE-START
; BZ=0006 US=1
; ZT-Zellen-Pruefung:
; 2-0000: 00000000111
; 2-0001: 00000000222
; 2-0002: 00000000000
; 2-0040: 00000000000
; 0-0000: 00000000000
;#PRUEFE-ENDE
