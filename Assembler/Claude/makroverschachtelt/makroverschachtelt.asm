; makroverschachtelt.asm - Test verschachtelter Makroaufrufe in Quelltextreihenfolge (Assemblerdokumentation 4.7 und 4.15)
;#DOK-0001 Test: $SET/$INC/$V wirken bei verschachtelten Aufrufen in Quelltextreihenfolge; ein Makro-Label als Parameter an ein verschachteltes Makro
;#PROT STUFE=2
ZINIT:          MACRO
                $SET n 0
                MEND
; INNER erzeugt den Stand der Variablen n im Augenblick seines Aufrufs
INNER:          MACRO
                dw      $V(n)        ; Stand von n beim Aufruf
                MEND
; OUT1: erst erhoehen, dann INNER aufrufen
OUT1:           MACRO
                $INC n
                INNER
                MEND
; OUT2: erst INNER aufrufen, dann erhoehen (Reihenfolge innerhalb des Rumpfes)
OUT2:           MACRO
                INNER
                $INC n
                MEND
; INN springt zum uebergebenen Label und hat selbst ein Label gleicher Nummer
INN:            MACRO 1
                000     $1           ; Sprung zum uebergebenen Label
                240     fehler       ; wird uebersprungen
ML0001%:        211     eins         ; eigenes Label (gleiche Nummer wie in AUS)
                MEND
; AUS ruft INN mit dem eigenen Label ML0001% auf; der Sprung muss in AUS landen, nicht in INN
AUS:            MACRO
                INN     ML0001%
                240     fehler       ; wird uebersprungen
ML0001%:        211     eins         ; AC := 1
                240     treffer      ; treffer := 1
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                ZINIT                ; kein Code: n := 0
                OUT1                 ; Zelle 0001: n = 1, INNER erzeugt 1
                OUT1                 ; Zelle 0002: n = 2, INNER erzeugt 2
                OUT2                 ; Zelle 0003: INNER erzeugt 2, danach n = 3
                OUT2                 ; Zelle 0004: INNER erzeugt 3, danach n = 4
                INNER                ; Zelle 0005: INNER erzeugt 4
eins:           dw      1            ; Zelle 0006: Konstante 1
fehler:         dw      0            ; Zelle 0007: bleibt 0
treffer:        dw      0            ; Zelle 0010: wird 1
haupt:          AUS                  ; Zellen 0011 bis 0016: INN (000, 240, 211) und AUS (240, 211, 240)
                164     0001         ; Zelle 0017: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0020: Halt
ende:           end

; Sollwerte von Hand hergeleitet. Der Sprung auf 0011 geht zum Label von AUS (Zelle 0015: 211 eins), AC = 1, treffer = 1,
; die Zellen 0012 (INN: 240 fehler), 0013 (INN: Label), 0014 (AUS: 240 fehler) werden uebersprungen bzw. nicht erreicht: fehler = 0.
; Halt auf 0020, BZ danach 0021.
;#PRUEFE-START
; BZ=0021 AC=00000000001 US=1
; 0001: 00000000001   # OUT1 Nr. 1: n = 1
; 0002: 00000000002   # OUT1 Nr. 2: n = 2
; 0003: 00000000002   # OUT2 Nr. 1: INNER vor dem Erhoehen: 2
; 0004: 00000000003   # OUT2 Nr. 2: 3
; 0005: 00000000004   # INNER am Schluss: 4
; 0007: 00000000000   # fehler
; 0010: 00000000001   # treffer
;#PRUEFE-ENDE
