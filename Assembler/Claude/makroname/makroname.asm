; makroname.asm - Test der benannten Makro-Parameter ($name statt $1 bis $9; Assemblerdokumentation 4.26)
;#DOK-0001 Test von MACRO mit Namen: $name im Operanden und in $CALC, mehr als neun Namen, $DEFAULT name, $P(name), $LEN(name), $PR(name), $REPT, $IF, variable Parameterzahl, Aufruf eines Makros aus einem Makro, Gross und Klein
;#PROT STUFE=2
;#MACRODATEI1=makroname.macro
; Fall A: SUMPAAR ist das Beispiel 2 der Doku: erstes Wort = erster, zweites Wort = Summe beider Parameter.
SUMPAAR:        MACRO erster zweiter
                dw      $erster                 ; erstes Wort $erster
                dw      $CALC($erster+$zweiter) ; Summe beider Parameter
                MEND                            ; Ende von SUMPAAR
; Fall B: VIELE hat zwoelf Namen; zehn, elf und zwoelf liegen hinter der Grenze 9 der Zahlenform.
; elf und zwoelf haben Vorgabewerte ($DEFAULT mit Namen); Nummern bleiben neben den Namen gueltig.
VIELE:          MACRO a1 a2 a3 a4 a5 a6 a7 a8 a9 zehn elf zwoelf
                $DEFAULT elf 7
                $DEFAULT zwoelf 8
                dw      $zehn                   ; Parameter 10 (Name zehn)
                dw      $elf                    ; Parameter 11 oder Vorgabe 7
                dw      $zwoelf                 ; Parameter 12 oder Vorgabe 8
                dw      $#                      ; Zahl der uebergebenen Parameter
                dw      $CALC($zehn+$elf)       ; zehn plus elf
                dw      $CALC($LEN(zehn)+$LEN(a1)) ; Zeichenzahl von zehn plus Zeichenzahl von a1
                dw      $P(zehn)                ; $P mit Namen: Parameter 10
                dw      $a9                     ; Parameter 9 mit Namen
                dw      $2                      ; Parameter 2 mit Nummer
                MEND                            ; Ende von VIELE
; Fall C: GRENZE prueft beide Parameter mit $PR(name) und verzweigt mit $IF auf den Namen.
GRENZE:         MACRO modus wert
                $PR(modus) AUS EIN
                $PR(wert)  $TYPZAHL 0 100
                dw      $wert                   ; geprueften Wert ausgeben
                $IF $modus = EIN
                dw      1                       ; Modus EIN
                $ELSE
                dw      0                       ; Modus AUS
                $ENDIF
                MEND                            ; Ende von GRENZE
; Fall D: WIEDERHOL wiederholt mit $REPT $anzahl und mit $REPT $LEN(text).
WIEDERHOL:      MACRO anzahl text
                $REPT $anzahl
                dw      5                       ; ein Wort je Wiederholung von anzahl
                $ENDREPT
                $REPT $LEN(text)
                dw      6                       ; ein Wort je Zeichen von text
                $ENDREPT
                MEND                            ; Ende von WIEDERHOL
; Fall E: FOLGE hat zwei Namen und variable Parameterzahl (+); weitere Parameter nur ueber $P.
FOLGE:          MACRO anfang ende +
                dw      $#                      ; Zahl der uebergebenen Parameter
                dw      $CALC($anfang+$ende)    ; Summe der beiden benannten Parameter
                dw      $P(4)                   ; vierter Parameter, ohne Namen
                MEND                            ; Ende von FOLGE
; Fall F: AUSSEN ruft INNEN auf und uebergibt die Werte seiner Parameter.
INNEN:          MACRO ziel anzahl
                dw      $CALC($ziel*$anzahl)    ; Produkt
                MEND                            ; Ende von INNEN
AUSSEN:         MACRO breite hoehe
                INNEN   $breite $hoehe          ; Werte weitergeben
                MEND                            ; Ende von AUSSEN
; Fall G: Gross und Klein zaehlen: $anzahl und $Anzahl sind zwei Parameter.
GK:             MACRO anzahl Anzahl
                dw      $anzahl                 ; erster Parameter
                dw      $Anzahl                 ; zweiter Parameter
                MEND                            ; Ende von GK
; Fall H: $LEN(ausdruck) wirkt auch in einem Makro ohne Namen (Zahlenform): $LEN(1) ist die Zeichenzahl des ersten Parameters.
LAENGE:         MACRO 1
                dw      $LEN(1)                 ; Zeichenzahl von Parameter 1
                dw      $CALC($LEN(1)+$LEN(1))  ; doppelte Zeichenzahl
                MEND                            ; Ende von LAENGE
; Fall I: DREISSIG hat die groesstmoegliche Zahl von Namen (32): p1 bis p32.
DREISSIG:       MACRO p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32
                dw      $p32                    ; Parameter 32 (Name p32)
                dw      $P(p31)                 ; Parameter 31 ueber $P mit Namen
                dw      $CALC($p1+$p32)         ; Parameter 1 plus Parameter 32
                MEND                            ; Ende von DREISSIG
