; pname.asm - Test des Projektmakros PNAME (Element 13 des ZIL: Programmname eintragen) mit 11a (SPUF-PN = 2 Spuren, zwei Gruppenbefehle 441); Name als kat5 (eine Zelle), Eintrag zu 2 Zellen
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 7000, Ausrichtung auf eine 040-Grenze (die Spurpuffer legt equ40 selbst auf Spurgrenzen).
; Ablauf: (1) SPUF-PN mit Mist in Zelle 20 (Spur 1 des Puffers) und Zelle 40 (Spur 2 des Puffers) belegen, dann 11a: zwei 441 (je Spur eines). (2) Wort 2 des Eintrags ID 3 (Zelle 5) vorbelegen
;   mit z0 = 1 und Laenge 5252 (muss erhalten bleiben), Wort 1 des Eintrags ID 3 (Zelle 4) mit Mist (wird ueberschrieben). (3) SPUF-00: Zaehler (Zelle 17) = 2, Trommel (18) = 0, Spur (19) = 0177 = 127.
;   (4) PNAME mit R1 = SPUF-PN, R2 = Namenszelle n1, R3 = SPUF-00; danach zweiter Aufruf mit der Namenszelle n2; dritter Aufruf mit Zaehler 31 (ID 32, letzter Eintrag von SPUF-PN, Zellen 62 und 63) und der Namenszelle n3.
;   (5) SPUF-PN Spur 1 und 2 auf ZT 0 Spur 1 und 2, SPUF-00 auf ZT 0 Spur 0 schreiben.
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 pname: Projektmakro PNAME (Element 13) mit 11a, drei Aufrufe (ID 3, 4 und 32), kat5-Name in einer Zelle, Eintrag zu 2 Zellen, Uebertrag Spur 127 -> Trommel 1 Spur 0, Wort 2 nur in den eigenen Feldern
;#SPEI-0001 0001-0001
;#PROT STUFE=2

