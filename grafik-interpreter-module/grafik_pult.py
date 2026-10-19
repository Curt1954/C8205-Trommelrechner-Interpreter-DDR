# -*- coding: utf-8 -*-
"""
grafik_pult.py - Pult-Steuerung des Modus GRAFIK (Stufe 2). Reine Standardbibliothek, KEIN Tkinter (dadurch testbar).
Version: G2-001

Aufgaben (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitte 1.3, 1.7, 1.8, 3.5); GRAFIK_Beschreibung §4 (alt: Dok. 06)):
  * Netzablauf: AUS (Start) -> HOCHLAUF (B rot, 11,3 s) -> BETRIEB (B gruen) -> AUSLAUF (B dunkel, ~2 s) -> ENDE.
    Im Zustand AUS, HOCHLAUF und AUSLAUF nimmt nur der Netzschalter Klicks an.
  * Tasten: Klick-Tasten (0,4 s hell), Wippen H-R und T-SW (rasten ein), Selektoren SP, BS, LS, SW (einrastend),
    Kanaltasten K0 bis K3 (Klick-Tasten), Halter fuer E und M (Umschalt+Klick), Rollensperre bei R.
  * Weitergabe an den Rechner (c8205_grafik.Rechner.taste) bzw. an die K0-Warteschlange (Eingabetasten, Quelle 'T').
  * Zustand fuer die Anzeige: lampen() und zeichenliste() (Tk-Schicht in grafik_pult_fenster.py).
Zeit wird immer als Parameter 'jetzt' (Sekunden, monotone Uhr) uebergeben.

Standardannahmen dieser Stufe (zur Abnahme, nicht ausdruecklich bestaetigt) stehen in GRAFIK_Beschreibung §10.3.
"""
import json
import os
import struct
import threading

from grafik_debuglog import log

VERSION_PULT = 'G2-010'

HOCHLAUF_S = 11.3       # Laenge von fade_in (GRAFIK_Beschreibung §3.6 (alt: Dok. 01 Abschnitt 1.8 Nr. 4)); Ton folgt in Stufe 4
AUSLAUF_S = 2.0         # Laenge von fade_out (rund 2 s)
TASTENZEIT_S = 0.25     # Dauer "gedrueckt" der Klick-Tasten (einstellbar; Projektinhaber 17.10.2026: 0,25 s statt 0,4 s)
LAMPENTAKT_S = 0.04     # Lampen hoechstens alle 40 ms (GRAFIK_Beschreibung §3.5 (alt: Dok. 01 Abschnitt 1.5))
# Ruhiges Bild (GRAFIK_Beschreibung §3.5 (alt: Dok. 01 Abschnitt 6.2), Entwurf 84; Standardannahme, bei der Handabnahme einzustellen):
MITTEL_FENSTER_S = 0.04  # Beurteilungsfenster je Lampe
MITTEL_AN = 0.60         # ab diesem Anteil "an" im Fenster leuchtet die Lampe
MITTEL_AUS = 0.40        # bis zu diesem Anteil ist sie dunkel; dazwischen bleibt der bisherige Zustand (Hysterese)
ABTAST_S = 0.002         # Abtastabstand des Abtast-Threads im Dauerlauf

AUS, HOCHLAUF, BETRIEB, AUSLAUF, ENDE = 'aus', 'hochlauf', 'betrieb', 'auslauf', 'ende'

# Manifestname -> Token der K0-Eingabe (Eingabetasten)
EINGABE_TOKEN = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
                 'B': 'B', 'D': 'D', 'PLUS': '+', 'MINUS': '-', 'KOMMA': ',', 'PUNKT': '.', 'DOPPELPUNKT': ':',
                 'ZR': 'ZR', 'WM': 'WM', 'IS': 'IS', 'IB': 'IB'}
