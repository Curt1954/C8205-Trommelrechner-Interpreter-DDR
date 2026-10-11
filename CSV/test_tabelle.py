#!/usr/bin/env python3
"""Erzeugt eine Übersichtstabelle aller Tests.

Spalten:
  1. Testdateiname
  2. Inhalt des Tests (verbal, aus den #DOK-Zeilen)
  3. Dateien der virtuellen Geräte (Leser, SW-Ausgabe, K0, ...) und
     Test-Vergleichsdateien (--pruefe-sw-ausgabe / --pruefe-stanzer1)
  4. zugehöriger ASM-Quelltext (falls vorhanden)

Aufruf (aus beliebigem Verzeichnis; die Basis mit Tests/ und Assembler/ wird
automatisch gesucht: aktuelles Verzeichnis, Skriptverzeichnis, jeweils deren
Elternverzeichnis - z.B. wenn das Skript in CSV/ neben Assembler/ liegt):
    python3 test_tabelle.py                    # schreibt test_tabelle.csv, .md, .xlsx (wenn openpyxl da ist)
    python3 test_tabelle.py --basis /pfad --format md csv xlsx html
Die Ausgabedateien landen im Skriptverzeichnis (oder unter --ausgabe, wenn Pfad angegeben).
"""
import argparse
import csv
import difflib
import html
import os
import re
import sys

ASM_VERZEICHNISSE = ["Claude", "Claude_bsp_reassemblierung", "Proj_FeldSortieren",
                     "Projekt_1", "Projekt_2"]

# Schalter in den Testdateien -> Anzeigename
GERAETE = [
    ("--leser1", "Leser 1"),
    ("--leser2", "Leser 2"),
    ("--k0", "K0-Eingabe"),
    ("--sw-ausgabe", "SW-Ausgabe"),
    ("--pruefe-sw-ausgabe", "Vergleich SW-Ausgabe"),
    ("--pruefe-stanzer1", "Vergleich Stanzer 1"),
]


SKRIPTDIR = os.path.dirname(os.path.abspath(__file__))


