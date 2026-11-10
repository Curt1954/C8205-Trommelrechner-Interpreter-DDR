; hschl_zulang.asm - ERZEUGT von gen/hschl_zulang_gen.py (Quelle gen/hschl_variante.py; nicht von Hand aendern). Test des Makros HSCHL (ZIL Element 15, Ablage als Typ 10). Variante: 2048 Eingaben
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (Tabellen und Spurpuffer legen equ100/equ40 selbst).
; Ablauf: K1 (Lochbandleser 1) anwaehlen, KBGB := 1, R1 = Spurpuffer Programmcode (spufpc), R2 = Trommel 0, R3 = Spur 127 (0177), UP hschl aufrufen, danach die Abweichung von R1 und R3 festhalten (dif1, dif3), Halt.
; Der Fehlerausgang des Makros (Parameter fe_lang) traegt die Fehlerart 2 (mehr als 4095 Sektoren) in die Zelle fehlart ein und haelt. Das UP eingabe (Makro TYP10EINGABE) liest die Eingaben, sein
;     Endeausgang ist die Marke hs_ende in HSCHL.
;   Der Streifen liegt in Leser 1 (Datei hschl_zulang.txt). Die ZT beginnen leer (#ZTROMMEL=LEER). KBGB steht vor dem Aufruf auf 1 und muss danach 1 sein (der Streifen kann Um. GB und Um. KB enthalten).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 hschl_zulang: Projektmakro HSCHL: 2048 Eingaben = 4096 Sektoren (mehr als 4095): Fehlerausgang fe_lang nach 127 geschriebenen Spuren, Halt, keine Rueckgabe
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/hschl_zulang.txt

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

; Sollwerte von Hand hergeleitet: Streifen hschl_zulang.txt = 2048 Eingaben 1 2 <k oktal> . (k = 1 bis 2048) und /. Eingabe k: Kz 1 und 2: Wort 2 = 01 * 2^6 + 02 = 0102, Wort 1 = k (die Ziffern von k
;     oktal als Oktalziffern gelesen ergeben k).
; Nach der 2048. Eingabe zaehlt der Sektorzaehler 4096: 4096 - 4096 >= 0 fuehrt in fe_lang (Parameter 1), fehlart := 2, Halt, keine Rueckgabe (R2 bleibt 0).
; Geschrieben sind bis dahin 127 volle Spuren (127 * 16 = 2032 Eingaben): die Zielspuren zaehlen von p = 127 (Trommel 0, Spur 127) bis p = 253 (Trommel 1, Spur 125): Trommel 0 Spur 127 = Zellen 07740
;     bis 07777, Trommel 1 Spur 0 bis 125 = Zellen 0000 bis 07677.
; Erste Spur: Zelle 0 = Wort 1 von Eingabe 1 = 1, Zelle 1 = 0102, Zelle 30 = Wort 1 von Eingabe 16 = 16 = 020, Zelle 31 = 0102. Letzte geschriebene Spur (Trommel 1 Spur 125 = Zellen 07640 bis 07677):
;     Eingaben 2017 bis 2032, Zelle 0 = 2017 = 03741 (3 * 512 + 7 * 64 + 4 * 8 + 1), Zelle 30 = 2032 = 03760, Zelle 31 = 0102.
; Die 128. Spur (p = 254 = Trommel 1, Spur 126 = Zellen 07700 bis 07777) wird nicht mehr geschrieben: die Eingaben 2033 bis 2048 stehen nur im Puffer.
;#PRUEFE-START
; US=1
; 0001: 00000000000   # dif1: nie berechnet
; 0002: 00000000000   # dif3: nie berechnet
; 0003: 00000000002   # fehlart: 2 = mehr als 4095 Sektoren
; 7776: 00000000000   # R2: unveraendert (kehrt nicht zurueck)
; ZT-Zellen-Pruefung:
; 0-7677: 00000000000   # Spur 126 der Trommel 0 (davor): nicht beschrieben
; 0-7740: 00000000001   # erste geschriebene Spur: Zelle 0 (Wort 1 der Eingabe 1)
; 0-7741: 00000000102   # Zelle 1 (Wort 2 der Eingabe 1)
; 0-7776: 00000000020   # Zelle 30 (Wort 1 der Eingabe 16)
; 0-7777: 00000000102   # letzte Zelle der ersten Spur
; 1-0000: 00000000021   # Trommel 1 Spur 0 (Uebertrag): Wort 1 der Eingabe 17
; 1-7640: 00000003741   # Trommel 1 Spur 125 (letzte geschriebene Spur): Zelle 0 (Eingabe 2017)
; 1-7676: 00000003760   # Trommel 1 Spur 125: Zelle 30 (Eingabe 2032)
; 1-7677: 00000000102   # Trommel 1 Spur 125: letzte Zelle
; 1-7700: 00000000000   # Trommel 1 Spur 126: nicht mehr geschrieben
; 1-7777: 00000000000   # Trommel 1 Spur 127: nicht geschrieben
;#PRUEFE-ENDE
