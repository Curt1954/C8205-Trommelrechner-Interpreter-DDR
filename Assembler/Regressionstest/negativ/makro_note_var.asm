        start
; makro_note_var: eine nicht auswertbare $V(...)-Angabe in $NOTE ist ein Fehler (Doku 4.24), Rueckgabecode 16
N1:     MACRO
        $NOTE n=$V(nix)
        dw 1
        MEND
        N1
        end
