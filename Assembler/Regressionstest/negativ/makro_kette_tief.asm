; makro_kette_tief: Makroaufrufe sind 34 Ebenen tief verschachtelt (erlaubt sind 32)
        start
M1:     MACRO
        M2
        MEND
M2:     MACRO
        M3
        MEND
M3:     MACRO
        M4
        MEND
M4:     MACRO
        M5
        MEND
M5:     MACRO
        M6
        MEND
M6:     MACRO
        M7
        MEND
M7:     MACRO
        M8
        MEND
M8:     MACRO
        M9
        MEND
M9:     MACRO
        M10
        MEND
M10:     MACRO
        M11
        MEND
M11:     MACRO
        M12
        MEND
M12:     MACRO
        M13
        MEND
M13:     MACRO
        M14
        MEND
M14:     MACRO
        M15
        MEND
M15:     MACRO
        M16
        MEND
M16:     MACRO
        M17
        MEND
M17:     MACRO
        M18
        MEND
M18:     MACRO
        M19
        MEND
M19:     MACRO
        M20
        MEND
M20:     MACRO
        M21
        MEND
M21:     MACRO
        M22
        MEND
M22:     MACRO
        M23
        MEND
M23:     MACRO
        M24
        MEND
M24:     MACRO
        M25
        MEND
M25:     MACRO
        M26
        MEND
M26:     MACRO
        M27
        MEND
M27:     MACRO
        M28
        MEND
M28:     MACRO
        M29
        MEND
M29:     MACRO
        M30
        MEND
M30:     MACRO
        M31
        MEND
M31:     MACRO
        M32
        MEND
M32:     MACRO
        M33
        MEND
M33:     MACRO
        M34
        MEND
M34:     MACRO
        040 ziel
        MEND
        M1
        040 ziel
ziel:   dw 1
