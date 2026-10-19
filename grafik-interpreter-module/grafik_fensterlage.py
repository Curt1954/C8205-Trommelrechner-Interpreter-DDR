# -*- coding: utf-8 -*-
"""
grafik_fensterlage.py - merkt sich die letzte Position der Fenster im Modus GRAFIK (Pult und SW-Fenster). Nur Standardbibliothek.
Version: FL-001 (19.10.2026, Wunsch des Projektinhabers)

Die Positionen stehen in einer kleinen JSON-Datei im Benutzerordner (nicht im Projektordner, der kann schreibgeschuetzt oder ein Zip sein):
  Windows  %APPDATA%\\C8205\\fensterlage.json
  macOS    ~/Library/Application Support/C8205/fensterlage.json
  sonst    $XDG_CONFIG_HOME/c8205/fensterlage.json  (Vorgabe ~/.config/c8205/fensterlage.json)
Umgebungsvariable C8205_FENSTERLAGE ueberschreibt den Pfad (Pruefungen); C8205_FENSTERLAGE=aus schaltet das Merken ab.
Gespeichert wird nur die Ecke links oben (x, y) je Fenstername ('pult', 'sw'); beide Fenster haben feste Groesse.
Gelesen wird ueber wm geometry (self.w.geometry()), nicht winfo_x/winfo_y: unter X11 weichen die um die Rahmenbreite ab und das Fenster
wuerde bei jedem Start wandern. Liegt die gespeicherte Ecke ausserhalb des sichtbaren Bereichs (Bildschirm abgesteckt, Aufloesung geaendert),
gilt die Vorgabe des Fensters. Jeder Fehler (Datei fehlt/kaputt/nicht schreibbar) bleibt still: dann gilt die Vorgabe.
"""
import json
import os
import re
import sys

VERSION_FENSTERLAGE = 'FL-001'
_GEOM = re.compile(r'^(?:\d+x\d+)?([+-]-?\d+)([+-]-?\d+)$')


def pfad():
    p = os.environ.get('C8205_FENSTERLAGE')
    if p:
        return None if p.lower() == 'aus' else p
    if sys.platform.startswith('win'):
        basis = os.environ.get('APPDATA') or os.path.expanduser('~')
        return os.path.join(basis, 'C8205', 'fensterlage.json')
    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'C8205', 'fensterlage.json')
    basis = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(basis, 'c8205', 'fensterlage.json')


def _lesen():
    p = pfad()
    if not p:
        return {}
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def laden(name):
    """(x, y) oder None."""
    e = _lesen().get(name)
    try:
        return int(e['x']), int(e['y'])
    except Exception:
        return None


def speichern(name, x, y):
    p = pfad()
    if not p:
        return False
    try:
        d = _lesen()
        d[name] = {'x': int(x), 'y': int(y)}
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=1)
        os.replace(tmp, p)
        return True
    except Exception:
        return False


def ecke(fenster):
    """Ecke links oben aus 'wm geometry' (z. B. '1148x860+30+-5'); None, wenn nicht lesbar."""
    try:
        m = _GEOM.match(fenster.geometry())
        if m:
            return int(m.group(1).replace('+', '')), int(m.group(2).replace('+', ''))
    except Exception:
        pass
    return None


def sichtbar(fenster, x, y, breite, hoehe):
    """True, wenn von dem Fenster an (x, y) noch ein greifbares Stueck im sichtbaren Bereich liegt (Titelleiste)."""
    try:
        vx, vy = int(fenster.winfo_vrootx()), int(fenster.winfo_vrooty())
        vb, vh = int(fenster.winfo_vrootwidth()), int(fenster.winfo_vrootheight())
        if vb <= 0 or vh <= 0:
            raise ValueError
    except Exception:
        try:
            vx = vy = 0
            vb, vh = int(fenster.winfo_screenwidth()), int(fenster.winfo_screenheight())
        except Exception:
            return True                     # nichts pruefbar: gespeicherte Lage gilt
    return (vx - breite + 80 <= x <= vx + vb - 80) and (vy <= y <= vy + vh - 60)


def anwenden(fenster, name, breite, hoehe):
    """Setzt das Fenster auf die gespeicherte Lage; Rueckgabe True, wenn eine gueltige gespeicherte Lage verwendet wurde."""
    p = laden(name)
    if p is None or not sichtbar(fenster, p[0], p[1], breite, hoehe):
        return False
    try:
        fenster.geometry(f'+{p[0]}+{p[1]}')
        return True
    except Exception:
        return False


class Merker:
    """Wird im Takt des Fensters aufgerufen (merken()); schreibt die Lage, wenn sie sich geaendert hat und eine Sekunde lang gleich blieb.
    beenden() schreibt sofort (Fenster schliessen). Kein Schreiben, solange die Lage noch die unveraenderte Startlage ist."""
    RUHE_S = 1.0

    def __init__(self, fenster, name, zeit):
        self.w, self.name, self.zeit = fenster, name, zeit
        self.gespeichert = ecke(fenster)
        self._kandidat = None
        self._seit = 0.0

    def merken(self):
        e = ecke(self.w)
        if e is None or e == self.gespeichert:
            self._kandidat = None
            return False
        if e != self._kandidat:
            self._kandidat, self._seit = e, self.zeit()
            return False
        if self.zeit() - self._seit >= self.RUHE_S:
            return self._schreiben(e)
        return False

    def _schreiben(self, e):
        if speichern(self.name, e[0], e[1]):
            self.gespeichert, self._kandidat = e, None
            return True
        return False

    def beenden(self):
        e = ecke(self.w)
        if e is not None and e != self.gespeichert:
            return self._schreiben(e)
        return False
