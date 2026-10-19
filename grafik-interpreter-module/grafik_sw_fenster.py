# -*- coding: utf-8 -*-
"""
grafik_sw_fenster.py - Tk-Schicht des SW-Fensters im Modus GRAFIK (Stufe 3). Nur Standardbibliothek (Tkinter).
Version: G4-008

Ein Tk-Prozess, zwei Fenster (GRAFIK_Beschreibung §11 (alt: Dok. 04 Punkt 16)): das SW-Fenster ist ein Toplevel des Pult-Fensters.
Aussehen wie das bisherige Fenster "SW Ausgabe": 130 x 36 Zeichen, Markieren und Kopieren. Jedes angenommene Zeichen der Eingabe wird
angezeigt (Entscheidung 18.10.2026, GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-04): ueber dieselbe Warteschlange wie die Ausgabe des Rechners (eine Schreibposition).
Die Logik (Schreibposition, Tabulator, Anschlag, Eingabeabbildung) steckt in grafik_sw.py.

ACHTUNG: In der Entwicklungsumgebung gab es kein Tkinter; dieses Fenster wurde dort NICHT gestartet (nur gegen ein
Ersatzmodul geprueft). Erster echter Start: auf dem Rechner des Auftraggebers.

Faden-Regel: SwSenke.schreibe() wird im Rechner-Thread aufgerufen; der Hoerer legt den Text nur in eine Warteschlange ab.
Alle Tk-Aufrufe laufen im Fenster-Thread (Takt 25 ms).

Fokus (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitt 1.7), Entwurf 69/72): Erwartet der Rechner eine SW-Eingabe, fordert das Fenster den Fokus an
(lift + focus_set, nicht erzwungen). Der Titel zeigt dann "Eingabe erwartet"; ein Mausklick in das Fenster holt den Fokus
(der Klick dient nur dem Fokus). Ist die Eingabe erledigt, geht der Fokus zum Pult zurueck.
"""
import queue
import sys
import time

from grafik_sw import SwAnzeige, SwEingabe
from grafik_debuglog import log
import grafik_fensterlage as lage
import grafik_tastatur as TAST

VERSION_SW_FENSTER = 'G4-008'
TITEL = 'C 8205 SW-Fenster'
TAKT_MS = 10        # G4-007: der Takt gibt auch die Eingaben aus dem Puffer an den Rechner weiter (je 011 eine); 10 ms halten die Verzoegerung klein


