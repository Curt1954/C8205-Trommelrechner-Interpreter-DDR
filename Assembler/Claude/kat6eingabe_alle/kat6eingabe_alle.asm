; kat6eingabe_alle.asm - KAT6EINGABE: alle 48 Tasten mit kat6-Zeichen (a bis z, 0 bis 9, Leertaste, . , - + = / % Akzent : Um. GB Um. KB), dazwischen Tasten ohne kat6-Zeichen (werden ueberlesen)
;   Eingabedatei: WR a b c d e / f g h i j % k ... z 0 ... 9 ZR . , - + = Um. GB Um. KB : mit eingestreuten Tasten WR, BM, IS, TAB
;   (/, % und der Akzent sind bei kat6 Zeichen und werden gespeichert, anders als bei kat5).
;   R2 = 50, Eingabeende mit dem Zeichen : als 48. Zeichen (das 10. Wort ist unvollstaendig und bekommt Stoppbit und z0, R2 wird nicht erreicht).
;#DOK-0001 KAT6EINGABE: alle kat6-Zeichen, Tasten ohne kat6-Zeichen werden ueberlesen, Ende mit Doppelpunkt im unvollstaendigen Wort
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/kat6eingabe_alle.txt
;#TASTENFOLGE H SW=1 G R

r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)
r2:             abs     07776                ; Register 2: hoechste Zeichenzahl
r3:             abs     07774                ; Register 3: Adresse der KB/GB-Zelle (Adressfeld)

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
text:           db      10                   ; Zellen 0001 bis 0012: Bereich fuer 50 Zeichen = 10 Worte
kbein:          dw      0                    ; Zelle 0013: KB/GB-Zustand der Eingabe (0 = KB), initial KB (Festlegung 030)
radr:           da      text                 ; Zelle 0014: Adresse des Bereichs (Adressfeld)
rkbe:           da      kbein                ; Zelle 0015: Adresse der Zustandszelle (Adressfeld)
haupt:          ANWAHL  K0                   ; Kanal 0 = SW zur Eingabe anwaehlen
                211     radr                 ; AC := Adresse des Bereichs
                240     r1                   ; R1 := Adresse des Bereichs
                211     #50                  ; AC := hoechste Zeichenzahl
                240     r2                   ; R2 := 50
                211     rkbe                 ; AC := Adresse der Zustandszelle
                240     r3                   ; R3 := Adresse der Zustandszelle
                025     eingabe              ; Aufruf KAT6EINGABE
                020     0                    ; Halt

; ---- UP KAT6EINGABE als Makro (Makrodatei c82ass.makros)
eingabe:        KAT6EINGABE                  ; Unterprogramm: liest Zeichen ueber K0 und legt den kat6-Text ab R1 ab
                end

; Sollwerte von Hand hergeleitet. kat6-Codes (= Eingabeadressen): 0 bis 7 = 00 bis 07, 8 = 010, 9 = 011, Leertaste 012, : 015, + und = 020, a bis i 021 bis 031, . 033, Um. GB 037, - 040, j bis r 041 bis 051,
; Um. KB 057, Akzent 060, / 061, s bis z 062 bis 071, Komma 073, % 074. Die Tasten WR, BM, IS und TAB werden ueberlesen. Die 48 Zeichen belegen 10 Worte (9 volle zu je 5 Zeichen, Stoppbit z2):
; Wort 1 a b c d e   = 12524232221   Wort 2 / f g h i = 13130272661   Wort 3 j % k l m = 14443427441   Wort 4 n o p q r = 15150474645
; Wort 5 s t Akzent u v = 16564606362   Wort 6 w x y z 0 = 10071706766   Wort 7 1 2 3 4 5 = 10504030201   Wort 8 6 7 8 9 ZR = 11211100706
; Wort 9 . , - + = = 12020407333   Wort 10 Um.GB Um.KB : mit Stoppbit in Bit 18 und z0 = 40001155737. Zustand: zuletzt Um. KB -> kbein = 0. R1 = 0001 * 01000, R2 = 50, R3 = 0013 * 01000, AC = -1.
;#PRUEFE-START
; BZ=0027 AC=77777777777
; 0001: 12524232221   # Wort 1
; 0002: 13130272661   # Wort 2
; 0003: 14443427441   # Wort 3
; 0004: 15150474645   # Wort 4
; 0005: 16564606362   # Wort 5
; 0006: 10071706766   # Wort 6
; 0007: 10504030201   # Wort 7
; 0010: 11211100706   # Wort 8
; 0011: 12020407333   # Wort 9
; 0012: 40001155737   # Wort 10
; 0013: 00000000000   # kbein: zuletzt Um. KB
; 7773: 00000001000   # R1 unveraendert
; 7774: 00000013000   # R3 unveraendert
; 7776: 00000000062   # R2 unveraendert (50)
;#PRUEFE-ENDE
