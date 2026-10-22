;#; LEITADRESSE 00   ; absolut geschrieben: zum Laden ueber das KEP (--ABSPR) werden keine Adressen umgerechnet
         start
; namen_raten.asm  --  Ratespiel "Rate mal, welchen Namen ich mir gemerkt habe" ueber das Schreibwerk (SW)
;
; Aufgabe: Das Programm waehlt aus fuenf Namen mit je 7 Buchstaben einen aus und nennt den 1. Buchstaben.
;          Der Benutzer tippt am SW die uebrigen Buchstaben der Reihe nach. Ein falscher Buchstabe darf
;          einmal wiederholt werden (2. Versuch je Buchstabe). Ist auch der 2. Versuch falsch, kommt
;          "Du musst deine Fantasie viel mehr schulen.", dann 3 Leerzeilen und das Spiel beginnt von vorn.
;          Sind alle 7 Buchstaben erraten: "Toll, du bist fantasiebegabt.", 3 Leerzeilen, neues Spiel.
;          Ein Punkt (.) beendet das Programm zu jeder Zeit; das steht in der Aufforderung am Anfang jedes Spiels.
; Namen im Programm: Michael, Barbara, Susanne, Andreas, Claudia (je 7 Buchstaben).
; Tasten:  Buchstaben werden verglichen (Gross-/Kleinschreibung ist egal). Um. KB und Um. GB werden ueberlesen,
;          der Punkt beendet das Programm, jede andere Taste zaehlt als Fehlversuch.
; Zeichensatz: Das SW kennt weder das ss-Zeichen noch Umlaute; deshalb steht im Text "musst" mit zwei s.
; Hinweis fuer Aenderungen: Keine Zeile mit einem Label ohne Befehl verwenden. Der Assembler zaehlt sie in Pass 2
;          mit, erzeugt aber kein Wort; dadurch stimmen alle folgenden Symbole nicht mehr.
;
; Aufruf:  Tastenfolge  H SW=1 G R   (der Schalter SW muss gedrueckt sein: Buchstaben kommen nur ueber das SW).
;          Zelle 0000 springt nach 02000. Ausgabe ueber K2 (ANWAHL 4500), Eingabe ueber K0 (WRZL waehlt K0 an).
;
; Eingabe: 011 ztab ist ein Eingabe-Halt mit Loeschen. Das Zeichen liefert seine Eingabeadresse, sie wird in den
;          Adressteil ODER-verknuepft; der Befehl liest also die Zelle ztab + Eingabeadresse (ztab liegt auf einem
;          Vielfachen von 0100). Zeichen ohne Sprung-Umstellung (alle Buchstaben, Ziffern) werden so zu einem Datenwort
;          im AC. Zeichen MIT Sprung-Umstellung (Punkt, Leertaste, Um. KB, ...) fuehren die Tabellenzelle als BEFEHL aus.
;          In ztab steht fuer jeden Buchstaben seine Eingabeadresse in den Adressstellen (Eingabeadresse << 9).
; Namen:   Jeder Name ist eine Folge von Eingabeadressen im selben Format (8 Zellen: 7 Buchstaben und das Endwort 0).
;          Gross- und Kleinbuchstaben haben dieselbe Eingabeadresse und gelten daher als gleich.
; Auswahl: Eine feste Liste von 32 Zufallszahlen (Namensnummer 0..4, mal 8 Zellen Abstand, in den Adressstellen)
;          wird der Reihe nach durchlaufen; die Endmarke -1 setzt den Zeiger wieder an den Anfang. Der Zeiger
;          ist der veraenderliche Befehl "lzuf" und bleibt von Spiel zu Spiel erhalten.
; 1. Buchstabe: atab liefert zur Eingabeadresse den Ausgabebefehl (030 <Ausgabeadresse>); er wird in die Zelle "aus"
;          gespeichert und dort als Befehl ausgefuehrt, in Grossschreibung (Um. GB davor).

beginn:  000    anfang            ; Zelle 0000: Sprung nach 02000
         equ    02000

; ---------------------------------------------------------------------- Aufforderung (bei jedem Spiel)
anfang:  ANWAHL 4500              ; K2 = Schreibwerk-Ausgabe
         dtm    \Rate mal, welchen Namen ich mir gemerkt habe.\
         dz     $wrzl
         dtm    \Mit der Eingabe eines Punktes beendest du das Programm.\
         dz     $wrzl