KANAL = ('K0', 'K1', 'K2', 'K3')
SELEKTOREN = ('SP', 'BS', 'LS', 'SW_umschalt')          # einrastend, je fuer sich
# Bei Stellung R mechanisch gesperrt: E, M, G, Ue und T-SW. Die Eingabetasten sind NICHT in dieser Menge: Das Programm laeuft in Stellung R
# und wartet dort im Eingabe-Halt auf sie; ihre Verriegelung ist die elektronische (nur bei Eingabe-Halt, K0 und Stellung T), siehe klick().
# (Auslegung; GRAFIK_Beschreibung §3.3 (alt: Dok. 01 3.5) nennt sie bei der Rollensperre mit, das widerspricht dem Ablauf 1.8 Nr. 12 bis 14.)
ROLLENGESPERRT = {'E', 'M', 'G', 'UE', 'T', 'SW'}

# Computertastatur (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitt 1.7)): Zeichen -> Manifestname
TASTATUR = {**{c: c for c in '0123456789'}, '+': 'PLUS', '-': 'MINUS', ',': 'KOMMA', '.': 'PUNKT', ':': 'DOPPELPUNKT',
            'b': 'B', 'd': 'D', ' ': 'ZR'}

FLAG_LAMPEN = ('E', 'A', 'T', 'SW', 'K1', 'K2', 'K3', 'FE', 'FUE', 'BS', 'US', 'H')


