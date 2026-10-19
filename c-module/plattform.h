/* plattform.h — duenne Schicht fuer Linux (pthread, clock_nanosleep) und Windows (Win32).
 * Nur von trommel.c eingebunden (static-Funktionen und -Variablen, eine Uebersetzungseinheit).
 *
 * STAND: Der Linux-Zweig ist gebaut und getestet. Der Windows-Zweig ist NICHT uebersetzt und NICHT getestet
 * (in der Entwicklungsumgebung gab es keinen Windows-Compiler); er ist nach der Win32-Dokumentation geschrieben.
 *
 * Windows-Besonderheit: Die Systemuhr laeuft dort grob (Schlafen mit Millisekundenraster). Deshalb schlaeft
 * der Hintergrundprozess ohne anstehenden Auftrag grob (1 ms, weckbar) und holt die Ticks nach; bei anstehendem
 * Auftrag wartet er aktiv (Spin) bis zum naechsten Tickbeginn.
 */
#ifndef PLATTFORM_H
#define PLATTFORM_H

#include <stdint.h>

#ifdef _WIN32
/* ======================= Windows ======================= */
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <mmsystem.h>
#ifdef _MSC_VER
#pragma comment(lib, "winmm.lib")
#endif

typedef CRITICAL_SECTION   pf_mutex_t;
typedef CONDITION_VARIABLE pf_cond_t;
typedef HANDLE             pf_thread_t;
#define PF_THREAD_FUNC(name) static DWORD WINAPI name(LPVOID arg)
#define PF_THREAD_ENDE       return 0

static LARGE_INTEGER pf_freq;
static HANDLE        pf_wecker;       /* weckt den Hintergrundprozess aus dem groben Schlaf */
static int           pf_zeit_aktiv = 0;

static void pf_zeit_start(void)
{
    if (pf_zeit_aktiv) return;
    QueryPerformanceFrequency(&pf_freq);
    timeBeginPeriod(1);               /* Millisekundenraster fuer Sleep/Wait */
    pf_wecker = CreateEventA(NULL, FALSE, FALSE, NULL);
    pf_zeit_aktiv = 1;
}
static uint64_t pf_zeit_ns(void)
{
    LARGE_INTEGER c;
    uint64_t sek, rest;
    QueryPerformanceCounter(&c);
    sek  = (uint64_t)c.QuadPart / (uint64_t)pf_freq.QuadPart;
    rest = (uint64_t)c.QuadPart % (uint64_t)pf_freq.QuadPart;
    return sek * 1000000000ULL + rest * 1000000000ULL / (uint64_t)pf_freq.QuadPart;
}
static void pf_schlafe_bis(uint64_t ziel_ns, int spinnen)
{
    for (;;) {
        uint64_t jetzt = pf_zeit_ns(), rest;
        DWORD ms;
        if (jetzt >= ziel_ns) return;
        if (spinnen) { YieldProcessor(); continue; }
        rest = ziel_ns - jetzt;
        ms = (DWORD)(rest / 1000000ULL);
        if (ms < 1) ms = 1;
        WaitForSingleObject(pf_wecker, ms);   /* kehrt bei Auftragseingang frueher zurueck */
        return;
    }
}
static void pf_wecken(void) { if (pf_zeit_aktiv) SetEvent(pf_wecker); }
static void pf_timerslack_minimieren(void) { }

typedef volatile LONG pf_flag_t;                 /* atomar les- und schreibbarer Schalter */
static void pf_flag_setze(pf_flag_t *f, int v) { InterlockedExchange(f, (LONG)v); }
static int  pf_flag_lese(pf_flag_t *f)         { return (int)InterlockedCompareExchange(f, 0, 0); }

