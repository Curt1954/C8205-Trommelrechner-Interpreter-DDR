# -*- coding: utf-8 -*-
"""
grafik_hwcheck.py - Hardware-Check-Fenster des Modus GRAFIK (Schalter --HWCHECK). Nur Standardbibliothek (Tkinter).
Aenderungen (28.10.2026: Beschriftung der Zusatztrommeln ZT0 bis ZT3 statt ZT1 bis ZT4, passend zur Anwahl 5100 030 bis 5400 030; HW-005: Zusatztrommeln)

Ein zweites, nur so grosses wie noetig, verschiebbares Fenster mit sechs Zeilen untereinander (alles oktal, ausser der letzten):
    BZ         4 Stellen
    BR         AR-Teil (4 Stellen) und OR (3 Stellen), wie die Lampenreihen AR und OR am Pult (m.adr, m.OR)
    Spur Sektor  Spurnummer (3 Stellen, 0..177) und Sektornummer (2 Stellen, 0..37) der Adresse im Speicheradressregister AR (m.AR):
               Spur = AR >> 5, Sektor = AR & 0o37 (logische Sektornummer, wie sektor() im Interpreter)
    AC         11 Stellen in Vierergruppen, von links gebildet (4 + 4 + 3)
    <<AR>>     Speicherinhalt (11 Stellen, ebenso 4 + 4 + 3) an der Adresse im Register AR (m.AR); die Adresse steht im Namen
    Haltzeit   (HW-004, dezimal) Millisekunden zwischen dem Start (Taste R) und dem folgenden Halt bzw. zwischen zwei aufeinanderfolgenden
               Halts (Stopp, E/A-Halt, Fehler), dazu 'von -> bis'. Messung: grafik_haltzeit.py (m.haltuhr); ohne Messung '---.- ms'
HW-005, nur mit --C8205Z (experimenteller Prototyp C8205Z): fuenf weitere Zeilen. Je Zusatztrommel ZT0 bis ZT3 eine Zeile mit der zuletzt
bearbeiteten Adresse (Spur Sektor, wie die Zeile Spur Sektor; '--- --' = noch keine) und hinter der angewaehlten ZT ein kleiner gruener Punkt;
darunter EIN Inhaltsfeld <<ZTd>> (11 Stellen, 4 + 4 + 3) fuer die angewaehlte ZT (es ist immer nur eine aktiv). Ohne den Schalter bleibt
das Fenster bei sechs Zeilen. Die Daten liefert GrafikZT.ansicht() (grafik_zt.py).
Das Fenster bleibt aufgeblendet, solange der Grafik-Interpreter laeuft: es laesst sich nicht schliessen (X wirkt nicht), es endet mit dem
Pult-Fenster. Es veraendert nichts: der Speicherinhalt wird ohne Koinzidenz direkt gelesen (keine Wartezeit, keine Statistik).
Vierergruppen werden von LINKS gebildet (11 Stellen = 4 + 4 + 3; HW-003, Auftraggeber 17.10.2026; vorher von rechts). Die Formatierung (hwcheck_zeilen) braucht kein Tkinter und ist pruefbar.
"""
VERSION_HWCHECK = 'HW-007'
MASK12, MASK33 = 0o7777, (1 << 33) - 1
from grafik_haltzeit import zeile as haltzeit_zeile


def gruppen4(wert, stellen):
    """Oktalzahl mit fester Stellenzahl, von LINKS in Vierergruppen: 22060635124 -> '2206 0635 124' (Null: '0000 0000 000')."""
    s = f'{wert:0{stellen}o}'
    return ' '.join(s[i:i + 4] for i in range(0, len(s), 4))


LETZTER_FEHLER = None      # Grund, wenn der Speicherinhalt nicht lesbar war (Anzeige dann '---- ---- ---'); nur zur Fehlersuche


def einblick_lesen(trommel, adresse):
    """Speicherinhalt ohne Nebenwirkung (ohne Koinzidenz, ohne Statistik); None, wenn er nicht lesbar ist (Grund in LETZTER_FEHLER).
    1. Methode einblick() der Trommel (grafik_trommel.py); 2. Rueckfall: direkt das C-Modul (trommel.T.lesen), falls die
    Trommel-Klasse keine einblick() hat (aelterer Stand von grafik_trommel.py) - der HW-Check haengt so nicht von dieser Datei ab."""
    global LETZTER_FEHLER
    adresse &= MASK12
    f = getattr(trommel, 'einblick', None)
    if f is None:
        T = getattr(trommel, 'T', None)
        lesen = getattr(T, 'lesen', None)
        if lesen is None:
            LETZTER_FEHLER = 'Trommel hat weder einblick() noch T.lesen()'
            return None
        if not getattr(trommel, 'eingeschaltet', True):
            LETZTER_FEHLER = 'Trommel nicht eingeschaltet'
            return None
        f = lambda a: lesen(a) & MASK33
    try:
        LETZTER_FEHLER = None
        return f(adresse)
    except Exception as e:
        LETZTER_FEHLER = f'{type(e).__name__}: {e}'
        return None


def haltzeit_text(m):
    """Wert der Zeile Haltzeit (HW-004): Millisekunden Start -> Halt bzw. Halt -> Halt; ohne Messung (oder ohne m.haltuhr) '---.- ms'."""
    uhr = getattr(m, 'haltuhr', None)
    try:
        return haltzeit_zeile(uhr.lesen() if uhr is not None else None)
    except Exception:
        return haltzeit_zeile(None)