def png_groesse(pfad):
    with open(pfad, 'rb') as f:
        kopf = f.read(24)
    if kopf[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('kein PNG: ' + pfad)
    return struct.unpack('>II', kopf[16:24])


class Mittelung:
    """Mittelung der Lampenzustaende ueber ein Zeitfenster mit Schalthysterese (ruhiges Bild im Dauerlauf)."""

    def __init__(self, fenster=MITTEL_FENSTER_S, an=MITTEL_AN, aus=MITTEL_AUS):
        self.fenster, self.an, self.aus = fenster, an, aus
        self.zaehler, self.n, self.t0 = {}, 0, None
        self.zustand = {}
        self._lock = threading.Lock()

    def probe(self, werte, jetzt):
        with self._lock:
            if self.t0 is None:
                self.t0 = jetzt
            self.n += 1
            for k, v in werte.items():
                self.zaehler[k] = self.zaehler.get(k, 0) + (1 if v else 0)
            if jetzt - self.t0 >= self.fenster and self.n:
                for k, c in self.zaehler.items():
                    f = c / self.n
                    if f >= self.an:
                        self.zustand[k] = 1
                    elif f <= self.aus:
                        self.zustand[k] = 0
                    else:
                        self.zustand.setdefault(k, 0)
                self.zaehler, self.n, self.t0 = {}, 0, jetzt

    def sofort(self, werte):
        """Genauer Stand (bei Halt und nach E-Schritt): ersetzt den gemittelten Zustand."""
        with self._lock:
            self.zustand = {k: 1 if v else 0 for k, v in werte.items()}
            self.zaehler, self.n, self.t0 = {}, 0, None

    def kopie(self):
        with self._lock:
            return dict(self.zustand)


class PultSteuerung:
    def __init__(self, ordner, rechner=None, hochlauf_s=HOCHLAUF_S, auslauf_s=AUSLAUF_S, tastenzeit_s=TASTENZEIT_S,
                 bei_betrieb=None, bei_ende=None, ton=None, bei_ls=None):
        """ordner: Ordner 'pult' (Manifest, bild/, grafiken/). rechner: c8205_grafik.Rechner (oder None fuer reine Anzeige).
        bei_betrieb(): wird einmal aufgerufen, wenn B gruen wird (hier startet der Rechner-Thread).
        bei_ende(): wird beim Auslauf aufgerufen (Abbruch des Rechners), noch bevor ENDE erreicht ist."""
        self.ordner = ordner
        with open(os.path.join(ordner, 'pult_manifest.json'), encoding='utf-8') as f:
            self.m = json.load(f)
        self.r = rechner
        self.ton = ton
        self.bei_ls = bei_ls            # Stufe 4 (S4-10): Funktion(bool) beim Einrasten/Loesen des Selektors LS (Stanzerton); sonst None
        self.hochlauf_s, self.auslauf_s, self.tastenzeit_s = hochlauf_s, auslauf_s, tastenzeit_s
        self.bei_betrieb, self.bei_ende = bei_betrieb, bei_ende
        self.netz = AUS
        self._frist = None
        self._lock = threading.RLock()
        # Tastenzustand
        self.blink = {}                 # Taste -> Ende der Hellphase (Klick-Tasten)
        self.rastet = {'H', 'T', 'K0'}  # eingerastete Tasten. Start: H, T und K0 (Projektinhaber 17.10.2026: immer genau eine der Kanaltasten rastet; K0 beim Start)
        self.halter = set()             # E und M per Umschalt+Klick gehalten
        self.maus_gehalten = {}         # Taste -> True solange die Maustaste gedrueckt ist (E, M)
        self._gr = {}
        self.mit = Mittelung()
        self._abtast = None
        self.protokoll = []             # Wirkungen (Taste -> Rechner), fuer Tests und Fehlersuche
        self.klick_log = None           # Funktion(str) oder None: jeder Klick mit Ergebnis und Grund (Schalter --pult-protokoll)
        self.aufzeichnung = None        # grafik_debuglog.Aufzeichnung oder None: Klickspur (Schalter --AUFZEICHNUNG / --DEBUGLOG)

    # ------------------------------------------------------------------ Zustand
    def _r_stellung(self):
        """True bei Stellung R (Rollensperre): Schalter H-R steht auf R."""
        return 'R' in self.rastet

    def bedienbar(self):
        return self.netz == BETRIEB

    # ------------------------------------------------------------------ Netz
    def netz_klick(self, jetzt):
        with self._lock:
            if self.netz == AUS:
                self.netz = HOCHLAUF
                self._frist = jetzt + self.hochlauf_s
                if self.ton:
                    self.ton.fade_in()
                return True
            if self.netz in (HOCHLAUF, BETRIEB):          # Ausschalten, auch im Hochlauf (Nr. 5)
                self._auslauf_beginnen(jetzt)
                return True
            return False

    def _auslauf_beginnen(self, jetzt):
        self.netz = AUSLAUF
        self._frist = jetzt + self.auslauf_s
        self.blink.clear()
        self.maus_gehalten.clear()
        if self.ton:
            self.ton.fade_out()                              # beginnt mit dem Klick; fade_in bricht dabei ab
        if self.bei_ende:
            self.bei_ende()

    def fenster_schliessen(self, jetzt):
        """X am Pult-Fenster: wie Strg+C (GRAFIK_Beschreibung §3.1 (alt: Dok. 01 Abschnitt 1.6)) - sofortiges Ende ohne Auslauf."""
        with self._lock:
            self.netz = ENDE
            if self.ton:
                self.ton.alles_aus()
            if self.bei_ende:
                self.bei_ende()

    def tick(self, jetzt):
        """Zeitgesteuerte Uebergaenge. Liefert ENDE, sobald das Programm enden soll, sonst None."""
        with self._lock:
            for t in [t for t, bis in self.blink.items() if jetzt >= bis]:
                del self.blink[t]
            if self.netz == HOCHLAUF and jetzt >= self._frist:
                self.netz = BETRIEB
                if self.ton:
                    self.ton.grund_an()
                self.starte_abtastung()
                if self.bei_betrieb:
                    self.bei_betrieb()
            elif self.netz == AUSLAUF and jetzt >= self._frist and not (self.ton and self.ton.fade_laeuft() and jetzt < self._frist + 3.0):
                # Ende erst, wenn fade_out zu Ende gespielt ist (hoechstens 3 s ueber die Frist hinaus, falls der Spieler haengt)
                self.netz = ENDE
                if self.ton:
                    self.ton.alles_aus()
            return ENDE if self.netz == ENDE else None

    # ------------------------------------------------------------------ Tasten
    def _an_rechner(self, token):
        self.protokoll.append(token)
        log('TOKEN', f'an den Rechner: {token}')
        if self.r is None:
            return
        if hasattr(self.r, 'pult_taste'):               # echter Rechner: vorgemerkt, Ausfuehrung im Rechner-Thread (nie im Fenster-Thread)
            self.r.pult_taste(token)
            return
        if token not in ('M-', 'E-', 'SW=0', 'SW=1', 'SP+', 'SP-', 'BS+', 'BS-') and not self.r.mhalt and token != 'M+':
            self.r.neue_folge()
        self.r.taste(token)

    def _blinken(self, taste, jetzt):
        self.blink[taste] = jetzt + self.tastenzeit_s

    def klick(self, taste, jetzt, umschalt=False):
        ok = None
        try:
            ok = self._klick(taste, jetzt, umschalt)
        finally:
            if self.aufzeichnung is not None:           # auch Klicks ohne Wirkung; bei einer Ausnahme mit wirkt=?
                try:
                    self.aufzeichnung.klick(taste, jetzt, umschalt, ok)
                except Exception:
                    pass
        if self.klick_log:
            self.klick_log(self._klick_zeile(taste, ok, umschalt))
        return ok

    def _klick_zeile(self, taste, ok, umschalt):
        st = 'R' if 'R' in self.rastet else ('H' if 'H' in self.rastet else '?')
        erw = self.r.m.k0.erwartet('T') if self.r is not None else None
        return (f'Pult-Klick {taste}{"+Umschalt" if umschalt else ""}: {"WIRKT" if ok else "ohne Wirkung"} | netz={self.netz} '
                f'stellung={st} eingabe_erwartet={erw} halter={sorted(self.halter)}')

    def eingabe_erwartet(self):
        return bool(self.netz == BETRIEB and self.r is not None and self.r.m.k0.erwartet('T'))

    def _klick(self, taste, jetzt, umschalt=False):
        """Maustaste GEDRUECKT auf einer Taste (alle Tasten loesen beim Druecken aus). Liefert True, wenn die Taste wirkte."""
        with self._lock:
            if taste == 'NETZ':
                return self.netz_klick(jetzt)
            if not self.bedienbar():
                return False
            # --- Wippe H-R
            if taste == 'H':
                if 'H' in self.rastet:
                    return False
                self.rastet.discard('R')
                self.rastet.add('H')
                self._an_rechner('H')
                return True
            if taste == 'R':
                if 'R' in self.rastet or self.halter:         # E/M gehalten: R wirkungslos (Entwurf 78)
                    return False
                self.rastet.discard('H')
                self.rastet.add('R')
                self._an_rechner('R')
                return True
            # --- Rollensperre
            if self._r_stellung() and (taste in ROLLENGESPERRT):
                return False
            # --- Wippe T-SW
            if taste in ('T', 'SW'):
                if taste in self.rastet:
                    return False
                self.rastet.discard('SW' if taste == 'T' else 'T')
                self.rastet.add(taste)
                self._an_rechner('SW=0' if taste == 'T' else 'SW=1')
                return True
            # --- Selektoren (einrastend)
            if taste in SELEKTOREN:
                if taste in self.rastet:
                    self.rastet.discard(taste)
                    ein = False
                else:
                    self.rastet.add(taste)
                    ein = True
                if taste == 'SW_umschalt':
                    if self.r is not None:
                        self.r.sw.unterdruecken = ein
                    self.protokoll.append('SW_umschalt+' if ein else 'SW_umschalt-')
                elif taste in ('SP', 'BS'):
                    self._an_rechner(taste + ('+' if ein else '-'))
                else:                                          # LS: nur Ton (Stufe 4), keine Wirkung auf den Rechner
                    self.protokoll.append('LS+' if ein else 'LS-')
                    if self.bei_ls is not None:
                        self.bei_ls(ein)
                return True
            # --- Kanaltasten: Klick-Tasten
            if taste in KANAL:                                  # Radio-Verhalten: genau eine rastet (Aenderung 17.10.2026 gegen Entwurf 77)
                self.rastet -= set(KANAL)
                self.rastet.add(taste)
                self._an_rechner(taste)
                return True
            # --- E und M: Halter. Niederdruecken und Loslassen sind getrennte Ereignisse (E+ / E-, M+ / M-): E+ fuehrt Phase IV und I aus,
            #     E- Phase II und III (Handbuch, Taste E); bei gehaltener Taste (Umschalt+Klick) liegt dazwischen beliebig viel Zeit.
            if taste in ('E', 'M'):
                if umschalt:
                    if taste in self.halter:
                        self.halter.discard(taste)
                        self._an_rechner(taste + '-')
                    else:
                        self.halter.add(taste)
                        self._an_rechner(taste + '+')
                    return True
                if taste in self.halter:                       # normaler Klick auf gehaltene Taste: nichts
                    return False
                self._blinken(taste, jetzt)
                self.maus_gehalten[taste] = True
                self._an_rechner(taste + '+')
                return True
            # --- Eingabetasten: nur, wenn der Rechner jetzt ein Zeichen von T erwartet
            if taste in EINGABE_TOKEN:
                if self.r is None or not self.r.m.k0.erwartet('T'):
                    return False
                if not self.r.m.k0.annehmen('T', EINGABE_TOKEN[taste]):
                    return False
                self.protokoll.append('K0:' + EINGABE_TOKEN[taste])
                self._blinken(taste, jetzt)
                return True
            # --- uebrige Klick-Tasten: G, UE, ST
            if taste in ('G', 'UE', 'ST'):
                self._blinken(taste, jetzt)
                self._an_rechner(taste)
                return True
            return False

    def loslassen(self, taste, jetzt):
        """Maustaste LOSGELASSEN (egal wo der Zeiger steht). Nur fuer E und M von Bedeutung."""
        with self._lock:
            if self.maus_gehalten.pop(taste, None):
                if self.aufzeichnung is not None:
                    try:
                        self.aufzeichnung.loslassen(taste, jetzt)
                    except Exception:
                        pass
                if taste in ('E', 'M') and taste not in self.halter:
                    self._an_rechner(taste + '-')               # Loslassen: bei E beginnen jetzt Phase II und III
                if taste == 'M':
                    self._blinken('M', jetzt)
                return True
            return False

    def fokus_verloren(self, jetzt):
        """Bei Fokusverlust wird eine mit der Maus gehaltene Taste losgelassen; Einrastungen und Halter bleiben."""
        for t in list(self.maus_gehalten):
            self.loslassen(t, jetzt)

    def tastatur(self, zeichen, jetzt):
        """Computertastatur: nur Eingabetasten (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitt 1.7))."""
        name = TASTATUR.get(zeichen.lower() if zeichen.isalpha() else zeichen)
        return self.klick(name, jetzt) if name else False

    # ------------------------------------------------------------------ Anzeige
    def _werte(self):
        """Alle Lampenwerte des Rechners als flaches Dict (Schluessel 'f:E', 'a:bit', 'o:bit', 'v:V1')."""
        m = self.r.m
        w = {f'f:{n}': m.fl.get(n, 0) for n in FLAG_LAMPEN}
        w.update({f'v:{n}': m.fl.get(n, 0) for n in ('V1', 'V2')})
        adr, or_ = m.adr, m.OR
        w.update({f'a:{b}': (adr >> b) & 1 for b in range(12)})
        w.update({f'o:{b}': (or_ >> b) & 1 for b in range(9)})
        return w

    def starte_abtastung(self):
        """Abtast-Thread: im Dauerlauf alle ABTAST_S die Lampenwerte in die Mittelung; sonst genauer Stand."""
        if self._abtast is not None or self.r is None:
            return
        import time

        def lauf():
            while self.netz in (BETRIEB, HOCHLAUF):
                try:
                    if self.netz == BETRIEB:
                        if getattr(self.r, 'laeuft', False):
                            self.mit.probe(self._werte(), time.monotonic())
                        else:
                            self.mit.sofort(self._werte())
                except Exception:
                    pass
                time.sleep(ABTAST_S)
        self._abtast = threading.Thread(target=lauf, name='lampenabtastung', daemon=True)
        self._abtast.start()

    def lampen(self):
        """Dict Lampenname -> 'hell'/'dunkel'/'rot'/'gruen' fuer die 15 grossen Lampen, dazu ('ar', bit), ('or', bit), V1, V2."""
        gross = {}
        betrieb = self.netz == BETRIEB
        fl = self.r.m.fl if (self.r is not None and betrieb) else {}      # Lampe BS = Flag BS (bedingter Stopp wirksam); der Schalter steht in m.bs_schalter
        mit = None
        if betrieb and self.r is not None and getattr(self.r, 'laeuft', False):
            mit = self.mit.kopie() or None            # Dauerlauf: gemittelter Zustand; Halt: genauer Stand
        if mit is not None:
            fl = {n: mit.get(f'f:{n}', fl.get(n, 0)) for n in list(FLAG_LAMPEN) + ['V1', 'V2']}
            fl['V1'], fl['V2'] = mit.get('v:V1', 0), mit.get('v:V2', 0)
        for n in FLAG_LAMPEN:
            gross[n] = 'hell' if fl.get(n) else 'dunkel'
        gross['R'] = 'hell' if (betrieb and 'H' in fl and not fl['H']) else 'dunkel'
        gross['B'] = {HOCHLAUF: 'rot', BETRIEB: 'gruen'}.get(self.netz, 'dunkel')
        gross['N'] = 'gruen'
        adr = (self.r.m.adr & 0o7777) if (self.r is not None and betrieb) else 0
        or_ = (self.r.m.OR & 0o777) if (self.r is not None and betrieb) else 0
        if mit is not None:
            adr = sum(mit.get(f'a:{b}', 0) << b for b in range(12))
            or_ = sum(mit.get(f'o:{b}', 0) << b for b in range(9))
        v = {n: bool(fl.get(n)) for n in ('V1', 'V2')}
        return gross, adr, or_, v

    def taste_gedrueckt(self, name, jetzt=None):
        if name in self.blink:
            return True
        return name in self.rastet or name in self.halter or name in self.maus_gehalten

    def _sprite(self, name):
        if name not in self._gr:
            self._gr[name] = png_groesse(os.path.join(self.ordner, 'grafiken', name))
        return self._gr[name]

    def zeichenliste(self):
        """Liste von Dicts {id, bild, x, y, sichtbar}; (x, y) ist die linke obere Ecke im 860-px-Bild (wie pult_modell.py)."""
        gross, adr, or_, v = self.lampen()
        out = []
        for name, p in self.m['lampen_gross'].items():
            b = f'lampe_{gross[name]}.png'
            w, h = self._sprite(b)
            out.append(dict(id=f'lampe:{name}', bild=b, x=p['cx'] - w // 2, y=p['cy'] - h // 2, sichtbar=True))
        for e in self.m['lampen_ar']:
            b = 'diode_hell.png' if (adr >> e['bit']) & 1 else 'diode_dunkel.png'
            w, h = self._sprite(b)
            out.append(dict(id=f"ar:{e['bit']}", bild=b, x=e['cx'] - w // 2, y=e['cy'] - h // 2, sichtbar=True))
        for e in self.m['lampen_or']:
            b = 'diode_hell.png' if (or_ >> e['bit']) & 1 else 'diode_dunkel.png'
            w, h = self._sprite(b)
            out.append(dict(id=f"or:{e['bit']}", bild=b, x=e['cx'] - w // 2, y=e['cy'] - h // 2, sichtbar=True))
        for name, p in self.m['lampen_v'].items():
            b = 'diode_hell.png' if v.get(name) else 'diode_dunkel.png'
            w, h = self._sprite(b)
            out.append(dict(id=f'v:{name}', bild=b, x=p['cx'] - w // 2, y=p['cy'] - h // 2, sichtbar=True))
        s = self.m['schluessel']
        b = 'schluessel_ein.png' if self.netz in (HOCHLAUF, BETRIEB) else 'schluessel_aus.png'
        w, h = self._sprite(b)
        out.append(dict(id='schluessel', bild=b, x=s['cx'] - w // 2, y=s['cy'] - h // 2, sichtbar=True))
        for i, t in self.m['tasten'].items():
            if self.taste_gedrueckt(i):
                out.append(dict(id=f'taste:{i}', bild=t['hell'], x=t['x_hell'], y=t['y_hell'], sichtbar=True))
            else:   # losgelassen zeigt schon das Foto
                out.append(dict(id=f'taste:{i}', bild=t['dunkel'], x=t['x'], y=t['y'], sichtbar=False))
        return out

    def treffer(self, x, y):
        """Name der Bedienstelle an (x, y) im Bild oder None. Der Netzschalter ist der Schluesselschalter (Kreis)."""
        s = self.m['schluessel']
        if (x - s['cx']) ** 2 + (y - s['cy']) ** 2 <= s['r'] ** 2:
            return 'NETZ'
        for i, t in self.m['tasten'].items():
            if t['x'] <= x < t['x'] + t['w'] and t['y'] <= y < t['y'] + t['h']:
                return i
        return None
