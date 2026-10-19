/* tonmisch.c - Tonmischer fuer den Modus GRAFIK (Stufe 4, GRAFIK_Beschreibung Abschnitt 6 (alt: Dok. 10) S4-01 bis S4-03, S4-12).  Siehe tonmisch.h.
 * Eine Uebersetzungseinheit; die Plattformschicht kommt aus plattform.h (Mutex, Bedingung, Thread, Uhr).
 * Linux: gebaut und geprueft.  Windows (winmm): nach der Win32-Dokumentation geschrieben, NICHT uebersetzt, NICHT getestet. */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "plattform.h"
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
#include "tonmisch.h"

#ifndef _WIN32
#include <fcntl.h>
#include <signal.h>
#include <spawn.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
extern char **environ;
#endif

#define MAX_STIMMEN 128
#define MAX_KLAENGE 4096
#define TEXT_LEN    160
#define BLOCK_NS    10000000ULL               /* 441 Samples bei 44100 Hz = genau 10 ms */

enum { SENKE_KEINE = 0, SENKE_PROZESS, SENKE_WINMM, SENKE_DATEI, SENKE_SPEICHER };

typedef struct { int16_t *d; size_t n; } klang_t;
typedef struct {
    int    kanal, klang, schleife;
    size_t pos;
    double pegel;
    char   key[TM_SCHLUESSEL];
} stimme_t;

struct tonmisch {
    pf_mutex_t lock;                           /* schuetzt Klaenge, Stimmen, Tore */
    klang_t   *klaenge; int n_klaenge, cap_klaenge;
    stimme_t   st[MAX_STIMMEN]; int n_st;
    int        tor[TM_KANAELE];

    int        art;                            /* Senke */
    char       name[64];                       /* Name des Abspielprogramms (Meldungen) */
    int        fd;
#ifndef _WIN32
    pid_t      pid;
#else
    HWAVEOUT   wo; WAVEHDR hdr[TM_RING]; int16_t wbuf[TM_RING][TM_BLOCK]; int wnext;
#endif
    uint8_t   *mem; size_t mem_n, mem_cap;

    pf_thread_t thread; int thread_laeuft;
    pf_flag_t  stop;
    int        vorlauf;                        /* Bloecke Vorlauf vor der Uhr */
    int        geschlossen;

    pf_mutex_t tlock; pf_cond_t tcond;         /* Takt und Ausfall */
    unsigned long bloecke; int ausfall; int beendet; char text[TEXT_LEN];
};

/* ------------------------------------------------------------------ Hilfen */
static void schluessel_kopie(char *ziel, const char *s)
{
    size_t n = 0;
    if (s) { n = strlen(s); if (n >= TM_SCHLUESSEL) n = TM_SCHLUESSEL - 1; memcpy(ziel, s, n); }
    ziel[n] = 0;
}

static void melde_ausfall(tm_t *t, const char *fmt, ...)
{
    va_list ap;
    pf_mutex_lock(&t->tlock);
    if (!t->ausfall) {
        va_start(ap, fmt); vsnprintf(t->text, sizeof t->text, fmt, ap); va_end(ap);
        t->ausfall = 1;
    }
    pf_cond_broadcast(&t->tcond);
    pf_mutex_unlock(&t->tlock);
}

/* entfernt Stimme i (Reihenfolge ist unerheblich) -- unter Sperre */
static void stimme_weg(tm_t *t, int i) { t->st[i] = t->st[--t->n_st]; }

static int stimme_neu(tm_t *t, int kanal, int klang, int schleife, double pegel, const char *key)
{
    stimme_t *s;
    if (t->n_st >= MAX_STIMMEN) return TM_VOLL;
    s = &t->st[t->n_st++];
    s->kanal = kanal; s->klang = klang; s->schleife = schleife; s->pos = 0; s->pegel = pegel;
    schluessel_kopie(s->key, key);
    return TM_OK;
}

static void stimmen_mit_schluessel_weg(tm_t *t, const char *key)
{
    int i;
    for (i = 0; i < t->n_st; ) {
        if (strcmp(t->st[i].key, key) == 0) stimme_weg(t, i); else i++;
    }
}

