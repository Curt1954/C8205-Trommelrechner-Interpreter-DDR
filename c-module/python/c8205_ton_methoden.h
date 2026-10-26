/* c8205_ton_methoden.h - Python-Methoden des Tonmischers (tonmisch.c), eingebunden in c8205_trommel_modul.c:
 * EIN Erweiterungsmodul (eine .so/.pyd) fuer Trommel und Tonmischer (GRAFIK_Beschreibung Abschnitt 6 (alt: Dok. 10) S4-02).
 * Der Mischer ist eine Instanz; Python haelt sie als Kapsel (PyCapsule), die beim Freigeben tm_frei() ruft.
 * Der Mischer ruft nie in Python zurueck (keine GIL im Mischer-Thread): Zeitgeber ueber ton_warte_takt, Ausfall ueber ton_ausfall.
 * Blockierende Aufrufe (ton_warte_takt, ton_schliessen, ton_schritt) geben die GIL frei.
 * Nur Limited API (abi3). Die Aufrufer sind grafik_tonmisch_c.py und die Pruefungen. */
#ifndef C8205_TON_METHODEN_H
#define C8205_TON_METHODEN_H
#include "../tonmisch.h"

static PyObject *TonFehler;
#define TON_KAPSEL "c8205_trommel.tonmisch"

static void ton_kapsel_frei(PyObject *cap)
{
    tm_t *t = (tm_t *)PyCapsule_GetPointer(cap, TON_KAPSEL);
    if (t) {
        Py_BEGIN_ALLOW_THREADS
        tm_frei(t);
        Py_END_ALLOW_THREADS
    }
}

static tm_t *ton_holen(PyObject *cap)
{
    tm_t *t = (tm_t *)PyCapsule_GetPointer(cap, TON_KAPSEL);
    if (!t && !PyErr_Occurred()) PyErr_SetString(TonFehler, "ungueltiger Mischer");
    return t;
}

static PyObject *ton_rc(int rc, const char *was)
{
    if (rc == TM_OK) Py_RETURN_NONE;
    PyErr_Format(TonFehler, "%s: %s", was, rc == TM_VOLL ? "keine freie Stimme" : rc == TM_AUSFALL ? "Senke ausgefallen" : "Fehler");
    return NULL;
}

static PyObject *m_ton_neu(PyObject *self, PyObject *args)
{
    tm_t *t;
    (void)self; (void)args;
    t = tm_neu();
    if (!t) return PyErr_NoMemory();
    return PyCapsule_New(t, TON_KAPSEL, ton_kapsel_frei);
}

static PyObject *m_ton_klang(PyObject *self, PyObject *args)
{
    PyObject *cap; const char *d; Py_ssize_t n; int id; tm_t *t;
    (void)self;
    if (!PyArg_ParseTuple(args, "Oy#", &cap, &d, &n)) return NULL;
    if (!(t = ton_holen(cap))) return NULL;
    if (n % 2) { PyErr_SetString(TonFehler, "Klang: ungerade Byteanzahl"); return NULL; }
    id = tm_klang(t, (const int16_t *)(const void *)d, (size_t)(n / 2));   /* Reihenfolge des Rechners (array('h').tobytes()) */
    if (id < 0) { PyErr_SetString(TonFehler, "Klang konnte nicht angelegt werden (Speicher oder zu viele Klaenge)"); return NULL; }
    return PyLong_FromLong(id);
}

