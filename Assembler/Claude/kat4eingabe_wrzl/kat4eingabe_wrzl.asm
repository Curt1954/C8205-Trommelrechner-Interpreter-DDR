; kat4eingabe_wrzl.asm - Hauptprogramm und Unterprogramm KAT4EINGABE (Zeicheneingabe ueber K0 = T-SW/SW in einen kat4-Text),
;                    danach Ausgabe des Eingegebenen mit dem Makro KAT4AUSGABE
;
; Hauptprogramm: verwaltet die KB/GB-Zustaende (kbein: SW-Eingabe, kbaus: Ausgabe; 0 = KB, 1 = GB; initial KB, Festlegung 030) und uebergibt den UP
;                die Adresse der jeweiligen Zelle in R3 (Register 7774) als Referenz; die UP ziehen den Zustand bei Um. GB / Um. KB nach.
;                Waehlt K0 (SW) zur Eingabe an, uebergibt dem UP in R1 (Register 7773) die Adresse des Bereichs (Adressfeld, wie bei
;                KAT4AUSGABE) und in R2 (Register 7776, laut BIS-Dokumentation) die hoechste Zeichenzahl (hier 8), ruft das UP auf,
;                schreibt eine Zeilenschaltung und gibt den Text mit KAT4AUSGABE auf K2 (Schreibwerk) wieder aus.
; UP kat4eingabe: Aufruf mit 025, Kanal K0 vorher angewaehlt. Jedes Eingabezeichen wird in sein kat4-Zeichen umgesetzt
;                (kat4-Zeichen = Ausgabeadresse / 8, erstes Zeichen im Wort rechts, 4 Zeichen je Wort, z0 am letzten Wort).
;                Die Worte werden ab der Adresse in R1 gespeichert. Die Eingabe endet
;                  - mit dem Zeichen WRZL (SatzMarke): es wird nicht gespeichert, das letzte Wort bekommt z0,
;                  - sobald R2 Zeichen angenommen sind (volle Zeichenzahl gilt als Eingabeende): das letzte Wort bekommt z0.
;                Zaehlt jedes gespeicherte kat4-Zeichen, auch die Umschaltzeichen Um. KB / Um. GB. Bereichsgroesse in Worten:
;                (R2 + 3) / 4. Mit WRZL nach genau 4, 8, ... Zeichen steht ein leeres Endwort (nur z0) hinter dem letzten vollen Wort.
;                R1 und R2 bleiben unveraendert. R2 muss mindestens 1 sein (bei 0 wird kein Zeichen gelesen: leerer Text, nur z0).
;                Rueckkehr: AC = Rueckkehrwort wird auf die Zelle rueck gesichert (am UP-Ende sequentiell erreicht, Festlegung 010).
;                Zerstoert werden die Zellen des UP (zeiger, wort, zaehl, m, sb) und die Arbeitsspur 7640 (Schieben).
; Eingabeauswertung: 010 ztab liest ein Zeichen und addiert die Zelle ztab ODER Eingabeadresse zum AC. Die Tabelle ztab enthaelt je Zeichen
;                das kat4-Zeichen schon um 24 Stellen nach links verschoben; der AC enthaelt vorher das um ein Zeichen (8 Stellen)
;                nach rechts geschobene Wort, so dass das neue Zeichen links einrueckt und das erste Zeichen nach 4 Zeichen rechts steht.
;                Zeichen mit Sprung-Umstellung (Leertaste, :, ., ,, -, Tab, Um. KB, Um. GB, ...) springen auf die Tabellenzelle und
;                werden von den Behandlern hNN ueber uebern angefuegt.
; Empfehlung (001): kleinste Startzelle 0000, groesste Startzelle 7200 (Laenge 0312 Zellen, Ende vor 7600), Ausrichtung auf eine
;                0100-Grenze wegen der Tabelle ztab (equ100). Testprogramm ab 0000.
;#DOK-0001 KAT4EINGABE: vorzeitiges Ende mit WRZL nach 5 Zeichen (h i Leertaste . Um. GB), Sprungzeichen, Ausgabe mit KAT4AUSGABE
;#SPEI-0001 0001-0005
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat4eingabe_wrzl.txt
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat4eingabe_wrzl
;#TASTENFOLGE H SW=1 G R
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat4eingabe_wrzl-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      2                    ; Zellen 0001 und 0002: Bereich fuer 8 Zeichen = 2 Worte
radr:           da      text                 ; Zelle 0003: Adresse des Bereichs (Adressfeld)
kbein:          dw      0                    ; Zelle 0004: KB/GB-Zustand der SW-Eingabe (0 = KB, 1 = GB), initial KB (Festlegung 030)
kbaus:          dw      0                    ; Zelle 0005: KB/GB-Zustand der Schreibwerk-Ausgabe, initial KB
rkbe:           da      kbein                ; Zelle 0006: Adresse der Eingabe-Zustandszelle (Adressfeld)
rkba:           da      kbaus                ; Zelle 0007: Adresse der Ausgabe-Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr                 ; AC := Adresse des Bereichs
                240     r1                   ; R1 := Adresse des Bereichs
                211     #8                   ; AC := hoechste Zeichenzahl
                240     r2                   ; R2 := 8
                211     rkbe                 ; AC := Adresse der Eingabe-Zustandszelle
                240     r3                   ; R3 := Adresse der Eingabe-Zustandszelle
                025     eingabe              ; Aufruf KAT4EINGABE, AC := Rueckkehrwort
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                WRZL                         ; Zeilenschaltung (waehlt danach K0 an)
                ANWAHL  K2                   ; Kanal 2 wieder anwaehlen
                211     rkba                 ; AC := Adresse der Ausgabe-Zustandszelle
                240     r3                   ; R3 := Adresse der Ausgabe-Zustandszelle
                025     ausgabe              ; Aufruf KAT4AUSGABE (R1 = Adresse des Textes bleibt vom UP unveraendert)
                WRZL                         ; Zeilenschaltung zum Schluss
                020     0                    ; Halt