r1:             abs     07773                ; Register 1: SPUF-PN (Adressfeld)
r2:             abs     07776                ; Register 2: Adresse der Namenszelle (Adressfeld)
r3:             abs     07774                ; Register 3: SPUF-00 (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
apn:            da      spufpn               ; Zelle 0001: Adresse SPUF-PN (Adressfeld)
a00:            da      spuf00               ; Zelle 0002: Adresse SPUF-00 (Adressfeld)
anm1:           da      n1                   ; Zelle 0003: Namenszelle n1 (Eintrag ID 3)
anm2:           da      n2                   ; Zelle 0004: Namenszelle n2 (Eintrag ID 4)
anm3:           da      n3                   ; Zelle 0005: Namenszelle n3 (Eintrag ID 32)

haupt:          211     #07777777777         ; AC := Mist
                240     spufpn+024           ; Mist in Zelle 20 des Puffers (Spur 1 des Puffers)
                240     spufpn+050           ; Mist in Zelle 40 des Puffers (Spur 2 des Puffers)
                441     spufpn               ; 11a: Spur 1 des Puffers := 0
                441     spufpn+040           ; 11a: Spur 2 des Puffers := 0
                211     #07777777777         ; AC := Mist
                240     spufpn+4             ; Wort 1 des Eintrags ID 3 (Zelle 4): Mist (wird ueberschrieben)
                211     #040000005252        ; AC := z0 = 1 und Laenge 5252 (bleiben erhalten)
                240     spufpn+5             ; Wort 2 des Eintrags ID 3 (Zelle 5) vorbelegt
                211     #2                   ; AC := Zaehler 2 (zwei Programme vergeben)
                240     spuf00+021           ; SPUF-00 Zelle 17 := 2
                241     spuf00+022           ; SPUF-00 Zelle 18 := 0 (letzte belegte Trommel)
                211     #0177                ; AC := 127 (letzte belegte Spur)
                240     spuf00+023           ; SPUF-00 Zelle 19 := 127
                211     apn                  ; AC := Adresse SPUF-PN
                240     r1                   ; R1 := SPUF-PN
                211     anm1                 ; AC := Adresse n1
                240     r2                   ; R2 := Namenszelle n1
                211     a00                  ; AC := Adresse SPUF-00
                240     r3                   ; R3 := SPUF-00
                025     pname                ; Element 13: Eintrag ID 3 (Zellen 4 und 5)
                211     anm2                 ; AC := Adresse n2
                240     r2                   ; R2 := Namenszelle n2 (R1 und R3 bleiben)
                025     pname                ; Element 13: Eintrag ID 4 (Zellen 6 und 7)
                211     #31                  ; AC := 31 (dezimal): 31 Programme vergeben, die naechste ID ist 32
                240     spuf00+021           ; SPUF-00 Zelle 17 := 31
                211     anm3                 ; AC := Adresse n3
                240     r2                   ; R2 := Namenszelle n3
                025     pname                ; Element 13: Eintrag ID 32 (Zellen 62 und 63, Ende von SPUF-PN)
                030     05100                ; Anwahl ZT 0 (5100 030)
                211     apn                  ; AC := Adresse SPUF-PN
                210     #0400000601          ; plus Spur 1 (1 * 2^26) und Operationscode 601
                240     ab1                  ; Ausgabebefehl auf die naechste Zelle
ab1:            db      1                    ; Laufzeit: Spur 1 von ZT 0 := Spur 1 des Puffers
                211     apn                  ; AC := Adresse SPUF-PN
                210     #01000040601         ; plus Spur 2 (2 * 2^26), 32 Zellen (040 * 01000 = 040000) und 601
                240     ab2                  ; Ausgabebefehl auf die naechste Zelle
ab2:            db      1                    ; Laufzeit: Spur 2 von ZT 0 := Spur 2 des Puffers
                211     a00                  ; AC := Adresse SPUF-00
                210     #0601                ; plus Spur 0 und Operationscode 601
                240     ab3                  ; Ausgabebefehl auf die naechste Zelle
ab3:            db      1                    ; Laufzeit: Spur 0 von ZT 0 := SPUF-00
                020     0                    ; Halt

n1:             kat5    abc                  ; Namenszelle (Eintrag ID 3): kat5 "abc" = 02122230000
n2:             kat5    hallo                ; Namenszelle (Eintrag ID 4): kat5 "hallo" = 03021343437
n3:             kat5    ab12z                ; Namenszelle (Eintrag ID 32): kat5 "ab12z" = 02122101152

; ---- UP pname: Programmname eintragen (Projektmakro PNAME). R1 = SPUF-PN, R2 = Namenszelle, R3 = SPUF-00
pname:          PNAME                        ; Unterprogramm (Makro)

; ---- Spurpuffer (je auf einer 040-Grenze)
                equ40   *                    ; SPUF-00 auf einer Spurgrenze
spuf00:         db      040                  ; SPUF-00: Spur 0 von ZT 0 (32 Zellen)
                equ40   *                    ; SPUF-PN auf einer Spurgrenze
spufpn:         db      0100                 ; SPUF-PN: 2 Spuren = 64 Zellen
schluss:        end

; Sollwerte von Hand hergeleitet (Zaehler 2, Trommel 0, Spur 127; Wort 2 vorbelegt mit z0 = 1 und Laenge 5252):
; kat5-Namen (Doku 3.3.15: Codes a = 021 ... z = 052, Ziffern 0 = 07 ... 9 = 020; Zeichen 1 bis 5 stehen in z3-z8, z9-z14, z15-z20, z21-z26, z27-z32, also je 2 Oktalziffern hinter der fuehrenden 0):
;   abc = 0 21 22 23 00 00 = 02122230000 (Gegenprobe der Doku); hallo: h = 021 + 7 = 030, a = 021, l = 021 + 11 = 034, l = 034, o = 021 + 14 = 037 -> 0 30 21 34 34 37 = 03021343437;
;   ab12z: a = 021, b = 022, 1 = 010, 2 = 011, z = 021 + 25 = 052 -> 0 21 22 10 11 52 = 02122101152.
; Aufruf 1 (Name n1): Z = 2, ID = 3, Eintrag ab Zelle 2 * 2 = 4 (Zellen 4 und 5). Naechste Spur: p = 128 * 0 + 127 + 1 = 128 = Trommel 1, Spur 0.
;   Wort 2 = Typ 10 (20000000000) + ID 3 * 2^21 (30000000) + p * 2^12 = 128 * 4096 = 2^19 (2000000) = 20032000000; dazu bleiben z0 (40000000000) und Laenge (5252) = 60032005252.
; Aufruf 2 (Name n2): Zaehler ist jetzt 3, ID 4, Eintrag ab Zelle 6 (Zellen 6 und 7); Zellen 18 und 19 sind unveraendert, also wieder Trommel 1, Spur 0.
;   Wort 2 = 20000000000 + 4 * 2^21 (40000000) + 2^19 (2000000) = 20042000000 (z0 = 0 und Laenge 0 aus 11a).
; Aufruf 3 (Name n3): Zaehler von Hand auf 31 gesetzt, ID 32, Eintrag ab Zelle 2 * 31 = 62 (Zellen 62 und 63 = Spur 2 des Puffers, Zellen 30 und 31). Wort 2 = 20000000000 + 32 * 2^21 (2^26 = 400000000) + 2^19 (2000000) = 20402000000.
; Zaehler nach den drei Aufrufen 32 = 040 oktal; Zellen 18 und 19 unveraendert (0 und 0177). Zelle 20 und Zelle 40 des Puffers sind durch 11a (zwei 441) wieder 0.
; ZT 0 (Spur 1 = ZT-Zellen 0040 bis 0077, Spur 2 = 0100 bis 0137, Spur 0 = 0000 bis 0037): Zelle c der Puffer-Spur 1 liegt auf 0040 + c, der Puffer-Spur 2 auf 0100 + (c - 32):
;   Zelle 4 auf 0044, Zelle 5 auf 0045, Zelle 6 auf 0046, Zelle 7 auf 0047, Zelle 61 auf 0135, Zelle 62 auf 0136, Zelle 63 auf 0137.
;#PRUEFE-START
; US=1
; ZT-Zellen-Pruefung:
; 0-0040: 00000000000   # Eintrag ID 1, Wort 1 (nie beschrieben)
; 0-0041: 00000000000   # Eintrag ID 1, Wort 2
; 0-0042: 00000000000   # Eintrag ID 2, Wort 1
; 0-0043: 00000000000   # Eintrag ID 2, Wort 2
; 0-0044: 02122230000   # Eintrag ID 3, Wort 1 = n1 = kat5 abc (Zelle 4)
; 0-0045: 60032005252   # Eintrag ID 3, Wort 2: Typ 10, ID 3, Trommel 1, Spur 0; z0 und Laenge erhalten (Zelle 5)
; 0-0046: 03021343437   # Eintrag ID 4, Wort 1 = n2 = kat5 hallo (Zelle 6)
; 0-0047: 20042000000   # Eintrag ID 4, Wort 2: Typ 10, ID 4, Trommel 1, Spur 0 (Zelle 7)
; 0-0050: 00000000000   # Zelle 8: nie beschrieben
; 0-0064: 00000000000   # Zelle 20 (Spur 1 des Puffers): Mist durch 11a geloescht
; 0-0110: 00000000000   # Zelle 40 (Spur 2 des Puffers, Zelle 8): Mist durch 11a geloescht
; 0-0135: 00000000000   # Eintrag ID 31, Wort 2 (Zelle 61): nie beschrieben
; 0-0136: 02122101152   # Eintrag ID 32, Wort 1 = n3 = kat5 ab12z (Zelle 62)
; 0-0137: 20402000000   # Eintrag ID 32, Wort 2: Typ 10, ID 32, Trommel 1, Spur 0 (Zelle 63)
; 0-0021: 00000000040   # SPUF-00 Zelle 17: Zaehler = 32
; 0-0022: 00000000000   # SPUF-00 Zelle 18: Trommel unveraendert
; 0-0023: 00000000177   # SPUF-00 Zelle 19: Spur unveraendert
;#PRUEFE-ENDE