def hwcheck_zeilen(m):
    """Sechs Zeilen (Name, Wert) fuer die Anzeige. m: c8205_interp.Machine."""
    ar = m.AR & MASK12
    inhalt = einblick_lesen(m.trommel, ar)
    return [
        ('BZ', f'{m.BZ & MASK12:04o}'),
        ('BR', f'{m.adr & MASK12:04o} {m.OR & 0o777:03o}'),
        ('Spur Sektor', f'{(ar >> 5) & 0o177:03o} {ar & 0o37:02o}'),
        ('AC', gruppen4(m.AC & MASK33, 11)),
        (f'<<AR>>  AR={ar:04o}', gruppen4(inhalt & MASK33, 11) if inhalt is not None else '---- ---- ---'),
        ('Haltzeit', haltzeit_text(m)),
    ]


def zt_zeilen(zt):
    """Zeilen der Zusatztrommeln (HW-005): vier Mal (Name, Adresse 'ttt ss', angewaehlt) und ein Inhaltsfeld (Name, Wert). zt: GrafikZT
    (Methode ansicht()) oder None. Rueckgabe (zeilen4, inhaltszeile)."""
    try:
        g, adressen, inhalt = zt.ansicht()
    except Exception:
        g, adressen, inhalt = 0, [None] * 4, None
    zeilen = []
    for k in range(1, 5):                      # k = 1..4 ist die Nummer im Modul; angezeigt wird d = k - 1 (ZT0..ZT3, Anwahl 5k00 030, 5100 = ZT0 bis 5400 = ZT3)
        a = adressen[k - 1]
        zeilen.append((f'ZT{k - 1}', f'{(a >> 5) & 0o177:03o} {a & 0o37:02o}' if a is not None else '--- --', g == k))
    if g:
        a = adressen[g - 1]
        name = f'<<ZT{g - 1}>>' + (f'  {a:04o}' if a is not None else '')
    else:
        name = '<<ZT>>'
    return zeilen, (name, gruppen4(inhalt & MASK33, 11) if inhalt is not None else '---- ---- ---')


class HwCheckFenster:
    def __init__(self, root, maschine, tk=None, versatz=(1180, 40)):
        """root: Hauptfenster (Pult); maschine: Machine. tk: Modul tkinter (Parameter fuer Pruefungen)."""
        if tk is None:
            import tkinter as tk
        self.m = maschine
        self.win = tk.Toplevel(root)
        self.win.title('C 8205 HW-Check')
        self.win.resizable(False, False)
        self.win.protocol('WM_DELETE_WINDOW', lambda: None)       # bleibt aufgeblendet (Projektinhaber 17.10.2026)
        try:
            self.win.geometry(f'+{versatz[0]}+{versatz[1]}')
        except Exception:
            pass
        self._namen, self._werte = [], []
        for i in range(6):
            n = tk.Label(self.win, text='', font=('Courier', 14, 'bold'), anchor='w', justify='left')
            w = tk.Label(self.win, text='', font=('Courier', 14), anchor='w', justify='left', padx=8)
            n.grid(row=i, column=0, sticky='w', padx=(8, 0), pady=2)
            w.grid(row=i, column=1, sticky='w', pady=2)
            self._namen.append(n)
            self._werte.append(w)
        self.zt = getattr(maschine, 'zt', None)
        if self.zt is not None and hasattr(self.zt, 'ansicht'):        # --C8205Z: Zeilen der Zusatztrommeln (HW-005)
            self._zt_namen, self._zt_werte, self._zt_punkte = [], [], []
            for i in range(5):
                n = tk.Label(self.win, text='', font=('Courier', 14, 'bold'), anchor='w', justify='left')
                w = tk.Label(self.win, text='', font=('Courier', 14), anchor='w', justify='left', padx=8)
                p = tk.Label(self.win, text='', font=('Courier', 14, 'bold'), fg='#00a000', anchor='w')
                n.grid(row=6 + i, column=0, sticky='w', padx=(8, 0), pady=2)
                w.grid(row=6 + i, column=1, sticky='w', pady=2)
                p.grid(row=6 + i, column=2, sticky='w', padx=(0, 8), pady=2)
                self._zt_namen.append(n)
                self._zt_werte.append(w)
                self._zt_punkte.append(p)
        else:
            self.zt = None
        self._alt = None
        self._zt_alt = None
        self.aktualisieren()

    def aktualisieren(self):
        if self.zt is not None:
            zt = zt_zeilen(self.zt)
            if zt != self._zt_alt:
                self._zt_alt = zt
                zeilen, inhalt = zt
                for i, (name, wert, an) in enumerate(zeilen):
                    self._zt_namen[i].configure(text=name)
                    self._zt_werte[i].configure(text=wert)
                    self._zt_punkte[i].configure(text='\u25cf' if an else '')
                self._zt_namen[4].configure(text=inhalt[0])
                self._zt_werte[4].configure(text=inhalt[1])
                self._zt_punkte[4].configure(text='')
        zeilen = hwcheck_zeilen(self.m)
        if zeilen == self._alt:
            return
        self._alt = zeilen
        for i, (name, wert) in enumerate(zeilen):
            self._namen[i].configure(text=name)
            self._werte[i].configure(text=wert)