; ---------------------------------------------------------------------- Namen auswaehlen
lzuf:    211    zufall            ; AC := Eintrag der Zufallsliste (Namensnummer * 8 Zellen, << 9); Befehl wird weitergeschaltet
         040    wrap              ; Eintrag < 0: Endmarke, Liste von vorn
         210    nbasis            ; AC := "211 namen" + Eintrag = Befehl auf den 1. Buchstaben des gewaehlten Namens
         240    l1
         210    eins              ; Adresse + 1: 2. Buchstabe
         240    lnam
         211    lzuf              ; Zeiger der Zufallsliste um 1 weiter
         210    eins
         240    lzuf

; ---------------------------------------------------------------------- 1. Buchstabe nennen
l1:      211    namen             ; AC := Eingabeadresse des 1. Buchstabens (Befehl wird je Spiel gesetzt)
         210    abef              ; AC := "211 atab" + Eingabeadresse = Befehl "211 atab+Eingabeadresse"
         240    ba
ba:      dw     0                 ; wird ausgefuehrt: AC := Ausgabebefehl "030 <Ausgabeadresse>" des Buchstabens
         240    aus
         ANWAHL 4500
         dtm    \1. Buchstabe ist:  \
         dz     $ingb             ; Grossbuchstabe
aus:     dw     0                 ; wird zum Ausgabebefehl des 1. Buchstabens
         WRZL                     ; Zeilenschaltung, danach K0 (Eingabe) angewaehlt

; ---------------------------------------------------------------------- naechsten Buchstaben erwarten
lnam:    211    namen             ; AC := erwarteter Buchstabe (Eingabeadresse << 9); 0 = Namensende (Befehl wird weitergeschaltet)
         240    erw
         320    null              ; Vergleich mit 0 (markierter Einzelbefehl, Vgl 3 bei Gleichheit)
         170    gewonnen          ; Vgl 3: Namensende erreicht, alle Buchstaben erraten
         211    lnam
         210    eins
         240    lnam              ; Zeiger auf den uebernaechsten Buchstaben
         211    minus1
         240    vers              ; vers := -1: 1. Versuch

lesen:   011    ztab              ; Eingabe-Halt mit Loeschen: AC := ztab + Eingabeadresse (Sprung-Zeichen springen)
         320    erw               ; getippten Buchstaben mit dem erwarteten vergleichen
         170    richtig           ; Vgl 3: gleich

falsch:  211    vers              ; Fehlversuch (auch Sprungziel der Sonderzeichen in ztab)
         040    nochmal           ; vers < 0: das war der 1. Versuch
         ANWAHL 4500              ; 2. Fehlversuch
         dtm    \  Du musst deine Fantasie viel mehr schulen.\
         dz     $wrzl             ; Zeilenende
         dz     $wrzl             ; Leerzeile 1
         dz     $wrzl             ; Leerzeile 2
         dz     $wrzl             ; Leerzeile 3
         000    anfang            ; von vorn

nochmal: 211    null
         240    vers              ; vers := 0: 2. Versuch
         ANWAHL 4500
         dtm    \  Falsch, noch ein Versuch.\
         WRZL
         000    lesen

richtig: ANWAHL 4500
         dtm    \  Richtig!\
         WRZL
         000    lnam

gewonnen: ANWAHL 4500
         dtm    \  Toll, du bist fantasiebegabt.\
         dz     $wrzl             ; Zeilenende
         dz     $wrzl             ; Leerzeile 1
         dz     $wrzl             ; Leerzeile 2
         dz     $wrzl             ; Leerzeile 3
         000    anfang            ; von vorn

ende:    ANWAHL 4500              ; Punkt eingegeben
         dtm    \  Programm beendet.\
         dz     $wrzl
         020    0                 ; Stopp

wrap:    211    zanf              ; Endmarke der Zufallsliste: Zeiger wieder auf den Anfang ...
         240    lzuf
         000    lzuf              ; ... und den Eintrag erneut holen

; ---------------------------------------------------------------------- Konstanten und Merkzellen
eins:    dw     01000             ; 1 in den Adressstellen (Adresse << 9)
null:    dw     0
minus1:  dw     -1
erw:     dw     0                 ; erwarteter Buchstabe
vers:    dw     0                 ; -1 = 1. Versuch, 0 = 2. Versuch
nbasis:  211    namen             ; Vorlage: Befehl auf den 1. Buchstaben des 1. Namens
zanf:    211    zufall            ; Vorlage: Anfangswert des Zeigers lzuf
abef:    211    atab              ; Vorlage: Befehl auf den Anfang der Ausgabetabelle atab

