; makrostrfkt.asm - Test von $SUBSTR, $INDEX, $UPPER, $LOWER und $STRCMP (Assemblerdokumentation 4.21)
;#DOK-0001 Test Zeichenkettenfunktionen: Teilstring, Suche, Gross-/Kleinwandlung, Vergleich mit Leerzeichen, Ziel in der Variablen selbst
;#PROT STUFE=2
; SUBT: Teilstring von "BANANE" (B1 A2 N3 A4 N5 E6); die Texte werden ueber Laenge $V(#z) und $STRCMP geprueft
SUBT:           MACRO
                $SUBSTR z "BANANE" 2 3
                dw      $V(#z)                  ; ANA hat 3 Zeichen
                $STRCMP r "$V(z)" "ANA"
                dw      $V(r)                   ; gleich: 0
                $SUBSTR z "BANANE" 5
                dw      $V(#z)                  ; ohne Anzahl der Rest NE: 2
                $STRCMP r "$V(z)" "NE"
                dw      $V(r)                   ; gleich: 0
                $SUBSTR z "BANANE" 1
                dw      $V(#z)                  ; ganzer Text: 6
                $SUBSTR z "BANANE" 6 1
                dw      $V(#z)                  ; letztes Zeichen: 1
                $STRCMP r "$V(z)" "E"
                dw      $V(r)                   ; gleich: 0
                MEND
; INDX: Position des ersten Vorkommens, 0 wenn es fehlt, Gross-/Kleinschreibung wird unterschieden
INDX:           MACRO
                $INDEX p "abc=42" "="
                dw      $V(p)                   ; Gleichheitszeichen an Position 4
                $INDEX p "abc" "x"
                dw      $V(p)                   ; nicht gefunden: 0
                $INDEX p "BANANE" "AN"
                dw      $V(p)                   ; erstes Vorkommen bei 2
                $INDEX p "BANANE" "ANE"
                dw      $V(p)                   ; ANE beginnt bei 4
                $INDEX p "banane" "A"
                dw      $V(p)                   ; A gross kommt in banane nicht vor: 0
                $INDEX p "a b c" " "
                dw      $V(p)                   ; erstes Leerzeichen an Position 2
                $INDEX p "BANANE" "BANANE"
                dw      $V(p)                   ; ganzer Text: Position 1
                MEND
; UPLO: Wandlung; Ziffern, Leerzeichen und Minus bleiben, Umlaut bleibt (zwei Bytes); Ziel ist auch die Quelle
UPLO:           MACRO
                $UPPER t "Ab c-9z"
                $STRCMP r "$V(t)" "AB C-9Z"
                dw      $V(r)                   ; gleich: 0
                dw      $V(#t)                  ; 7 Zeichen
                $LOWER t "Ab C-9Z"
                $STRCMP r "$V(t)" "ab c-9z"
                dw      $V(r)                   ; gleich: 0
                $UPPER t "$V(t)"
                $STRCMP r "$V(t)" "AB C-9Z"
                dw      $V(r)                   ; aus ab c-9z wird AB C-9Z: 0
                $UPPER u "äb"
                dw      $V(#u)                  ; ä zaehlt 2 Bytes, b 1: 3
                $STRCMP r "$V(u)" "äB"
                dw      $V(r)                   ; ä unveraendert, b gross: 0
                MEND
; VERGL: erzeugt die Vorzeichen-Kennung des Vergleichs: 0 gleich, 1 a groesser, 2 a kleiner
VERGL:          MACRO
                $IF $V(r) = 0
                dw      0                       ; gleich
                $ENDIF
                $IF $V(r) = 1
                dw      1                       ; a groesser
                $ENDIF
                $IF $V(r) = -1
                dw      2                       ; a kleiner
                $ENDIF
                MEND
; STRV: Byteweiser Vergleich ohne Ruecksicht auf Wortgrenzen
STRV:           MACRO
                $STRCMP r "abc" "abd"
                VERGL                           ; c kleiner d: 2
                $STRCMP r "abd" "abc"
                VERGL                           ; d groesser c: 1
                $STRCMP r "abc" "abc"
                VERGL                           ; gleich: 0
                $STRCMP r "ab" "abc"
                VERGL                           ; Anfangsstueck ist kleiner: 2
                $STRCMP r "abc" "ab"
                VERGL                           ; laenger ist groesser: 1
                $STRCMP r "a b" "a b"
                VERGL                           ; gleich trotz Leerzeichen: 0
                $STRCMP r "a b" "a  b"
                VERGL                           ; b (98) gegen Leerzeichen (32): groesser: 1
                $STRCMP r "B" "a"
                VERGL                           ; B (66) kleiner als a (97): 2
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                SUBT                 ; Zellen 1 bis 7
                INDX                 ; Zellen 8 bis 14 (dezimal)
                UPLO                 ; Zellen 15 bis 20 (dezimal)
                STRV                 ; Zellen 21 bis 28 (dezimal)
haupt:          164     0001         ; Zelle 29: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 30: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal).
; SUBT Zellen 1 bis 7 (oktal 0001 bis 0007): 3, 0, 2, 0, 6, 1, 0.
; INDX Zellen 8 bis 14 (oktal 0010 bis 0016): 4, 0, 2, 4, 0, 2, 1.
; UPLO Zellen 15 bis 20 (oktal 0017 bis 0024): 0, 7, 0, 0, 3, 0.
; STRV Zellen 21 bis 28 (oktal 0025 bis 0034): 2, 1, 0, 2, 1, 0, 1, 2.
; haupt = Zelle 29 (oktal 0035), Halt auf Zelle 30 (oktal 0036), BZ danach 0037.
;#PRUEFE-START
; BZ=0037 US=1
; 0001: 00000000003   # SUBT: Laenge von ANA
; 0002: 00000000000   # SUBT: ANA gleich ANA
; 0003: 00000000002   # SUBT: Rest NE hat 2 Zeichen
; 0004: 00000000000   # SUBT: NE gleich NE
; 0005: 00000000006   # SUBT: ganzer Text 6
; 0006: 00000000001   # SUBT: ein Zeichen
; 0007: 00000000000   # SUBT: E gleich E
; 0010: 00000000004   # INDX: = in abc=42
; 0011: 00000000000   # INDX: x nicht in abc
; 0012: 00000000002   # INDX: AN in BANANE
; 0013: 00000000004   # INDX: ANE in BANANE
; 0014: 00000000000   # INDX: A gross nicht in banane
; 0015: 00000000002   # INDX: Leerzeichen in a b c
; 0016: 00000000001   # INDX: ganzer Text
; 0017: 00000000000   # UPLO: UPPER Ab c-9z gleich AB C-9Z
; 0020: 00000000007   # UPLO: Laenge 7
; 0021: 00000000000   # UPLO: LOWER gleich ab c-9z
; 0022: 00000000000   # UPLO: UPPER mit Ziel gleich Quelle
; 0023: 00000000003   # UPLO: Umlaut zaehlt 2 Bytes
; 0024: 00000000000   # UPLO: Umlaut unveraendert
; 0025: 00000000002   # STRV: abc gegen abd
; 0026: 00000000001   # STRV: abd gegen abc
; 0027: 00000000000   # STRV: abc gegen abc
; 0030: 00000000002   # STRV: ab gegen abc
; 0031: 00000000001   # STRV: abc gegen ab
; 0032: 00000000000   # STRV: a b gegen a b
; 0033: 00000000001   # STRV: a b gegen a  b
; 0034: 00000000002   # STRV: B gegen a
;#PRUEFE-ENDE
