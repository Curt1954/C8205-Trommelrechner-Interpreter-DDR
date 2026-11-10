; zil.asm - ZIL, der Initialloader der Zusatztrommeln (Projekt ZT-Loader), PROTOTYP: Ablauf nach dem Flussdiagramm ZIL_Ablauf.pdf; nur repo ist noch Platzhalter, alle uebrigen UP sind echt (ztinit, pname, neuanl, hschl).
; Die Elemente 16 und 17 schreiben auf die ZT (SPUF-PN noch einmal mit neuanl, SPUF-00 mit Anwahl 5100 030 und Ausgabe 601).
;
; Ablauf (Flussdiagramm ZIL_Ablauf.pdf Seite 1; Nummern in Klammern = Nummern des Diagramms, ZT-Repository_Aufgabenstellung.md Abschnitt 6):
;   1a. Das Hauptprogramm setzt die GLOBALE Zelle KBGB (Zelle 7775, ganzes Projekt, 0 = KB, 1 = GB) auf KB. Wer KB/GB aendert, fuehrt sie nach.
;   1b. Das Hauptprogramm gibt vor der ersten Ausgabe eine Zeilenschaltung auf dem Schreibwerk aus (ANWAHL K2, WRZL; WRZL waehlt danach K0 an).
;   1.  UP repo (Platzhalter fuer "Hat die ZT 0 ein Repository?"): R1 = Adresse SPUF-00 (Spurpuffer Spur 0 von ZT 0, Adressfeld),
;       Ergebnis R2 = 1 (Repository vorhanden) oder 0. Der Platzhalter meldet nur "UP Repository pruefen" und liefert die Konstante d_repo.
;   2.  R2 = 0: Ausschrift "Kein Repository gefunden", Halt.   R2 = 1: Ausschrift "Repository gefunden".
;   3.  Frage "Zusatztrommel loeschen [J/N]", Antwort ueber K0 (SW): nur ein GROSSgeschriebenes J oder N zaehlt (Um. GB, dann j oder n);
;       alle anderen Zeichen, auch kleines j oder n, werden uebergangen (der Antwort "Ja" folgt eine Loeschung, deshalb streng).
;   4.  N: 7b Zeilenschaltung (ANWAHL K2, WRZL), Ausschrift "Programmende", Halt.   J: 7a Zeilenschaltung (ANWAHL K2, WRZL), UP ztinit (Makro ZTINIT, siehe unten), status := 3, weiter mit 5.
;       ztinit: R1 = Adresse SPUF-00, alle vier ZT loeschen, Spur 0 von ZT 0 anlegen, ZT 0 angewaehlt, keine Ausschrift.
;       (7a, 7b: die Antwort J oder N steht als Echo des Schreibwerks auf der Zeile; ohne Zeilenschaltung stuende die naechste Ausschrift dahinter.)
;   5.  Ja-Weg (ZTD als Programm 1 laden):
;       11a Spurpuffer SPUF-PN (Namensverzeichnis, 2 Spuren = 64 Zellen) auf der Spurgrenze loeschen (zwei Gruppenbefehle 441, je Spur einer);
;       13  UP pname (Projektmakro PNAME) "Programmname eintragen": R1 = Adresse SPUF-PN, R2 = Adresse der Namenszelle (kat5 "ztd", eine Zelle seit 09.11.2026), R3 = Adresse SPUF-00;
;           PNAME traegt Name (Wort 1), Typ 10, ID, Trommel und Spur (Wort 2) ein und fuehrt den Zaehler in SPUF-00 Zelle 17 nach (ZT-Repository_Aufgabenstellung 6b), keine Ausschrift;
;       14  UP neuanl (Projektmakro NEUANL) "neuanlage Programm": R1 = Adresse SPUF-PN, R2 = Trommelnummer 0, R3 = Spurnummer 1 (Zahlen); schreibt SPUF-PN (jetzt noch mit Laenge 0) auf ZT 0 Spur 1 und 2,
;           keine Rueckgabe, keine Ausschrift, KBGB unberuehrt, die Trommel bleibt angewaehlt (ZT-Repository_Aufgabenstellung 6 Punkt 7);
;       12  Ausschrift "Lochband mit ZTD in Leser 1 einlegen";   14a K1 anwaehlen (Lochbandleser 1), HINTER 12 (Festlegung Inhaber 30.10.2026: MELDUNG waehlt K2 und danach K0 an, K1 bleibt so bis 15 angewaehlt);
;       15  UP hschl (Projektmakro HSCHL) "Hauptschleife Ls nach ZT": R1 = Adresse des Puffers Programmcode (1 Spur = 32 Zellen), R2 = Trommelnummer 0, R3 = Spurnummer 33 der ersten Zielspur (Zahlen), Aus R2 = Sektoranzahl (= 2 * Zahl der Eingaben);
; hschl liest den Streifen aus Leser 1 (K1) als Folge von Typ-10-Eingaben (UP eingabe = Projektmakro TYP10EINGABE: zwei Kennzeichen, Ziffern, Punkt oder Doppelpunkt; jede Eingabe = 2 Worte) und schreibt
;           sie spurweise (16 Eingaben je Spur) auf die ZT; / beendet den Streifen;
; bei mehr als 4095 Sektoren (2048 Eingaben) kehrt es NICHT zurueck, sondern springt auf den Fehlerausgang fe_lang dieses Programms (15b): Ausschrift "lochstreifen zu lang", Halt (einen Fehler "Ziffer 8
;           oder 9" gibt es nicht mehr: 8 und 9 sind gueltige Kennzeichen);
;       16  Laenge (Feld z21 bis z32 von Wort 2) des Eintrags in SPUF-PN := Sektoranzahl (die uebrigen Felder hat PNAME gesetzt: Wort 2 = 20010410000 + Laenge: Typ 10, ID 1, Trommel 0, Spur 33);
;           danach schreibt UP neuanl (Makro NEUANL, R1 = SPUF-PN, R2 = 0, R3 = 1) SPUF-PN noch einmal auf ZT 0 Spur 1 und 2 (keine Ausschrift);
;       17  Anwahl ZT 0 (030 05100) und Ausgabe 601: SPUF-00 auf ZT 0 Spur 0 (der Zaehler in Zelle 17 steht jetzt auf 1; die Zellen 18 und 19 werden nicht nachgefuehrt, md 8 Punkt 4 ist offen), keine Ausschrift;
;       18  Ausschrift "ZTD geladen mit Programm-ID 1".
; Jede Ausschrift steht auf einer eigenen Zeile (Makro MELDUNG: K2 anwaehlen, Text ueber das UP ausgabe = Makro KAT4AUSGABE_G, Zeilenschaltung; WRZL waehlt danach K0 an).
; Die Texte stehen als kat4-Woerter MIT Umschaltzeichen im Textblock (erzeugt von gen/zil_texte.py); jeder Text beginnt in KB. Das UP liest KBGB und fuehrt es bei jedem Umschaltzeichen im Text nach:
;   steht KBGB auf GB (z. B. nach der Frage, deren Text in GB endet), gibt es vor dem Text Um. KB aus. Folge fuer die Eingabe: nach der Frage steht KBGB = 1, die Eingabe muss mit Um. KB beginnen, damit das kleine j uebergangen wird.
; Der Platzhalter repo meldet nur seinen Namen ("Wo bin ich") mit MELDUNG und kehrt zurueck.
; Alle Wege enden am selben Halt (ende); die Zelle status haelt den Weg fest: 1 = kein Repository, 2 = Nein, 3 = Ja (initialisiert). 15b setzt status nicht.
;
; Unterprogramme und Zellen:
;   repo     Aufruf 025, R1 = Adresse spuf00 (Adressfeld), Ergebnis R2 (Register 7776) = 1 oder 0. Rueckkehrwort auf rr (am UP-Ende sequentiell, Festlegung 010).
;   jneingabe Aufruf 025, K0 vorher angewaehlt, Ergebnis R2 = 1 (J) oder 0 (N). Liest mit 011 und einer Zeichentabelle auf einer 0100-Grenze.
;            Der KB/GB-Zustand steht in der GLOBALEN Zelle KBGB (7775, initial KB, vom Hauptprogramm gesetzt); Um. GB setzt 1, Um. KB setzt 0.
;            Nur wenn KBGB = 1 gilt j als Ja und n als Nein; alle anderen Zeichen und Sprungzeichen fuehren zurueck zum Lesen.
;   ztinit   Aufruf 025, R1 = Adresse spuf00 (Adressfeld). KEIN Platzhalter mehr: Makro ZTINIT aus macro_zt_loader.macro (ZT-Repository_Aufgabenstellung 6a), keine Ausschrift; SPUF-00 enthaelt danach Spur 0 von ZT 0, ZT 0 ist angewaehlt.
;   pname    Aufruf 025, R1 = Adresse spufpn, R2 = Adresse der Namenszelle zname, R3 = Adresse spuf00 (alle im Adressfeld). KEIN Platzhalter mehr: Makro PNAME aus macro_zt_loader.macro (Aufgabenstellung 6b), keine Ausschrift.
;   neuanl   Aufruf 025, R1 = Adresse spufpn (Adressfeld), R2 = Trommelnummer, R3 = Spurnummer (Zahlen). KEIN Platzhalter mehr: Makro NEUANL aus macro_zt_loader.macro (Aufgabenstellung 6 Punkt 7), keine Ausschrift.
;   hschl    Aufruf 025, R1 = Adresse spufpc (Adressfeld), R2 = Trommelnummer, R3 = Spurnummer der ersten Zielspur (Zahlen), Ergebnis R2 = Sektoranzahl (2 je Eingabe), R1, R3 und KBGB unveraendert.
;   KEIN Platzhalter mehr: Makro HSCHL und UP eingabe (Makro TYP10EINGABE) aus macro_zt_loader.macro (Aufgabenstellung 6c, 7a); Typ 10 statt kat4 seit 01.11.2026 (Auftrag Inhaber);
;            der Fehlerausgang fe_lang ist der erste Parameter des Makros HSCHL, hs_ende (Streifenende) wird von HSCHL gesetzt. Streifen im Test: Leser 1, Datei hschl_zil.txt (3 Eingaben und /, 6 Sektoren).
; Fehler im Lochstreifen (15b): es gibt keine Fehlerrueckgabe (Vorgabe Inhaber). hschl springt bei mehr als 4095 Sektoren nach fe_lang; dort steht die Ausschrift und der Halt (000 ende).
;   Die Zelle lsfehl und die Pruefung 15a gibt es nicht mehr.
; Hinweis: MELDUNG waehlt K2 und danach (WRZL) K0 an; darum steht die K1-Anwahl (14a) hinter der Aufforderung (12), und K1 bleibt bis zum Lesen in 15 angewaehlt (Kanalfolge 4).
;   hschl liest mit 011 von K1 (Leser 1); der Test beweist die Kanalfolge damit auch: waere K1 nicht angewaehlt, kaeme kein Wort auf die ZT.
; Empfehlung (001): kleinste Startzelle 0000, Ende vor 7600; Tabelle auf 0100-Grenze, Spurpuffer SPUF-00, SPUF-PN und Programmcode auf 040-Grenzen (Lage relativ zum Lader).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 zil (Prototyp): Repository vorhanden, Antwort J (nach einem kleinen j und n, die uebergangen werden): UP ztinit, Ja-Weg bis ZTD geladen, Weg 3
;#SPEI-0001 0001-0001
;#PROT STUFE=2
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/zil.txt
; --leser1 Test-virtuelleGeraete/Leser1/hschl_zil.txt
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/zil
;#TASTENFOLGE H SW=1 G R
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/zil-sw-ausgabe.txt

r1:             abs     07773                ; Register 1 (Adressfeld oder Wert, je nach UP)
r2:             abs     07776                ; Register 2: Ergebnis der UP (1 = ja / vorhanden, 0 = nein) bzw. Parameter
r3:             abs     07774                ; Register 3: Parameter des UP pname (Adresse SPUF-00); kein KB/GB-Zustand mehr
kbgb:           abs     07775                ; KBGB: GLOBALE Zelle KB/GB (0 = KB, 1 = GB), ganzes Projekt, Arbeitsspur 77xx

; MELDUNG textmarke: eine Ausschrift auf dem Schreibwerk (K2): R1 := Adresse des Textes (kat4-Woerter MIT Umschaltzeichen, Textblock weiter unten, erzeugt von gen/zil_texte.py),
;   UP ausgabe (Makro KAT4AUSGABE_G, liest und fuehrt die globale Zelle KBGB nach), danach Zeilenschaltung und K0 (WRZL).
;   Der Text beginnt in KB; steht KBGB auf GB, gibt das UP zuerst Um. KB aus. Die Textmarke ist ein Symbol (kein Text in Anfuehrungszeichen).
;   MELDUNG ueberschreibt AC und R1 (R1 ist nur Parameter des UP-Aufrufs, vgl. die Platzhalter).
MELDUNG:        MACRO 1
                $PR1 $TYPSYM
                ANWAHL  K2                   ; Kanal 2 = Schreibwerk
                211     @$1                  ; AC := Adresse des Textes (Adressfeld, Literal)
                240     r1                   ; R1 := Adresse des Textes
                025     ausgabe              ; UP ausgabe (KAT4AUSGABE_G): Text ausgeben, KBGB nachfuehren
                WRZL                         ; Zeilenschaltung (jede Ausschrift auf einer eigenen Zeile), danach K0
                MEND

                start                        ; Zaehlung beginnt bei 0000
                ZTKONST              ; benannte Konstanten (ZT_PROGSPUR1), erzeugt keine Zelle
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
status:         dw      0                    ; Zelle 0001: Weg des Programms (1 kein Repository, 2 Nein, 3 Ja), nur fuer den Test
a00:            da      spuf00               ; Zelle 0002: Adresse SPUF-00 (Spur 0 von ZT 0, Adressfeld)
apn:            da      spufpn               ; Zelle 0003: Adresse SPUF-PN (Namensverzeichnis, Adressfeld)
apc:            da      spufpc               ; Zelle 0004: Adresse des Puffers Programmcode, 1 Spur (Adressfeld)
anm:            da      zname                ; Zelle 0005: Adresse der Namenszelle kat5 "ztd" (Adressfeld)
d_repo:         dw      1                    ; Zelle 0006: Platzhalter-Ergebnis von repo (1 = Repository vorhanden)

haupt:          241     kbgb                 ; 1a: KBGB := 0 (KB), AC := 0
                ANWAHL  K2                   ; 1b: Schreibwerk anwaehlen
                WRZL                         ; 1b: Zeilenschaltung vor der ersten Ausgabe (danach K0)
                211     a00                  ; AC := Adresse SPUF-00 (Spur 0 von ZT 0)
                240     r1                   ; R1 := Adresse SPUF-00
                025     repo                 ; UP repo: R2 := 1 (Repository vorhanden) oder 0
                211     r2                   ; AC := Ergebnis
                330     #0                   ; Vergleich mit 0
                170     keinrepo             ; gleich 0: kein Repository
                MELDUNG t_repgef
                MELDUNG t_frage
                025     jneingabe            ; Antwort lesen: R2 := 1 (J) oder 0 (N), K0 ist angewaehlt
                211     r2                   ; AC := Antwort
                330     #1                   ; Vergleich mit 1
                170     ja                   ; gleich 1: Ja
                ANWAHL  K2                   ; 7b: Schreibwerk anwaehlen (Antwort N steht als Echo auf der Zeile)
                WRZL                         ; 7b: Zeilenschaltung vor der Ausschrift (danach K0)
                MELDUNG t_pende       ; Nein
                211     #2                   ; AC := 2
                240     status               ; Weg 2: Nein
                000     ende                 ; zum Halt
ja:             ANWAHL  K2                   ; 7a: Schreibwerk anwaehlen (Antwort J steht als Echo auf der Zeile)
                WRZL                         ; 7a: Zeilenschaltung vor der Ausschrift (danach K0)
                211     a00                  ; AC := Adresse SPUF-00 (Spur 0 von ZT 0)
                240     r1                   ; R1 := Adresse SPUF-00
                025     ztinit               ; UP ztinit: alle ZT loeschen, Spur 0 anlegen (SPUF-00 danach = Spur 0), ZT 0 angewaehlt, keine Ausschrift
                211     #3                   ; AC := 3
                240     status               ; Weg 3: Ja
                441     spufpn               ; 11a: Spur 1 von SPUF-PN (Spurgrenze) loeschen: alle 32 Zellen := 0, AC := 0
                441     spufpn+040           ; 11a: Spur 2 von SPUF-PN loeschen (2-Spur-Puffer, 64 Zellen)
                211     apn                  ; AC := Adresse SPUF-PN
                240     r1                   ; 13: R1 := Adresse SPUF-PN
                211     anm                  ; AC := Adresse der Namenszelle
                240     r2                   ; R2 := Adresse der Namenszelle (kat5 ztd)
                211     a00                  ; AC := Adresse SPUF-00
                240     r3                   ; R3 := Adresse SPUF-00
                025     pname                ; UP Programmname eintragen (Makro PNAME): Eintrag ID 1, Zaehler in SPUF-00 := 1
                211     apn                  ; AC := Adresse SPUF-PN
                240     r1                   ; 14: R1 := Adresse SPUF-PN
                241     r2                   ; R2 := 0 (Trommelnummer: Verzeichnis auf ZT 0), AC := 0
                211     #1                   ; AC := 1
                240     r3                   ; R3 := 1 (Spurnummer der ersten Verzeichnisspur; die zweite ist Spur 2)
                025     neuanl               ; UP neuanlage Programm (Makro NEUANL): SPUF-PN mit Laenge 0 auf ZT 0 Spur 1 und 2 schreiben
                MELDUNG t_lband              ; 12: Aufforderung (MELDUNG endet mit WRZL, also K0 angewaehlt)
                ANWAHL  K1                   ; 14a: K1 anwaehlen (Lochbandleser 1), HINTER 12, damit K1 bis Element 15 angewaehlt bleibt
                211     apc                  ; AC := Adresse des Puffers Programmcode (1 Spur)
                240     r1                   ; 15: R1 := Adresse Programmcode
                241     r2                   ; 15: R2 := 0 (Trommelnummer der ersten Zielspur), AC := 0
                211     #ZT_PROGSPUR1        ; AC := 33 (ZT_PROGSPUR1 aus ZTKONST, Literal # ist dezimal; oktal 41)
                240     r3                   ; 15: R3 := 33 (Spurnummer der ersten Zielspur: Spur nach der letzten belegten, Zelle 19 = 32)
                025     hschl                ; UP Hauptschleife Ls nach ZT (Makro HSCHL): R2 := Sektoranzahl; zu lang: kein Ruecksprung (fe_lang)
                211     r2                   ; 16: AC := Sektoranzahl (Laenge, hoechstens 4095)
                210     spufpn+1             ; plus Wort 2 (PNAME hat Typ, ID, Trommel, Spur gesetzt; z0 und Laenge sind 0): Laenge einsetzen
                240     spufpn+1             ; Wort 2 in SPUF-PN eintragen (Zelle 1 = Eintrag ID 1, Wort 2)
                211     apn                  ; 16: AC := Adresse SPUF-PN
                240     r1                   ; 16: R1 := Adresse SPUF-PN
                241     r2                   ; 16: R2 := 0 (Trommelnummer: Verzeichnis auf ZT 0), AC := 0
                211     #1                   ; AC := 1
                240     r3                   ; 16: R3 := 1 (Spurnummer der ersten Verzeichnisspur; die zweite ist Spur 2)
                025     neuanl               ; 16: UP neuanl (Makro NEUANL) schreibt SPUF-PN, jetzt mit der Laenge, noch einmal auf ZT 0 Spur 1 und 2 (ZT 0 bleibt angewaehlt)
                030     05100                ; 17: Anwahl ZT 0 (5100 030)
                601     spuf00               ; 17: Ausgabe SPUF-00 (32 Zellen, Spurgrenze) auf Spur 0 von ZT 0 (zzz0 = 0000)
                MELDUNG t_geladen      ; 18: Schlussmeldung
                000     ende                 ; zum Halt
fe_lang:        MELDUNG t_lszu       ; 15b: Fehlerausgang von hschl: mehr als 4095 Sektoren (2048 Eingaben)
                000     ende                 ; zum Halt
keinrepo:       MELDUNG t_keinrep
                211     #1                   ; AC := 1
                240     status               ; Weg 1: kein Repository
ende:           020     0                    ; Halt (alle Wege)

; ---- UP repo (Platzhalter): Hat die ZT 0 ein Repository? R1 = Adresse SPUF-00, Ergebnis R2
repo:           240     rr                   ; Rueckkehrwort sichern
                MELDUNG t_uprepo
                211     d_repo               ; AC := Platzhalter-Ergebnis
                240     r2                   ; R2 := Ergebnis
rr:             db      1                    ; Laufzeit: Rueckkehrwort (am UP-Ende sequentiell erreicht)

; ---- UP ztinit: Zusatztrommeln initialisieren (Makro ZTINIT aus macro_zt_loader.macro). R1 = Adresse SPUF-00, keine Rueckgabe, keine Ausschrift
ztinit:         ZTINIT                       ; Unterprogramm (Makro)

; ---- UP pname: Programmname eintragen (Makro PNAME aus macro_zt_loader.macro). R1 = SPUF-PN, R2 = Adresse der Namenszelle, R3 = SPUF-00, keine Rueckgabe, keine Ausschrift
pname:          PNAME                        ; Unterprogramm (Makro)

; ---- UP neuanl: neuanlage Programm (Makro NEUANL aus macro_zt_loader.macro). R1 = SPUF-PN, R2 = Trommelnummer, R3 = Spurnummer der ersten Spur, keine Rueckgabe, keine Ausschrift
neuanl:         NEUANL                       ; Unterprogramm (Makro)

; ---- UP hschl: Hauptschleife Ls nach ZT (Makro HSCHL aus macro_zt_loader.macro, Aufgabenstellung 6c).
; R1 = Adresse Programmcode, R2 = Trommelnummer, R3 = Spurnummer der ersten Zielspur, Ergebnis R2 = Sektoranzahl, R1, R3 und KBGB unveraendert; Fehlerausgang fe_lang (keine Rueckkehr); Streifenende:
;           Marke hs_ende (von HSCHL gesetzt, Endeausgang von TYP10EINGABE)
hschl:          HSCHL   fe_lang eingabe ende ; Unterprogramm (Makro): liest mit dem UP eingabe, setzt die Marke hs_ende, schreibt die Spuren

; ---- UP eingabe: eine Typ-10-Eingabe lesen (Makro TYP10EINGABE aus macro_zt_loader.macro, Aufgabenstellung 7a). R1 = Adresse des 2-Zellen-Bereichs, Kanal K1 angewaehlt; / springt nach hs_ende (Streifenende), KBGB wird nachgefuehrt
eingabe:        TYP10EINGABE hs_ende         ; Unterprogramm (Makro) mit Endeausgang hs_ende

; ---- UP jneingabe: J oder N (gross) lesen, Ergebnis R2 = 1 (J) oder 0 (N)
jneingabe:      240     rj                   ; Rueckkehrwort sichern
lesen:          011     tab                  ; Zeichen lesen: AC := Tabellenzelle (Sprungzeichen springen von selbst)
                240     zeich                ; zeich := Tabellenwert (1 = j, 2 = n, sonst 0)
                211     kbgb                 ; AC := KB/GB-Zustand (globale Zelle KBGB)
                330     #0                   ; Vergleich mit 0
                170     lesen                ; Kleinbuchstaben (KB): Zeichen zaehlt nicht
                211     zeich                ; AC := Tabellenwert
                330     #1                   ; Vergleich mit 1
                170     antj                 ; gleich 1: J
                330     #2                   ; Vergleich mit 2
                170     antn                 ; gleich 2: N
                000     lesen                ; anderes Zeichen: weiterlesen
antn:           241     r2                   ; N: R2 := 0, AC := 0
                000     rj                   ; zurueck
antj:           211     #1                   ; J: AC := 1
                240     r2                   ; R2 := 1
rj:             db      1                    ; Laufzeit: Rueckkehrwort (am UP-Ende sequentiell erreicht)
hgb:            211     #1                   ; Um. GB: AC := 1
                240     kbgb                 ; KBGB := 1
                000     lesen                ; weiterlesen
hkb:            241     kbgb                 ; Um. KB: KBGB := 0, AC := 0
                000     lesen                ; weiterlesen
zeich:          db      1                    ; Arbeitszelle: Tabellenwert des gelesenen Zeichens
zname:          kat5    ztd                  ; Namenszelle: kat5 "ztd" (ein Wort, 05244240000, keine Endemarke), vom UP pname in SPUF-PN einzutragen

; ---- Zeichentabelle (64 Zellen auf einer 0100-Grenze, Eingabeadresse = Zellenadresse ODER tab), ein Block (Festlegung 027)
                equ100  *                    ; tab muss durch 0100 teilbar sein
tab:            begin                        ; Beginn des Tabellenblocks (nichts darf verlegt werden)
                dw      0               ; 00: 0: keine Antwort, Wert 0
                dw      0               ; 01: 1: keine Antwort, Wert 0
                dw      0               ; 02: 2: keine Antwort, Wert 0
                dw      0               ; 03: 3: keine Antwort, Wert 0
                dw      0               ; 04: 4: keine Antwort, Wert 0
                dw      0               ; 05: 5: keine Antwort, Wert 0
                dw      0               ; 06: 6: keine Antwort, Wert 0
                dw      0               ; 07: 7: keine Antwort, Wert 0
                dw      0               ; 10: 8: keine Antwort, Wert 0
                dw      0               ; 11: 9: keine Antwort, Wert 0
                000     lesen           ; 12: Leertaste / ZWR: Sprungzeichen, zurueck zum Lesen
                dw      0               ; 13: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 14: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                000     lesen           ; 15: : (Doppelpunkt): Sprungzeichen, zurueck zum Lesen
                000     lesen           ; 16: Irrung Satz: Sprungzeichen, zurueck zum Lesen
                dw      0               ; 17: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 20: +: keine Antwort, Wert 0
                dw      0               ; 21: a: keine Antwort, Wert 0
                dw      0               ; 22: b: keine Antwort, Wert 0
                dw      0               ; 23: c: keine Antwort, Wert 0
                dw      0               ; 24: d: keine Antwort, Wert 0
                dw      0               ; 25: e: keine Antwort, Wert 0
                dw      0               ; 26: f: keine Antwort, Wert 0
                dw      0               ; 27: g: keine Antwort, Wert 0
                dw      0               ; 30: h: keine Antwort, Wert 0
                dw      0               ; 31: i: keine Antwort, Wert 0
                000     lesen           ; 32: WRZL: Sprungzeichen, zurueck zum Lesen
                000     lesen           ; 33: . (Punkt): Sprungzeichen, zurueck zum Lesen
                dw      0               ; 34: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 35: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 36: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                000     hgb             ; 37: Um. GB: KBGB := 1
                000     lesen           ; 40: - / Dreieck: Sprungzeichen, zurueck zum Lesen
                dw      1               ; 41: j: J (mit Um. GB) = Ja, Wert 1
                dw      0               ; 42: k: keine Antwort, Wert 0
                dw      0               ; 43: l: keine Antwort, Wert 0
                dw      0               ; 44: m: keine Antwort, Wert 0
                dw      2               ; 45: n: N (mit Um. GB) = Nein, Wert 2
                dw      0               ; 46: o: keine Antwort, Wert 0
                dw      0               ; 47: p: keine Antwort, Wert 0
                dw      0               ; 50: q: keine Antwort, Wert 0
                dw      0               ; 51: r: keine Antwort, Wert 0
                dw      0               ; 52: WR: keine Antwort, Wert 0
                dw      0               ; 53: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 54: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 55: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 56: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                000     hkb             ; 57: Um. KB: KBGB := 0
                000     lesen           ; 60: ` / ;: Sprungzeichen, zurueck zum Lesen
                dw      0               ; 61: / ): keine Antwort, Wert 0
                dw      0               ; 62: s: keine Antwort, Wert 0
                dw      0               ; 63: t: keine Antwort, Wert 0
                dw      0               ; 64: u: keine Antwort, Wert 0
                dw      0               ; 65: v: keine Antwort, Wert 0
                dw      0               ; 66: w: keine Antwort, Wert 0
                dw      0               ; 67: x: keine Antwort, Wert 0
                dw      0               ; 70: y: keine Antwort, Wert 0
                dw      0               ; 71: z: keine Antwort, Wert 0
                000     lesen           ; 72: BM: Sprungzeichen, zurueck zum Lesen
                000     lesen           ; 73: , / ?: Sprungzeichen, zurueck zum Lesen
                dw      0               ; 74: % / *: keine Antwort, Wert 0
                000     lesen           ; 75: Tabulator: Sprungzeichen, zurueck zum Lesen
                dw      0               ; 76: nicht belegte Eingabeadresse: keine Antwort, Wert 0
                dw      0               ; 77: Transport: keine Antwort, Wert 0
                bend                         ; Ende des Tabellenblocks

; ---- UP ausgabe: kat4-Text auf dem angewaehlten Kanal ausgeben (Projektmakro KAT4AUSGABE_G aus macro_zt_loader.macro), R1 = Adresse des Textes, KBGB wird gelesen und nachgefuehrt
ausgabe:        KAT4AUSGABE_G                ; Unterprogramm (Makro)

; ---- Texte der Ausschriften (kat4, Umschaltzeichen im Text; jeder Text beginnt in KB)
;#TEXTE-START   (erzeugt von gen/zil_texte.py, nicht von Hand aendern; Zeichen je Wort 4, erstes rechts, z0 = 040000000000 am letzten Wort)
                begin                        ; ein Block (Festlegung 027): der Optimierer darf die dw-Zeilen der Texte nicht verlegen
t_repgef:       dw      004523644457       ; "Repository gefunden" (Ende KB)
                dw      005130443127       ; Fortsetzung
                dw      015022243163       ; Fortsetzung
                dw      004611233432       ; Fortsetzung
                dw      004515042544       ; Fortsetzung
                dw      040000000105       ; Fortsetzung
t_frage:        dw      014423674457       ; "Zusatztrommel loeschen [J/N]" (Ende GB)
                dw      017134630542       ; Fortsetzung
                dw      012421444563       ; Fortsetzung
                dw      003220622524       ; Fortsetzung
                dw      014211243103       ; Fortsetzung
                dw      010511234043       ; Fortsetzung
                dw      012101027432       ; Fortsetzung
                dw      010513660517       ; Fortsetzung
                dw      040000000031       ; Fortsetzung
t_pende:        dw      011123653457       ; "Programmende" (Ende KB)
                dw      006122233506       ; Fortsetzung
                dw      010511252124       ; Fortsetzung
                dw      040000022464       ; Fortsetzung
t_lband:        dw      010623641457       ; "Lochband mit ZTD in Leser 1 einlegen" (Ende KB)
                dw      006114434043       ; Fortsetzung
                dw      012406432105       ; Fortsetzung
                dw      005706471451       ; Fortsetzung
                dw      003215071571       ; Fortsetzung
                dw      003221224517       ; Fortsetzung
                dw      004523641457       ; Fortsetzung
                dw      003222222542       ; Fortsetzung
                dw      005111215001       ; Fortsetzung
                dw      006711241505       ; Fortsetzung
                dw      040000042445       ; Fortsetzung
t_lszu:         dw      007010643103       ; "lochstreifen zu lang" (Ende KB)
                dw      004522271542       ; Fortsetzung
                dw      010511223051       ; Fortsetzung
                dw      003231074432       ; Fortsetzung
                dw      046721230503       ; Fortsetzung
t_geladen:      dw      006434674457       ; "ZTD geladen mit Programm-ID 1" (Ende KB)
                dw      004515647432       ; Fortsetzung
                dw      004515030503       ; Fortsetzung
                dw      005125015105       ; Fortsetzung
                dw      012713615163       ; Fortsetzung
                dw      006721444517       ; Fortsetzung
                dw      012425030511       ; Fortsetzung
                dw      006412227500       ; Fortsetzung
                dw      040000247432       ; Fortsetzung
t_keinrep:      dw      004523651057       ; "Kein Repository gefunden" (Ende KB)
                dw      005706442451       ; Fortsetzung
                dw      012711247511       ; Fortsetzung
                dw      016312261106       ; Fortsetzung
                dw      003232044506       ; Fortsetzung
                dw      014411422467       ; Fortsetzung
                dw      050511232105       ; Fortsetzung
t_uprepo:       dw      003225662057       ; "UP Repository pruefen" (Ende KB)
                dw      012711247511       ; Fortsetzung
                dw      016312261106       ; Fortsetzung
                dw      003232044506       ; Fortsetzung
                dw      004531044527       ; Fortsetzung
                dw      040021222446       ; Fortsetzung
                bend                         ; Ende des Textblocks
;#TEXTE-ENDE

; ---- Spurpuffer (je auf einer 040-Grenze, Spur = Adresse div 040); Inhalt erst mit den echten UP
                equ40   *                    ; SPUF-00 auf einer 040-Grenze
spuf00:         db      040                  ; SPUF-00: Spurpuffer fuer Spur 0 von ZT 0 (32 Zellen)
                equ40   *                    ; SPUF-PN auf einer Spurgrenze (11a), 2 Spuren
spufpn:         db      0100                 ; SPUF-PN: Spurpuffer Namensverzeichnis, 2 Spuren = 64 Zellen (Verzeichnisspuren 1 und 2), vom Hauptprogramm mit zwei 441 geloescht
                equ40   *                    ; Puffer Programmcode (1 Spur) auf einer Spurgrenze
spufpc:         db      040                  ; Programmcode: 1 Spur = 32 Zellen (Platzhalter, wird noch nicht benutzt)
schluss:        end

; Sollwerte von Hand hergeleitet (Weg 3: Repository vorhanden, Antwort J, ZTD geladen; seit 09.11.2026 Name als kat5 in einer Zelle, Eintrag zu 2 Zellen, Verzeichnis Spuren 1 bis 32, erste Programmspur 33):
; Eingabe (Datei zil.txt): Um. KB (nach der Frage steht KBGB = 1), j n (KB, werden uebergangen), Um. GB, a (Zeichen ohne Antwort, wird uebergangen), j (= J, Ja).
;   Um. GB setzt KBGB := 1, die Antwort J setzt R2 := 1, danach ztinit (keine Ausschrift, KBGB bleibt 1) und status := 3; der Ja-Weg laeuft bis zur Schlussmeldung.
; Ausgabe auf SW, zuerst eine Zeilenschaltung (leere erste Zeile, 1b), dann je Zeile eine Ausschrift (Umschaltzeichen im Text, Ausgabe wie bisher mit dtm);
;   nach der Frage folgt wegen 7a eine leere Zeile (Zeilenschaltung nach der Antwort J), dann:
;   UP Repository pruefen / Repository gefunden / Zusatztrommel loeschen [J/N] / (leere Zeile, 7a; ztinit, pname, neuanl und hschl geben nichts aus) /
;   Lochband mit ZTD in Leser 1 einlegen / ZTD geladen mit Programm-ID 1   (die Elemente 16 und 17 schreiben auf die ZT und geben nichts aus)
; Zellen und Register nach dem Lauf: status = 3 (Zelle 0001),
;   KBGB = 0 (Zelle 7775: nach Um. GB 1, ztinit laesst sie unberuehrt, dann die Ausschrift des UP pname mit Um. KB vorweg; die letzte Ausschrift "ZTD geladen mit Programm-ID 1" endet in KB),
;   R2 = 6 nach hschl (Sektoranzahl = 2 * 3 Eingaben, von hschl geliefert; Element 16 setzt R2 danach fuer neuanl auf 0, Endwert R2 = 0 und R3 = 1: der Streifen hschl_zil.txt hat 3 Typ-10-Eingaben und /),
;   SPUF-PN Zelle 1 = Wort 2 von ZTD = 20010410000 + 6 = 20010410006, nach 16 auch auf ZT 0 Spur 1.
; hschl (Makro HSCHL mit UP eingabe = TYP10EINGABE, Typ 10, Aufgabenstellung 5a, 6c und 7a), von Hand hergeleitet: R1 = Puffer Programmcode, R2 = 0 (Trommel), R3 = 33 (Spur, oktal 41): ZT 0 Spur 33 = ZT-Zellen 33 * 32 = 1056 dez = 02040 bis 02077.
;   Streifen hschl_zil.txt = + 0 7 7 1 2 3 4 5 6 7 0 1 2 : WRZL / 2 Leertaste 1 Leertaste 1 2 3 . WRZL / 2 . WRZL / (3 Eingaben, dann WRZL und /):
;   Eingabe 1 (Beispiel 1 aus 7a): Kz + (20) und 0 (00): Wort 2 = 20 * 2^6 + 00 = 02000; 12 Ziffern, die letzten 11 bleiben: Wort 1 = 71234567012. Eingabe 2: Kz 2 (02) und 1 (01): Wort 2 = 02 * 2^6 + 01 = 0201, Ziffern 1 2 3: Wort 1 = 123.
;   Eingabe 3 (Beispiel 3 aus 7a): Kz 2, Punkt vor dem 2. Kennzeichen: Wort 2 = 02 * 2^6 = 0200, Wort 1 = 0. Leertaste und WRZL werden uebergangen. Je Eingabe zwei Zellen (Wort 1, Wort 2): 71234567012, 02000, 123, 0201, 0, 0200 = 6 Sektoren.
;   R3 bleibt 33 (hschl aendert R3 nicht, MELDUNG auch nicht), R1 bleibt unveraendert (HSCHL stellt es zurueck), KBGB bleibt unveraendert. Bis zum Streifenende ist nur eine Spur zu schreiben (6 Worte), ein Spurwechsel kommt nicht vor.
; pname (Makro PNAME, Aufgabenstellung 6b), von Hand hergeleitet: Zaehler (SPUF-00 Zelle 17) war 0, also ID 1 und Eintrag ab SPUF-PN Zelle 2 * 0 = 0 (Zellen 0 und 1); Trommel 0, Spur 32 + 1 = 33 (oktal 41): p = 33;
;   Wort 2 = Typ 10 (20000000000) + ID 1 * 2^21 (10000000) + p * 2^12 (410000) = 20010410000, danach 16: Laenge 6 -> 20010410006. Wort 1 = kat5 "ztd": z = 021 + 25 = 052, t = 021 + 19 = 044, d = 021 + 3 = 024
;   in z3 bis z8, z9 bis z14 und z15 bis z20 = 0 52 44 24 00 00 = 05244240000 (keine Endemarke). Der Zaehler in SPUF-00 Zelle 17 ist danach 1 (im Puffer; Element 17 schreibt ihn auf die ZT).
;   (Layout laut .dmp: SPUF-00 auf 1300, SPUF-PN auf 1340 (64 Zellen), Zelle 1 also auf 1341; die Lage ist Layout, nicht Sollwert)
; neuanl (Makro NEUANL, Aufgabenstellung 6 Punkt 7), von Hand hergeleitet: R1 = SPUF-PN, R2 = 0, R3 = 1: SPUF-PN Zellen 0 bis 31 auf ZT 0 Spur 1 (ZT-Zellen 1 * 32 = 040 bis 077), Zellen 32 bis 63 auf Spur 2 (0100 bis 0137).
;   Beim ERSTEN Aufruf (Element 14) steht in SPUF-PN nur der Eintrag von PNAME ohne Laenge (Wort 2 = 20010410000); den ZWEITEN Aufruf (Element 16) macht das Hauptprogramm nach dem Eintragen der Laenge:
;   danach steht auf ZT 0 Spur 1: 0040 = 05244240000 (Wort 1 von ID 1), 0041 = Wort 2 = 20010410006 (Laenge 6, ueberschreibt das Wort mit Laenge 0), 0042 = 0 (Wort 1 von ID 2);
;   die zweite Spur ist ganz 0 (0100). Beide Aufrufe mit R1 = SPUF-PN, R2 = 0, R3 = 1.
; Element 17 (von Hand hergeleitet): Anwahl 5100 030 (ZT 0), dann 601 mit Spur 0 (zzz0 = 0000) und Adresse SPUF-00: die 32 Zellen von SPUF-00 gehen auf Spur 0 von ZT 0 (ZT-Zellen 0 bis 037). Gegenueber ztinit
;   hat PNAME nur Zelle 17 geaendert (Zaehler 0 -> 1): ZT 0021 = 1; Zelle 0 (52525252525), 16 (1), 18 (0) und 19 (040) sind unveraendert. Die Zellen 18 und 19 werden nicht nachgefuehrt (md 8 Punkt 4 offen).
; ztinit (Spezifikation ZT-Repository_Aufgabenstellung 6a): SPUF-00 (1300 bis 1337) enthaelt danach Spur 0 von ZT 0: Zelle 0 (1300) = 52525252525, Zelle 16 (1320) = 1, Zelle 19 (1323) = 040 (32 dezimal), sonst 0 (Zelle 17 setzt danach PNAME auf 1);
;   dieselben Werte stehen auf ZT 0 (ZT-Zellen 0000, 0020, 0021, 0022, 0023, geschrieben als 513. Ausgabe von ztinit). Die Marke ;#ZTROMMEL=LEER macht alle ZT vorher zu 0.
;#PRUEFE-START
; 0001: 00000000003   # status: Weg 3 (Ja)
; 7775: 00000000000   # KBGB: letzte Ausschrift endet in KB
; 7776: 00000000000   # R2: 0 (Trommelnummer, von Element 16 fuer neuanl gesetzt; die Sektoranzahl 6 von hschl steht in SPUF-PN und auf der ZT)
; 7774: 00000000001   # R3: Spurnummer 1 (Element 16 setzt sie fuer neuanl nach hschl); neuanl und MELDUNG ruehren R3 nicht an
; 1340: 05244240000   # SPUF-PN Zelle 0: Wort 1 = Name ztd (kat5), von PNAME eingetragen
; 1341: 20010410006   # SPUF-PN Zelle 1: Wort 2 von ZTD = 20010410000 (PNAME) + Sektoranzahl 6 (Element 16)
; 1342: 00000000000   # SPUF-PN Zelle 2: Wort 1 von ID 2, nie beschrieben
; 1300: 52525252525   # SPUF-00 Zelle 0: Repository-Kennzeichen (von ztinit aufgebaut)
; 1320: 00000000001   # SPUF-00 Zelle 16: Repository-Kopf
; 1321: 00000000001   # SPUF-00 Zelle 17: Zaehler = 1 (von PNAME nachgefuehrt, nur im Puffer)
; 1323: 00000000040   # SPUF-00 Zelle 19: letzte belegte Spur (40 oktal = 32 dezimal)
; 1440: 71234567012   # Puffer Programmcode Zelle 0: Eingabe 1 Wort 1 (von hschl gelesen und abgelegt)
; 1441: 00000002000   # Zelle 1: Eingabe 1 Wort 2 (Kz + 0)
; 1442: 00000000123   # Zelle 2: Eingabe 2 Wort 1
; 1443: 00000000201   # Zelle 3: Eingabe 2 Wort 2 (Kz 2 1)
; 1444: 00000000000   # Zelle 4: Eingabe 3 Wort 1
; 1445: 00000000200   # Zelle 5: Eingabe 3 Wort 2 (Kz 2)
; 1446: 00000000000   # Zelle 6: Rest 0 (Puffer vorher mit 441 geloescht)
; ZT-Zellen-Pruefung:
; 0-0000: 52525252525   # ZT 0 Spur 0 Zelle 0: Repository-Kennzeichen
; 0-0020: 00000000001   # Zelle 16: Repository-Kopf
; 0-0021: 00000000001   # Zelle 17: Zaehler = 1 (Element 17 hat SPUF-00 nach PNAME auf die ZT geschrieben)
; 0-0022: 00000000000   # Zelle 18: letzte belegte Trommel
; 0-0023: 00000000040   # Zelle 19: letzte belegte Spur (32 dezimal)
; 0-0040: 05244240000   # Verzeichnis Spur 1 Zelle 0: Wort 1 = Name ztd (kat5; von neuanl, Element 14, geschrieben)
; 0-0041: 20010410006   # Verzeichnis Spur 1 Zelle 1: Wort 2 mit Laenge 6 (Element 14 schrieb Laenge 0, Element 16 hat SPUF-PN nach dem Eintragen der Laenge noch einmal geschrieben)
; 0-0042: 00000000000   # Verzeichnis Spur 1 Zelle 2: Wort 1 von ID 2, nie beschrieben
; 0-0043: 00000000000   # Spur 1 Zelle 3: nie beschrieben (Puffer leer ausser ID 1)
; 0-0100: 00000000000   # Spur 2 Zelle 0 (zweite Haelfte von SPUF-PN): 0
; 0-2040: 71234567012   # ZT 0 Spur 33 Zelle 0 (ZTD): Eingabe 1 Wort 1, von hschl geschrieben
; 0-2041: 00000002000   # Zelle 1: Eingabe 1 Wort 2
; 0-2042: 00000000123   # Zelle 2: Eingabe 2 Wort 1
; 0-2043: 00000000201   # Zelle 3: Eingabe 2 Wort 2
; 0-2044: 00000000000   # Zelle 4: Eingabe 3 Wort 1
; 0-2045: 00000000200   # Zelle 5: Eingabe 3 Wort 2
; 0-2046: 00000000000   # Rest der Spur 33: 0
; 0-2077: 00000000000   # letzte Zelle der Spur 33: 0
; 0-2100: 00000000000   # Spur 34 nicht beschrieben
; 0-3040: 00000000000   # frueher erste Programmspur 49: jetzt nicht beschrieben
;#PRUEFE-ENDE
