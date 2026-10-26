/* c8205_ztmodul.c — Python-Erweiterungsmodul "c8205_ztmodul": die Zusatztrommeln des C 8205Z (zt_modul.c) fuer GRAFIK.
 * Version: 0.01-002
 * Bindet zt_modul.c FEST ein (mit -DZT_OHNE_TROMMEL; trommel.c ist NICHT enthalten, damit es nur EINE Haupttrommel gibt: die
 * des Moduls c8205_trommel). Die Haupttrommel wird ueber drei Python-Funktionen angekoppelt (lesen, schreiben, aktueller_sektor
 * von c8205_trommel); die Rueckrufe kommen aus dem Aufrufer- und aus dem Empfaengerthread und nehmen die GIL.
 * Blockierende Aufrufe geben die GIL frei. Limited API (abi3) wie c8205_trommel. */
#ifndef Py_LIMITED_API
#define Py_LIMITED_API 0x03080000
#endif
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#undef Py_RETURN_NONE
#define Py_RETURN_NONE do { Py_IncRef(Py_None); return Py_None; } while (0)
#include "../zt_modul.h"

static PyObject *ZtFehler;
static PyObject *fn_lesen, *fn_schreiben, *fn_sektor;

/* ---- Rueckrufe der Kopplung (GIL nehmen) ---- */
static uint64_t ht_lesen(unsigned adr)
{
    uint64_t w = 0;
    PyGILState_STATE g = PyGILState_Ensure();
    PyObject *r = PyObject_CallFunction(fn_lesen, "I", adr);
    if (r) { w = (uint64_t)PyLong_AsUnsignedLongLongMask(r); Py_DecRef(r); } else PyErr_Clear();
    PyGILState_Release(g);
    return w;
}
static int ht_schreiben(unsigned adr, uint64_t wert)
{
    int rc = 0;
    PyGILState_STATE g = PyGILState_Ensure();
    PyObject *r = PyObject_CallFunction(fn_schreiben, "IK", adr, (unsigned long long)wert);
    if (r) Py_DecRef(r); else { PyErr_Clear(); rc = -1; }
    PyGILState_Release(g);
    return rc;
}
static unsigned ht_sektor(void)
{
    unsigned s = 0;
    PyGILState_STATE g = PyGILState_Ensure();
    PyObject *r = PyObject_CallFunction(fn_sektor, NULL);
    if (r) { s = (unsigned)PyLong_AsUnsignedLongMask(r); Py_DecRef(r); } else PyErr_Clear();
    PyGILState_Release(g);
    return s;
}
static const zt_ht_t KOPPLUNG = { ht_lesen, ht_schreiben, ht_sektor };

static PyObject *m_einschalten(PyObject *self, PyObject *args)
{
    PyObject *liste, *l, *s, *z;
    const char *pf[ZT_ANZAHL];
    PyObject *keep[ZT_ANZAHL] = {0};
    int start, rc;
    (void)self;
    if (!PyArg_ParseTuple(args, "OiOOO", &liste, &start, &l, &s, &z)) return NULL;
    if (!PyList_Check(liste) || PyList_Size(liste) != ZT_ANZAHL) { PyErr_SetString(ZtFehler, "pfade: Liste mit vier Dateinamen erwartet"); return NULL; }
    for (int k = 0; k < ZT_ANZAHL; k++) {
        PyObject *e = PyList_GetItem(liste, k);          /* geliehen */
        keep[k] = PyUnicode_AsUTF8String(e);
        if (!keep[k]) { for (int j = 0; j < k; j++) Py_DecRef(keep[j]); return NULL; }
        pf[k] = PyBytes_AsString(keep[k]);
    }
    Py_XDECREF(fn_lesen); Py_XDECREF(fn_schreiben); Py_XDECREF(fn_sektor);
    Py_IncRef(l); Py_IncRef(s); Py_IncRef(z);
    fn_lesen = l; fn_schreiben = s; fn_sektor = z;
    zt_ht_ankoppeln(&KOPPLUNG);
    Py_BEGIN_ALLOW_THREADS
    rc = zt_einschalten(pf, start);
    Py_END_ALLOW_THREADS
    for (int k = 0; k < ZT_ANZAHL; k++) Py_DecRef(keep[k]);
    if (rc != ZT_OK) { PyErr_SetString(ZtFehler, "Zusatztrommeln nicht einschaltbar (Datei nicht lesbar oder nicht beschreibbar)"); return NULL; }
    Py_RETURN_NONE;
}

