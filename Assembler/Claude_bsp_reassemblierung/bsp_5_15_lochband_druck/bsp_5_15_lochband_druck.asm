; bsp_5_15_lochband_druck.asm  -  symbolisches Assemblerprogramm zu Testdatei bsp_5_15_lochband_druck.txt
; #DOK-0001 Abdruck numerischer Texte vom Lochband im R 300-Code (Programmieranleitung 5.15), Leser 2 -> Schreibwerk
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe
; --leser2 Test-virtuelleGeraete/Leser2/bsp_5_15_lochstreifen.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Startstück (nicht Teil des Buchprogramms): Das Schreibwerk muss nach der Aufgabe auf Kleinbuchstaben (KB) stehen;
; sein Zustand nach dem Einschalten ist zufällig. Daher Anwahl K2, Umschaltung auf KB, dann Sprung zum Programmanfang 3014.
m0000:          000     m3100                    ; Sprung zum Startstück
                equ     03100
m3100:          030     04500                    ; Anwahl Kanal K2 (Schreibwerk-Ausgabe)
                030     01170                    ; Umschaltung auf KB
                000     m3014                    ; Sprung zum Programmanfang

; Programm 5.15, erste Fassung (Zellen oberhalb 2777)
                equ     03000
m3000:          030     00200                    ; Druck "0"
                030     00010                    ; Druck "1"
                030     00020                    ; Druck "2"
                030     00230                    ; Druck "3"
                030     00040                    ; Druck "4"
                030     00250                    ; Druck "5"
                030     00260                    ; Druck "6"
                030     00070                    ; Druck "7"
                030     00100                    ; Druck "8"
                030     00310                    ; Druck "9"
                030     00320                    ; Zwischenraum
                000     m3015                    ; Sprung zur Eingabe
m3014:          030     04500                    ; Anwahl 2, Programmanfang
m3015:          011     m3000                    ; Eingabe eines Zeichens, <AC> := Druckbefehl, falls Umstellung in Addition
                240     m3021                    ; <3021> := Druckbefehl
                000     m3021                    ; Sprung zum Druckbefehl
                030     00400                    ; Druck "+"
m3021:          000     m0000                    ; Druckbefehl (wird zur Laufzeit gesetzt)
                000     m3015                    ; Sprung zur Eingabe
; Im Buch steht hier "2730 030"; maßgeblich ist die Ausgabe-Adresse 272x (Tabelle 1, Wagenrücklauf mit Zeilenschaltung), wie in der zweiten
;   Fassung des Buches ("2720 030")
                equ     03032
                030     02720                    ; Wagenrücklauf mit Zeilenschaltung
                000     m3015                    ; Sprung zur Eingabe
                equ     03040
                030     01000                    ; Druck "-"
                000     m3015                    ; Sprung zur Eingabe
                equ     03073
                030     01530                    ; Druck ","
                000     m3015                    ; Sprung zur Eingabe
                030     01550                    ; Tabulator
                000     m3015                    ; Sprung zur Eingabe

; Testende (nicht Teil des Buchprogramms): Das Zeichen "/" (Eingabeadresse 61) führt nach 3061, dort steht ein unbedingter Stopp.
                equ     03061
                020     0                        ; unbedingter Stopp

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3062 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3021: 00000200030
; 3061: 00000000020
; --pruefe-sw-ausgabe bsp_5_15_lochband_druck-sw-ausgabe.txt
;
