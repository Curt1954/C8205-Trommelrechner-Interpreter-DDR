; makro_local_zuviele: mehr als 64 lokale Variablen in einem Makroaufruf sind ein Fehler (Grenze seit c82ass 1.02-001: 64, vorher 16)
        start
L6:     MACRO
        $LOCAL a1 a2 a3 a4 a5 a6 a7 a8
        $LOCAL b1 b2 b3 b4 b5 b6 b7 b8
        $LOCAL c1 c2 c3 c4 c5 c6 c7 c8
        $LOCAL d1 d2 d3 d4 d5 d6 d7 d8
        $LOCAL e1 e2 e3 e4 e5 e6 e7 e8
        $LOCAL f1 f2 f3 f4 f5 f6 f7 f8
        $LOCAL g1 g2 g3 g4 g5 g6 g7 g8
        $LOCAL h1 h2 h3 h4 h5 h6 h7 h8
        $LOCAL i1
        MEND
        L6
        end
