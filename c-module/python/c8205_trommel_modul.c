/* c8205_trommel_modul.c — Python-Erweiterungsmodul "c8205_trommel".
 * Bindet trommel.c, bahnsperre.c und unterbrechung.c FEST ein (statisch gelinkt: eine Datei, keine zweite Bibliothek zu finden).
 * Limited API (abi3): ein Build gilt fuer CPython ab 3.8, ohne Neubau je Python-Version.
 * Blockierende Aufrufe geben die GIL frei. Strg+C behandelt Python (KeyboardInterrupt nach hoechstens einem blockierenden
 * Zugriff, d. h. nach <= 3,2 ms); unterbrechung_einrichten() wird hier NICHT aufgerufen (es wuerde den Handler von Python ersetzen).
 * Aufraeumen nach Strg+C: trommel_ausschalten() im finally des Aufrufers (Interpreter: Trommel.schliessen()). */
#ifndef Py_LIMITED_API
#define Py_LIMITED_API 0x03080000
#endif
#define PY_SSIZE_T_CLEAN
#include <Python.h>
/* G4-005: Py_RETURN_NONE der 3.12-Header gibt bei abi3 (Py_LIMITED_API < 3.12) None OHNE Referenzzaehler zurueck (None ist dort
 * unsterblich); auf 3.8 bis 3.11 sinkt dann bei jedem Aufruf der Zaehler von None -> "none_dealloc: deallocating None".  Darum hier
 * ueberall die echten Funktionen Py_IncRef/Py_DecRef (exportiert, in jeder Python-Version gleich) statt der Makros. */
#undef Py_RETURN_NONE
#define Py_RETURN_NONE do { Py_IncRef(Py_None); return Py_None; } while (0)
#include "../trommel.h"
#include "../bahnsperre.h"
#include "c8205_ton_methoden.h"      /* Tonmischer (tonmisch.c): ton_*-Methoden, TonFehler */

static PyObject *TrommelFehler, *TrommelAbbruch;

static PyObject *wirf(int rc)
{
    if (rc == TROMMEL_ABGEBROCHEN) PyErr_SetString(TrommelAbbruch, "Trommelzugriff abgebrochen");
    else PyErr_SetString(TrommelFehler, "Trommelzugriff fehlgeschlagen (Trommel aus, Adresse > 07777 oder Dateifehler)");
    return NULL;
}

static PyObject *m_einschalten(PyObject *self, PyObject *args, PyObject *kw)
{
    const char *pfad; const char *basp = NULL; int start = -1, rc;
    char stellung[8] = "", meldung[512] = "";
    static char *kwlist[] = {"pfad", "start_index", "basp", NULL};
    (void)self;
    if (!PyArg_ParseTupleAndKeywords(args, kw, "s|iz", kwlist, &pfad, &start, &basp)) return NULL;
    /* Als Erstes die Bahnsperrenschalter (vor dem ersten Trommelzugriff, Entwurf 86/87) */
    rc = bahnsperre_hochfahren(pfad, basp, stellung, meldung, sizeof meldung);
    if (rc != 0) { PyErr_SetString(TrommelFehler, meldung); return NULL; }
    Py_BEGIN_ALLOW_THREADS
    rc = trommel_einschalten_start(pfad, start);
    Py_END_ALLOW_THREADS
    if (rc != 0) {
        PyErr_SetString(TrommelFehler, "Trommel konnte nicht eingeschaltet werden (Grund steht auf stderr)");
        return NULL;
    }
    return PyUnicode_FromString(stellung);   /* uebernommene Stellung der Bahnsperrenschalter */
}

static PyObject *m_ausschalten(PyObject *self, PyObject *args)
{
    (void)self; (void)args;
    Py_BEGIN_ALLOW_THREADS
    trommel_ausschalten();
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *m_lesen_warten(PyObject *self, PyObject *args)
{
    unsigned int adr, wz = 0; uint64_t w = 0; int rc;
    (void)self;
    if (!PyArg_ParseTuple(args, "I", &adr)) return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = trommel_lesen_warten(adr, &w, &wz);
    Py_END_ALLOW_THREADS
    if (rc != TROMMEL_OK) return wirf(rc);
    return Py_BuildValue("(KI)", (unsigned long long)w, wz);
}

static PyObject *m_schreiben_warten(PyObject *self, PyObject *args)
{
    unsigned int adr, wz = 0; unsigned long long wert; int rc;
    (void)self;
    if (!PyArg_ParseTuple(args, "IK", &adr, &wert)) return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = trommel_schreiben_warten(adr, (uint64_t)wert, &wz);
    Py_END_ALLOW_THREADS
    if (rc != TROMMEL_OK && rc != TROMMEL_SCHREIBEN_GESPERRT) return wirf(rc);
    return Py_BuildValue("(NI)", PyBool_FromLong(rc == TROMMEL_SCHREIBEN_GESPERRT), wz);   /* N: uebernimmt die Referenz (vorher Leck) */   /* (gesperrt, wartezeit) */
}

static PyObject *m_warten_abbrechen(PyObject *self, PyObject *args)
{
    (void)self; (void)args;
    trommel_warten_abbrechen();
    Py_RETURN_NONE;
}

static PyObject *m_aktueller_sektor(PyObject *self, PyObject *args)
{
    (void)self; (void)args;
    return PyLong_FromUnsignedLong(trommel_aktueller_sektor());
}

static PyObject *m_lesen(PyObject *self, PyObject *args)
{
    unsigned int adr;
    (void)self;
    if (!PyArg_ParseTuple(args, "I", &adr)) return NULL;
    return PyLong_FromUnsignedLongLong((unsigned long long)trommel_lesen(adr));
}

static PyObject *m_schreiben(PyObject *self, PyObject *args)
{
    unsigned int adr; unsigned long long wert; int rc;
    (void)self;
    if (!PyArg_ParseTuple(args, "IK", &adr, &wert)) return NULL;
    rc = trommel_schreiben(adr, (uint64_t)wert);
    if (rc != TROMMEL_OK && rc != TROMMEL_SCHREIBEN_GESPERRT) return wirf(rc);
    return PyBool_FromLong(rc == TROMMEL_SCHREIBEN_GESPERRT);
}

static PyObject *m_statistik(PyObject *self, PyObject *args)
{
    trommel_statistik_t s; PyObject *d;
    (void)self; (void)args;
    trommel_statistik_lesen(&s);
    d = PyDict_New();
    if (!d) return NULL;
#define EIN(name, wert) do { PyObject *v = PyLong_FromUnsignedLongLong(wert); \
        if (!v || PyDict_SetItemString(d, name, v) != 0) { Py_DecRef(v); Py_DecRef(d); return NULL; } Py_DecRef(v); } while (0)
    EIN("ticks", s.ticks); EIN("aufwachen", s.aufwachen); EIN("nachgeholte_ticks", s.nachgeholte_ticks);
    EIN("verspaetung_summe_ns", s.verspaetung_summe_ns); EIN("verspaetung_max_ns", s.verspaetung_max_ns);
    EIN("zugriffe", s.zugriffe); EIN("wartezeit_summe_ticks", s.wartezeit_summe_ticks);
#undef EIN
    return d;
}

