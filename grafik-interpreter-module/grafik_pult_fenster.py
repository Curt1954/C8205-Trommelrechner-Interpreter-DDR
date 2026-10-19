# -*- coding: utf-8 -*-
"""
grafik_pult_fenster.py - Tk-Schicht des Bedienpult-Fensters im Modus GRAFIK (Stufe 2). Nur Standardbibliothek (Tkinter).
Version: G2-001

Die gesamte Logik steckt in grafik_pult.PultSteuerung; hier nur Zeichnen (Canvas, Foto + Teilgrafiken), Maus, Computertastatur, Fenster schliessen.
ACHTUNG: In der Entwicklungsumgebung gab es kein Tkinter; dieses Fenster wurde dort NICHT gestartet (nur mit einem Ersatzmodul
geprueft, siehe testscripte/grafik_pult_tests.py). Erster echter Start: auf dem Rechner des Auftraggebers.

Fenster: feste Groesse 1148 x 860 px, nicht skalierbar (GRAFIK_Beschreibung §3.1 (alt: Dok. 01 Abschnitt 1.6)).
"""
import os
import time

import grafik_fensterlage as lage

import sys

from grafik_pult import LAMPENTAKT_S, ENDE
from grafik_debuglog import log

VERSION_FENSTER = 'G4-008'