; ---- UP KAT4EINGABE und KAT4AUSGABE als Makros (Makrodatei c82ass.makros)
eingabe:        KAT4EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat4-Text ab R1 ab (Tabelle ztab liegt im Makro)
ausgabe:        KAT4AUSGABE                  ; Unterprogramm: gibt den kat4-Text ab R1 aus
ende:           end

; Sollwerte von Hand hergeleitet (Kodetabelle 1, erstes Zeichen rechts, z0 = 040000000000):
; h = 070, i = 051, Leertaste = 032, Punkt = 073, Um. GB = 057 (WRZL wird nicht gespeichert).
; Wort 1 = 073 032 051 070 (je 8 Bit, erstes Zeichen rechts) = 07306424470; Wort 2 = z0 + 057 = 40000000057 (3 Stellen fehlen, nach rechts ausgerichtet).
;
; Zustaende: kbein/kbaus beginnen mit 0 (KB). Die Eingabe enthaelt Um. GB (Zeichen 5) -> kbein = 1, die Ausgabe des Textes gibt Um. GB aus -> kbaus = 1.
; Halt in 0031 (4 Zellen mehr fuer die Zustandszellen, 4 mehr fuer R3), BZ = 0032.
;#PRUEFE-START
; BZ=0032
; 0001: 07306424470   # Wort 1: h i Leertaste .
; 0002: 40000000057   # Wort 2: Um. GB mit z0
; 0004: 00000000001   # kbein: Zustand der Eingabe nach dem UP
; 0005: 00000000001   # kbaus: Zustand der Ausgabe nach dem UP
; 7773: 00000001000   # R1 unveraendert
; 7774: 00000005000   # R3: zuletzt die Adresse der Ausgabe-Zustandszelle (0005 * 01000)
; 7776: 00000000010   # R2 unveraendert
;#PRUEFE-ENDE
