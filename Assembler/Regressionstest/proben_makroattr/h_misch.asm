        start
        000     haupt
; CO: $CALCO und $CALCOn mit zellen (tab hat 10 Zellen: oktal 012)
CO:     MACRO
        dw      $CALCO(zellen(tab))         ; 012 = 10
        dw      $CALCO4(zellen(tab))        ; 0012 = 10
        MEND
; TX: $CALC im Text von $SET und in Textargumenten (4.22)
TX:     MACRO
        $SET t "$CALC(zellen(tab))"
        dw      $V(#t)                      ; Text 10: 2 Zeichen
        $VAL v "$V(t)"
        dw      $V(v)                       ; 10
        $STRCMP r "$CALC(art(tab))" "4"
        dw      $V(r)                       ; 4 gleich 4: 0
        MEND
; PE: Parameter ist ein Ausdruck mit Attributfunktion; $REPT $1, $IF $CALC($1)
PE:     MACRO 1
        $REPT $1
        dw      $Z1                         ; 0, 1
        $ENDREPT
        $IF $CALC($1) = 2
        dw      22                          ; erzeugt
        $ENDIF
        MEND
; SO: Operation aus Parameter (4.15)
SO:     MACRO 2
        $1      $2
        MEND
; AB: Attributabfrage in einem Makro, das ueber OP M aufgerufen wird
AB:     MACRO 1
        dw      $CALC(zellen(tab)+def(tab)*100+art(tab)*1000)   ; 10 + 100 + 4000 = 4110
        MEND
; ZW: Makro ruft Makro auf; das innere fragt
INNEN:  MACRO 1
        dw      $CALC(zellen($1))           ; 10
        MEND
AUSSEN: MACRO 1
        INNEN   $1
        MEND
        CO                                  ; E=10,10
        TX                                  ; E=2,10,0
        PE      zellen(a2)                  ; E=0,1,22
        SO      AB 0                        ; E=4110
        AUSSEN  tab                         ; E=10
haupt:  164     0001
        020     0
tab:    db      012
a2:     dbn     2
        end
