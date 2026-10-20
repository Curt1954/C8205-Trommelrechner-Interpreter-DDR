#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C8205-Hilfsprogramm: Lochstreifen erzeugen (Gegenstueck zu c8205_lochstreifen_anzeige.py).

Oeffnet ein Eingabefenster (gleichartig wie das Fenster der Anzeige: Tkinter, 130 x 36 Zeichen, Bildlaufleiste,
Standardposition rechts unten, bleibt offen, bis es mit X geschlossen wird). Jedes eingegebene Zeichen des
R300-Kodes (Kodetabelle 1) wird sofort als Lochungszeile in den virtuellen Lochstreifen geschrieben: eine Zeile je
Zeichen, 8 Zeichen 0/1 in der Spurfolge  w v u p 8 4 2 1  (Format wie die Stanzer-Ausgabe des Interpreters
c8205_interp.py und wie der Eingang --leser1/--leser2). Andere Zeichen werden abgewiesen (Signalton, Hinweis in der
Titelleiste), nichts wird gestanzt.

Aufruf:  python3 c8205_lochstreifen_eingabe.py --LS-STANZER PFAD [--text]
         --LS-STANZER PFAD  Lochstreifen, der erzeugt wird. Datei, oder Verzeichnis (bzw. Pfad mit / am Ende): dann
                            VERZ/stanzer-ausgabe.txt (wie --stanzer1 des Interpreters). Eine vorhandene Datei wird
                            ueberschrieben; fehlende Ordner werden angelegt.
         --text             Zeichen von der Standardeingabe lesen statt im Fenster (auch Rueckfall, wenn kein Fenster
                            moeglich ist); Ende mit Strg+D (Windows: Strg+Z, Enter)
         --debug            Diagnose: Tasten, Mausereignisse und Kopiervorgaenge auf der Fehlerausgabe (Terminal)

