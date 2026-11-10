; kat6ausgabe_alle.asm - Test KAT6AUSGABE: alle Zeichen des kat6-Vorrats in KB und in GB (auch / % und Akzent), Zeilenschaltung, Zustandswechsel ueber Textgrenzen hinweg
;                        Text 1: Zustand KB (Start): a bis z, Leerzeichen, 0 bis 9, . , - + : / % Akzent
;                        Text 2: Um. GB, dann a bis z in GB (Grossbuchstaben)
;                        Text 3: ohne Umschaltzeichen, Zustand GB aus Text 2: 0 1 2 4 5 6 8 9, Leerzeichen, . , = : / % Akzent in GB (ohne 3, 7 und -, deren GB-Zeichen kein ASCII haben)
;                        Text 4: Um. KB, a b, Zeilenschaltung, c d
;#DOK-0001 KAT6AUSGABE: alle Zeichen in KB und GB, Zeilenschaltung
;#SPEI-0001 0001-0033
;#PROT STUFE=2
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/kat6ausgabe_alle
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/kat6ausgabe_alle-sw-ausgabe.txt

r1:             abs     07773                ; Register 1: Startadresse des Textes (Adressfeld)
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text1:          kat6    abcdefghijklmnopqrstuvwxyz 0123456789.,-+:/%`  ; Zellen 0001 bis 0011: 45 Zeichen, 9 Worte
text2:          kat6    $ingbabcdefghijklmnopqrstuvwxyz  ; Zellen 0012 bis 0017: Um. GB und a bis z, 6 Worte
text3:          kat6    01245689 .,=:/%`  ; Zellen 0020 bis 0023: 16 Zeichen, 4 Worte
text4:          kat6    $inkbab$wrzlcd  ; Zellen 0024 bis 0025: Um. KB, a, b, Zeilenschaltung, c, d
radr1:          da      text1                ; Zelle 0026: Adresse von Text 1 (Adressfeld)
radr2:          da      text2                ; Zelle 0027: Adresse von Text 2 (Adressfeld)
radr3:          da      text3                ; Zelle 0030: Adresse von Text 3 (Adressfeld)
radr4:          da      text4                ; Zelle 0031: Adresse von Text 4 (Adressfeld)
kbaus:          dw      0                    ; Zelle 0032: KB/GB-Zustand (0 = KB, 1 = GB), initial KB
rkb:            da      kbaus                ; Zelle 0033: Adresse der Zustandszelle (Adressfeld)
haupt:          211     rkb                  ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     radr1                ; AC := Adresse von Text 1
                240     r1                   ; R1 := Adresse von Text 1
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 1)
                211     radr2                ; AC := Adresse von Text 2
                240     r1                   ; R1 := Adresse von Text 2
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 2)
                211     radr3                ; AC := Adresse von Text 3
                240     r1                   ; R1 := Adresse von Text 3
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 3)
                211     radr4                ; AC := Adresse von Text 4
                240     r1                   ; R1 := Adresse von Text 4
                025     ausgabe              ; Aufruf KAT6AUSGABE (Text 4)
                020     0                    ; Halt
ausgabe:        KAT6AUSGABE                  ; UP: Ausgabe eines kat6-Textes
ende:           end

; Sollwerte von Hand hergeleitet, unabhaengiger Kodierer nach Doku 3.3.18 (Codes: a bis i = 021 bis 031, j bis r = 041 bis 051, s bis z = 062 bis 071, Ziffern 00 bis 07, 8 = 010, 9 = 011,
; Leerzeichen 012, : 015, + und = 020, wrzl 032, . 033, Um. GB 037, - 040, Um. KB 057, Akzent 060, / 061, Komma 073, % 074; erstes Zeichen rechts, Stoppbit z2 bzw. ueber dem letzten Zeichen, z0 im letzten Wort).
; Schreibwerkausgabe aus Tabelle 1 der Kodetabellen (Spalten Klbuch/Gbuch, ASCII):
; Text 1 (KB): "abcdefghijklmnopqrstuvwxyz 0123456789.,-+:/%`".
; Text 2 (Um. GB, dann GB): Grossbuchstaben "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (das Zeichen Um. GB selbst druckt nichts).
; Text 3 (GB aus Text 2): 0 -> #, 1 -> <, 2 -> ", 4 -> [, 5 -> >, 6 -> ', 8 -> ~, 9 -> ], Leerzeichen, . -> !, , -> ?, = (Code 020) -> =, : -> (, / -> ), % -> *, Akzent -> ;  = `#<"[>'~] !?=()*;`.
; Text 4: Um. KB, "ab", Zeilenschaltung (Zeichen 10), "cd" -> "ab" Zeilenumbruch "cd". Wort 1 = c wrzl b a Um. KB = 23 32 22 21 57 mit Stoppbit z2 -> 12332222157; Wort 2 = d mit Stoppbit z26 und z0 -> 40000000124.
; Zellen: text1 0001 bis 0011, text2 0012 bis 0017, text3 0020 bis 0023, text4 0024 bis 0025, radr1..4 0026 bis 0031, kbaus 0032, rkb 0033,
; Hauptprogramm 0034 bis 0053 (3 + 4*3 + Halt = 16 Zellen, Halt 0053 -> BZ = 0054).
; Zustand: Text 4 beginnt mit Um. KB -> kbaus = 0. R1 = Adresse von Text 4 = 0024 * 01000 = 24000; R3 = Adresse von kbaus = 0032 * 01000 = 32000. AC = letztes Textwort von Text 4 = 40000000124.
;#PRUEFE-START
; BZ=0054 AC=40000000124
; 0001: 12524232221
; 0011: 56074611520
; 0012: 12423222137
; 0017: 40000017170
; 0020: 10504020100
; 0023: 40000000160
; 0024: 12332222157
; 0025: 40000000124
; 0032: 00000000000
; 7773: 00000024000
; 7774: 00000032000
;#PRUEFE-ENDE
