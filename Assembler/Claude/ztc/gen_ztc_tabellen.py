#!/usr/bin/env python3
# gen_ztc_tabellen.py - erzeugt die beiden Eingabetabellen (je 64 Zellen) fuer ztc.asm aus Tabelle 1 des Interpreters.
# Aufruf (im Projektstamm): python3 -I Assembler/Claude/ztc/gen_ztc_tabellen.py > tabellen.inc
# Regel: Eingabebefehl 011 tab springt bei Zeichen mit Sprung-Umstellung auf die Tabellenzelle (Zelle wird als Befehl ausgefuehrt),
#        sonst AC := Zelleninhalt. tab muss auf einem Vielfachen von 0100 liegen (Eingabeadresse 00..77 wird ODER-verknuepft).
import sys, os
sys.path.insert(0, os.getcwd())
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import c8205_interp as ci

# Zeile je Eingabeadresse (BM und ZV teilen 072: es gilt die Sprungzeile BM)
zeilen = {}
for r in ci.TABELLE1:
    if r[0] == 54 or r[6] is None:
        continue
    zeilen.setdefault(r[6], []).append(r)
zeilen[0o36] = [ci.EINGABE_ZEILE[0o36]]

def name(r):
    n = r[1] if r[1] not in ('', None) else r[2]
    return str(n)

def zelle(code, modus):
    """modus 'k' = Tastatur-Dialog, 'b' = Lochband. -> (Operand-Text, Kommentar)"""
    rs = zeilen.get(code, [])
    # in dezimal gefuehrter Spalte 6 steht die Eingabeadresse; ci.TABELLE1 fuehrt sie als int
    if not rs:
        return ('dw      077', 'unbelegt')
    sprung = any(r[7] for r in rs)
    nm = '/'.join(sorted({name(r) for r in rs}))
    n1 = rs[0][1]
    if sprung:
        if n1 in ('Leertaste', 'SatzMarke', '.'):
            return ('000     ' + ('d_end' if modus == 'k' else ('b_pkt' if n1 == '.' else 'b_skip')), nm)
        if n1 in ('Um. KB', 'Um. GB') and modus == 'b':
            return ('000     b_skip', nm)
        return ('000     ' + ('d_lies' if modus == 'k' else 'b_fehl'), nm)
    if n1 in list('0123456789'):
        return ('dw      0%o' % int(n1), 'Ziffer ' + n1)
    if modus == 'k' and n1 == 'j':
        return ('dw      0100', 'J')
    if modus == 'k' and n1 == 'n':
        return ('dw      0101', 'N')
    if modus == 'b' and n1 == '/':
        return ('dw      040', 'Schraegstrich (Bandende)')
    return ('dw      077', nm)

out = []
for modus, label, kopf in (('k', 'tab_k', 'Tastaturtabelle des Dialogs (Eingabeadresse = Zellennummer)'),
                           ('b', 'tab_b', 'Lochbandtabelle (Eingabeadresse = Zellennummer)')):
    out.append('; ---- %s ----' % kopf)
    # die ganze Tabelle steht in einem begin/bend-Block, damit der Optimierer (Doku 5.2) keine Zelle verlegt;
    # Befehlszeilen (000 ziel) sind in begin/bend erlaubt (ab c82ass 1.00-041)
    out.append('                begin                ; Tabelle festhalten (Optimierer verlegt keine Zelle)')
    for c in range(64):
        op, kom = zelle(c, modus)
        lab = (label + ':') if c == 0 else ''
        out.append('%-16s%-16s; %02o %s' % (lab, op, c, kom))
    out.append('                bend                 ; Ende der festgehaltenen Tabelle')
    out.append('')
print('\n'.join(out))