static void pf_mutex_init(pf_mutex_t *m)    { InitializeCriticalSection(m); }
static void pf_mutex_lock(pf_mutex_t *m)    { EnterCriticalSection(m); }
static void pf_mutex_unlock(pf_mutex_t *m)  { LeaveCriticalSection(m); }
static void pf_cond_init(pf_cond_t *c)      { InitializeConditionVariable(c); }
static void pf_cond_broadcast(pf_cond_t *c) { WakeAllConditionVariable(c); }
static void pf_cond_wait_ms(pf_cond_t *c, pf_mutex_t *m, unsigned ms) { SleepConditionVariableCS(c, m, ms); }
static int  pf_thread_start(pf_thread_t *t, LPTHREAD_START_ROUTINE fn, void *arg)
{
    *t = CreateThread(NULL, 0, fn, arg, 0, NULL);
    return *t ? 0 : -1;
}
static void pf_thread_join(pf_thread_t *t) { WaitForSingleObject(*t, INFINITE); CloseHandle(*t); }

#else
/* ======================= POSIX (Linux) ======================= */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <errno.h>
#include <pthread.h>
#include <time.h>
#ifdef __linux__
#include <sys/prctl.h>
#endif

typedef pthread_mutex_t pf_mutex_t;
typedef pthread_cond_t  pf_cond_t;
typedef pthread_t       pf_thread_t;
#define PF_THREAD_FUNC(name) static void *name(void *arg)
#define PF_THREAD_ENDE       return NULL

static void pf_zeit_start(void) { }
static uint64_t pf_zeit_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}
static void pf_schlafe_bis(uint64_t ziel_ns, int spinnen)
{
    struct timespec ts;
    (void)spinnen;                       /* clock_nanosleep ist fein genug */
    ts.tv_sec  = (time_t)(ziel_ns / 1000000000ULL);
    ts.tv_nsec = (long)(ziel_ns % 1000000000ULL);
    while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL) == EINTR)
        ;
}
static void pf_wecken(void) { }
static void pf_timerslack_minimieren(void)
{
#if defined(__linux__) && defined(PR_SET_TIMERSLACK)
    prctl(PR_SET_TIMERSLACK, 1UL, 0UL, 0UL, 0UL);   /* Standard 50 us waeren fast ein halber Tick */
#endif
}

typedef volatile int pf_flag_t;                  /* atomar les- und schreibbarer Schalter (GCC/Clang) */
static void pf_flag_setze(pf_flag_t *f, int v) { __atomic_store_n(f, v, __ATOMIC_SEQ_CST); }
static int  pf_flag_lese(pf_flag_t *f)         { return __atomic_load_n(f, __ATOMIC_SEQ_CST); }

static void pf_mutex_init(pf_mutex_t *m)    { pthread_mutex_init(m, NULL); }
static void pf_mutex_lock(pf_mutex_t *m)    { pthread_mutex_lock(m); }
static void pf_mutex_unlock(pf_mutex_t *m)  { pthread_mutex_unlock(m); }
static void pf_cond_init(pf_cond_t *c)
{
    pthread_condattr_t ca;
    pthread_condattr_init(&ca);
    pthread_condattr_setclock(&ca, CLOCK_MONOTONIC);
    pthread_cond_init(c, &ca);
    pthread_condattr_destroy(&ca);
}
static void pf_cond_broadcast(pf_cond_t *c) { pthread_cond_broadcast(c); }
static void pf_cond_wait_ms(pf_cond_t *c, pf_mutex_t *m, unsigned ms)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    ts.tv_sec  += ms / 1000u;
    ts.tv_nsec += (long)(ms % 1000u) * 1000000L;
    if (ts.tv_nsec >= 1000000000L) { ts.tv_sec++; ts.tv_nsec -= 1000000000L; }
    pthread_cond_timedwait(c, m, &ts);
}
static int  pf_thread_start(pf_thread_t *t, void *(*fn)(void *), void *arg) { return pthread_create(t, NULL, fn, arg); }
static void pf_thread_join(pf_thread_t *t) { pthread_join(*t, NULL); }
#endif

#endif
