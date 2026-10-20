; Test: Mit #STARTE im Vorspann entfaellt der Abschnitt Tastenfolge: der .test-Datei
; #DOK-0001 Start ab Speicherplatz 0000 mit #STARTE
; #TROMMEL=LEER   # Trommel vorher leeren
; #STARTE 0
; #INTERRUPT H G R   (gehoert nicht in den Vorspann, wird nicht uebernommen)
               start
               020   0
ende:          end
