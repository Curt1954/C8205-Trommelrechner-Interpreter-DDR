; makromend.asm - Test: Das Wort MEND in einem Kommentar der Makrodatei beendet das Makro nicht (Assemblerdokumentation 4)
;#DOK-0001 Test: Makrodatei mit "AMEND", "RECOMMEND" und "MENDEL" in Kommentaren; das Makro LADEERG wird vollstaendig gelesen
;#PROT STUFE=2
;#MACRODATEI1=macro_mend.macro
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
wert:           dw      017          ; Zelle 0001: Konstante
erg:            dw      0            ; Zelle 0002: Ergebnis (initialisiert)
haupt:          LADEERG              ; Zellen 0003 und 0004: 211 wert, 240 erg
                164     0001         ; Zelle 0005: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0006: Halt
ende:           end

; Sollwerte von Hand hergeleitet. Wie mini.asm: Zelle 0001 (017) wird nach Zelle 0002 kopiert; Halt auf 0006, BZ danach 0007.
;#PRUEFE-START
; BZ=0007 AC=00000000017 US=1
; 0002: 00000000017   # erg
;#PRUEFE-ENDE