/* ton_senke(h, art, arg=None): 'speicher' | 'keine' | 'datei' (arg Pfad) | 'prozess' (arg Folge von Zeichenketten) | 'winmm' */
static PyObject *m_ton_senke(PyObject *self, PyObject *args)
{
    PyObject *cap, *arg = Py_None; const char *art; tm_t *t; int rc = TM_FEHLER;
    (void)self;
    if (!PyArg_ParseTuple(args, "Os|O", &cap, &art, &arg)) return NULL;
    if (!(t = ton_holen(cap))) return NULL;
    if (strcmp(art, "keine") == 0) rc = TM_OK;
    else if (strcmp(art, "speicher") == 0) rc = tm_senke_speicher(t);
    else if (strcmp(art, "winmm") == 0) rc = tm_senke_winmm(t);
    else if (strcmp(art, "datei") == 0) {
        PyObject *b; const char *p;
        if (!PyUnicode_Check(arg)) { PyErr_SetString(PyExc_TypeError, "datei: Pfad erwartet"); return NULL; }
        b = PyUnicode_AsUTF8String(arg);
        if (!b) return NULL;
        p = PyBytes_AsString(b);
        rc = p ? tm_senke_datei(t, p) : TM_FEHLER;
        Py_DecRef(b);
    } else if (strcmp(art, "prozess") == 0) {
        Py_ssize_t i, n; char **argv; PyObject **teile;
        if (!PyList_Check(arg) && !PyTuple_Check(arg)) { PyErr_SetString(PyExc_TypeError, "prozess: Liste von Zeichenketten erwartet"); return NULL; }
        n = PySequence_Size(arg);
        if (n < 1) { PyErr_SetString(PyExc_ValueError, "prozess: leerer Befehl"); return NULL; }
        argv = (char **)calloc((size_t)n + 1, sizeof(char *));
        teile = (PyObject **)calloc((size_t)n, sizeof(PyObject *));
        if (!argv || !teile) { free(argv); free(teile); return PyErr_NoMemory(); }
        for (i = 0; i < n; i++) {
            PyObject *it = PySequence_GetItem(arg, i), *b = it && PyUnicode_Check(it) ? PyUnicode_AsUTF8String(it) : NULL;
            Py_DecRef(it);
            if (!b) {
                Py_ssize_t j;
                for (j = 0; j < i; j++) Py_DecRef(teile[j]);
                free(argv); free(teile);
                if (!PyErr_Occurred()) PyErr_SetString(PyExc_TypeError, "prozess: nur Zeichenketten");
                return NULL;
            }
            teile[i] = b; argv[i] = PyBytes_AsString(b);
        }
        rc = tm_senke_prozess(t, argv);
        for (i = 0; i < n; i++) Py_DecRef(teile[i]);
        free(argv); free(teile);
    }
    return ton_rc(rc, art);
}

static PyObject *m_ton_starten(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    return ton_rc(tm_starten(t), "starten");
}

static PyObject *m_ton_vorlauf(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int n; (void)self;
    if (!PyArg_ParseTuple(args, "Oi", &cap, &n) || !(t = ton_holen(cap))) return NULL;
    return ton_rc(tm_vorlauf(t, n), "vorlauf");
}

static PyObject *m_ton_schritt(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int n, rc; (void)self;
    if (!PyArg_ParseTuple(args, "Oi", &cap, &n) || !(t = ton_holen(cap))) return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = tm_schritt(t, n);
    Py_END_ALLOW_THREADS
    return ton_rc(rc, "schritt");
}

static PyObject *m_ton_block(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int16_t b[TM_BLOCK]; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    tm_block(t, b);
    return PyBytes_FromStringAndSize((const char *)b, TM_BLOCK_BYTE);          /* Reihenfolge des Rechners wie array('h') */
}

static PyObject *m_ton_schliessen(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    Py_BEGIN_ALLOW_THREADS
    tm_schliessen(t);
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject *m_ton_einzel(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int kanal, klang; double pegel; const char *key = NULL; (void)self;
    if (!PyArg_ParseTuple(args, "Oiidz", &cap, &kanal, &klang, &pegel, &key) || !(t = ton_holen(cap))) return NULL;
    return PyLong_FromLong(tm_einzel(t, kanal, klang, pegel, key));      /* 0 = ok, -1 = falscher Aufruf, -2 = keine freie Stimme */
}

static PyObject *m_ton_dauer_an(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int kanal, klang; double pegel; const char *key; (void)self;
    if (!PyArg_ParseTuple(args, "Oisid", &cap, &kanal, &key, &klang, &pegel) || !(t = ton_holen(cap))) return NULL;
    return PyLong_FromLong(tm_dauer_an(t, kanal, key, klang, pegel));    /* 0 = ok, -1 = falscher Aufruf, -2 = keine freie Stimme */
}

static PyObject *m_ton_dauer_pegel(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; const char *key; double pegel; (void)self;
    if (!PyArg_ParseTuple(args, "Osd", &cap, &key, &pegel) || !(t = ton_holen(cap))) return NULL;
    tm_dauer_pegel(t, key, pegel);
    Py_RETURN_NONE;
}

static PyObject *m_ton_dauer_aus(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; const char *key; (void)self;
    if (!PyArg_ParseTuple(args, "Os", &cap, &key) || !(t = ton_holen(cap))) return NULL;
    tm_dauer_aus(t, key);
    Py_RETURN_NONE;
}

static PyObject *m_ton_tor(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; int kanal, offen; (void)self;
    if (!PyArg_ParseTuple(args, "Oii", &cap, &kanal, &offen) || !(t = ton_holen(cap))) return NULL;
    tm_tor(t, kanal, offen);
    Py_RETURN_NONE;
}

static PyObject *m_ton_alles_aus(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    tm_alles_aus(t);
    Py_RETURN_NONE;
}

static PyObject *m_ton_klingt(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    return PyLong_FromLong(tm_klingt(t));
}

static PyObject *m_ton_klingt_schluessel(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; const char *key; (void)self;
    if (!PyArg_ParseTuple(args, "Os", &cap, &key) || !(t = ton_holen(cap))) return NULL;
    return PyLong_FromLong(tm_klingt_schluessel(t, key));
}

static PyObject *m_ton_bloecke(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    return PyLong_FromUnsignedLong(tm_bloecke(t));
}

static PyObject *m_ton_warte_takt(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; unsigned long zuletzt, n; unsigned ms; (void)self;
    if (!PyArg_ParseTuple(args, "OkI", &cap, &zuletzt, &ms) || !(t = ton_holen(cap))) return NULL;
    Py_BEGIN_ALLOW_THREADS
    n = tm_warte_takt(t, zuletzt, ms);
    Py_END_ALLOW_THREADS
    return PyLong_FromUnsignedLong(n);
}

static PyObject *m_ton_ausfall(PyObject *self, PyObject *args)
{
    PyObject *cap; tm_t *t; char text[200]; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    if (!tm_ausfall(t, text, sizeof text)) Py_RETURN_NONE;
    return PyUnicode_FromString(text);
}

static PyObject *m_ton_speicher(PyObject *self, PyObject *args)
{
    PyObject *cap, *r; tm_t *t; size_t n; (void)self;
    if (!PyArg_ParseTuple(args, "O", &cap) || !(t = ton_holen(cap))) return NULL;
    n = tm_speicher_laenge(t);
    r = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)n);
    if (!r) return NULL;
    tm_speicher_kopie(t, (uint8_t *)PyBytes_AsString(r), n);
    return r;
}