def finde_basis(vorgabe=None):
    """Verzeichnis suchen, das Tests/ und Assembler/ enthaelt."""
    if vorgabe:
        return os.path.abspath(vorgabe)
    kandidaten = []
    for start in (os.getcwd(), SKRIPTDIR):
        k = os.path.abspath(start)
        for _ in range(3):  # Verzeichnis selbst und bis zu 2 Ebenen darueber
            if k not in kandidaten:
                kandidaten.append(k)
            k = os.path.dirname(k)
    for k in kandidaten:
        if os.path.isdir(os.path.join(k, "Tests")) and os.path.isdir(os.path.join(k, "Assembler")):
            return k
    for k in kandidaten:
        if os.path.isdir(os.path.join(k, "Tests")):
            return k
    sys.exit("Keine Basis mit Tests/ und Assembler/ gefunden. Bitte --basis /pfad angeben.")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def lies(pfad):
    with open(pfad, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def trommelzellen(pfad):
    """Zellen (Adresse -> Wert) aus dem Abschnitt 'Trommeldatei:'."""
    zellen, im_abschnitt = {}, False
    for z in lies(pfad):
        if z.startswith("Trommeldatei"):
            im_abschnitt = True
            continue
        if im_abschnitt and re.match(r"(Tastenfolge|Pr\S*fungen)\s*:", z):
            break
        if im_abschnitt:
            m = re.match(r"\s*([0-7]{4}):\s*([0-7]+)", z)
            if m:
                zellen[m[1]] = m[2]
    return zellen


def beschreibung(zeilen):
    """#DOK-Zeilen (ohne Duplikate) zu einem Text verbinden."""
    teile = []
    for z in zeilen:
        m = re.match(r"#DOK-\d+\s*(.*)", z)
        if m and m[1].strip() and m[1].strip() not in teile:
            teile.append(m[1].strip())
    return " ".join(teile)


def ersatzbeschreibung(zeilen, name):
    """Falls keine #DOK-Zeile existiert: Kommentare / Tastenfolge als Hinweis."""
    kommentare = []
    for z in zeilen:
        if z.startswith("#") and not re.match(r"#(DOK|SPEI|PROT|SPUR|STARTE|INTERRUPT|AC|BZ)", z):
            t = z.lstrip("# ").strip()
            if t:
                kommentare.append(t)
    text = " ".join(kommentare[:2])
    for i, z in enumerate(zeilen):
        if z.startswith("Tastenfolge"):
            for folge in zeilen[i + 1:i + 2]:
                if folge.strip():
                    text += f" [Tastenfolge: {folge.strip()}]"
            break
    return (text.strip() or "(keine #DOK-Beschreibung vorhanden)")


def geraete_zeilen(zeilen, basis, testname=""):
    """Geräte-/Vergleichsdateien aus den '--schalter wert'-Zeilen (nur Pfade)."""
    ausgabe = []
    schalter_bekannt = {sw for sw, _ in GERAETE}
    for z in zeilen:
        if not z.startswith("--"):
            continue
        teile = z.split(" #")[0].strip().split(None, 1)
        if len(teile) < 2 or teile[0] not in schalter_bekannt:
            continue
        schalter, wert = teile[0], re.sub(r"^datei=", "", teile[1].strip())
        pfad = os.path.join(basis, wert)
        # Ausgabedateien/-verzeichnisse entstehen erst beim Lauf
        if schalter != "--sw-ausgabe" and not os.path.exists(pfad):
            print(f"Warnung: {testname}: Datei fehlt: {wert}", file=sys.stderr)
        ausgabe.append(wert)
    return ausgabe


def asm_dateien(basis):
    liste = []
    for d in ASM_VERZEICHNISSE:
        wurzel = os.path.join(basis, "Assembler", d)
        for r, _, fs in os.walk(wurzel):
            for f in sorted(fs):
                if f.endswith(".asm"):
                    pfad = os.path.join(r, f)
                    liste.append((os.path.relpath(pfad, os.path.join(basis, "Assembler")), pfad))
    return sorted(liste)


def kern(s):
    """Normalisierter Name ohne 'bsp'-Teile (pj2-bsp_x und pj2_x sollen passen)."""
    return "_".join(t for t in norm(s).split("_") if t != "bsp")


def finde_asm(testpfad, stamm, asm, asm_zellen, text=""):
    """Zuordnung: 1. gleicher Name, 2. Trommelinhalt passt (bei Mehrdeutigkeit
    ähnlichster Name), 3. Namenspräfix, 4. Voraussetzung Minimalprogramm."""
    def stamm_von(rel):
        return os.path.splitext(os.path.basename(rel))[0]

    gleich = [rel for rel, p in asm if stamm_von(p) == stamm]
    if gleich:
        return gleich[0], ""
    zellen = trommelzellen(testpfad)
    def aehnl(rel):
        return difflib.SequenceMatcher(None, norm(stamm), norm(stamm_von(rel))).ratio()
    if zellen:
        kand = [rel for rel, p in asm
                if asm_zellen[rel] and all(asm_zellen[rel].get(k) == v for k, v in zellen.items())]
        kand.sort(key=aehnl, reverse=True)
        if kand and aehnl(kand[0]) >= 0.6:
            hinweis = " (über Trommelinhalt)"
            if len(kand) > 1 and aehnl(kand[0]) == aehnl(kand[1]):
                hinweis = " (mehrdeutig: " + ", ".join(os.path.basename(k) for k in kand[:3]) + ")"
            return kand[0], hinweis
    # Namenspräfix (ziffern_uebergehen -> ziffern, pj2-bsp_maximum_3_zahlen_a_max -> pj2_maximum_3_zahlen)
    k = kern(stamm)
    pre = [rel for rel, p in asm
           if k.startswith(kern(stamm_von(rel)) + "_") and len(kern(stamm_von(rel))) >= 5]
    if pre:
        pre.sort(key=lambda r: len(kern(stamm_von(r))), reverse=True)
        return pre[0], " (über Namen)"
    # BIS-Tests setzen das Minimalprogramm auf der Trommel voraus
    if "minimalprogramm" in text.lower() or stamm.startswith("pj2-bis_"):
        for rel, p in asm:
            if stamm_von(p) == "pj2-bis_minimalprogramm":
                return rel, " (Voraussetzung: Minimalprogramm auf der Trommel)"
    return "", ""


def sammle(basis):
    testdir = os.path.join(basis, "Tests")
    if not os.path.isdir(testdir):
        sys.exit(f"Verzeichnis nicht gefunden: {testdir}")
    asm = asm_dateien(basis)
    asm_zellen = {}
    for rel, p in asm:
        t = os.path.splitext(p)[0] + ".test"
        asm_zellen[rel] = trommelzellen(t) if os.path.exists(t) else {}

    zeilen_tab = []
    for name in sorted(os.listdir(testdir)):
        if not name.endswith((".txt", ".test")):
            continue
        pfad = os.path.join(testdir, name)
        z = lies(pfad)
        # Datei hat das Testformat? (Soll-Dateien haben keinen Abschnitt 'Trommeldatei:')
        if not any(x.startswith("Trommeldatei") for x in z):
            continue
        stamm = os.path.splitext(name)[0]
        text = beschreibung(z) or ersatzbeschreibung(z, name)
        geraete = geraete_zeilen(z, basis, name)
        rel, hinweis = finde_asm(pfad, stamm, asm, asm_zellen, text)
        zeilen_tab.append((name, text, "\n".join(geraete), rel))
        if hinweis:
            print(f"Hinweis: {name} -> {rel}{hinweis}", file=sys.stderr)
    return zeilen_tab


KOPF = ["Testdatei", "Inhalt des Tests", "Dateien virtueller Geräte / Vergleichsdatei", "ASM-Quelltext"]


def schreibe_csv(tab, pfad):
    with open(pfad, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(KOPF)
        w.writerows(tab)


def schreibe_md(tab, pfad):
    def e(s):
        return s.replace("|", "\\|").replace("\n", "<br>")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(KOPF) + " |\n|" + "---|" * len(KOPF) + "\n")
        for r in tab:
            f.write("| " + " | ".join(e(x) for x in r) + " |\n")


def schreibe_html(tab, pfad):
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><meta charset='utf-8'><title>Testübersicht</title>"
                "<style>body{font:14px sans-serif}table{border-collapse:collapse}"
                "td,th{border:1px solid #aaa;padding:4px 8px;vertical-align:top}"
                "th{background:#eee}</style><table><tr>"
                + "".join(f"<th>{html.escape(k)}</th>" for k in KOPF) + "</tr>\n")
        for r in tab:
            f.write("<tr>" + "".join(
                f"<td>{html.escape(x).replace(chr(10), '<br>')}</td>" for x in r) + "</tr>\n")
        f.write("</table>")