static int kanal_ok(int kanal) { return kanal >= 0 && kanal < TM_KANAELE; }

/* ------------------------------------------------------------------ Lebenslauf */
tm_t *tm_neu(void)
{
    tm_t *t = (tm_t *)calloc(1, sizeof *t);
    int k;
    if (!t) return NULL;
    pf_mutex_init(&t->lock);
    pf_mutex_init(&t->tlock);
    pf_cond_init(&t->tcond);
    for (k = 0; k < TM_KANAELE; k++) t->tor[k] = 1;
    t->fd = -1;
    t->vorlauf = TM_VORLAUF;
#ifndef _WIN32
    t->pid = -1;
#endif
    return t;
}

int tm_klang(tm_t *t, const int16_t *daten, size_t anzahl)
{
    int16_t *kopie;
    if (!t || (!daten && anzahl)) return TM_FEHLER;
    kopie = (int16_t *)malloc((anzahl ? anzahl : 1) * sizeof(int16_t));
    if (!kopie) return TM_FEHLER;
    if (anzahl) memcpy(kopie, daten, anzahl * sizeof(int16_t));
    pf_mutex_lock(&t->lock);
    if (t->n_klaenge >= MAX_KLAENGE) { pf_mutex_unlock(&t->lock); free(kopie); return TM_FEHLER; }
    if (t->n_klaenge >= t->cap_klaenge) {
        int neu = t->cap_klaenge ? t->cap_klaenge * 2 : 64;
        klang_t *p = (klang_t *)realloc(t->klaenge, (size_t)neu * sizeof(klang_t));
        if (!p) { pf_mutex_unlock(&t->lock); free(kopie); return TM_FEHLER; }
        t->klaenge = p; t->cap_klaenge = neu;
    }
    t->klaenge[t->n_klaenge].d = kopie;
    t->klaenge[t->n_klaenge].n = anzahl;
    t->n_klaenge++;
    pf_mutex_unlock(&t->lock);
    return t->n_klaenge - 1;
}

/* ------------------------------------------------------------------ Mischen */
void tm_block(tm_t *t, int16_t *ziel)
{
    int32_t acc[TM_BLOCK];
    int i, j, behalten = 0;
    memset(acc, 0, sizeof acc);
    pf_mutex_lock(&t->lock);
    for (i = 0; i < t->n_st; i++) {
        stimme_t *s = &t->st[i];
        const klang_t *k = &t->klaenge[s->klang];
        const int16_t *d = k->d;
        size_t n = k->n, idx = s->pos;
        double g = s->pegel;
        if (n == 0) continue;                                  /* leerer Klang: Stimme faellt weg */
        if (s->schleife) {
            for (j = 0; j < TM_BLOCK; j++) {
                int32_t v = d[idx];
                if (++idx >= n) idx = 0;
                if (g == 1.0) acc[j] += v; else if (g > 0.0) acc[j] += (int32_t)(v * g);
            }
            s->pos = idx;                                      /* = (pos + BLOCK) mod n */
            t->st[behalten++] = *s;
        } else {
            size_t rest = n - idx, m = rest < TM_BLOCK ? rest : TM_BLOCK;
            for (j = 0; j < (int)m; j++) {
                int32_t v = d[idx + (size_t)j];
                if (g == 1.0) acc[j] += v; else if (g > 0.0) acc[j] += (int32_t)(v * g);
            }
            s->pos = idx + TM_BLOCK;
            if (s->pos < n) t->st[behalten++] = *s;
        }
    }
    t->n_st = behalten;
    pf_mutex_unlock(&t->lock);
    for (j = 0; j < TM_BLOCK; j++) ziel[j] = (int16_t)(acc[j] > 32767 ? 32767 : (acc[j] < -32768 ? -32768 : acc[j]));
}