; ---------------------------------------------------------------------- Namen (Eingabeadressen << 9, je Name 7 Buchstaben + Endwort)
namen:   dw     044*01000      ; Name 0, Buchstabe 1: m  (Eingabeadresse 044)
         dw     031*01000      ; Name 0, Buchstabe 2: i  (Eingabeadresse 031)
         dw     023*01000      ; Name 0, Buchstabe 3: c  (Eingabeadresse 023)
         dw     030*01000      ; Name 0, Buchstabe 4: h  (Eingabeadresse 030)
         dw     021*01000      ; Name 0, Buchstabe 5: a  (Eingabeadresse 021)
         dw     025*01000      ; Name 0, Buchstabe 6: e  (Eingabeadresse 025)
         dw     043*01000      ; Name 0, Buchstabe 7: l  (Eingabeadresse 043)
         dw     0                  ; Name 0 (Michael): Endwort
         dw     022*01000      ; Name 1, Buchstabe 1: b  (Eingabeadresse 022)
         dw     021*01000      ; Name 1, Buchstabe 2: a  (Eingabeadresse 021)
         dw     051*01000      ; Name 1, Buchstabe 3: r  (Eingabeadresse 051)
         dw     022*01000      ; Name 1, Buchstabe 4: b  (Eingabeadresse 022)
         dw     021*01000      ; Name 1, Buchstabe 5: a  (Eingabeadresse 021)
         dw     051*01000      ; Name 1, Buchstabe 6: r  (Eingabeadresse 051)
         dw     021*01000      ; Name 1, Buchstabe 7: a  (Eingabeadresse 021)
         dw     0                  ; Name 1 (Barbara): Endwort
         dw     062*01000      ; Name 2, Buchstabe 1: s  (Eingabeadresse 062)
         dw     064*01000      ; Name 2, Buchstabe 2: u  (Eingabeadresse 064)
         dw     062*01000      ; Name 2, Buchstabe 3: s  (Eingabeadresse 062)
         dw     021*01000      ; Name 2, Buchstabe 4: a  (Eingabeadresse 021)
         dw     045*01000      ; Name 2, Buchstabe 5: n  (Eingabeadresse 045)
         dw     045*01000      ; Name 2, Buchstabe 6: n  (Eingabeadresse 045)
         dw     025*01000      ; Name 2, Buchstabe 7: e  (Eingabeadresse 025)
         dw     0                  ; Name 2 (Susanne): Endwort
         dw     021*01000      ; Name 3, Buchstabe 1: a  (Eingabeadresse 021)
         dw     045*01000      ; Name 3, Buchstabe 2: n  (Eingabeadresse 045)
         dw     024*01000      ; Name 3, Buchstabe 3: d  (Eingabeadresse 024)
         dw     051*01000      ; Name 3, Buchstabe 4: r  (Eingabeadresse 051)
         dw     025*01000      ; Name 3, Buchstabe 5: e  (Eingabeadresse 025)
         dw     021*01000      ; Name 3, Buchstabe 6: a  (Eingabeadresse 021)
         dw     062*01000      ; Name 3, Buchstabe 7: s  (Eingabeadresse 062)
         dw     0                  ; Name 3 (Andreas): Endwort
         dw     023*01000      ; Name 4, Buchstabe 1: c  (Eingabeadresse 023)
         dw     043*01000      ; Name 4, Buchstabe 2: l  (Eingabeadresse 043)
         dw     021*01000      ; Name 4, Buchstabe 3: a  (Eingabeadresse 021)
         dw     064*01000      ; Name 4, Buchstabe 4: u  (Eingabeadresse 064)
         dw     024*01000      ; Name 4, Buchstabe 5: d  (Eingabeadresse 024)
         dw     031*01000      ; Name 4, Buchstabe 6: i  (Eingabeadresse 031)
         dw     021*01000      ; Name 4, Buchstabe 7: a  (Eingabeadresse 021)
         dw     0                  ; Name 4 (Claudia): Endwort

