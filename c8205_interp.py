#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C8205-Interpreter (Python-Stuetze), interpretativer Modus: alle Zeiten = 0.

Version: 0.03-007
(Aufbau und Regeln der Versionsnummer: markdown-dateien/C8205-Versionierung.md; Abfrage: python3 c8205_interp.py --version)
REGEL: Jede Aenderung dieser Datei erhoeht den Build (zzz) um 1; dazu die Zeile "Version:" und die Konstante VERSION gemeinsam aendern.
Hauptversion und Unterversion nur auf ausdrueckliche Aufforderung des Projektinhabers erhoehen.

Aufruf:  python3 c8205_interp.py [--mdverz VERZ] [--out VERZ|DATEI.log]
         [--leser1 PFAD] [--leser2 PFAD] [--stanzer1 PFAD] [--sw-ausgabe PFAD]
         [--k0 datei=PFAD] [--knotentest] [--NO-TERMOUT] [--SW-TERMINAL] [--zwischenablage auto|tk|system]
         [--pruefe-stanzer1 DATEI] [--pruefe-sw-ausgabe DATEI] TEST.txt [TEST2.txt ...]
         python3 c8205_interp.py --version      (zeigt die Versionsnummer und endet)
         (--leser1, --leser2, --stanzer1, --sw-ausgabe und --k0 duerfen auch als Zeile in der Testdatei stehen; die Kommandozeile hat Vorrang)
         (--SW-TERMINAL: Schreibwerk-Ausgabe zusaetzlich im Fenster "SW Ausgabe"; das Fenster bleibt auch nach dem Testende offen, bis es mit X
          geschlossen wird; Text mit der Maus markieren und kopieren; NUR als Kommandozeilenschalter, nicht als Zeile in der Testdatei)
         --out mit Endung (z. B. Test-Protokolle/test1.log): das Protokoll wird genau in diese Datei geschrieben
         (fehlende Ordner werden angelegt; nur mit einem Test). Ohne Endung: Verzeichnis, Protokoll dann
         in VERZ/<Testname>/protokoll.txt (Vorgabe fuer --out: Test-Protokolle/ neben dem Skript). Eine Protokolldatei entsteht nur bei #PROT STUFE=2.

Regeln (aus "C8205-Interpreter-Durchführung_eines_Tests.md"):
  * Der Knotengraph wird WORTLAUTGETREU aus der Datei "C8205-Interpreter-Eingänge_der_Knoten.md" gelesen und abgelaufen.
  * Vereinfachende Beschreibungen duerfen den Graphen nicht veraendern. Unklares wird als Stub gemeldet
    (Abbruch mit Meldung), nie stillschweigend "repariert".
  * Formale Pruefung vor Start (Abschnitt 5); bei Unstimmigkeit startet der Test NICHT.
  * #PROT STUFE=0/1/2: 0 = kein Knotenprotokoll, 1 = Knotenzeilen auf dem Bildschirm,
    2 = Knotenzeilen nur in protokoll.txt. Die #DOK-Diagnose (Befehl 164) erscheint stets auf dem Bildschirm.
  * Befehlszeilenschalter --knotentest (Standard: aus): nur wenn gesetzt, enthalten die Knotenprotokolle
    die Zeilen der durchlaufenen Knoten (K001 KON B ..., K004 TST 002 ... -> falsch). Ohne den Schalter
    bleiben davon nur die BR-Zeilen (nach Knoten 009), Diagnose und Fehler-/Stub-Meldungen.

Aenderung 10.10.2026 (Version 0.03-007): Das Fenster "SW Ausgabe" (--SW-TERMINAL) bleibt jetzt IMMER offen, auch nach dem Ende des Tests und
  unabhaengig von der Mausposition, bis es mit X geschlossen wird (die Selbstschliessung bei Zeiger ausserhalb entfaellt, ebenso der Hinweis,
  den Mauszeiger vorher in die rechte untere Ecke zu stellen). Markieren und Kopieren wie in den Lochstreifen-Hilfsprogrammen (Anzeige/Eingabe):
  Kopieren beim Loslassen der Maustaste (auch nach Doppelklick), mit Strg+C, Strg+Umschalt+C, Strg+Einfg (auch ohne Fokus im Textfeld) und ueber
  das Kontextmenue (rechte Maustaste; macOS auch mittlere Taste/Strg+Klick) mit "Kopieren" und "Alles markieren"; Strg+A markiert alles; Rueckmeldung
  in der Titelleiste. Verfahren: Windows Win32-API (CF_UNICODETEXT, bis zu 20 Versuche), Linux/macOS/WSL zuerst wl-copy bzw. xsel (sonst xclip),
  pbcopy, clip.exe, Tk nur als Rueckfall; derselbe Text wird binnen 5 s nicht erneut abgelegt. Neuer Schalter --zwischenablage auto|tk|system
  (Vorgabe auto), wirkt nur mit --SW-TERMINAL. Das Fenster laeuft unter Linux (eigene Sitzung) und Windows (ohne Konsolenfenster) weiter,
  auch wenn der Interpreter oder sein Terminal schon beendet ist.
Aenderung 10.10.2026 (Version 0.03-006): Mit --SW-TERMINAL werden auch alle Eingaben ueber K0 (Pult-Tastatur T oder Schreibwerk SW, vom Terminal
  oder aus --k0 datei=PFAD) als Echo im Fenster "SW Ausgabe" ausgegeben, in Dunkelgelb (Ausgaben des Rechners bleiben in der Standardfarbe).
  Echo nur fuer angenommene Zeichen, in der Darstellung des Schreibwerks (a028/sw_zeichen) bei der gerade gueltigen Zeichenlage KB/GB.
  Lochbandleser (K1/K2) werden nicht ausgegeben. Ohne --SW-TERMINAL aendert sich nichts.
Aenderung 10.10.2026 (Version 0.03-005): Hilfetext (--help) und Kopfkommentar zu --SW-TERMINAL: Hinweis, dass das Fenster nur zu sehen ist, wenn der
  Mauszeiger VOR dem Aufruf in der rechten unteren Bildschirmecke steht. Keine Aenderung am Verhalten.
Aenderung 10.10.2026 (Version 0.03-004): --SW-TERMINAL oeffnet jetzt ein eigenes Ausgabefenster "SW Ausgabe" (nur Text, 130 x 36 Zeichen,
  verschiebbar, Standardposition rechts unten auf dem Desktop; Tkinter, als eigener Prozess, der Text ueber eine Pipe erhaelt). Alle
  Zeichen, die auf das Schreibwerk gehen, erscheinen darin, gleichgueltig ob --sw-ausgabe gesetzt ist; Datei bzw. Terminal bleiben wie bisher.
  Nach dem Ende des Aufrufs schliesst sich das Fenster selbst, wenn der Mauszeiger nicht darin steht; steht er darin, bleibt es offen,
  bis es mit X geschlossen wird. Ist kein Fenster moeglich (kein tkinter, keine grafische Oberflaeche), erscheint eine Warnung und der Test
  laeuft ohne Fenster weiter. Ersetzt die Spiegelung der Ausgabe ins Terminal aus Version 0.03-003. Weiterhin nur Kommandozeile.
Aenderung 10.10.2026 (Version 0.03-003): Neuer Kommandozeilenschalter --SW-TERMINAL (Standard: aus). Mit --sw-ausgabe geht die
  Schreibwerk-Ausgabe (K2) nur in die Datei; mit --SW-TERMINAL erscheint sie zusaetzlich auf dem Terminal (dunkelgelb), auch bei
  --NO-TERMOUT. Ohne --sw-ausgabe aendert der Schalter nichts (die Ausgabe geht ohnehin ans Terminal). Der Schalter wird beim
  Testlauf ausgewertet und ist nur auf der Kommandozeile zulaessig; als Zeile in der Testdatei ist er ein Formfehler.
Aenderung 09.10.2026 (Version 0.03-002): Regel zum Hochzaehlen der Versionsnummer im Kopfkommentar ergaenzt (jede Aenderung: Build + 1;
  Haupt- und Unterversion nur auf Aufforderung des Projektinhabers). Keine Aenderung am Verhalten.
Aenderung 09.10.2026 (Version 0.03-001): Versionsnummer der Form y.xx-zzz eingefuehrt (Ausgangsstand 0.03-001, festgelegt vom
  Projektinhaber; Definition: markdown-dateien/C8205-Versionierung.md). Konstante VERSION, Zeile "Version:" im Kopfkommentar und
  Schalter --version (zeigt die Version und endet). Am Ablauf der Tests und an allen Ausgaben aendert sich nichts.
Aenderung 08.10.2026: Neue Testmarken #AC=<11 Oktalstellen> und #BZ=<4 Oktalstellen> (Durchfuehrung_eines_Tests.md, Abschnitt 2).
  Sind sie angegeben, werden AC bzw. BZ vor der ersten Taste und vor jedem Befehl auf den Wert gesetzt (Anfangszustand); fehlen sie,
  bleibt alles wie bisher (AC=0, BZ=0). Eine danach abgearbeitete Taste G wirkt unveraendert wie bisher (BZ:=0, AC bleibt).
Aenderung 04.10.2026 (5): Befehlsentnahme nach X-Abbruch (GX/WX, B=5/7; Befehlsliste 4.1.6, Abb. 10): Der naechste Befehl wird ohne
  Wartezeit W1 entnommen. Die Spur kommt aus dem Befehlszaehler (AR=BZ=b+1), der Sektor aus der Trommellage in der zweiten Wortzeit nach
  dem Abbruch (= Sektor der Zusatzzelle + 2 physische Schritte, je +15 oktal). Der Befehl muss also NICHT in Zelle b+1 stehen. AR und BZ
  bleiben b+1, daher ergibt Phase III (ANWEISUNG-001) wie in der Quelle BZ = b+2. Betroffen: t002 (merkt den Entnahmefall), a044 (Sektor),
  a005 (Entnahme). Alt-Tests 0004, 0006, 0007, 0021 legten den Folgebefehl in Zelle b+1 und muessen ihn in den fälligen Sektor legen.
Aenderung 04.10.2026 (5), Tasten nach Stopp (Originaldokumentation 4.3.2.3, Abb. 19): Nach M (ohne E) mit einem Sprung mit Rueckkehrabsicht in BR
  (B=0/1, A=2, Z>=4: 025, 027, 125, 127) gilt Phase III als abgelaufen: der Ablauf beginnt nicht mehr bei Knoten 19 (der ueber Knoten 40 die
  Sprungoperation <AC>:=<AC> v Vr<BZ> ausfuehrte), sondern bei Knoten 54 (Konnektor 4) nach Umstellung A:=0 (eintritt_br). Es laufen nur
  Ueberlauftest, Resultatbehandlung und Phase II ab. Alle anderen aufgestellten BR (Ue, ST, E ohne M) beginnen weiter bei Knoten 19.
  Machine.br_tasten_m merkt, dass der BR durch M aufgestellt wurde (G und E unter M loeschen den Merker). Tests tk-001 bis tk-008.
Aenderung 04.10.2026 (4): Auch --leser1, --leser2 und --stanzer1 duerfen als Zeile in der Testdatei stehen (Durchfuehrung_eines_Tests.md,
  Abschnitt 2b), Regeln wie bei --sw-ausgabe und --k0 (in jedem Abschnitt, je Schalter hoechstens einmal, Kommandozeile hat Vorrang,
  relative Pfade vom aktuellen Verzeichnis aus). Zeigt --leser1/--leser2 in der Testdatei auf ein Verzeichnis, erscheint ein Hinweis
  (alle Dateien darin werden gelesen).
Aenderung 04.10.2026 (3): Lochbandeingabe ueberspringt "Irrung Zeichen" (Lochbild 11111111): keine Paritaetspruefung, kein FE, nicht ins AR;
  der Eingabebefehl liest das naechste Zeichen (a032; Python_Interpreter.md 8.2, 13.2; Tests lb-001 bis lb-003).
Aenderung 04.10.2026 (2), KEP-Test bsp_5_18_kep: (1) TABELLE1 Zeile 49 (Leertaste/ZWR): Sprung-Umstellung True (vorher False; Kodetabellen
  1.4/1.5/1.8). (2) Eingabe-Lesebefehl (Umstellung B:=B+2, A=1) addiert den Inhalt der Zelle (Adreßteil v Eingabeadresse) zum AC, nicht die
  Eingabeadresse selbst (Kodetabellen 1.8: Zellen 0020/0021 des KEP sind Konstanten). Python_Interpreter.md 13.2 (Ziffer 5 -> AC=...05) ist
  davon betroffen und muss angepasst werden (AC erhaelt den Inhalt der Zelle 0005).
Aenderung 04.10.2026: (1) Knotentabelle: Knoten 30 (Halt wegen Ueberlauf, Test in Knoten 28) nutzt jetzt ANWEISUNG-046 statt -030
  (liegt in der Eingaenge-Datei, der Graph wird zur Laufzeit gelesen; a046 setzt weder US noch BS). (2) ANWEISUNG-010: beim
  Ueberlaufsprung (B=0, A=7) mit vorhandenem Ueberlauf wird FUE gleichzeitig geloescht (Programmieranleitung 4.3.2.10); vorher
  haette der umgestellte Sprung an Knoten 55 angehalten. (3) Leer-Befehl 164-167 ohne Resultatbehandlung (a022) und Ueberlauf nur
  bei R=0 (a021) waren schon umgesetzt, nur die Kommentare/T2 wurden angepasst.
Aenderung 02.10.2026: bedingter Sprung mit Rueckkehrabsicht (B=0, A=6, Z>=4, Schalter SP) im Knotengraphen
  umgesetzt (T2: ANWEISUNG-008, -009, -010, -018); ANWEISUNG-029 stellt nach dem Sichern der Rueckkehradresse
  auf unbedingten Sprung um (A:=0, T2 ANWEISUNG-013) - vorher wurde das Sprungziel bei jedem Sprung mit
  Rueckkehrabsicht (024-027, 124-127) verworfen.
Aenderung 02.10.2026 (2): ANWEISUNG-029 verlor bei ungeradem <BZ> das unterste Bit (Abschneiden auf 12 Bit nach BZ>>1);
  jetzt AC := AC | (BZ << 8), das Bit landet in z24 (T2 ANWEISUNG-029, Spezialgrafik Sprung mit Rueckkehrabsicht).
Aenderung 03.10.2026: Python_Interpreter.md, Abschnitt 11 ("Neu definiert") umgesetzt: --sw-ausgabe; Lochbandleser und K0-Datei
  mit stillem Warten statt Halt bei Dateiende; K0 ohne Flag = Terminal (--k0 tastatur entfaellt, --k0 datei=PFAD auch Verzeichnis);
  formale Vorab-Pruefung der Geraetepfade; Kanaltasten K0-K3 in der Tastenfolge; --NO-TERMOUT; Rueckkehrcode 0/4/6/8/16
  (bezogen auf den zuletzt bearbeiteten Test).
