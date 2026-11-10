; zt_feld.asm - 32 Zufallskonstanten (Spur 0100) auf Zusatztrommel ZT1 (Datei zt2.txt), Adresse 01000 schreiben,
;   von dort in die Spur 0200 (32 Worte) zurueckholen, danach Halt. Nur mit Schalter --C8205Z.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          030     05200        ; Anwahl der Zusatztrommel ZT1 = Datei zt2.txt (5200 030 = 5k00 mit k = 2)
                dw      010000100601 ; Ausgabe 601: HT-Spur 0100 -> ZT1 Adresse 01000 (zzz0 = 1000)
                dw      010000200661 ; Eingabe 661: ZT1 Adresse 01000 -> HT-Spur 0200 (bbbb = 0200)
                164     0001         ; Diagnoseausgabe (nur im Test)
                020     0            ; Halt
                equ     0100         ; Feld beginnt auf Spur 0100 (Zellen 0100 bis 0137)
feld:
                dw      015445266246 ; Konstante 00
                dw      014103440540 ; Konstante 01
                dw      030762262267 ; Konstante 02
                dw      007144017147 ; Konstante 03
                dw      006210574202 ; Konstante 04
                dw      025510457602 ; Konstante 05
                dw      027012644630 ; Konstante 06
                dw      022220436026 ; Konstante 07
                dw      034102711536 ; Konstante 10
                dw      016145305463 ; Konstante 11
                dw      002234544765 ; Konstante 12
                dw      032101714277 ; Konstante 13
                dw      034736232166 ; Konstante 14
                dw      015055262427 ; Konstante 15
                dw      013504227406 ; Konstante 16
                dw      036102224705 ; Konstante 17
                dw      004473520431 ; Konstante 20
                dw      030417545042 ; Konstante 21
                dw      026041000163 ; Konstante 22
                dw      035462221617 ; Konstante 23
                dw      004245044735 ; Konstante 24
                dw      001511562157 ; Konstante 25
                dw      012662371210 ; Konstante 26
                dw      016075713202 ; Konstante 27
                dw      014352251230 ; Konstante 30
                dw      024000070303 ; Konstante 31
                dw      030176147121 ; Konstante 32
                dw      002337250776 ; Konstante 33
                dw      035045150050 ; Konstante 34
                dw      013352433661 ; Konstante 35
                dw      022512267717 ; Konstante 36
                dw      023731411727 ; Konstante 37
                equ     0200         ; Zielbereich Spur 0200 (Zellen 0200 bis 0237), 32 Worte
ziel:           dbn     040          ; 32 Zellen mit 0 vorbelegt
ende:           end

; Sollwerte von Hand: Feld 0100-0137 bleibt unveraendert; nach 661 steht dieselbe Folge auf 0200-0237.
;#PRUEFE-START
; US=1
; 0200: 15445266246
; 0201: 14103440540
; 0202: 30762262267
; 0203: 07144017147
; 0204: 06210574202
; 0205: 25510457602
; 0206: 27012644630
; 0207: 22220436026
; 0210: 34102711536
; 0211: 16145305463
; 0212: 02234544765
; 0213: 32101714277
; 0214: 34736232166
; 0215: 15055262427
; 0216: 13504227406
; 0217: 36102224705
; 0220: 04473520431
; 0221: 30417545042
; 0222: 26041000163
; 0223: 35462221617
; 0224: 04245044735
; 0225: 01511562157
; 0226: 12662371210
; 0227: 16075713202
; 0230: 14352251230
; 0231: 24000070303
; 0232: 30176147121
; 0233: 02337250776
; 0234: 35045150050
; 0235: 13352433661
; 0236: 22512267717
; 0237: 23731411727
;#PRUEFE-ENDE
