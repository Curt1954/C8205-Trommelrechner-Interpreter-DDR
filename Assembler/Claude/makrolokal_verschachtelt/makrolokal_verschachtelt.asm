; makrolokal_verschachtelt.asm - Test von ;#MAKROLOKAL=1 bei verschachtelten Aufrufen: ein aufgerufenes Makro sieht die lokalen Variablen des aufrufenden nicht (Assemblerdokumentation 4.31)
;#DOK-0001 Test verschachtelte Aufrufe: INNEN hat sein eigenes x, AUSSEN behaelt x und z, Werte gehen nur ueber Parameter
;#PROT STUFE=2
;#MAKROLOKAL=1
; INNEN: eigenes x und y (lokal); das z von AUSSEN ist hier nicht sichtbar
INNEN:          MACRO 1
                $SET x $1               ; lokal in INNEN, das x von AUSSEN bleibt unberuehrt
                $SET y $CALC($V(x)*2)
                dw      $V(y)           ; 2 * $1
                dw      $DEFINED(z)     ; 0: z gehoert AUSSEN
                MEND
; AUSSEN: eigenes x und z (lokal); ruft INNEN auf
AUSSEN:         MACRO
                $SET x 1
                $SET z 5
                INNEN   20              ; Zellen: 40 und 0
                dw      $V(x)           ; 1: unveraendert nach der Rueckkehr
                dw      $V(z)           ; 5
                dw      $DEFINED(y)     ; 0: y gehoert INNEN
                MEND
                $SET quelltext 1     ; nur damit der Quelltext ausgewertet wird: $V und $DEFINED im Quelltext brauchen eine $-Zeile (Doku 4.1)
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                AUSSEN               ; Zellen 0001 bis 0005
                dw      $DEFINED(x)  ; Zelle 0006: 0 (nach dem Aufruf gibt es kein x)
haupt:          164     0001         ; Zelle 0007: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): INNEN 20: 2 * 20 = 40 dezimal = 050 oktal.
; haupt liegt auf Zelle 7, der Halt auf Zelle 8 (oktal 0010), BZ danach 0011.
;#PRUEFE-START
; BZ=0011 US=1
; 0001: 00000000050   # INNEN: y = 40
; 0002: 00000000000   # INNEN: $DEFINED(z) = 0
; 0003: 00000000001   # AUSSEN: x unveraendert = 1
; 0004: 00000000005   # AUSSEN: z = 5
; 0005: 00000000000   # AUSSEN: $DEFINED(y) = 0
; 0006: 00000000000   # Quelltext: $DEFINED(x) = 0
;#PRUEFE-ENDE