; Fall J: DATEIMAK steht in makroname.macro (;#MACRODATEI1): Namen gelten auch in Makrodateien.
                start                           ; Zaehlung beginnt bei 0000
                000     haupt                   ; Zelle 0000: Sprung zum Hauptprogramm
                SUMPAAR 3 4                     ; Zellen 0001 und 0002
                VIELE   1 2 3 4 5 6 7 8 9 10    ; Zellen 0003 bis 0013: zehn Parameter
                VIELE   1 2 3 4 5 6 7 8 9 10 11 12 ; Zellen 0014 bis 0024: zwoelf Parameter
                GRENZE  EIN 50                  ; Zellen 0025 und 0026
                GRENZE  AUS 7                   ; Zellen 0027 und 0030
                WIEDERHOL 2 abcd                ; Zellen 0031 bis 0036
                FOLGE   1 2 3 4                 ; Zellen 0037 bis 0041
                AUSSEN  6 7                     ; Zelle 0042
                GK      3 5                     ; Zellen 0043 und 0044
                LAENGE  hallo                   ; Zellen 0045 und 0046
                DREISSIG 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32
                                                ; Zellen 0047 bis 0051
                DATEIMAK 20 30                  ; Zellen 0052 und 0053
haupt:          164     0001                    ; Zelle 0054: Diagnoseausgabe (nur im Test)
                020     0                       ; Zelle 0055: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zahlen im Quelltext dezimal, hier oktal); Halt auf 0055, BZ danach 0056.
;#PRUEFE-START
; BZ=0056 US=1
; 0001: 00000000003   # SUMPAAR 3 4: erster = 3
; 0002: 00000000007   # SUMPAAR 3 4: 3+4 = 7
; 0003: 00000000012   # VIELE (10 Parameter): zehn = 10 = 012
; 0004: 00000000007   # elf nicht uebergeben: Vorgabe 7
; 0005: 00000000010   # zwoelf nicht uebergeben: Vorgabe 8 = 010
; 0006: 00000000012   # $# = 10 = 012
; 0007: 00000000021   # zehn+elf = 10+7 = 17 = 021
; 0010: 00000000003   # $LEN(zehn)+$LEN(a1) = 2+1 = 3
; 0011: 00000000012   # $P(zehn) = 10 = 012
; 0012: 00000000011   # $a9 = 9 = 011
; 0013: 00000000002   # $2 = 2
; 0014: 00000000012   # VIELE (12 Parameter): zehn = 10 = 012
; 0015: 00000000013   # elf = 11 = 013
; 0016: 00000000014   # zwoelf = 12 = 014
; 0017: 00000000014   # $# = 12 = 014
; 0020: 00000000025   # zehn+elf = 10+11 = 21 = 025
; 0021: 00000000003   # $LEN(zehn)+$LEN(a1) = 2+1 = 3
; 0022: 00000000012   # $P(zehn) = 10 = 012
; 0023: 00000000011   # $a9 = 9 = 011
; 0024: 00000000002   # $2 = 2
; 0025: 00000000062   # GRENZE EIN 50: wert = 50 = 062
; 0026: 00000000001   # Modus EIN
; 0027: 00000000007   # GRENZE AUS 7: wert = 7
; 0030: 00000000000   # Modus AUS
; 0031: 00000000005   # WIEDERHOL 2 abcd: anzahl = 2 Worte 5 (erstes)
; 0032: 00000000005   # zweites Wort 5
; 0033: 00000000006   # $LEN(text) = 4 Worte 6 (erstes)
; 0034: 00000000006   # zweites Wort 6
; 0035: 00000000006   # drittes Wort 6
; 0036: 00000000006   # viertes Wort 6
; 0037: 00000000004   # FOLGE 1 2 3 4: $# = 4
; 0040: 00000000003   # anfang+ende = 1+2 = 3
; 0041: 00000000004   # $P(4) = 4
; 0042: 00000000052   # AUSSEN 6 7 -> INNEN: 6*7 = 42 = 052
; 0043: 00000000003   # GK 3 5: $anzahl = 3
; 0044: 00000000005   # $Anzahl = 5
; 0045: 00000000005   # LAENGE hallo: $LEN(1) = 5
; 0046: 00000000012   # 5+5 = 10 = 012
; 0047: 00000000040   # DREISSIG 1 bis 32: $p32 = 32 = 040
; 0050: 00000000037   # $P(p31) = 31 = 037
; 0051: 00000000041   # $p1+$p32 = 1+32 = 33 = 041
; 0052: 00000000062   # DATEIMAK 20 30: 20+30 = 50 = 062
; 0053: 00000000036   # $hoehe = 30 = 036
;#PRUEFE-ENDE
