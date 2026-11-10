        start
KOP:    MACRO 1
        $PR1 $TYPTEXT 5
        dw $LEN1
        MEND
        KOP "abc def"
        end