; ---------------------------------------------------------------------- Zufallsliste: 32 Namensnummern, Endmarke -1
; Eintrag = Namensnummer * 010000 (8 Zellen Abstand der Namen, << 9 in die Adressstellen)
zufall:  dw     2*010000          ;  0: Name 2 (Susanne)
         dw     0*010000          ;  1: Name 0 (Michael)
         dw     1*010000          ;  2: Name 1 (Barbara)
         dw     0*010000          ;  3: Name 0 (Rudolph)
         dw     1*010000          ;  4: Name 1 (Herbert)
         dw     3*010000          ;  5: Name 3 (Andreas)
         dw     1*010000          ;  6: Name 1 (Barbara)
         dw     0*010000          ;  7: Name 0 (Michael)
         dw     2*010000          ;  8: Name 2 (Susanne)
         dw     4*010000          ;  9: Name 4 (Claudia)
         dw     0*010000          ; 10: Name 0 (Michael)
         dw     2*010000          ; 11: Name 2 (Susanne)
         dw     4*010000          ; 12: Name 4 (Claudia)
         dw     3*010000          ; 13: Name 3 (Andreas)
         dw     4*010000          ; 14: Name 4 (Barbara)
         dw     3*010000          ; 15: Name 3 (Marlies)
         dw     4*010000          ; 16: Name 4 (Claudia)
         dw     0*010000          ; 17: Name 0 (Michael)
         dw     4*010000          ; 18: Name 4 (Claudia)
         dw     2*010000          ; 19: Name 2 (Susanne)
         dw     1*010000          ; 20: Name 1 (Barbara)
         dw     3*010000          ; 21: Name 3 (Andreas)
         dw     4*010000          ; 22: Name 4 (Claudia)
         dw     2*010000          ; 23: Name 2 (Susanne)
         dw     3*010000          ; 24: Name 3 (Andreas)
         dw     1*010000          ; 25: Name 1 (Barbara)
         dw     4*010000          ; 26: Name 4 (Claudia)
         dw     0*010000          ; 27: Name 0 (Michael)
         dw     3*010000          ; 28: Name 3 (Andreas)
         dw     2*010000          ; 29: Name 2 (Susanne)
         dw     1*010000          ; 30: Name 1 (Barbara)
         dw     0*010000          ; 31: Name 0 (Michael)
         dw     -1                 ; Endmarke

; ---------------------------------------------------------------------- Ausgabetabelle atab (Index = Eingabeadresse): Ausgabebefehl des Buchstabens
atab:    dw     0                  ; 00
         dw     0                  ; 01
         dw     0                  ; 02
         dw     0                  ; 03
         dw     0                  ; 04
         dw     0                  ; 05
         dw     0                  ; 06
         dw     0                  ; 07
         dw     0                  ; 10
         dw     0                  ; 11
         dw     0                  ; 12
         dw     0                  ; 13
         dw     0                  ; 14
         dw     0                  ; 15
         dw     0                  ; 16
         dw     0                  ; 17
         dw     0                  ; 20
         dw     0610030        ; 21: a
         dw     0620030        ; 22: b
         dw     0430030        ; 23: c
         dw     0640030        ; 24: d
         dw     0450030        ; 25: e
         dw     0460030        ; 26: f
         dw     0670030        ; 27: g
         dw     0700030        ; 30: h
         dw     0510030        ; 31: i
         dw     0                  ; 32
         dw     0                  ; 33
         dw     0                  ; 34
         dw     0                  ; 35
         dw     0                  ; 36
         dw     0                  ; 37
         dw     0                  ; 40
         dw     01210030        ; 41: j
         dw     01220030        ; 42: k
         dw     01030030        ; 43: l
         dw     01240030        ; 44: m
         dw     01050030        ; 45: n
         dw     01060030        ; 46: o
         dw     01270030        ; 47: p
         dw     01300030        ; 50: q
         dw     01110030        ; 51: r
         dw     0                  ; 52
         dw     0                  ; 53
         dw     0                  ; 54
         dw     0                  ; 55
         dw     0                  ; 56
         dw     0                  ; 57
         dw     0                  ; 60
         dw     0                  ; 61
         dw     01420030        ; 62: s
         dw     01630030        ; 63: t
         dw     01440030        ; 64: u
         dw     01650030        ; 65: v
         dw     01660030        ; 66: w
         dw     01470030        ; 67: x
         dw     01500030        ; 70: y
         dw     01710030        ; 71: z
         dw     0                  ; 72
         dw     0                  ; 73
         dw     0                  ; 74
         dw     0                  ; 75
         dw     0                  ; 76
         dw     0                  ; 77

