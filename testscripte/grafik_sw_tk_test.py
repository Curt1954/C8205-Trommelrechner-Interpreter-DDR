#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grafik_sw_tk_test.py - Test des ECHTEN Tk-Fensters "SW" (Stufe 3) und des --HWCHECK-Fensters, beide zusammen.
Version: SWTK-004 (nach Checkpoint 45, NICHT abgenommen). Nur Standardbibliothek; braucht Tkinter und einen Bildschirm.

WAS ER TUT
  Er oeffnet in EINEM Prozess ein echtes Tk-Hauptfenster (Attrappe fuer das Pult), darauf das echte SW-Fenster (grafik_sw_fenster.SwFenster)
  und das echte HW-Check-Fenster (grafik_hwcheck.HwCheckFenster) - wie c8205_grafik.py --HWCHECK sie oeffnet. Ein Faden spielt den Rechner
  (liest K0-Zeichen aus der echten K0-Warteschlange). Tastendruecke werden mit Tk-Ereignissen (event_generate) in das Fenster gegeben,
  also durch dieselbe Bindung <Key>, die auch Ihre Tastatur benutzt (nicht durch einen Aufruf der Logik).
  Der Test ersetzt NICHT Ihre Augen: Aussehen, Schrift, Lage am Bildschirm, Fenstermanager sehen nur Sie (siehe --manuell).

PRUEFUNGEN (Status OK / FEHLER / WARNUNG; WARNUNG = hier nicht entscheidbar oder vom Fenstermanager abhaengig, bitte ansehen)
  Fenster:   Titel, 130 x 36 Zeichen, kein Zeilenumbruch, wirklich sichtbar, Schrift mit fester Breite, Lage innerhalb des Bildschirms
  Ausgabe:   Text vom Rechner erscheint (Tabulator alle 12 Spalten), benannte Zeichen unsichtbar, jedes angenommene getippte Zeichen erscheint (seit 18.10.2026, S3-04 neu)
  Eingabe:   ohne Eingabe-Halt wird vorgemerkt (Puffer, G4-007) und bei Kanalwechsel verworfen; mit Eingabe-Halt: Titel "Eingabe erwartet", Fokus; Folge 2 A 3 Enter Tab Leertaste
             gibt genau die erwarteten K0-Zeichen (Umschaltzeichen nur bei Wechsel der Lage des SW); Zeichen ausserhalb des R300-Codes
             (ä ö ü ß @ € §) werden verworfen; AltGr-Tilde (Windows: Strg+Alt) geht durch; Strg+Taste ohne Eingabe; Sondertasten ohne Wirkung
  Kopieren:  Markieren und Strg+C legen den Text in die Zwischenablage
  HWCHECK:   Fenster da, sechs Zeilen wie hwcheck_zeilen(), Aktualisierung, X wirkt nicht, nimmt dem SW-Fenster den Fokus nicht,
             keine Ueberdeckung mit dem SW-Fenster, innerhalb des Bildschirms
  Schluss:   nach erledigter Eingabe geht der Fokus zum Pult zurueck; X am SW-Fenster ruft die Schliess-Funktion (wie Strg+C)

AUFRUF (aus dem Projektordner)
  python3 testscripte/grafik_sw_tk_test.py                 Windows/Mac/Linux mit Bildschirm: Fenster erscheinen kurz, NICHT anfassen (ca. 15 s)
  python3 testscripte/grafik_sw_tk_test.py --manuell       danach bleiben beide Fenster offen; Sie tippen selbst, das Terminal zeigt, was der
                                                           "Rechner" bekommt; Checkliste fuer Umlaute, AltGr, Fokus, Kopieren; Enter beendet
  python3 testscripte/grafik_sw_tk_test.py --manuell --DEBUGLOG [DATEI]
                                                           wie --manuell, dazu das Fehlersuch-Protokoll des SW-Fensters (Voreinstellung sw_tk_test_debug.log);
                                                           die Zeilen aus dem SW-Fenster (Taste ..., Taste ignoriert ...) erscheinen auch im Terminal
  python3 testscripte/grafik_sw_tk_test.py --xvfb          Linux ohne Bildschirm (xvfb-run); der Fokus-Teil ist dort nur eingeschraenkt aussagekraeftig
  python3 testscripte/grafik_sw_tk_test.py --bericht X.txt Bericht in diese Datei (Voreinstellung: sw_tk_test_bericht.txt, beim Trockenlauf
                                                           sw_tk_test_trockenlauf.txt, jeweils im aktuellen Ordner)
  python3 testscripte/grafik_sw_tk_test.py --ohne-tk       TROCKENLAUF ohne Tkinter (Ersatzmodul, ruft die Tastenbehandlung direkt auf);
                                                           prueft das Skript und die Eingabelogik, NICHT das echte Fenster und NICHT --HWCHECK