def schreibe_xlsx(tab, pfad):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
    except ImportError:
        print("openpyxl fehlt -> xlsx übersprungen (pip install openpyxl)", file=sys.stderr)
        return False
    wb = Workbook()
    ws = wb.active
    ws.title = "Tests"
    ws.append(KOPF)
    for r in tab:
        ws.append(list(r))
    for c in ws[1]:
        c.font = Font(bold=True)
    for sp, breite in zip("ABCD", (42, 80, 60, 50)):
        ws.column_dimensions[sp].width = breite
    for row in ws.iter_rows(min_row=1):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(pfad)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--basis", default=None, help="Verzeichnis mit Tests/, Assembler/ ... (Standard: automatisch suchen)")
    ap.add_argument("--format", nargs="+", default=["csv", "md", "xlsx"],
                    choices=["csv", "md", "xlsx", "html"])
    ap.add_argument("--ausgabe", default="test_tabelle", help="Dateiname ohne Endung")
    a = ap.parse_args()

    basis = finde_basis(a.basis)
    print("Basis:", basis)
    tab = sammle(basis)
    ausgabe = a.ausgabe if os.path.isabs(a.ausgabe) else os.path.join(SKRIPTDIR, a.ausgabe)
    for fmt in a.format:
        ziel = f"{ausgabe}.{fmt}"
        ok = {"csv": schreibe_csv, "md": schreibe_md, "html": schreibe_html,
              "xlsx": schreibe_xlsx}[fmt](tab, ziel)
        if ok is not False:
            print("geschrieben:", ziel)
    ohne_asm = sum(1 for r in tab if not r[3])
    print(f"{len(tab)} Tests, davon {len(tab) - ohne_asm} mit ASM-Quelltext, {ohne_asm} ohne.")


if __name__ == "__main__":
    main()
