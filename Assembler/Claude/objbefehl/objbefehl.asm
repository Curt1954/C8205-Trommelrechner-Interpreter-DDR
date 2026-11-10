; objbefehl.asm - Test der Anweisungen ;#PRECOMMAND= und ;#POSTCOMMAND= (c82ass ab 1.03-009, Doku 5.7)
; Der Lochstreifen .obj beginnt mit den beiden PRECOMMAND (in der Reihenfolge des Quelltexts: 212000. dann 77.) und endet mit den beiden
; POSTCOMMAND (102000000. dann 1.), danach folgt das Endekennzeichen /. Dazwischen stehen die Woerter des Programms.
; Der Regressionstest vergleicht die .obj-Datei mit der Referenz; hier prueft nur die .test, dass das Programm selbst unveraendert laeuft.
;#DOK-0001 PRECOMMAND vor dem ersten Wort und POSTCOMMAND hinter dem letzten Wort des .obj, vor dem Endekennzeichen
;#PRECOMMAND=212000.
;#POSTCOMMAND=102000000. ; Beispielwert
;#PRECOMMAND=77.
;#POSTCOMMAND=1.
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          211     wert         ; Zelle 0001: AC := wert
                240     erg          ; Zelle 0002: erg := AC
                020     0            ; Zelle 0003: Halt
wert:           dw      0123         ; Zelle 0004: Konstante
erg:            dw      0            ; Zelle 0005: Ergebnis
ende:           end

;#PRUEFE-START
; BZ=0004
; 0005: 00000000123   # erg = wert
;#PRUEFE-ENDE