/* ------------------------------------------------------------------ Ereignisse */
int tm_einzel(tm_t *t, int kanal, int klang, double pegel, const char *schluessel)
{
    int rc = TM_OK;
    if (!t || !kanal_ok(kanal)) return TM_FEHLER;
    pf_mutex_lock(&t->lock);
    if (klang < 0 || klang >= t->n_klaenge) rc = TM_FEHLER;
    else if (t->tor[kanal]) rc = stimme_neu(t, kanal, klang, 0, pegel, schluessel);   /* Tor zu: verworfen */
    pf_mutex_unlock(&t->lock);
    return rc;
}

int tm_dauer_an(tm_t *t, int kanal, const char *schluessel, int klang, double pegel)
{
    int rc = TM_OK;
    if (!t || !kanal_ok(kanal) || !schluessel || !schluessel[0]) return TM_FEHLER;
    pf_mutex_lock(&t->lock);
    if (klang < 0 || klang >= t->n_klaenge) rc = TM_FEHLER;
    else {
        char key[TM_SCHLUESSEL];
        schluessel_kopie(key, schluessel);
        stimmen_mit_schluessel_weg(t, key);                    /* ein zweites mit demselben Schluessel ersetzt das erste */
        if (t->tor[kanal]) rc = stimme_neu(t, kanal, klang, 1, pegel, key);
    }
    pf_mutex_unlock(&t->lock);
    return rc;
}

void tm_dauer_pegel(tm_t *t, const char *schluessel, double pegel)
{
    int i;
    char key[TM_SCHLUESSEL];
    if (!t || !schluessel || !schluessel[0]) return;
    schluessel_kopie(key, schluessel);
    pf_mutex_lock(&t->lock);
    for (i = 0; i < t->n_st; i++) if (strcmp(t->st[i].key, key) == 0) t->st[i].pegel = pegel;
    pf_mutex_unlock(&t->lock);
}

void tm_dauer_aus(tm_t *t, const char *schluessel)
{
    char key[TM_SCHLUESSEL];
    if (!t || !schluessel || !schluessel[0]) return;
    schluessel_kopie(key, schluessel);
    pf_mutex_lock(&t->lock);
    stimmen_mit_schluessel_weg(t, key);
    pf_mutex_unlock(&t->lock);
}

void tm_tor(tm_t *t, int kanal, int offen)
{
    int i;
    if (!t || !kanal_ok(kanal)) return;
    pf_mutex_lock(&t->lock);
    t->tor[kanal] = offen ? 1 : 0;
    if (!offen) for (i = 0; i < t->n_st; ) { if (t->st[i].kanal == kanal) stimme_weg(t, i); else i++; }
    pf_mutex_unlock(&t->lock);
}

void tm_alles_aus(tm_t *t)
{
    if (!t) return;
    pf_mutex_lock(&t->lock);
    t->n_st = 0;
    pf_mutex_unlock(&t->lock);
}

int tm_klingt(tm_t *t)
{
    int n;
    pf_mutex_lock(&t->lock); n = t->n_st; pf_mutex_unlock(&t->lock);
    return n;
}

int tm_klingt_schluessel(tm_t *t, const char *schluessel)
{
    int i, n = 0;
    char key[TM_SCHLUESSEL];
    schluessel_kopie(key, schluessel);
    pf_mutex_lock(&t->lock);
    for (i = 0; i < t->n_st; i++) if (strcmp(t->st[i].key, key) == 0) n++;
    pf_mutex_unlock(&t->lock);
    return n;
}

/* ------------------------------------------------------------------ Senken */
static int senke_gewaehlt(tm_t *t) { return t->art != SENKE_KEINE || t->geschlossen; }

int tm_senke_speicher(tm_t *t)
{
    if (!t || senke_gewaehlt(t)) return TM_FEHLER;
    t->art = SENKE_SPEICHER;
    return TM_OK;
}

size_t tm_speicher_laenge(tm_t *t) { return t ? t->mem_n : 0; }

size_t tm_speicher_kopie(tm_t *t, uint8_t *ziel, size_t kapazitaet)
{
    size_t n;
    if (!t || !ziel) return 0;
    n = t->mem_n < kapazitaet ? t->mem_n : kapazitaet;
    if (n) memcpy(ziel, t->mem, n);
    return n;
}

