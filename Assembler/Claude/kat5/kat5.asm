; kat5.asm - Test von kat5 (komprimierter Text, 1 bis 5 Zeichen in genau einem Wort, linksbuendig, 6-Bit-Code in Sortierreihenfolge), Doku 3.3.15 ab c82ass 1.03-001
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
t1:             kat5    abcde        ; Zelle 0001: genau ein volles Wort
t2:             kat5    hallo        ; Zelle 0002: Beispiel der Doku
t3:             kat5    \ a b \      ; Zelle 0003: fuenf Zeichen, fuehrendes und abschliessendes Leerzeichen bleiben
t4:             kat5    x$wrzl       ; Zelle 0004: Buchstabe und Marke $wrzl (Code 053)
t5:             kat5    $ingb=$inkb  ; Zelle 0005: Marken $ingb (055), $inkb (054) und = (05)
t6:             kat5    01234        ; Zelle 0006: Ziffern 0 bis 4 (Codes 07 bis 013)
t7:             kat5    56789        ; Zelle 0007: Ziffern 5 bis 9 (Codes 014 bis 020)
t8:             kat5    a$WRZL       ; Zelle 0010: Marke in Grossbuchstaben wird erkannt
t9:             kat5    a$wrzlb      ; Zelle 0011: Zeichen folgt unmittelbar auf die Marke
t10:            kat5    ,-.+:        ; Zelle 0012: Satzzeichen (Codes 02 bis 06)
t11:            kat5    z            ; Zelle 0013: ein einziges Zeichen, Fuellung 00 rechts
t12:            kat5    ab           ; Zelle 0014: zwei Zeichen (Beispiel der Doku)
t13:            kat5    b            ; Zelle 0015: groesser als abc und ab (Sortierung)
t14:            kat5    a:b          ; Zelle 0016: Doppelpunkt im Text (Beispiel der Doku)
t15:            kat5    abc          ; Zelle 0017: groesser als ab, kleiner als b (Beispiel der Doku)
t16:            kat5    a b          ; Zelle 0020: Leerzeichen im Text ohne Backslash
t17:            kat5    abcd$wrzl    ; Zelle 0021: Marke als fuenftes Zeichen
haupt:          020     0            ; Zelle 0022: Halt
ende:           end

; Sollwerte von Hand aus der Tabelle der Doku 3.3.15 hergeleitet: 6 Bit je Zeichen = 2 Oktalziffern, erstes Zeichen links
; (z3 bis z8), Fuellung 00 rechts, die erste Oktalstelle des Wortes (z0 bis z2) ist 0, kein Endekennzeichen.
; Codes: Leerzeichen 01, Komma 02, - 03, . 04, + und = 05, Doppelpunkt 06, Ziffern 0 bis 9 = 07 bis 020, a = 021 ... z = 052,
; $wrzl 053, $inkb 054, $ingb 055.
; t1 abcde: 0 21 22 23 24 25. t2 hallo: h 030, a 021, l 034, l 034, o 037: 0 30 21 34 34 37 (Doku).
; t3 Leer a Leer b Leer: 0 01 21 01 22 01. t4 x = 050, $wrzl = 053: 0 50 53 00 00 00.
; t5 $ingb = $inkb: 0 55 05 54 00 00. t6 0 bis 4: 0 07 10 11 12 13. t7 5 bis 9: 0 14 15 16 17 20.
; t8 a $wrzl: 0 21 53 00 00 00. t9 a $wrzl b: 0 21 53 22 00 00. t10 , - . + : = 0 02 03 04 05 06.
; t11 z: 0 52 00 00 00 00. t12 ab: 0 21 22 00 00 00 (Doku 02122000000). t13 b: 0 22 00 00 00 00 (Doku 02200000000).
; t14 a : b: 0 21 06 22 00 00 (Doku 02106220000). t15 abc: 0 21 22 23 00 00 (Doku 02122230000).
; t16 a Leer b: 0 21 01 22 00 00. t17 a b c d $wrzl: 0 21 22 23 24 53.
; Sortierreihenfolge: t12 (ab) < t15 (abc) < t13 (b) als Zahlen.
;#PRUEFE-START
; BZ=0023
; 0001: 02122232425   # t1
; 0002: 03021343437   # t2 (hallo)
; 0003: 00121012201   # t3
; 0004: 05053000000   # t4
; 0005: 05505540000   # t5
; 0006: 00710111213   # t6 (0 bis 4)
; 0007: 01415161720   # t7 (5 bis 9)
; 0010: 02153000000   # t8
; 0011: 02153220000   # t9
; 0012: 00203040506   # t10 (Satzzeichen)
; 0013: 05200000000   # t11
; 0014: 02122000000   # t12 (ab)
; 0015: 02200000000   # t13 (b)
; 0016: 02106220000   # t14 (a:b)
; 0017: 02122230000   # t15 (abc)
; 0020: 02101220000   # t16 (a b)
; 0021: 02122232453   # t17
;#PRUEFE-ENDE