Der Bericht nennt in der ersten Zeile, welcher der drei Faelle vorliegt: ECHTER LAUF, TROCKENLAUF oder NICHT GELAUFEN (dann mit Grund und Abhilfe).
Nur der ECHTE LAUF sagt etwas ueber das Tk-Fenster und --HWCHECK.
Rueckgabewert: 0 = kein FEHLER; 1 = mindestens ein FEHLER; 2 = nicht gelaufen (Tkinter oder Bildschirm oder xvfb-run fehlt;
Linux: sudo apt install python3-tk, fuer --xvfb: sudo apt install xvfb).
"""
import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
import types

VERSION_SWTK = 'SWTK-004'
HALTEZEIT = 0.12            # Haltezeit einer Taste im Test (s); die zweite Eingabe geht beim Loslassen (U-11), das Programm muss bis dahin wieder bei 011 sein
HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
sys.path.insert(0, HIER)

STRG, ALTGR_WIN, ALT_LINUX, ALTGR_X11 = 0x4, 0x20000 | 0x4, 0x8, 0x80
SHIFT_X11 = 0x1
ALTGR_TASTEN_X11 = ('at', 'EuroSign', 'bracketleft', 'bracketright', 'braceleft', 'braceright', 'backslash', 'bar', 'asciitilde')
SHIFT_TASTEN_X11 = ('section',)


def zustand_x11(keysym, state):
    """SWTK-003: event_generate(keysym=...) findet unter X11 nur den Tastencode; das Zeichen kommt aus dem Zustand. Ohne Umschalt/AltGr kam im Lauf
    vom 18.10.2026 fuer A ein a, fuer @ ein q, fuer Euro ein e, fuer Paragraph eine 3 an (Test-Artefakt, wie die Wiedergabe in F-54). Deshalb hier wie
    eine echte Tastatur: Grossbuchstabe und Paragraph mit Umschalt (0x1), @ Euro [ ] { } Backslash | ~ mit AltGr (0x80)."""
    if state or not sys.platform.startswith('linux'):
        return state
    if len(keysym) == 1 and keysym.isalpha() and keysym.isupper():
        return SHIFT_X11
    if keysym in SHIFT_TASTEN_X11:
        return SHIFT_X11
    if keysym in ALTGR_TASTEN_X11:
        return ALTGR_X11
    return state


class Ergebnisse:
    def __init__(self):
        self.zeilen = []

    def melde(self, status, name, detail=''):
        z = f'{status:8s} {name}' + (f'  -  {detail}' if detail else '')
        self.zeilen.append((status, z))
        print(z, flush=True)

    def ok(self, name, detail=''): self.melde('OK', name, detail)
    def fehler(self, name, detail=''): self.melde('FEHLER', name, detail)
    def warnung(self, name, detail=''): self.melde('WARNUNG', name, detail)
    def info(self, name, detail=''): self.melde('INFO', name, detail)

    def pruefe(self, name, bedingung, detail='', bei_nein='FEHLER', immer=False):
        """detail steht bei FEHLER/WARNUNG immer, bei OK nur mit immer=True."""
        if bedingung:
            self.ok(name, detail if immer else '')
        else:
            self.melde(bei_nein, name, detail)
        return bool(bedingung)

    def anzahl(self, status):
        return sum(1 for s, _ in self.zeilen if s == status)


ART_ECHT = 'ECHTER LAUF'
ART_TROCKEN = 'TROCKENLAUF (kein Tkinter: sagt NICHTS ueber das echte Fenster und --HWCHECK)'
ART_NICHT = 'NICHT GELAUFEN'


def bericht_schreiben(pfad, art, zeilen, schluss):
    """Bericht in eine Datei; die erste Zeile nennt Version, Zeit, Plattform, Python und die ART des Laufs."""
    try:
        with open(pfad, 'w', encoding='utf-8') as d:
            d.write(f'grafik_sw_tk_test.py {VERSION_SWTK}, {time.strftime("%d.%m.%Y %H:%M:%S")}, Plattform {sys.platform}, '
                    f'Python {sys.version.split()[0]}  --  {art}\n')
            d.write('\n'.join(zeilen) + f'\n\n{schluss}\n')
        print(f'Bericht: {os.path.abspath(pfad)}  (bitte zurueckschicken)')
    except Exception as e:
        print(f'Bericht nicht geschrieben: {e}')


def nicht_gelaufen(args, grund, abhilfe):
    """Der Test konnte nicht starten: Meldung UND Bericht (damit es etwas zum Zurueckschicken gibt); Rueckgabewert 2."""
    print(f'FEHLER: {grund}. {abhilfe}', file=sys.stderr)
    bericht_schreiben(args.bericht, ART_NICHT, [f'NICHT GELAUFEN  -  {grund}', f'Abhilfe: {abhilfe}'],
                      'ERGEBNIS: NICHT GELAUFEN - am echten Fenster wurde nichts geprueft')
    return 2


class RechnerFaden:
    """Spielt den Rechner: holt K0-Zeichen aus der K0-Warteschlange (Eingabe-Halt) und stellt die Zeichenlage um (wie a032)."""
    def __init__(self, k0, m, protokoll=None):
        self.k0, self.m, self.erhalten, self.protokoll = k0, m, [], protokoll
        self.ende_nach = None                      # nach so vielen Zeichen nicht mehr warten (Eingabe "erledigt")
        self.stop = threading.Event()
        self.th = threading.Thread(target=self._lauf, daemon=True)

    def starten(self):
        self.th.start()
        return self

    def _lauf(self):
        while not self.stop.is_set():
            if self.ende_nach is not None and len(self.erhalten) >= self.ende_nach:
                return
            try:
                t = self.k0.naechstes()
            except Exception:
                return
            if t is None:
                return
            self.erhalten.append(t)
            if t == 'Um. GB': self.m.zeichenlage = 'GB'
            if t == 'Um. KB': self.m.zeichenlage = 'KB'
            if self.protokoll:
                self.protokoll(t)

    def beenden(self):
        self.stop.set()
        try:
            self.k0.abbrechen()
        except Exception:
            pass


class EchtesPult:
    """Attrappe fuer PultFenster: ein echtes Tk-Hauptfenster mit einer Zeichenflaeche (hat den Fokus, wenn das SW nichts erwartet)."""
    def __init__(self, tk):
        self.root = tk.Tk()
        self.root.title('C 8205 Pult (Attrappe, Test)')
        self.root.geometry('+20+40')
        self.cv = tk.Canvas(self.root, width=520, height=240, bg='#d8d8d8', takefocus=1)
        self.cv.pack()
        self.cv.focus_set()
        self.geschlossen = 0

    def _schliessen(self):
        self.geschlossen += 1


class Treiber:
    """Tk-Schleife von Hand fahren (kein mainloop): update() und kurze Pausen; im Trockenlauf stattdessen f.takt()."""
    def __init__(self, root, f, ohne_tk):
        self.root, self.f, self.ohne_tk = root, f, ohne_tk

    def tick(self):
        if self.ohne_tk:
            self.f.takt()
        else:
            self.root.update()

    def pumpe(self, sek):
        t0 = time.time()
        while time.time() - t0 < sek:
            self.tick()
            time.sleep(0.01)

    def warte(self, bedingung, sek=4.0):
        t0 = time.time()
        while time.time() - t0 < sek:
            self.tick()
            if bedingung():
                return True
            time.sleep(0.01)
        return bool(bedingung())


def lauf(args):
    R = Ergebnisse()
    ohne_tk = args.ohne_tk
    from grafik_sw import abbilden
    from grafik_k0 import K0Warteschlange
    from c8205_grafik import SwSenke
    from grafik_sw_fenster import SwFenster, TITEL
    from grafik_sw_tests import FakeMaschine, PultAttrappe, _fake_tk

    if ohne_tk:
        tk = _fake_tk()
        pult = PultAttrappe()
        pult.root.update = lambda: None
    else:
        try:
            import tkinter as tk
        except Exception as e:
            return nicht_gelaufen(args, f'Tkinter fehlt ({type(e).__name__}: {e})',
                                  'Linux: sudo apt install python3-tk; Windows/Mac: Python mit Tcl/Tk installieren (python.org)')
        try:
            pult = EchtesPult(tk)
        except Exception as e:
            return nicht_gelaufen(args, f'kein Bildschirm fuer Tk ({type(e).__name__}: {e})',
                                  'in einem Terminal auf dem Bildschirm starten; Linux ohne Bildschirm: --xvfb (braucht xvfb-run: sudo apt install xvfb)')
    R.info('Test', f'{VERSION_SWTK}, Python {sys.version.split()[0]}, Plattform {sys.platform}' + (', TROCKENLAUF (kein Tkinter)' if ohne_tk else f', Tk {tk.TkVersion}, ECHTER LAUF'))

    m = FakeMaschine()
    k0 = K0Warteschlange(m)
    senke = SwSenke()
    f = SwFenster(pult, senke, k0, m, bei_schliessen=pult._schliessen, tk=tk)
    f.starten()
    T = Treiber(pult.root, f, ohne_tk)
    T.pumpe(0.3)
    faden = None

    def text_im_fenster():
        if ohne_tk:
            return f.txt.text
        return f.txt.get('1.0', 'end-1c')

    try:
        # ---- Fenster -------------------------------------------------------------------------------------------------------------
        R.pruefe('Fenster: Titel', f.w.title() == TITEL, f'Titel ist {f.w.title()!r}', immer=True)
        if ohne_tk:
            R.pruefe('Fenster: 130 x 36, kein Umbruch', (f.txt.cfg['width'], f.txt.cfg['height'], f.txt.cfg['wrap']) == (130, 36, 'none'))
        else:
            R.pruefe('Fenster: 130 x 36, kein Umbruch', (int(f.txt.cget('width')), int(f.txt.cget('height')), str(f.txt.cget('wrap'))) == (130, 36, 'none'),
                     f"width={f.txt.cget('width')} height={f.txt.cget('height')} wrap={f.txt.cget('wrap')}")
            R.pruefe('Fenster: sichtbar', f.w.winfo_viewable() == 1, 'winfo_viewable ist 0 (Fenster nicht aufgeblendet)')
            import tkinter.font as tkfont
            fnt = tkfont.nametofont(str(f.txt.cget('font')))
            R.pruefe('Fenster: Schrift mit fester Breite', fnt.measure('i') == fnt.measure('W') == fnt.measure('0'),
                     f"Breite i/W/0 = {fnt.measure('i')}/{fnt.measure('W')}/{fnt.measure('0')} ({fnt.actual('family')})")
            spalten = f.txt.winfo_width() // max(1, fnt.measure('0'))
            zeilen = f.txt.winfo_height() // max(1, fnt.metrics('linespace'))
            R.pruefe('Fenster: zeigt wirklich 130 Spalten und 36 Zeilen', spalten >= 130 and zeilen >= 36,
                     f'sichtbar etwa {spalten} Spalten und {zeilen} Zeilen (Bildschirm zu klein?)', bei_nein='WARNUNG')
            x, y, b, h = f.w.winfo_rootx(), f.w.winfo_rooty(), f.w.winfo_width(), f.w.winfo_height()
            R.pruefe('Fenster: Lage innerhalb des Bildschirms',
                     x >= 0 and y >= 0 and x + b <= f.w.winfo_screenwidth() and y + h <= f.w.winfo_screenheight(),
                     f'SW-Fenster {b}x{h} bei +{x}+{y}, Bildschirm {f.w.winfo_screenwidth()}x{f.w.winfo_screenheight()}', bei_nein='WARNUNG')

        # ---- Ausgabe -------------------------------------------------------------------------------------------------------------
        for s in ('Hallo', '\t', 'x', '<ZV>', '\n'):
            senke.schreibe(s)
        T.pumpe(0.2)
        zeile1 = text_im_fenster().split('\n')[0]
        R.pruefe('Ausgabe: Text und Tabulator (alle 12 Spalten), <ZV> unsichtbar', zeile1 == 'Hallo' + ' ' * 7 + 'x', f'Zeile 1 ist {zeile1!r}', immer=True)

        # ---- Taste ohne Eingabe-Halt -------------------------------------------------------------------------------------------
        def senden(keysym, char='', state=0):
            """Eine Taste in das SW-Fenster geben: echt durch ein Tk-Ereignis, im Trockenlauf durch direkten Aufruf der Tastenbehandlung."""
            if ohne_tk:
                ev = types.SimpleNamespace(char=char, keysym=keysym, state=state)
                erg = f._taste(ev)
                time.sleep(HALTEZEIT)             # echtes Tastendruecken hat eine Haltezeit; ohne sie waere die zweite Eingabe (Loslassen) sofort faellig
                f._taste_los(ev)                  # Loslassen der Taste (Fall b: zweite Eingabe, U-11)
                return erg
            try:
                if pult.root.focus_get() is not f.txt:
                    f.txt.focus_force()
                    T.pumpe(0.05)
            except Exception:
                pass
            state = zustand_x11(keysym, state)
            f.txt.event_generate('<KeyPress>', keysym=keysym, state=state)
            T.pumpe(HALTEZEIT)                # Haltezeit der Taste (U-11, Fall b)
            f.txt.event_generate('<KeyRelease>', keysym=keysym, state=state)
            T.pumpe(0.02)

        vor_x = text_im_fenster()
        senden('x', 'x')
        T.pumpe(0.2)
        R.pruefe('Eingabe ohne Eingabe-Halt: im Puffer vorgemerkt, keine Anzeige', text_im_fenster() == vor_x and f.eingabe.ausstehend() >= 1,
                 f'Fensterinhalt {vor_x!r} -> {text_im_fenster()!r}, im Puffer: {f.eingabe.ausstehend()}')       # G4-007 (vorher: blockiert)
        m.kanal_wechsel = getattr(m, 'kanal_wechsel', 0) + 1                  # Kanalwechsel (wie a028): der Puffer wird im naechsten Takt verworfen
        T.pumpe(0.2)
        R.pruefe('Kanalwechsel: Puffer verworfen, nichts angezeigt', f.eingabe.ausstehend() == 0 and text_im_fenster() == vor_x,
                 f'im Puffer: {f.eingabe.ausstehend()}, Fensterinhalt {text_im_fenster()!r}')

        # ---- Eingabe-Halt: Titel und Fokus ---------------------------------------------------------------------------------------
        faden = RechnerFaden(k0, m).starten()
        ok = T.warte(lambda: f.eingabe.erwartet() and 'Eingabe erwartet' in (f.w.title() or ''), 3.0)
        R.pruefe('Eingabe-Halt: Titel "Eingabe erwartet"', ok, f'Titel ist {f.w.title()!r}', immer=True)
        if not ohne_tk:
            R.pruefe('Eingabe-Halt: Fenster fordert den Fokus an', pult.root.focus_get() is f.txt,
                     f'Fokus liegt bei {pult.root.focus_get()}; der Fenstermanager darf das verweigern (Windows: Vordergrundsperre) - '
                     'dann klickt der Bediener in das Fenster', bei_nein='WARNUNG')
        R.pruefe('Eingabe-Halt: kein verirrtes Zeichen angekommen', faden.erhalten == [], f'erhalten {faden.erhalten}')

        # ---- Tasten ---------------------------------------------------------------------------------------------------------------
        def tippe(name, keysym, char, soll=None, state=0):
            """soll: erwartete K0-Zeichen; None = aus abbilden() mit der Lage des SW ableiten ([] = nichts erwartet)."""
            vorher = len(faden.erhalten)
            if soll is None:
                soll = abbilden(char, f.eingabe.lage) or []
            senden(keysym, char, state)
            if soll:
                T.warte(lambda: len(faden.erhalten) >= vorher + len(soll), 3.0)
            else:
                T.pumpe(0.3)
            T.warte(lambda: f.eingabe.erwartet() and f.eingabe.zweite is None, 3.0)      # zweite Eingabe (etwa 0,1 s nach dem Umschaltzeichen) gesendet, 011 wieder aktiv
            got = faden.erhalten[vorher:]
            R.pruefe(f'Taste {name}', got == soll, f'erwartet {soll}, bekommen {got}', immer=True)

        # Folge: 2 (erstes Zeichen: Lage unbestimmt, deshalb IMMER Um. KB, 2; G3-008) - A (GB: Um. GB, A) - 3 (KB: Um. KB, 3) - Enter - Tab - Leertaste
        for name, ks, ch, soll in (('2', '2', '2', ['Um. KB', '2']), ('A', 'A', 'A', ['Um. GB', 'A']), ('3', '3', '3', ['Um. KB', '3']),
                                   ('Enter', 'Return', '\r', ['WRZL']), ('Tab', 'Tab', '\t', ['TAB']), ('Leertaste', 'space', ' ', ['ZR'])):
            tippe(name, ks, ch, soll)
        R.pruefe('Folge 2 A 3 Enter Tab Leertaste: genau die erwarteten K0-Zeichen',
                 faden.erhalten == ['Um. KB', '2', 'Um. GB', 'A', 'Um. KB', '3', 'WRZL', 'TAB', 'ZR'], f'bekommen {faden.erhalten}', immer=True)
        T.pumpe(0.1)
        R.pruefe('Anzeige: jedes angenommene Zeichen steht im Fenster (2 A 3, Enter = neue Zeile, Tab, Leertaste), Umschaltzeichen nie',
                 (f.anzeige.text() if ohne_tk else text_im_fenster()).rstrip() == ('Hallo' + ' ' * 7 + 'x\n2A3'),      # Trockenlauf: Logikschicht (das Ersatz-Textfeld ersetzt Zeilen nur grob)
                 f'Fensterinhalt {text_im_fenster()[:60]!r}')

        # Zeichen ausserhalb des R300-Codes: still verworfen (kein Ton, nichts geliefert, kein Absturz)
        for name, ks, ch in (('ä', 'adiaeresis', 'ä'), ('ö', 'odiaeresis', 'ö'), ('ü', 'udiaeresis', 'ü'), ('ß', 'ssharp', 'ß'),
                             ('@', 'at', '@'), ('€', 'EuroSign', '€'), ('§', 'section', '§')):
            tippe(f'{name} (nicht im R300-Code)', ks, ch, soll=[])
        # AltGr: Windows meldet AltGr als Strg+Alt (state 0x20004); X11 als Mod5 (0x80). Die Tilde braucht auf deutscher Tastatur AltGr.
        if sys.platform == 'darwin':
            R.info('Taste AltGr-Tilde', 'macOS: uebersprungen (Wahltaste liefert die Tilde ohne Zusatzzustand)')
        else:
            st = ALTGR_WIN if sys.platform == 'win32' else ALTGR_X11
            tippe(f'~ mit AltGr (state=0x{st:x})', 'asciitilde', '~', state=st)
        # Strg+Taste: keine Eingabe
        tippe('Strg+x (keine Eingabe)', 'x', '\x18', soll=[], state=STRG)
        # Sondertasten
        for ks, ch in (('Left', ''), ('F1', ''), ('Escape', '\x1b'), ('Delete', '\x7f'), ('Home', ''), ('Shift_L', '')):
            tippe(f'{ks} (ohne Wirkung)', ks, ch, soll=[])
        tippe('BackSpace (nichts zum Rechner; Löschwirkung in der Anzeige, G4-006)', 'BackSpace', '\x08', soll=[])

        # ---- Kopieren ------------------------------------------------------------------------------------------------------------
        if ohne_tk:
            R.info('Kopieren', 'im Trockenlauf nicht geprueft')
        else:
            try:
                f.txt.focus_force()
                f.txt.tag_add('sel', '1.0', '1.5')
                f.txt.event_generate('<Control-c>')
                T.pumpe(0.3)
                try:
                    inhalt = pult.root.clipboard_get()
                except Exception as e:
                    inhalt = f'<{type(e).__name__}>'
                R.pruefe('Kopieren: Markieren und Strg+C legen "Hallo" in die Zwischenablage', inhalt == 'Hallo',
                         f'Zwischenablage {inhalt!r} (unter Linux ohne Zwischenablage-Dienst moeglich)', bei_nein='WARNUNG')
            except Exception as e:
                R.fehler('Kopieren', f'{type(e).__name__}: {e}')

        # ---- HWCHECK zusammen mit dem SW-Fenster ------------------------------------------------------------------------------------
        if ohne_tk:
            R.info('HWCHECK', 'im Trockenlauf nicht geprueft (nur Formatierung, siehe grafik_pult_tests.py Klasse HwCheck)')
        else:
            from grafik_hwcheck import HwCheckFenster, hwcheck_zeilen
            hw = types.SimpleNamespace(BZ=0o1234, adr=0o2345, OR=0o123, AC=0o22060635124, AR=0o1234,
                                       trommel=types.SimpleNamespace(einblick=lambda a: 0o12345670123 if a == 0o1234 else 0))
            titel_vorher = f.w.title()
            try:
                H = HwCheckFenster(pult.root, hw)
            except Exception as e:
                R.fehler('HWCHECK: Fenster oeffnen', f'{type(e).__name__}: {e}')
                H = None
            if H is not None:
                T.pumpe(0.4)
                R.pruefe('HWCHECK: Titel', H.win.title() == 'C 8205 HW-Check', f'Titel {H.win.title()!r}')
                R.pruefe('HWCHECK: sichtbar', H.win.winfo_viewable() == 1)
                soll = hwcheck_zeilen(hw)
                ist = [(n.cget('text'), w.cget('text')) for n, w in zip(H._namen, H._werte)]
                R.pruefe('HWCHECK: sechs Zeilen wie hwcheck_zeilen()', ist == soll, f'ist {ist}')
                R.pruefe('HWCHECK: AC und <<AR>> in Vierergruppen von links', ist[3][1] == '2206 0635 124' and ist[4][1] == '1234 5670 123',
                         f'AC {ist[3][1]!r}, <<AR>> {ist[4][1]!r}')
                hw.AC, hw.AR = 0, 0o40
                H.aktualisieren()
                T.pumpe(0.1)
                R.pruefe('HWCHECK: Aktualisierung (AC 0, AR 0040)', H._werte[3].cget('text') == '0000 0000 000' and '0040' in H._namen[4].cget('text'),
                         f"AC {H._werte[3].cget('text')!r}, Name {H._namen[4].cget('text')!r}")
                try:
                    pult.root.tk.call(H.win.protocol('WM_DELETE_WINDOW'))
                except Exception as e:
                    R.warnung('HWCHECK: X-Aufruf', f'{type(e).__name__}: {e}')
                T.pumpe(0.1)
                R.pruefe('HWCHECK: X wirkt nicht, Fenster bleibt', H.win.winfo_exists() == 1 and H.win.winfo_viewable() == 1)
                R.pruefe('HWCHECK: SW-Fenster behaelt den Eingabe-Halt (Titel)', 'Eingabe erwartet' in f.w.title(), f'Titel {f.w.title()!r}, vorher {titel_vorher!r}')
                R.pruefe('HWCHECK: SW-Fenster behaelt den Fokus', pult.root.focus_get() is f.txt, f'Fokus liegt bei {pult.root.focus_get()}', bei_nein='WARNUNG')
                a = (f.w.winfo_rootx(), f.w.winfo_rooty(), f.w.winfo_width(), f.w.winfo_height())
                b = (H.win.winfo_rootx(), H.win.winfo_rooty(), H.win.winfo_width(), H.win.winfo_height())
                ueber = a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
                R.pruefe('HWCHECK: ueberdeckt das SW-Fenster nicht', not ueber, f'SW {a}, HW-Check {b} (x, y, Breite, Hoehe)', bei_nein='WARNUNG')
                R.pruefe('HWCHECK: innerhalb des Bildschirms', b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= H.win.winfo_screenwidth() and b[1] + b[3] <= H.win.winfo_screenheight(),
                         f'HW-Check {b[2]}x{b[3]} bei +{b[0]}+{b[1]}, Bildschirm {H.win.winfo_screenwidth()}x{H.win.winfo_screenheight()} '
                         '(Versatz +1180+40 ist fest eingestellt; auf kleinen Bildschirmen ragt das Fenster hinaus)', bei_nein='WARNUNG')

        # ---- Eingabe erledigt: Fokus zum Pult -------------------------------------------------------------------------------------
        faden.ende_nach = len(faden.erhalten) + len(abbilden('7', f.eingabe.lage))      # danach wartet der "Rechner" nicht mehr
        tippe('7 (letztes Zeichen vor Programmende)', '7', '7')
        T.pumpe(1.0)
        R.pruefe('Eingabe erledigt: Titel ohne "Eingabe erwartet"', 'Eingabe erwartet' not in f.w.title(), f'Titel {f.w.title()!r}')
        if not ohne_tk:
            R.pruefe('Eingabe erledigt: Fokus geht zum Pult zurueck', pult.root.focus_get() is pult.cv, f'Fokus liegt bei {pult.root.focus_get()}', bei_nein='WARNUNG')
        # X am SW-Fenster
        try:
            if ohne_tk:
                f.w.bound['WM_DELETE_WINDOW']()
            else:
                pult.root.tk.call(f.w.protocol('WM_DELETE_WINDOW'))
        except Exception as e:
            R.fehler('X am SW-Fenster', f'{type(e).__name__}: {e}')
        R.pruefe('X am SW-Fenster: ruft die Schliess-Funktion des Pults (wie Strg+C)', pult.geschlossen == 1, f'Aufrufe {pult.geschlossen}')

        # ---- Manuelle Pruefung ----------------------------------------------------------------------------------------------------
        if args.manuell and not ohne_tk:
            manuell(R, T, f, k0, m, pult, senke)
    finally:
        if faden:
            faden.beenden()
        try:
            f.beenden()
            if not ohne_tk:
                pult.root.destroy()
        except Exception:
            pass

    print()
    n_f, n_w = R.anzahl('FEHLER'), R.anzahl('WARNUNG')
    zahlen = f'{R.anzahl("OK")} OK, {n_w} WARNUNG, {n_f} FEHLER'
    if ohne_tk:
        schluss = f'ERGEBNIS (TROCKENLAUF - nicht das echte Fenster, nicht --HWCHECK): {zahlen}'
    else:
        schluss = f'ERGEBNIS (ECHTER LAUF): {zahlen}'
    print(schluss)
    if ohne_tk:
        print('Das war der TROCKENLAUF (Kopieren und HWCHECK wurden nicht geprueft). Fuer das echte Fenster ohne --ohne-tk starten:\n'
              '  python3 testscripte/grafik_sw_tk_test.py')
    bericht_schreiben(args.bericht, ART_TROCKEN if ohne_tk else ART_ECHT, [z for _, z in R.zeilen], schluss)
    return 1 if n_f else 0


CHECKLISTE = """
MANUELLE PRUEFUNG - beide Fenster bleiben offen. Das Terminal zeigt jedes Zeichen, das der "Rechner" bekommt.
Bitte nacheinander ansehen und tippen (Eingabe-Halt ist dauernd aktiv). Mit --DEBUGLOG stehen die SW-Zeilen als \"Protokoll: ...\" im Terminal.
  1. Lage/Groesse: SW-Fenster rechts unten, Pult-Attrappe links oben, HW-Check-Fenster rechts oben; ueberdecken sie sich? Passt alles auf den Bildschirm?
  2. Schrift: gleichmaessige Spalten (Zeile "Spaltenlineal" im SW-Fenster), lesbar, Tabulator alle 12 Spalten.
  3. Tippen Sie:  a  A  3  Enter  Tab  Leertaste  - im Terminal stehen die K0-Zeichen, im Fenster erscheint jedes angenommene Zeichen (a A 3, Zeilenwechsel, Tab, Leerschritt), kein Umschaltzeichen.
  4. Umlaute und AltGr:  ä ö ü ß  @  €  - muessen verworfen werden (keine Zeile \"Rechner bekommt\", keine Anzeige).
     Dann  [  ]  ~  #  (AltGr+8, AltGr+9, AltGr+Plus, Raute-Taste): gehen durch (Um. GB oder Um. KB je nach Lage, dann das Zeichen; im Fenster nur das Zeichen).
     Dann den Gravis (Umschalt+Akzenttaste, danach Leertaste): Verhalten am echten Fenster unbekannt, bitte melden, was im Terminal und im Fenster erscheint.
  5. Shift-Zahlenreihe:  ! \" § $ % & / ( ) =  - Zeichen im R300-Code gehen durch (Umschaltzeichen nur bei Wechsel der Lage), die anderen werden still verworfen.
     Tippen Sie auch ein Mal schnell hintereinander (a A a A): jedes Zeichen, das im Fenster erscheint, muss im Terminal als \"Rechner bekommt\" stehen; blockierte Tasten (kein 011 aktiv) erscheinen weder noch.
  6. Fokus: klicken Sie auf die Pult-Attrappe, dann in das SW-Fenster; Tippen geht immer an das SW-Fenster, wenn es den Fokus hat.
  7. Kopieren: im SW-Fenster mit der Maus markieren (wird sofort kopiert) und in einen Editor einfuegen; Strg+C und Strg+A ebenso; Rechtsklick-Menue.
  8. X am SW-Fenster: es schliesst sich NICHT von selbst (ruft nur die Schliess-Funktion des Pults); im Test passiert daher nichts sichtbar.
Zum Beenden: im Terminal Enter druecken.
"""


def manuell(R, T, f, k0, m, pult, senke):
    print(CHECKLISTE, flush=True)
    senke.schreibe('Spaltenlineal: ' + ''.join(str(i % 10) for i in range(1, 116)) + '\n')
    senke.schreibe('0         1         2         3         4         5         6         7         8         9         10        11        12        13\n')
    fertig = threading.Event()
    threading.Thread(target=lambda: (sys.stdin.readline(), fertig.set()), daemon=True).start()
    faden = RechnerFaden(k0, m, protokoll=lambda t: print(f'  Rechner bekommt: {t!r}  (Lage Rechner {m.zeichenlage}, Lage SW {f.eingabe.lage})', flush=True)).starten()
    try:
        while not fertig.is_set():
            try:
                T.tick()
            except Exception:
                break
            time.sleep(0.02)
    finally:
        faden.beenden()
    R.info('Manuell', 'durchgefuehrt (Ergebnis der Sichtpruefung bitte selbst mitteilen)')


def _log_ins_terminal(pfad):
    """SWTK-003: Zeilen der Kategorie SW aus dem Debug-Protokoll auch im Terminal zeigen (Faden liest die Datei mit)."""
    def tail():
        try:
            with open(pfad, encoding='utf-8') as fh:
                while True:
                    z = fh.readline()
                    if not z:
                        time.sleep(0.05)
                        continue
                    if ' SW ' in z[:40]:
                        print('  Protokoll: ' + z.rstrip(), flush=True)
        except Exception:
            return
    threading.Thread(target=tail, daemon=True).start()


def main():
    ap = argparse.ArgumentParser(description='Test des echten SW-Fensters und des HW-Check-Fensters (Tkinter)')
    ap.add_argument('--manuell', action='store_true', help='danach Fenster offen lassen, selbst tippen (Checkliste)')
    ap.add_argument('--xvfb', action='store_true', help='Linux ohne Bildschirm: ueber xvfb-run starten')
    ap.add_argument('--ohne-tk', dest='ohne_tk', action='store_true', help='Trockenlauf mit Ersatzmodul (kein Tkinter)')
    ap.add_argument('--DEBUGLOG', '--debuglog', dest='DEBUGLOG', nargs='?', const='sw_tk_test_debug.log', default=None, metavar='DATEI',
                    help='Fehlersuch-Protokoll des SW-Fensters in DATEI schreiben (Voreinstellung sw_tk_test_debug.log), SW-Zeilen auch im Terminal (SWTK-003)')
    ap.add_argument('--bericht', default=None, help='Berichtsdatei (Voreinstellung: sw_tk_test_bericht.txt, beim Trockenlauf sw_tk_test_trockenlauf.txt)')
    args = ap.parse_args()
    if args.bericht is None:
        args.bericht = 'sw_tk_test_trockenlauf.txt' if args.ohne_tk else 'sw_tk_test_bericht.txt'
    if args.xvfb and not os.environ.get('SWTK_IN_XVFB'):
        if not shutil.which('xvfb-run'):
            return nicht_gelaufen(args, 'xvfb-run nicht gefunden', 'sudo apt install xvfb (nur Linux); sonst ohne --xvfb auf einem Bildschirm starten')
        rest = [a for a in sys.argv[1:] if a != '--xvfb']
        env = dict(os.environ, SWTK_IN_XVFB='1')
        return subprocess.call(['xvfb-run', '-a', sys.executable, os.path.abspath(__file__)] + rest, env=env)
    if args.DEBUGLOG:
        import grafik_debuglog as DL
        DL.starten(args.DEBUGLOG)
        DL.log('START', f'{VERSION_SWTK}, Python {sys.version.split()[0]}, {sys.platform}, Aufruf: {sys.argv}')
        print(f'Debug-Log wird geschrieben: {os.path.abspath(args.DEBUGLOG)}', file=sys.stderr)
        _log_ins_terminal(args.DEBUGLOG)
    return lauf(args)


if __name__ == '__main__':
    sys.exit(main())
