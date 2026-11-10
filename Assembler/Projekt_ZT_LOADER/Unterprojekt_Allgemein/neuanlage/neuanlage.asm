; neuanlage.asm - Test des Projektmakros NEUANL (Element 14 des ZIL: neuanlage Programm = SPUF-PN auf zwei ZT-Spuren schreiben)
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7000, Ausrichtung auf eine 040-Grenze (die Spurpuffer legt equ40 selbst auf Spurgrenzen).
; Ablauf: (1) SPUF-PN (64 Zellen) ist mit den Werten 01000 bis 01077 belegt (Zelle i = 01000 + i, oktal). (2) NEUANL mit R1 = SPUF-PN, R2 = 2 (Trommel), R3 = 5 (Spur): Zellen 0 bis 31 -> ZT 2 Spur 5, Zellen 32 bis 63 -> ZT 2 Spur 6.
;   (3) Zelle 0 des Puffers := 07654, zweiter Aufruf mit R2 = 3, R3 = 0176 (126): Zellen 0 bis 31 -> ZT 3 Spur 126, Zellen 32 bis 63 -> ZT 3 Spur 127 (hoechste erlaubte erste Spur).
;   (4) Ausgabe des Markerpuffers SPUF-00 (Zelle 0 = 0777) OHNE neue Anwahl auf Spur 0: sie muss auf ZT 3 landen (die Trommel des letzten Aufrufs bleibt angewaehlt).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 neuanlage: Projektmakro NEUANL (Element 14): SPUF-PN auf zwei Spuren je Trommel, zwei Aufrufe (ZT 2 Spur 5/6, ZT 3 Spur 126/127), Trommel bleibt angewaehlt
;#SPEI-0001 0001-0001
;#PROT STUFE=2

r1:             abs     07773                ; Register 1: SPUF-PN (Adressfeld)
r2:             abs     07776                ; Register 2: Trommelnummer
r3:             abs     07774                ; Register 3: Spurnummer der ersten Spur

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
apn:            da      spufpn               ; Zelle 0001: Adresse SPUF-PN (Adressfeld)
amk:            da      spuf00               ; Zelle 0002: Adresse des Markerpuffers (Adressfeld)

haupt:          211     apn                  ; AC := Adresse SPUF-PN
                240     r1                   ; R1 := SPUF-PN
                211     #2                   ; AC := 2
                240     r2                   ; R2 := Trommel 2
                211     #5                   ; AC := 5
                240     r3                   ; R3 := Spur 5 (zweite Spur: 6)
                025     neuanl               ; Element 14: SPUF-PN nach ZT 2 Spur 5 und 6
                211     #07654               ; AC := neuer Wert
                240     spufpn               ; Zelle 0 des Puffers := 07654
                211     #3                   ; AC := 3
                240     r2                   ; R2 := Trommel 3 (R1 bleibt)
                211     #0176                ; AC := 126
                240     r3                   ; R3 := Spur 126 (zweite Spur: 127)
                025     neuanl               ; Element 14: SPUF-PN nach ZT 3 Spur 126 und 127
                211     #0777                ; AC := Marker
                240     spuf00               ; Zelle 0 des Markerpuffers := 0777
                211     amk                  ; AC := Adresse des Markerpuffers
                210     #0601                ; plus Spur 0 und Operationscode 601, KEINE neue Anwahl
                240     ab1                  ; Ausgabebefehl auf die naechste Zelle
ab1:            db      1                    ; Laufzeit: Spur 0 der angewaehlten Trommel := Markerpuffer
                020     0                    ; Halt

; ---- UP neuanl: neuanlage Programm (Projektmakro NEUANL). R1 = SPUF-PN, R2 = Trommelnummer, R3 = Spurnummer der ersten Spur
neuanl:         NEUANL                       ; Unterprogramm (Makro)

; ---- Spurpuffer (je auf einer 040-Grenze)
                equ40   *                    ; Markerpuffer auf einer Spurgrenze
spuf00:         db      040                  ; Markerpuffer: 32 Zellen
                equ40   *                    ; SPUF-PN auf einer Spurgrenze
