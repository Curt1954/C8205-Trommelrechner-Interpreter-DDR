# -*- coding: utf-8 -*-
"""
grafik_takt.py - Taktprotokoll: schreibt die virtuelle Trommelzeit (Wortzeiten) des Modus GRAFIK mit. Kein Tkinter, kein C-Modul noetig.
Version: TP-001 (08.11.2026, Auftrag des Inhabers: Taktmessung der Eingabeschleife, abschaltbar)

Zweck: Die virtuelle Zeit vt (GRAFIK_Beschreibung §7.8) ist deterministisch (nur Programm und Startlage). Dieses Modul haengt sich an die
Stellen, an denen vt fortgeschrieben wird, und schreibt je Ereignis eine Zeile. Ausgewertet (Fenster, Schleife, Summen) wird danach mit
einem eigenen Skript; die Uhr laeuft fuer ALLE Befehle, es wird nichts ausgelassen ("alles mitschreiben, hinterher auswaehlen").

Aus: ohne Schalter --taktprotokoll ist dieses Modul nicht geladen und die Trommel traegt nur eine Pruefung "takt is None" je tick/Zugriff.
Nur mit --trommelzeit echt oder schnell (in 'alt' gibt es keine virtuelle Zeit).

Dateiformat (UTF-8, LF; Kopf mit '#'; danach Tabulator-getrennt, eine Zeile je Ereignis):
  lfd  vt  art  knoten  phase  BZ  BR  OR  AC  n  adresse
  lfd      laufende Nummer ab 1
  vt       virtuelle Zeit in Wortzeiten VOR dem Ereignis (Dezimalzahl)
  art      T = Phase beginnt (eine Wortzeit; Knoten 63: zusaetzliche Wortzeit des Sprungs, Phase I uebersprungen)
           L = Lesezugriff auf die Trommel, S = Schreibzugriff
           Z = Luecke: vt wurde ausserhalb von tick() und Trommelzugriff fortgeschrieben (z. B. Zeitaufschlag der Zusatztrommeln, --C8205Z);
               n = Zahl der Wortzeiten der Luecke, Knoten und Phase wie beim naechsten Ereignis. So bleibt die Zeitfolge lueckenlos.
  knoten   Knotennummer des Graphen, in dem das Ereignis geschieht
  phase    I, II, III, IV (zuletzt begonnene Phase)
  BZ, BR, OR, AC   Befehlszaehler, Adressteil des Befehlsregisters, Operationscode (3 Ziffern) und Akkumulator im Augenblick des Ereignisses (oktal)
  n        bei T: Zahl der Wortzeiten (1); bei L/S: Wartezeit bis der Sektor unter dem Kopf liegt (0 bis 31)
  adresse  bei L/S: Trommeladresse (oktal 4 Stellen); bei T leer ('-')
Zeit nach dem Ereignis: bei T vt + n; bei L/S vt + n (Zugriff selbst kostet keine eigene Wortzeit, die naechste Phase beginnt mit tick()).
Der Befehlsbeginn ist die Zeile T mit Knoten 2 (Phase I). Die Wartezeit im Eingabe-Halt und im Halt steht nicht im Protokoll: vt steht dort still.
Am Ende steht eine Zeile '# Ende ...' (bei Ueberschreiten von --takt-max: '# ABGEBROCHEN ...', die Uhr laeuft weiter, nur die Mitschrift endet).
"""
import os

VERSION_TAKT = 'TP-001'
STANDARD_MAX = 5_000_000          # Zeilen; 0 = unbegrenzt


def _okt(w, stellen):
    return format(int(w) & ((1 << (3 * stellen)) - 1), 'o').zfill(stellen)


class TaktProtokoll:
    def __init__(self, pfad, maschine=None, maximum=STANDARD_MAX, zeitmodell='?', vt0=0):
        self.pfad = pfad
        self.m = maschine              # HaltMaschine (BZ, adr, OR, AC); None = Spalten leer
        self.maximum = maximum
        self.knoten = 0                # vom Rechner vor jedem Knoten gesetzt
        self.phase = '-'
        self.lfd = 0
        self.abgebrochen = False
        self.vt_letzte = vt0
        self.wartezeit_summe = 0
        self.zugriffe = 0
        ordner = os.path.dirname(os.path.abspath(pfad))
        os.makedirs(ordner, exist_ok=True)
        self.f = open(pfad, 'w', encoding='utf-8', newline='\n')
        self.f.write(f'# C8205 Taktprotokoll {VERSION_TAKT}; Zeitmodell {zeitmodell}; vt am Anfang {vt0} (Lage der Trommel beim Einschalten)\n')
        self.f.write('# lfd\tvt\tart\tknoten\tphase\tBZ\tBR\tOR\tAC\tn\tadresse\n')

    # --- vom Rechner ----------------------------------------------------------------------------------------------
    def phase_setzen(self, text):
        self.phase = text

    # --- von der Trommel ------------------------------------------------------------------------------------------
    def tick(self, vt, n):
        self._zeile(vt, 'T', n, None)

    def zugriff(self, art, vt, wartezeit, adresse):
        self.zugriffe += 1
        self.wartezeit_summe += wartezeit
        self._zeile(vt, art, wartezeit, adresse)

    def _zeile(self, vt, art, n, adresse):
        if vt != self.vt_letzte:
            luecke, vt_l = vt - self.vt_letzte, self.vt_letzte
            self.vt_letzte = vt
            self._schreibe(vt_l, 'Z', luecke, None)
        self.vt_letzte = vt + n
        self._schreibe(vt, art, n, adresse)

    def _schreibe(self, vt, art, n, adresse):
        if self.abgebrochen or self.f is None:
            return
        if self.maximum and self.lfd >= self.maximum:
            self.abgebrochen = True
            self.f.write(f'# ABGEBROCHEN nach {self.lfd} Zeilen (--takt-max); die Uhr laeuft weiter, die Mitschrift endet\n')
            return
        self.lfd += 1
        m = self.m
        if m is not None:
            ctx = f'{_okt(m.BZ, 4)}\t{_okt(m.adr, 4)}\t{_okt(m.OR, 3)}\t{_okt(m.AC, 11)}'
        else:
            ctx = '-\t-\t-\t-'
        adr = '-' if adresse is None else _okt(adresse, 4)
        self.f.write(f'{self.lfd}\t{vt}\t{art}\t{self.knoten}\t{self.phase}\t{ctx}\t{n}\t{adr}\n')

    # --- Ende -----------------------------------------------------------------------------------------------------
    def zusammenfassung(self):
        return (f'{self.pfad} ({self.lfd} Zeilen, vt am Ende {self.vt_letzte}, {self.zugriffe} Zugriffe, Wartezeit {self.wartezeit_summe}'
                + (', ABGEBROCHEN' if self.abgebrochen else '') + ')')

    def schliessen(self):
        if self.f is not None:
            if not self.abgebrochen:
                self.f.write(f'# Ende: {self.lfd} Zeilen, vt am Ende {self.vt_letzte}, {self.zugriffe} Zugriffe, Wartezeit {self.wartezeit_summe}\n')
            self.f.close()
            self.f = None
