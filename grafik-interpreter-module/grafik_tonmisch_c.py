# -*- coding: utf-8 -*-
"""
grafik_tonmisch_c.py - Mischer fuer GRAFIK ueber das C-Modul `tonmisch` (Stufe 4, GRAFIK_Beschreibung §6 (alt: Dok. 10) S4-01 bis S4-03, S4-12).
Version: G4-003.  Nur Standardbibliothek; braucht das Erweiterungsmodul c8205_trommel (mit den ton_*-Methoden, c-module/python).

CMischer hat dieselbe Schnittstelle wie grafik_tonmisch.Mischer (einzel, dauer_an, dauer_pegel, dauer_aus, tor, alles_aus, klingt,
klingt_schluessel, block, starten, schliessen, takt_haken, haken_fehler, bei_ausfall, ausfall, bloecke_gesendet), damit die
Aufrufer (Rechnerton, Schreibwerk, Leser, Stanzer, c8205_grafik) unveraendert bleiben.  Der Mischer-Thread laeuft in C und braucht die
GIL nicht: ein haengendes Tk oder Python verursacht keine Tonluecke.  Die Zeitgeber (takt_haken) und die Ausfallmeldung laufen in einem
kleinen Python-Thread, der ton_warte_takt() (ohne GIL) abwartet; der Mischer ruft nie in Python zurueck.

Ein Klang wird beim ersten Gebrauch (nach der Identitaet des array-Objekts) einmal ins C-Modul kopiert; die Arrays muessen deshalb
dieselben Objekte bleiben (Schreibwerk, Leser, Stanzer, Rechnerton halten ihre Klaenge dauerhaft).
Ist das Modul nicht ladbar oder ohne ton_*-Methoden (alter Build): neuer_mischer() faellt auf den Python-Mischer zurueck.
"""
import array
import os
import sys
import threading

import grafik_tonmisch as TM

VERSION_TONMISCH_C = 'G4-005'
KANAL_NR = {k: i for i, k in enumerate(TM.KANAELE)}      # rechner 0, schreibwerk 1, leser 2, stanzer 3 (wie TM_KANAL_* in tonmisch.h)
TM_FEHLER, TM_VOLL = -1, -2
_HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # Projektordner (die Module liegen in grafik-interpreter-module/)
MODULVERZ = os.path.join(_HIER, 'c-module', 'python')


def lade_ton_modul():
    """Das Erweiterungsmodul c8205_trommel mit ton_*-Methoden oder None (nicht gebaut, alter Build)."""
    if MODULVERZ not in sys.path:
        sys.path.insert(0, MODULVERZ)
    try:
        import c8205_trommel
    except ImportError:
        return None
    return c8205_trommel if hasattr(c8205_trommel, 'ton_neu') else None


class CListenSenke:
    """Senke im Speicher des C-Moduls (Pruefungen): .bloecke = Liste der Bloecke zu 882 Byte."""
    art, arg = 'speicher', None
    def __init__(self):
        self._m = None
    @property
    def bloecke(self):
        if self._m is None:
            return []
        b = self._m.C.ton_speicher(self._m.h)
        return [b[i:i + TM.BLOCK * 2] for i in range(0, len(b), TM.BLOCK * 2)]
    def schreibe(self, b):                                # nur der Vollstaendigkeit halber (die Bloecke erzeugt der Mischer selbst)
        raise NotImplementedError('CListenSenke wird vom C-Modul gefuellt')
    def schliessen(self):
        pass


class CProzessSenke:
    """Abspielprogramm mit Roh-Audio ueber eine Roehre; vom C-Modul gestartet.  Nicht startbar: SenkeAusfall beim Anlegen des Mischers."""
    art = 'prozess'
    def __init__(self, befehl):
        self.befehl = list(befehl)
        self.arg = self.befehl
    def schliessen(self):
        pass


class CDateiSenke:
    """Bloecke in eine Datei (Trockenlauf)."""
    art = 'datei'
    def __init__(self, pfad):
        self.arg = pfad
    def schliessen(self):
        pass