class PultFenster:
    def __init__(self, steuerung, ordner, bei_schliessen=None, tk=None):
        """steuerung: PultSteuerung; ordner: Ordner 'pult'; bei_schliessen(): X am Fenster (wie Strg+C);
        tk: Modul tkinter (Parameter fuer Pruefungen mit Ersatzmodul)."""
        if tk is None:
            import tkinter as tk
        self.tk = tk
        self.s = steuerung
        self.ordner = ordner
        self.bei_schliessen = bei_schliessen
        self.root = tk.Tk()
        self.root.title('C 8205 Bedienpult')
        self.root.resizable(False, False)
        m = steuerung.m
        self.cv = tk.Canvas(self.root, width=m['breite'], height=m['hoehe'], highlightthickness=0, bg='white', takefocus=1)
        self.cv.pack()
        try:                                                  # FL-001: letzte Position (Vorgabe: der Fenstermanager entscheidet)
            self.root.update_idletasks()
            if lage.anwenden(self.root, 'pult', m['breite'], m['hoehe']):
                log('FOKUS', 'Pult: Fensterlage aus der letzten Sitzung')
        except Exception:
            pass
        self._hintergrund = tk.PhotoImage(file=os.path.join(ordner, m['bild']))
        self.cv.create_image(0, 0, image=self._hintergrund, anchor='nw')
        self._bilder, self._items = {}, {}
        self._fokus_klick = False
        self.cv.bind('<ButtonPress-1>', self._maus_druecken)
        self.cv.bind('<ButtonRelease-1>', self._maus_loslassen)
        self.cv.bind('<Key>', self._taste)
        self.cv.bind('<KeyRelease>', self._taste_los)
        self.sw_weiter = None       # G4-008: SwFenster; Tasten, die beim Pult ankommen, waehrend K0/SW angewaehlt ist, gehen an dessen Eingabe
        self.cv.bind('<FocusOut>', lambda e: self.s.fokus_verloren(time.monotonic()))
        self.root.protocol('WM_DELETE_WINDOW', self._schliessen)
        self._gedrueckt = None
        self.beendet = False
        self._titel = None
        self._abbruch = False
        self.zusatz = []            # Zusatzfenster mit aktualisieren() (HW-Check), im 40-ms-Takt
        self.wiedergabe = None      # grafik_debuglog.Wiedergabe oder None (Schalter --WIEDERGABE, nur Debug-Modus)
        self.letzter_takt = time.monotonic()
        try:
            self._merker = lage.Merker(self.root, 'pult', time.monotonic)
        except Exception:
            self._merker = None

    def _foto(self, name):
        if name not in self._bilder:
            self._bilder[name] = self.tk.PhotoImage(file=os.path.join(self.ordner, 'grafiken', name))
        return self._bilder[name]

    def zeichnen(self):
        for z in self.s.zeichenliste():
            alt = self._items.get(z['id'])
            zustand = 'normal' if z['sichtbar'] else 'hidden'
            if alt is None:
                it = self.cv.create_image(z['x'], z['y'], image=self._foto(z['bild']), anchor='nw', state=zustand)
                self._items[z['id']] = (it, z['bild'])
            else:
                it, bild = alt
                if bild != z['bild']:
                    self.cv.itemconfigure(it, image=self._foto(z['bild']))
                    self.cv.coords(it, z['x'], z['y'])
                    self._items[z['id']] = (it, z['bild'])
                self.cv.itemconfigure(it, state=zustand)

    # --- Ereignisse
    def _wiedergabe_sperrt(self, was):
        """Waehrend eine Klickspur abgespielt wird, wirken Maus und Tastatur nicht (sonst stoeren sie den Ablauf); X und Strg+C gehen weiter."""
        if self.wiedergabe is not None and not self.wiedergabe.fertig:
            log('MAUS', f'{was} ignoriert: Wiedergabe laeuft')
            return True
        return False

    def _maus_druecken(self, ev):
        if self._wiedergabe_sperrt('Mausklick'):
            return
        fokus = self.root.focus_get()
        log('MAUS', f'Druck x={ev.x} y={ev.y} state={ev.state} fokus={fokus} canvas_hat_fokus={fokus is self.cv}')
        if fokus is not self.cv:
            # Ein Klick, der nur den Fokus zurueckholt, loest keine Taste aus (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitt 1.7), Fokus)
            log('MAUS', '-> nur Fokus zurueckgeholt, KEINE Taste (Fokusregel)')
            self.cv.focus_set()
            return
        ziel = self.s.treffer(ev.x, ev.y)
        if ziel is None:
            log('MAUS', '-> kein Element unter dem Zeiger')
            return
        umschalt = bool(ev.state & 0x0001)
        ok = self.s.klick(ziel, time.monotonic(), umschalt=umschalt)
        log('MAUS', f'-> Ziel {ziel} umschalt={umschalt} wirkt={ok}')
        if ok:
            self._gedrueckt = ziel

    def _maus_loslassen(self, ev):
        if self._wiedergabe_sperrt('Loslassen'):
            return
        log('MAUS', f'Loslassen x={ev.x} y={ev.y}')
        # Loslassen zaehlt, egal wo der Zeiger steht
        self.s.loslassen('E', time.monotonic())
        self.s.loslassen('M', time.monotonic())
        self._gedrueckt = None

    def _taste(self, ev):
        if self._wiedergabe_sperrt('Computertaste'):
            return
        zeichen = ev.char or ''
        w = self.sw_weiter
        if w is not None:
            # G4-008: Der Fokus pendelt zwischen SW-Fenster und Pult (nach jedem Zeichen zurueck zum Pult, erst bei der naechsten Eingabeaufforderung
            # wieder ins SW-Fenster, Lauf 19.10.2026: im Log 'Computertastatur ... wirkt=False' fuer verschluckte Zeichen). Eine Taste, die in dieser
            # Luecke am Pult ankommt, ist eine SW-Eingabe: sie geht an die Eingabe des SW-Fensters (dort in den Puffer), solange K0/SW angewaehlt ist.
            try:
                if w.taste_vom_pult(ev):
                    return 'break'
            except Exception as e:
                log('FEHLER', f'Taste vom Pult an das SW-Fenster: {e!r}')
        log('TASTE', f'Computertastatur char={zeichen!r} keysym={getattr(ev, "keysym", "")}')
        if zeichen:
            ok = self.s.tastatur(zeichen, time.monotonic())
            log('TASTE', f'-> wirkt={ok}')

    def _taste_los(self, ev):
        """G4-008: Loslassen einer Taste am Pult gehoert zur SW-Eingabe, wenn deren Druecken dorthin ging (Umschalttaste, zweite Eingabe beim Loslassen)."""
        w = self.sw_weiter
        if w is None or self._wiedergabe_sperrt('Taste loslassen'):
            return
        try:
            w.taste_los_vom_pult(ev)
        except Exception as e:
            log('FEHLER', f'Loslassen vom Pult an das SW-Fenster: {e!r}')

    def _schliessen(self):
        self.s.fenster_schliessen(time.monotonic())
        if self.bei_schliessen:
            self.bei_schliessen()

    # --- Takt
    def abbruch_anfordern(self):
        """Aus dem Signalhandler (Strg+C): nur ein Flag; das Beenden macht der naechste Takt."""
        self._abbruch = True

    def takt(self):
        if self.beendet:
            return
        t_start = time.monotonic()
        self.letzter_takt = t_start
        try:
            if self._abbruch:
                self.s.fenster_schliessen(time.monotonic())
                self.beenden()
                return
            if self.s.tick(time.monotonic()) == ENDE:
                self.beenden()
                return
            self.zeichnen()
            if self._merker is not None:
                self._merker.merken()
            t_zusatz = time.monotonic()
            for z in self.zusatz:
                z.aktualisieren()
            if time.monotonic() - t_zusatz > 0.1:
                log('LANGSAM', f'Zusatzfenster (HW-Check) aktualisieren dauerte {time.monotonic() - t_zusatz:.3f} s')
            titel = 'C 8205 Bedienpult' + (' - Eingabe erwartet (Eingabetasten frei)' if self.s.eingabe_erwartet() else '')
            if titel != self._titel:
                self._titel = titel
                self.root.title(titel)
        except Exception:
            # Eine Ausnahme darf die Taktkette nicht abreissen lassen (sonst bleibt das Pult stehen): melden und weitermachen
            import traceback
            traceback.print_exc()
            log('FEHLER', 'Takt: ' + traceback.format_exc())
        if time.monotonic() - t_start > 0.15:
            log('LANGSAM', f'Takt dauerte {time.monotonic() - t_start:.3f} s')
        if not self.beendet:
            self.root.after(int(LAMPENTAKT_S * 1000), self.takt)

    def debug_einhaengen(self):
        """Nur mit --DEBUGLOG (echtes Tk): Fokuswechsel aller Fenster, Ausnahmen in Rueckrufen und Klicks im Zusatzfenster protokollieren."""
        def fokus(ev, was):
            try:
                log('FOKUS', f'{was} {ev.widget}')
            except Exception:
                pass
        self.root.bind_all('<FocusIn>', lambda e: fokus(e, 'FocusIn'), add='+')
        self.root.bind_all('<FocusOut>', lambda e: fokus(e, 'FocusOut'), add='+')
        self.root.bind_all('<ButtonPress>', lambda e: fokus(e, f'Klick Maustaste {getattr(e, "num", "?")} in'), add='+')

        def cb_fehler(exc, val, tb):
            import traceback
            txt = ''.join(traceback.format_exception(exc, val, tb))
            log('FEHLER', 'Tk-Rueckruf: ' + txt)
            sys.stderr.write(txt)
        self.root.report_callback_exception = cb_fehler

    # --- Wiedergabe einer Klickspur (Debug)
    def wiedergabe_einhaengen(self, wiedergabe):
        self.wiedergabe = wiedergabe

    def _wiedergabe_planen(self):
        """Naechstes Ereignis der Klickspur genau zu seiner Zeit im Tk-Thread (wie ein echter Mausklick), nicht im 40-ms-Takt."""
        w = self.wiedergabe
        if w is None or w.fertig or self.beendet:
            return
        ms = int(round(w.bis_naechster(time.monotonic()) * 1000))
        self.root.after(max(0, ms), self._wiedergabe_schritt)

    def _wiedergabe_schritt(self):
        if self.beendet or self.wiedergabe is None:
            return
        try:
            self.wiedergabe.faellige(time.monotonic())
        except Exception:
            import traceback
            traceback.print_exc()
            log('FEHLER', 'Wiedergabe: ' + traceback.format_exc())
            # faellige() hat den Zaehler schon weitergesetzt: das fehlerhafte Ereignis ist ausgelassen, der Rest laeuft weiter
        self._wiedergabe_planen()

    def beenden(self):
        self.beendet = True
        try:
            if self._merker is not None:
                self._merker.beenden()          # FL-001: letzte Lage sofort schreiben
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def starten(self):
        self.zeichnen()
        self.cv.focus_set()
        self.root.after(int(LAMPENTAKT_S * 1000), self.takt)
        if self.wiedergabe is not None:
            self.wiedergabe.starten(time.monotonic())
            self._wiedergabe_planen()
        self.root.mainloop()
