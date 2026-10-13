; pj2-erstellen_lochstreifen_zur_programmeingabe-1.asm
; Gibt den Text "Alles Ok" auf dem Schreibwerk (SW) aus und beendet sich (Stopp).
;
; Zweck: Das Programm ist die Vorlage fuer den Lochstreifen lochstreifen_zur_programmeingabe-1.txt
; (virtuelle_Geraete/Leser1/). Der Streifen beginnt mit dem Kennzeichen 20 5000. (Relativadresse 5000)
; und enthaelt danach alle Zeilen der Objektdatei dieses Programms (ohne Adress-Spalte).
;
; Das Programm ist lageunabhaengig: Es enthaelt keinen Sprung und keinen Zugriff auf eigene Zellen.
; Die Anwahl des Schreibwerks (030 04500) und die Ausgabezeichen (dtm) haben das Kennzeichen K1K2 = 00,
; also keine Adressaenderung beim Laden. Der Stopp (020 0) hat K1K2 = 01 (Adressteil 0000 plus
; Hauptleitadresse); fuer den Stopp ist sein Adressteil ohne Bedeutung.
; Das Programm belegt 14 Zellen (oktal 0000 bis 0015) und liegt nach dem Laden mit dem Kennzeichen
; 20 5000. ab Hauptleitadresse + 5000 (bei Hauptleitadresse 0 also 5000 bis 5015):
;   0000        Kanal-Anwahl SW1 Output (K2)
;   0001 - 0014 Text "Alles Ok" mit den noetigen Umschaltzeichen (dtm, 12 Zellen)
;   0015        Stopp
; Start nach dem Laden: Sprung auf die Zelle 5000 (+ Hauptleitadresse).
;
; Die Zeichenlage (KB/GB) des Schreibwerks ist nach dem Einschalten zufaellig. Deshalb beginnt der
; Text mit dtm: Die Anweisung setzt vor dem ersten Zeichen immer ein Umschaltzeichen (hier GB fuer das A).
; Der Assembler fuegt innerhalb des Textes weitere Umschaltzeichen nur dort ein, wo die Lage wechselt
; (A GB, lles KB, O GB, k KB). Das Leerzeichen hat in beiden Lagen denselben Kode.

                start
                ANWAHL  SW1O                    ; Kanal K2 anwaehlen (Schreibwerk 1, Ausgabe)
                dtm     \Alles Ok\              ; Text "Alles Ok" ausgeben
halt:           020     0                       ; Stopp: Programmende
                end
