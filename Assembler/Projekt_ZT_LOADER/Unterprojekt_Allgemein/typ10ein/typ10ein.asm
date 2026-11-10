; typ10ein.asm - ERZEUGT von gen/typ10ein_gen.py (nicht von Hand aendern). Test des Projektmakros TYP10EINGABE (ZT-Repository_Aufgabenstellung 7a): liest 9 Typ-10-Eingaben vom Lochbandleser 1 (K1).
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (die Tabelle legt equ100 selbst).
; Ablauf: KBGB := 0, K1 anwaehlen; je Eingabe R1 := Adresse des 2-Zellen-Bereichs, UP eingabe aufrufen, KBGB danach in die Zelle kb+i merken; am Ende R1 pruefen (dif1), Halt.
; Der Streifen (Test-virtuelleGeraete/Leser1/typ10ein.txt) enthaelt die Eingaben nacheinander, danach eine Zeile mit ungerader Lochzahl.
;#MACRODATEI1=../../macro_zt_loader.macro
;#DOK-0001 typ10ein: Projektmakro TYP10EINGABE: 9 Eingaben vom Leser 1, Wort 1 und Wort 2 je Eingabe, KBGB nach jeder Eingabe, R1 unveraendert
;#SPEI-0001 0001-0034
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/typ10ein.txt

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
kbgb:           abs     07775                ; globale KB/GB-Zelle des Projekts (0 = KB, 1 = GB)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
erg:            db      18                  ; Zellen 0001 bis 0022: Ergebnisbereiche, je Eingabe 2 Zellen (Wort 1, Wort 2)
kb:             db      9                   ; Zellen 0023 bis 0033: KBGB nach jeder Eingabe
dif1:           db      1                    ; Zelle 0034: R1 - Soll nach dem letzten Aufruf (0, wenn R1 unveraendert)

haupt:          241     kbgb                 ; KBGB := 0 (Anfangszustand KB), AC := 0
                ANWAHL  K1                   ; Lochbandleser 1 anwaehlen (Kanal K1)
                211     a0                   ; AC := Adresse des Bereichs der Eingabe 1
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 1 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+0                 ; Zelle kb+0 := KBGB
                211     a1                   ; AC := Adresse des Bereichs der Eingabe 2
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 2 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+1                 ; Zelle kb+1 := KBGB
                211     a2                   ; AC := Adresse des Bereichs der Eingabe 3
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 3 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+2                 ; Zelle kb+2 := KBGB
                211     a3                   ; AC := Adresse des Bereichs der Eingabe 4
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 4 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+3                 ; Zelle kb+3 := KBGB
                211     a4                   ; AC := Adresse des Bereichs der Eingabe 5
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 5 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+4                 ; Zelle kb+4 := KBGB
                211     a5                   ; AC := Adresse des Bereichs der Eingabe 6
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 6 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+5                 ; Zelle kb+5 := KBGB
                211     a6                   ; AC := Adresse des Bereichs der Eingabe 7
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 7 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+6                 ; Zelle kb+6 := KBGB
                211     a7                   ; AC := Adresse des Bereichs der Eingabe 8
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 8 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+7                 ; Zelle kb+7 := KBGB
                211     a8                   ; AC := Adresse des Bereichs der Eingabe 9
                240     r1                   ; R1 := Bereich
                025     eingabe              ; UP eingabe: Eingabe 9 lesen
                211     kbgb                 ; AC := KBGB nach der Eingabe
                240     kb+8                 ; Zelle kb+8 := KBGB
                211     r1                   ; AC := R1
                220     a8                   ; minus Soll (Bereich der letzten Eingabe): 0, wenn R1 unveraendert
                240     dif1                 ; dif1 := Abweichung
                020     0                    ; Halt (normales Ende)
a0:             da      erg+0                ; Adresse des Bereichs der Eingabe 1 (Adressfeld)
a1:             da      erg+2                ; Adresse des Bereichs der Eingabe 2 (Adressfeld)
a2:             da      erg+4                ; Adresse des Bereichs der Eingabe 3 (Adressfeld)
a3:             da      erg+6                ; Adresse des Bereichs der Eingabe 4 (Adressfeld)
a4:             da      erg+8                ; Adresse des Bereichs der Eingabe 5 (Adressfeld)
a5:             da      erg+10                ; Adresse des Bereichs der Eingabe 6 (Adressfeld)
a6:             da      erg+12                ; Adresse des Bereichs der Eingabe 7 (Adressfeld)
a7:             da      erg+14                ; Adresse des Bereichs der Eingabe 8 (Adressfeld)
a8:             da      erg+16                ; Adresse des Bereichs der Eingabe 9 (Adressfeld)

