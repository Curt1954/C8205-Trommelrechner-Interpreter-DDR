; makros.asm - Test der Makros in c82ass.makros: SCHIEBE_LI und SCHIEBE_RE (alle 64 Faelle), ARRAY_ADD, ARRAY_SUB,
;              ARRAY_SWAP (Regression nach dw 0 -> db 1), ERHOEHE, ZEIGER_NAECHST
; Empfehlung (001): Testprogramm ab 0000; SCHIEBE_* ueberschreiben Zellen der Arbeitsspur 7640 (Festlegung 025/026).
;#DOK-0001 Test der Makros SCHIEBE_LI, SCHIEBE_RE, ARRAY_ADD, ARRAY_SUB, ARRAY_SWAP, ERHOEHE, ZEIGER_NAECHST
;#PROT STUFE=2
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          ARRAY_ADD afeld i1 badd   ; badd := 210 feld[1]
                211     eins         ; AC := 1
badd:           db      1            ; hier steht der Additionsbefehl 210 feld[1]: AC := 1 + 7
                240     eadd         ; eadd := 8
                ARRAY_SUB afeld i2 bsub   ; bsub := 220 feld[2]
                211     hundert      ; AC := 64
bsub:           db      1            ; hier steht der Subtraktionsbefehl 220 feld[2]: AC := 64 - 9
                240     esub         ; esub := 55
                ARRAY_SWAP afeld i0 i2 tmp ; feld[0] und feld[2] vertauschen
                240     eswap        ; AC nach ARRAY_SWAP (= altes feld[0]) sichern
                ERHOEHE idx          ; idx := idx + 1 Adresseinheit
                ZEIGER_NAECHST zeiger ; zeiger := zeiger + 1 Adresseinheit
                211     eins         ; AC := 1
                SCHIEBE_LI 1        ; AC := 1 mal 2 hoch 1
                240     l01          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 2        ; AC := 1 mal 2 hoch 2
                240     l02          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 3        ; AC := 1 mal 2 hoch 3
                240     l03          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 4        ; AC := 1 mal 2 hoch 4
                240     l04          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 5        ; AC := 1 mal 2 hoch 5
                240     l05          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 6        ; AC := 1 mal 2 hoch 6
                240     l06          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 7        ; AC := 1 mal 2 hoch 7
                240     l07          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 8        ; AC := 1 mal 2 hoch 8
                240     l08          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 9        ; AC := 1 mal 2 hoch 9
                240     l09          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 10        ; AC := 1 mal 2 hoch 10
                240     l10          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 11        ; AC := 1 mal 2 hoch 11
                240     l11          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 12        ; AC := 1 mal 2 hoch 12
                240     l12          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 13        ; AC := 1 mal 2 hoch 13
                240     l13          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 14        ; AC := 1 mal 2 hoch 14
                240     l14          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 15        ; AC := 1 mal 2 hoch 15
                240     l15          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 16        ; AC := 1 mal 2 hoch 16
                240     l16          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 17        ; AC := 1 mal 2 hoch 17
                240     l17          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 18        ; AC := 1 mal 2 hoch 18
                240     l18          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 19        ; AC := 1 mal 2 hoch 19
                240     l19          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 20        ; AC := 1 mal 2 hoch 20
                240     l20          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 21        ; AC := 1 mal 2 hoch 21
                240     l21          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 22        ; AC := 1 mal 2 hoch 22
                240     l22          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 23        ; AC := 1 mal 2 hoch 23
                240     l23          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 24        ; AC := 1 mal 2 hoch 24
                240     l24          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 25        ; AC := 1 mal 2 hoch 25
                240     l25          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 26        ; AC := 1 mal 2 hoch 26
                240     l26          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 27        ; AC := 1 mal 2 hoch 27
                240     l27          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 28        ; AC := 1 mal 2 hoch 28
                240     l28          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 29        ; AC := 1 mal 2 hoch 29
                240     l29          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 30        ; AC := 1 mal 2 hoch 30
                240     l30          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 31        ; AC := 1 mal 2 hoch 31
                240     l31          ; Ergebnis ablegen
                211     eins         ; AC := 1
                SCHIEBE_LI 32        ; AC := 1 mal 2 hoch 32
                240     l32          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 1        ; AC := 2 hoch 31, 1 mal rechts
                240     r01          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 2        ; AC := 2 hoch 31, 2 mal rechts
                240     r02          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 3        ; AC := 2 hoch 31, 3 mal rechts
                240     r03          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 4        ; AC := 2 hoch 31, 4 mal rechts
                240     r04          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 5        ; AC := 2 hoch 31, 5 mal rechts
                240     r05          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 6        ; AC := 2 hoch 31, 6 mal rechts
                240     r06          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 7        ; AC := 2 hoch 31, 7 mal rechts
                240     r07          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 8        ; AC := 2 hoch 31, 8 mal rechts
                240     r08          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 9        ; AC := 2 hoch 31, 9 mal rechts
                240     r09          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 10        ; AC := 2 hoch 31, 10 mal rechts
                240     r10          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 11        ; AC := 2 hoch 31, 11 mal rechts
                240     r11          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 12        ; AC := 2 hoch 31, 12 mal rechts
                240     r12          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 13        ; AC := 2 hoch 31, 13 mal rechts
                240     r13          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 14        ; AC := 2 hoch 31, 14 mal rechts
                240     r14          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 15        ; AC := 2 hoch 31, 15 mal rechts
                240     r15          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 16        ; AC := 2 hoch 31, 16 mal rechts
                240     r16          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 17        ; AC := 2 hoch 31, 17 mal rechts
                240     r17          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 18        ; AC := 2 hoch 31, 18 mal rechts
                240     r18          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 19        ; AC := 2 hoch 31, 19 mal rechts
                240     r19          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 20        ; AC := 2 hoch 31, 20 mal rechts
                240     r20          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 21        ; AC := 2 hoch 31, 21 mal rechts
                240     r21          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 22        ; AC := 2 hoch 31, 22 mal rechts
                240     r22          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 23        ; AC := 2 hoch 31, 23 mal rechts
                240     r23          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 24        ; AC := 2 hoch 31, 24 mal rechts
                240     r24          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 25        ; AC := 2 hoch 31, 25 mal rechts
                240     r25          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 26        ; AC := 2 hoch 31, 26 mal rechts
                240     r26          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 27        ; AC := 2 hoch 31, 27 mal rechts
                240     r27          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 28        ; AC := 2 hoch 31, 28 mal rechts
                240     r28          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 29        ; AC := 2 hoch 31, 29 mal rechts
                240     r29          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 30        ; AC := 2 hoch 31, 30 mal rechts
                240     r30          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 31        ; AC := 2 hoch 31, 31 mal rechts
                240     r31          ; Ergebnis ablegen
                211     bit31        ; AC := 2 hoch 31
                SCHIEBE_RE 32        ; AC := 2 hoch 31, 32 mal rechts
                240     r32          ; Ergebnis ablegen
