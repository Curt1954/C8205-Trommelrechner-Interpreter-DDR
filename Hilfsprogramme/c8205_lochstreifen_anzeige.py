#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C8205-Hilfsprogramm: Lochstreifen ausschreiben.

Liest einen virtuellen Lochstreifen (Format wie fuer --leser1/--leser2 des Interpreters c8205_interp.py: eine
Lochungszeile je Textzeile, 8 Zeichen 0/1 in der Spurfolge  w v u p 8 4 2 1, Leerzeilen werden ueberlesen) und
schreibt ihn als Text in einem scrollbaren Fenster aus. Das Fenster entspricht dem Fenster "SW Ausgabe" von
--SW-TERMINAL (Tkinter, 130 x 36 Zeichen, Standardposition rechts unten), bleibt aber offen, bis es mit X
geschlossen wird, und hat eine Bildlaufleiste.

Aufruf:  python3 c8205_lochstreifen_anzeige.py --LS-LESER PFAD [--lage KB|GB] [--text]
         --LS-LESER PFAD   virtueller Lochstreifen: Datei oder Verzeichnis (wie bei --leser1/--leser2 des
                           Interpreters; bei einem Verzeichnis werden alle Dateien ausser Dateien mit fuehrendem
                           Punkt in Namensreihenfolge hintereinander gelesen)
         --lage KB|GB      Zeichenlage am Anfang (Vorgabe KB, wie beim Rechner nach dem Einschalten)
         --text            Ausgabe auf dem Terminal statt im Fenster (auch Rueckfall, wenn kein Fenster moeglich ist)
         --debug           Diagnose: Tasten, Mausereignisse und Kopiervorgaenge auf der Fehlerausgabe (Terminal)

Darstellung (Kodetabelle 1, Spalte "Ausgabe-Adresse"; Darstellung der Zeichen wie beim Schreibwerk des Interpreters):
  * Die Zeichenlage (Klbuch/Gbuch) wird durch die Zeichen Um. KB / Um. GB umgeschaltet; sie gilt auch ueber
    Dateigrenzen hinweg. Die Umschaltzeichen werden nicht ausgegeben, sie wirken nur.
  * Irrung Zeichen loescht das davor stehende Zeichen derselben Zeile, Irrung Satz die ganze bisherige Zeile
    (Satz); beide erscheinen nicht als Marke. Ein Zeilenumbruch wird dadurch nie zurueckgenommen.
  * Sonstige Zeichen ohne Entsprechung als druckbares Zeichen erscheinen als Marke, z. B. <Transport (Relikt)>.
    SatzMarke/WRZL ergibt einen Zeilenumbruch, Tabulator einen Tabulator, Leertaste/ZR ein Leerzeichen.
  * Zeilen ohne Datenlochung (Vorspann) werden ueberlesen.
  * Zeilen mit gerader Zahl gelochter Spuren (ausser "Irrung Zeichen", alle 8 Spuren) sind kein gueltiges Zeichen:
    Marke <Paritaetsfehler 01010101> (rot). Zeilen, die keine 8 Zeichen 0/1 sind, erscheinen als
    <ungueltige Zeile ...> (rot).
