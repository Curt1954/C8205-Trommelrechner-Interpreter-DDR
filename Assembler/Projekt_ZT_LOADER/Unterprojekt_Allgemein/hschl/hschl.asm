; hschl.asm - ERZEUGT von gen/hschl_gen.py (Quelle gen/hschl_variante.py; nicht von Hand aendern). Test des Makros HSCHL (ZIL Element 15, Ablage als Typ 10). Variante: 17 Eingaben, 34 Worte, Trommeluebertrag
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (Tabellen und Spurpuffer legen equ100/equ40 selbst).
; Ablauf: K1 (Lochbandleser 1) anwaehlen, KBGB := 1, R1 = Spurpuffer Programmcode (spufpc), R2 = Trommel 0, R3 = Spur 127 (0177), UP hschl aufrufen, danach die Abweichung von R1 und R3 festhalten (dif1, dif3), Halt.
; Der Fehlerausgang des Makros (Parameter fe_lang) traegt die Fehlerart 2 (mehr als 4095 Sektoren) in die Zelle fehlart ein und haelt. Das UP eingabe (Makro TYP10EINGABE) liest die Eingaben, sein
;     Endeausgang ist die Marke hs_ende in HSCHL.
;   Der Streifen liegt in Leser 1 (Datei hschl.txt). Die ZT beginnen leer (#ZTROMMEL=LEER). KBGB steht vor dem Aufruf auf 1 und muss danach 1 sein (der Streifen kann Um. GB und Um. KB enthalten).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 hschl: Projektmakro HSCHL: 17 Eingaben (Typ 10), 34 Worte, zwei Spuren, Uebertrag Spur 127 -> Trommel 1 Spur 0, R1, R3 und KBGB unveraendert
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/hschl.txt

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

; Sollwerte von Hand hergeleitet (Python-Modell in gen/hschl_variante.py nach 7a; die ersten 9 Eingaben unten von Hand nachgerechnet). Ablage als Typ 10: je Eingabe 2 Zellen, Wort 1 = Datenwert (11
;     Oktalziffern), Wort 2 = Kennzeichen (Kz 1 in z21 bis z26, Kz 2 in z27 bis z32, je Eingabeadresse).
; Streifen hschl.txt (Leser 1) = 17 Eingaben, dann WRZL und /:
;   1  + 0 7 7 1 2 3 4 5 6 7 0 1 2 :   Kz + (20) und 0 (00): Wort 2 = 20 * 2^6 + 00 = 02000; 12 Ziffern, die letzten 11 bleiben: Wort 1 = 71234567012
;   2  + 0 1 2 3 :                    Wort 1 = 123, Wort 2 = 02000
;   3  2 .                            Kz 2 (02) und 0 ergaenzt: Wort 2 = 02 * 2^6 = 0200, Wort 1 = 0
;   4  2 Leertaste 1 a 8 WRZL 9 + 5 : Kz 2 (02) und 1 (01): Wort 2 = 0201; Leertaste, a, 8, WRZL, 9 und + im Ziffernteil werden uebergangen, Ziffer 5: Wort 1 = 5
;   5  Um. GB 3 3 .                    Um. GB wird nur nach KBGB gefuehrt (nicht gespeichert); Kz 3 und 3: Wort 2 = 03 * 2^6 + 03 = 0303, Wort 1 = 0
;   6  Um. KB 7 .                      ein einzelnes Kz 7 (07): Wort 2 = 07 * 2^6 = 0700, Wort 1 = 0
;   7  8 9 .                           8 (Eingabeadresse 010) und 9 (011) sind als Kz gueltig: Wort 2 = 010 * 2^6 + 011 = 01011, Wort 1 = 0
;   8  0 0 und elf Siebenen :          Wort 1 = 77777777777 (z0 gesetzt), Wort 2 = 0
;   9 bis 17: 3 4 k 7 k . mit k = 011 bis 021 (zweimal k in Oktalziffern): Kz 3 und 4: Wort 2 = 03 * 2^6 + 04 = 0304; Eingabe 9: Ziffern 1 1 7 1 1 = Wort 1 = 11711.
; 17 Eingaben = 34 Sektoren: die ersten 16 Eingaben (32 Worte) fuellen die erste Spur und gehen auf Trommel 0, Spur 127 = ZT-Zellen 127 * 32 = 4064 dez = 07740 bis 07777; die Zaehlung geht dann auf
;     Trommel 1, Spur 0 (Zellen 0000 bis 0037) ueber:
; dort liegt die 17. Eingabe (Worte 32 und 33). Die zweite Spur wird mit dem Puffer geschrieben, der vorher mit 441 geloescht wurde: Zellen 0002 bis 0037 sind 0. Sektoranzahl R2 = 34 = 042.
; R1 (Adresse spufpc), R3 (127) und KBGB (vor dem Aufruf 1, der Streifen enthaelt Um. GB und Um. KB) bleiben unveraendert.
;#PRUEFE-START
; US=1
; 0001: 00000000000   # dif1: R1 unveraendert
; 0002: 00000000000   # dif3: R3 unveraendert
; 0003: 00000000000   # fehlart: kein Fehler
; 7776: 00000000042   # R2: Sektoranzahl 34
; 7775: 00000000001   # KBGB unveraendert 1
; ZT-Zellen-Pruefung:
; 0-7740: 71234567012   # ZT 0 Spur 127: Wort 0
; 0-7741: 00000002000   # ZT 0 Spur 127: Wort 1
; 0-7742: 00000000123   # ZT 0 Spur 127: Wort 2
; 0-7743: 00000002000   # ZT 0 Spur 127: Wort 3
; 0-7744: 00000000000   # ZT 0 Spur 127: Wort 4
; 0-7745: 00000000200   # ZT 0 Spur 127: Wort 5
; 0-7746: 00000000005   # ZT 0 Spur 127: Wort 6
; 0-7747: 00000000201   # ZT 0 Spur 127: Wort 7
; 0-7750: 00000000000   # ZT 0 Spur 127: Wort 8
; 0-7751: 00000000303   # ZT 0 Spur 127: Wort 9
; 0-7752: 00000000000   # ZT 0 Spur 127: Wort 10
; 0-7753: 00000000700   # ZT 0 Spur 127: Wort 11
; 0-7754: 00000000000   # ZT 0 Spur 127: Wort 12
; 0-7755: 00000001011   # ZT 0 Spur 127: Wort 13
; 0-7756: 77777777777   # ZT 0 Spur 127: Wort 14
; 0-7757: 00000000000   # ZT 0 Spur 127: Wort 15
; 0-7760: 00000011711   # ZT 0 Spur 127: Wort 16
; 0-7761: 00000000304   # ZT 0 Spur 127: Wort 17
; 0-7762: 00000012712   # ZT 0 Spur 127: Wort 18
; 0-7763: 00000000304   # ZT 0 Spur 127: Wort 19
; 0-7764: 00000013713   # ZT 0 Spur 127: Wort 20
; 0-7765: 00000000304   # ZT 0 Spur 127: Wort 21
; 0-7766: 00000014714   # ZT 0 Spur 127: Wort 22
; 0-7767: 00000000304   # ZT 0 Spur 127: Wort 23
; 0-7770: 00000015715   # ZT 0 Spur 127: Wort 24
; 0-7771: 00000000304   # ZT 0 Spur 127: Wort 25
; 0-7772: 00000016716   # ZT 0 Spur 127: Wort 26
; 0-7773: 00000000304   # ZT 0 Spur 127: Wort 27
; 0-7774: 00000017717   # ZT 0 Spur 127: Wort 28
; 0-7775: 00000000304   # ZT 0 Spur 127: Wort 29
; 0-7776: 00000020720   # ZT 0 Spur 127: Wort 30
; 0-7777: 00000000304   # ZT 0 Spur 127: Wort 31
; 1-0000: 00000021721   # ZT 1 Spur 0 (Uebertrag der Trommel): Wort 32
; 1-0001: 00000000304   # ZT 1 Spur 0 (Uebertrag der Trommel): Wort 33
; 1-0002: 00000000000   # Rest der zweiten Spur: 0 (Puffer vorher geloescht)
; 1-0037: 00000000000   # letzte Zelle der zweiten Spur: 0
; 1-0040: 00000000000   # Spur 1 der Trommel 1 nicht beschrieben
; 0-7677: 00000000000   # Spur 126 der Trommel 0 (davor) nicht beschrieben
; 0-0000: 00000000000   # Spur 0 der Trommel 0 nicht beschrieben
;#PRUEFE-ENDE
