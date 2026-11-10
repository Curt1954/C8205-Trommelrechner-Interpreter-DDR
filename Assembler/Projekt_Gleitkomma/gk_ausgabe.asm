; gk_ausgabe.asm  --  Projekt_Gleitkomma: Gleitkommazahl (dwg-Format) zur Basis 10 ausgeben (gk_ausgabe) und einlesen (gk_eingabe)
; STAND 07.11.2026: gk_ausgabe (Entwurf S1 bis S8) und gk_eingabe in einer Datei, gemeinsame Tabellen. Siehe Datei aufgabe.
;
; ===== UP gk_ausgabe: <AC> als normalisierte Gleitkommazahl zur Basis 10 auf dem angewaehlten Kanal (Schreibwerk) ausgeben, gibt nichts zurueck.
; ANNAHMEN (offen, bitte bestaetigen): A1 dvg = dwg (Doku 3.3.21: z0 Vorzeichen, z1..z6 Exponent e+32, z7..z32 Mantisse 0,5<=m<1).
;   A2 Druckbild [+|-]0,dddddddde[+|-]ee (Dezimalkomma), 8 Ziffern (die 8. Ziffer ist wegen der 26-Bit-Mantisse nicht immer exakt), 0,1<=Mantisse<1.
;   A3 Das UP druckt nur KB-Zeichen, erwartet KB, laesst KB. A4 Aufruf ohne 025: Aufrufer legt das Rueckkehrwort nach gk_rueck,
;   laedt die Zahl in den AC, Sprung 000 gk_ausgabe. A5 Das UP zerstoert AC und eigene Zellen und die Arbeitsspur 7640 bis 7677.
; VERFAHREN: Betrag und Vorzeichen; Null gesondert. Dezimalexponent E per Vergleich mit Tabelle T10 (10^-9 bis 10^9, Abbruchwort 0).
;   N = |z| * 10^(8-E) als ganze Zahl 10^7 bis 10^8: Mantisse (32-Bit-Bruch) mal Tabellenfaktor P (Bruch, Multiplikation 6.1.1)
;   dann s-fach nach rechts mit Rundung, s = 64 - e' - p. Ist N = 10^8, dann N = 10^7 und E = E+1. Ziffern durch Subtraktion der Zehnerpotenzen.
;
; ===== UP gk_eingabe: liest eine Zahl vom angewaehlten Eingabekanal (K0, Schreibwerk/Tastatur) und gibt sie als dwg-Zahl im <AC> zurueck.
; Aufruf (wie A4): Aufrufer waehlt den Eingabekanal an, legt das Rueckkehrwort nach gk_rueck_ein, Sprung 000 gk_eingabe; Ergebnis im AC.
; ANNAHMEN (offen, bitte bestaetigen): E1 Eingabeform [+|-] Ziffern [, Ziffern] [e|E [+|-] Ziffern] und ein Punkt als Eingabeende, z. B. -0,0000000000001E5. ; das Komma trennt die
;   Nachkommastellen; Leertaste (ZR), Zeilenschaltung (WRZL), Umschaltzeichen und Tabulator
;   werden uebergangen (E2: KB/GB wird nicht nachgefuehrt, Festlegung 030 offen). E3 Es zaehlen die ersten 9 bis 10 Stellen (Betrag unter 4,3E9); weitere Ziffern vor dem Komma
;   verschieben nur den Exponenten, weitere Nachkommaziffern werden verworfen. E4 Keine Pruefung der Eingabe (Festlegung 005 sinngemaess):
;   ein Zeichen, das nicht in der Tabelle vorgesehen ist (Buchstaben ausser e), liefert einen Zellenwert und wirkt wie e oder wie eine Ziffer.
;   E5 Ergebnis ohne Bereichspruefung (dwg-Bereich 2^-33 bis fast 2^31); die Rundung ist wegen der Tabelle T10 (26-Bit-Mantisse) bis etwa 2 Einheiten
;   der letzten Stelle ungenau, wenn der Dezimalexponent nicht 0 ist. E6 Das UP zerstoert AC, eigene Zellen und die Arbeitsspur 7640 bis 7677.
; VERFAHREN: Betrag aus Stellen als ganze Zahl N, Dezimalexponent k = Exponent - Zahl der Nachkommastellen; N auf 32-Bit-Bruch a (0,5 bis 1) normieren;
;   a mal 10^k aus T10 (Schritte zu hoechstens 10^+-9, Bruchmultiplikation 6.1.1, nach jedem Schritt normiert); Rundung auf 26 Bit, Packen, Vorzeichen.
; Zeichentabelle tab (0100-Grenze, 64 Zellen, Festlegung 014): in den Zellen unbelegter Zeichen liegen die Zeichen-Ausgabebefehle zif,
;   die Zehnerpotenzen pw0 und alle Arbeitszellen beider UP (Eingabe und Ausgabe laufen nie gleichzeitig, sie teilen sich die Arbeitszellen).
; Zellenverwendung Eingabe: nn = N, dcnt = Phase (0 vor Punkt, 1 hinter Punkt, 2 Exponent), pwv = Vorzeichenmerker, ww = Exponentenwert,
;   ea = Dezimalexponent k in Adresseneinheiten (01000), idx = Ziffer-gelesen-Merker, zabs = Vorzeichen der Mantisse, tmp = Ziffer bzw. Schritt,
;   aa = Bruch a, e1 = Exponentenfeld; die Tabelle T10 mit Faktoren und die Arbeitsspur 7640 dienen der Multiplikation.
; Speicher: ohne Testhauptprogramm beginnt gk_ausgabe bei 0000, dann gk_eingabe, Literale in der Luecke vor tab, Zeichentabelle tab (0500), Tabellen T10/P/p.
; Das Testhauptprogramm liegt relativ ab 02000 (hinter den UP). Ein BIS-Objektprogramm laedt nie nach 0000 bis 0377 und beschreibt keine Zelle von 0000 bis 01777;
; die Lage bestimmt der Lader mit der Leitadresse (zum Beispiel 2000: UP ab 2000, Hauptprogramm ab 4000).
;
; Testfaelle: Das Hauptprogramm liest Zahlen ein (K0, Datei Test-virtuelleGeraete/T-SW-Eingabe/gk_ausgabe.txt, jede Zahl mit Punkt beendet) und gibt jede mit gk_ausgabe aus.
;     Eingabe -16.        -> -0,16000000e+02      Eingabe 0,5.         -> +0,50000000e+00      Eingabe 1,5e3.       -> +0,15000000e+04
;     Eingabe 2147483616. -> +0,21474836e+10      Eingabe 0,001.       -> +0,10000000e-02      Eingabe 0.           -> +0,00000000e+00
;     Eingabe 100.        -> +0,10000000e+03      Eingabe -12,5e+1.    -> -0,12500000e+03      Eingabe 123456789.   -> +0,12345679e+09
;     Eingabe 999999999.  -> +0,10000000e+10      Eingabe -0,0000000000001E5. -> -0,10000000e-07
;
;#TROMMEL=LEER
;#PROT STUFE=2
;#BZ=1777
;#TASTENFOLGE H SW=1 M+ E M- R
; Test: Befehlszaehler 1777 (#BZ), Tastenfolge H SW=1 M+ E M- R (E zaehlt 1 dazu: Start bei 02000); Schalter SW=1 noetig fuer die K0-Eingabe von e und WRZL.
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/gk_ausgabe.txt
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/gk_ausgabe
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/gk_ausgabe-sw-ausgabe.txt
                start                ; Zaehlung beginnt bei 0000 (relativ): die UP ab 0000, das Testhauptprogramm ab 02000
gk_ausgabe:     240     zabs         ; Eintritt, Zahl im AC: merken
                040     gk_n         ; z0 gesetzt: negativ
                dto     +            ; Vorzeichen + drucken
                000     gk_c         ; weiter
gk_n:           dto     -            ; Vorzeichen - drucken
                211     zabs         ; AC := z
                200     #037777777777 ; z0 loeschen: Betrag
                240     zabs         ; Betrag merken
gk_c:           211     zabs         ; AC := |z|
                330     #0           ; mit 0 vergleichen
                170     gk_null      ; gleich: Null
                200     #0377777777  ; Mantisse (26 Bit) ausblenden
                644     07662        ; 6 links: Bruch m = 0,5 bis 1 (32 Bit)
                240     aa           ; Bruch a merken
                211     zabs         ; AC := |z|
                642     07656        ; 26 rechts: e' = e + 32
                240     e1           ; e' merken
                211     @t10_19      ; AC := Adresse des letzten Tabellenworts (10^9)
                240     idx          ; Suchzeiger
gk_sl:          211     idx          ; Suchschleife: AC := Zeiger
                251     0            ; AC := T10[Zeiger]
                240     tmp          ; Tabellenwert merken
                211     zabs         ; AC := |z|
                330     tmp          ; |z| mit Tabellenwert vergleichen
                150     gk_gef       ; |z| >= Tabellenwert: gefunden (Abbruchwort 0 trifft immer)
                211     idx          ; Zeiger
                220     #01000       ; ein Wort tiefer
                240     idx          ; Zeiger merken
                000     gk_sl        ; weiter suchen
gk_gef:         211     idx          ; Zeiger i
                220     @t10_9       ; i - 9 = E (in Adresseneinheiten)
                240     ea           ; E * 01000 merken
                211     aa           ; Bruch a
                440     07640        ; a in alle Zellen der Arbeitsspur
                211     idx          ; Zeiger
                210     #024000      ; 20 Worte weiter: Tabelle P
                251     0            ; AC := P (Faktor)
                472     07640        ; Teilprodukte
                211     #020000000000 ; Rundung 2^-1
                412     07640        ; AC := a * P
                240     ww           ; Produkt merken
                211     idx          ; Zeiger
                210     #050000      ; 40 Worte weiter: Tabelle p
                251     0            ; AC := p
                240     pq           ; p merken
                211     #62          ; 62
                220     e1           ; - e'
                220     pq           ; - p = s - 2
                240     cnt          ; Zaehler
gk_sh:          211     ww           ; Schiebeschleife: AC := Produkt
                212     #0           ; 1 rechts
                240     ww           ; merken
                211     cnt          ; Zaehler
                220     #1           ; - 1
                240     cnt          ; merken
                050     gk_sh        ; s-1 Schritte
                211     ww           ; AC := Produkt
                210     #1           ; + 1 (Rundung)
                212     #0           ; letzter Schritt rechts
                240     nn           ; N = 10^7 bis 10^8
                220     #100000000   ; N - 10^8
                040     gk_prt       ; kleiner: in Ordnung
                211     #10000000    ; N := 10^7
                240     nn           ; merken
                211     ea           ; E
                210     #01000       ; E + 1
                240     ea           ; merken
                000     gk_prt       ; drucken
gk_null:        241     nn           ; Null: N := 0
                241     ea           ; E := 0
gk_prt:         dto     0            ; Druck: 0
                dto     ,            ; Dezimalkomma
                211     @pw0         ; Zeiger auf 10^7
                240     pwi          ; merken
                211     #7           ; 8 Ziffern
                240     dcnt         ; Zaehler
gk_nd:          211     pwi          ; naechste Ziffer: Zeiger
                251     0            ; AC := Zehnerpotenz
                240     pwv          ; merken
                241     dg           ; Ziffer := 0
gk_sb:          211     nn           ; Subtraktionsschleife: N
                220     pwv          ; - Zehnerpotenz
                040     gk_sd        ; negativ: Ziffer fertig
                240     nn           ; N verkleinern
                211     dg           ; Ziffer
                210     #01000       ; + 1 (Adresseneinheit)
                240     dg           ; merken
                000     gk_sb        ; weiter
gk_sd:          025     prdig        ; Ziffer drucken
                211     pwi          ; Zeiger
                210     #01000       ; naechstes Wort
                240     pwi          ; merken
                211     dcnt         ; Zaehler
                220     #1           ; - 1
                240     dcnt         ; merken
                050     gk_nd        ; 8 Ziffern
                dto     e            ; Exponentenzeichen
                211     ea           ; E
                040     gk_en        ; negativ
                dto     +            ; Vorzeichen +
                000     gk_ex        ; weiter
gk_en:          dto     -            ; Vorzeichen -
                221     ea           ; AC := -E
                240     ea           ; |E| merken
gk_ex:          211     ea           ; |E|
                220     #012000      ; - 10
                040     gk_t0        ; unter 10: Zehnerziffer 0
                240     ea           ; |E| - 10
                211     #01000       ; Ziffer 1
                240     dg           ; merken
                000     gk_t1        ; drucken
gk_t0:          241     dg           ; Ziffer 0
gk_t1:          025     prdig        ; Zehnerziffer drucken
                211     ea           ; Einerziffer
                240     dg           ; merken
                025     prdig        ; Einerziffer drucken
gk_rueck:       db      1            ; Rueckkehrwort vom Aufrufer, wird zuletzt durchlaufen (010)
prdig:          240     pr_rueck     ; UP Ziffer drucken: Rueckkehrwort sichern
                211     dg           ; Ziffer * 01000
                210     @zif         ; + Adresse der Ausgabebefehle
                251     0            ; AC := Ausgabebefehl der Ziffer
                240     pr           ; auf die naechste Zelle legen
pr:             db      1            ; Laufzeit: Ausgabebefehl, druckt die Ziffer
pr_rueck:       db      1            ; Rueckkehrwort, wird durchlaufen (010)

; ---- UP gk_eingabe: Zahl lesen bis zum Punkt (Eingabeende), Ergebnis dwg im AC. Rueckkehrwort liegt auf gk_rueck_ein (am UP-Ende sequentiell, Festlegung 010)
gk_eingabe:     241     nn           ; N := 0
                241     dcnt         ; Phase := 0 (vor dem Punkt)
                241     pwv          ; Vorzeichenmerker := 0
                241     ea           ; Dezimalexponent k := 0
gk_rd:          011     tab          ; Zeichen lesen: AC := Tabellenzelle (Sprungzeichen springen selbst)
                330     #10          ; Vergleich mit 10
                170     gk_rd        ; gleich 10: Plus, uebergehen
                150     gk_e         ; groesser: e
gk_dg:          240     tmp          ; Ziffer merken
                211     dcnt         ; Phase
                330     #2           ; Exponent?
                170     gk_xz        ; ja: Exponentenziffer
                211     nn           ; N
                330     #400000000   ; noch Platz fuer eine Stelle (N*10+9 < 2^32)?
                150     gk_fl        ; nein
                004     *+1          ; 2 N
                004     *+1          ; 4 N
                210     nn           ; 5 N
                004     *+1          ; 10 N
                210     tmp          ; + Ziffer
                240     nn           ; N merken
                211     dcnt         ; Phase
                330     #0           ; vor dem Punkt?
                170     gk_rd        ; ja: weiter
                211     ea           ; hinter dem Punkt: k := k - 1
                220     #01000       ; ... - 1
                000     gk_ke        ; speichern
gk_fl:          211     dcnt         ; N voll: Phase
                330     #0           ; vor dem Punkt?
                170     gk_pi        ; ja: k := k + 1
                000     gk_rd        ; nein: Ziffer verwerfen
gk_pi:          211     ea           ; k
                210     #01000       ; + 1
gk_ke:          240     ea           ; k merken
                000     gk_rd        ; naechstes Zeichen
gk_xz:          211     ww           ; Exponentenziffer: Exponent
                004     *+1          ; 2 x
                004     *+1          ; 4 x
                210     ww           ; 5 x
                004     *+1          ; 10 x
                210     tmp          ; + Ziffer
                240     ww           ; merken
                000     gk_rd        ; weiter
gk_e:           211     pwv          ; e: Vorzeichen der Mantisse
                240     zabs         ; merken
                241     pwv          ; Vorzeichenmerker := 0 (jetzt fuer den Exponenten)
                241     ww           ; Exponentenwert := 0
                211     #2           ; Phase 2
                240     dcnt         ; merken
                000     gk_rd        ; weiter
gk_pt:          211     #1           ; Komma: Phase 1 (Nachkommastellen)
                240     dcnt         ; merken
                000     gk_rd        ; weiter
gk_mi:          211     #1           ; Minus: Merker setzen
                240     pwv          ; merken
                000     gk_rd        ; weiter
gk_te:          211     dcnt         ; Phase
                330     #2           ; Exponent vorhanden?
                170     gk_x         ; ja
                211     pwv          ; nein: Merker ist das Vorzeichen der Mantisse
                240     zabs         ; merken
                000     gk_nx        ; weiter
gk_x:           211     ww           ; Exponentenwert
                644     07653        ; 9 links: in Adresseneinheiten
                240     tmp          ; merken
                211     pwv          ; Vorzeichen des Exponenten
                330     #0           ; Vergleich mit 0
                211     ea           ; k
                170     gk_pe        ; Exponent positiv
                220     tmp          ; k - Exponent
                000     gk_ne        ; weiter
gk_pe:          210     tmp          ; k + Exponent
gk_ne:          240     ea           ; k merken
gk_nx:          211     #0100        ; Exponentenfeld fuer N: 64
                240     e1           ; merken
                211     nn           ; N
                330     #0           ; Null?
                170     gk_rueck_ein ; ja: Ergebnis 0 (AC = 0)
gk_nl:          330     #020000000000 ; Normieren: Bit z1 gesetzt?
                150     gk_nf        ; ja: fertig
                004     *+1          ; sonst 1 links
                240     nn           ; merken
                211     e1           ; Exponentenfeld
                220     #1           ; - 1
                240     e1           ; merken
                211     nn           ; AC := N
                000     gk_nl        ; weiter
gk_nf:          240     aa           ; Bruch a (0,5 bis 1)
gk_ml:          211     ea           ; Multiplikationsschleife: k
                330     #0           ; fertig?
                170     gk_pk        ; ja: packen
                330     #011000      ; k mit +9 vergleichen
                140     gk_a         ; kleiner oder gleich
                211     #011000      ; k := +9
gk_a:           330     #-011000     ; mit -9 vergleichen
                150     gk_b         ; groesser oder gleich
                211     #-011000     ; k := -9
gk_b:           240     tmp          ; Schritt j
                211     @t10_0       ; Adresse von 10^0
                210     tmp          ; + j: Adresse von 10^j
                251     0            ; AC := Tabellenwort (dwg)
                240     idx          ; merken
                200     #0377777777  ; Mantisse (26 Bit)
                644     07662        ; 6 links: Bruch m (32 Bit)
                240     ww           ; merken
                211     aa           ; Bruch a
                440     07640        ; a in alle Zellen der Arbeitsspur
                211     ww           ; m
                472     07640        ; Teilprodukte
                211     #020000000000 ; Rundung 2^-1
                412     07640        ; AC := a * m
                240     aa           ; merken
                211     idx          ; Tabellenwort
                642     07656        ; 26 rechts: Exponentenfeld
                210     e1           ; + e1
                220     #040         ; - 32
                240     e1           ; merken
                211     aa           ; Produkt
                330     #020000000000 ; Bit z1 gesetzt?
                150     gk_n1        ; ja
                004     *+1          ; sonst 1 links
                240     aa           ; merken
                211     e1           ; Exponentenfeld
                220     #1           ; - 1
                240     e1           ; merken
gk_n1:          211     ea           ; k
                220     tmp          ; - j
                240     ea           ; merken
                000     gk_ml        ; weiter
gk_pk:          211     aa           ; Packen: Bruch a
                642     07677        ; 5 rechts
                210     #1           ; + 1 (Rundung, kein Ueberlauf moeglich)
                642     07663        ; 1 rechts: M = 26-Bit-Mantisse (2^25 bis 2^26)
                240     aa           ; merken
                642     07656        ; 26 rechts: 1 bei Rundungsueberlauf (M = 2^26), sonst 0
                644     07673        ; 25 links: 2^25 bei Ueberlauf (Exponent +1, Mantisse 0,5)
                210     aa           ; + M
                240     aa           ; merken
                211     e1           ; Exponentenfeld
                644     07656        ; 26 links
                210     aa           ; + Mantisse
                240     aa           ; merken
                211     zabs         ; Vorzeichen
                330     #0           ; positiv?
                211     aa           ; AC := Ergebnis
                170     gk_rueck_ein ; ja: zurueck
                210     #040000000000 ; z0 setzen: negativ (Wert -2^32 addieren)
gk_rueck_ein:   db      1            ; Laufzeit: Rueckkehrwort (am UP-Ende sequentiell erreicht)


; ---- Zeichentabelle (64 Zellen auf einer 0100-Grenze, Eingabeadresse = Zellenadresse ODER tab), kein begin/bend (dto im Block nicht zulaessig)
;      Zellen der Ziffern = Ziffernwert, Plus = 10, e = 11. Sprungzeichen: Zelle ist ein Sprung. Unbelegte Zellen: Daten (Festlegung 014).
                equ100  *            ; tab muss durch 0100 teilbar sein
tab:            dw      0            ; 00: Ziffer 0 (Tabellenanfang)
                dw      1            ; 01: Ziffer 1
                dw      2            ; 02: Ziffer 2
                dw      3            ; 03: Ziffer 3
                dw      4            ; 04: Ziffer 4
                dw      5            ; 05: Ziffer 5
                dw      6            ; 06: Ziffer 6
                dw      7            ; 07: Ziffer 7
                dw      8            ; 10: Ziffer 8
                dw      9            ; 11: Ziffer 9
                000     gk_rd        ; 12: Leertaste: Sprungzeichen, uebergehen
zabs:           db      1            ; 13: Arbeitszelle |z| bzw. Vorzeichen der Mantisse
aa:             db      1            ; 14: Arbeitszelle Bruch der Mantisse
                000     gk_rd        ; 15: Doppelpunkt: Sprungzeichen, uebergehen
                000     gk_rd        ; 16: Irrung Satz: Sprungzeichen, uebergehen
e1:             db      1            ; 17: Arbeitszelle e'
                dw      10           ; 20: Plus: Wert 10
idx:            db      1            ; 21: Arbeitszelle Suchzeiger bzw. Tabellenwort
tmp:            db      1            ; 22: Arbeitszelle Tabellenwert bzw. Ziffer
ea:             db      1            ; 23: Arbeitszelle E * 01000 bzw. k
ww:             db      1            ; 24: Arbeitszelle Produkt bzw. Exponentenwert
                dw      11           ; 25: e: Wert 11
pq:             db      1            ; 26: Arbeitszelle p
cnt:            db      1            ; 27: Arbeitszelle Zaehler
nn:             db      1            ; 30: Arbeitszelle N
pwi:            db      1            ; 31: Arbeitszelle Zeiger Zehnerpotenz
                000     gk_rd        ; 32: WRZL: Sprungzeichen, uebergehen
                000     gk_te        ; 33: Punkt: Sprungzeichen, Eingabeende
dcnt:           db      1            ; 34: Arbeitszelle Ziffernzaehler bzw. Phase
pwv:            db      1            ; 35: Arbeitszelle Zehnerpotenz bzw. Vorzeichenmerker
dg:             db      1            ; 36: Arbeitszelle Ziffer * 01000
                000     gk_rd        ; 37: Um. GB: Sprungzeichen, uebergehen
                000     gk_mi        ; 40: Minus: Sprungzeichen, Vorzeichen
zif:            dto     0123456789   ; 41 bis 52: Ausgabebefehle der Ziffern 0 bis 9
                dw      0            ; 53: frei
                dw      0            ; 54: frei
                dw      0            ; 55: frei
                dw      0            ; 56: frei
                000     gk_rd        ; 57: Um. KB: Sprungzeichen, uebergehen
                000     gk_rd        ; 60: Strichpunkt: Sprungzeichen, uebergehen
pw0:            dw      10000000     ; 61: Zehnerpotenzen 10^7 bis 10^0 (61 bis 70)
                dw      1000000      ; 62: 10^6
                dw      100000       ; 63: 10^5
                dw      10000        ; 64: 10^4
                dw      1000         ; 65: 10^3
                dw      100          ; 66: 10^2
                dw      10           ; 67: 10^1
                dw      1            ; 70: 10^0
                dw      0            ; 71: frei
                000     gk_rd        ; 72: BM: Sprungzeichen, uebergehen
                000     gk_pt        ; 73: Komma: Sprungzeichen, Dezimalkomma
                dw      0            ; 74: frei
                000     gk_rd        ; 75: Tabulator: Sprungzeichen, uebergehen
                dw      0            ; 76: frei
                dw      0            ; 77: frei

                begin                ; Tabellen zusammenhaengend (gemeinsam fuer Ausgabe und Eingabe): T10, P, p (je 20 Worte, Index i = E + 9)
                dw      0            ; i=0 Abbruchwort (|z| < 10^-9)
                dwg     1E-9         ; i=1: 10^-9
                dwg     1E-8         ; i=2: 10^-8
                dwg     1E-7         ; i=3: 10^-7
                dwg     1E-6         ; i=4: 10^-6
                dwg     1E-5         ; i=5: 10^-5
                dwg     1E-4         ; i=6: 10^-4
                dwg     1E-3         ; i=7: 10^-3
                dwg     1E-2         ; i=8: 10^-2
t10_9:          dwg     1E-1         ; i=9: 10^-1
t10_0:          dwg     1E0         ; i=10: 10^0
                dwg     1E1         ; i=11: 10^1
                dwg     1E2         ; i=12: 10^2
                dwg     1E3         ; i=13: 10^3
                dwg     1E4         ; i=14: 10^4
                dwg     1E5         ; i=15: 10^5
                dwg     1E6         ; i=16: 10^6
                dwg     1E7         ; i=17: 10^7
                dwg     1E8         ; i=18: 10^8
t10_19:         dwg     1E9         ; i=19: 10^9
                dw      026150536057   ; i=0: P fuer 10^(8--9)
                dw      021606744677   ; i=1: P fuer 10^(8--8)
                dw      034327724462   ; i=2: P fuer 10^(8--7)
                dw      026571420364   ; i=3: P fuer 10^(8--6)
                dw      022141163452   ; i=4: P fuer 10^(8--5)
                dw      035065122420   ; i=5: P fuer 10^(8--4)
                dw      027220733500   ; i=6: P fuer 10^(8--3)
                dw      022500574400   ; i=7: P fuer 10^(8--2)
                dw      035632624000   ; i=8: P fuer 10^(8--1)
                dw      027657020000   ; i=9: P fuer 10^(8-0)
                dw      023045500000   ; i=10: P fuer 10^(8-1)
                dw      036411000000   ; i=11: P fuer 10^(8-2)
                dw      030324000000   ; i=12: P fuer 10^(8-3)
                dw      023420000000   ; i=13: P fuer 10^(8-4)
                dw      037200000000   ; i=14: P fuer 10^(8-5)
                dw      031000000000   ; i=15: P fuer 10^(8-6)
                dw      024000000000   ; i=16: P fuer 10^(8-7)
                dw      020000000000   ; i=17: P fuer 10^(8-8)
                dw      031463146315   ; i=18: P fuer 10^(8-9)
                dw      024365605075   ; i=19: P fuer 10^(8-10)
                dw      57           ; i=0: p
                dw      54           ; i=1: p
                dw      50           ; i=2: p
                dw      47           ; i=3: p
                dw      44           ; i=4: p
                dw      40           ; i=5: p
                dw      37           ; i=6: p
                dw      34           ; i=7: p
                dw      30           ; i=8: p
                dw      27           ; i=9: p
                dw      24           ; i=10: p
                dw      20           ; i=11: p
                dw      17           ; i=12: p
                dw      14           ; i=13: p
                dw      10           ; i=14: p
                dw      7           ; i=15: p
                dw      4           ; i=16: p
                dw      1           ; i=17: p
                dw      -3           ; i=18: p
                dw      -6           ; i=19: p
                bend

; ===== TESTHAUPTPROGRAMM, relativ ab 02000 (Zahl lesen, mit gk_eingabe wandeln, mit gk_ausgabe drucken). Fuer den Routinebetrieb den Abschnitt bis
; 'ENDE TESTHAUPTPROGRAMM' entfernen. Die UP liegen relativ ab 0000, die Lage bestimmt der Lader (Leitadresse, durch 0100 teilbar).
                equ     02000        ; relative Adresse 02000
haupt:          ANWAHL  K2           ; Kanal 2 = Schreibwerk
                KB                   ; Schreibwerk auf Kleinbuchstaben (KB) schalten
                WRZL                 ; Zeilenschaltung, danach ist K0 (Eingabe) angewaehlt
lese:           211     rwe          ; Rueckkehrwort der Eingabe
                240     gk_rueck_ein ; in die Rueckkehrzelle von gk_eingabe
                000     gk_eingabe   ; Zahl einlesen, Ergebnis im AC
nache:          240     zw           ; gk-Zahl merken
                ANWAHL  K2           ; Kanal 2 = Schreibwerk
                KB                   ; Schreibwerk auf Kleinbuchstaben (KB) schalten
                211     rwa          ; Rueckkehrwort der Ausgabe
                240     gk_rueck     ; in die Rueckkehrzelle von gk_ausgabe
                211     zw           ; gk-Zahl in den AC
                000     gk_ausgabe   ; Zahl ausgeben
nacha:          WRZL                 ; Zeilenschaltung, danach ist K0 (Eingabe) angewaehlt
                211     zn           ; Zaehler
                220     #1           ; - 1
                240     zn           ; merken
                050     lese         ; noch nicht fertig: naechste Zahl
                020     0            ; Halt
rwe:            da      nache        ; Rueckkehrwort der Eingabe
rwa:            da      nacha        ; Rueckkehrwort der Ausgabe
zw:             db      1            ; gelesene gk-Zahl
zn:             dw      10           ; Zaehler: 11 Zahlen
; ===== ENDE TESTHAUPTPROGRAMM
ende:           end                  ; Ende
sp7640:         abs     07640        ; Arbeitsspur (nur Bezug)