"""
import argparse
import os
import sys

VERSION = '1.9'   # 1.9: Um. KB/Um. GB werden nicht mehr ausgegeben (wirken nur), Irrung Zeichen/Satz loeschen im Text; 1.8: unter X11 zuerst xsel, dann xclip; 1.7: Option --zwischenablage auto|tk|system; 1.6: xclip wieder mit -t UTF8_STRING (VM-Abgleich uebernimmt sonst nichts); 1.5: gleicher Text wird innerhalb 5 s nicht erneut kopiert; 1.4: Systemprogramm zuerst, Tk nur als Rueckfall, xclip wie im Terminal aufgerufen; 1.3: xclip mit -t UTF8_STRING, Gegenprobe bei --debug; 1.2: Zwischenablage waehlt das Verfahren bei jedem Kopieren (Win32 / Tk + wl-copy, xclip, xsel, pbcopy, clip.exe); 1.1: Zwischenablage auch unter Windows (Win32-API), AltGr-Korrektur; 1.0: Linux

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

# Marken fuer die Darstellung: Tag-Namen fuer das Fenster
NORMAL, MARKE, FEHLER, DATEI = 'normal', 'marke', 'fehler', 'datei'
FARBEN = {MARKE: '#2E6DA4', FEHLER: '#C00000', DATEI: '#808080'}

ZWISCHENABLAGE = 'auto'   # --zwischenablage: auto (Systemprogramm, dann Tk), tk (nur Tk), system (nur Systemprogramm/Win32)
DEBUG = False     # --debug: Ereignisse und Kopiervorgaenge auf der Fehlerausgabe melden


def dbg(*a):
    if DEBUG:
        print('[debug]', *a, file=sys.stderr, flush=True)


def zeichen_text(zeile, lage):
    """(Text, Tag) fuer eine Tabellenzeile in der gerade gueltigen Zeichenlage ('KB' oder 'GB')."""
    kl, gb, a_gb, a_kb = zeile
    a = a_kb if lage == 'KB' else a_gb
    if a in (9, 10, 32) or 33 <= a <= 255:    # wie sw_zeichen im Interpreter
        return chr(a), NORMAL
    name = kl if lage == 'KB' else gb
    if len(name) == 1:                         # echte Glyphe ohne Ascii-Wert, z. B. ≈ ≋ △
        return name, NORMAL
    return f'<{name}>', MARKE


def lochstreifen_dateien(pfad):
    """Liste der Dateien des virtuellen Lochstreifens (Datei oder Verzeichnis, wie _Stapel im Interpreter)."""
    if os.path.isdir(pfad):
        return sorted(os.path.join(pfad, f) for f in os.listdir(pfad)
                      if os.path.isfile(os.path.join(pfad, f)) and not f.startswith('.'))
    if os.path.isfile(pfad):
        return [pfad]
    raise FileNotFoundError(f'Lochstreifen-Pfad nicht gefunden: {pfad}')


def ausschreiben(pfad, lage='KB'):
    """Liest den Lochstreifen und liefert die Ausgabe als Liste von (Text, Tag)."""
    dateien = lochstreifen_dateien(pfad)
    mehrere = len(dateien) > 1
    teile = []
    anzahl = 0
    for datei in dateien:
        if mehrere:
            teile.append((f'\n--- Datei: {os.path.basename(datei)} ---\n', DATEI))
        with open(datei, encoding='utf-8') as fh:
            for z in (x.strip() for x in fh):
                if not z:
                    continue
                if len(z) != 8 or set(z) - {'0', '1'}:
                    teile.append((f'<ungültige Zeile {z!r}>', FEHLER))
                    continue
                wert = int(z, 2)
                if wert == 0:                  # Vorspann (keine Datenlochung)
                    continue
                zeile = TABELLE.get(format(wert, '03o'))
                gerade = z.count('1') % 2 == 0
                if gerade and wert != 0o377:
                    teile.append((f'<Paritätsfehler {z}>', FEHLER))
                    continue
                if zeile is None:
                    teile.append((f'<unbekannte Lochung {z}>', FEHLER))
                    continue
                anzahl += 1
                if wert == 0o117:                  # Um. KB / Um. GB: wirken nur, keine Ausgabe
                    lage = 'KB'
                elif wert == 0o057:
                    lage = 'GB'
                elif wert == 0o377:                # Irrung Zeichen: letztes Zeichen der Zeile loeschen
                    if teile and '\n' not in teile[-1][0] and teile[-1][1] != DATEI:
                        teile.pop()
                elif wert == 0o016:                # Irrung Satz: ganze bisherige Zeile loeschen
                    while teile and '\n' not in teile[-1][0] and teile[-1][1] != DATEI:
                        teile.pop()
                else:
                    teile.append(zeichen_text(zeile, lage))
    if anzahl == 0 and not any(t == FEHLER for _, t in teile):
        teile.append(('(Der Lochstreifen enthält keine Zeichen.)', MARKE))
    return teile


def fenster_unmoeglich():
    """Grund, warum kein Fenster geoeffnet werden kann, sonst None (wie sw_fenster_unmoeglich im Interpreter)."""
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


def zeige_fenster(teile):
    import tkinter as tk

    root = tk.Tk()
    root.title('Lochstreifen')
    rahmen = tk.Frame(root)
    rahmen.pack(fill='both', expand=True)
    txt = tk.Text(rahmen, width=130, height=36, wrap='char', font='TkFixedFont', state='disabled')
    bildlauf = tk.Scrollbar(rahmen, orient='vertical', command=txt.yview)
    txt.configure(yscrollcommand=bildlauf.set)
    bildlauf.pack(side='right', fill='y')
    txt.pack(side='left', fill='both', expand=True)
    for tag, farbe in FARBEN.items():
        txt.tag_configure(tag, foreground=farbe)

    txt.configure(state='normal')
    for text, tag in teile:
        txt.insert('end', text, () if tag == NORMAL else (tag,))
    txt.configure(state='disabled')
    txt.focus_set()
    kopieren_ermoeglichen(root, txt)

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


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(
        prog='c8205_lochstreifen_anzeige.py', allow_abbrev=False,
        description='Schreibt einen virtuellen C8205-Lochstreifen in einem scrollbaren Fenster aus.')
    ap.add_argument('--LS-LESER', '--ls-leser', dest='ls_leser', metavar='PFAD', required=True,
                    help='virtueller Lochstreifen: Datei oder Verzeichnis (Format wie --leser1/--leser2 des Interpreters)')
    ap.add_argument('--lage', choices=('KB', 'GB'), type=str.upper, default='KB',
                    help='Zeichenlage am Anfang (Vorgabe KB)')
    ap.add_argument('--text', action='store_true', help='Ausgabe auf dem Terminal statt im Fenster')
    ap.add_argument('--zwischenablage', choices=('auto', 'tk', 'system'), default='auto',
                    help='Kopierverfahren: auto (Vorgabe: Systemprogramm, sonst Tk), tk (nur Tk), system (nur Systemprogramm bzw. Win32)')
    ap.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    ap.add_argument('--debug', action='store_true', help='Ereignisse und Kopiervorgaenge auf der Fehlerausgabe melden')
    args = ap.parse_args()
    global DEBUG, ZWISCHENABLAGE
    DEBUG = args.debug
    ZWISCHENABLAGE = args.zwischenablage

    try:
        teile = ausschreiben(args.ls_leser, args.lage)
    except (OSError, UnicodeDecodeError) as e:
        print(f'FEHLER: {e}', file=sys.stderr)
        sys.exit(2)

    if not args.text:
        grund = fenster_unmoeglich()
        if grund:
            print(f'WARNUNG: kein Fenster möglich: {grund}. Ausgabe auf dem Terminal.', file=sys.stderr)
            args.text = True
    if args.text:
        s = ''.join(t for t, _ in teile)
        print(s if s.endswith('\n') else s + '\n', end='')
    else:
        zeige_fenster(teile)


if __name__ == '__main__':
    main()
