; makrosymbol.asm - Test: abs- und equ-Symbole mit festem Zahlenwert in Rechenausdruecken des Makro-Praeprozessors
;                  ($CALC, $CALCO, $IF, $REPT, als Aufrufparameter; Assemblerdokumentation 4.18, c82ass ab 1.00-062)
;#DOK-0001 Test: breite=12, hoehe=010 (=8), maske=077 (abs vor start), spaet=7 (abs hinter end), lage=07640 und spur=lage+040 (equ hinter end)
;#PROT STUFE=2
breite:         abs     12           ; dezimal 12
hoehe:          abs     010          ; oktal 010 = 8
maske:          abs     077          ; oktal 077 = 63
SYM:            MACRO
                dw      $CALC(breite*hoehe)         ; 12*8 = 96
                dw      $CALC(maske-hoehe)          ; 63-8 = 55
                dw      $CALC(min(breite,hoehe))    ; 8
                dw      $CALCO4(maske&breite)       ; 63&12 = 12, oktal 00014
                $IF $CALC(breite>hoehe) = 1
                dw      1                           ; 12 > 8: wahr
                $ELSE
                dw      0
                $ENDIF
                MEND
MAL:            MACRO 1
                dw      $CALC($1*3)                 ; Parameter darf ein Symbol sein: dreifacher Wert
                MEND
REP:            MACRO
                $REPT hoehe/4
                dw      $CALC($Z1+breite)           ; hoehe/4 = 2 Durchlaeufe: 12, 13
                $ENDREPT
                MEND
FERN:           MACRO
                dw      $CALC(spaet+1)              ; Symbol steht erst hinter end
                dw      $CALC(spur-lage)            ; equ-Symbole, spur verweist auf lage: 040 = 32
                dw      $CALCO(spur)                ; 07640+040 = 07700
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                SYM                  ; Zellen 0001 bis 0005
                MAL     breite       ; Zelle 0006
                MAL     hoehe        ; Zelle 0007
                MAL     breite+1     ; Zelle 0010: (breite+1)*3
                REP                  ; Zellen 0011 und 0012
                FERN                 ; Zellen 0013 bis 0015
haupt:          020     0            ; Zelle 0016: Halt
ende:           end
spaet:          abs     7            ; Definition hinter dem Aufruf
lage:           equ     07640        ; equ mit festem Zahlenwert
spur:           equ     lage+040     ; verweist auf ein anderes equ-Symbol

; Sollwerte von Hand hergeleitet; Halt auf 0016, BZ danach 0017.
; 12*8=96=0140; 63-8=55=067; min(12,8)=8=010; 63&12=12=014; 12>8 -> 1; 3*12=36=044; 3*8=24=030; 3*(12+1)=39=047;
; REP: 12=014 und 13=015; spaet+1=8=010; 040 - 0 = 32 = 040; 07640+040 = 07700.
;#PRUEFE-START
; BZ=0017 US=1
; 0001: 00000000140   # breite*hoehe = 96
; 0002: 00000000067   # maske-hoehe = 55
; 0003: 00000000010   # min(breite,hoehe) = 8
; 0004: 00000000014   # $CALCO4(maske&breite) = 00014
; 0005: 00000000001   # $IF breite>hoehe: wahr
; 0006: 00000000044   # MAL breite = 36
; 0007: 00000000030   # MAL hoehe = 24
; 0010: 00000000047   # MAL breite+1 = 39
; 0011: 00000000014   # REP, Durchlauf 0: 0+12
; 0012: 00000000015   # REP, Durchlauf 1: 1+12
; 0013: 00000000010   # spaet+1 = 8
; 0014: 00000000040   # spur-lage = 32
; 0015: 00000007700   # $CALCO(spur) = 07700
;#PRUEFE-ENDE
