; hschl_rand.asm - ERZEUGT von gen/hschl_rand_gen.py (Quelle gen/hschl_variante.py; nicht von Hand aendern). Test des Makros HSCHL (ZIL Element 15, Ablage als Typ 10). Variante: / bricht eine Eingabe ab
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (Tabellen und Spurpuffer legen equ100/equ40 selbst).
; Ablauf: K1 (Lochbandleser 1) anwaehlen, KBGB := 1, R1 = Spurpuffer Programmcode (spufpc), R2 = Trommel 0, R3 = Spur 127 (0177), UP hschl aufrufen, danach die Abweichung von R1 und R3 festhalten (dif1, dif3), Halt.
; Der Fehlerausgang des Makros (Parameter fe_lang) traegt die Fehlerart 2 (mehr als 4095 Sektoren) in die Zelle fehlart ein und haelt. Das UP eingabe (Makro TYP10EINGABE) liest die Eingaben, sein
;     Endeausgang ist die Marke hs_ende in HSCHL.
;   Der Streifen liegt in Leser 1 (Datei hschl_rand.txt). Die ZT beginnen leer (#ZTROMMEL=LEER). KBGB steht vor dem Aufruf auf 1 und muss danach 1 sein (der Streifen kann Um. GB und Um. KB enthalten).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 hschl_rand: Projektmakro HSCHL: 16 Eingaben, die 17. von / abgebrochen: verworfen, eine Spur, R2 = 32
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/hschl_rand.txt

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

; Sollwerte von Hand hergeleitet: Streifen hschl_rand.txt = die ersten 16 Eingaben von hschl.txt, dann 2 1 5 und / (eine 17. Eingabe ohne Punkt, vom Streifenende abgebrochen).
; Die begonnene 17. Eingabe wird verworfen (nichts in den Puffer geschrieben, nicht gezaehlt): Sektoranzahl R2 = 32 = 040, genau eine Spur (ZT 0 Spur 127), keine zweite Spur; ZT 1 Spur 0 bleibt 0. Inhalt der Spur wie bei hschl_voll.
;#PRUEFE-START
; US=1
; 0001: 00000000000   # dif1: R1 unveraendert
; 0002: 00000000000   # dif3: R3 unveraendert
; 0003: 00000000000   # fehlart: kein Fehler
; 7776: 00000000040   # R2: Sektoranzahl 32 (die 17. Eingabe zaehlt nicht)
; 7775: 00000000001   # KBGB unveraendert 1
; ZT-Zellen-Pruefung:
; 0-7740: 71234567012   # Wort 0
; 0-7777: 00000000304   # Wort 31
; 1-0000: 00000000000   # keine zweite Spur: die abgebrochene Eingabe wird verworfen
; 1-0001: 00000000000   # Zelle 1 der zweiten Spur: 0
;#PRUEFE-ENDE
