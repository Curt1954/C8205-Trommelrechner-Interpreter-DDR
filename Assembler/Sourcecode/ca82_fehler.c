// ca82_fehler.c - zentrale Fehlerausgabe auf STDERR mit Zaehler und Obergrenze
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
//
// Alle Fehlermeldungen mit Ort (datei:zeile: Fehler: text) laufen durch fehlerMitOrt(). Es werden hoechstens
// MAX_FEHLER_AUSGABE Meldungen ausgegeben; weitere werden nur gezaehlt. Die Zusammenfassung erscheint am
// Programmende (atexit), auch wenn ein Pass mit exit() abbricht.
#include "ca82_intern.h"

#define MAX_FEHLER_AUSGABE 20

static int fehlerGesamt = 0;       // Anzahl aller gemeldeten Fehler
static int fehlerUnterdrueckt = 0; // davon nicht ausgegeben

void fehlerMitOrt(int quellzeile, const char *text) {
    fehlerGesamt++;
    if (fehlerGesamt > MAX_FEHLER_AUSGABE) {
        fehlerUnterdrueckt++;
        return;
    }
    fflush(stdout);   // Reihenfolge von STDOUT und STDERR auch bei Umleitung erhalten
    if (quellzeile > 0) fprintf(stderr, "%s:%d: %sFehler:%s %s\n", inputFileName, quellzeile, _violett, _normal, text);
    else                fprintf(stderr, "%s: %sFehler:%s %s\n", inputFileName, _violett, _normal, text);
}

int anzahlFehler(void) {
    return fehlerGesamt;
}

// Wird mit atexit() registriert.
void fehlerZusammenfassung(void) {
    if (fehlerUnterdrueckt > 0) {
        fflush(stdout);
        fprintf(stderr, "%s: %d Fehler insgesamt, %d weitere Fehlermeldungen unterdrückt (Obergrenze %d).\n",
                inputFileName, fehlerGesamt, fehlerUnterdrueckt, MAX_FEHLER_AUSGABE);
    }
}
