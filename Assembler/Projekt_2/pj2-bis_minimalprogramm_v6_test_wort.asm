; C8205 BIS - Test der Eingabe eines Wortes mit Kennzeichen des Minimalprogramms v6 (pj2-bis_minimalprogramm_v6.asm)
;
; Das Minimalprogramm ist geladen. Dieses kleine Programm liegt auf 02000. Das Minimalprogramm hat kein Hauptprogramm und keinen
; Sprung ueber Zelle 0000; der Aufruf erfolgt mit der Tastenfolge H G und Start bei 2000 (im Test: #STARTE 2000), nicht mit einem Sofortbefehl.
; Es ruft die Eingabe eines Wortes mit Kennzeichen (Ansprungzelle 0262) mit K0 auf. Hauptleitadresse und Relativadresse kommen
; vom Band: gespeichert wird ab Hauptleitadresse + Relativadresse = 1000 + 2000 = 3000. Die Eingabe speichert alle Woerter mit
; K1 = 0 fortlaufend und kehrt beim Schlusszeichen ':' zurueck. Dann gibt das Programm die Zellen 3000 bis 3003 und den Leitbefehl mit dem Triadendruck (0200) auf SW aus,
; je eine Zeile, und endet mit einem unbedingten Stopp.
; Eingabe fuer den Regressionstest (Hauptleitadresse := 1000, Relativadresse := 2000, vier Woerter, Schlusszeichen):
;     2 1 1 0 0 0 .   2 0 2 0 0 0 .   0 0 1 2 3 .   0 1 4 5 6 .   0 0 7 6 5 4 3 2 1 0 7 6 5 .   0 .   :
; Erwartete Ausgabe auf SW (Gruppen zu je 4 Ziffern):
;     0000 0000 123      Zelle 3000: Wort ohne Leitadresse
;     0000 1000 456      Zelle 3001: Wort plus 1. Leitadresse (1000 in t6 ... t3)
;     7654 3210 765      Zelle 3002: Wort mit 11 Ziffern
;     0000 0000 000      Zelle 3003: 0.
;     0000 3004 240      Leitbefehl nach vier gespeicherten Woertern
;
; Adressen im Minimalprogramm (Ansprungzellen, Uebergabezelle und Arbeitszelle)
triadendruck:   abs     0200            ; Ansprungzelle Triadendruck (Wort in R1 = 7773)
eingabewortkz:  abs     0262            ; Ansprungzelle Eingabe eines Wortes mit Kennzeichen
adr7773:        abs     07773           ; Uebergabezelle
LB:             abs     07600           ; Leitbefehl (240 mit Adresse)
z3000:          abs     03000           ; erste Abspeicherzelle

; Absolute Adressen, kein Basisanteil: Leitadresse 00 (Assemblerdokumentation 3.3.12)
;#; LEITADRESSE 00
                start
                equ     02000
test_wort:      030     04700           ; Kanal K0 (Bedienpult-Tastatur)
                025     eingabewortkz   ; Woerter eingeben, Rueckkehr bei ':'
                030     04500           ; Schreibwerk SW1 als Ausgabe
                dz      $inkb           ; Zeichenlage Kleinbuchstaben (beim Start zufaellig)
                211     z3000
                240     adr7773
                025     triadendruck
                dz      $wrzl           ; Zeilenschaltung
                211     z3000+1
                240     adr7773
                025     triadendruck
                dz      $wrzl
                211     z3000+2
                240     adr7773
                025     triadendruck
                dz      $wrzl
                211     z3000+3
                240     adr7773
                025     triadendruck
                dz      $wrzl
                211     LB              ; Leitbefehl ausgeben
                240     adr7773
                025     triadendruck
                dz      $wrzl
                020     0               ; unbedingter Stopp
                end