static PyObject *m_bahnsperre_setzen(PyObject *self, PyObject *args)
{
    int a, b, c, d, e, f;
    (void)self;
    if (!PyArg_ParseTuple(args, "iiiiii", &a, &b, &c, &d, &e, &f)) return NULL;
    bahnsperre_setzen(a, b, c, d, e, f);
    Py_RETURN_NONE;
}

static PyMethodDef methoden[] = {
    {"einschalten", (PyCFunction)(void(*)(void))m_einschalten, METH_VARARGS | METH_KEYWORDS, "einschalten(pfad, start_index=-1, basp=None) -> stellung: Bahnsperre aus --BASP bzw. Schalterdatei uebernehmen, Trommeldatei pruefen, Hintergrundprozess starten (pfad: UTF-8)"},
    {"ausschalten", m_ausschalten, METH_NOARGS, "ausschalten(): wartende Aufrufer freigeben, Hintergrundprozess beenden, Datei schliessen (mehrfach aufrufbar)"},
    {"lesen_warten", m_lesen_warten, METH_VARARGS, "lesen_warten(adresse) -> (wert, wartezeit_ticks); blockiert bis die Zelle aktuell ist"},
    {"schreiben_warten", m_schreiben_warten, METH_VARARGS, "schreiben_warten(adresse, wert) -> (gesperrt, wartezeit_ticks)"},
    {"warten_abbrechen", m_warten_abbrechen, METH_NOARGS, "warten_abbrechen(): beendet einen wartenden Zugriff aus einem anderen Thread"},
    {"aktueller_sektor", m_aktueller_sektor, METH_NOARGS, "aktueller_sektor() -> aktuelle Sektornummer (exakt aus der Uhr)"},
    {"lesen", m_lesen, METH_VARARGS, "lesen(adresse): direkt, OHNE Koinzidenz (nur Vorbelegung/Tests)"},
    {"schreiben", m_schreiben, METH_VARARGS, "schreiben(adresse, wert) -> gesperrt: direkt, OHNE Koinzidenz (nur Vorbelegung/Tests)"},
    {"statistik", m_statistik, METH_NOARGS, "statistik() -> dict"},
    {"bahnsperre_setzen", m_bahnsperre_setzen, METH_VARARGS, "bahnsperre_setzen(ein_aus, s0040, s0100, s0200, s0400, s1000)"},
    TON_METHODEN,
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef modul = {
    PyModuleDef_HEAD_INIT, "c8205_trommel",
    "C 8205: Magnettrommel mit Koinzidenz im Hintergrundprozess und Tonmischer (C-Module statisch eingebunden).", -1, methoden,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit_c8205_trommel(void)
{
    PyObject *m = PyModule_Create(&modul);
    if (!m) return NULL;
    TrommelFehler = PyErr_NewException("c8205_trommel.TrommelFehler", PyExc_Exception, NULL);
    TrommelAbbruch = PyErr_NewException("c8205_trommel.TrommelAbbruch", TrommelFehler, NULL);
    if (!TrommelFehler || !TrommelAbbruch) { Py_DecRef(TrommelFehler); Py_DecRef(TrommelAbbruch); Py_DecRef(m); return NULL; }
    Py_IncRef(TrommelFehler); Py_IncRef(TrommelAbbruch);
    if (PyModule_AddObject(m, "TrommelFehler", TrommelFehler) < 0 || PyModule_AddObject(m, "TrommelAbbruch", TrommelAbbruch) < 0) {
        Py_DecRef(m); return NULL;
    }
    TonFehler = PyErr_NewException("c8205_trommel.TonFehler", PyExc_Exception, NULL);
    if (!TonFehler) { Py_DecRef(m); return NULL; }
    Py_IncRef(TonFehler);
    if (PyModule_AddObject(m, "TonFehler", TonFehler) < 0) { Py_DecRef(m); return NULL; }
    return m;
}
