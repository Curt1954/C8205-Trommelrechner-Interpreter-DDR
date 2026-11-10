;aufrufnr.asm - Test von $AUFRUFNR (Aufrufnummer im Makroprozessor, Assemblerdokumentation 4.29, ab c82ass 1.01-024)
;#DOK-0001 Test $AUFRUFNR: eigene Nummer je Aufruf, verschachtelter Aufruf, Nummer als Parameter weitergereicht, $AUFRUFNR in $CALC
;#PROT STUFE=2
                start                           ; Zaehlung beginnt bei 0000
                000     haupt                   ; Zelle 0000: Sprung zum Hauptprogramm
; INNEN: legt den uebergebenen Parameter (Nummer des aeusseren Aufrufs) und die eigene Nummer ab
INNEN:          MACRO aussen
                dw      $aussen                 ; Nummer des aeusseren Aufrufs (als Parameter weitergereicht)
                dw      $AUFRUFNR               ; eigene Nummer des inneren Aufrufs
                MEND
; AUSSEN: eigene Nummer, dann der verschachtelte Aufruf (bekommt die naechste Nummer), danach wieder die eigene
AUSSEN:         MACRO
                dw      $AUFRUFNR               ; eigene Nummer
                INNEN   $AUFRUFNR               ; innerer Aufruf mit eigener Nummer; Parameter ist die aeussere Nummer
                dw      $AUFRUFNR               ; nach der Rueckkehr gilt wieder die eigene Nummer
                MEND
; ZEHN: $AUFRUFNR im Rechenausdruck
ZEHN:           MACRO
                dw      $CALC($AUFRUFNR*10)     ; Nummer mal 10
                MEND
                AUSSEN                          ; Aufruf 1: Zellen 0001 bis 0004 = 1, 1, 2, 1 (INNEN ist Aufruf 2)
                AUSSEN                          ; Aufruf 3: Zellen 0005 bis 0010 = 3, 3, 4, 3 (INNEN ist Aufruf 4)
                ZEHN                            ; Aufruf 5: Zelle 0011 = 50 = 062 oktal
haupt:          020     0                       ; Zelle 0012: Halt
ende:           end

; Sollwerte von Hand hergeleitet (siehe Kommentare der Aufrufe); Halt auf 0012 oktal, BZ danach 0013
;#PRUEFE-START
; BZ=0013 US=1
; 0001: 00000000001
; 0002: 00000000001
; 0003: 00000000002
; 0004: 00000000001
; 0005: 00000000003
; 0006: 00000000003
; 0007: 00000000004
; 0010: 00000000003
; 0011: 00000000062
;#PRUEFE-ENDE
