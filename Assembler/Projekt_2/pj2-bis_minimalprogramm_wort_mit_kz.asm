; C8205 BIS - Eingabe eines wortes mit Kennzeichen:
;
; Zugelassene Zeichen:  0 1 2 3 4 5 6 7 8 9 B D + <ZR> / : <BM>
;
; Auf Grund der beschränkten Hardware prüft das Programm nicht, ob andere Zeichen als zu zugelassenen eingegeben
; werden. Falls das der Fall ist, kommt es zu einer Fehlreaktion.
; Der Bediener des Programmes ist in der Pflicht, nur zulässige Eingaben vorzunehmen.
;

                start
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm

                equ100  *-2
kz_eingabe:     240     kz_rs           ; Rueckkehrbefehl sichern auf Arbeitszelle 
                000     eingabe
kz_tab:         dw      0             ; Ziffer 0
                dw      01            ; Ziffer 1 
                dw      02            ; Ziffer 2
                dw      03            ; Ziffer 3                                                                                                  
                dw      04            ; Ziffer 4
                dw      05            ; Ziffer 5
                dw      06            ; Ziffer 6
                dw      07            ; Ziffer 7
                dw      010           ; Ziffer 8
                dw      011           ; Ziffer 9
                001     eingabe       ; Fortsetzung nach Eingabe von ZW
eingabe:        010     kz_tab
                644     adr7706
                214     adr7706
                000     eingabe

                spa     022
                dw      022           ; B
                spa     024
                dw      024           ; D

                spa     033
                211     adr7706
                000     kz_rs

schleife:       014     kz_tab          ; Linksverschiebung
                004     *+1
                004     schleife
ende:           000     kz_rs 

                spa     052
                001     eingabe        ; ZR  löschen und Neuanfang

                spa     073
                002     ende            ; Fortsetzung nach Eingabe von "Punkt"

adr7706:        abs     07706
kz_rs:          abs     07741           ; Rueckkehrbefehl
r1:             abs     07773


; ---- Hauptprogramm -------------------------------------------------------------------------------
haupt:          equ     02400
                030     04700           ; Kanal K0 
                025     kz_eingabe ; Zeichen 0 bis 7 und Punkt einlesen
                240     r1              ; R1 := eingelesene Konstante
                020     0000            ; Stopp (AC = R1 = Konstante)
                end
