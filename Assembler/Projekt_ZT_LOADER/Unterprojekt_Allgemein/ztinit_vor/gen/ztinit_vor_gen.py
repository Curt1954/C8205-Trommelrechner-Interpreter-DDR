#!/usr/bin/env python3
"""ztinit_vor_gen.py -- erzeugt ztinit_vor.asm: dieselbe Vorbelegung der Zusatztrommeln wie ztinit, aber OHNE den Aufruf von ztinit (Halt davor).
Der Aufbau steht in ../../ztinit/gen/ztinit_gen.py (bauen(vor=True)), dort auch die Begruendung. Die erzeugte .asm nie von Hand aendern."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ztinit', 'gen'))
import ztinit_gen

if __name__ == '__main__':
    ztinit_gen.schreibe(True)
