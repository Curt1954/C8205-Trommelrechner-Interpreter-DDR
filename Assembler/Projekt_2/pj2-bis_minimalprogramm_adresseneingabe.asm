; C8205 BIS - Adresseneingabe: Eingabe der Zeichen 0 bis 7 und Punkt (8-Kanal-Ausfuehrung, R 300-Code)
;
; Das Unterprogramm liest ueber den vom Aufrufer angewaehlten Kanal eine Oktalzahl mit bis zu 8 Ziffern.
; Schlusszeichen ist der Punkt. Aufruf: Der Aufrufer waehlt den Eingabekanal an,
; dann 025 adresseneingabe. Rueckkehr mit der Konstanten im Akkumulator.
;
;   Eingabe        Ergebnis im AC (z0 bis z23, rechtsbuendig in den Oktalstellen t3 bis t10)
;
; Auf Grund der beschränkten Hardware prüft das Programm nicht, ob andere Zeichen als zu zugelassenen eingegeben
; werden. Falls das der Fall ist, kommt es zu einer Fehlreaktion.
; Der Bediener des Programmes ist in der Pflicht, nur zulässige Eingaben vorzunehmen.
;

                start
                000     haupt           ; Zelle 0000: Sprung zum Hauptprogramm

; ---- Adresseneingabe: Unterprogramm auf Spur 0300 ------------------------------------------------
                equ     0156
adresseneingabe: 240    ae_rs           ; Rueckkehrbefehl sichern auf Arbeitszelle 
                001     schleife
                 
                equ100  *
schleife:       014     ae_tab          ; Linksverschiebung
                004     *+1
                004     schleife
ende:           000     ae_rs 

                spa     040
ae_tab:         dw      0               ; Ziffer 0
                dw      0100            ; Ziffer 1 (1 * 0100)
                dw      0200            ; Ziffer 2
x3:               dw      0300            ; Ziffer 3
                dw      0400            ; Ziffer 4
                dw      0500            ; Ziffer 5
                dw      0600            ; Ziffer 6
                dw      0700            ; Ziffer 7

                spa     052
                001     schleife        ; ZR  löschen und Neuanfang

                spa     073
                002     ende            ; Fortsetzung nach Eingabe von "Punkt"

ae_rs:          abs     07741           ; Rueckkehrbefehl
r1:             abs     07773


; ---- Hauptprogramm -------------------------------------------------------------------------------
haupt:          equ     02400
                030     04700           ; Kanal K0 
                025     adresseneingabe ; Zeichen 0 bis 7 und Punkt einlesen
                240     r1              ; R1 := eingelesene Konstante
                020     0000            ; Stopp (AC = R1 = Konstante)
