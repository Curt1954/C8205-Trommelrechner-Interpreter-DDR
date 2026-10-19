/* unterbrechung.c — s. unterbrechung.h für die Verwendungs-Konvention. */
#include "unterbrechung.h"
#include <stddef.h>

volatile sig_atomic_t abbruch_angefordert = 0;

static void handler(int signum)
{
    (void)signum;
    abbruch_angefordert = 1;
}

void unterbrechung_einrichten(void)
{
#ifdef _WIN32
    /* Windows kennt kein sigaction; signal(SIGINT) genügt. Der Handler läuft dort in einem eigenen Thread,
     * das Flag wird von wartenden Schleifen regelmäßig geprüft (Trommel: alle 50 ms). */
    signal(SIGINT, handler);
#else
    struct sigaction sa;
    sa.sa_handler = handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;   /* kein SA_RESTART: unterbrochene Syscalls sollen
                           mit Fehler zurueckkehren statt automatisch
                           neu zu starten, damit Wartefunktionen die
                           Chance bekommen, abbruch_angefordert zu sehen. */
    sigaction(SIGINT, &sa, NULL);
#endif
}
