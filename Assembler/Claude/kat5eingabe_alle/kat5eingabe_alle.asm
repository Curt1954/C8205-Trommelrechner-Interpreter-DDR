; kat5eingabe_alle.asm - KAT5EINGABE: alle 45 kat5-Zeichen ueber ihre Tasten, dazwischen Tasten ohne kat5-Zeichen (werden ueberlesen)
;   Eingabedatei: WR a b c d e / f g h i j % k ... z 0 ... 9 ZR . , - + = Um. GB Um. KB : mit eingestreuten Tasten WR, /, %, BM, IS, `, TAB
;   Neun Aufrufe in einer Schleife (ein Wort je Aufruf, R1 um 01000 weiter): jedes Wort endet nach 5 Zeichen, eine Taste ohne kat5-Zeichen hinter dem 5. Zeichen
;   liest erst der naechste Aufruf (und ueberliest sie). Das 9. Wort endet mit dem Doppelpunkt als 5. Zeichen (der Doppelpunkt beendet nicht, er ist ein Zeichen).
;#DOK-0001 KAT5EINGABE: alle kat5-Zeichen, Tasten ohne kat5-Zeichen werden ueberlesen, neun Aufrufe in einer Schleife
;#SPEI-0001 0001-0016
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat5eingabe_alle.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      10                   ; Zellen 0001 bis 0012: Bereich fuer 10 Worte (das 10. bleibt unberuehrt)
kbein:          dw      0                    ; Zelle 0013: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr:           da      text                 ; Zelle 0014: Adresse des ersten Wortes (Adressfeld)
rkbe:           da      kbein                ; Zelle 0015: Adresse der Zustandszelle (Adressfeld)
zaehl:          dw      0                    ; Zelle 0016: Schleifenzaehler (noch einzulesende Worte minus 1)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr                 ; AC := Adresse des ersten Wortes
                240     r1                   ; R1 := Adresse des ersten Wortes
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                211     #8                   ; AC := 8 (dezimal: 9 Worte minus 1)
                240     zaehl                ; zaehl := 8
schl:           025     eingabe              ; Aufruf KAT5EINGABE: ein Wort ab R1
                211     r1                   ; AC := Adresse des gelesenen Wortes
                210     #01000               ; plus eine Adresseinheit: naechstes Wort
                240     r1                   ; R1 := Adresse des naechsten Wortes
                211     zaehl                ; AC := zaehl
                220     #1                   ; AC := zaehl - 1
                240     zaehl                ; zaehl := zaehl - 1
                050     schl                 ; zaehl >= 0: naechstes Wort
                020     0                    ; Halt

; ---- UP KAT5EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT5EINGABE                  ; Unterprogramm: liest ein Wort ueber K0 und legt es auf R1 ab
                end

; Sollwerte von Hand hergeleitet. kat5-Codes nach Doku 3.3.15: Leertaste 01, Komma 02, Minus 03, Punkt 04, + und = 05, Doppelpunkt 06, 0 bis 9 = 07 bis 020,
; a bis z = 021 bis 052, Um. KB 054, Um. GB 055. Die Tasten WR, /, %, BM, IS, ` und TAB werden ueberlesen. Die 45 Zeichen belegen 9 Worte zu je 5 Zeichen
; (erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0, kein Endekennzeichen):
; Wort 1 a b c d e  = 02122232425   Wort 2 f g h i j  = 02627303132   Wort 3 k l m n o  = 03334353637   Wort 4 p q r s t  = 04041424344
; Wort 5 u v w x y  = 04546475051   Wort 6 z 0 1 2 3  = 05207101112   Wort 7 4 5 6 7 8  = 01314151617   Wort 8 9 ZR . , -  = 02001040203
; Wort 9 + = Um.GB Um.KB : = 05 05 55 54 06 = 00505555406. Zustand: zuletzt Um. KB -> kbein = 0.
; Zellen: text 0001 bis 0012, kbein 0013, radr 0014, rkbe 0015, zaehl 0016, Hauptprogramm 0017 bis 0036 (Halt) -> BZ = 0037.
; Schleife: zaehl 8 vor dem ersten Aufruf, nach dem 9. Aufruf -1 -> AC = -1 = 77777777777, zaehl = 77777777777.
; R1 = nach dem 9. Aufruf um eine Adresseinheit hinter dem 9. Wort = 0012 * 01000 = 012000; R3 = 0013 * 01000 = 013000.
;#PRUEFE-START
; BZ=0037 AC=77777777777
; 0001: 02122232425   # Wort 1: a b c d e
; 0002: 02627303132   # Wort 2: f g h i j
; 0003: 03334353637   # Wort 3: k l m n o
; 0004: 04041424344   # Wort 4: p q r s t
; 0005: 04546475051   # Wort 5: u v w x y
; 0006: 05207101112   # Wort 6: z 0 1 2 3
; 0007: 01314151617   # Wort 7: 4 5 6 7 8
; 0010: 02001040203   # Wort 8: 9 ZR . , -
; 0011: 00505555406   # Wort 9: + = Um. GB Um. KB :
; 0012: 00000000000   # Wort 10 unberuehrt
; 0013: 00000000000   # kbein: zuletzt Um. KB
; 0016: 77777777777   # zaehl: -1 nach 9 Durchlaeufen
; 7773: 00000012000   # R1 = Adresse hinter dem 9. Wort
; 7774: 00000013000   # R3 unveraendert
;#PRUEFE-ENDE
