#!/usr/bin/env python3
# ablauf_pdf.py - baut ZIL_Ablauf.pdf (Flussdiagramm zil.asm, 4 Seiten A3 hoch) aus haupt.dot, jn.dot, zi.dot und hs.dot
# Aufruf (im Ordner zil/ablauf, von ueberall moeglich):  python3 ablauf_pdf.py
# Ablauf: 1. mk_dot.py erzeugt haupt.dot, jn.dot, zi.dot und hs.dot  2. dot (Graphviz) -> je ein PDF  3. pypdf setzt jedes PDF
#         mittig und so gross wie moeglich auf eine A3-Seite (Hochformat, Rand 28 pt)  4. Seitenlayout TwoPageLeft
#         (beim Oeffnen Doppelseitenansicht), Titel "ZIL Ablauf".
# Voraussetzung: python3, pypdf, Graphviz (dot) im Suchpfad.  Kein Netz noetig.
import os, subprocess, sys, tempfile
from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from pypdf.generic import NameObject
HIER = os.path.dirname(os.path.abspath(__file__))
os.chdir(HIER)
A3 = (842.0, 1191.0)      # A3 hoch in pt (wie das bisherige PDF)
RAND = 28.0
subprocess.run([sys.executable, 'mk_dot.py'], check=True)
w = PdfWriter()
with tempfile.TemporaryDirectory() as tmp:
    for name in ('haupt', 'jn', 'zi', 'hs'):
        pdf = os.path.join(tmp, name + '.pdf')
        subprocess.run(['dot', '-Tpdf', name + '.dot', '-o', pdf], check=True)
        q = PdfReader(pdf).pages[0]
        bw, bh = float(q.mediabox.width), float(q.mediabox.height)
        f = min((A3[0] - 2 * RAND) / bw, (A3[1] - 2 * RAND) / bh)      # so gross wie moeglich, nie verzerrt
        seite = PageObject.create_blank_page(width=A3[0], height=A3[1])
        dx = (A3[0] - bw * f) / 2.0
        dy = A3[1] - RAND - bh * f                                       # oben ausrichten
        seite.merge_transformed_page(q, Transformation().scale(f, f).translate(dx, dy))
        w.add_page(seite)
w.add_metadata({'/Title': 'ZIL Ablauf'})
w._root_object[NameObject('/PageLayout')] = NameObject('/TwoPageLeft')
with open('ZIL_Ablauf.pdf', 'wb') as fh:
    w.write(fh)
print('ZIL_Ablauf.pdf geschrieben (%d Seiten)' % len(w.pages))
