; makrotext.asm - Test der Zeichenketten-Parameter ($TYPTEXT, Zeichenzahl $LENn) im Makro-Praeprozessor (Assemblerdokumentation 4.10)
;#DOK-0001 Test von Parametern in Anfuehrungszeichen mit Leerzeichen, $PRx $TYPTEXT und $LENn (auch in $CALC)
;#PROT STUFE=2
; TXT2 text: Zeichenzahl in $IF und $REPT; ein Wort 1 bei mehr als 5 Zeichen, sonst 2, dann je Zeichen ein Wort 3
TXT2:           MACRO 1
                $IF $LEN1 > 5
                dw      1               ; Text laenger als 5 Zeichen
                $ELSE
                dw      2               ; Text hoechstens 5 Zeichen
                $ENDIF
                $REPT $LEN1
                dw      3               ; je Zeichen ein Wort
                $ENDREPT
                MEND
; TXT text n: legt die Zeichenzahl des Textes, die Zeichenzahl plus n und die Zahl der uebergebenen Parameter ab
TXT:            MACRO 2
                $PR1 $TYPTEXT 20
                dw      $LEN1           ; Zeichenzahl des Textes (Parameter 1)
                dw      $CALC($LEN1+$2) ; Zeichenzahl plus Parameter 2
                dw      $#              ; Zahl der Parameter: der Text zaehlt als ein Parameter
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                TXT     "ab cd e" 3  ; Zellen 0001 bis 0003: Text mit 7 Zeichen (2 Leerzeichen), n = 3
                TXT     'x y'  10    ; Zellen 0004 bis 0006: Apostrophe, 3 Zeichen, n = 10
                TXT     hallo  1     ; Zellen 0007 bis 0011: ohne Anfuehrungszeichen, 5 Zeichen, n = 1
                TXT2    "ab cd e"    ; Zellen 0012 bis 0021: 7 Zeichen, also 1 und sieben mal 3
                TXT2    xy           ; Zellen 0022 bis 0024: 2 Zeichen, also 2 und zwei mal 3
haupt:          164     0001         ; Zelle 0025: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0026: Halt
ende:           end

; Sollwerte von Hand hergeleitet: "ab cd e" hat a b _ c d _ e = 7 Zeichen; 'x y' = 3; hallo = 5.
;#PRUEFE-START
; BZ=0027 US=1
; 0001: 00000000007   # Zeichenzahl 7
; 0002: 00000000012   # 7+3 = 10 = 012
; 0003: 00000000002   # zwei Parameter (Text und n)
; 0004: 00000000003   # Zeichenzahl 3
; 0005: 00000000015   # 3+10 = 13 = 015
; 0006: 00000000002   # zwei Parameter
; 0007: 00000000005   # Zeichenzahl 5
; 0010: 00000000006   # 5+1 = 6
; 0011: 00000000002   # zwei Parameter
; 0012: 00000000001   # TXT2: 7 > 5
; 0013: 00000000003   # erstes Zeichen
; 0021: 00000000003   # siebtes Zeichen
; 0022: 00000000002   # TXT2: 2 <= 5
; 0023: 00000000003   # erstes Zeichen
; 0024: 00000000003   # zweites Zeichen
;#PRUEFE-ENDE
