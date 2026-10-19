         start  0
; sw_zwei_ziffern.asm  --  Beispiel fuer Eingabe ueber das Schreibwerk (SW)
;
; Ablauf: Aufforderung auf dem Schreibwerk (K2) ausgeben, eine Ziffer 0-3 ueber K0 einlesen,
;         Ergebnis ausgeben, dann ein zweites Mal Aufforderung, Eingabe und Ergebnis, Stopp.
;         4 ... 9 werden uebergangen (wie bei ziffern.asm).
; Zweck:  Zwischen den beiden Eingaben steht ein Anwahlbefehl K2 (Ausgabe). Die Eingabe kommt
;         ueber SW nur, wenn der Anwahlbefehl K0 die Schalterstellung SW auswertet (Schalter SW
;         gedrueckt: Flag SW, sonst Flag T). Mit Schalter SW gedrueckt muss das SW-Fenster beide
;         Ziffern annehmen; ohne Schalter SW muss das Programm auf die Pult-Tastatur (T) warten.

beginn:  ANWAHL 4500                ; K2 = Schreibwerk-Ausgabe
         dtm    \Erste Ziffer 0-3:\
         WRZL                       ; Zeilenschaltung, danach K0 (Eingabe) angewaehlt

lesen1:  011    ztab                ; Eingabe-Halt mit Loeschen
         040    e1
         004    *+1
         040    e2
         004    *+1
         040    e3
         004    *+1
         040    e0
         000    lesen1              ; 4 bis 9: uebergehen

e1:      ANWAHL 4500
         dtm    \Erste: 1\
         dz     $wrzl
         000    zwei
e2:      ANWAHL 4500
         dtm    \Erste: 2\
         dz     $wrzl
         000    zwei
e3:      ANWAHL 4500
         dtm    \Erste: 3\
         dz     $wrzl
         000    zwei
e0:      ANWAHL 4500
         dtm    \Erste: 0\
         dz     $wrzl

zwei:    ANWAHL 4500                ; K2: loescht T und SW, der Schalter SW bleibt gedrueckt
         dtm    \Zweite Ziffer 0-3:\
         WRZL                       ; K0-Anwahl liest die Schalterstellung SW

lesen2:  011    ztab
         040    z1
         004    *+1
         040    z2
         004    *+1
         040    z3
         004    *+1
         040    z0
         000    lesen2

z1:      ANWAHL 4500
         dtm    \Zweite: 1\
         dz     $wrzl
         020    0                   ; Stopp
z2:      ANWAHL 4500
         dtm    \Zweite: 2\
         dz     $wrzl
         020    0
z3:      ANWAHL 4500
         dtm    \Zweite: 3\
         dz     $wrzl
         020    0
z0:      ANWAHL 4500
         dtm    \Zweite: 0\
         dz     $wrzl
         020    0

         equ100 *                   ; ztab muss durch 0100 teilbar sein
ztab:    dw     004000000000        ; Ziffer 0 : z3
         dw     040000000000        ; Ziffer 1 : z0
         dw     020000000000        ; Ziffer 2 : z1
         dw     010000000000        ; Ziffer 3 : z2
         dw     0
         dw     0
         dw     0
         dw     0
         dw     0
         dw     0

         end
