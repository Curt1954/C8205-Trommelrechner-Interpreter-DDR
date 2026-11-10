; hschl_ziffer.asm - ERZEUGT von gen/hschl_ziffer_gen.py (Quelle gen/hschl_variante.py; nicht von Hand aendern). Test des Makros HSCHL (ZIL Element 15, Ablage als Typ 10). Variante: Ziffern 8 und 9 kein Fehler
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (Tabellen und Spurpuffer legen equ100/equ40 selbst).
; Ablauf: K1 (Lochbandleser 1) anwaehlen, KBGB := 1, R1 = Spurpuffer Programmcode (spufpc), R2 = Trommel 0, R3 = Spur 127 (0177), UP hschl aufrufen, danach die Abweichung von R1 und R3 festhalten (dif1, dif3), Halt.
; Der Fehlerausgang des Makros (Parameter fe_lang) traegt die Fehlerart 2 (mehr als 4095 Sektoren) in die Zelle fehlart ein und haelt. Das UP eingabe (Makro TYP10EINGABE) liest die Eingaben, sein
;     Endeausgang ist die Marke hs_ende in HSCHL.
;   Der Streifen liegt in Leser 1 (Datei hschl_ziffer.txt). Die ZT beginnen leer (#ZTROMMEL=LEER). KBGB steht vor dem Aufruf auf 1 und muss danach 1 sein (der Streifen kann Um. GB und Um. KB enthalten).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 hschl_ziffer: Projektmakro HSCHL: Ziffern 8 und 9 als Kennzeichen gueltig, im Ziffernteil uebergangen, kein Fehler
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/hschl_ziffer.txt

r1:             abs     07773                ; Register 1: Adresse des Spurpuffers Programmcode (Adressfeld)
r2:             abs     07776                ; Register 2: Trommelnummer, nach dem Lauf Sektoranzahl
r3:             abs     07774                ; Register 3: Spurnummer der ersten Zielspur
kbgb:           abs     07775                ; KBGB, globale KB/GB-Zelle

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
dif1:           dw      0                    ; Zelle 0001: R1 - apc nach dem Aufruf (0, wenn R1 unveraendert)
dif3:           dw      0                    ; Zelle 0002: R3 - 0177 nach dem Aufruf (0, wenn R3 unveraendert)
fehlart:        dw      0                    ; Zelle 0003: Fehlerart (0 kein Fehler, 2 zu lang), vom Fehlerausgang gesetzt
apc:            da      spufpc               ; Zelle 0004: Adresse des Spurpuffers Programmcode (Adressfeld)

haupt:          ANWAHL  K1                   ; Lochbandleser 1 anwaehlen (Kanal K1)
                211     #1                   ; AC := 1
                240     kbgb                 ; KBGB := 1 (GB); der Lauf darf es nicht aendern
                211     apc                  ; AC := Adresse des Spurpuffers
                240     r1                   ; R1 := Spurpuffer Programmcode
                241     r2                   ; R2 := 0 (Trommel 0), AC := 0
                211     #0177                ; AC := 127
                240     r3                   ; R3 := Spur 127 der Trommel 0 (die zweite Spur liegt dann auf Trommel 1, Spur 0)
                025     hschl                ; UP hschl: Streifen lesen, auf die ZT schreiben, R2 := Sektoranzahl
                211     r1                   ; AC := R1
                220     apc                  ; minus Soll: 0, wenn R1 unveraendert
                240     dif1                 ; dif1 := Abweichung von R1
                211     r3                   ; AC := R3
                220     #0177                ; minus Soll: 0, wenn R3 unveraendert
                240     dif3                 ; dif3 := Abweichung von R3
                020     0                    ; Halt (normales Ende)
fe_lang:        211     #2                   ; Fehlerausgang zu lang: AC := 2
                240     fehlart              ; fehlart := 2
                020     0                    ; Halt (Fehler zu lang)

; ---- UP hschl: Hauptschleife Ls nach ZT (Projektmakro HSCHL). R1 = Spurpuffer Programmcode, R2 = Trommel, R3 = Spur der ersten Zielspur; Fehlerausgang fe_lang, UP eingabe, Streifenende hs_ende
hschl:          HSCHL   fe_lang eingabe ende ; Unterprogramm (Makro); setzt die Marke hs_ende

; ---- UP eingabe: eine Typ-10-Eingabe lesen (Projektmakro TYP10EINGABE), Endeausgang hs_ende
eingabe:        TYP10EINGABE hs_ende         ; Unterprogramm (Makro)

; ---- Spurpuffer Programmcode (auf einer 040-Grenze, 1 Spur = 32 Zellen)
                equ40   *                    ; Spurgrenze
spufpc:         db      040                  ; Spurpuffer Programmcode: 32 Zellen
schluss:        end

; Sollwerte von Hand hergeleitet: Streifen hschl_ziffer.txt = 3 Eingaben und /. Der frueher gemeldete Fehler "Ziffer 8 oder 9" gibt es nicht mehr (Typ 10, 7a).
;   1  8 9 .              8 und 9 als Kennzeichen: Wort 2 = 010 * 2^6 + 011 = 01011, Wort 1 = 0
;   2  0 8 9 8 Leertaste 9 7 .   Kz 0 (00) und 8 (010): Wort 2 = 00 * 2^6 + 010 = 010; im Ziffernteil werden 9, 8, Leertaste und 9 uebergangen, Ziffer 7: Wort 1 = 7
;   3  + 8 .              Kz + (020) und 8 (010): Wort 2 = 020 * 2^6 + 010 = 02010, Wort 1 = 0
; Sektoranzahl R2 = 6, kein Fehler (fehlart 0), eine Spur auf Trommel 0 Spur 127 (Zellen 07740 bis 07745), der Rest 0.
;#PRUEFE-START
; US=1
; 0001: 00000000000   # dif1: R1 unveraendert
; 0002: 00000000000   # dif3: R3 unveraendert
; 0003: 00000000000   # fehlart: kein Fehler (8 und 9 sind keine Fehler mehr)
; 7776: 00000000006   # R2: Sektoranzahl 6
; 7775: 00000000001   # KBGB unveraendert 1
; ZT-Zellen-Pruefung:
; 0-7740: 00000000000   # ZT 0 Spur 127: Wort 0
; 0-7741: 00000001011   # ZT 0 Spur 127: Wort 1
; 0-7742: 00000000007   # ZT 0 Spur 127: Wort 2
; 0-7743: 00000000010   # ZT 0 Spur 127: Wort 3
; 0-7744: 00000000000   # ZT 0 Spur 127: Wort 4
; 0-7745: 00000002010   # ZT 0 Spur 127: Wort 5
; 0-7746: 00000000000   # Rest der Spur: 0
; 0-7777: 00000000000   # letzte Zelle der Spur: 0
; 1-0000: 00000000000   # keine zweite Spur
;#PRUEFE-ENDE