Aenderung 03.10.2026 (4): Neue Pruefungen --pruefe-stanzer1 DATEI und --pruefe-sw-ausgabe DATEI (Durchfuehrung_eines_Tests.md,
  Abschnitt 3b): die vom Lauf erzeugte Stanzer- bzw. Schreibwerk-Datei wird mit einer Soll-Datei verglichen (Unterschiede als diff);
  fehlt eine der beiden Dateien oder unterscheiden sie sich, ist die Pruefung falsch. Das Ergebnis geht in "Test wahr/falsch"
  und in den Rueckkehrcode (0/6) ein. Ein reiner Stanzer-Pfad mit Schraegstrich am Ende (noch nicht vorhandenes Verzeichnis)
  gilt jetzt als Verzeichnis (vorher IsADirectoryError).
  Nachtrag: dieselben Pruefungen koennen als Zeile im Abschnitt "Pruefungen:" der Testdatei stehen
  ("--pruefe-stanzer1 DATEI", "--pruefe-sw-ausgabe DATEI", je hoechstens einmal); ein Schalter der Kommandozeile hat Vorrang.
Aenderung 03.10.2026 (5): --sw-ausgabe PFAD und --k0 datei=PFAD duerfen auch als Zeile in der Testdatei stehen (Durchfuehrung_eines_Tests.md,
  Abschnitt 2b), in jedem Abschnitt, je Schalter hoechstens einmal; ein Schalter der Kommandozeile hat Vorrang. Relative Pfade
  gelten wie auf der Kommandozeile (vom aktuellen Verzeichnis aus). Formfehler (ohne Wert, doppelt, --k0 ohne datei=) verhindern den Teststart.
Aenderung 02.10.2026 (3): Stopp-Zustaende getrennt (Originaldokumentation: Lampen US, BS, FUE). ANWEISUNG-030 (Knoten 45) setzt
  nur noch US; neu ANWEISUNG-045 (Knoten 79, bedingter Stopp, Schalter BS gesetzt) setzt BS; neu ANWEISUNG-046 (Knoten 46,
  58, 66, Halt wegen Ueberlauf) setzt weder US noch BS. Die Unterscheidung ueber m.came_from entfaellt.
Aenderung 03.10.2026 (3): Testdatei-Suche ueber den Namen ueberspringt PDF-Erzeugung/ und _work/ (dort liegen Kopien) und bevorzugt bei
  mehreren Treffern Tests/ neben dem Skript bzw. im aktuellen Ordner.
Aenderung 04.10.2026: Abgleich mit Originaldokumentation 4.3.2.5 (Ausgabe-Halt): (1) Graph: Knoten 80/81 (Ueberlauftest nach Ausgabe-/Anwahlbefehl,
  Halt wegen Ueberlauf; der Graph wird zur Laufzeit gelesen). (2) Ausgabe-Halt ohne Ausgabegeraet (K0, K3, keine Anwahl) meldet einen Stub (vorher
  stille Nicht-Ausgabe). (3) Schreibwerk (K2) wertet nur z14, z15, z17-z20 aus (SW_ZEILE), z13 (w) und z16 (p) werden ignoriert; der Stanzer bleibt
  bei allen 8 Bit (AUSGABE_ZEILE).
