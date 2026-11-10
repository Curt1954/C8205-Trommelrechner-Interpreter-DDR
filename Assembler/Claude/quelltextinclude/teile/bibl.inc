; bibl.inc - Unterprogramm-Bibliothek zu quelltextinclude.asm (mit $INCLUDE eingebunden)
verdopple:      240     rueck        ; erste Zeile des UP: Rueckkehrwort sichern
                211     erg          ; AC := erg
                210     erg          ; AC := AC + erg
                240     erg          ; erg := AC
                000     rueck        ; zurueck zum Aufrufer
                $INCLUDE bibl2.inc   ; verschachtelt: Pfad relativ zu teile/bibl.inc, also teile/bibl2.inc