spufpn:         begin                        ; ein Block: der Optimierer darf die dw-Zeilen nicht verlegen
                dw      01000                  ; Zelle 0 (Spur 1 des Puffers, Zelle 0)
                dw      01001                  ; Zelle 1 (Spur 1 des Puffers, Zelle 1)
                dw      01002                  ; Zelle 2 (Spur 1 des Puffers, Zelle 2)
                dw      01003                  ; Zelle 3 (Spur 1 des Puffers, Zelle 3)
                dw      01004                  ; Zelle 4 (Spur 1 des Puffers, Zelle 4)
                dw      01005                  ; Zelle 5 (Spur 1 des Puffers, Zelle 5)
                dw      01006                  ; Zelle 6 (Spur 1 des Puffers, Zelle 6)
                dw      01007                  ; Zelle 7 (Spur 1 des Puffers, Zelle 7)
                dw      01010                  ; Zelle 8 (Spur 1 des Puffers, Zelle 8)
                dw      01011                  ; Zelle 9 (Spur 1 des Puffers, Zelle 9)
                dw      01012                  ; Zelle 10 (Spur 1 des Puffers, Zelle 10)
                dw      01013                  ; Zelle 11 (Spur 1 des Puffers, Zelle 11)
                dw      01014                  ; Zelle 12 (Spur 1 des Puffers, Zelle 12)
                dw      01015                  ; Zelle 13 (Spur 1 des Puffers, Zelle 13)
                dw      01016                  ; Zelle 14 (Spur 1 des Puffers, Zelle 14)
                dw      01017                  ; Zelle 15 (Spur 1 des Puffers, Zelle 15)
                dw      01020                  ; Zelle 16 (Spur 1 des Puffers, Zelle 16)
                dw      01021                  ; Zelle 17 (Spur 1 des Puffers, Zelle 17)
                dw      01022                  ; Zelle 18 (Spur 1 des Puffers, Zelle 18)
                dw      01023                  ; Zelle 19 (Spur 1 des Puffers, Zelle 19)
                dw      01024                  ; Zelle 20 (Spur 1 des Puffers, Zelle 20)
                dw      01025                  ; Zelle 21 (Spur 1 des Puffers, Zelle 21)
                dw      01026                  ; Zelle 22 (Spur 1 des Puffers, Zelle 22)
                dw      01027                  ; Zelle 23 (Spur 1 des Puffers, Zelle 23)
                dw      01030                  ; Zelle 24 (Spur 1 des Puffers, Zelle 24)
                dw      01031                  ; Zelle 25 (Spur 1 des Puffers, Zelle 25)
                dw      01032                  ; Zelle 26 (Spur 1 des Puffers, Zelle 26)
                dw      01033                  ; Zelle 27 (Spur 1 des Puffers, Zelle 27)
                dw      01034                  ; Zelle 28 (Spur 1 des Puffers, Zelle 28)
                dw      01035                  ; Zelle 29 (Spur 1 des Puffers, Zelle 29)
                dw      01036                  ; Zelle 30 (Spur 1 des Puffers, Zelle 30)
                dw      01037                  ; Zelle 31 (Spur 1 des Puffers, Zelle 31)
                dw      01040                  ; Zelle 32 (Spur 2 des Puffers, Zelle 0)
                dw      01041                  ; Zelle 33 (Spur 2 des Puffers, Zelle 1)
                dw      01042                  ; Zelle 34 (Spur 2 des Puffers, Zelle 2)
                dw      01043                  ; Zelle 35 (Spur 2 des Puffers, Zelle 3)
                dw      01044                  ; Zelle 36 (Spur 2 des Puffers, Zelle 4)
                dw      01045                  ; Zelle 37 (Spur 2 des Puffers, Zelle 5)
                dw      01046                  ; Zelle 38 (Spur 2 des Puffers, Zelle 6)
                dw      01047                  ; Zelle 39 (Spur 2 des Puffers, Zelle 7)
                dw      01050                  ; Zelle 40 (Spur 2 des Puffers, Zelle 8)
                dw      01051                  ; Zelle 41 (Spur 2 des Puffers, Zelle 9)
                dw      01052                  ; Zelle 42 (Spur 2 des Puffers, Zelle 10)
                dw      01053                  ; Zelle 43 (Spur 2 des Puffers, Zelle 11)
                dw      01054                  ; Zelle 44 (Spur 2 des Puffers, Zelle 12)
                dw      01055                  ; Zelle 45 (Spur 2 des Puffers, Zelle 13)
                dw      01056                  ; Zelle 46 (Spur 2 des Puffers, Zelle 14)
                dw      01057                  ; Zelle 47 (Spur 2 des Puffers, Zelle 15)
                dw      01060                  ; Zelle 48 (Spur 2 des Puffers, Zelle 16)
                dw      01061                  ; Zelle 49 (Spur 2 des Puffers, Zelle 17)
                dw      01062                  ; Zelle 50 (Spur 2 des Puffers, Zelle 18)
                dw      01063                  ; Zelle 51 (Spur 2 des Puffers, Zelle 19)
                dw      01064                  ; Zelle 52 (Spur 2 des Puffers, Zelle 20)
                dw      01065                  ; Zelle 53 (Spur 2 des Puffers, Zelle 21)
                dw      01066                  ; Zelle 54 (Spur 2 des Puffers, Zelle 22)
                dw      01067                  ; Zelle 55 (Spur 2 des Puffers, Zelle 23)
                dw      01070                  ; Zelle 56 (Spur 2 des Puffers, Zelle 24)
                dw      01071                  ; Zelle 57 (Spur 2 des Puffers, Zelle 25)
                dw      01072                  ; Zelle 58 (Spur 2 des Puffers, Zelle 26)
                dw      01073                  ; Zelle 59 (Spur 2 des Puffers, Zelle 27)
                dw      01074                  ; Zelle 60 (Spur 2 des Puffers, Zelle 28)
                dw      01075                  ; Zelle 61 (Spur 2 des Puffers, Zelle 29)
                dw      01076                  ; Zelle 62 (Spur 2 des Puffers, Zelle 30)
                dw      01077                  ; Zelle 63 (Spur 2 des Puffers, Zelle 31)
                bend
