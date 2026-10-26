; #DOK-0001
; #SPEI-0001 0000-0000
; #PROT STUFE=2
; #TROMMEL=LEER
         start
         000  start
         000  tstart
         equ  02000
start:   211  #0100
         210  #0100
         210  #0100
         240  adr777
adr777:  abs  07777
         020  01
tstart:  211  #200
         240  adr777
         020  02
         end

