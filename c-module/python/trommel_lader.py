"""Laedt das C-Modul c8205_trommel. Ist es nicht ladbar: Fehlermeldung und Beenden.
Rueckkehrcode 16 = "Test startet nicht", wie bei fehlender oder fehlerhafter Trommeldatei (Python_Interpreter.md, Abschnitt 6).
(Der Wert 16 ist ein VORSCHLAG und noch nicht mit dem Projektinhaber abgestimmt.)"""
import sys

RC_START_NICHT_MOEGLICH = 16


def lade_trommelmodul(melde=print):
    try:
        import c8205_trommel
    except ImportError as e:
        melde('\nFEHLER: das C-Modul "c8205_trommel" (echte Trommel) ist nicht ladbar: ' + str(e))
        melde('  Bauen: im Ordner trommel/c-module/python  "python3 setup.py build_ext --inplace" '
              '(Windows: "python setup.py build_ext --inplace"; braucht einen C-Compiler und die Python-Entwicklungsdateien).')
        melde('  Es startet kein Test.')
        sys.exit(RC_START_NICHT_MOEGLICH)
    return c8205_trommel
