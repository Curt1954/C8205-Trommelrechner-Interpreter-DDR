; test_vorspann.asm - Vorspann der .test-Datei aus dem Quelltext
;#DOK-0001 Druck von BZ und AC (Bedienpult 4.2, 4.3): Ein bei 5000 laufendes Programm wird unterbrochen (BZ = 5000, AC = 10101010101).
; #DOK-0002 H G Ue E rettet den AC nach 7777 (BZ = 5001); H G M+ E M- R springt nach Zelle 0001 (druck) mit AC = 5003 im Adressfeld.
;#DOK-0003 5000: Ausgabe eines Zeichens (030 0520), 5001: Stopp 1111.
; --sw-ausgabe virtuelle_Geraete/SW-Ausgabe
;#PROT STUFE=2
; Ein gewoehnlicher Kommentar gehoert nicht in den Vorspann.
;#; LEITADRESSE 02

               start
               020   0          ; halt
ende:          end

; Pruefungen:
; --pruefe-sw-ausgabe test_vorspann-sw-ausgabe.txt
