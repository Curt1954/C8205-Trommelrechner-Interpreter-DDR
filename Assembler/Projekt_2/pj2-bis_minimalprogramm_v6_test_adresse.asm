; C8205 BIS - Test der Adresseneingabe des Minimalprogramms v6 (pj2-bis_minimalprogramm_v6.asm)
;
; Das Minimalprogramm ist geladen. Dieses kleine Programm liegt auf 02000. Das Minimalprogramm hat kein Hauptprogramm und keinen
; Sprung ueber Zelle 0000; der Aufruf erfolgt mit der Tastenfolge H G und Start bei 2000 (im Test: #STARTE 2000), nicht mit einem Sofortbefehl.
; Es ruft dreimal die Adresseneingabe (Ansprungzelle 0316) mit der Bedienpult-Tastatur K0 auf. Jede Adresse (bis 8 Oktalziffern,
; mit Punkt abgeschlossen; kein ZR) steht danach im AC in den Triaden t10 ... t3 und wird mit dem Triadendruck (0200) auf SW
; ausgegeben, je eine Zeile. Danach unbedingter Stopp.
; Eingabe fuer den Regressionstest:   1 2 3 4 .   7 6 5 4 3 2 1 0 .   5 .
; Erwartete Ausgabe auf SW (Gruppen zu je 4 Ziffern):
;     0000 1234 000
;     7654 3210 000
;     0000 0005 000
;
; Adressen im Minimalprogramm (Ansprungzellen und Uebergabezelle des Druckteils)
triadendruck:   abs     0200            ; Ansprungzelle Triadendruck (Wort in R1 = 7773)
adresseneingabe: abs    0316            ; Ansprungzelle Adresseneingabe (Ergebnis im AC)
adr7773:        abs     07773           ; Uebergabezelle

; Absolute Adressen, kein Basisanteil: Leitadresse 00 (Assemblerdokumentation 3.3.12)
;#; LEITADRESSE 00
                start
                equ     02000
test_adresse:   030     04700           ; Kanal K0 (Bedienpult-Tastatur)
                025     adresseneingabe ; 1. Adresse
                240     adr7773
                030     04500           ; Schreibwerk SW1 als Ausgabe
                dz      $inkb           ; Zeichenlage Kleinbuchstaben (beim Start zufaellig)
                025     triadendruck
                dz      $wrzl           ; Zeilenschaltung
                030     04700
                025     adresseneingabe ; 2. Adresse
                240     adr7773
                030     04500
                dz      $inkb
                025     triadendruck
                dz      $wrzl
                030     04700
                025     adresseneingabe ; 3. Adresse
                240     adr7773
                030     04500
                dz      $inkb
                025     triadendruck
                dz      $wrzl
                020     0               ; unbedingter Stopp
                end
