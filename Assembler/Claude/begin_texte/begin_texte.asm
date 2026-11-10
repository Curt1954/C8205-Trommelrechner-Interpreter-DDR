; begin_texte.asm - Anweisungen, die Speicher belegen, zwischen begin und bend: dz, da, dto, dtm, dt, kat4 (Assemblerdokumentation 3.3.12)
                start                    ; Zaehlung beginnt bei 0000
                000     haupt            ; Zelle 0000: Sprung zum Hauptprogramm
                begin                    ; Block ohne Schluesselwort: bleibt an seiner Stelle
tab:            dz      $wrzl            ; Zelle 0001: Zeilenschaltung, Wort 0000 2720 030
                da      tab              ; Zelle 0002: Adresse von tab (1), um 9 Bit verschoben
                dto     1                ; Zelle 0003: Ziffer 1 ohne Umschaltzeichen
                dtm     1                ; Zellen 0004 und 0005: Umschaltzeichen auf KB, dann Ziffer 1
                dt      1                ; Zelle 0006: Ziffer 1 im Zustand KB des vorangehenden dtm
                kat4    1                ; Zelle 0007: komprimierter Text (nur Uebersetzung, Zellenwert nicht geprueft)
                bend                     ; Ende des Blocks
erg:            dw      0                ; Zelle 0010: Ergebnis
haupt:          211     tab              ; Zelle 0011: AC := Wort der Zelle 0001
                240     erg              ; Zelle 0012: (erg) := AC
                020     0                ; Zelle 0013: Halt
ende:           end

; Sollwerte von Hand hergeleitet: dz $wrzl hat die Ausgabeadresse 2720, Wort 0000 2720 030 = 00002720030 (Tabelle 2, Abschnitt 3.3.6).
; da tab: tab liegt auf Zelle 1, um 9 Bit verschoben = 01000 = 00000001000. Ziffer 1: Ausgabeadresse 0010, Wort 00000010030 (nach Kodetabelle).
; Ziffern gehoeren zum Zustand KB: dtm 1 setzt vor die Ziffer das Umschaltzeichen $inkb (Ausgabeadresse 1170), Wort 00001170030 (Tabelle 2).
; Halt auf Zelle 0013, BZ = 0014; der AC enthaelt das Wort der Zelle 0001.
;#PRUEFE-START
; BZ=0014 AC=00002720030 US=1
; 0001: 00002720030   # dz $wrzl
; 0002: 00000001000   # da tab
; 0003: 00000010030   # dto 1
; 0004: 00001170030   # dtm 1: Umschaltzeichen KB
; 0005: 00000010030   # dtm 1: Ziffer 1
; 0006: 00000010030   # dt 1
; 0010: 00002720030   # erg
;#PRUEFE-ENDE
