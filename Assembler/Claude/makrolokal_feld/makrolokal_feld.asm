; makrolokal_feld.asm - Test von $DIM mit ;#MAKROLOKAL=1: lokales Feld im Makroaufruf, globales Feld mit $GLOBAL (Assemblerdokumentation 4.31)
;#DOK-0001 Test lokale und globale Felder: $DIM lokal, $GLOBAL tab vor $DIM tab n macht das Feld global, ein lokales Feld verdeckt das globale
;#PROT STUFE=2
;#MAKROLOKAL=1
; LOKAL: $DIM legt das Feld a lokal an; s ist lokal; erzeugt die Summe a(1) + a(2)
LOKAL:          MACRO
                $DIM a 3
                $SET a(1) 5
                $SET a(2) 7
                $SET s 0
                $INC s $V(a(1))
                $INC s $V(a(2))
                dw      $V(s)           ; 5 + 7 = 12
                MEND
; GTAB: globales Feld tab mit zwei Elementen ($GLOBAL zuerst, dann $DIM)
GTAB:           MACRO
                $GLOBAL tab
                $DIM tab 2
                $SET tab(0) 11
                $SET tab(1) 22
                MEND
; LTAB: liest das globale Feld tab (mit $GLOBAL vereinbart)
LTAB:           MACRO
                $GLOBAL tab
                dw      $V(tab(0))      ; 11
                dw      $V(tab(1))      ; 22
                MEND
; VERD: ein lokales Feld tab verdeckt das globale; das globale bleibt unberuehrt
VERD:           MACRO
                $DIM tab 3
                $SET tab(2) 99
                dw      $V(tab(2))      ; 99
                dw      $V(tab(0))      ; 0 (Element des lokalen Feldes)
                MEND
                $SET quelltext 1     ; nur damit der Quelltext ausgewertet wird: $V und $DEFINED im Quelltext brauchen eine $-Zeile (Doku 4.1)
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                LOKAL                ; Zelle 0001: 12
                GTAB                 ; kein Code
                LTAB                 ; Zellen 0002 und 0003: 11, 22
                VERD                 ; Zellen 0004 und 0005: 99, 0
                LTAB                 ; Zellen 0006 und 0007: 11, 22 (globales Feld unveraendert)
                dw      $DEFINED(a)  ; Zelle 0010: 0 (lokales Feld a ist weg)
                dw      $DEFINED(tab)   ; Zelle 0011: 1
haupt:          164     0001         ; Zelle 0012: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0013: Halt (Zelle 11 dezimal)
ende:           end

; Sollwerte von Hand hergeleitet (Zellen dezimal gezaehlt, Adressen und Werte oktal): 12 dezimal = 014; 11 = 013; 22 = 026; 99 = 0143.
; haupt liegt auf Zelle 10 dezimal (oktal 0012), der Halt auf Zelle 11 dezimal (oktal 0013), BZ danach 0014.
;#PRUEFE-START
; BZ=0014 US=1
; 0001: 00000000014   # LOKAL: 12
; 0002: 00000000013   # LTAB: tab(0) = 11
; 0003: 00000000026   # LTAB: tab(1) = 22
; 0004: 00000000143   # VERD: lokales tab(2) = 99
; 0005: 00000000000   # VERD: lokales tab(0) = 0
; 0006: 00000000013   # LTAB: globales tab(0) unveraendert
; 0007: 00000000026   # LTAB: globales tab(1) unveraendert
; 0010: 00000000000   # $DEFINED(a) = 0
; 0011: 00000000001   # $DEFINED(tab) = 1
;#PRUEFE-ENDE