schluss:        end

; Sollwerte von Hand hergeleitet (Zelle i des Puffers = 01000 + i oktal; ZT-Zelle = Spur * 040 + Zelle in der Spur):
; Aufruf 1 (Trommel 2, Spur 5): Spur 5 liegt auf ZT-Zellen 5 * 32 = 160 dez = 0240 bis 0277, Spur 6 auf 0300 bis 0337. Puffer-Zelle 0 (01000) -> 2-0240, Zelle 31 (01037) -> 2-0277,
;   Zelle 32 (01040) -> 2-0300, Zelle 63 (01077) -> 2-0337. Die Nachbarspuren 4 (2-0200) und 7 (2-0340) bleiben 0, ebenso Trommel 0 (0-0240): es wird nur die angewaehlte Trommel beschrieben.
; Aufruf 2 (Trommel 3, Spur 126), Puffer-Zelle 0 jetzt 07654: Spur 126 liegt auf 126 * 32 = 4032 dez = 07700 bis 07737, Spur 127 auf 07740 bis 07777. 3-7700 = 07654 (neu), 3-7701 = 01001 (Zelle 1),
;   3-7737 = 01037 (Zelle 31), 3-7740 = 01040 (Zelle 32), 3-7777 = 01077 (Zelle 63); Spur 125 (3-7677) bleibt 0. Der erste Aufruf (2-0240 = 01000) ist durch die Aenderung der Zelle 0 nicht beruehrt.
; Markerausgabe ohne neue Anwahl: Spur 0 der angewaehlten Trommel 3 = Markerpuffer, 3-0000 = 0777; auf ZT 2 und ZT 0 bleibt Zelle 0000 gleich 0.
; Register nach dem Lauf: R1 (7773) = Adresse SPUF-PN im Adressfeld = 0100 * 01000 = 00000100000 (spufpn liegt laut .dmp auf 0100, Layout), R2 (7776) = 3, R3 (7774) = 0176 (unveraendert durch NEUANL).
; Layout: NEUANL ist TYP=M ohne equ100/equ40 am Anfang (Gruppe 4) und wandert mit der Makro-Umordnung (Vorgabe ab c82ass 1.03-007) hinter end; hinter dem Halt (Zelle 0027) beginnt spuf00 nach equ40 * auf 0040,
;   spufpn nach equ40 * auf 0100 (64 Zellen bis 0177), schluss 0200. Ohne Umordnung (Pragma ;#MAKROUMORDNEN=NO) lag spufpn auf 0140 (0140 * 01000 = 00000140000).
;#PRUEFE-START
; US=1
; 7773: 00000100000   # R1 unveraendert: Adresse SPUF-PN im Adressfeld
; 7776: 00000000003   # R2 unveraendert: Trommel 3 (letzter Aufruf)
; 7774: 00000000176   # R3 unveraendert: Spur 126 (letzter Aufruf)
; ZT-Zellen-Pruefung:
; 2-0240: 00000001000   # Aufruf 1: Puffer-Zelle 0 -> ZT 2 Spur 5 Zelle 0
; 2-0277: 00000001037   # Puffer-Zelle 31 -> letzte Zelle von Spur 5
; 2-0300: 00000001040   # Puffer-Zelle 32 -> ZT 2 Spur 6 Zelle 0 (zweite Spur)
; 2-0337: 00000001077   # Puffer-Zelle 63 -> letzte Zelle von Spur 6
; 2-0200: 00000000000   # Spur 4 (Nachbarspur davor) unberuehrt
; 2-0340: 00000000000   # Spur 7 (Nachbarspur dahinter) unberuehrt
; 0-0240: 00000000000   # Trommel 0 unberuehrt (nur die angewaehlte Trommel wird beschrieben)
; 3-7700: 00000007654   # Aufruf 2: Puffer-Zelle 0 (jetzt 07654) -> ZT 3 Spur 126 Zelle 0
; 3-7701: 00000001001   # Puffer-Zelle 1
; 3-7737: 00000001037   # Puffer-Zelle 31 -> letzte Zelle von Spur 126
; 3-7740: 00000001040   # Puffer-Zelle 32 -> ZT 3 Spur 127 Zelle 0 (zweite Spur)
; 3-7777: 00000001077   # Puffer-Zelle 63 -> letzte Zelle von Spur 127
; 3-7677: 00000000000   # Spur 125 (Nachbarspur davor) unberuehrt
; 3-0000: 00000000777   # Markerausgabe ohne neue Anwahl landet auf ZT 3 (die Trommel bleibt angewaehlt)
; 2-0000: 00000000000   # nicht auf ZT 2
; 0-0000: 00000000000   # nicht auf ZT 0
;#PRUEFE-ENDE
