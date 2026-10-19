/* unterbrechung.h — projektweite Konvention: jede wartende/spinnende
 * Schleife (busy-spin oder anders) MUSS diese Komponente einbinden und
 * zusätzlich zu ihrer eigentlichen Abbruchbedingung auf
 * abbruch_angefordert prüfen, damit Strg+C (SIGINT) das Programm
 * jederzeit kontrolliert (statt abrupt) beenden kann — inkl. Chance
 * für aufrufenden Code, vor dem Beenden aufzuräumen (z. B.
 * trommel_ausschalten()).
 *
 * Verwendung in einer Warteschleife:
 *   while (<Bedingung> && !abbruch_angefordert) { ... }
 *   if (abbruch_angefordert) { <aufraeumen>; return/exit; }
 */
#ifndef UNTERBRECHUNG_H
#define UNTERBRECHUNG_H

#include <signal.h>
#include "c8205_api.h"

/* sig_atomic_t: garantiert signalsicher lesbar/schreibbar, daher hier
 * bewusst kein einfaches int. */
extern C8205_API volatile sig_atomic_t abbruch_angefordert;

/* Installiert den SIGINT-Handler. Einmal zu Programmbeginn aufrufen. */
C8205_API void unterbrechung_einrichten(void);

#endif
