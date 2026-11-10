; kat_einmal.asm - Test: die sechs UP-Makros KAT4/5/6 AUSGABE/EINGABE erzeugen ihren Rumpf nur beim ersten Aufruf (Einmal-Schutz in c82ass.makros)
; Jedes Makro steht zweimal im Quelltext: erster Aufruf mit Marke (erzeugt das UP), zweiter ohne Marke (erzeugt nichts).
; Die Marke emark steht hinter allen Aufrufen; ihre Adresse haengt von der Zellenzahl ab. Wuerde ein zweiter Aufruf den Rumpf erneut erzeugen, läge emark woanders.
;#DOK-0001 Einmal-Schutz: KAT4/5/6 AUSGABE/EINGABE je zweimal aufgerufen, Rumpf nur einmal vorhanden (Adresse der Endemarke)
;#PROT STUFE=2
                start                ; Zaehlung beginnt bei 0000
                000     haupt        ; Zelle 0000: Sprung zum Hauptprogramm
haupt:          020     0            ; Zelle 0001: Halt (die UP werden nicht aufgerufen, nur erzeugt)
k4aus:          KAT4AUSGABE          ; UP kat4 Ausgabe, erster Aufruf
                KAT4AUSGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
k4ein:          KAT4EINGABE          ; UP kat4 Eingabe, erster Aufruf
                KAT4EINGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
k5aus:          KAT5AUSGABE          ; UP kat5 Ausgabe, erster Aufruf
                KAT5AUSGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
k5ein:          KAT5EINGABE          ; UP kat5 Eingabe, erster Aufruf
                KAT5EINGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
k6aus:          KAT6AUSGABE          ; UP kat6 Ausgabe, erster Aufruf
                KAT6AUSGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
k6ein:          KAT6EINGABE          ; UP kat6 Eingabe, erster Aufruf
                KAT6EINGABE          ; zweiter Aufruf ohne Marke, erzeugt nichts
emark:          dw      0123         ; Endemarke mit festem Wert
ende:           end

; Sollwerte: Zelle 0000 Sprung, 0001 Halt, ab 0002 die UP-Rümpfe (je einmal), danach emark.
; Makro-Umordnung (Vorgabe ab c82ass 1.03-007, Pragma ;#MAKROUMORDNEN=NO schaltet sie ab): KAT4AUSGABE (057 Zellen) und KAT6AUSGABE (062 Zellen)
; fangen nicht mit equ100/equ40 an und wandern hinter das Programmende, also hinter emark (k6aus 1201, k4aus 1263). Ohne Umordnung läge emark bei 1400.
; Von Hand: k4ein 0002, 0136 Codezellen bis 0137, Tabelle nach equ100 auf 0200 bis 0277; k5aus 0300 (0117 Zellen bis 0416);
; k5ein 0417, 070 Codezellen bis 0506, Tabelle 0600 bis 0677; k6ein 0700, 0140 Codezellen bis 1037, Tabelle 1100 bis 1177; emark 1200.
; Halt in 0001, BZ = 0002; emark (Zelle 1200 oktal) enthaelt 0123 oktal. Zelle 1342 (hinter k4aus, 1263 + 057 Zellen) bleibt leer: KAT4AUSGABE und KAT6AUSGABE stehen
; hinter emark, dort faende sich ein doppelt erzeugter Rumpf; emark allein bemerkt ihn nicht mehr.
;#PRUEFE-START
; BZ=0002
; 1200: 00000000123   # emark: Endemarke hinter den vier nicht verlegten UP; KAT4AUSGABE und KAT6AUSGABE stehen dahinter
; 1342: 00000000000   # leer: hinter dem Rumpf von KAT4AUSGABE (Ende 1341) darf nichts stehen; ein zweiter Rumpf wuerde hier beginnen
;#PRUEFE-ENDE
