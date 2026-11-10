; kat6eingabe.asm - Hauptprogramm und Makro KAT6EINGABE / Unterprogramm (Zeicheneingabe ueber K0 = T-SW/SW in einen kat6-Text)
;
; Hauptprogramm: verwaltet den KB/GB-Zustand der Eingabe (kbein: 0 = KB, 1 = GB; initial KB, Festlegung 030) und uebergibt dem UP die Adresse
;                der Zelle in R3 (Register 7774) als Referenz; das UP zieht den Zustand bei Um. GB / Um. KB nach. Waehlt K0 zur Eingabe an,
;                uebergibt dem UP in R1 (Register 7773) die Adresse des kat6-Textbereichs (Adressfeld) und in R2 (Register 7776) die hoechste
;                Zeichenzahl (hier 12) und ruft das UP auf.
; UP kat6eingabe: Aufruf mit 025, Kanal K0 vorher angewaehlt. Jedes Eingabezeichen wird als kat6-Code gespeichert (kat6: Eingabecode der Kodetabelle,
;                6 Bit je Zeichen, 5 Zeichen je Wort, erstes Zeichen rechts, Stoppbit ueber dem letzten Zeichen jedes Wortes, z0 am letzten Wort). Die Worte werden ab der Adresse in R1 gespeichert. Die Eingabe endet
;                  - mit dem Zeichen : (wird als letztes Zeichen gespeichert und zaehlt mit),
;                  - mit dem Zeichen WRZL (nicht gespeichert),
;                  - sobald R2 Zeichen angenommen sind.
;                Bereichsgroesse in Worten: (R2 + 4) / 5 = 3. Tasten ohne kat6-Zeichen werden ueberlesen.
; Empfehlung (001): kleinste Startzelle 0000, Ende vor 7600 (Arbeitsspur). Das Makro KAT6EINGABE belegt Zellen bis zur 0100-Grenze seiner Tabelle.
;#DOK-0001 KAT6EINGABE: Eingabe "hallo welt:" ueber K0 (11 Zeichen, Eingabeende mit Doppelpunkt, 3 Worte)
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat6eingabe_dp.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      3                    ; Zellen 0001 bis 0003: Bereich fuer 12 Zeichen = 3 Worte
kbein:          dw      0                    ; Zelle 0004: KB/GB-Zustand der Eingabe (0 = KB, 1 = GB), initial KB (Festlegung 030)
radr:           da      text                 ; Zelle 0005: Adresse des Bereichs (Adressfeld)
rkbe:           da      kbein                ; Zelle 0006: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr                 ; AC := Adresse des Bereichs
                240     r1                   ; R1 := Adresse des Bereichs
                211     #12                  ; AC := hoechste Zeichenzahl
                240     r2                   ; R2 := 12
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                025     eingabe              ; Aufruf KAT6EINGABE, AC := Rueckkehrwort
                020     0                    ; Halt

; ---- UP KAT6EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT6EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat6-Text ab R1 ab (Tabelle ztab liegt im Makro)
                end

; Sollwerte von Hand hergeleitet nach Assemblerdokumentation 3.3.18 (kat6-Codes = Eingabeadressen: h = 030, a = 021, l = 043, o = 046, Leerzeichen = 012, w = 066, e = 025, t = 063,
; : = 015; erstes Zeichen rechts, 6 Bit = 2 Oktalziffern je Zeichen, Stoppbit 1 unmittelbar links vom letzten Zeichen des Wortes, z0 = 040000000000 am letzten Wort).
; Eingabe: h a l l o ZR w e l t : (11 Zeichen, der 12. Platz bleibt frei, danach Eingabeende durch den Doppelpunkt).
; Wort 1 (h a l l o)  : o 46, l 43, l 43, a 21, h 30 und Stoppbit z2 (volles Wort)        -> 14643432130
; Wort 2 (ZR w e l t) : t 63, l 43, e 25, w 66, Leerzeichen 12 und Stoppbit z2            -> 16343256612
; Wort 3 (:) mit z0    : : 15 rechts, Stoppbit in Bit 6 (= 0100), z0                       -> 40000000115
; Zustandszelle kbein bleibt 0. R1 = 0001 * 01000, R2 = 12, R3 = 0004 * 01000. AC = -1 (Rest nach dem Eingabeende).
; Halt in Zelle 0017, BZ = 0020. Das Zeichen x nach dem Doppelpunkt wird nicht gelesen.
;#PRUEFE-START
; BZ=0020 AC=77777777777
; 0001: 14643432130   # Wort 1: h a l l o
; 0002: 16343256612   # Wort 2: ZR w e l t
; 0003: 40000000115   # Wort 3: : mit z0
; 0004: 00000000000   # kbein: Zustand der Eingabe nach dem UP
; 7773: 00000001000   # R1 unveraendert
; 7774: 00000004000   # R3 unveraendert
; 7776: 00000000014   # R2 unveraendert
;#PRUEFE-ENDE