Aenderung 03.10.2026 (2): ANWEISUNG-017 geaendert (T2: "Wenn der Ausgabebefehl keine Kanal-Anwahl ist, wird das Zeichen auf dem
  angewaehlten Kanal ausgegeben ..."): die Zeichenausgabe (SW/Stanzer) steht jetzt in a017 (Knoten 23); a028 (Knoten 39) waehlt nur noch
  den Kanal bei Anwahlbefehlen. Verhalten nach aussen unveraendert.
Aenderung 07.10.2026: Trommel materialisiert. Die Trommel ist jetzt eine persistente Textdatei
  (virtuelle_Geraete/Trommel/trommel.txt, 4096 Zeilen aaaa: ttttttttttt). Der Interpreter liest sie
  beim Teststart, uebertraegt die Adresse:Wert-Zeilen der Testdatei initial auf die Trommel und
  schreibt jede Zelländerung eines Befehls unmittelbar als Zeilenupdate in die Datei. Neue Klasse
  Trommel und Funktion pruefe_trommeldatei; Machine.rd/Machine.wr arbeiten ueber die Trommel.
"""
import argparse
import difflib
import os
import random
import re
import subprocess
import sys
import time

VERSION = '0.03-007'   # Form y.xx-zzz; muss mit der Zeile "Version:" im Kopfkommentar uebereinstimmen (C8205-Versionierung.md)

MASK33 = (1 << 33) - 1
MASK12 = 0xFFF

TROMMEL_ZEILE_LAENGE = 18
TROMMEL_ADR_ANZAHL = 4096
TROMMEL_ZEILE_RE = re.compile(r'^([0-7]{4}): ([0-7]{11})\n$')

PHYS_LOG = [0o00,0o15,0o32,0o07,0o24,0o01,0o16,0o33,
            0o10,0o25,0o02,0o17,0o34,0o11,0o26,0o03,
            0o20,0o35,0o12,0o27,0o04,0o21,0o36,0o13,
            0o30,0o05,0o22,0o37,0o14,0o31,0o06,0o23]

TABELLE1 = [
    (1, '1', '<', '001', 60, 49, 1, False),
    (2, '2', '"', '002', 34, 50, 2, False),
    (3, '3', '≈', '023', 0, 51, 3, False),
    (4, '4', '[', '004', 91, 52, 4, False),
    (5, '5', '>', '025', 62, 53, 5, False),
    (6, '6', "'", '026', 39, 54, 6, False),
    (7, '7', '≋', '007', 0, 55, 7, False),
    (8, '8', '~', '010', 126, 56, 8, False),
    (9, '9', ']', '031', 93, 57, 9, False),
    (10, '0', '#', '020', 35, 48, 0, False),
    (11, '%', '*', '174', 42, 37, 60, False),
    (12, 'Tabulator', 'Tabulator', '155', 9, 9, 61, True),
    (13, 'q', 'Q', '130', 81, 113, 40, False),
    (14, 'w', 'W', '166', 87, 119, 54, False),
    (15, 'e', 'E', '045', 69, 101, 21, False),
    (16, 'r', 'R', '111', 82, 114, 41, False),
    (17, 't', 'T', '163', 84, 116, 51, False),
    (18, 'z', 'Z', '171', 90, 122, 57, False),
    (19, 'u', 'U', '144', 85, 117, 52, False),
    (20, 'i †', 'I', '051', 73, 105, 25, False),
    (21, 'o', 'O', '106', 79, 111, 38, False),
    (22, 'p', 'P', '127', 80, 112, 39, False),
    (23, ':', '(', '015', 40, 58, 13, True),
    (24, '+', '=', '040', 61, 43, 16, True),
    (25, 'Um. KB', 'Um. KB', '117', 0, 0, 47, True),
    (26, 'Um. GB', 'Um. GB', '057', 0, 0, 31, True),
    (27, 'a', 'A', '061', 65, 97, 17, False),
    (28, 's', 'S', '142', 83, 115, 50, False),
    (29, 'd', 'D', '064', 68, 100, 20, False),
    (30, 'f', 'F', '046', 70, 102, 22, False),
    (31, 'g', 'G', '067', 71, 103, 23, False),
    (32, 'h', 'H', '070', 72, 104, 24, False),
    (33, 'j', 'J', '121', 74, 106, 33, False),
    (34, 'k', 'K', '122', 75, 107, 34, False),
    (35, 'l', 'L', '103', 76, 108, 35, False),
    (36, '`', ';', '160', 59, 96, 48, False),
    (37, '/', ')', '141', 41, 47, 49, True),
    (38, 'SatzMarke', 'WRZL', '272', 10, 10, 26, True),
    (39, 'y', 'Y', '150', 89, 121, 56, False),
    (40, 'x', 'X', '147', 88, 120, 55, False),
    (41, 'c', 'C', '043', 67, 99, 19, False),
    (42, 'v', 'V', '165', 86, 118, 53, False),
    (43, 'b', 'B', '062', 66, 98, 18, False),
    (44, 'n', 'N', '105', 78, 110, 37, False),
    (45, 'm', 'M', '124', 77, 109, 36, False),
    (46, ',', '?', '153', 63, 44, 59, True),
    (47, '.', '!', '073', 33, 46, 27, True),
    (48, '-', '△', '100', 465, 45, 32, True),
    (49, 'Leertaste', 'ZR', '032', 32, 32, 10, True),
    (50, 'Irrung Zeichen', 'Irrung Zeichen', '377', 0, 0, None, False),
    (51, 'Irrung Satz', 'Irrung Satz', '016', 0, 0, 14, True),
    (52, 'Transport (Relikt)', 'Transport (Relikt)', '177', 0, 0, 63, False),
]
AUSGABE_ZEILE = {r[3]: r for r in TABELLE1 if r[0] != 52}
SW_ZEILE = {int(r[3], 8) & 0o157: r for r in TABELLE1 if r[0] not in (50, 52)}
EINGABE_ZEILE = {r[6]: r for r in TABELLE1 if r[6] is not None and r[0] != 52}
EINGABE_ZEILE[0o36] = (0, 'Irrung Block', 'Irrung Block', '', 0, 0, 0o36, True)


def octs(v, n):
    return format(v, 'o').rjust(n, '0')


def sgn(w):
    w &= MASK33
    return w - (1 << 33) if (w >> 32) else w


class Stub(Exception):
    pass


class LaufFehler(Exception):
    pass


class KonfigFehler(Stub):
    pass


def load_graph(path):
    g = {}
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = [p.strip() for p in line.split(';', 4)]
        if len(parts) < 5:
            continue
        num = int(parts[0])
        typ, text, outs = parts[2], parts[3], parts[4]
        n = dict(num=num, typ=typ, text=text, out=None, wahr=None, falsch=None, end=False, anw=None)
        m = re.fullmatch(r'\$ANWEISUNG-(\d+)', text)
        if m:
            n['anw'] = int(m.group(1))
        if outs.strip() == '---':
            n['end'] = True
        else:
            for tgt, _inp, kind in re.findall(r'(\d+)\((\d+)(?: (falsch|wahr))?\)', outs):
                if kind == 'falsch':
                    n['falsch'] = int(tgt)
                elif kind == 'wahr':
                    n['wahr'] = int(tgt)
                else:
                    n['out'] = int(tgt)
        g[num] = n
    return g


def load_t2(path):
    t2 = {}
    for raw in open(path, encoding='utf-8'):
        m = re.match(r'\s*ANWEISUNG-(\d+)\s*;', raw)
        if m:
            t2[int(m.group(1))] = raw.split(';')[1].strip() if ';' in raw else ''
    return t2


def pruefe_trommeldatei(pfad):
    fehler = []
    if not os.path.isfile(pfad):
        return [f'Trommeldatei nicht gefunden: {pfad}']
    try:
        # newline='' : keine Umwandlung von CRLF in LF; die Pruefung sieht die echten Zeilenenden.
        with open(pfad, encoding='utf-8', newline='') as fh:
            zeilen = fh.readlines()
    except OSError as e:
        return [f'Trommeldatei nicht lesbar: {pfad} ({e.strerror})']
    if any(z.endswith('\r\n') for z in zeilen):
        return [f'Trommeldatei hat CRLF-Zeilenenden (19 Byte je Zeile): {pfad}. Erwartet wird LF '
                f'({TROMMEL_ZEILE_LAENGE} Byte je Zeile), da der Interpreter Zellen ueber Adresse x '
                f'{TROMMEL_ZEILE_LAENGE} positioniert. Datei auf LF umstellen '
                f'(z. B. mit erzeuge_leere_trommel.py neu erzeugen oder dos2unix).']
    if len(zeilen) != TROMMEL_ADR_ANZAHL:
        fehler.append(f'Trommeldatei hat {len(zeilen)} Zeilen; erwartet werden genau '
                      f'{TROMMEL_ADR_ANZAHL} (Adressen 0000 bis 7777).')
    erwartete_adr = 0
    for nr, z in enumerate(zeilen, 1):
        if nr > TROMMEL_ADR_ANZAHL:
            break
        m = TROMMEL_ZEILE_RE.match(z)
        if not m:
            fehler.append(f'Zeile {nr}: ungueltiges Format (erwartet "aaaa: ttttttttttt"): {z.rstrip()!r}')
            erwartete_adr += 1
            continue
        adr = int(m.group(1), 8)
        if adr != erwartete_adr:
            fehler.append(f'Zeile {nr}: Adresse {m.group(1)} erwartet, gefunden {octs(erwartete_adr, 4)}.')
        erwartete_adr += 1
    return fehler


class Trommel:
    def __init__(self, pfad):
        self.pfad = pfad
        self.mem = {}
        self.datei = None
        fehler = pruefe_trommeldatei(pfad)
        if fehler:
            raise KonfigFehler('Trommeldatei formal fehlerhaft:\n  - ' + '\n  - '.join(fehler))
        with open(pfad, encoding='utf-8', newline='') as fh:
            for z in fh:
                m = TROMMEL_ZEILE_RE.match(z)
                if not m:
                    continue
                self.mem[int(m.group(1), 8)] = int(m.group(2), 8)
        try:
            # newline='' : Python schreibt '\n' unveraendert (nie '\r\n') und rechnet beim Lesen nichts um;
            # nur so stimmt die Byteposition Adresse x TROMMEL_ZEILE_LAENGE auch unter Windows.
            self.datei = open(pfad, 'r+', encoding='utf-8', newline='')
        except OSError as e:
            raise KonfigFehler(f'Trommeldatei nicht zum Schreiben zu oeffnen: {pfad} ({e.strerror})')

    def rd(self, adresse):
        return self.mem.get(adresse & MASK12, 0)

    def wr(self, adresse, wert):
        adresse &= MASK12
        wert &= MASK33
        self.mem[adresse] = wert
        zeile = f'{adresse:04o}: {wert:011o}\n'
        pos = adresse * TROMMEL_ZEILE_LAENGE
        try:
            self.datei.seek(pos)
            self.datei.write(zeile)
        except OSError as e:
            raise KonfigFehler(f'Trommeldatei nicht beschreibbar: {self.pfad} ({e.strerror})')

    def uebertrage_aus_testdatei(self, test_mem):
        for adr, wert in test_mem.items():
            self.wr(adr, wert)

    def schliessen(self):
        if self.datei is not None:
            try:
                self.datei.close()
            except OSError:
                pass
            self.datei = None


def interrupt_token_ok(t):
    u = t.upper().replace('\u00dc', 'UE')
    if u in ('H', 'R', 'G', 'E', 'ST', 'UE', 'M', 'M+', 'M-', 'K0', 'K1', 'K2', 'K3'):
        return True
    if re.fullmatch(r'(BS|SP|SW)(=[01]|\+|-)', u):
        return True
    return bool(re.fullmatch(r'(M|SW|BS|SP)-?(DRUECK\w*|GEDRUECKT-HALTEN|LOS\w*)', u))


def interrupt_pruefe(tokens):
    """Formale Pruefung der Tastenfolge eines #INTERRUPT; liefert Fehlertexte."""
    fe = []
    if not tokens:
        return ['ohne Tastenfolge']
    if tokens[0].upper() != 'H':
        fe.append(f'die erste Taste muss H sein, gefunden {tokens[0]!r}')
    mhalt = False
    for t in tokens:
        if not interrupt_token_ok(t):
            fe.append(f'unbekannte Taste {t!r}')
            continue
        u = t.upper().replace('\u00dc', 'UE')
        if u == 'R' and mhalt:
            fe.append('R bei noch gedrueckter Taste M')
        if u.startswith('M') and u not in ('ST',):
            press = u in ('M', 'M+') or 'DRUECK' in u or 'HALT' in u
            release = u == 'M' or not press
            if press:
                if mhalt:
                    fe.append('M gedrueckt, obwohl M bereits gedrueckt ist')
                mhalt = True
            if release:
                if not mhalt:
                    fe.append('M losgelassen, obwohl M nicht gedrueckt ist')
                mhalt = False
    if mhalt:
        fe.append('Tastenfolge endet mit gedrueckter Taste M')
    return fe


class Test:
    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.mem = {}
        self.dok = []
        self.spei = []
        self.spur = []
        self.stufe = None
        self.ac_init = None
        self.bz_init = None
        self.tasten = []
        self.interrupts = []
        self.starte = None
        self.starte_nr = None
        self._letzte_adr = None
        self._offen = []
        self.zeilen = []
        self.pruef_reg = {}
        self.pruef_mem = {}
        self._pruef_regzeile_gesehen = False
        self.geraete = {}
        self.pruef_dateien = {}
        self.fehler = []
        self.hinweise = []
        self._parse()

    PRUEF_SCHLUESSEL = {'BZ': 4, 'AC': 11, 'AR': 4, 'FE': 1, 'FUE': 1, 'BS': 1, 'US': 1,
                        'E': 1, 'A': 1, 'V1': 1, 'V2': 1}

    def _parse_pruef_regzeile(self, s, nr):
        s2 = s.split('#', 1)[0].strip()
        if not s2:
            return
        for tok in s2.split():
            mt = re.fullmatch(r'([A-Z0-9]+)=([0-7]+)', tok)
            if not mt:
                self.fehler.append(f'Zeile {nr}: Pruefungen: ungueltiges Element {tok!r}')
                continue
            key, val = mt.group(1), mt.group(2)
            if key not in self.PRUEF_SCHLUESSEL:
                self.fehler.append(f'Zeile {nr}: Pruefungen: unbekannter Schluessel {key!r}')
                continue
            breite = self.PRUEF_SCHLUESSEL[key]
            if len(val) != breite:
                self.fehler.append(f'Zeile {nr}: Pruefungen: {key}={val!r} hat nicht {breite} Oktalstellen')
                continue
            if breite == 1 and val not in ('0', '1'):
                self.fehler.append(f'Zeile {nr}: Pruefungen: Flag {key}={val!r} muss 0 oder 1 sein')
                continue
            if key in self.pruef_reg:
                self.fehler.append(f'Zeile {nr}: Pruefungen: Schluessel {key} mehrfach angegeben')
                continue
            self.pruef_reg[key] = int(val, 8)

    def _parse(self):
        modus = 'trommel'
        for nr, raw in enumerate(open(self.path, encoding='utf-8'), 1):
            line = raw.rstrip('\n').rstrip()
            s = line.strip()
            if not s:
                continue
            if s.lower().startswith('trommeldatei'):
                modus = 'trommel'
                continue
            if s.lower().startswith('tastenfolge'):
                modus = 'tasten'
                rest = s.split(':', 1)[1].strip() if ':' in s else ''
                self.tasten += rest.split()
                continue
            if s.lower().startswith('pr\u00fcfungen') or s.lower().startswith('pruefungen'):
                modus = 'pruefungen'
                rest = s.split(':', 1)[1].strip() if ':' in s else ''
                if rest:
                    self._parse_pruef_regzeile(rest, nr)
                    self._pruef_regzeile_gesehen = True
                continue
            m_ger = re.fullmatch(r'--(sw-ausgabe|k0|leser1|leser2|stanzer1)(?:\s+(.*?))?\s*(?:#.*)?', s)
            if m_ger:
                key = m_ger.group(1).replace('-', '_')
                wert = (m_ger.group(2) or '').strip()
                if not wert:
                    self.fehler.append(f'Zeile {nr}: --{m_ger.group(1)} ohne Wert')
                elif key in self.geraete:
                    self.fehler.append(f'Zeile {nr}: --{m_ger.group(1)} mehrfach angegeben')
                elif key == 'k0' and not wert.startswith('datei='):
                    self.fehler.append(f"Zeile {nr}: --k0: 'datei=PFAD' erwartet, gefunden {wert!r}")
                elif key == 'k0' and not wert[len('datei='):].strip():
                    self.fehler.append(f'Zeile {nr}: --k0 datei= ohne Pfad')
                else:
                    self.geraete[key] = wert[len('datei='):].strip() if key == 'k0' else wert
                    if key in ('leser1', 'leser2') and os.path.isdir(wert):
                        self.hinweise.append(f'Hinweis Zeile {nr}: --{m_ger.group(1)} {wert} ist ein Verzeichnis: alle Dateien darin werden als Lochstreifen gelesen; eine einzelne Datei ist sicherer')
                continue
            if re.match(r'--sw-terminal(\s|#|$)', s, re.I):
                self.fehler.append(f'Zeile {nr}: --SW-TERMINAL ist nur als Kommandozeilenschalter zulaessig, nicht in der Testdatei')
                continue
            if re.match(r'#STARTE(\s|$)', s, re.I):
                if modus == 'pruefungen':
                    self.fehler.append(f'Zeile {nr}: #STARTE ist im Abschnitt Pruefungen: nicht zulaessig')
                    continue
                wert = s[len('#STARTE'):].split('#', 1)[0].strip()
                if not wert:
                    self.fehler.append(f'Zeile {nr}: #STARTE ohne Oktalzahl')
                elif not re.fullmatch(r'[0-7]{1,4}', wert):
                    self.fehler.append(f'Zeile {nr}: #STARTE {wert!r} ungueltig (1 bis 4 Oktalziffern erwartet)')
                elif self.starte is not None:
                    self.fehler.append(f'Zeile {nr}: #STARTE mehrfach')
                else:
                    self.starte = int(wert, 8)
                    self.starte_nr = nr
                continue
            if re.match(r'#STARTE', s, re.I):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #STARTE: {s!r}')
                continue
            if re.match(r'#INTERRUPT(\s|$)', s, re.I):
                if modus != 'trommel':
                    self.fehler.append(f'Zeile {nr}: #INTERRUPT ist nur im Abschnitt Trommeldatei: zulaessig')
                    continue
                tok = s[len('#INTERRUPT'):].split('#', 1)[0].split()
                fe = interrupt_pruefe(tok)
                if self._letzte_adr is None:
                    fe.append('steht vor der ersten Befehlszeile (muss ZWISCHEN zwei Befehlszeilen stehen)')
                elif any(i['nach'] == self._letzte_adr for i in self.interrupts):
                    fe.append(f'nach Adresse {octs(self._letzte_adr,4)} ist schon ein #INTERRUPT angegeben')
                if fe:
                    for f in fe:
                        self.fehler.append(f'Zeile {nr}: #INTERRUPT: {f}')
                else:
                    ir = dict(nach=self._letzte_adr, tokens=tok, nr=nr, folgt=False)
                    self.interrupts.append(ir)
                    self._offen.append(ir)
                continue
            if re.match(r'#INTERRUPT', s, re.I):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #INTERRUPT: {s!r}')
                continue
            if modus == 'pruefungen':
                m_dat = re.fullmatch(r'--pruefe-(stanzer1|sw-ausgabe)(?:\s+(.*?))?\s*(?:#.*)?', s)
                if m_dat:
                    key = 'pruefe_' + m_dat.group(1).replace('-', '_')
                    soll = (m_dat.group(2) or '').strip()
                    if not soll:
                        self.fehler.append(f'Zeile {nr}: Pruefungen: --pruefe-{m_dat.group(1)} ohne Dateiname')
                    elif key in self.pruef_dateien:
                        self.fehler.append(f'Zeile {nr}: Pruefungen: --pruefe-{m_dat.group(1)} mehrfach angegeben')
                    else:
                        self.pruef_dateien[key] = soll
                    continue
                m_mem = re.fullmatch(r'([0-7]{4}):\s*([0-7]{11})\s*(#.*)?', s)
                if m_mem:
                    a, w = int(m_mem.group(1), 8), int(m_mem.group(2), 8)
                    if a in self.pruef_mem and self.pruef_mem[a] != w:
                        self.fehler.append(f'Zeile {nr}: Pruefungen: Adresse {m_mem.group(1)} '
                                            f'widersprüchlich mehrfach belegt')
                    self.pruef_mem[a] = w
                elif not self._pruef_regzeile_gesehen:
                    self._parse_pruef_regzeile(s, nr)
                    self._pruef_regzeile_gesehen = True
                else:
                    self.fehler.append(f'Zeile {nr}: Pruefungen: ungueltige Zeile: {s!r}')
                continue
            if modus == 'tasten':
                self.tasten += s.split()
                continue
            m = re.fullmatch(r'#DOK-([0-7]{4})\s*(.*)', s)
            if m:
                self.dok.append((int(m.group(1), 8), m.group(2)))
                continue
            if s.startswith('#DOK'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #DOK: {s!r}')
                continue
            m = re.fullmatch(r'#SPEI-([0-7]{4})\s+([0-7]{4})-([0-7]{4})', s)
            if m:
                self.spei.append((int(m.group(1), 8), int(m.group(2), 8), int(m.group(3), 8)))
                continue
            if s.startswith('#SPEI'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #SPEI: {s!r}')
                continue
            m = re.fullmatch(r'#SPUR-([0-7]{4})\s+([0-7]{4})', s)
            if m:
                self.spur.append((int(m.group(1), 8), int(m.group(2), 8)))
                continue
            if s.startswith('#SPUR'):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #SPUR: {s!r}')
                continue
            m = re.fullmatch(r'#PROT\s+STUFE=(\S+)', s)
            if m:
                if self.stufe is not None:
                    self.fehler.append(f'Zeile {nr}: #PROT STUFE mehrfach')
                if m.group(1) not in ('0', '1', '2'):
                    self.fehler.append(f'Zeile {nr}: #PROT STUFE={m.group(1)} ungueltig (0,1,2)')
                else:
                    self.stufe = int(m.group(1))
                continue
            m = re.fullmatch(r'#(AC|BZ)\s*=\s*(\S*)\s*(?:#.*)?', s)
            if m:
                reg, val = m.group(1), m.group(2)
                breite = 11 if reg == 'AC' else 4
                if getattr(self, reg.lower() + '_init') is not None:
                    self.fehler.append(f'Zeile {nr}: #{reg} mehrfach')
                elif not re.fullmatch(r'[0-7]{%d}' % breite, val):
                    self.fehler.append(f'Zeile {nr}: #{reg}={val!r} ungueltig ({breite} Oktalstellen erwartet)')
                else:
                    setattr(self, reg.lower() + '_init', int(val, 8))
                continue
            if re.match(r'#(AC|BZ)\b', s):
                self.fehler.append(f'Zeile {nr}: fehlerhafte Testmarke #{s[1:3]}: {s!r}')
                continue
            if s.startswith('#'):
                continue
            m = re.fullmatch(r'([0-7]{4}):\s*([0-7]{11})\s*(#.*)?', s)
            if not m:
                self.fehler.append(f'Zeile {nr}: ungueltiges Zeilenformat: {s!r}')
                continue
            a, w = int(m.group(1), 8), int(m.group(2), 8)
            if a in self.mem and self.mem[a] != w:
                self.fehler.append(f'Zeile {nr}: Adresse {m.group(1)} widerspruechlich belegt')
            self.mem[a] = w
            self.zeilen.append(f'{m.group(1)}: {m.group(2)}')
            for ir in self._offen:
                ir['folgt'] = True
            self._offen = []
            self._letzte_adr = a
        if self.stufe is None:
            self.stufe = 1
        for x, s0, e0 in self.spei:
            if not s0 <= e0:
                self.fehler.append(f'#SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}: keine gueltige Spanne')
        if self.starte is not None:
            if self.tasten:
                self.fehler.append(f'Zeile {self.starte_nr}: #STARTE ersetzt die Tastenfolge; daneben darf keine Tastenfolge stehen')
            else:
                self.tasten = ['H', 'G', 'M+'] + ['E'] * self.starte + ['M-', 'R']
        for ir in self.interrupts:
            if not ir['folgt']:
                self.fehler.append(f'Zeile {ir["nr"]}: #INTERRUPT: steht nicht zwischen zwei Befehlszeilen (keine Zeile danach)')
        if not self.tasten:
            self.fehler.append('Tastenfolge fehlt')


class Machine:
    FLAGS = ['E', 'A', 'T', 'SW', 'K1', 'K2', 'K3', 'FE', 'FUE', 'BS', 'US', 'V1', 'V2', 'H', 'SP']

    def __init__(self, trommel):
        self.trommel = trommel
        self.AC = self.BZ = self.AR = self.OR = self.adr = 0
        self.fl = {k: 0 for k in self.FLAGS}
        self.x_merker = 0
        self.x_fetch = False
        self.x_sek = 0
        self.zaehler = 0
        self.start_sek = 0
        self.vgl_ac = 0
        self.vgl_v = 0
        self.halted = False
        self.halt_grund = ''
        self.came_from = None
        self.diag_hook = None
        self.sw_lage = random.choice(['KB', 'GB'])
        self.sw_zeilenanfang = True
        self.log = lambda s: None
        self.leser = {1: None, 2: None}
        self.stanzer = None
        self.sw_datei = None
        self.eingabe_sprung = False
        self.k0 = None
        self.zeichenlage = 'KB'
        self.vor_phase2 = False
        self.vor_phase1 = False   # nach einem #INTERRUPT: Phase IV des vorigen Befehls ist abgelaufen, E beginnt bei Phase I
        self.br_aufgestellt = False
        self.bz_g = False   # G hat BR = 0000 000 aufgestellt; BZ wird erst durch dessen Ausfuehrung 0
        self.lese_adr = False
        self.br_tasten_m = False

    def rd(self, a):
        return self.trommel.rd(a)

    def wr(self, a, v):
        self.trommel.wr(a, v)

    @property
    def B(self): return (self.OR >> 6) & 7
    @property
    def A(self): return (self.OR >> 3) & 7
    @property
    def Z(self): return self.OR & 7
    @property
    def L(self): return self.Z & 1
    @property
    def R(self): return self.Z >> 1
    @property
    def z30(self): return 1 if self.Z >= 4 else 0

    def ac_neg(self, r_abhaengig=False):
        if r_abhaengig and self.R == 1:
            return (self.AC & 1) == 1
        return ((self.AC >> 32) & 1) == 1


def sektor(a):
    return a & 0o37


def t002(m):
    r = m.x_merker
    m.x_merker = 0
    m.x_fetch = bool(r)
    return bool(r)

def t003(m): return True
def t006(m): return m.B not in (0, 1) and m.A in (5, 7) and m.L == 1
def t008(m): return (m.B <= 1 and m.A in (4, 5, 7)) or (m.B == 0 and m.A == 6 and m.z30 == 1)

def t009(m):
    B, A = m.B, m.A
    v1, v2 = m.fl['V1'], m.fl['V2']
    v3 = v1 and v2
    return bool((B == 0 and A == 4 and m.ac_neg()) or
                (B == 0 and A == 5 and not m.ac_neg()) or
                (B == 1 and A == 4 and (v1 or v3)) or
                (B == 1 and A == 5 and (v2 or v3)) or
                (B == 0 and A == 7 and m.fl['FUE']) or
                (B == 1 and A == 7 and v3) or
                (B == 0 and A == 6 and m.z30 == 1 and m.fl['SP']))

def t011(m): return m.L == 1
def t013(m): return m.B <= 1 and m.A == 2 and m.z30 == 1
def t014(m): return m.B <= 1 and m.A == 2 and m.z30 == 0
def t015(m): return m.B <= 1 and m.A == 1
def t016(m): return m.B <= 1 and m.A == 3
def t018(m): return (m.B <= 1 and m.A in (0, 4, 5, 7)) or (m.B == 0 and m.A == 6 and m.z30 == 1)
def t019(m): return m.B == 3
def t020(m): return bool(m.fl['FUE'])
def t023(m): return m.B >= 4
def t031(m): return bool(m.fl['BS'])
def t034(m): return m.B == 3
def t036(m): return m.B <= 1 and m.A == 0
def t038(m): return m.B == 2
def t040(m): return m.B >= 4 and m.zaehler == 32
def t041(m): return m.B in (6, 7) and m.start_sek != 0 and sektor(m.AR) == 0o23
def t042(m): return m.B in (5, 7) and m.ac_neg(r_abhaengig=True)
def t043(m): return m.B <= 1 and m.A in (2, 6) and m.z30 == 0

def t024(m):
    return t040(m) or t041(m)


def a044(m):
    m.x_sek = (sektor(m.AR) + 2 * 0o15) & 0o37
    m.x_merker = 1


def a001(m):
    t_ar, t_bz = m.AR, m.BZ
    m.AR = t_bz
    m.BZ = (t_ar + 1) & MASK12

def a004(m): pass

def a005(m):
    if m.x_fetch:
        m.x_fetch = False
        w = m.rd((m.AR & ~0o37) | m.x_sek)
    else:
        w = m.rd(m.AR)
    m.OR = w & 0x1FF
    m.adr = (w >> 9) & MASK12

def a007(m): m.BZ = m.adr
def a010(m):
    if m.A == 6:
        m.OR = (m.OR & ~0o070) | 0o020
    else:
        if m.B == 0 and m.A == 7:
            m.fl['FUE'] = 0
        m.OR = m.OR & ~0o070

def a012(m): m.AC = 0

def a021(m):
    B, A, Z, R = m.B, m.A, m.Z, m.R
    a = m.AR
    lese, m.lese_adr = m.lese_adr, False

    def addsub(sub, cond_pos):
        ac, v = sgn(m.AC), sgn(m.rd(a))
        res = ac - v if sub else ac + v
        if B in (2, 3) and R == 0:
            m.fl['FUE'] = 0 if -(1 << 32) <= res < (1 << 32) else 1
        m.AC = res & MASK33

    if B == 1 and A == 6:
        pass
    elif A == 0:
        m.AC &= m.rd(a)
    elif A == 1:
        addsub(False, None)
    elif A == 2:
        addsub(True, None)
    elif A == 3:
        if B == 3 and Z in (0, 1):
            pass
        elif Z == 3:
            pass
        elif Z == 2:
            m.vr_uebertrag = 0
            if m.AC & 1:
                summe = m.AC + m.rd(a)
                m.AC = summe & MASK33
                m.vr_uebertrag = (summe >> 33) & 1
        else:
            addsub(not m.ac_neg(), None)
    elif A == 4:
        m.wr(a, m.AC)
    elif A == 5:
        if Z % 2 == 1:
            raise Stub(f'Befehl {B}{A}{Z}: R-Operation muesste ueber Knoten 10/37/38 laufen')
        m.wr(a, m.AC & m.rd(a))
    elif A == 6:
        m.wr(a, (~m.AC & MASK33) & m.rd(a))
    elif A == 7:
        if Z % 2 == 1:
            raise Stub(f'Befehl {B}{A}{Z}: R-Minus-Operation muesste ueber Knoten 10/37/38 laufen')
        if Z == 2:
            if (m.AC & 1) == 0:
                m.wr(a, 0)
        elif not m.ac_neg():
            m.wr(a, 0)
    m.zaehler += 1


def a022(m):
    R = m.R
    if m.B == 1 and m.A == 6 and m.Z >= 4:
        R = 0
    if R == 1:
        m.AC = ((m.AC >> 1) & MASK33) | (getattr(m, 'vr_uebertrag', 0) << 32)
        m.vr_uebertrag = 0
    elif R == 2:
        m.AC = (m.AC << 1) & MASK33
    elif R == 3:
        m.AC = ((m.AC << 1) & MASK33) | ((m.AC >> 32) & 1)
    if (m.B, m.A, m.Z) == (1, 6, 4) and m.diag_hook:
        m.diag_hook(m)

def a025(m):
    m.AR = (m.AR & ~0o37) | ((m.AR + 0o15) & 0o37)

def a026(m): m.BZ = (((m.AC >> 9) & MASK12) | m.adr) & MASK12
def a027(m): m.OR = m.OR & ~(1 << 5)

def a029(m):
    m.AC = (m.AC | (m.BZ << 8)) & MASK33
    m.OR = m.OR & ~0o070

def a030(m):
    m.fl['US'] = 1
    m.halt_grund = 'Unbedingter Stop (US:=1)'
    m.halted = True

def a045(m):
    m.fl['BS'] = 1
    m.halt_grund = 'Bedingter Stop (BS:=1)'
    m.halted = True

def a046(m):
    m.halt_grund = 'Halt wegen Ueberlauf (FUE bereits 1)'
    m.halted = True

def a035(m):
    m.fl['V1'] = m.fl['V2'] = 1
    m.vgl_ac = m.AC
    m.vgl_v = m.rd(m.AR) if m.A <= 3 else 0

def a037(m):
    ac, v = sgn(m.vgl_ac), sgn(m.vgl_v)
    if ac < v:
        m.fl['V1'], m.fl['V2'] = 1, 0
    elif ac > v:
        m.fl['V1'], m.fl['V2'] = 0, 1
    else:
        m.fl['V1'] = m.fl['V2'] = 1


def sw_zeichen(m, zeile):
    nr, kl, gb, _, a_gb, a_kb = zeile[:6]
    a = a_kb if m.sw_lage == 'KB' else a_gb
    if a in (9, 10, 32) or 33 <= a <= 255:
        return chr(a)
    name = kl if m.sw_lage == 'KB' else gb
    return f'<{name or "Nr." + str(nr)}>'


ROT = '\033[31m'
RESET = '\033[0m'
GERAETE = {'leser1': None, 'leser2': None, 'stanzer1': None, 'sw_ausgabe': None, 'k0': None,
           'pruefe_stanzer1': None, 'pruefe_sw_ausgabe': None}
NO_TERMOUT = False
SW_FENSTER = None      # --SW-TERMINAL: SwFenster-Objekt, sonst None
POLL_SEKUNDEN = 0.5


def tp(*a, **k):
    if not NO_TERMOUT:
        print(*a, **k)


def vp(*a, **k):
    print(*a, **k)


def rot(m, text):
    if NO_TERMOUT:
        return
    if not m.sw_zeilenanfang:
        sys.stdout.write('\n')
        m.sw_zeilenanfang = True
    sys.stdout.flush()
    if sys.stderr.isatty() and 'NO_COLOR' not in os.environ:
        text = ROT + text + RESET
    sys.stderr.write(text + '\n')
    sys.stderr.flush()


class _Stapel:
    def __init__(self, pfad, fehlertext):
        self.pfad = pfad
        self.fehlertext = fehlertext
        self.gesehen = None
        self.offen = []

    def _scan(self):
        if os.path.isdir(self.pfad):
            return sorted(os.path.join(self.pfad, f) for f in os.listdir(self.pfad)
                          if os.path.isfile(os.path.join(self.pfad, f)) and not f.startswith('.'))
        if os.path.isfile(self.pfad):
            return [self.pfad]
        raise KonfigFehler(f'{self.fehlertext}: {self.pfad}')

    def naechste(self):
        if self.gesehen is None:
            self.gesehen = set()
        while True:
            neu = [f for f in self._scan() if f not in self.gesehen]
            if neu:
                self.gesehen.update(neu)
                self.offen.extend(neu)
            if self.offen:
                return self.offen.pop(0)
            time.sleep(POLL_SEKUNDEN)


class Leser:
    def __init__(self, pfad):
        self.pfad = pfad
        self.stapel = _Stapel(pfad, 'Lochstreifen-Pfad nicht gefunden')
        self.datei = None
        self.zeilen = None
        self.pos = 0

    def naechste(self):
        while True:
            if self.zeilen is None:
                self.datei = self.stapel.naechste()
                with open(self.datei, encoding='utf-8') as fh:
                    self.zeilen = [x.strip() for x in fh]
                self.pos = 0
            while self.pos < len(self.zeilen):
                z = self.zeilen[self.pos]
                self.pos += 1
                if not z:
                    continue
                if not re.fullmatch(r'[01]{8}', z):
                    raise KonfigFehler(f'Lochstreifen {self.datei}: ungueltige Zeile {z!r}')
                return z
            self.zeilen = None


class Stanzer:
    def __init__(self, pfad):
        if os.path.isdir(pfad) or pfad.endswith(('/', '\\')):
            self.pfad = os.path.join(pfad, 'stanzer-ausgabe.txt')
        else:
            self.pfad = pfad
        self.begonnen = False

    def stanze(self, lb):
        d = os.path.dirname(os.path.abspath(self.pfad))
        os.makedirs(d, exist_ok=True)
        with open(self.pfad, 'a' if self.begonnen else 'w', encoding='utf-8') as fh:
            fh.write(format(lb, '08b') + '\n')
        self.begonnen = True


class SwDatei:
    def __init__(self, pfad):
        if os.path.isdir(pfad) or not os.path.splitext(pfad)[1]:
            self.pfad = os.path.join(pfad, 'sw-ausgabe.txt')
        else:
            self.pfad = pfad
        self.begonnen = False

    def schreibe(self, s):
        os.makedirs(os.path.dirname(os.path.abspath(self.pfad)), exist_ok=True)
        with open(self.pfad, 'a' if self.begonnen else 'w', encoding='utf-8') as fh:
            fh.write(s)
        self.begonnen = True


ROW_NR = {r[0]: r for r in TABELLE1}


def _norm(s):
    return re.sub(r'[\s.]', '', s).upper()


NAMEN = {}
for _r in TABELLE1:
    if _r[0] != 52:
        for _nm in (_r[1], _r[2]):
            if len(_nm) > 1:
                NAMEN.setdefault(_norm(_nm), _r)
NAMEN.update({'ZR': ROW_NR[49], 'WM': ROW_NR[12], 'TAB': ROW_NR[12], 'WRZL': ROW_NR[38],
              'IS': ROW_NR[51], 'IB': EINGABE_ZEILE[0o36]})

T_ERLAUBT = {_r[6] for _r in TABELLE1
             if _r[6] is not None and _r[0] != 52 and _r[1] in list('0123456789+-,.:')}
T_ERLAUBT |= {ROW_NR[49][6], ROW_NR[12][6], ROW_NR[51][6], 0o36}


def k0_zeile(tok, lage):
    if tok == ' ':
        return ROW_NR[49]
    if len(tok) == 1:
        code = ord(tok)
        for ci in ((4, 5) if lage == 'GB' else (5, 4)):
            for r in TABELLE1:
                if r[0] != 52 and r[6] is not None and r[ci] == code:
                    return r
        return None
    return NAMEN.get(_norm(tok))


class K0Quelle:
    def __init__(self, pfad=None):
        self.tast = pfad is None
        self.pfad = pfad
        self.stapel = None if self.tast else _Stapel(pfad, 'K0-Eingabe-Pfad nicht gefunden')
        self.zeilen = None
        self.pos = 0

    def naechstes(self):
        if self.tast:
            if sys.stdin.isatty():
                if sys.platform == 'win32':
                    import msvcrt
                    c = msvcrt.getch().decode('utf-8', errors='replace')
                else:
                    import termios, tty
                    fd = sys.stdin.fileno()
                    alt = termios.tcgetattr(fd)
                    try:
                        tty.setcbreak(fd)
                        c = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, alt)
            else:
                c = sys.stdin.read(1)
            return c or None
        while True:
            if self.zeilen is None:
                datei = self.stapel.naechste()
                try:
                    with open(datei, encoding='utf-8') as fh:
                        self.zeilen = [x.rstrip('\r\n') for x in fh]
                except OSError as e:
                    raise KonfigFehler(f'K0-Datei nicht lesbar: {datei} ({e.strerror})')
                self.pos = 0
            while self.pos < len(self.zeilen):
                z = self.zeilen[self.pos]
                self.pos += 1
                if z == '' or z.startswith('#'):
                    continue
                return z if len(z) == 1 else z.strip()
            self.zeilen = None

SW_FARBE = '\033[33m'
SW_RESET = '\033[0m'

def sw_schreibe(m, s):
    if SW_FENSTER is not None:
        SW_FENSTER.schreibe(s)
    if m.sw_datei is not None:
        m.sw_datei.schreibe(s)
        return
    if sys.stdout.isatty() and 'NO_COLOR' not in os.environ:
        sys.stdout.write(SW_FARBE + s + SW_RESET)
    else:
        sys.stdout.write(s)
    sys.stdout.flush()
    m.sw_zeilenanfang = s.endswith('\n')


def sw_fenster_unmoeglich():
    """Grund, warum kein Fenster geoeffnet werden kann, sonst None."""
    if sys.platform.startswith('linux') and not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        return 'keine grafische Oberflaeche (DISPLAY nicht gesetzt)'
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return 'tkinter fehlt (Linux: Paket python3-tk installieren)'
    return None


class SwFenster:
    """Ausgabefenster "SW Ausgabe" (--SW-TERMINAL): eigener Prozess, bekommt den Text ueber eine Pipe."""

    def __init__(self, zwischenablage='auto'):
        self.proc = None
        self.versucht = False
        self.zwischenablage = zwischenablage   # auto | tk | system (Kopierverfahren, s. zwischenablage_kopieren)

    def oeffne(self):
        if self.versucht:
            return
        self.versucht = True
        grund = sw_fenster_unmoeglich()
        if grund:
            vp(f'WARNUNG: --SW-TERMINAL: kein Ausgabefenster moeglich: {grund}. Der Test laeuft ohne Fenster.')
            return
        kw = {}
        if sys.platform == 'win32':
            kw['creationflags'] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw['start_new_session'] = True   # Strg+C/Schliessen des Terminals trifft nur den Interpreter, das Fenster bleibt
        try:
            self.proc = subprocess.Popen([sys.executable, os.path.abspath(__file__), '--sw-fenster-prozess', self.zwischenablage],
                                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, **kw)
        except OSError as e:
            vp(f'WARNUNG: --SW-TERMINAL: Ausgabefenster konnte nicht gestartet werden ({e}). Der Test laeuft ohne Fenster.')
            self.proc = None

    def schreibe(self, s):
        if self.proc is None:
            return
        try:
            self.proc.stdin.write(s.encode('utf-8'))
            self.proc.stdin.flush()
        except (OSError, ValueError):   # Fenster wurde schon mit X geschlossen
            self.proc = None

    def echo(self, s):
        """Echo einer K0-Eingabe: in \x01 ... \x02 eingeschlossen, das Fenster zeigt es in Dunkelgelb."""
        self.schreibe('\x01' + s + '\x02')

    def ende(self):
        """Ende des Aufrufs: Pipe schliessen. Das Fenster bleibt immer offen, bis es mit X geschlossen wird."""
        if self.proc is None:
            return
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        self.proc = None


# ---- Zwischenablage des Fensters (laeuft nur im Fensterprozess); Verfahren wie in den Lochstreifen-Hilfsprogrammen ----

def _zab_win32(text):
    """Windows: Win32-API (CF_UNICODETEXT, Zeilenenden \\r\\n), bis zu 20 Versuche im Abstand von 50 ms."""
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.WinDLL('user32', use_last_error=True)
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    u32.OpenClipboard.argtypes = [wintypes.HWND]
    u32.OpenClipboard.restype = wintypes.BOOL
    u32.EmptyClipboard.restype = wintypes.BOOL
    u32.CloseClipboard.restype = wintypes.BOOL
    u32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    u32.SetClipboardData.restype = wintypes.HANDLE
    k32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    k32.GlobalAlloc.restype = wintypes.HGLOBAL
    k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    k32.GlobalLock.restype = wintypes.LPVOID
    k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    k32.GlobalUnlock.restype = wintypes.BOOL
    k32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    k32.GlobalFree.restype = wintypes.HGLOBAL
    roh = (text.replace('\r\n', '\n').replace('\n', '\r\n') + '\0').encode('utf-16-le')
    for _ in range(20):
        if u32.OpenClipboard(None):
            try:
                u32.EmptyClipboard()
                h = k32.GlobalAlloc(0x0002, len(roh))   # GMEM_MOVEABLE
                if not h:
                    return False
                p = k32.GlobalLock(h)
                if not p:
                    k32.GlobalFree(h)
                    return False
                ctypes.memmove(p, roh, len(roh))
                k32.GlobalUnlock(h)
                if not u32.SetClipboardData(13, h):     # CF_UNICODETEXT; bei Erfolg gehoert der Speicher Windows
                    k32.GlobalFree(h)
                    return False
                return True
            finally:
                u32.CloseClipboard()
        time.sleep(0.05)
    return False


def _zab_systemprogramme():
    """Moegliche Systemprogramme (Name, Aufruf, Kodierung) in der Reihenfolge des Versuchs; fehlende werden uebersprungen.
    Wird bei jedem Kopieren neu bestimmt (nach WAYLAND_DISPLAY / XDG_SESSION_TYPE / DISPLAY und den installierten Programmen)."""
    import shutil
    env = os.environ
    liste = []
    if sys.platform == 'darwin':
        liste.append(('pbcopy', ['pbcopy'], 'utf-8'))
    else:
        wayland = bool(env.get('WAYLAND_DISPLAY')) or env.get('XDG_SESSION_TYPE', '').lower() == 'wayland'
        if wayland:
            liste.append(('wl-copy', ['wl-copy'], 'utf-8'))
        if env.get('DISPLAY'):
            liste.append(('xsel', ['xsel', '--clipboard', '--input'], 'utf-8'))
            liste.append(('xclip', ['xclip', '-selection', 'clipboard', '-t', 'UTF8_STRING'], 'utf-8'))
        try:
            with open('/proc/version', encoding='utf-8', errors='replace') as f:
                wsl = 'microsoft' in f.read().lower()
        except OSError:
            wsl = False
        if wsl:
            liste.append(('clip.exe', ['clip.exe'], 'utf-16'))
    return [p for p in liste if shutil.which(p[1][0])]


def _zab_programm(aufruf, kodierung, text):
    if aufruf[0] == 'clip.exe':
        text = text.replace('\n', '\r\n')
    try:
        r = subprocess.run(aufruf, input=text.encode(kodierung), stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=3)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def _zab_tk(root, text):
    """Tk-Zwischenablage (Rueckfall), bis zu 5 Versuche."""
    for _ in range(5):
        try:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            if root.clipboard_get() == text:
                return True
        except Exception:
            pass
        time.sleep(0.05)
    return False


def zwischenablage_kopieren(root, text, modus='auto'):
    """Legt text in die Zwischenablage. modus: auto (zuerst System, dann Tk), tk (nur Tk), system (nur Systemprogramm/Win32).
    Rueckgabe: (Erfolg, Name des Verfahrens)."""
    if modus in ('auto', 'system'):
        if sys.platform == 'win32':
            if _zab_win32(text):
                return True, 'Win32'
        else:
            for name, aufruf, kodierung in _zab_systemprogramme():
                if _zab_programm(aufruf, kodierung, text):
                    return True, name
    if modus in ('auto', 'tk'):
        if _zab_tk(root, text):
            return True, 'Tk'
    return False, ''


def sw_fenster_main(zwischenablage='auto'):
    """Wird im eigenen Prozess ausgefuehrt (interner Aufruf --sw-fenster-prozess [MODUS])."""
    import codecs
    import queue
    import threading
    import tkinter as tk

    if zwischenablage not in ('auto', 'tk', 'system'):
        zwischenablage = 'auto'
    root = tk.Tk()
    TITEL = 'SW Ausgabe'
    root.title(TITEL)
    txt = tk.Text(root, width=130, height=36, wrap='char', font='TkFixedFont', state='disabled')
    txt.tag_configure('echo', foreground='#B8860B')   # Dunkelgelb: Echo der K0-Eingaben
    txt.pack(fill='both', expand=True)
    root.resizable(False, False)
    root.update_idletasks()
    b, h = root.winfo_reqwidth(), root.winfo_reqheight()
    x = max(0, root.winfo_screenwidth() - b - 10)
    y = max(0, root.winfo_screenheight() - h - 70)   # Rand fuer Taskleiste/Dock
    root.geometry(f'+{x}+{y}')

    q = queue.Queue()
    im_echo = [False]   # zwischen \x01 und \x02 (kann ueber Pipe-Pakete hinweg dauern)

    def leser():
        while True:
            daten = sys.stdin.buffer.read1(4096)
            q.put(daten or None)
            if not daten:
                return

    threading.Thread(target=leser, daemon=True).start()
    dec = codecs.getincrementaldecoder('utf-8')('replace')

    def abfragen():
        try:
            while True:
                daten = q.get_nowait()
                if daten is None:                      # Ende des Aufrufs: Fenster bleibt offen, bis X geklickt wird
                    return
                text = dec.decode(daten).replace('\r', '')
                txt.configure(state='normal')
                for teil in re.split('([\x01\x02])', text):
                    if teil == '\x01':
                        im_echo[0] = True
                    elif teil == '\x02':
                        im_echo[0] = False
                    elif teil:
                        txt.insert('end', teil, ('echo',) if im_echo[0] else ())
                txt.see('end')
                txt.configure(state='disabled')
        except queue.Empty:
            pass
        root.after(30, abfragen)

    # ---- Markieren und Kopieren (wie in den Lochstreifen-Hilfsprogrammen) ----
    titel_job = [None]
    letzte = ['', 0.0]   # zuletzt kopierter Text und Zeitpunkt: derselbe Text wird binnen 5 s nicht erneut abgelegt

    def meldung(s):
        root.title(f'{TITEL} - {s}')
        if titel_job[0] is not None:
            root.after_cancel(titel_job[0])
        titel_job[0] = root.after(2500, lambda: root.title(TITEL))

    def kopiere(_ereignis=None):
        try:
            text = txt.get('sel.first', 'sel.last')
        except tk.TclError:
            return 'break'          # nichts markiert
        if not text:
            return 'break'
        if text == letzte[0] and time.monotonic() - letzte[1] < 5.0:
            meldung(f'kopiert ({len(text)} Zeichen)')
            return 'break'
        ok, verfahren = zwischenablage_kopieren(root, text, zwischenablage)
        if ok:
            letzte[0], letzte[1] = text, time.monotonic()
            meldung(f'kopiert ({len(text)} Zeichen, {verfahren})')
        else:
            meldung('Kopieren fehlgeschlagen')
        return 'break'

    def alles_markieren(_ereignis=None):
        txt.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def nach_maus_loslassen(_ereignis):
        root.after(20, kopiere)     # kurz warten, bis die Markierung feststeht; Tk-eigene Bindung bleibt unberuehrt

    def taste_win32(e):
        """Windows: Strg+C / Strg+A / Strg+Einfg auch ueber den Tastenkode (nicht-lateinisches Layout).
        AltGr (= Strg+Alt) ist kein Strg-Befehl."""
        if not (e.state & 0x0004) or (e.state & 0x20000):
            return None
        if e.keycode == 67 or e.keycode == 45:
            return kopiere()
        if e.keycode == 65:
            return alles_markieren()
        return None

    for w in (txt, root):    # auch wenn der Tastaturfokus nicht im Textfeld liegt
        for folge in ('<Control-c>', '<Control-C>', '<Control-Insert>'):
            w.bind(folge, kopiere)
        for folge in ('<Control-a>', '<Control-A>'):
            w.bind(folge, alles_markieren)
        if sys.platform == 'win32':
            w.bind('<Control-KeyPress>', taste_win32)
    txt.bind('<ButtonRelease-1>', nach_maus_loslassen, add='+')   # auch nach Doppelklick

    menue = tk.Menu(root, tearoff=0)
    menue.add_command(label='Kopieren', command=kopiere)
    menue.add_command(label='Alles markieren', command=alles_markieren)

    def kontextmenue(e):
        try:
            menue.tk_popup(e.x_root, e.y_root)
        finally:
            menue.grab_release()

    txt.bind('<Button-3>', kontextmenue)
    if sys.platform == 'darwin':
        txt.bind('<Button-2>', kontextmenue)
        txt.bind('<Control-Button-1>', kontextmenue)

    root.after(30, abfragen)
    root.mainloop()


def a028(m):
    a = m.AR
    if a & 0o4000:
        kanal = {0o7: 0, 0o6: 1, 0o5: 2, 0o4: 3}.get((a >> 6) & 0o7)
        if kanal is None:
            m.fl['A'] = 1
            raise Stub(f'Anwahlbefehl {octs(a,4)}: a2 < 4 nicht definiert; Flag A bleibt gesetzt')
        for k in (1, 2, 3):
            m.fl[f'K{k}'] = 1 if k == kanal else 0
        if kanal == 0:
            m.fl['T'], m.fl['SW'] = (0, 1) if m.fl['SW'] else (1, 0)
        else:
            m.fl['T'] = m.fl['SW'] = 0
        return


def a017(m):
    a = m.AR
    if a & 0o4000:
        return
    m.fl['A'] = 1
    v8 = (a >> 3) & 0o377
    z = AUSGABE_ZEILE.get(format(v8, 'o').rjust(3, '0'))
    if m.fl['K2']:
        z = SW_ZEILE.get(v8 & 0o157)
        if z is None:
            m.log(f'Hinweis: Ausgabe-Adresse {octs(a,4)} nicht in Tabelle 1 - keine Ausgabe')
        elif z[3] == '117':
            m.sw_lage = 'KB'
        elif z[3] == '057':
            m.sw_lage = 'GB'
        else:
            sw_schreibe(m, sw_zeichen(m, z))
    elif m.fl['K1']:
        if m.stanzer is None:
            rot(m, 'FEHLER: Ausgabe auf Lochbandstanzer 1 (Kanal K1) angefordert, aber --stanzer1 nicht angegeben.')
            raise KonfigFehler('--stanzer1 nicht angegeben')
        if z is None:
            m.log(f'Hinweis: Ausgabe-Adresse {octs(a,4)} nicht in Tabelle 1 - nichts gestanzt')
        else:
            m.stanzer.stanze(int(z[3], 8))
    else:
        raise Stub('Ausgabe-Halt ohne Ausgabegeraet (Kanal K0, K3 oder keine Anwahl); nach der Originaldokumentation 4.3.2.5 '
                   'stoppt der Rechner mit gesetztem Flag A (Lampe A)')
    m.fl['A'] = 0

def k0_echo_text(m, zeile):
    """Darstellung eines angenommenen K0-Zeichens wie beim Schreibwerk (sw_zeichen), aber mit der Eingabe-Zeichenlage."""
    nr, kl, gb, _, a_gb, a_kb = zeile[:6]
    a = a_kb if m.zeichenlage == 'KB' else a_gb
    if a in (9, 10, 32) or 33 <= a <= 255:
        return chr(a)
    name = kl if m.zeichenlage == 'KB' else gb
    return f'<{name or "Nr." + str(nr)}>'


def a032(m):
    m.fl['E'] = 1
    if m.fl['K1'] or m.fl['K2']:
        k = 1 if m.fl['K1'] else 2
        leser = m.leser.get(k)
        if leser is None:
            rot(m, f'FEHLER: Eingabe von Lochbandleser {k} (Kanal K{k}) angefordert, aber --leser{k} nicht angegeben.')
            raise KonfigFehler(f'--leser{k} nicht angegeben')
        try:
            z = leser.naechste()
            while z == '11111111':
                z = leser.naechste()
        except KonfigFehler as e:
            rot(m, f'FEHLER: Lochbandleser {k}: {e}')
            raise
        if z is None:
            m.halted = True
            m.halt_grund = f'Lochbandleser {k}: kein Lochstreifen mehr - Rechner wartet (Flag E bleibt 1)'
            return
        lb = int(z, 2)
        if bin(lb).count('1') % 2 == 0:
            m.fl['FE'] = 1
            m.halted = True
            m.halt_grund = f'Fehler bei Eingabe (FE): gerade Zahl von Lochungen ({z})'
            return
        ea = (lb & 0x0F) | ((lb >> 1) & 0x30)
        e = EINGABE_ZEILE.get(ea)
        if e is None:
            raise Stub(f'Eingabeadresse {ea:02o} (Lochbild {z}) kommt in Tabelle 1 nicht vor')
    elif not m.fl['K3'] and (m.fl['T'] or m.fl['SW']):
        modus = 'Schreibwerk (SW)' if m.fl['SW'] else 'Pult-Tastatur (T)'
        if m.k0 is None:
            m.k0 = K0Quelle(None)
        while True:
            try:
                tok = m.k0.naechstes()
            except KonfigFehler as ex:
                rot(m, f'FEHLER: {ex}')
                raise
            if tok is None:
                m.halted = True
                m.halt_grund = 'EINGABE_ENDE: K0-Eingabequelle zu Ende (Flag E bleibt 1)'
                return
            e = k0_zeile(tok, m.zeichenlage)
            if e is None:
                grund = f'Zeichen {tok!r} kommt in Tabelle 1 nicht vor'
            elif m.fl['T'] and e[6] not in T_ERLAUBT:
                grund = (f'{tok!r} ist an der Pult-Tastatur (T) nicht eingebbar - '
                         f'nur 0-9 + - , . : ZR WM IS IB (fuer alle Codes: Schalter SW druecken)')
            else:
                break
            if m.k0.tast:
                continue
            rot(m, f'FEHLER: K0-Eingabe: {grund}.')
            raise KonfigFehler(grund)
        ea = e[6]
        if SW_FENSTER is not None:
            SW_FENSTER.echo(k0_echo_text(m, e))
    else:
        raise Stub('Eingabebefehl: Kanal K3 bzw. kein Kanal angewaehlt - keine Eingabe moeglich')
    m.AR |= ea
    m.eingabe_sprung = e[7]
    if e[0] == 25:
        m.zeichenlage = 'KB'
    elif e[0] == 26:
        m.zeichenlage = 'GB'
    m.fl['E'] = 0

def a033(m):
    if m.eingabe_sprung:
        m.OR &= ~0o070
    else:
        m.OR = (m.OR & ~0o700) | (((m.B + 2) & 7) << 6)
        m.lese_adr = True

def make_stub(n):
    def f(m):
        raise Stub(f'ANWEISUNG-{n:03d} ist noch nicht implementiert (Ein-/Ausgabe o. ae.)')
    return f

FUNCS = {}
for _n, _f in list(globals().items()):
    mm = re.fullmatch(r'([ta])(\d{3})', _n)
    if mm:
        FUNCS[int(mm.group(2))] = _f

TYP = {'Konnektor': 'KON', 'Phasenzuordnung': 'PHA', 'Anweisung': 'ANW', 'Test': 'TST'}


def eintritt_br(m):
    B, A, Z = (m.OR >> 6) & 7, (m.OR >> 3) & 7, m.OR & 7
    nach_m = m.br_tasten_m
    m.br_tasten_m = False
    if nach_m and B in (0, 1) and A == 2 and Z >= 4:
        m.OR &= ~0o070
        return 54
    return 19


def _starte_kompakt(eff):
    """Kompakte Protokollform fuer #STARTE (Ergaenzung 08.10.2026): Eine Folge von mindestens 4 aufeinanderfolgenden
    Zeilen 'E  : (M gehalten) ...' wird auf die ersten zwei Zeilen, eine Sammelzeile und die letzte Zeile gekuerzt.
    Die Rechnung bleibt unberuehrt, nur die Protokollzeilen werden gekuerzt. Ausgeschriebene Tastenfolgen werden
    nicht gekuerzt (der Aufruf erfolgt nur bei #STARTE)."""
    praefix = 'E  : (M gehalten)'
    aus = []
    i = 0
    while i < len(eff):
        if not eff[i].startswith(praefix):
            aus.append(eff[i])
            i += 1
            continue
        j = i
        while j < len(eff) and eff[j].startswith(praefix):
            j += 1
        folge = eff[i:j]
        if len(folge) < 4:
            aus += folge
        else:
            m_a = re.search(r'BZ := (\d{4})', folge[2])
            m_b = re.search(r'BZ := (\d{4})', folge[-2])
            bis = m_b.group(1) if m_b else '????'
            von = m_a.group(1) if m_a else '????'
            aus += folge[:2]
            aus.append(f'... {len(folge) - 3} weitere E (BZ {von} bis {bis}): je Anschlag BZ := BZ+1, AR := BZ, '
                       'AC := BZ+1 im Adressfeld (kompakte Protokollform bei #STARTE)')
            aus.append(folge[-1])
        i = j
    return aus


def tastenfolge(m, tokens, run_e=None):
    eff = []
    ok = True
    mhalt = False
    e_unter_m = 0
    or_basis = m.OR
    sw_gedrueckt = False
    toks = list(tokens)

    def or_neu():
        m.OR = or_basis | (0o025 if mhalt else 0)

    for t in toks:
        u = t.upper().replace('\u00dc', 'UE')
        if u == 'H':
            m.fl['H'] = 1
            eff.append('H  : Schalter H-R -> "H", Flag H := 1')
        elif u == 'G':
            for k in m.fl:
                if k not in ('H', 'T', 'BS', 'SP'):
                    m.fl[k] = 0
            m.fl['T'], m.fl['SW'] = (0, 1) if sw_gedrueckt else (1, 0)
            m.AR = 0
            m.adr = 0
            or_basis = 0
            or_neu()
            m.bz_g = True   # BZ bleibt; BZ := 0 erst bei Ausfuehrung des Sprungs nach 0000 (E ohne weitere Operation, R)
            m.br_aufgestellt = False
            m.br_tasten_m = False
            m.vor_phase2 = False
            m.vor_phase1 = False
            m.fl['US'] = 1
            eff.append('G  : alle Flags ausser H,T,BS,SP := 0 (BS, SP: eingerastete Schalter); BR := 0000 000 (AR:=0000, OR:=000); US := 1; K0 angewaehlt, '
                       + ('SW gedrueckt -> SW := 1' if sw_gedrueckt else 'SW nicht gedrueckt -> T := 1')
                       + '; BZ bleibt unveraendert (BZ := 0 erst bei Ausfuehrung des Sprungs nach 0000)')
        elif u.startswith('SW') and (u.find('DRUECK') >= 0 or u in ('SW=1', 'SW+')):
            sw_gedrueckt = True
            m.fl['SW'], m.fl['T'] = 1, 0
            eff.append('SW gedrueckt: Schalter SW -> Flag SW := 1, T := 0')
        elif u.startswith('SW') and ('LOS' in u or u in ('SW=0', 'SW-')):
            sw_gedrueckt = False
            m.fl['SW'], m.fl['T'] = 0, 1
            eff.append('SW geloest (Stellung T): Flag SW := 0, T := 1')
        elif u == 'M' or (u.startswith('M') and (any(w in u for w in ('DRUECK', 'HALT')) or u == 'M+')) \
                or (u.startswith('M') and ('LOS' in u or u == 'M-')):
            press = u == 'M' or u == 'M+' or any(w in u for w in ('DRUECK', 'HALT'))
            release = u == 'M' or not press
            if press:
                if mhalt:
                    ok = False
                    eff.append('?? : M gedrueckt, obwohl M bereits gedrueckt ist')
                    continue
                mhalt = True
                e_unter_m = 0
                or_basis = m.OR
                or_neu()
                eff.append('M gedrueckt halten: OR := OR ODER 025 (BR = AR 025)' if u != 'M'
                           else 'M  : (= M gedrueckt, sofort losgelassen) OR := OR ODER 025 -> BR = AR 025')
            if release:
                if not mhalt:
                    ok = False
                    eff.append('?? : M losgelassen, obwohl M nicht gedrueckt ist')
                    continue
                mhalt = False
                if e_unter_m == 0:
                    or_basis |= 0o025
                    m.br_aufgestellt = True
                    m.br_tasten_m = True
                    or_neu()
                    if u != 'M':
                        eff.append('M loslassen: kein E unter M -> BR = AR 025 bleibt aufgestellt (Ausfuehrung durch E oder R)')
                else:
                    or_neu()
                    eff.append('M loslassen: OR-Verknuepfung mit 025 entfaellt fuer Folgeschritte')
        elif u[:2] in ('BS', 'SP') and len(u) > 2 and (u[2:] in ('=1', '+', '=0', '-') or any(w in u for w in ('DRUECK', 'LOS'))):
            name = u[:2]
            press = u[2:] in ('=1', '+') or 'DRUECK' in u
            m.fl[name] = 1 if press else 0
            eff.append(f'{name} : Schalter {name} ' + ('gedrueckt (eingerastet) -> ' if press else 'geloest -> ') + f'Flag {name} := {m.fl[name]}')
        elif u == 'ST':
            if not (m.fl['US'] or m.fl['BS']):
                eff.append('ST : elektronisch verriegelt, Rechner steht weder im bedingten noch im unbedingten Stopp -> keine Wirkung')
            else:
                or_basis |= 0o240
                or_neu()
                m.fl['US'] = 0
                m.br_aufgestellt = True
                eff.append(f'ST : (US oder BS) OR := OR ODER 240 -> BR = {octs(m.adr,4)} {octs(m.OR,3)}, AR unveraendert; US := 0 (aufgestellt, nicht ausgefuehrt)')
        elif u == 'UE':
            if not m.fl['H']:
                eff.append('Ue : nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung')
            else:
                m.AR = 0o7777
                m.adr = 0o7777
                or_basis |= 0o240
                or_neu()
                m.br_aufgestellt = True
                eff.append(f'Ue : AR := 7777; OR := OR ODER 240 -> BR = 7777 {octs(m.OR,3)} (Transport, aufgestellt, nicht ausgefuehrt)')
        elif u == 'E' and mhalt:
            if m.bz_g:
                # erstes E nach G: BR = 0000 025 springt nach 0000 mit Rueckkehrabsicht; der alte BZ geht als
                # Rueckkehradresse (alter BZ + 2) in den AC, BZ := 1 (Befehl aus Zelle 0000 geholt)
                alt = m.BZ
                m.bz_g = False
                m.BZ = 1
                m.AR = 1
                m.AC = ((alt + 2) & MASK12) << 9
            else:
                m.BZ = (m.BZ + 1) & MASK12
                m.AR = m.BZ
                m.AC = ((m.BZ + 1) & MASK12) << 9
            m.vor_phase2 = True
            m.br_tasten_m = False
            e_unter_m += 1
            eff.append(f'E  : (M gehalten) Befehlsentnahme gesperrt, BZ := {octs(m.BZ,4)}, AR := {octs(m.AR,4)}, '
                       f'AC := {octs(m.AC,11)} (BZ+1 im Adressfeld)')
        elif u == 'E':
            if run_e is None:
                ok = False
                eff.append('?? : Einzelschritt E ohne M ist hier nicht ausfuehrbar')
            elif not m.fl['H']:
                eff.append('E  : nur bei Schalter H wirksam, H nicht gesetzt -> keine Wirkung')
            elif m.halted:
                eff.append(f'E  : Automat steht im Stopp ({m.halt_grund}) -> keine weitere Ausfuehrung')
            else:
                if m.bz_g and m.OR == 0:
                    m.BZ = 0
                    m.bz_g = False
                eff.append(run_e())
        elif u in ('K0', 'K1', 'K2', 'K3'):
            kn = int(u[1])
            for k in (1, 2, 3):
                m.fl[f'K{k}'] = 1 if k == kn else 0
            if kn == 0:
                m.fl['T'], m.fl['SW'] = (0, 1) if sw_gedrueckt else (1, 0)
            else:
                m.fl['T'] = m.fl['SW'] = 0
            eff.append(f'{u} : Kanaltaste (rastend): Kanal K{kn} angewaehlt'
                       + (' ' + ('(SW gedrueckt -> SW := 1)' if sw_gedrueckt else '(SW nicht gedrueckt -> T := 1)') if kn == 0 else '')
                       + '; ein im Programm ausgefuehrter Anwahlbefehl uebersteuert diese Einstellung')
        elif u == 'R':
            if mhalt:
                ok = False
                eff.append('?? : R bei noch gedruecktem M (M muss vorher losgelassen werden)')
            m.fl['H'] = 0
            m.fl['US'] = 0
            if m.bz_g and m.OR == 0:
                m.BZ = 0
                m.bz_g = False
            eff.append('R  : Schalter H-R -> "R", Flag H := 0, US := 0; Interpretation beginnt bei Konnektor B'
                       + (' bzw. bei Knoten 19 (nach M mit Sprung mit Rueckkehrabsicht bei Knoten 54), wenn BR aufgestellt ist' if m.br_aufgestellt else ''))
        else:
            ok = False
            eff.append(f'?? : Taste/Schritt {t!r} ist im Regelwerk (Abschnitt 3) nicht definiert')
    if mhalt:
        ok = False
        eff.append('?? : Tastenfolge endet mit gedrueckter Taste M (M muss losgelassen werden)')
    if toks[-1:] and toks[-1].upper() == 'R':
        if m.fl['H'] != 0:
            ok = False
    elif m.fl['H'] != 1:
        ok = False
        eff.append('?? : Tastenfolge endet weder mit R noch im Halt (H) - Ausgangszustand nicht definiert')
    else:
        eff.append('Ende der Tastenfolge ohne R: Rechner bleibt im Halt (H)')
    return ok, eff


def lauf(test, graph, t2, outdir, trommel, max_knoten=2_000_000, knotentest=False):
    trommel.uebertrage_aus_testdatei(test.mem)

    m = Machine(trommel)
    if test.ac_init is not None:
        m.AC = test.ac_init
    if test.bz_init is not None:
        m.BZ = test.bz_init
    for k, key in ((1, 'leser1'), (2, 'leser2')):
        if GERAETE[key]:
            m.leser[k] = Leser(GERAETE[key])
    if GERAETE['stanzer1']:
        m.stanzer = Stanzer(GERAETE['stanzer1'])
    if GERAETE['sw_ausgabe']:
        m.sw_datei = SwDatei(GERAETE['sw_ausgabe'])
    m.k0 = K0Quelle(GERAETE['k0'])
    stufe = test.stufe
    zeilen = []
    diag_screen = []
    m.log = lambda s: zeilen.append(s)
    kopf = []

    def diag(mm):
        out = []
        for x, text in test.dok:
            if x == mm.adr:
                out.append(f'#DOK-{octs(x,4)} {text}')
        for x, s0, e0 in test.spei:
            if x == mm.adr:
                out.append(f'#SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}')
                for a in range(s0, e0 + 1):
                    out.append(f'{octs(a,4)}: {octs(mm.rd(a),11)}')
        for x, aaaa in test.spur:
            if x == mm.adr:
                out.append(f'#SPUR-{octs(x,4)} {octs(aaaa,4)}')
                spur = aaaa & ~0o37
                for log in PHYS_LOG:
                    a = spur | log
                    out.append(f'{octs(a,4)}: {octs(mm.rd(a),11)}')
        if not out:
            return
        diag_screen.extend(out)
        zeilen.extend(['--- Diagnose (Befehl 164) ---'] + out + ['--- Ende Diagnose ---'])

    m.diag_hook = diag

    def br_zeile(vor):
        f = m.fl
        zeilen.append(f'  BR={octs(m.adr,4)} {octs(m.OR,3)}  (vor Knoten {vor:03d})  '
                      f'BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} F\u00dc={f["FUE"]} '
                      f'V1={f["V1"]} V2={f["V2"]} V3={f["V1"] & f["V2"]}')

    def exec_node(node):
        n = graph[node]
        typ = n['typ']
        zusatz = ''
        br_nach = None
        if node == 2:
            br_zeile(2)
        try:
            if typ == 'Konnektor':
                bez = n['text']
                ziel = n['out']
                if ziel is None:
                    for k, o in graph.items():
                        if o['typ'] == 'Konnektor' and o['text'] == bez and o['out'] is not None and k != node:
                            ziel = o['out']
                            if k == 7:
                                br_nach = 7
                            break
                text = f'KON {bez}'
                nxt = ziel
            elif typ == 'Phasenzuordnung':
                text = 'PHA ' + n['text'].replace('Beginn ', '')
                if 'Phase IV' in n['text']:
                    m.zaehler = 0
                    m.start_sek = sektor(m.AR)
                nxt = n['out']
            elif typ == 'Anweisung':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                f(m)
                text = f'ANW {n["anw"]:03d}'
                nxt = n['out']
            elif typ == 'Test':
                f = FUNCS.get(n['anw'])
                if f is None:
                    raise Stub(f'ANWEISUNG-{n["anw"]:03d} unbekannt')
                r = f(m)
                text = f'TST {n["anw"]:03d}'
                zusatz = ' -> wahr' if r else ' -> falsch'
                nxt = n['wahr'] if r else n['falsch']
            else:
                raise Stub(f'Knotentyp {typ!r} unbekannt')
        except KonfigFehler as e:
            fe = f'Geraet nicht nutzbar (Knoten {node}): {e}'
            zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        except Stub as e:
            fe = f'STUB bei Knoten {node}: {e}'
            zeilen.append(f'K{node:03d} {fe}')
            raise LaufFehler(fe)
        if knotentest:
            zeilen.append(f'K{node:03d} {text} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}{zusatz}')
        if br_nach:
            br_zeile(br_nach)
        if n.get('end'):
            return None
        return nxt

    def run_e():
        if m.vor_phase2:
            node = 8
        elif m.vor_phase1 and not m.br_aufgestellt:
            node = 2
        else:
            node = eintritt_br(m)
        m.vor_phase2 = False
        m.vor_phase1 = False
        schritt = 0
        while True:
            schritt += 1
            if schritt > max_knoten:
                raise LaufFehler('Abbruch: Knotenlimit im Einzelschritt E erreicht')
            if node == 19 and schritt > 1:
                break
            nxt = exec_node(node)
            if m.halted:
                return f'E  : Einzelschritt endet im Stopp: {m.halt_grund}'
            if nxt is None:
                raise LaufFehler(f'Knoten {node} hat keinen Ausgang')
            m.came_from = node
            node = nxt
        m.br_aufgestellt = True
        return (f'E  : Einzelschritt (Phase IV, I, II, III), Halt vor Knoten 019; '
                f'BR={octs(m.adr,4)} {octs(m.OR,3)} BZ={octs(m.BZ,4)} AR={octs(m.AR,4)} AC={octs(m.AC,11)}')

    try:
        ok, eff = tastenfolge(m, test.tasten, run_e)
    except LaufFehler as e:
        return dict(ok=False, grund=str(e), kopf=kopf, zeilen=zeilen, diag=diag_screen, m=m)

    kopf.append(f'Test {test.name}')
    kopf.append('')
    kopf.append('== 1. Ausgangsbedingungen ==')
    kopf.append('Trommeldatei (uebernommen, Ausschnitt; nicht genannte Zellen = 0):')
    kopf += ['  ' + z for z in test.zeilen]
    for x, text in test.dok:
        kopf.append(f'  #DOK-{octs(x,4)} {text}')
    for x, s0, e0 in test.spei:
        kopf.append(f'  #SPEI-{octs(x,4)} {octs(s0,4)}-{octs(e0,4)}')
    for x, aaaa in test.spur:
        kopf.append(f'  #SPUR-{octs(x,4)} {octs(aaaa,4)}')
    if test.ac_init is not None:
        kopf.append(f'  #AC={octs(test.ac_init,11)}')
    if test.bz_init is not None:
        kopf.append(f'  #BZ={octs(test.bz_init,4)}')
    for ir in test.interrupts:
        kopf.append(f'  #INTERRUPT nach Befehl {octs(ir["nach"],4)}: ' + ' '.join(ir['tokens']))
    kopf.append(f'  #PROT STUFE={stufe}')
    if test.starte is not None:
        kopf.append(f'  #STARTE {octs(test.starte,4)} (Makro: H G M+ {test.starte}x E M- R, E {test.starte}-mal = dezimal)')
        kopf.append('Tastenfolge: (aus #STARTE erzeugt)')
    else:
        kopf.append('Tastenfolge: ' + ' '.join(test.tasten))
    if test.starte is not None:
        eff = _starte_kompakt(eff)
    kopf += ['  ' + e for e in eff]
    if test.ac_init is not None or test.bz_init is not None:
        kopf.append('  Anfangswerte: ' + ', '.join(
            [f'AC = {octs(test.ac_init,11)} (#AC)' if test.ac_init is not None else 'AC = 0 (kein #AC)',
             f'BZ = {octs(test.bz_init,4)} (#BZ)' if test.bz_init is not None else 'BZ = 0 (kein #BZ)']))
        kopf.append('  Nicht spezifizierte Register (AR, OR, ...) starten mit 0.')
    else:
        kopf.append('  Nicht spezifizierte Register (AC, ...) starten mit 0.')
    if not ok:
        return dict(ok=False, grund='Tastenfolge nicht gueltig/definiert', kopf=kopf, zeilen=[], diag=[], m=m)

    if m.halted or m.fl['H']:
        grund = m.halt_grund if m.halted else 'Halt (Schalter H): Tastenfolge endet ohne R'
        return dict(ok=True, grund=grund, kopf=kopf, zeilen=zeilen, diag=diag_screen, m=m, knoten=0)

    ir_tab = {ir['nach']: ir for ir in test.interrupts}
    cur = None          # Adresse des Befehls, dessen Phase I zuletzt begonnen hat
    ende_grund = None

    def interrupt(ir, adr):
        m.br_aufgestellt = m.br_tasten_m = m.vor_phase2 = m.bz_g = False
        m.vor_phase1 = True
        zeilen.append(f'--- INTERRUPT nach Befehl {octs(adr,4)} (Testzeile {ir["nr"]}): '
                      f'BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} ---')
        try:
            ok_i, eff_i = tastenfolge(m, ir['tokens'], run_e)
        except LaufFehler as e:
            return 'fehler', str(e)
        zeilen.extend('  ' + e for e in eff_i)
        m.vor_phase1 = False
        letzte = ir['tokens'][-1].upper()
        if not ok_i:
            return 'fehler', f'Tastenfolge nicht gueltig (INTERRUPT Testzeile {ir["nr"]}, nach Befehl {octs(adr,4)})'
        if m.halted:
            return 'ende', m.halt_grund
        if letzte == 'ST':
            m.fl['H'] = 0
        if letzte in ('R', 'ST'):
            zeilen.append('--- Ende INTERRUPT: Ablauf wird fortgesetzt ---')
            return 'weiter', None
        return 'ende', f'Halt (Schalter H): INTERRUPT nach Befehl {octs(adr,4)} endet ohne R/ST'

    node = eintritt_br(m) if m.br_aufgestellt else 1
    m.br_aufgestellt = False
    zaehl = 0
    fehler = None
    while not m.halted:
        zaehl += 1
        if zaehl > max_knoten:
            fehler = 'Abbruch: Knotenlimit erreicht (Endlosschleife?)'
            break
        if node == 2 and ir_tab:
            if cur is not None and cur in ir_tab and m.BZ == ((cur + 1) & MASK12):
                status, info = interrupt(ir_tab[cur], cur)
                cur = None
                if status == 'fehler':
                    fehler = info
                    break
                if status == 'ende':
                    ende_grund = info
                    break
                node = eintritt_br(m) if m.br_aufgestellt else 1
                m.br_aufgestellt = False
                continue
            cur = m.BZ
        try:
            nxt = exec_node(node)
        except LaufFehler as e:
            fehler = str(e)
            break
        if m.halted:
            break
        if nxt is None:
            fehler = f'Knoten {node} hat keinen Ausgang'
            break
        m.came_from = node
        node = nxt

    return dict(ok=fehler is None, grund=fehler or ende_grund or m.halt_grund, kopf=kopf, zeilen=zeilen,
                diag=diag_screen, m=m, knoten=zaehl)


def flags_text(m):
    return ' '.join(f'{k}={m.fl[k]}' for k in ('FE', 'FUE', 'BS', 'US', 'E', 'A', 'V1', 'V2'))


def pruefe_ergebnis(test, m):
    if not test.pruef_reg and not test.pruef_mem:
        return None
    wahr = True
    zeilen = []
    for key, soll in test.pruef_reg.items():
        if key == 'BZ':
            ist, breite = m.BZ, 4
        elif key == 'AC':
            ist, breite = m.AC, 11
        elif key == 'AR':
            ist, breite = m.AR, 4
        else:
            ist, breite = m.fl[key], 1
        gut = (ist == soll)
        wahr = wahr and gut
        zeilen.append(f'  {key}: soll={octs(soll, breite)} ist={octs(ist, breite)} '
                      f'{"OK" if gut else "FEHLER"}')
    for a in sorted(test.pruef_mem):
        soll = test.pruef_mem[a]
        ist = m.rd(a)
        gut = (ist == soll)
        wahr = wahr and gut
        zeilen.append(f'  {octs(a,4)}: soll={octs(soll,11)} ist={octs(ist,11)} {"OK" if gut else "FEHLER"}')
    return wahr, zeilen


DIFF_MAX = 100


def _zeilen_von(pfad):
    with open(pfad, encoding='utf-8', errors='replace') as fh:
        return fh.read().splitlines()


def soll_pfad(datei, testpfad):
    if os.path.dirname(datei):
        return datei
    return os.path.join(os.path.dirname(testpfad), datei)


def vergleiche_datei(name, soll, ist, ist_erzeugt):
    kopf = f'  {name}: soll={soll} ist={ist}'
    fehlt = []
    if not os.path.isfile(soll):
        fehlt.append('Soll-Datei fehlt')
    if not ist_erzeugt or not os.path.isfile(ist):
        fehlt.append('Ist-Datei fehlt, vom Lauf nicht angelegt')
    if fehlt:
        return False, [kopf + ' FEHLER (' + ' und '.join(fehlt) + ')']
    a, b = _zeilen_von(soll), _zeilen_von(ist)
    if a == b:
        return True, [kopf + ' OK']
    diff = list(difflib.unified_diff(a, b, fromfile='soll ' + soll, tofile='ist ' + ist, lineterm='', n=1))
    zeilen = [kopf + ' FEHLER (Inhalt verschieden, diff):']
    zeilen += ['    ' + d for d in diff[:DIFF_MAX]]
    if len(diff) > DIFF_MAX:
        zeilen.append(f'    ... {len(diff) - DIFF_MAX} weitere diff-Zeilen nicht angezeigt')
    return False, zeilen


def dateipruefungen(test):
    return {k: GERAETE[k] or test.pruef_dateien.get(k) for k in ('pruefe_stanzer1', 'pruefe_sw_ausgabe')
            if GERAETE[k] or test.pruef_dateien.get(k)}


def pruefe_dateien(test, testpfad, m):
    wahr, zeilen, da = True, [], False
    for key, name, geraet in (('pruefe_stanzer1', 'Stanzer 1', m.stanzer),
                              ('pruefe_sw_ausgabe', 'Schreibwerk', m.sw_datei)):
        datei = dateipruefungen(test).get(key)
        if not datei:
            continue
        da = True
        gut, z = vergleiche_datei(name, soll_pfad(datei, testpfad),
                                  geraet.pfad if geraet is not None else '-',
                                  geraet is not None and geraet.begonnen)
        wahr = wahr and gut
        zeilen += z
    return (wahr, zeilen) if da else None


def finde_testdatei(pfad, here):
    import unicodedata
    if os.path.isfile(pfad):
        return pfad
    def norm(s):
        return unicodedata.normalize('NFC', s).casefold()
    ziel = norm(os.path.basename(pfad))
    treffer = []
    for wurzel in dict.fromkeys([os.getcwd(), here]):
        for d, dirs, files in os.walk(wurzel):
            dirs[:] = [x for x in dirs if not x.startswith('.')
                       and x not in ('Test-Protokolle', 'ergebnis', 'PDF-Erzeugung', '_work')]
            for fn in files:
                if norm(fn) == ziel:
                    q = os.path.join(d, fn)
                    if q not in treffer:
                        treffer.append(q)
    if len(treffer) > 1:
        ablagen = {os.path.abspath(os.path.join(w, 'Tests')) for w in (os.getcwd(), here)}
        bevorzugt = [q for q in treffer if os.path.abspath(os.path.dirname(q)) in ablagen]
        if len(set(os.path.abspath(q) for q in bevorzugt)) == 1:
            treffer = [bevorzugt[0]]
    if not treffer:
        return None
    return treffer[0] if len(treffer) == 1 else treffer


def vorab_geraete(test):
    fehler = []
    for k, key in ((1, 'leser1'), (2, 'leser2')):
        p = GERAETE[key]
        if p and not (os.path.isdir(p) or os.path.isfile(p)):
            fehler.append(f'Lochbandleser {k}: Lochstreifen-Pfad nicht gefunden: {p}')
    p = GERAETE['k0']
    if p and not (os.path.isdir(p) or os.path.isfile(p)):
        fehler.append(f'K0: Eingabe-Pfad nicht gefunden: {p}')
    wirksam = dateipruefungen(test)
    if wirksam.get('pruefe_stanzer1') and not GERAETE['stanzer1']:
        fehler.append('--pruefe-stanzer1 ohne --stanzer1: es gibt keine erzeugte Datei, die verglichen werden koennte')
    if wirksam.get('pruefe_sw_ausgabe') and not GERAETE['sw_ausgabe']:
        fehler.append('--pruefe-sw-ausgabe ohne --sw-ausgabe: es gibt keine erzeugte Datei, die verglichen werden koennte')
    return fehler


def main():
    global NO_TERMOUT, SW_FENSTER
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='+')
    ap.add_argument('--version', action='version', version='%(prog)s ' + VERSION,
                    help='zeigt die Versionsnummer (Form y.xx-zzz) und beendet das Programm')
    ap.add_argument('--mdverz', default=os.path.join(here, 'markdown-dateien'), metavar='VERZ',
                    help='Verzeichnis mit den beiden .md-Dateien (Knotengraph und Knotenbeschreibung); '
                    'Standard: markdown-dateien/ neben dem Skript')
    ap.add_argument('--trommel', metavar='PFAD',
                    default=os.path.join(here, 'virtuelle_Geraete', 'Trommel', 'trommel.txt'),
                    help='Pfad der Trommeldatei (4096 Zeilen "aaaa: ttttttttttt"); '
                    'Standard: virtuelle_Geraete/Trommel/trommel.txt neben dem Skript')
    ap.add_argument('--leser1', '--lochbandleser1', metavar='PFAD', help='Lochstreifen fuer Leser 1 (Kanal K1): Datei oder Verzeichnis')
    ap.add_argument('--leser2', '--lochbandleser2', metavar='PFAD', help='Lochstreifen fuer Leser 2 (Kanal K2): Datei oder Verzeichnis')
    ap.add_argument('--stanzer1', '--lochbandstanzer1', metavar='PFAD', help='Ausgabedatei des Stanzers 1 (Kanal K1)')
    ap.add_argument('--sw-ausgabe', metavar='PFAD', dest='sw_ausgabe',
                    help='Schreibwerk-Ausgabe (Kanal K2) in die Datei sw-ausgabe.txt dieses Verzeichnisses; '
                    'ohne den Schalter geht die Ausgabe ans Terminal (dunkelgelb)')
    ap.add_argument('--pruefe-stanzer1', metavar='DATEI', dest='pruefe_stanzer1',
                    help='Soll-Datei fuer die Stanzer-Ausgabe (--stanzer1): wird mit der erzeugten Datei verglichen (diff); '
                    'ein Name ohne Ordner liegt neben der Testdatei. Fehlt eine Datei oder weichen sie ab, ist die Pruefung falsch.')
    ap.add_argument('--pruefe-sw-ausgabe', metavar='DATEI', dest='pruefe_sw_ausgabe',
                    help='Soll-Datei fuer die Schreibwerk-Ausgabe (--sw-ausgabe), Vergleich wie bei --pruefe-stanzer1')
    ap.add_argument('--k0', metavar='datei=PFAD',
                    help="K0-Eingabe aus Datei(en): 'datei=PFAD' (Datei oder Verzeichnis, alphanumerische Reihenfolge, "
                    "ein Zeichen oder Name wie ZR/WM/IS/IB/TAB/WRZL je Zeile); ohne den Schalter Eingabe vom Terminal")
    ap.add_argument('--out', default=os.path.join(here, 'Test-Protokolle'),
                    help='Protokolldatei (mit Endung) oder Verzeichnis; Standard: Test-Protokolle/ neben dem Skript')
    ap.add_argument('--knotentest', action='store_true', default=False,
                    help='Knotenzeilen (Kxxx ...) ins Protokoll aufnehmen; Standard: aus (BR-Zeilen, Diagnose '
                    'und Fehlermeldungen bleiben immer erhalten)')
    ap.add_argument('--NO-TERMOUT', action='store_true', default=False, dest='no_termout',
                    help='unterdrueckt alle Ausgaben des Interpreters selbst am Terminal (Ausnahmen: vom '
                    'C8205-Programm erzeugte Zeichen, Meldungen bei fehlgeschlagener Vorab-Pruefung)')
    ap.add_argument('--SW-TERMINAL', action='store_true', default=False, dest='sw_terminal',
                    help='Schreibwerk-Ausgabe zusaetzlich in einem eigenen Fenster "SW Ausgabe" (130 x 36 Zeichen, '
                    'rechts unten) zeigen, gleichgueltig ob --sw-ausgabe gesetzt ist. Das Fenster bleibt auch nach dem '
                    'Ende des Tests offen, bis es mit X geschlossen wird; Text mit der Maus markieren und kopieren '
                    '(Maus loslassen, Strg+C, Strg+Einfg, Kontextmenue) (Standard: aus; '
                    'nur Kommandozeile, nicht in der Testdatei)')
    ap.add_argument('--zwischenablage', choices=['auto', 'tk', 'system'], default='auto', metavar='auto|tk|system',
                    help='Kopierverfahren des Fensters "SW Ausgabe" (nur mit --SW-TERMINAL): auto = zuerst Systemprogramm '
                    '(Windows: Win32-API; Linux: wl-copy, xsel, xclip; macOS: pbcopy), dann Tk; tk = nur Tk-Zwischenablage; '
                    'system = nur Systemprogramm bzw. Win32-API (Standard: auto)')
    args = ap.parse_args()
    if args.k0 and not args.k0.startswith('datei='):
        ap.error("--k0: 'datei=PFAD' erwartet (ohne --k0 wird vom Terminal gelesen; 'tastatur' entfaellt)")
    NO_TERMOUT = args.no_termout
    SW_FENSTER = SwFenster(args.zwischenablage) if args.sw_terminal else None
    GERAETE.update(leser1=args.leser1, leser2=args.leser2, stanzer1=args.stanzer1,
                   sw_ausgabe=args.sw_ausgabe, k0=args.k0.split('=', 1)[1] if args.k0 else None,
                   pruefe_stanzer1=args.pruefe_stanzer1, pruefe_sw_ausgabe=args.pruefe_sw_ausgabe)

    GERAETE_ZEILEN = ('leser1', 'leser2', 'stanzer1', 'sw_ausgabe', 'k0')
    cli_geraete = {k: GERAETE[k] for k in GERAETE_ZEILEN}

    out_ist_datei = bool(os.path.splitext(args.out)[1])
    if out_ist_datei and len(args.tests) > 1:
        ap.error('--out mit Dateiendung (' + args.out + ') ist nur mit genau einer Testdatei zulaessig')

    if (args.pruefe_stanzer1 or args.pruefe_sw_ausgabe) and len(args.tests) > 1:
        ap.error('--pruefe-stanzer1/--pruefe-sw-ausgabe sind nur mit genau einer Testdatei zulaessig')

    graph_pfad = os.path.join(args.mdverz, 'C8205-Interpreter-Eingänge_der_Knoten.md')
    t2_pfad = os.path.join(args.mdverz, 'C8205-Interpreter-Beschreibung_der_Knoten.md')
    if not os.path.isfile(graph_pfad):
        ap.error(f'Knotengraph nicht gefunden: {graph_pfad}')
    if not os.path.isfile(t2_pfad):
        ap.error(f'Knotenbeschreibung nicht gefunden: {t2_pfad}')
    graph = load_graph(graph_pfad)
    t2 = load_t2(t2_pfad)
    fehlend = sorted({n['anw'] for n in graph.values() if n['anw'] and n['anw'] not in t2})
    if fehlend:
        tp('WARNUNG: im Graph referenzierte ANWEISUNG-Nummern fehlen in T2:', fehlend)
    nichtimpl = sorted(n for n in {x['anw'] for x in graph.values() if x['anw']} if n not in FUNCS)
    if nichtimpl:
        tp('WARNUNG: nicht implementierte ANWEISUNG-Nummern:', nichtimpl)

    trommel_fehler = pruefe_trommeldatei(args.trommel)
    if trommel_fehler:
        vp(f'\nFEHLER: Trommeldatei "{args.trommel}" ist formal fehlerhaft - Test(s) starten nicht:')
        for f in trommel_fehler[:50]:
            vp('  -', f)
        if len(trommel_fehler) > 50:
            vp(f'  ... {len(trommel_fehler) - 50} weitere Fehler')
        sys.exit(16)
    try:
        trommel = Trommel(args.trommel)
    except KonfigFehler as e:
        vp(f'\nFEHLER: Trommeldatei "{args.trommel}" kann nicht geoeffnet werden: {e}')
        sys.exit(16)

    rc = 0
    try:
        for pfad in args.tests:
            gefunden = finde_testdatei(pfad, here)
            if isinstance(gefunden, list):
                vp(f'\nFEHLER: Testdatei {pfad!r} nicht eindeutig gefunden:')
                for g in gefunden:
                    vp('  -', g)
                rc = 16
                continue
            if gefunden is None:
                vp(f'\nFEHLER: Testdatei nicht gefunden: {pfad!r} (aktuelles Verzeichnis: {os.getcwd()})')
                rc = 16
                continue
            if gefunden != pfad:
                tp(f'Testdatei: {gefunden}')
            pfad = gefunden
            t = Test(pfad)
            for k in GERAETE_ZEILEN:
                GERAETE[k] = cli_geraete[k] or t.geraete.get(k)
            tp(f'\n=== Test {t.name} (#PROT STUFE={t.stufe}) ===')
            for h in t.hinweise:
                tp(h)
            vorab = list(t.fehler) + vorab_geraete(t)
            if vorab:
                vp('FORMALE PRUEFUNG NEGATIV - Test startet nicht, Klaerung erforderlich:')
                for f in vorab:
                    vp('  -', f)
                rc = 16
                continue
            if SW_FENSTER is not None:
                SW_FENSTER.oeffne()
            try:
                r = lauf(t, graph, t2, args.out, trommel, knotentest=args.knotentest)
            except KeyboardInterrupt:
                tp('\nABBRUCH durch den Benutzer (Strg+C)')
                rc = 8
                continue
            m = r['m']
            if not m.sw_zeilenanfang:
                tp()
            if not r['ok']:
                tp('TEST NICHT ORDNUNGSGEMAESS BEENDET:', r['grund'])
            if t.stufe == 1:
                tp('-- Knotenzustaende --')
                for z in r['zeilen']:
                    tp(z)
            if r['diag'] and t.stufe != 1:
                tp('-- Diagnose --')
                for z in r['diag']:
                    tp(z)
            tp(f'Ende: {r["grund"]} | Knoten: {r.get("knoten", 0)} | BZ={octs(m.BZ,4)} AC={octs(m.AC,11)} '
               f'AR={octs(m.AR,4)} | {flags_text(m)}')

            pruef = pruefe_ergebnis(t, m)
            dpruef = pruefe_dateien(t, pfad, m) if r['ok'] else None
            if dpruef is not None:
                pruef = dpruef if pruef is None else (pruef[0] and dpruef[0], pruef[1] + dpruef[1])
            elif pruef is None and dateipruefungen(t):
                pruef = (False, [])
            pruef_ausgabe = []
            if pruef is not None:
                if not r['ok']:
                    pruef_ausgabe = ['Ergebnispruefung: nicht durchgefuehrt '
                                     '(Test nicht ordnungsgemaess beendet)']
                else:
                    wahr, pzeilen = pruef
                    pruef_ausgabe = ['Ergebnispruefung:'] + pzeilen + [f'Test {"wahr" if wahr else "falsch"}']
                for z in pruef_ausgabe:
                    tp(z)

            if not r['ok']:
                rc = 16 if r['grund'].startswith('Tastenfolge nicht gueltig') else 8
            elif pruef is None:
                rc = 4
            else:
                rc = 0 if pruef[0] else 6

            if t.stufe == 2:
                if out_ist_datei:
                    p = args.out
                    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
                else:
                    d = os.path.join(args.out, t.name)
                    os.makedirs(d, exist_ok=True)
                    p = os.path.join(d, 'protokoll.txt')
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write('\n'.join(r['kopf']) + '\n\n== 2. Zustaende des Knotenautomaten ==\n')
                    fh.write('\n'.join(r['zeilen']) + '\n\n')
                    fh.write(f'== Ende ==\n{r["grund"]}\nBZ={octs(m.BZ,4)} AC={octs(m.AC,11)} AR={octs(m.AR,4)} '
                             f'{flags_text(m)}\n')
                    if pruef_ausgabe:
                        fh.write('\n== 3. Ergebnispruefung ==\n' + '\n'.join(pruef_ausgabe) + '\n')
                tp('Protokolldatei:', p)
            elif out_ist_datei:
                tp(f'Hinweis: keine Protokolldatei {args.out}, da #PROT STUFE={t.stufe} '
                   f'(Datei entsteht nur bei #PROT STUFE=2).')
    finally:
        trommel.schliessen()
        if SW_FENSTER is not None:
            SW_FENSTER.ende()

    sys.exit(rc)


if __name__ == '__main__':
    if sys.argv[1:2] == ['--sw-fenster-prozess']:   # interner Aufruf fuer --SW-TERMINAL
        sw_fenster_main(sys.argv[2] if len(sys.argv) > 2 else 'auto')
    else:
        main()