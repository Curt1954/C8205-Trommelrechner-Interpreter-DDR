; makro_local_felder_zuviele: mehr als 16 lokale Felder in einem Makroaufruf sind ein Fehler (Grenze seit c82ass 1.02-001: 16, vorher 4)
        start
L7:     MACRO
        $LOCAL f1(2) f2(2) f3(2) f4(2) f5(2) f6(2) f7(2) f8(2)
        $LOCAL f9(2) f10(2) f11(2) f12(2) f13(2) f14(2) f15(2) f16(2)
        $LOCAL f17(2)
        MEND
        L7
        end
