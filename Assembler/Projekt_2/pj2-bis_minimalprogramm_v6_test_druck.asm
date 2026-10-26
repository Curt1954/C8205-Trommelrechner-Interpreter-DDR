; C8205 BIS - Test der Druckprogramme des Minimalprogramms v6 (pj2-bis_minimalprogramm_v6.asm)
;
; Das Minimalprogramm ist geladen. Dieses kleine Programm liegt auf 02000. Das Minimalprogramm hat kein Hauptprogramm und keinen
; Sprung ueber Zelle 0000; der Aufruf erfolgt mit der Tastenfolge H G und Start bei 2000 (im Test: #STARTE 2000), nicht mit einem Sofortbefehl.
; Es waehlt das Schreibwerk SW1 als Ausgabe an, schaltet auf Kleinbuchstaben und gibt vier leicht erkennbare Oktalzahlen
; mit dem Triadendruck (Ansprungzelle 0200) aus, je eine Zeile. Danach unbedingter Stopp.
; Erwartete Ausgabe auf SW (Gruppen zu je 4 Ziffern):
;     0123 4567 012
;     7654 3210 765
;     1111 2222 333
;     7000 0000 007
;
; Adressen im Minimalprogramm (Ansprungzellen und Uebergabezelle des Druckteils)
triadendruck:   abs     0200            ; Ansprungzelle Triadendruck (Wort in R1 = 7773)
adr7773:        abs     07773           ; Uebergabezelle

; Absolute Adressen, kein Basisanteil: Leitadresse 00 (Assemblerdokumentation 3.3.12)
;#; LEITADRESSE 00
                start
                equ     02000
test_druck:     030     04500           ; Schreibwerk SW1 als Ausgabe anwaehlen
                dz      $inkb           ; Zeichenlage Kleinbuchstaben (beim Start zufaellig)
                211     z1
                240     adr7773
                025     triadendruck
                dz      $wrzl           ; Zeilenschaltung
                211     z2
                240     adr7773
                025     triadendruck
                dz      $wrzl
                211     z3
                240     adr7773
                025     triadendruck
                dz      $wrzl
                211     z4
                240     adr7773
                025     triadendruck
                dz      $wrzl
                020     0               ; unbedingter Stopp
z1:             dw      01234567012
z2:             dw      076543210765
z3:             dw      011112222333
z4:             dw      070000000007
                end
