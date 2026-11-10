; makrovartext.asm - Test von Zeichenketten in $SET und $V(name), $V(#name) (Assemblerdokumentation 4.12)
;#DOK-0001 Test von $SET name "text": Text mit Leerzeichen, Parameter im Text, $V(#name) = Zeichenzahl, $V(name) in $IF
;#PROT STUFE=2
; T1 p: legt "ab <p> e" in t ab und erzeugt ein Wort mit der Zeichenzahl des Textes
T1:             MACRO 1
                $SET t "ab $1 e"
                dw      $V(#t)          ; Zeichenzahl des Textes in t
                MEND
; T2: setzt u auf einen Text, vergleicht ihn mit ja, erzeugt Wort 1 (ja) oder 2, dann ein Wort mit der Zeichenzahl
T2:             MACRO 1
                $SET u "$1"
                $IF $V(u) = ja
                dw      1               ; u ist ja
                $ELSE
                dw      2               ; u ist etwas anderes
                $ENDIF
                dw      $V(#u)          ; Zeichenzahl von u
                MEND
; T3: eine Variable wird erst Text, dann Zahl: $V liefert danach die Zahl
T3:             MACRO
                $SET w "abc"
                $SET w 7
                dw      $V(w)           ; Zahl 7
                MEND
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
                T1      "cd fg"      ; Zelle 0001: Text "ab cd fg e" hat 10 Zeichen = 012
                T2      ja           ; Zellen 0002, 0003: u = ja -> 1; 2 Zeichen
                T2      nein         ; Zellen 0004, 0005: u = nein -> 2; 4 Zeichen
                T3                   ; Zelle 0006: 7
haupt:          164     0001         ; Zelle 0007: Diagnoseausgabe (nur im Test)
                020     0            ; Zelle 0010: Halt
ende:           end

; Sollwerte von Hand hergeleitet: "ab cd fg e" = a b _ c d _ f g _ e = 10 Zeichen = 012; ja -> 1 und 2; nein -> 2 und 4; w = 7. Halt auf 0010, BZ danach 0011.
;#PRUEFE-START
; BZ=0011 US=1
; 0001: 00000000012   # 10 Zeichen
; 0002: 00000000001   # u = ja
; 0003: 00000000002   # 2 Zeichen
; 0004: 00000000002   # u = nein
; 0005: 00000000004   # 4 Zeichen
; 0006: 00000000007   # w nach Text wieder Zahl
;#PRUEFE-ENDE
