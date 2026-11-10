; kat5ausgabe_alle.asm - Test KAT5AUSGABE: alle 45 kat5-Codes in KB und in GB, Zeilenschaltung, Zustandswechsel ueber Wortgrenzen hinweg
;                        20 Worte hintereinander (Zellen 0001 bis 0024), ein Wort je Aufruf, Schleife mit R1 um 01000 weiter:
;                        Text 1 (9 Worte), Zustand KB (Start): a bis z, Leerzeichen, 0 bis 9, . , - + :
;                        Text 2 (6 Worte): Um. GB, dann a bis z in GB (Grossbuchstaben)
;                        Text 3 (3 Worte), ohne Umschaltzeichen, Zustand GB aus Text 2: Ziffern, Leerzeichen, . , = : in GB (ohne 3, 7 und -, deren GB-Zeichen kein ASCII haben)
;                        Text 4 (2 Worte): Um. KB, a b, Zeilenschaltung, c d
;#DOK-0001 KAT5AUSGABE: alle Codes in KB und GB, Zeilenschaltung, 20 Worte in einer Schleife
;#SPEI-0001 0001-0030
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat5ausgabe_alle
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat5ausgabe_alle-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Adresse des Wortes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat5    abcde                ; Zelle 0001: Text 1, Wort 1
                kat5    fghij                ; Zelle 0002: Text 1, Wort 2
                kat5    klmno                ; Zelle 0003: Text 1, Wort 3
                kat5    pqrst                ; Zelle 0004: Text 1, Wort 4
                kat5    uvwxy                ; Zelle 0005: Text 1, Wort 5
                kat5    z 012                ; Zelle 0006: Text 1, Wort 6: z, Leerzeichen, 0, 1, 2
                kat5    34567                ; Zelle 0007: Text 1, Wort 7
                kat5    89.,-                ; Zelle 0010: Text 1, Wort 8: 8, 9, Punkt, Komma, Minus
                kat5    +:                   ; Zelle 0011: Text 1, Wort 9: Plus, Doppelpunkt
                kat5    $ingbabcd            ; Zelle 0012: Text 2, Wort 1: Um. GB, a, b, c, d
                kat5    efghi                ; Zelle 0013: Text 2, Wort 2
                kat5    jklmn                ; Zelle 0014: Text 2, Wort 3
                kat5    opqrs                ; Zelle 0015: Text 2, Wort 4
                kat5    tuvwx                ; Zelle 0016: Text 2, Wort 5
                kat5    yz                   ; Zelle 0017: Text 2, Wort 6: y, z
                kat5    01245                ; Zelle 0020: Text 3, Wort 1
                kat5    689 .                ; Zelle 0021: Text 3, Wort 2: 6, 8, 9, Leerzeichen, Punkt
                kat5    ,=:                  ; Zelle 0022: Text 3, Wort 3: Komma, Gleichheitszeichen, Doppelpunkt
                kat5    $inkbab$wrzlc        ; Zelle 0023: Text 4, Wort 1: Um. KB, a, b, Zeilenschaltung, c
                kat5    d                    ; Zelle 0024: Text 4, Wort 2: d
radr1:          da      text1                ; Zelle 0025: Adresse von Text 1, Wort 1 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0026: KB/GB-Zustand (0 = KB, 1 = GB), initial KB
rkb:            da      kbaus                ; Zelle 0027: Adresse der Zustandszelle (Adressfeld)
zaehl:          dw      0                    ; Zelle 0030: Schleifenzaehler (noch auszugebende Worte minus 1)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Wort 1
                240     r1                   ; R1 := Adresse von Wort 1
                211     #19                  ; AC := 19 (dezimal: 20 Worte minus 1)
                240     zaehl                ; zaehl := 19
schl:           025     ausgabe              ; Aufruf KAT5AUSGABE: ein Wort ab R1
                211     r1                   ; AC := Adresse des ausgegebenen Wortes
                210     #01000               ; plus eine Adresseinheit: naechstes Wort
                240     r1                   ; R1 := Adresse des naechsten Wortes
                211     zaehl                ; AC := zaehl
                220     #1                   ; AC := zaehl - 1
                240     zaehl                ; zaehl := zaehl - 1
                050     schl                 ; zaehl >= 0: naechstes Wort
                020     0                    ; Halt
ausgabe:        KAT5AUSGABE                  ; UP: Ausgabe eines kat5-Wortes
ende:           end

; Sollwerte von Hand hergeleitet. Schreibwerkausgabe aus Tabelle 1 der Kodetabellen (Spalten Klbuch/Gbuch, ASCII):
; Text 1 (KB): "abcdefghijklmnopqrstuvwxyz 0123456789.,-+:".
; Text 2 (Um. GB, dann GB): Grossbuchstaben "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (das Zeichen Um. GB selbst druckt nichts).
; Text 3 (GB aus Text 2): 0 -> #, 1 -> <, 2 -> ", 4 -> [, 5 -> >, 6 -> ', 8 -> ~, 9 -> ], Leerzeichen, . -> !, , -> ?, = (Code 05) -> =, : -> (  = `#<"[>'~] !?=(`.
; Text 4: Um. KB, "ab", Zeilenschaltung (Zeichen 10), "cd" -> "ab" Zeilenumbruch "cd".
; kat5-Codes nach Doku 3.3.15: Leerzeichen 01, Komma 02, Minus 03, Punkt 04, + und = 05, Doppelpunkt 06, 0 bis 9 = 07 bis 020, a bis z = 021 bis 052, $wrzl 053, $inkb 054, $ingb 055.
; Wort 19 (Text 4, Wort 1) "$inkbab$wrzlc": Um. KB 054, a 021, b 022, Zeilenschaltung 053, c 023 -> 0 54 21 22 53 23 = 05421225323.
; Wort 20 (Text 4, Wort 2) "d": d 024 -> 0 24 00 00 00 00 = 02400000000.   Wort 10 (Text 2, Wort 1) "$ingbabcd": Um. GB 055, a 021, b 022, c 023, d 024 -> 05521222324.
; Zellen: Worte 0001 bis 0024 (20 Worte), radr1 0025, kbaus 0026, rkb 0027, zaehl 0030, Hauptprogramm 0031 bis 0050 (Halt) -> BZ = 0051.
; Schleife: zaehl 19 vor dem ersten Aufruf, je Durchlauf um 1 weniger, nach dem 20. Aufruf -1 (kein Sprung mehr) -> AC = -1 = 77777777777, zaehl = 77777777777.
; Zustand: Wort 19 beginnt mit Um. KB -> kbaus = 0. R1 = nach dem 20. Aufruf noch einmal um eine Adresseinheit weiter = 0025 * 01000 = 025000 (Zelle 0025); R3 = Adresse von kbaus = 0026 * 01000 = 026000.
;#PRUEFE-START
; BZ=0051 AC=77777777777
; 0012: 05521222324   # Wort 10: Um. GB, a, b, c, d
; 0023: 05421225323   # Wort 19: Um. KB, a, b, Zeilenschaltung, c
; 0024: 02400000000   # Wort 20: d
; 0026: 00000000000   # kbaus: zuletzt Um. KB
; 0030: 77777777777   # zaehl: -1 nach 20 Durchlaeufen
; 7773: 00000025000   # R1 = Adresse hinter dem 20. Wort
; 7774: 00000026000   # R3 unveraendert
;#PRUEFE-ENDE