class CMischer:
    def __init__(self, senke=None, bei_ausfall=None, modul=None):
        self.C = modul or lade_ton_modul()
        if self.C is None:
            raise RuntimeError('C-Modul tonmisch nicht ladbar (c8205_trommel mit ton_*-Methoden bauen: make pyext)')
        self.h = self.C.ton_neu()
        self.senke = senke
        self.bei_ausfall = bei_ausfall
        self.takt_haken = []
        self.haken_fehler = []
        self.ausfall = None
        self.verworfen = 0                                 # Klaenge, die wegen voller Stimmenzahl (128) nicht angenommen wurden
        self._klaenge = {}                                 # id(array) -> (array, Klangnummer)
        self.C.ton_vorlauf(self.h, TM.VORLAUF_BLOECKE)      # G4-004: Vorlauf in Bloecken (Konstante in grafik_tonmisch)
        self._stop = threading.Event()
        self._thread = None
        if senke is not None:
            try:
                self.C.ton_senke(self.h, senke.art, senke.arg)
            except self.C.TonFehler as e:
                name = senke.arg[0] if senke.art == 'prozess' else senke.art
                raise TM.SenkeAusfall(f'{name} nicht startbar ({e})')
            if hasattr(senke, '_m') or isinstance(senke, CListenSenke):
                senke._m = self

    # --- Klaenge -----------------------------------------------------------------------------------------------
    def _klang(self, daten):
        e = self._klaenge.get(id(daten))
        if e is None or e[0] is not daten:
            a = daten if isinstance(daten, array.array) and daten.typecode == 'h' else array.array('h', daten)
            if sys.byteorder == 'big':
                a = array.array('h', a); a.byteswap()
            e = (daten, self.C.ton_klang(self.h, a.tobytes()))
            self._klaenge[id(daten)] = e
        return e[1]

    def _rc(self, rc):
        if rc == TM_VOLL:
            self.verworfen += 1
        elif rc == TM_FEHLER:
            raise ValueError('tonmisch: falscher Kanal oder Klang')

    # --- Ereignisse (wie grafik_tonmisch.Mischer) ----------------------------------------------------------------
    def einzel(self, kanal, daten, pegel=1.0, schluessel=None):
        self._rc(self.C.ton_einzel(self.h, KANAL_NR[kanal], self._klang(daten), float(pegel), schluessel))

    def dauer_an(self, kanal, schluessel, daten, pegel=1.0):
        self._rc(self.C.ton_dauer_an(self.h, KANAL_NR[kanal], schluessel, self._klang(daten), float(pegel)))

    def dauer_pegel(self, schluessel, pegel):
        self.C.ton_dauer_pegel(self.h, schluessel, float(pegel))

    def dauer_aus(self, schluessel):
        if schluessel:
            self.C.ton_dauer_aus(self.h, schluessel)

    def tor(self, kanal, offen):
        self.C.ton_tor(self.h, KANAL_NR[kanal], 1 if offen else 0)

    def alles_aus(self):
        self.C.ton_alles_aus(self.h)

    def klingt(self):
        return self.C.ton_klingt(self.h)

    def klingt_schluessel(self, schluessel):
        return self.C.ton_klingt_schluessel(self.h, schluessel)

    @property
    def bloecke_gesendet(self):
        return self.C.ton_bloecke(self.h)

    def block(self):
        """Ein Block zu 10 ms von Hand gemischt (Pruefungen), bytes, 882 Byte, little endian."""
        b = self.C.ton_block(self.h)
        if sys.byteorder == 'big':
            a = array.array('h'); a.frombytes(b); a.byteswap(); b = a.tobytes()
        return b

    # --- Strom ---------------------------------------------------------------------------------------------------
    def haken_aufrufen(self):
        for h in list(self.takt_haken):
            try:
                h()
            except Exception as e:                         # ein Fehler im Zeitgeber darf den Tonstrom nicht beenden
                self.haken_fehler.append(f'{e.__class__.__name__}: {e}')
                del self.haken_fehler[:-20]

    def starten(self):
        if self._thread is not None:
            return
        try:
            self.C.ton_starten(self.h)
        except self.C.TonFehler as e:
            raise TM.SenkeAusfall(f'Tonstrom nicht startbar ({e})')
        self._thread = threading.Thread(target=self._haken_lauf, name='tonmisch-haken', daemon=True)
        self._thread.start()

    def _haken_lauf(self):
        n = 0
        while not self._stop.is_set():
            n2 = self.C.ton_warte_takt(self.h, n, 50)       # ohne GIL; kehrt mit dem naechsten Block (alle 10 ms) zurueck
            if self._stop.is_set():
                return
            text = self.C.ton_ausfall(self.h)
            if text is not None:
                self.ausfall = text
                if self.bei_ausfall is not None:
                    self.bei_ausfall(text)
                return
            if n2 != n:
                n = n2
                self.haken_aufrufen()

    def schliessen(self):
        self._stop.set()
        self.C.ton_schliessen(self.h)                       # Thread in C beenden, Senke schliessen, weckt ton_warte_takt
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(1.0)


def neuer_mischer(spieler=None, bei_ausfall=None, c_bevorzugt=True):
    """Mischer mit Abspielprogramm `spieler` (Befehl als Liste).  Rueckgabe: (mischer, 'C' | 'Python').
    Das C-Modul wird bevorzugt; ist es nicht ladbar, kommt der Python-Mischer (Hinweis macht der Aufrufer).
    Wirft TM.SenkeAusfall, wenn das Abspielprogramm nicht startbar ist."""
    if c_bevorzugt and lade_ton_modul() is not None:
        return CMischer(CProzessSenke(spieler), bei_ausfall=bei_ausfall), 'C'
    return TM.Mischer(TM.ProzessSenke(spieler), bei_ausfall=bei_ausfall), 'Python'
