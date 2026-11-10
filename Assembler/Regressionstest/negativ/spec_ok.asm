        start
; $SPEC im Quelltext: TYP=A zweimal Code, TYP=M mit $GLOBAL einmal, Kurzformen, beliebige Reihenfolge
EINS: MACRO 1
; Kommentar vor $SPEC ist erlaubt

        $SPEC   ACTION=None TYP=A    ; Kommentar dahinter
        dw $1
        MEND
ZWEI: MACRO
        $SPEC   TYP=Macro CLASS=KAT4 ACTION=Load
        $GLOBAL zwei_da
        $IF $V(zwei_da) = 0
        $SET zwei_da 1
        dw 7
        $ENDIF
        MEND
DREI: MACRO
        $SPEC   CLASS=LADER TYP=L
        $GLOBAL drei_da
        $IF $V(drei_da) = 0
        $SET drei_da 1
        dw 9
        $ENDIF
        MEND
        EINS 5
        EINS 6
        ZWEI
        ZWEI
        DREI
        DREI
        020 0
        end
