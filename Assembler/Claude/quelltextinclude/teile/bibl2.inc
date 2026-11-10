; bibl2.inc - zweite Bibliotheksdatei (aus bibl.inc eingebunden, Tiefe 2)
plus1:          240     rueck        ; erste Zeile des UP: Rueckkehrwort sichern
                211     erg          ; AC := erg
                210     eins         ; AC := AC + 1
                240     erg          ; erg := AC
                000     rueck        ; zurueck zum Aufrufer
plus3:          240     rueck        ; erste Zeile des UP: Rueckkehrwort sichern
                211     erg          ; AC := erg
                210     drei         ; AC := AC + 3
                240     erg          ; erg := AC
                000     rueck        ; zurueck zum Aufrufer