; ---------------------------------------------------------------------- Eingabetabelle ztab (Index = Eingabeadresse), auf Vielfachem von 0100
         equ100 *
ztab:    dw     0                  ; 00: kein Buchstabe (Fehlversuch)
         dw     0                  ; 01: kein Buchstabe (Fehlversuch)
         dw     0                  ; 02: kein Buchstabe (Fehlversuch)
         dw     0                  ; 03: kein Buchstabe (Fehlversuch)
         dw     0                  ; 04: kein Buchstabe (Fehlversuch)
         dw     0                  ; 05: kein Buchstabe (Fehlversuch)
         dw     0                  ; 06: kein Buchstabe (Fehlversuch)
         dw     0                  ; 07: kein Buchstabe (Fehlversuch)
         dw     0                  ; 10: kein Buchstabe (Fehlversuch)
         dw     0                  ; 11: kein Buchstabe (Fehlversuch)
         000    falsch        ; 12: Leertaste / ZWR: zaehlt als Fehlversuch
         dw     0                  ; 13: kein Buchstabe (Fehlversuch)
         dw     0                  ; 14: kein Buchstabe (Fehlversuch)
         000    falsch        ; 15: : / (          : zaehlt als Fehlversuch
         000    falsch        ; 16: Irrung Satz: zaehlt als Fehlversuch
         dw     0                  ; 17: kein Buchstabe (Fehlversuch)
         dw     0                  ; 20: kein Buchstabe (Fehlversuch)
         dw     021*01000     ; 21: a
         dw     022*01000     ; 22: b
         dw     023*01000     ; 23: c
         dw     024*01000     ; 24: d
         dw     025*01000     ; 25: e
         dw     026*01000     ; 26: f
         dw     027*01000     ; 27: g
         dw     030*01000     ; 30: h
         dw     031*01000     ; 31: i
         000    falsch        ; 32: SatzMarke / WRZL: zaehlt als Fehlversuch
         000    ende        ; 33: . / !          : Punkt beendet das Programm
         dw     0                  ; 34: kein Buchstabe (Fehlversuch)
         dw     0                  ; 35: kein Buchstabe (Fehlversuch)
         dw     0                  ; 36: kein Buchstabe (Fehlversuch)
         000    lesen        ; 37: Um. GB: ueberlesen, weiter warten
         000    falsch        ; 40: - / Dreieck: zaehlt als Fehlversuch
         dw     041*01000     ; 41: j
         dw     042*01000     ; 42: k
         dw     043*01000     ; 43: l
         dw     044*01000     ; 44: m
         dw     045*01000     ; 45: n
         dw     046*01000     ; 46: o
         dw     047*01000     ; 47: p
         dw     050*01000     ; 50: q
         dw     051*01000     ; 51: r
         dw     0                  ; 52: kein Buchstabe (Fehlversuch)
         dw     0                  ; 53: kein Buchstabe (Fehlversuch)
         dw     0                  ; 54: kein Buchstabe (Fehlversuch)
         dw     0                  ; 55: kein Buchstabe (Fehlversuch)
         dw     0                  ; 56: kein Buchstabe (Fehlversuch)
         000    lesen        ; 57: Um. KB: ueberlesen, weiter warten
         000    falsch        ; 60: ` / ;          : zaehlt als Fehlversuch
         dw     0                  ; 61: kein Buchstabe (Fehlversuch)
         dw     062*01000     ; 62: s
         dw     063*01000     ; 63: t
         dw     064*01000     ; 64: u
         dw     065*01000     ; 65: v
         dw     066*01000     ; 66: w
         dw     067*01000     ; 67: x
         dw     070*01000     ; 70: y
         dw     071*01000     ; 71: z
         000    falsch        ; 72: BM (ZV hat dieselbe Adresse, aber keine Sprung-Umstellung): Fehlversuch
         000    falsch        ; 73: , / ?          : zaehlt als Fehlversuch
         dw     0                  ; 74: kein Buchstabe (Fehlversuch)
         000    falsch        ; 75: Tabulator: zaehlt als Fehlversuch
         dw     0                  ; 76: kein Buchstabe (Fehlversuch)
         dw     0                  ; 77: kein Buchstabe (Fehlversuch)
         end
