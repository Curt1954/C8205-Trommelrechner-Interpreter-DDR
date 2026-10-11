         start  0
; ziffern.asm  --  Ziffer 0-3 einlesen und auswerten
;
; Ablauf: Aufforderung auf dem Schreibwerk (SW, Kanal K2) ausgeben,
;         eine Ziffer ueber K0 einlesen (Tastatur oder SW).
;         1, 2, 3 -> zugehoerigen Text ausgeben und Stopp
;         0       -> "Programmende" ausgeben und Stopp
;         4 ... 9 -> uebergehen, naechste Eingabe abwarten
;
; Auswertung ohne Rechnen: Der Eingabe-Halt 011 liest die Zelle
; (ztab ODER Zeichenadresse) und addiert sie zum geloeschten AC.
; In dieser Zelle steht fuer jede Ziffer ein Bitmuster, das durch
; Linksverschiebung (004) nach z0 geschoben und mit Negativsprung (040)
; erkannt wird:   1 -> z0     2 -> z1     3 -> z2     0 -> z3
; Die Ziffern 4 bis 9 liefern 0 und fuehren zurueck zum Einlesen.
; Hinweis dt: Jede dt-Folge beginnt mit dtm (Umschaltzeichen passend
; zum ersten Zeichen), damit Assembler- und Laufzeitzustand KB/GB
; unabhaengig vom Programmweg uebereinstimmen.

beginn:  ANWAHL 4500                ; K2 = Schreibwerk-Ausgabe
         dtm    \Geben Sie eine Ziffer von 0-3 ein\
         WRZL                       ; Zeilenschaltung, danach K0 (Eingabe) angewaehlt

lesen:   011    ztab                ; Eingabe-Halt mit Loeschen: AC := <ztab ODER Zeichen>
         040    eins               ; AC<0 (z0)  -> Ziffer 1
         004    *+1                ; AC 1x links
         040    zwei               ; z1 -> z0   -> Ziffer 2
         004    *+1
         040    drei               ; z2 -> z0   -> Ziffer 3
         004    *+1
         040    null               ; z3 -> z0   -> Ziffer 0
         000    lesen              ; Ziffer 4 bis 9: uebergehen

eins:    ANWAHL 4500
         dtm    \Es wurde die Ziffer 1 eingegeben, machen Sie weiter ...\
         dz     $wrzl
         020    0                   ; Stopp

zwei:    ANWAHL 4500
         dtm    \Ziffer 2 eingegeben, machen Sie weiter ...\
         dz     $wrzl
         020    0                   ; Stopp

drei:    ANWAHL 4500
         dtm    \Das ist jetzt Ziffer 3! Machen Sie weiter ...\
         dz     $wrzl
         020    0                   ; Stopp

null:    ANWAHL 4500
         dtm    \Programmende\
         dz     $wrzl
         020    0                   ; Stopp

; Zeichentabelle fuer den Eingabe-Halt; Zellenadresse = ztab + Eingabeadresse
; (Eingabeadresse der Ziffern: 0->0, 1->1, 2->2, 3->3, 4->4 ... 7->7, 8->010, 9->011)
         equ100 *                   ; ztab muss durch 0100 teilbar sein
ztab:    dw     004000000000        ; Ziffer 0 : z3
         dw     040000000000        ; Ziffer 1 : z0
         dw     020000000000        ; Ziffer 2 : z1
         dw     010000000000        ; Ziffer 3 : z2
         dw     0                   ; Ziffer 4 : keine Auswertung
         dw     0                   ; Ziffer 5 : keine Auswertung
         dw     0                   ; Ziffer 6 : keine Auswertung
         dw     0                   ; Ziffer 7 : keine Auswertung
         dw     0                   ; Ziffer 8 : keine Auswertung
         dw     0                   ; Ziffer 9 : keine Auswertung

         end

