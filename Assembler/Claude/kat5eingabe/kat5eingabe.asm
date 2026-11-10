; kat5eingabe.asm - Hauptprogramm und Makro KAT5EINGABE / Unterprogramm (Zeicheneingabe ueber K0 = T-SW/SW in kat5-Worte)
;
; Hauptprogramm: verwaltet den KB/GB-Zustand der Eingabe (kbein: 0 = KB, 1 = GB; initial KB, Festlegung 030) und uebergibt dem UP die Adresse
;                der Zelle in R3 (Register 7774) als Referenz; das UP zieht den Zustand bei Um. GB / Um. KB nach. Waehlt K0 zur Eingabe an,
;                uebergibt dem UP in R1 (Register 7773) die Adresse des kat5-Wortes (Adressfeld) und ruft das UP auf. R2 wird nicht mehr benutzt.
; UP kat5eingabe: Aufruf mit 025, Kanal K0 vorher angewaehlt. Jeder Aufruf liest genau ein Wort. Jedes Eingabezeichen wird in seinen kat5-Code umgesetzt
;                (kat5: 6 Bit je Zeichen, 5 Zeichen je Wort, erstes Zeichen links in z3 bis z8, Fuellung 00 rechts, kein z0; Doku 3.3.15). Das Wort wird auf die Adresse
;                in R1 gespeichert. Die Eingabe endet
;                  - sobald 5 Zeichen angenommen sind,
;                  - mit dem Zeichen WRZL (nicht gespeichert; die Zeichen stehen links, rechts mit 00 aufgefuellt).
;                Der Doppelpunkt ist ein gewoehnliches Zeichen (Code 06) und beendet nicht. Tasten ohne kat5-Zeichen werden ueberlesen.
;                Hier zwei Aufrufe fuer "hallo welt" (R1 danach um 01000 weiter).
; Empfehlung (001): kleinste Startzelle 0000, Ende vor 7600 (Arbeitsspur). Das Makro KAT5EINGABE belegt Zellen bis zur 0100-Grenze seiner Tabelle.
;#DOK-0001 KAT5EINGABE: Eingabe "hallo welt" ueber K0 (zwei Aufrufe, je ein volles Wort mit 5 Zeichen)
;#SPEI-0001 0001-0003
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat5eingabe_dp.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      2                    ; Zellen 0001 und 0002: zwei Worte fuer "hallo" und " welt"
kbein:          dw      0                    ; Zelle 0003: KB/GB-Zustand der Eingabe (0 = KB, 1 = GB), initial KB (Festlegung 030)
radr:           da      text                 ; Zelle 0004: Adresse des ersten Wortes (Adressfeld)
rkbe:           da      kbein                ; Zelle 0005: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr                 ; AC := Adresse des ersten Wortes
                240     r1                   ; R1 := Adresse des ersten Wortes
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                025     eingabe              ; Aufruf 1 KAT5EINGABE: h a l l o, Wort voll
                211     r1                   ; AC := Adresse des ersten Wortes
                210     #01000               ; plus eine Adresseinheit: zweites Wort
                240     r1                   ; R1 := Adresse des zweiten Wortes
                025     eingabe              ; Aufruf 2 KAT5EINGABE: ZR w e l t, Wort voll
                020     0                    ; Halt

; ---- UP KAT5EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT5EINGABE                  ; Unterprogramm: liest ein Wort ueber K0 und legt es auf R1 ab (Tabelle ztab liegt im Makro)
                end

; Sollwerte von Hand hergeleitet (kat5-Codes nach Doku 3.3.15: a = 021, e = 025, h = 030, l = 034, o = 037, t = 044, w = 047, Leertaste = 01;
; erstes Zeichen links, 2 Oktalziffern je Zeichen, z0 bis z2 = 0). Eingabe: h a l l o ZR w e l t (zehn Zeichen, ZR = Leertaste), mehr steht nicht in der Datei.
; Wort 1 (h a l l o)  : h 30, a 21, l 34, l 34, o 37     -> 0 30 21 34 34 37 = 03021343437
; Wort 2 (ZR w e l t) : Leertaste 01, w 47, e 25, l 34, t 44 -> 0 01 47 25 34 44 = 00147253444
; Beide Worte sind nach 5 Zeichen voll, das UP liest nie ueber das Dateiende hinaus. Zustandszelle kbein bleibt 0.
; Zellen: text 0001/0002, kbein 0003, radr 0004, rkbe 0005, Hauptprogramm 0006 bis 0020 (Halt) -> BZ = 0021.
; R1 = Adresse des zweiten Wortes = 0002 * 01000 = 02000, R3 = 0003 * 01000 = 03000. AC = zuletzt gespeichertes Wort = 00147253444.
;#PRUEFE-START
; BZ=0021 AC=00147253444
; 0001: 03021343437   # Wort 1: h a l l o
; 0002: 00147253444   # Wort 2: ZR w e l t
; 0003: 00000000000   # kbein: Zustand der Eingabe nach dem UP
; 7773: 00000002000   # R1 = Adresse des zweiten Wortes
; 7774: 00000003000   # R3 unveraendert
;#PRUEFE-ENDE
