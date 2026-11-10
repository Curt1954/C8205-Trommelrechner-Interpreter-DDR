; makroattr3.asm - Attributabfragen in Makros aus einer Projektmakrodatei und im Quelltext (Assemblerdokumentation 4.23)
;#DOK-0001 Test Attributabfragen in Makros aus ;#MACRODATEI1: art, def; Marke aus einem Makro der Makrodatei ist kein Symbol des Quelltexts (A-11)
;#MACRODATEI1=makroattr3.macro
;#PROT STUFE=2
; Jeder Aufruf erzeugt genau ein Wort; hinter E= steht der von Hand hergeleitete Wert (dezimal), in der Reihenfolge der Zellen ab 0001.
Q_ART:    MACRO 1
          dw      $CALC(art($1))              ; Makro im Quelltext
          MEND
          start                               ; Zaehlung beginnt bei 0000
          000     haupt                       ; Zelle 0: Sprung zum Hauptprogramm
          MD_ART  a_abs                       ; E=1
          MD_ART  a_equ                       ; E=2
          MD_ART  a_dw                        ; E=4
          MD_ART  md_marke                    ; E=0
          MD_ERZ                              ; E=77
          MD_IF   a_abs                       ; E=1
          MD_IF   nix                         ; E=2
          MD_IF   md_marke                    ; E=2
          Q_ART   a_equ                       ; E=2
haupt:    164     0001                        ; Diagnoseausgabe (nur im Test)
          020     0                           ; Halt
a_dw:     dw      7                           ; Marke auf dw
ende:     end
a_abs:    abs     5                           ; abs-Symbol
a_equ:    equ     a_abs+3                     ; equ mit Symbol im Operanden
; Sollwerte von Hand hergeleitet (Zellen ab 0001 in Aufrufreihenfolge, Werte dezimal in den E=-Marken; hier oktal). 9 Woerter.
;#PRUEFE-START
; BZ=0014 US=1
; 0001: 00000000001   # MD_ART a_abs
; 0002: 00000000002   # MD_ART a_equ
; 0003: 00000000004   # MD_ART a_dw
; 0004: 00000000000   # MD_ART md_marke
; 0005: 00000000115   # MD_ERZ
; 0006: 00000000001   # MD_IF a_abs
; 0007: 00000000002   # MD_IF nix
; 0010: 00000000002   # MD_IF md_marke
; 0011: 00000000002   # Q_ART a_equ
;#PRUEFE-ENDE
