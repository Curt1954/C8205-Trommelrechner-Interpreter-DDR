# -*- coding: utf-8 -*-
"""
grafik_tastatur.py - Tastaturbelegung des Rechners, an dem GRAFIK laeuft (Schalter --TASTATUR=de|en).
Version: G4-010

Wofuer die Belegung gebraucht wird:
  * Beim ECHTEN Tippen liefert Tk das Zeichen (ev.char) schon in der Belegung des Betriebssystems; SW-Fenster und Pult werten das Zeichen
    aus, nicht die Taste. Dort aendert der Schalter nichts.
  * Beim ABSPIELEN einer Klickspur (Ereignisart tipp, --WIEDERGABE) steht nur der Tk-keysym in der Datei. Unter X11 sucht event_generate zum
    keysym den Tastencode und leitet das Zeichen aus dem Modifikatorzustand ab; AltGr (Mod5, 0x80) muss deshalb mitgegeben werden, und zwar
    nur dort, wo die Belegung das Zeichen auf AltGr legt. Das ist belegungsabhaengig (de: [ ] { } \\ | @ ~ Euro auf AltGr; en: gibt es nicht).
  * Beschreibung(): wie man ein Zeichen auf der gewaehlten Belegung tippt (Protokoll, Hilfe).

Vorgabe: de. Gesetzt wird einmal beim Start (c8205_grafik.py); setze() ist auch fuer Pruefungen gedacht.
"""

BELEGUNGEN = ('de', 'en')
VORGABE = 'de'
_aktuell = VORGABE

# Zeichen, die unter X11 mit AltGr getippt werden (keysym), je Belegung
_ALTGR = {
    'de': ('bracketleft', 'bracketright', 'braceleft', 'braceright', 'backslash', 'bar', 'at', 'EuroSign', 'asciitilde'),
    'en': (),
}

# Tippweise der R300-Zeichen, die sich zwischen den Belegungen unterscheiden: zeichen -> (de, en)
_TIPPWEISE = {
    ':': ('Umschalt+.', 'Umschalt+;'),
    ';': ('Umschalt+,', ';'),
    '"': ('Umschalt+2', "Umschalt+'"),
    "'": ('Umschalt+#', "'"),
    '+': ('+', 'Umschalt+='),
    '=': ('Umschalt+0', '='),
    '*': ('Umschalt+ +', 'Umschalt+8'),
    '(': ('Umschalt+8', 'Umschalt+9'),
    ')': ('Umschalt+9', 'Umschalt+0'),
    '/': ('Umschalt+7', '/'),
    '?': ('Umschalt+ß', 'Umschalt+/'),
    '!': ('Umschalt+1', 'Umschalt+1'),
    '%': ('Umschalt+5', 'Umschalt+5'),
    '<': ('<', 'Umschalt+,'),
    '>': ('Umschalt+<', 'Umschalt+.'),
    '#': ('#', 'Umschalt+3'),
    '~': ('AltGr++', 'Umschalt+`'),
    '[': ('AltGr+8', '['),
    ']': ('AltGr+9', ']'),
    '`': ('Umschalt+´, dann Leertaste (Tottaste)', '`'),
    '-': ('-', '-'),
    ',': (',', ','),
    '.': ('.', '.'),
}


def setze(belegung):
    """Belegung setzen ('de' oder 'en', Gross-/Kleinschreibung gleich). ValueError bei anderem Wert."""
    global _aktuell
    b = str(belegung).strip().lower()
    if b not in BELEGUNGEN:
        raise ValueError(f'unbekannte Tastaturbelegung {belegung!r} (erlaubt: {"|".join(BELEGUNGEN)})')
    _aktuell = b
    return b


def belegung():
    return _aktuell


def braucht_altgr(keysym, b=None):
    """True, wenn der keysym auf der Belegung nur mit AltGr getippt wird."""
    return keysym in _ALTGR[b or _aktuell]


def altgr_keysyms(b=None):
    return _ALTGR[b or _aktuell]


def tippweise(zeichen, b=None):
    """Text, wie das Zeichen auf der Belegung getippt wird; Buchstaben und Ziffern: sie selbst (Grossbuchstabe: Umschalt+kleiner)."""
    b = b or _aktuell
    if zeichen in _TIPPWEISE:
        return _TIPPWEISE[zeichen][0 if b == 'de' else 1]
    if len(zeichen) == 1 and zeichen.isalpha() and zeichen.isupper():
        return 'Umschalt+' + zeichen.lower()
    return zeichen