halt:           020     0            ; Halt
eins:           dw      01           ; Konstante 1 (Ausgang fuer SCHIEBE_LI)
bit31:          dw      020000000000 ; Konstante 2 hoch 31 (Ausgang fuer SCHIEBE_RE)
feld:           dw      05           ; feld[0] = 5
                dw      07           ; feld[1] = 7
                dw      011          ; feld[2] = 9
afeld:          da      feld         ; Feldadresse im Adressfeld ($1 der ARRAY-Makros, nicht das Feld selbst)
i0:             dw      0            ; Index 0 in Adresseinheiten
i1:             dw      01000        ; Index 1 in Adresseinheiten
i2:             dw      02000        ; Index 2 in Adresseinheiten
hundert:        dw      0100         ; Konstante 64 (Minuend fuer ARRAY_SUB)
zeiger:         dw      03000        ; Zeigerzelle, Wert 3 Adresseinheiten
idx:            dw      05000        ; Indexzelle, Wert 5 Adresseinheiten
tmp:            db      1            ; Hilfszelle von ARRAY_SWAP
eadd:           db      1            ; Ergebnis ARRAY_ADD
esub:           db      1            ; Ergebnis ARRAY_SUB
eswap:          db      1            ; AC nach ARRAY_SWAP
l01:            db      1            ; Ergebnis SCHIEBE_LI 1
l02:            db      1            ; Ergebnis SCHIEBE_LI 2
l03:            db      1            ; Ergebnis SCHIEBE_LI 3
l04:            db      1            ; Ergebnis SCHIEBE_LI 4
l05:            db      1            ; Ergebnis SCHIEBE_LI 5
l06:            db      1            ; Ergebnis SCHIEBE_LI 6
l07:            db      1            ; Ergebnis SCHIEBE_LI 7
l08:            db      1            ; Ergebnis SCHIEBE_LI 8
l09:            db      1            ; Ergebnis SCHIEBE_LI 9
l10:            db      1            ; Ergebnis SCHIEBE_LI 10
l11:            db      1            ; Ergebnis SCHIEBE_LI 11
l12:            db      1            ; Ergebnis SCHIEBE_LI 12
l13:            db      1            ; Ergebnis SCHIEBE_LI 13
l14:            db      1            ; Ergebnis SCHIEBE_LI 14
l15:            db      1            ; Ergebnis SCHIEBE_LI 15
l16:            db      1            ; Ergebnis SCHIEBE_LI 16
l17:            db      1            ; Ergebnis SCHIEBE_LI 17
l18:            db      1            ; Ergebnis SCHIEBE_LI 18
l19:            db      1            ; Ergebnis SCHIEBE_LI 19
l20:            db      1            ; Ergebnis SCHIEBE_LI 20
l21:            db      1            ; Ergebnis SCHIEBE_LI 21
l22:            db      1            ; Ergebnis SCHIEBE_LI 22
l23:            db      1            ; Ergebnis SCHIEBE_LI 23
l24:            db      1            ; Ergebnis SCHIEBE_LI 24
l25:            db      1            ; Ergebnis SCHIEBE_LI 25
l26:            db      1            ; Ergebnis SCHIEBE_LI 26
l27:            db      1            ; Ergebnis SCHIEBE_LI 27
l28:            db      1            ; Ergebnis SCHIEBE_LI 28
l29:            db      1            ; Ergebnis SCHIEBE_LI 29
l30:            db      1            ; Ergebnis SCHIEBE_LI 30
l31:            db      1            ; Ergebnis SCHIEBE_LI 31
l32:            db      1            ; Ergebnis SCHIEBE_LI 32
r01:            db      1            ; Ergebnis SCHIEBE_RE 1
r02:            db      1            ; Ergebnis SCHIEBE_RE 2
r03:            db      1            ; Ergebnis SCHIEBE_RE 3
r04:            db      1            ; Ergebnis SCHIEBE_RE 4
r05:            db      1            ; Ergebnis SCHIEBE_RE 5
r06:            db      1            ; Ergebnis SCHIEBE_RE 6
r07:            db      1            ; Ergebnis SCHIEBE_RE 7
r08:            db      1            ; Ergebnis SCHIEBE_RE 8
r09:            db      1            ; Ergebnis SCHIEBE_RE 9
r10:            db      1            ; Ergebnis SCHIEBE_RE 10
r11:            db      1            ; Ergebnis SCHIEBE_RE 11
r12:            db      1            ; Ergebnis SCHIEBE_RE 12
r13:            db      1            ; Ergebnis SCHIEBE_RE 13
r14:            db      1            ; Ergebnis SCHIEBE_RE 14
r15:            db      1            ; Ergebnis SCHIEBE_RE 15
r16:            db      1            ; Ergebnis SCHIEBE_RE 16
r17:            db      1            ; Ergebnis SCHIEBE_RE 17
r18:            db      1            ; Ergebnis SCHIEBE_RE 18
r19:            db      1            ; Ergebnis SCHIEBE_RE 19
r20:            db      1            ; Ergebnis SCHIEBE_RE 20
r21:            db      1            ; Ergebnis SCHIEBE_RE 21
r22:            db      1            ; Ergebnis SCHIEBE_RE 22
r23:            db      1            ; Ergebnis SCHIEBE_RE 23
r24:            db      1            ; Ergebnis SCHIEBE_RE 24
r25:            db      1            ; Ergebnis SCHIEBE_RE 25
r26:            db      1            ; Ergebnis SCHIEBE_RE 26
r27:            db      1            ; Ergebnis SCHIEBE_RE 27
r28:            db      1            ; Ergebnis SCHIEBE_RE 28
r29:            db      1            ; Ergebnis SCHIEBE_RE 29
r30:            db      1            ; Ergebnis SCHIEBE_RE 30
r31:            db      1            ; Ergebnis SCHIEBE_RE 31
r32:            db      1            ; Ergebnis SCHIEBE_RE 32
ende:           end
;
; Sollwerte von Hand hergeleitet (Zelladressen aus der .sym):
; eadd = 1 + feld[1] = 1 + 7 = 8 = 010. esub = 64 - feld[2] = 64 - 9 = 55 = 067 (feld[2] vor dem Tausch).
; ARRAY_SWAP vertauscht feld[0]=5 und feld[2]=9: feld = 9, 7, 5; tmp = 5 (altes feld[0]); AC danach = 5 (zuletzt wurde das alte feld[0] gespeichert, AC := tmp).
; ERHOEHE idx: 5 + 1 Adresseinheit = 06000. ZEIGER_NAECHST zeiger: 3 + 1 = 04000.
; SCHIEBE_LI n: 1 mal 2 hoch n (n = 1..32, 2 hoch 32 = 040000000000). SCHIEBE_RE n: 2 hoch 31 durch 2 hoch n = 2 hoch (31-n), bei n = 32 ergibt sich 0 (logische Rechtsverschiebung).
;#PRUEFE-START
; BZ=0353 US=1
; 0370: 00000000010   # eadd
; 0371: 00000000067   # esub
; 0372: 00000000005   # eswap
; 0367: 00000000005   # tmp
; 0355: 00000000011   # feld[0]
; 0356: 00000000007   # feld[1]
; 0357: 00000000005   # feld[2]
; 0366: 00000006000   # idx
; 0365: 00000004000   # zeiger
; 0373: 00000000002   # l01 = SCHIEBE_LI 1
; 0374: 00000000004   # l02 = SCHIEBE_LI 2
; 0375: 00000000010   # l03 = SCHIEBE_LI 3
; 0376: 00000000020   # l04 = SCHIEBE_LI 4
; 0377: 00000000040   # l05 = SCHIEBE_LI 5
; 0400: 00000000100   # l06 = SCHIEBE_LI 6
; 0401: 00000000200   # l07 = SCHIEBE_LI 7
; 0402: 00000000400   # l08 = SCHIEBE_LI 8
; 0403: 00000001000   # l09 = SCHIEBE_LI 9
; 0404: 00000002000   # l10 = SCHIEBE_LI 10
; 0405: 00000004000   # l11 = SCHIEBE_LI 11
; 0406: 00000010000   # l12 = SCHIEBE_LI 12
; 0407: 00000020000   # l13 = SCHIEBE_LI 13
; 0410: 00000040000   # l14 = SCHIEBE_LI 14
; 0411: 00000100000   # l15 = SCHIEBE_LI 15
; 0412: 00000200000   # l16 = SCHIEBE_LI 16
; 0413: 00000400000   # l17 = SCHIEBE_LI 17
; 0414: 00001000000   # l18 = SCHIEBE_LI 18
; 0415: 00002000000   # l19 = SCHIEBE_LI 19
; 0416: 00004000000   # l20 = SCHIEBE_LI 20
; 0417: 00010000000   # l21 = SCHIEBE_LI 21
; 0420: 00020000000   # l22 = SCHIEBE_LI 22
; 0421: 00040000000   # l23 = SCHIEBE_LI 23
; 0422: 00100000000   # l24 = SCHIEBE_LI 24
; 0423: 00200000000   # l25 = SCHIEBE_LI 25
; 0424: 00400000000   # l26 = SCHIEBE_LI 26
; 0425: 01000000000   # l27 = SCHIEBE_LI 27
; 0426: 02000000000   # l28 = SCHIEBE_LI 28
; 0427: 04000000000   # l29 = SCHIEBE_LI 29
; 0430: 10000000000   # l30 = SCHIEBE_LI 30
; 0431: 20000000000   # l31 = SCHIEBE_LI 31
; 0432: 40000000000   # l32 = SCHIEBE_LI 32
; 0433: 10000000000   # r01 = SCHIEBE_RE 1
; 0434: 04000000000   # r02 = SCHIEBE_RE 2
; 0435: 02000000000   # r03 = SCHIEBE_RE 3
; 0436: 01000000000   # r04 = SCHIEBE_RE 4
; 0437: 00400000000   # r05 = SCHIEBE_RE 5
; 0440: 00200000000   # r06 = SCHIEBE_RE 6
; 0441: 00100000000   # r07 = SCHIEBE_RE 7
; 0442: 00040000000   # r08 = SCHIEBE_RE 8
; 0443: 00020000000   # r09 = SCHIEBE_RE 9
; 0444: 00010000000   # r10 = SCHIEBE_RE 10
; 0445: 00004000000   # r11 = SCHIEBE_RE 11
; 0446: 00002000000   # r12 = SCHIEBE_RE 12
; 0447: 00001000000   # r13 = SCHIEBE_RE 13
; 0450: 00000400000   # r14 = SCHIEBE_RE 14
; 0451: 00000200000   # r15 = SCHIEBE_RE 15
; 0452: 00000100000   # r16 = SCHIEBE_RE 16
; 0453: 00000040000   # r17 = SCHIEBE_RE 17
; 0454: 00000020000   # r18 = SCHIEBE_RE 18
; 0455: 00000010000   # r19 = SCHIEBE_RE 19
; 0456: 00000004000   # r20 = SCHIEBE_RE 20
; 0457: 00000002000   # r21 = SCHIEBE_RE 21
; 0460: 00000001000   # r22 = SCHIEBE_RE 22
; 0461: 00000000400   # r23 = SCHIEBE_RE 23
; 0462: 00000000200   # r24 = SCHIEBE_RE 24
; 0463: 00000000100   # r25 = SCHIEBE_RE 25
; 0464: 00000000040   # r26 = SCHIEBE_RE 26
; 0465: 00000000020   # r27 = SCHIEBE_RE 27
; 0466: 00000000010   # r28 = SCHIEBE_RE 28
; 0467: 00000000004   # r29 = SCHIEBE_RE 29
; 0470: 00000000002   # r30 = SCHIEBE_RE 30
; 0471: 00000000001   # r31 = SCHIEBE_RE 31
; 0472: 00000000000   # r32 = SCHIEBE_RE 32
;#PRUEFE-ENDE
