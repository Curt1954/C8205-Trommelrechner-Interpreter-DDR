; Definition VOR start
GRUSS:  MACRO 1
        dz  $ingb
        dz  $1
        dz  $inkb
        MEND

        start
        GRUSS +
        020 0
        end