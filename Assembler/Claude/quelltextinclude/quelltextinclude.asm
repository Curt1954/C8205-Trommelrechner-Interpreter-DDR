; quelltextinclude.asm - $INCLUDE im Quelltext (c82ass ab 1.01-009, Doku 4.14): Datenteil und Unterprogramm-Bibliothek
; liegen in eigenen Dateien im Unterordner teile/; die Bibliothek bindet ihrerseits eine zweite Datei ein.
; Ablauf: erg := wert (017); verdopple (036); plus1 (037); plus3 (042).
;#DOK-0001 Test fuer $INCLUDE im Quelltext: Datenteil, UP-Bibliothek und verschachteltes Include
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                $INCLUDE teile/daten.inc ; Datenteil: wert, erg, eins, rueck, drei (Zellen 0001 bis 0005)
haupt:          211     wert         ; AC := wert (017)
                240     erg          ; erg := AC
                025     verdopple    ; UP aus teile/bibl.inc: erg := erg + erg
                025     plus1        ; UP aus teile/bibl2.inc (dort eingebunden): erg := erg + 1
                025     plus3        ; UP aus teile/bibl2.inc: erg := erg + drei
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
                $INCLUDE teile/bibl.inc ; Bibliothek: verdopple, danach (verschachtelt) plus1 und plus3
ende:           end

; Sollwerte von Hand hergeleitet: Halt auf 0014; erg = 017 + 017 = 036, + 1 = 037, + 3 = 042 (oktal).
; Zelle = Operand * 01000 + Operationscode; rueck haelt nach dem letzten 025 (auf 0012) das Wort 000 0013.
;#PRUEFE-START
; BZ=0015 AC=00000000042 US=1
; 0000: 00000006000   # 000 haupt
; 0001: 00000000017   # wert
; 0002: 00000000042   # erg
; 0003: 00000000001   # eins
; 0004: 00000013000   # rueck
; 0005: 00000000003   # drei
; 0006: 00000001211   # 211 wert
; 0007: 00000002240   # 240 erg
; 0010: 00000015025   # 025 verdopple
; 0011: 00000022025   # 025 plus1
; 0012: 00000027025   # 025 plus3
; 0013: 00000001164   # 164 0001
; 0014: 00000000020   # 020 0
; 0015: 00000004240   # verdopple: 240 rueck
; 0016: 00000002211   # 211 erg
; 0017: 00000002210   # 210 erg
; 0020: 00000002240   # 240 erg
; 0021: 00000004000   # 000 rueck
; 0022: 00000004240   # plus1: 240 rueck
; 0023: 00000002211   # 211 erg
; 0024: 00000003210   # 210 eins
; 0025: 00000002240   # 240 erg
; 0026: 00000004000   # 000 rueck
; 0027: 00000004240   # plus3: 240 rueck
; 0030: 00000002211   # 211 erg
; 0031: 00000005210   # 210 drei
; 0032: 00000002240   # 240 erg
; 0033: 00000004000   # 000 rueck
;#PRUEFE-ENDE