class SwFenster:
    def __init__(self, pult_fenster, senke, k0, maschine, bei_schliessen=None, tk=None, zwischenablage='auto'):
        """pult_fenster: PultFenster (liefert root und den Fokus-Rueckweg); senke: SwSenke; k0: K0Warteschlange;
        maschine: Machine; bei_schliessen(): X am Fenster (wie Strg+C); tk: Modul tkinter (Pruefungen mit Ersatzmodul)."""
        if tk is None:
            import tkinter as tk
        self.tk = tk
        self.pult = pult_fenster
        self.senke = senke
        self.anzeige = SwAnzeige()
        self.q = queue.Queue()      # Text fuer die Anzeige: Ausgabe des Rechners UND Eingabe (eine Reihenfolge)
        self.eingabe = SwEingabe(k0, maschine, echo=self._echo_eingabe, rueck=lambda: self.q.put('\b'))      # G4-006: Rücktaste über dieselbe Warteschlange wie Ausgabe und Eingabe
        self.bei_schliessen = bei_schliessen
        self.zwischenablage = zwischenablage if zwischenablage in ('auto', 'tk', 'system') else 'auto'
        self.beendet = False
        self._titel = None
        self._titel_meldung = None
        self._titel_bis = 0.0
        self._fokus_angefordert = False
        self._inaktiv_seit = None
        self._letzte = ['', 0.0]
        self.w = tk.Toplevel(pult_fenster.root)
        self.w.title(TITEL)
        self.txt = tk.Text(self.w, width=130, height=36, wrap='none', font='TkFixedFont', state='disabled', takefocus=1)
        self.txt.pack(fill='both', expand=True)
        self.w.resizable(False, False)
        self.w.update_idletasks()
        b, h = self.w.winfo_reqwidth(), self.w.winfo_reqheight()
        x = max(0, self.w.winfo_screenwidth() - b - 10)
        y = max(0, self.w.winfo_screenheight() - h - 70)     # Rand fuer Taskleiste/Dock (wie "SW Ausgabe")
        self.w.geometry(f'+{x}+{y}')
        if lage.anwenden(self.w, 'sw', b, h):           # FL-001: letzte Position (Vorgabe: rechts unten)
            log('SW', 'Fensterlage aus der letzten Sitzung')
        self._merker = lage.Merker(self.w, 'sw', time.monotonic)
        self.w.protocol('WM_DELETE_WINDOW', self._schliessen)
        self._bindungen()
        # Hoerer: schon vorhandener Text zuerst, dann alles Neue
        for teil in list(self.senke.text):          # je Aufruf ein Zeichen, damit <Name> als benanntes Zeichen erkennbar bleibt
            self.q.put(teil)
        self.senke.hoere(self.q.put)

    def _echo_eingabe(self, text):
        """Angezeigte Eingabe (U-9, Stufe 4 S4-08): derselbe Klang wie jede Schreibwerkausgabe, keine Schreibwerkzeit, keine Sperre;
        der Selektor SW wirkt nicht auf sie. Dann wie bisher in die Anzeige-Warteschlange."""
        sw = getattr(self.senke, 'schreibwerk', None)
        log('SW', f'Eingabeklang {text!r}: Schreibwerk={sw is not None}, Mischer={getattr(sw, "mischer", None) is not None}')   # G4-005: Spur fuer "kein Klick beim ersten Zeichen"
        if sw is not None:
            try:
                sw.eingabe(text)
            except Exception as e:
                log('FEHLER', f'SW Eingabeklang: {e!r}')
        self.q.put(text)

    # --- Markieren und Kopieren (wie im bisherigen Fenster) --------------------------------------------------------
    def _meldung(self, s):
        self._titel_meldung = s
        self._titel_bis = time.monotonic() + 2.5

    def _kopiere(self, _ev=None):
        try:
            text = self.txt.get('sel.first', 'sel.last')
        except self.tk.TclError:
            return 'break'
        if not text:
            return 'break'
        if text == self._letzte[0] and time.monotonic() - self._letzte[1] < 5.0:
            self._meldung(f'kopiert ({len(text)} Zeichen)')
            return 'break'
        from c8205_interp import zwischenablage_kopieren
        ok, verfahren = zwischenablage_kopieren(self.w, text, self.zwischenablage)
        if ok:
            self._letzte[0], self._letzte[1] = text, time.monotonic()
            self._meldung(f'kopiert ({len(text)} Zeichen, {verfahren})')
        else:
            self._meldung('Kopieren fehlgeschlagen')
        return 'break'

    def _alles_markieren(self, _ev=None):
        self.txt.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def _bindungen(self):
        for wg in (self.txt, self.w):
            for folge in ('<Control-c>', '<Control-C>', '<Control-Insert>'):
                wg.bind(folge, self._kopiere)
            for folge in ('<Control-a>', '<Control-A>'):
                wg.bind(folge, self._alles_markieren)
        self.txt.bind('<ButtonRelease-1>', lambda e: self.w.after(20, self._kopiere), add='+')
        self.txt.bind('<ButtonPress-1>', self._maus_druecken, add='+')
        self.txt.bind('<Key>', self._taste)
        self.txt.bind('<KeyRelease>', self._taste_los, add='+')
        self._umschalt = {}                    # keysym -> Zeitpunkt des Druckens (echter Tastenabstand, GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-11, Z-2)
        self._letzte_taste = 0.0               # G4-011: Zeitpunkt der zuletzt gedrueckten Zeichentaste (bei gehaltener Umschalttaste zaehlt ab hier)
        self.txt.bind('<Tab>', self._taste)
        menue = self.tk.Menu(self.w, tearoff=0)
        menue.add_command(label='Kopieren', command=self._kopiere)
        menue.add_command(label='Alles markieren', command=self._alles_markieren)

        def kontext(e):
            try:
                menue.tk_popup(e.x_root, e.y_root)
            finally:
                menue.grab_release()
        self.txt.bind('<Button-3>', kontext)
        if sys.platform == 'darwin':
            self.txt.bind('<Button-2>', kontext)
            self.txt.bind('<Control-Button-1>', kontext)

    # --- Eingabe ----------------------------------------------------------------------------------------------------
    def _maus_druecken(self, ev):
        """Ein Klick, der nur den Fokus holt, dient nur dem Fokus (Markieren bleibt erlaubt)."""
        try:
            if self.w.focus_get() is not self.txt:
                self.txt.focus_set()
        except Exception:
            pass

    ABSTAND_MAX = 0.1                                    # s, G4-011 (Anforderung: zwei Eingaben im Abstand von etwa 0,1 s); Lauf 19.10.: 0,3 s kleckerte merklich
    UMSCHALT = ('Shift_L', 'Shift_R', 'ISO_Level3_Shift', 'Alt_R', 'Mode_switch')

    def _taste_los(self, ev):
        keysym = getattr(ev, 'keysym', '')
        if keysym in self.UMSCHALT:
            self._umschalt.pop(keysym, None)
            return None
        erg = self.eingabe.loslassen()                  # Fall (b): Zeichen beim Loslassen der Zeichentaste (jetzt frei; geht an den naechsten 011)
        if erg is not None:
            log('SW', f'zweite Eingabe beim Loslassen -> {erg}')
        return None

    def _taste(self, ev):
        state = getattr(ev, 'state', 0)
        keysym = getattr(ev, 'keysym', '')
        if keysym in self.UMSCHALT:
            self._umschalt.setdefault(keysym, time.monotonic())     # Zeit des ersten Druckens (Wiederholung ignorieren)
            return None
        if keysym == 'BackSpace' and not (state & 0x4) and not (state & 0x8):     # G4-006: Löschwirkung in der Anzeige, kein Name, kein Ton, nichts zum Rechner
            erg = self.eingabe.ruecktaste()
            log('SW', f'Rücktaste -> {erg} (Puffer: {len(self.eingabe.puffer)})')
            return 'break'
        zeichen = ev.char or ''
        if (state & 0x4) and not (state & 0x20000):      # Strg (ohne AltGr unter Windows): Kopieren u. a., keine Eingabe
            return None
        if sys.platform.startswith('linux') and (state & 0x8):    # Alt
            return None
        if keysym in ('Return', 'KP_Enter'):
            zeichen = '\r'
        elif keysym == 'Tab':
            zeichen = '\t'
        elif keysym == 'space':
            zeichen = ' '
        if not zeichen or (ord(zeichen[0]) < 32 and zeichen not in ('\r', '\t')):
            # G3-007: nur Protokoll, kein neues Verhalten. Zeigt am echten Fenster, was z. B. die Tottaste (Gravis,
            # keysym dead_grave, char leer) wirklich liefert (GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-09, B-3).
            log('SW', f'Taste ignoriert char={zeichen!r} keysym={keysym} state={hex(state)}')
            return 'break' if keysym == 'Tab' else None  # Sondertasten, Funktionstasten, Pfeile ... ohne Wirkung
        abstand = None                                  # Fall (b): ohne Umschalttaste geht das Zeichen beim Loslassen
        jetzt = time.monotonic()
        if self._umschalt:                              # Fall (a): echte Zeit zwischen Umschalttaste und Zeichentaste
            # G4-011 (Lauf 19.10.2026): Wird die Umschalttaste ueber mehrere Zeichen gehalten (!"%/()=?), darf der Abstand nicht ab ihrem ersten
            # Druecken laufen (sonst kam ':' erst nach 6 s). Es zaehlt ab der spaeteren von Umschalttaste und vorheriger Zeichentaste, hoechstens
            # ABSTAND_MAX (so lange liegen zwei Tasten eines Tastendrucks nie auseinander).
            ab = max(min(self._umschalt.values()), self._letzte_taste)
            abstand = min(self.ABSTAND_MAX, max(0.0, jetzt - ab))
        self._letzte_taste = jetzt
        ergebnis = self.eingabe.tippen(zeichen[0], abstand)      # geliefert | folgt | blockiert | verworfen
        log('SW', f'Taste char={zeichen!r} keysym={keysym} -> {ergebnis} (Puffer: {len(self.eingabe.puffer)})')
        return 'break'

    def taste_vom_pult(self, ev):
        """G4-008: Eine Taste, die das PULT-Fenster bekam (der Fokus lag in der Luecke zwischen zwei Eingabeaufforderungen dort). Ist K0/SW angewaehlt,
        gilt sie als SW-Eingabe und laeuft durch dieselbe Logik wie im SW-Fenster (Puffer, Umschaltzeichen, Rücktaste). Umschalttasten werden immer
        gemerkt (der echte Tastenabstand, U-11). Rueckgabe True: die Taste ist hier behandelt, das Pult soll sie nicht mehr auswerten."""
        keysym = getattr(ev, 'keysym', '')
        if keysym in self.UMSCHALT:
            self._taste(ev)
            return True
        if not self.eingabe._kanal_sw():
            return False
        log('SW', f'Taste am Pult angekommen (Fokus nicht im SW-Fenster): char={getattr(ev, "char", "")!r} keysym={keysym}')
        self._taste(ev)
        return True

    def taste_los_vom_pult(self, ev):
        """G4-008: Loslassen, am Pult angekommen (Gegenstueck zu taste_vom_pult)."""
        self._taste_los(ev)

    HALTEZEIT_WIEDERGABE = 0.12                          # s zwischen Druecken und Loslassen bei Ereignisart tipp (wie HALTEZEIT im Tk-Test)

    def tipp_wiedergabe(self, keysym):
        """Klickspur (Ereignisart tipp): eine Taste im SW-Fenster als ECHTES Tk-Tastenereignis (event_generate), das durch <Key> -> _taste laeuft.
        Das Ereignis geht an das Fenster mit dem Tastaturfokus; liegt der nicht auf dem SW-Text, wird er geholt (und im Log vermerkt)."""
        try:
            fokus = self.w.focus_get()
            log('SW', f'tipp {keysym}: Fokus auf SW-Text={fokus is self.txt} (focus_get={fokus}), Eingabe erwartet={self.eingabe.erwartet()}, '
                      f'Puffer={len(self.eingabe.puffer)}, Lage SW={self.eingabe.lage}')
            if fokus is not self.txt:
                log('SW', 'tipp: Fokus war NICHT auf dem SW-Text, wird geholt (focus_force)')
                self.txt.focus_force()
            zusatz = {}
            if sys.platform.startswith('linux') and TAST.braucht_altgr(keysym):      # G4-010: belegungsabhaengig (--TASTATUR)
                zusatz['state'] = 0x80                  # X11: Mod5 = AltGr, sonst kommt die Grundbelegung der Taste an (Lauf 18.10.2026: bracketleft als 8)
            self.txt.event_generate('<KeyPress>', keysym=keysym, **zusatz)
            # G3-006: Loslassen nach einer Haltezeit wie beim echten Tippen (Lauf 18.10.2026: Haltezeit 0 -> zweite Eingabe sofort faellig -> blockiert)
            self.w.after(int(self.HALTEZEIT_WIEDERGABE * 1000),
                         lambda k=keysym, z=dict(zusatz): self.txt.event_generate('<KeyRelease>', keysym=k, **z))
            return True
        except Exception:
            import traceback
            log('FEHLER', 'SW tipp: ' + traceback.format_exc())
            return False

    # --- Takt -------------------------------------------------------------------------------------------------------
    def _zeichnen(self):
        try:
            while True:
                teil = self.q.get_nowait()
                log('SWAUS', repr(teil))
                self.anzeige.schreibe(teil)
        except queue.Empty:
            pass
        geaendert = self.anzeige.hole_geaenderte()
        if not geaendert:
            return
        t = self.txt
        t.configure(state='normal')
        try:
            vorhanden = int(float(t.index('end-1c').split('.')[0]))      # Zeilen im Widget
            for n in geaendert:
                while vorhanden < n + 1:
                    t.insert('end', '\n')
                    vorhanden += 1
                t.delete(f'{n + 1}.0', f'{n + 1}.end')
                t.insert(f'{n + 1}.0', self.anzeige.zeile_text(n))
            t.see('end')
        finally:
            t.configure(state='disabled')

    def _fokus(self):
        aktiv = self.eingabe.eingabe_aktiv()
        if aktiv and not self._fokus_angefordert:
            self._fokus_angefordert = True
            try:
                self.w.lift()
                self.txt.focus_set()
            except Exception:
                pass
            log('SW', 'Eingabe erwartet: Fokus angefordert')
        elif aktiv:
            self._inaktiv_seit = None
        elif not aktiv and self._fokus_angefordert:
            # Entprellen: zwischen zwei Eingabe-Halts eines Programms (Zeichen fuer Zeichen) nicht jedes Mal zum Pult wechseln
            jetzt = time.monotonic()
            if self._inaktiv_seit is None:
                self._inaktiv_seit = jetzt
            if jetzt - self._inaktiv_seit < 0.4:
                return aktiv
            self._inaktiv_seit = None
            self._fokus_angefordert = False
            try:
                if self.w.focus_get() is self.txt:
                    self.pult.root.lift()
                    self.pult.cv.focus_set()
                    log('SW', 'Eingabe erledigt: Fokus zum Pult')
            except Exception:
                pass
        return aktiv

    def _titel_setzen(self, aktiv):
        titel = TITEL
        if aktiv:
            titel += ' - Eingabe erwartet'
        elif self._titel_meldung and time.monotonic() < self._titel_bis:
            titel += ' - ' + self._titel_meldung
        if titel != self._titel:
            self._titel = titel
            self.w.title(titel)

    def takt(self):
        if self.beendet:
            return
        try:
            self._zeichnen()
            erg = self.eingabe.liefern()                  # Puffer: vorderste Eingabe an den naechsten aktiven 011 (nach dem echten Tastenabstand, U-11); bei Kanalwechsel verwerfen
            if erg is not None:
                log('SW', f'Puffer -> {erg}' + (f' (verworfen insgesamt: {self.eingabe.verworfen_zaehler})' if erg == 'verworfen' else ''))
            self._merker.merken()
            aktiv = self._fokus()
            self._titel_setzen(aktiv)
        except Exception:
            import traceback
            traceback.print_exc()
            log('FEHLER', 'SW-Takt: ' + traceback.format_exc())
        if not self.beendet:
            self.w.after(TAKT_MS, self.takt)

    def starten(self):
        self.w.after(TAKT_MS, self.takt)

    def _schliessen(self):
        if self.bei_schliessen:
            self.bei_schliessen()

    def beenden(self):
        self.beendet = True
        try:
            self._merker.beenden()
        except Exception:
            pass
        try:
            self.w.destroy()
        except Exception:
            pass
