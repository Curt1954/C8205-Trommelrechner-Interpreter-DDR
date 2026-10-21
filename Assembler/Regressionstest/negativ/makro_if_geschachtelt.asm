        start
BAD1:   MACRO 1
        $IF    $1  =  1
        $IF $1 = 2
        030 05100
        $ELIF  $1  =  2
        030 05200
        MEND
        BAD1 1
        end