Bedienung:
  * Zeichen des Lochstreifenkodes: Ziffern, Kleinbuchstaben und Zeichen der Klbuch-Lage, Grossbuchstaben und
    Zeichen der Gbuch-Lage (< " [ > ' ~ ] # * ( = ; ) ? ! und die Glyphen ≈ ≋ △), dazu
    Leertaste = Leertaste/ZR, Tab = Tabulator, Enter = SatzMarke/WRZL.
  * Zeichenlage: Der Stanzer-Kode kennt die Lage nicht; sie wird durch die Zeichen Um. KB / Um. GB umgeschaltet. Das
    Programm stanzt Um. KB bzw. Um. GB selbst, wenn ein Zeichen die andere Lage braucht (Anfang: KB, wie beim
    Rechner nach dem Einschalten), zeigt sie aber nicht an. Von Hand: F1 = Um. KB, F2 = Um. GB.
  * Korrektur wie beim Lochstreifen ohne Rechner: Eine Lochung laesst sich nicht zuruecknehmen. Rueck-Taste stanzt
    "Irrung Zeichen" (alle 8 Spuren), Entf stanzt "Irrung Satz"; im Fenster loescht Irrung Zeichen das letzte Zeichen der
    Zeile, Irrung Satz die ganze Zeile (Zeilenumbrueche bleiben); beide erscheinen nicht als Marke.
  * Der Text im Fenster ist nicht editierbar (Nachlesen sowie Markieren mit der Maus und Kopieren mit Strg+C,
    Strg+Einfg oder rechter Maustaste sind moeglich); Einfuegen
    (Strg+V, Umschalt+Einfg) stanzt die Zeichen der Zwischenablage.
"""
import argparse
import os
import sys

VERSION = '1.9'   # 1.9: Um. KB/Um. GB werden nicht angezeigt (wirken nur), Irrung Zeichen/Satz loeschen im Fenster; 1.8: unter X11 zuerst xsel, dann xclip; 1.7: Option --zwischenablage auto|tk|system; 1.6: xclip wieder mit -t UTF8_STRING (VM-Abgleich uebernimmt sonst nichts); 1.5: gleicher Text wird innerhalb 5 s nicht erneut kopiert; 1.4: Systemprogramm zuerst, Tk nur als Rueckfall, xclip wie im Terminal aufgerufen; 1.3: xclip mit -t UTF8_STRING, Gegenprobe bei --debug; 1.2: Zwischenablage waehlt das Verfahren bei jedem Kopieren (Win32 / Tk + wl-copy, xclip, xsel, pbcopy, clip.exe); 1.1: Zwischenablage auch unter Windows (Win32-API), AltGr-Korrektur; 1.0: Linux

# Kodetabelle 1: Ausgabe-Adresse (oktal, 3 Stellen = die 8 Lochspuren w v u p 8 4 2 1) ->
# (Klbuch, Gbuch, Ascii GB, Ascii KB); entspricht TABELLE1 in c8205_interp.py (ohne Eingabe-Adresse)
TABELLE = {
    '001': ('1', '<', 60, 49), '002': ('2', '"', 34, 50), '023': ('3', '≈', 0, 51), '004': ('4', '[', 91, 52),
    '025': ('5', '>', 62, 53), '026': ('6', "'", 39, 54), '007': ('7', '≋', 0, 55), '010': ('8', '~', 126, 56),
    '031': ('9', ']', 93, 57), '020': ('0', '#', 35, 48), '174': ('%', '*', 42, 37),
    '155': ('Tabulator', 'Tabulator', 9, 9),
    '130': ('q', 'Q', 81, 113), '166': ('w', 'W', 87, 119), '045': ('e', 'E', 69, 101), '111': ('r', 'R', 82, 114),
    '163': ('t', 'T', 84, 116), '171': ('z', 'Z', 90, 122), '144': ('u', 'U', 85, 117), '051': ('i', 'I', 73, 105),
    '106': ('o', 'O', 79, 111), '127': ('p', 'P', 80, 112), '015': (':', '(', 40, 58), '040': ('+', '=', 61, 43),
    '117': ('Um. KB', 'Um. KB', 0, 0), '057': ('Um. GB', 'Um. GB', 0, 0),
    '061': ('a', 'A', 65, 97), '142': ('s', 'S', 83, 115), '064': ('d', 'D', 68, 100), '046': ('f', 'F', 70, 102),
    '067': ('g', 'G', 71, 103), '070': ('h', 'H', 72, 104), '121': ('j', 'J', 74, 106), '122': ('k', 'K', 75, 107),
    '103': ('l', 'L', 76, 108), '160': ('`', ';', 59, 96), '141': ('/', ')', 41, 47),
    '272': ('SatzMarke', 'WRZL', 10, 10),
    '150': ('y', 'Y', 89, 121), '147': ('x', 'X', 88, 120), '043': ('c', 'C', 67, 99), '165': ('v', 'V', 86, 118),
    '062': ('b', 'B', 66, 98), '105': ('n', 'N', 78, 110), '124': ('m', 'M', 77, 109), '153': (',', '?', 63, 44),
    '073': ('.', '!', 33, 46), '100': ('-', '△', 465, 45), '032': ('Leertaste', 'ZR', 32, 32),
    '377': ('Irrung Zeichen', 'Irrung Zeichen', 0, 0), '016': ('Irrung Satz', 'Irrung Satz', 0, 0),
    '177': ('Transport (Relikt)', 'Transport (Relikt)', 0, 0),
}

UM_KB, UM_GB, IRRUNG_ZEICHEN, IRRUNG_SATZ = 0o117, 0o057, 0o377, 0o016
SONDER = {0o117, 0o057, 0o377, 0o016, 0o177}   # keine Zeichen, die man tippt (Um., Irrung, Transport)

NORMAL, MARKE = 'normal', 'marke'
LOESCHE_ZEICHEN, LOESCHE_SATZ = 'loesche_zeichen', 'loesche_satz'   # Anweisungen an das Fenster, kein Text
FARBEN = {MARKE: '#2E6DA4'}

ZWISCHENABLAGE = 'auto'   # --zwischenablage: auto (Systemprogramm, dann Tk), tk (nur Tk), system (nur Systemprogramm/Win32)
DEBUG = False     # --debug: Ereignisse und Kopiervorgaenge auf der Fehlerausgabe melden


def dbg(*a):
    if DEBUG:
        print('[debug]', *a, file=sys.stderr, flush=True)


def _zeichentabelle():
    """Tippbares Zeichen -> (Lochungswert, noetige Lage 'KB'/'GB' oder None, wenn in beiden Lagen gleich)."""
    z = {}
    for okt, (kl, gb, a_gb, a_kb) in TABELLE.items():
        wert = int(okt, 8)
        if wert in SONDER:
            continue
        if a_kb == a_gb and a_kb in (9, 10, 32):           # Tabulator, SatzMarke/WRZL, Leertaste/ZR
            z[chr(a_kb)] = (wert, None)
            continue
        if 33 <= a_kb <= 255:
            z[chr(a_kb)] = (wert, 'KB')
        if 33 <= a_gb <= 255:
            z[chr(a_gb)] = (wert, 'GB')
        elif len(gb) == 1:                                  # Glyphen ohne Ascii-Wert: ≈ ≋ △
            z[gb] = (wert, 'GB')
    return z


ZEICHEN = _zeichentabelle()


def paritaet_ungerade(wert):
    return bin(wert).count('1') % 2 == 1


class Stanzer:
    """Virtueller Stanzer: schreibt jede Lochungszeile sofort in die Lochstreifendatei."""

    def __init__(self, pfad):
        if os.path.isdir(pfad) or pfad.endswith(('/', '\\')):
            self.pfad = os.path.join(pfad, 'stanzer-ausgabe.txt')
        else:
            self.pfad = pfad
        os.makedirs(os.path.dirname(os.path.abspath(self.pfad)), exist_ok=True)
        self.fh = open(self.pfad, 'w', encoding='utf-8')   # wie Stanzer im Interpreter: neu anlegen
        self.lage = 'KB'

    def schliessen(self):
        if self.fh:
            self.fh.close()
            self.fh = None

    def _stanze(self, wert):
        self.fh.write(format(wert, '08b') + '\n')
        self.fh.flush()

    def _um(self, lage):
        self._stanze(UM_KB if lage == 'KB' else UM_GB)
        self.lage = lage
        return []                      # wirkt nur, keine Anzeige

    def tippe(self, ch):
        """Zeichen stanzen. Rueckgabe: Liste von (Text, Tag) fuer die Anzeige, None wenn ch nicht im R300-Kode ist."""
        if ch not in ZEICHEN:
            return None
        wert, lage = ZEICHEN[ch]
        teile = []
        if lage is not None and lage != self.lage:
            self._um(lage)
        self._stanze(wert)
        teile.append((ch, NORMAL))
        return teile

    def um_taste(self, lage):
        return self._um(lage)

    def irrung_zeichen(self):
        self._stanze(IRRUNG_ZEICHEN)
        return [('', LOESCHE_ZEICHEN)]

    def irrung_satz(self):
        self._stanze(IRRUNG_SATZ)
        return [('', LOESCHE_SATZ)]


def verarbeite_taste(st, keysym, char, control):
    """Tastendruck auswerten (ohne Tk, daher einzeln testbar).
    Rueckgabe (verbraucht, teile, abgelehnt): verbraucht = Ereignis nicht an Tk weitergeben; teile = Anzeigeteile
    oder None; abgelehnt = nicht stanzbares Zeichen oder None; 'einfuegen' bei Strg+V / Umschalt+Einfg."""
    if control:
        if keysym.lower() == 'v':
            return True, None, 'einfuegen'
        return keysym.lower() not in ('c', 'a', 'insert'), None, None
    if keysym in ('Return', 'KP_Enter'):
        return True, st.tippe('\n'), None
    if keysym in ('Tab', 'ISO_Left_Tab'):
        return True, st.tippe('\t'), None
    if keysym == 'BackSpace':
        return True, st.irrung_zeichen(), None
    if keysym == 'Delete':
        return True, st.irrung_satz(), None
    if keysym == 'F1':
        return True, st.um_taste('KB'), None
    if keysym == 'F2':
        return True, st.um_taste('GB'), None
    if keysym == 'Insert':
        return True, None, 'einfuegen'
    if keysym in ('Up', 'Down', 'Left', 'Right', 'Prior', 'Next', 'Home', 'End') or not char:
        return False, None, None            # Bildlauf/Cursor und reine Umschalttasten: nichts stanzen
    if len(char) == 1 and ord(char) >= 32:
        teile = st.tippe(char)
        return True, teile, (None if teile else char)
    return True, None, None


def fenster_unmoeglich():
    """Grund, warum kein Fenster geoeffnet werden kann, sonst None (wie in c8205_lochstreifen_anzeige.py)."""
    if sys.platform.startswith('linux') and not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        return 'keine grafische Oberfläche (DISPLAY nicht gesetzt)'
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return 'tkinter fehlt (Linux: Paket python3-tk installieren)'
    return None


def _win_zwischenablage_setzen(text):
    """Windows: Text direkt ueber die Win32-API (CF_UNICODETEXT) in die Zwischenablage legen.
    Unabhaengig von Tk; wiederholt den Zugriff, falls ein anderes Programm (Zwischenablage-Verlauf, Remotedesktop,
    Clipboard-Manager) die Zwischenablage kurz gesperrt hat. True bei Erfolg."""
    import ctypes
    import time
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
    k32.GlobalLock.restype = ctypes.c_void_p        # ohne diese Angabe werden 64-Bit-Zeiger abgeschnitten
    k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    k32.GlobalUnlock.restype = wintypes.BOOL
    k32.GlobalFree.argtypes = [wintypes.HGLOBAL]
    k32.GlobalFree.restype = wintypes.HGLOBAL

    daten = (text.replace('\r\n', '\n').replace('\n', '\r\n') + '\0').encode('utf-16-le')
    for _ in range(20):
        if u32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        dbg('OpenClipboard fehlgeschlagen, Fehler', ctypes.get_last_error())
        return False
    try:
        u32.EmptyClipboard()
        h = k32.GlobalAlloc(0x0002, len(daten))     # GMEM_MOVEABLE
        if not h:
            return False
        p = k32.GlobalLock(h)
        if not p:
            k32.GlobalFree(h)
            return False
        ctypes.memmove(p, daten, len(daten))
        k32.GlobalUnlock(h)
        if not u32.SetClipboardData(13, h):         # CF_UNICODETEXT; bei Erfolg gehoert der Speicher dem System
            k32.GlobalFree(h)
            return False
        return True
    finally:
        u32.CloseClipboard()


def _extern_zwischenablage(text):
    """Linux/macOS/WSL: Text zusaetzlich ueber das passende Systemprogramm in die Zwischenablage legen.
    Das Programm wird erst beim Kopieren gewaehlt (Sitzungsart und vorhandene Programme), nicht beim Start:
    Wayland -> wl-copy, X11 -> xsel oder xclip, macOS -> pbcopy, WSL -> clip.exe. Diese Programme uebernehmen die
    Zwischenablage dauerhaft; die reine Tk-Zwischenablage geht unter X11/Wayland (XWayland) manchmal verloren.
    Rueckgabe: Namen der Programme, die erfolgreich waren (kann leer sein)."""
    import shutil
    import subprocess

    utf8 = text.encode('utf-8')
    kandidaten = []
    if sys.platform == 'darwin':
        kandidaten.append(('pbcopy', ['pbcopy'], utf8))
    elif sys.platform.startswith('linux'):
        if os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            kandidaten.append(('wl-copy', ['wl-copy'], utf8))
        if os.environ.get('DISPLAY'):
            kandidaten.append(('xsel', ['xsel', '--clipboard', '--input'], utf8))      # in VMware erprobt (vim: :w !xsel -b)
            kandidaten.append(('xclip', ['xclip', '-selection', 'clipboard', '-t', 'UTF8_STRING'], utf8))
        try:
            with open('/proc/version', encoding='utf-8', errors='replace') as fh:
                if 'microsoft' in fh.read().lower():                       # WSL: Windows-Zwischenablage
                    kandidaten.append(('clip.exe', ['clip.exe'], b'\xff\xfe' + text.encode('utf-16-le')))
        except OSError:
            pass
    erfolg = []
    for name, befehl, daten in kandidaten:
        if name == 'xclip' and 'xsel' in erfolg:                           # ein X11-Programm genuegt
            continue
        if not shutil.which(befehl[0]):
            dbg(f'{name}: nicht installiert')
            continue
        try:
            r = subprocess.run(befehl, input=daten, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        except (OSError, subprocess.SubprocessError) as e:
            dbg(f'{name}: fehlgeschlagen: {e}')
            continue
        dbg(f'{name}: Rueckgabewert {r.returncode}')
        if r.returncode == 0:
            erfolg.append(name)
            if DEBUG and name in ('xclip', 'xsel'):               # Gegenprobe: was liegt jetzt wirklich in der Ablage?
                lesen = ['xclip', '-selection', 'clipboard', '-o'] if name == 'xclip' else ['xsel', '--clipboard', '--output']
                ziele = ['xclip', '-selection', 'clipboard', '-t', 'TARGETS', '-o']
                try:
                    inhalt = subprocess.run(lesen, capture_output=True, timeout=3).stdout.decode('utf-8', 'replace')
                    dbg(f'{name}: Gegenprobe: {"gleich" if inhalt == text else "ABWEICHEND"} ({len(inhalt)} Zeichen)')
                    if name == 'xclip':
                        dbg('Ziele (TARGETS):', subprocess.run(ziele, capture_output=True, timeout=3).stdout.decode().split())
                except (OSError, subprocess.SubprocessError) as e:
                    dbg(f'{name}: Gegenprobe fehlgeschlagen: {e}')
    return erfolg


_LETZTES_KOPIEREN = {'text': None, 'zeit': 0.0, 'verfahren': None}


def zwischenablage_setzen(root, text):
    """Text in die Zwischenablage legen. Das Verfahren wird bei jedem Kopieren nach dem laufenden System gewaehlt:
    Windows -> Win32-API (Rueckfall Tk); Linux/macOS/WSL -> Tk und zusaetzlich ein Systemprogramm (siehe
    _extern_zwischenablage). Rueckgabe: Namen der erfolgreichen Verfahren, z. B. 'Tk+xclip', oder None."""
    import time
    import tkinter as tk

    jetzt = time.monotonic()
    if (text == _LETZTES_KOPIEREN['text'] and jetzt - _LETZTES_KOPIEREN['zeit'] < 5
            and _LETZTES_KOPIEREN['verfahren']):
        # Maus loslassen und Strg+C kurz hintereinander: nicht erneut kopieren. Jeder Besitzerwechsel der Ablage
        # wird von Gast-Zusatzprogrammen virtueller Maschinen (Host-Abgleich) einzeln verarbeitet und kann sie verwirren.
        dbg('gleicher Text wie eben schon kopiert, nicht erneut')
        _LETZTES_KOPIEREN['zeit'] = jetzt
        return _LETZTES_KOPIEREN['verfahren']
    erfolg = []
    if sys.platform == 'win32' and ZWISCHENABLAGE != 'tk':
        try:
            if _win_zwischenablage_setzen(text):
                erfolg.append('Win32')
        except Exception as e:                      # z. B. ctypes-Problem: dann Rueckfall auf Tk
            dbg('Win32-Zwischenablage fehlgeschlagen:', e)
    if sys.platform != 'win32' and ZWISCHENABLAGE != 'tk':   # Systemprogramm zuerst (wie 'text | xclip -selection clipboard')
        try:
            erfolg += _extern_zwischenablage(text)
        except Exception as e:
            dbg('Systemprogramm fehlgeschlagen:', e)
    if not erfolg and ZWISCHENABLAGE != 'system':   # Rueckfall: Tk-Zwischenablage
        for _ in range(5):
            try:
                root.clipboard_clear()
                root.clipboard_append(text)
                if sys.platform != 'win32':
                    root.update()                   # X11/macOS: Zwischenablage uebernehmen
                erfolg.append('Tk')
                break
            except tk.TclError as e:
                dbg('Tk-Zwischenablage fehlgeschlagen:', e)
                time.sleep(0.05)
    verfahren = '+'.join(erfolg) or None
    _LETZTES_KOPIEREN.update(text=text if verfahren else None, zeit=jetzt, verfahren=verfahren)
    return verfahren


# Windows: keycode ist der virtuelle Tastenkode; so wirken Strg+C/A/Einfg auch bei nicht-lateinischem Tastaturlayout
_WIN_STRG_TASTEN = {67: 'c', 65: 'a', 45: 'insert'}


def kopieren_ermoeglichen(root, txt):
    """Markieren mit der Maus und Kopieren in die Zwischenablage (Linux und Windows).
    Kopiert wird (1) sofort beim Loslassen der Maustaste nach dem Markieren, (2) mit Strg+C, Strg+Umschalt+C oder
    Strg+Einfg (fuer das ganze Fenster, auch wenn der Tastaturfokus nicht im Textfeld liegt), (3) ueber das
    Kontextmenue (rechte Maustaste). Jedes Kopieren meldet sich kurz in der Titelleiste."""
    import tkinter as tk

    titel = root.title()
    hinweis = [None]

    def melde(text):
        root.title(f'{titel} – {text}')
        if hinweis[0] is not None:
            root.after_cancel(hinweis[0])
        hinweis[0] = root.after(1500, lambda: root.title(titel))

    def kopieren(ev=None):
        dbg('kopieren() aufgerufen, Ausloeser:', getattr(ev, 'type', ev))
        try:
            text = txt.get('sel.first', 'sel.last')
        except tk.TclError as e:             # nichts markiert
            dbg('keine Markierung:', e)
            return 'break'
        if not text:
            dbg('Markierung leer')
            return 'break'
        verfahren = zwischenablage_setzen(root, text)
        if verfahren:
            melde(f'kopiert ({len(text)} Zeichen, {verfahren})')
            dbg(f'kopiert ({verfahren}): {len(text)} Zeichen')
        else:
            melde('Kopieren fehlgeschlagen')
        return 'break'

    def alles_markieren(ev=None):
        txt.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def strg_taste(ev):
        taste = ev.keysym.lower()
        if sys.platform == 'win32':
            taste = _WIN_STRG_TASTEN.get(ev.keycode, taste)
        if taste in ('c', 'insert'):
            return kopieren()
        if taste == 'a':
            return alles_markieren()
        return None

    menue = tk.Menu(root, tearoff=0)
    menue.add_command(label='Kopieren', command=kopieren)
    menue.add_command(label='Alles markieren', command=alles_markieren)

    def kontextmenue(ev):
        txt.focus_set()
        try:
            menue.tk_popup(ev.x_root, ev.y_root)
        finally:
            menue.grab_release()
        return 'break'

    txt.bind('<Button-1>', lambda ev: txt.focus_set(), add='+')   # Klick gibt dem Textfeld den Fokus (auch wenn gesperrt)
    txt.bind('<ButtonRelease-1>', lambda ev: root.after_idle(kopieren), add='+')   # Markieren kopiert sofort
    txt.bind('<Double-ButtonRelease-1>', lambda ev: root.after_idle(kopieren), add='+')
    for k in ('<Control-c>', '<Control-C>', '<Control-Insert>', '<<Copy>>'):
        txt.bind(k, kopieren)
    for k in ('<Control-a>', '<Control-A>'):
        txt.bind(k, alles_markieren)
    root.bind_all('<Control-Key>', strg_taste)       # Rueckfall: Fokus liegt irgendwo im Fenster
    if DEBUG:
        dbg('Tk', root.tk.call('info', 'patchlevel'), 'Python', sys.version.split()[0], 'Plattform', sys.platform,
            'Fenstersystem', root.tk.call('tk', 'windowingsystem'))
        root.bind_all('<Key>', lambda ev: dbg(f'Taste keysym={ev.keysym!r} char={ev.char!r} keycode={ev.keycode} '
                                              f'state={ev.state:#x} Fokus={root.focus_get()}'), add='+')
        root.bind_all('<ButtonRelease-1>', lambda ev: dbg(f'Maus losgelassen in {ev.widget}'), add='+')
    txt.bind('<Button-3>', kontextmenue)
    if sys.platform == 'darwin':
        txt.bind('<Button-2>', kontextmenue)
        txt.bind('<Control-Button-1>', kontextmenue)


def strg_gedrueckt(ev):
    """Strg gedrueckt? Windows meldet AltGr (z. B. @ { } [ ] \\ ~ | auf deutscher Tastatur) als Strg+Alt (0x20000);
    das ist keine Strg-Taste und darf nicht als Steuerbefehl gelten."""
    if sys.platform == 'win32' and ev.state & 0x20000:
        return False
    return bool(ev.state & 0x4)


def eingabe_fenster(st):
    import tkinter as tk

    titel = 'Lochstreifen-Eingabe'
    root = tk.Tk()
    root.title(titel)
    rahmen = tk.Frame(root)
    rahmen.pack(fill='both', expand=True)
    txt = tk.Text(rahmen, width=130, height=36, wrap='char', font='TkFixedFont')
    bildlauf = tk.Scrollbar(rahmen, orient='vertical', command=txt.yview)
    txt.configure(yscrollcommand=bildlauf.set)
    bildlauf.pack(side='right', fill='y')
    txt.pack(side='left', fill='both', expand=True)
    for tag, farbe in FARBEN.items():
        txt.tag_configure(tag, foreground=farbe)

    hinweis = [None]

    def titel_hinweis(text):
        root.title(f'{titel} – {text}')
        if hinweis[0] is not None:
            root.after_cancel(hinweis[0])
        hinweis[0] = root.after(2500, lambda: root.title(titel))

    def zeige(teile):
        for text, tag in teile:
            if tag == LOESCHE_ZEICHEN:            # letztes Zeichen der Zeile; Zeilenumbruch bleibt
                if txt.index('end-1c') != txt.index('end-1c linestart'):
                    txt.delete('end-2c')
            elif tag == LOESCHE_SATZ:             # ganze bisherige Zeile
                txt.delete('end-1c linestart', 'end-1c')
            else:
                txt.insert('end', text, () if tag == NORMAL else (tag,))
        txt.mark_set('insert', 'end')
        txt.see('end')

    def ablehnen(zeichen):
        root.bell()
        titel_hinweis(f'Zeichen {zeichen!r} nicht im R300-Kode')

    def einfuegen():
        try:
            text = root.clipboard_get()
        except tk.TclError:
            return
        abgelehnt = set()
        for ch in text.replace('\r', ''):
            teile = st.tippe(ch)
            if teile:
                zeige(teile)
            else:
                abgelehnt.add(ch)
        if abgelehnt:
            ablehnen(''.join(sorted(abgelehnt)))

    def taste(ev):
        verbraucht, teile, abgelehnt = verarbeite_taste(st, ev.keysym, ev.char, strg_gedrueckt(ev))
        if teile:
            zeige(teile)
        if abgelehnt == 'einfuegen':
            einfuegen()
        elif abgelehnt:
            ablehnen(abgelehnt)
        return 'break' if verbraucht else None

    txt.bind('<Key>', taste)
    for ereignis in ('<<Paste>>', '<<PasteSelection>>', '<<Cut>>', '<<Clear>>'):
        txt.bind(ereignis, lambda ev: 'break')   # keine Bearbeitung ausser durch Stanzen
    kopieren_ermoeglichen(root, txt)
    txt.focus_set()

    root.resizable(False, False)
    root.update_idletasks()
    b, h = root.winfo_reqwidth(), root.winfo_reqheight()
    x = max(0, root.winfo_screenwidth() - b - 10)
    y = max(0, root.winfo_screenheight() - h - 70)   # Rand fuer Taskleiste/Dock
    root.geometry(f'+{x}+{y}')
    root.lift()
    root.attributes('-topmost', True)                # kurz nach vorn, damit das Fenster sichtbar ist
    root.after(300, lambda: root.attributes('-topmost', False))
    root.mainloop()                                  # bleibt offen, bis das Fenster mit X geschlossen wird


def eingabe_text(st):
    """Rueckfall ohne Fenster: Zeichen von der Standardeingabe stanzen."""
    abgelehnt = set()
    for ch in sys.stdin.read().replace('\r', ''):
        if st.tippe(ch) is None:
            abgelehnt.add(ch)
    if abgelehnt:
        print(f'WARNUNG: nicht im R300-Kode, nicht gestanzt: {"".join(sorted(abgelehnt))!r}', file=sys.stderr)


def main():
    for strom in (sys.stdin, sys.stdout):
        if hasattr(strom, 'reconfigure'):
            strom.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(
        prog='c8205_lochstreifen_eingabe.py', allow_abbrev=False,
        description='Erzeugt einen virtuellen C8205-Lochstreifen (R300-Kode) aus Eingaben in einem Fenster.')
    ap.add_argument('--LS-STANZER', '--ls-stanzer', dest='ls_stanzer', metavar='PFAD', required=True,
                    help='zu erzeugender Lochstreifen: Datei oder Verzeichnis (dann stanzer-ausgabe.txt darin)')
    ap.add_argument('--text', action='store_true', help='Zeichen von der Standardeingabe statt im Fenster')
    ap.add_argument('--zwischenablage', choices=('auto', 'tk', 'system'), default='auto',
                    help='Kopierverfahren: auto (Vorgabe: Systemprogramm, sonst Tk), tk (nur Tk), system (nur Systemprogramm bzw. Win32)')
    ap.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    ap.add_argument('--debug', action='store_true', help='Ereignisse und Kopiervorgaenge auf der Fehlerausgabe melden')
    args = ap.parse_args()
    global DEBUG, ZWISCHENABLAGE
    DEBUG = args.debug
    ZWISCHENABLAGE = args.zwischenablage

    try:
        st = Stanzer(args.ls_stanzer)
    except OSError as e:
        print(f'FEHLER: {e}', file=sys.stderr)
        sys.exit(2)
    try:
        if not args.text:
            grund = fenster_unmoeglich()
            if grund:
                print(f'WARNUNG: kein Fenster möglich: {grund}. Eingabe von der Standardeingabe.', file=sys.stderr)
                args.text = True
        if args.text:
            eingabe_text(st)
        else:
            eingabe_fenster(st)
    finally:
        st.schliessen()
    print(f'Lochstreifen: {st.pfad}', file=sys.stderr)


if __name__ == '__main__':
    main()