; ---- UP eingabe: Projektmakro TYP10EINGABE. R1 = Bereich (2 Zellen), KBGB global
eingabe:        TYP10EINGABE                 ; Unterprogramm (Makro)
schluss:        end

; Sollwerte aus dem unabhaengigen Python-Modell (gen/typ10ein_gen.py) der Regeln von 7a; Beispiele 1 bis 3 aus 7a von Hand: (1) 71234567012 / 00000002000, (2) 00000000123 / 00000002000, (3) 0 / 00000000200.
; Eingabe 1: + 0 7 7 1 2 3 4 5 6 7 0 1 2 :  (12 Ziffern: die letzten 11 bleiben (Beispiel 1 aus 7a))
; Eingabe 2: + 0 1 2 3 :  (Vornullen (Beispiel 2 aus 7a))
; Eingabe 3: 2 .  (nur ein Kennzeichen (Beispiel 3 aus 7a))
; Eingabe 4: WRZL _ .  (Punkt sofort: nichts gelesen, alles 0; WRZL und Leertaste werden uebergangen)
; Eingabe 5: _ 1 WRZL 2 8 9 + 3 a _ 4 5 .  (Uebergehen von Leertaste, WRZL, Buchstabe, 8, 9 und + im Ziffernteil)
; Eingabe 6: GB 3 4 .  (Um. GB wird nachgefuehrt, Kennzeichen 3 und 4, keine Ziffern)
; Eingabe 7: 5 6 7 KB 1 :  (Um. KB wird nachgefuehrt, Ziffern 7 und 1)
; Eingabe 8: 0 0 7 7 7 7 7 7 7 7 7 7 7 :  (11 Ziffern 7: Wort 1 mit gesetztem Bit z0)
; Eingabe 9: + .  (ein Kennzeichen +, Eingabeadresse 20)
;#PRUEFE-START
; US=1
; 0001: 71234567012   # Eingabe 1 Wort 1
; 0002: 00000002000   # Eingabe 1 Wort 2
; 0003: 00000000123   # Eingabe 2 Wort 1
; 0004: 00000002000   # Eingabe 2 Wort 2
; 0005: 00000000000   # Eingabe 3 Wort 1
; 0006: 00000000200   # Eingabe 3 Wort 2
; 0007: 00000000000   # Eingabe 4 Wort 1
; 0010: 00000000000   # Eingabe 4 Wort 2
; 0011: 00000000345   # Eingabe 5 Wort 1
; 0012: 00000000102   # Eingabe 5 Wort 2
; 0013: 00000000000   # Eingabe 6 Wort 1
; 0014: 00000000304   # Eingabe 6 Wort 2
; 0015: 00000000071   # Eingabe 7 Wort 1
; 0016: 00000000506   # Eingabe 7 Wort 2
; 0017: 77777777777   # Eingabe 8 Wort 1
; 0020: 00000000000   # Eingabe 8 Wort 2
; 0021: 00000000000   # Eingabe 9 Wort 1
; 0022: 00000002000   # Eingabe 9 Wort 2
; 0023: 00000000000   # KBGB nach Eingabe 1
; 0024: 00000000000   # KBGB nach Eingabe 2
; 0025: 00000000000   # KBGB nach Eingabe 3
; 0026: 00000000000   # KBGB nach Eingabe 4
; 0027: 00000000000   # KBGB nach Eingabe 5
; 0030: 00000000001   # KBGB nach Eingabe 6
; 0031: 00000000000   # KBGB nach Eingabe 7
; 0032: 00000000000   # KBGB nach Eingabe 8
; 0033: 00000000000   # KBGB nach Eingabe 9
; 0034: 00000000000   # dif1: R1 unveraendert
; 7775: 00000000000   # KBGB am Ende
;#PRUEFE-ENDE
