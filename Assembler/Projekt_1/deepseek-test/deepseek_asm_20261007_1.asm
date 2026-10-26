; Negativtest: absichtlicher Fehler, Makro DOPPELT wird zweimal definiert (Rueckgabewert 16 erwartet)
        start
DOPPELT: MACRO
        dz  $ingb
        MEND
DOPPELT: MACRO
        dz  $inkb
        MEND
        DOPPELT
        020 0
        end