int tm_senke_datei(tm_t *t, const char *pfad)
{
    if (!t || !pfad || senke_gewaehlt(t)) return TM_FEHLER;
#ifdef _WIN32
    return TM_FEHLER;                                                  /* Windows: keine Datei-Senke (nur winmm) */
#else
    t->fd = open(pfad, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (t->fd < 0) return TM_FEHLER;
    t->art = SENKE_DATEI;
    return TM_OK;
#endif
}

#ifndef _WIN32
int tm_senke_prozess(tm_t *t, char *const argv[])
{
    int fd[2];
    posix_spawn_file_actions_t fa;
    struct sigaction sa;
    int rc;
    if (!t || !argv || !argv[0] || senke_gewaehlt(t)) return TM_FEHLER;
    if (sigaction(SIGPIPE, NULL, &sa) == 0 && sa.sa_handler == SIG_DFL) {   /* ein weggebrochenes Abspielprogramm soll uns nicht toeten */
        sa.sa_handler = SIG_IGN; sigemptyset(&sa.sa_mask); sa.sa_flags = 0;
        sigaction(SIGPIPE, &sa, NULL);
    }
    if (pipe2(fd, O_CLOEXEC) != 0) return TM_FEHLER;
    if (posix_spawn_file_actions_init(&fa) != 0) { close(fd[0]); close(fd[1]); return TM_FEHLER; }
    posix_spawn_file_actions_adddup2(&fa, fd[0], 0);                      /* Standardeingabe = Leseende der Roehre */
    posix_spawn_file_actions_addopen(&fa, 1, "/dev/null", O_WRONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 2, "/dev/null", O_WRONLY, 0);
    rc = posix_spawnp(&t->pid, argv[0], &fa, NULL, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    close(fd[0]);
    if (rc != 0) { close(fd[1]); t->pid = -1; return TM_FEHLER; }
    t->fd = fd[1];
    snprintf(t->name, sizeof t->name, "%s", argv[0]);
    t->art = SENKE_PROZESS;
    return TM_OK;
}
#else
int tm_senke_prozess(tm_t *t, char *const argv[]) { (void)t; (void)argv; return TM_FEHLER; }
#endif

#ifdef _WIN32
int tm_senke_winmm(tm_t *t)
{
    WAVEFORMATEX f;
    int i;
    if (!t || senke_gewaehlt(t)) return TM_FEHLER;
    memset(&f, 0, sizeof f);
    f.wFormatTag = WAVE_FORMAT_PCM; f.nChannels = 1; f.nSamplesPerSec = TM_RATE; f.wBitsPerSample = 16;
    f.nBlockAlign = 2; f.nAvgBytesPerSec = TM_RATE * 2;
    if (waveOutOpen(&t->wo, WAVE_MAPPER, &f, 0, 0, CALLBACK_NULL) != MMSYSERR_NOERROR) return TM_FEHLER;
    for (i = 0; i < TM_RING; i++) {
        memset(&t->hdr[i], 0, sizeof t->hdr[i]);
        t->hdr[i].lpData = (LPSTR)t->wbuf[i]; t->hdr[i].dwBufferLength = TM_BLOCK_BYTE;
        if (waveOutPrepareHeader(t->wo, &t->hdr[i], sizeof t->hdr[i]) != MMSYSERR_NOERROR) { waveOutClose(t->wo); return TM_FEHLER; }
        t->hdr[i].dwFlags |= WHDR_DONE;                                   /* Puffer frei */
    }
    t->wnext = 0;
    snprintf(t->name, sizeof t->name, "winmm");
    t->art = SENKE_WINMM;
    return TM_OK;
}
#else
int tm_senke_winmm(tm_t *t) { (void)t; return TM_FEHLER; }
#endif

/* Block (little endian, 882 Byte) an die Senke; bei Fehler Ausfall melden */
static int senke_schreibe(tm_t *t, const uint8_t *b)
{
    switch (t->art) {
#ifndef _WIN32
    case SENKE_PROZESS: case SENKE_DATEI: {
        size_t off = 0;
        while (off < TM_BLOCK_BYTE) {
            ssize_t w = write(t->fd, b + off, TM_BLOCK_BYTE - off);
            if (w < 0) {
                if (errno == EINTR) continue;
                melde_ausfall(t, "%s: Schreiben fehlgeschlagen (%s)", t->art == SENKE_PROZESS ? t->name : "Datei", strerror(errno));
                return -1;
            }
            off += (size_t)w;
        }
        if (t->art == SENKE_PROZESS && t->pid > 0) {
            int st = 0;
            if (waitpid(t->pid, &st, WNOHANG) == t->pid) {
                t->pid = -1;
                melde_ausfall(t, "%s beendet (Code %d)", t->name, WIFEXITED(st) ? WEXITSTATUS(st) : 128 + WTERMSIG(st));
                return -1;
            }
        }
        return 0;
    }
#else
    case SENKE_WINMM: {
        int i = t->wnext, warte = 0;
        while (!(t->hdr[i].dwFlags & WHDR_DONE)) {
            Sleep(1);
            if (++warte > 500) { melde_ausfall(t, "winmm: Puffer wird nicht frei"); return -1; }
        }
        memcpy(t->wbuf[i], b, TM_BLOCK_BYTE);                          /* little endian = Windows-Reihenfolge */
        t->hdr[i].dwFlags &= ~(DWORD)WHDR_DONE;
        if (waveOutWrite(t->wo, &t->hdr[i], sizeof t->hdr[i]) != MMSYSERR_NOERROR) { melde_ausfall(t, "winmm: waveOutWrite fehlgeschlagen"); return -1; }
        t->wnext = (i + 1) % TM_RING;
        return 0;
    }
#endif
    case SENKE_SPEICHER:
        if (t->mem_n + TM_BLOCK_BYTE > t->mem_cap) {
            size_t neu = t->mem_cap ? t->mem_cap * 2 : 65536;
            uint8_t *p;
            if (neu > TM_SPEICHER_MAX) neu = TM_SPEICHER_MAX;
            if (t->mem_n + TM_BLOCK_BYTE > neu || !(p = (uint8_t *)realloc(t->mem, neu))) { melde_ausfall(t, "Speichersenke voll"); return -1; }
            t->mem = p; t->mem_cap = neu;
        }
        memcpy(t->mem + t->mem_n, b, TM_BLOCK_BYTE);
        t->mem_n += TM_BLOCK_BYTE;
        return 0;
    default:
        return 0;                                                      /* keine Senke: verwerfen */
    }
}

/* einen Block erzeugen, senden, zaehlen */
static int erzeuge_block(tm_t *t)
{
    int16_t blk[TM_BLOCK];
    uint8_t b[TM_BLOCK_BYTE];
    int j;
    tm_block(t, blk);
    for (j = 0; j < TM_BLOCK; j++) { b[2 * j] = (uint8_t)(blk[j] & 0xFF); b[2 * j + 1] = (uint8_t)((blk[j] >> 8) & 0xFF); }
    if (senke_schreibe(t, b) != 0) return TM_AUSFALL;
    pf_mutex_lock(&t->tlock);
    t->bloecke++;
    pf_cond_broadcast(&t->tcond);
    pf_mutex_unlock(&t->tlock);
    return TM_OK;
}

/* ------------------------------------------------------------------ Strom */
PF_THREAD_FUNC(tm_lauf)
{
    tm_t *t = (tm_t *)arg;
    uint64_t t0 = pf_zeit_ns();
    unsigned long n = 0;
    while (!pf_flag_lese(&t->stop)) {
        if (erzeuge_block(t) != TM_OK) break;
        n++;
        if (n > (unsigned long)t->vorlauf) {                           /* nie weiter als t->vorlauf Bloecke vor der Uhr (S4-03) */
            uint64_t ziel = t0 + (uint64_t)(n - (unsigned long)t->vorlauf) * BLOCK_NS;
            while (!pf_flag_lese(&t->stop) && pf_zeit_ns() < ziel) pf_schlafe_bis(ziel, 0);
        }
    }
    PF_THREAD_ENDE;
}

int tm_vorlauf(tm_t *t, int bloecke)
{
    if (!t || t->thread_laeuft || bloecke < 1 || bloecke > TM_VORLAUF_MAX) return TM_FEHLER;
    t->vorlauf = bloecke;
    return TM_OK;
}

int tm_starten(tm_t *t)
{
    if (!t || t->geschlossen || t->thread_laeuft) return TM_FEHLER;
    pf_zeit_start();
    pf_flag_setze(&t->stop, 0);
    if (pf_thread_start(&t->thread, tm_lauf, t) != 0) return TM_FEHLER;
    t->thread_laeuft = 1;
    return TM_OK;
}

int tm_schritt(tm_t *t, int bloecke)
{
    int i;
    if (!t || t->geschlossen || t->thread_laeuft) return TM_FEHLER;
    for (i = 0; i < bloecke; i++) if (erzeuge_block(t) != TM_OK) return TM_AUSFALL;
    return TM_OK;
}

void tm_schliessen(tm_t *t)
{
    if (!t || t->geschlossen) return;
    t->geschlossen = 1;
    pf_flag_setze(&t->stop, 1);
    pf_mutex_lock(&t->tlock);
    t->beendet = 1;
    pf_cond_broadcast(&t->tcond);                                      /* wartende tm_warte_takt freigeben */
    pf_mutex_unlock(&t->tlock);
#ifndef _WIN32
    if (t->art == SENKE_PROZESS && t->pid > 0) kill(t->pid, SIGTERM);  /* ein in write() haengender Strom kommt so frei */
#endif
    if (t->thread_laeuft) { pf_thread_join(&t->thread); t->thread_laeuft = 0; }
#ifndef _WIN32
    if (t->fd >= 0) { close(t->fd); t->fd = -1; }
    if (t->art == SENKE_PROZESS && t->pid > 0) {
        int st = 0, i, fertig = 0;
        for (i = 0; i < 100 && !fertig; i++) {                         /* bis 0,5 s warten, dann hart beenden */
            if (waitpid(t->pid, &st, WNOHANG) == t->pid) fertig = 1; else { struct timespec ts = {0, 5000000L}; nanosleep(&ts, NULL); }
        }
        if (!fertig) { kill(t->pid, SIGKILL); waitpid(t->pid, &st, 0); }
        t->pid = -1;
    }
#else
    if (t->art == SENKE_WINMM) {
        int i;
        waveOutReset(t->wo);
        for (i = 0; i < TM_RING; i++) waveOutUnprepareHeader(t->wo, &t->hdr[i], sizeof t->hdr[i]);
        waveOutClose(t->wo);
    }
#endif
    pf_mutex_lock(&t->lock);
    t->n_st = 0;
    pf_mutex_unlock(&t->lock);
}

void tm_frei(tm_t *t)
{
    int i;
    if (!t) return;
    tm_schliessen(t);
    for (i = 0; i < t->n_klaenge; i++) free(t->klaenge[i].d);
    free(t->klaenge);
    free(t->mem);
    free(t);
}

/* ------------------------------------------------------------------ Takt und Ausfall */
unsigned long tm_bloecke(tm_t *t)
{
    unsigned long n;
    pf_mutex_lock(&t->tlock); n = t->bloecke; pf_mutex_unlock(&t->tlock);
    return n;
}

unsigned long tm_warte_takt(tm_t *t, unsigned long zuletzt, unsigned ms)
{
    unsigned long n;
    pf_mutex_lock(&t->tlock);
    if (t->bloecke == zuletzt && !t->ausfall && !t->beendet) pf_cond_wait_ms(&t->tcond, &t->tlock, ms);
    n = t->bloecke;
    pf_mutex_unlock(&t->tlock);
    return n;
}

int tm_ausfall(tm_t *t, char *text, size_t kapazitaet)
{
    int a;
    pf_mutex_lock(&t->tlock);
    a = t->ausfall;
    if (a && text && kapazitaet) snprintf(text, kapazitaet, "%s", t->text);
    pf_mutex_unlock(&t->tlock);
    return a;
}