static PyObject *m_ausschalten(PyObject *self, PyObject *args)
{
    (void)self; (void)args;
    Py_BEGIN_ALLOW_THREADS
    zt_ausschalten();
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *m_anwahl(PyObject *self, PyObject *args)
{
    int k;
    (void)self;
    if (!PyArg_ParseTuple(args, "i", &k)) return NULL;
    return PyLong_FromLong(zt_anwahl(k));
}

static PyObject *eingabe_ausgabe(PyObject *args, int richtung)
{
    unsigned zzz0, bbbb; int rc; zt_stat_t st;
    if (!PyArg_ParseTuple(args, "II", &zzz0, &bbbb)) return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = richtung == ZT_RICHTUNG_EINGABE ? zt_eingabe(zzz0, bbbb, &st) : zt_ausgabe(zzz0, bbbb, &st);
    Py_END_ALLOW_THREADS
    return Py_BuildValue("(iKK[IIII])", rc, st.dauer_ns, st.ticks_ht,
                         st.wartezeit_block[0], st.wartezeit_block[1], st.wartezeit_block[2], st.wartezeit_block[3]);
}
static PyObject *m_eingabe(PyObject *self, PyObject *args) { (void)self; return eingabe_ausgabe(args, ZT_RICHTUNG_EINGABE); }
static PyObject *m_ausgabe(PyObject *self, PyObject *args) { (void)self; return eingabe_ausgabe(args, ZT_RICHTUNG_AUSGABE); }

static PyObject *m_abbrechen(PyObject *self, PyObject *args) { (void)self; (void)args; zt_abbrechen(); Py_RETURN_NONE; }
static PyObject *m_gewaehlt(PyObject *self, PyObject *args) { (void)self; (void)args; return PyLong_FromLong(zt_gewaehlt()); }
static PyObject *m_semaphore_frei(PyObject *self, PyObject *args) { (void)self; (void)args; return PyBool_FromLong(zt_semaphore_frei()); }

static PyObject *m_zeitmodus(PyObject *self, PyObject *args)
{
    int m; (void)self;
    if (!PyArg_ParseTuple(args, "i", &m)) return NULL;
    zt_zeitmodus(m);
    Py_RETURN_NONE;
}
static PyObject *m_umschaltzeit(PyObject *self, PyObject *args)
{
    long long ns; (void)self;
    if (!PyArg_ParseTuple(args, "L", &ns)) return NULL;
    zt_umschaltzeit(ns);
    Py_RETURN_NONE;
}
static PyObject *m_phasen_fest(PyObject *self, PyObject *args)
{
    int an; long long pz, ph; (void)self;
    if (!PyArg_ParseTuple(args, "iLL", &an, &pz, &ph)) return NULL;
    zt_phasen_fest(an, pz, ph);
    Py_RETURN_NONE;
}
static PyObject *m_lesen(PyObject *self, PyObject *args)
{
    int k; unsigned adr; (void)self;
    if (!PyArg_ParseTuple(args, "iI", &k, &adr)) return NULL;
    return PyLong_FromUnsignedLongLong((unsigned long long)zt_lesen(k, adr));
}
static PyObject *m_schreiben(PyObject *self, PyObject *args)
{
    int k; unsigned adr; unsigned long long w; (void)self;
    if (!PyArg_ParseTuple(args, "iIK", &k, &adr, &w)) return NULL;
    return PyLong_FromLong(zt_schreiben(k, adr, (uint64_t)w));
}
static PyObject *m_letzte_adresse(PyObject *self, PyObject *args)
{
    int k; (void)self;
    if (!PyArg_ParseTuple(args, "i", &k)) return NULL;
    return PyLong_FromLong(zt_letzte_adresse(k));
}
static PyObject *m_leeren(PyObject *self, PyObject *args)
{
    (void)self; (void)args;
    Py_BEGIN_ALLOW_THREADS
    zt_leeren();
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}
static PyObject *m_modell_dauer(PyObject *self, PyObject *args)
{
    long long pz, ph, u; int richtung; zt_plan_t p; (void)self;
    if (!PyArg_ParseTuple(args, "LLLi", &pz, &ph, &u, &richtung)) return NULL;
    zt_modell_dauer(pz, ph, u, richtung, &p);
    return Py_BuildValue("(L[iiii])", p.dauer, p.folge[0], p.folge[1], p.folge[2], p.folge[3]);
}

static PyMethodDef methoden[] = {
    {"einschalten", m_einschalten, METH_VARARGS, "einschalten(pfade[4], start_index, ht_lesen, ht_schreiben, ht_aktueller_sektor): ZT-Dateien laden (fehlende anlegen), Empfaengerthread starten, Haupttrommel ankoppeln"},
    {"ausschalten", m_ausschalten, METH_NOARGS, "ausschalten(): geaenderte ZT sichern, Empfaengerthread beenden"},
    {"anwahl", m_anwahl, METH_VARARGS, "anwahl(k) -> rc: 5k00 030, k = 1..4"},
    {"gewaehlt", m_gewaehlt, METH_NOARGS, "gewaehlt() -> 0 (keine) oder 1..4"},
    {"eingabe", m_eingabe, METH_VARARGS, "eingabe(zzz0, bbbb) -> (rc, dauer_ns, ticks_ht, [wartezeit_us x 4]): 661, ZT -> HT"},
    {"ausgabe", m_ausgabe, METH_VARARGS, "ausgabe(zzz0, bbbb) -> (rc, dauer_ns, ticks_ht, [wartezeit_us x 4]): 601, HT -> ZT"},
    {"abbrechen", m_abbrechen, METH_NOARGS, "abbrechen(): weckt den wartenden Aufrufer (rc ZT_ABGEBROCHEN)"},
    {"zeitmodus", m_zeitmodus, METH_VARARGS, "zeitmodus(0 virtuell | 1 echt)"},
    {"umschaltzeit", m_umschaltzeit, METH_VARARGS, "umschaltzeit(ns)"},
    {"phasen_fest", m_phasen_fest, METH_VARARGS, "phasen_fest(an, phase_zt_ns, phase_ht_ns)"},
    {"lesen", m_lesen, METH_VARARGS, "lesen(k, adresse): Direktzugriff auf ZT k"},
    {"schreiben", m_schreiben, METH_VARARGS, "schreiben(k, adresse, wert) -> rc"},
    {"letzte_adresse", m_letzte_adresse, METH_VARARGS, "letzte_adresse(k) -> zuletzt bearbeitete Adresse (Spur*32+Sektor) der ZT k oder -1"},
    {"leeren", m_leeren, METH_NOARGS, "leeren(): alle ZT leeren, Anwahl aufheben"},
    {"semaphore_frei", m_semaphore_frei, METH_NOARGS, "semaphore_frei() -> bool"},
    {"modell_dauer", m_modell_dauer, METH_VARARGS, "modell_dauer(phase_zt_ns, phase_ht_ns, umschalt_ns, richtung) -> (dauer_ns, blockfolge)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef modul = {
    PyModuleDef_HEAD_INIT, "c8205_ztmodul", "C 8205Z: Zusatztrommeln mit Zeitmodell (zt_modul.c statisch eingebunden).", -1, methoden,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit_c8205_ztmodul(void)
{
    PyObject *m = PyModule_Create(&modul);
    if (!m) return NULL;
    ZtFehler = PyErr_NewException("c8205_ztmodul.ZtFehler", PyExc_Exception, NULL);
    if (!ZtFehler) { Py_DecRef(m); return NULL; }
    Py_IncRef(ZtFehler);
    if (PyModule_AddObject(m, "ZtFehler", ZtFehler) < 0) { Py_DecRef(m); return NULL; }
    PyModule_AddIntConstant(m, "ZT_OK", ZT_OK);
    PyModule_AddIntConstant(m, "ZT_KEINE_ANWAHL", ZT_KEINE_ANWAHL);
    PyModule_AddIntConstant(m, "ZT_ABGEBROCHEN", ZT_ABGEBROCHEN);
    PyModule_AddIntConstant(m, "ZT_FEHLER", ZT_FEHLER);
    return m;
}