#define TON_M(name, fn, doc) {name, fn, METH_VARARGS, doc}
#define TON_METHODEN \
    TON_M("ton_neu", m_ton_neu, "ton_neu() -> Mischer (Kapsel)"), \
    TON_M("ton_klang", m_ton_klang, "ton_klang(h, daten) -> Klangnummer; daten: bytes aus array('h').tobytes() (mono, 16 bit)"), \
    TON_M("ton_senke", m_ton_senke, "ton_senke(h, art, arg=None): 'speicher' | 'keine' | 'datei' (Pfad) | 'prozess' (Liste) | 'winmm'"), \
    TON_M("ton_vorlauf", m_ton_vorlauf, "ton_vorlauf(h, bloecke): Vorlauf vor der Uhr in Bloecken zu 10 ms (1 bis 3, Standard 2), vor ton_starten"), \
    TON_M("ton_starten", m_ton_starten, "ton_starten(h): Thread starten (Takt der Uhr)"), \
    TON_M("ton_schritt", m_ton_schritt, "ton_schritt(h, n): n Bloecke ohne Thread erzeugen und senden"), \
    TON_M("ton_block", m_ton_block, "ton_block(h) -> bytes: einen Block mischen, ohne Senke"), \
    TON_M("ton_schliessen", m_ton_schliessen, "ton_schliessen(h): Thread beenden, Senke schliessen, Stimmen verwerfen"), \
    TON_M("ton_einzel", m_ton_einzel, "ton_einzel(h, kanal, klang, pegel, schluessel) -> 0 | -1 (falscher Aufruf) | -2 (keine freie Stimme)"), \
    TON_M("ton_dauer_an", m_ton_dauer_an, "ton_dauer_an(h, kanal, schluessel, klang, pegel) -> 0 | -1 | -2"), \
    TON_M("ton_dauer_pegel", m_ton_dauer_pegel, "ton_dauer_pegel(h, schluessel, pegel)"), \
    TON_M("ton_dauer_aus", m_ton_dauer_aus, "ton_dauer_aus(h, schluessel)"), \
    TON_M("ton_tor", m_ton_tor, "ton_tor(h, kanal, offen)"), \
    TON_M("ton_alles_aus", m_ton_alles_aus, "ton_alles_aus(h)"), \
    TON_M("ton_klingt", m_ton_klingt, "ton_klingt(h) -> Zahl der Stimmen"), \
    TON_M("ton_klingt_schluessel", m_ton_klingt_schluessel, "ton_klingt_schluessel(h, schluessel) -> Zahl"), \
    TON_M("ton_bloecke", m_ton_bloecke, "ton_bloecke(h) -> gesendete Bloecke"), \
    TON_M("ton_warte_takt", m_ton_warte_takt, "ton_warte_takt(h, zuletzt, ms) -> Blockzahl (wartet, solange sie gleich zuletzt ist; gibt die GIL frei)"), \
    TON_M("ton_ausfall", m_ton_ausfall, "ton_ausfall(h) -> Text oder None"), \
    TON_M("ton_speicher", m_ton_speicher, "ton_speicher(h) -> bytes der Speichersenke")
#endif
