; Kein toter Code: Befehle hinter bedingtem Sprung, Stopp und Sprung mit Rueckkehrabsicht, verwendete Marke,
; Sprungtabelle (Sprung hinter Sprung) und ein Sprungbefehl, den ein Speicherbefehl ueberschreibt.
        start   0
        000     m1
        000     m2
        000     m3
pruef:  040     m4
        210     wert
        020     0
        211     wert
        025     up
        211     wert
        000     ende
m1:     211     wert
        240     ueber
ueber:  000     m3
        211     wert
        000     pruef
m2:     211     wert
m3:     211     wert
m4:     020     0
ende:   020     0
up:     020     0
wert:   dw      3
        end
