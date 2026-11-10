// ca82_fehler.c - zentrale Fehlerausgabe auf STDERR mit Zaehler, Zusammenfassung gleicher Fehler und Obergrenze
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
//
// Jede Fehlermeldung laeuft durch fehlerMeldungPruefen() (fehlerMitOrt() fuer Meldungen mit Ort, fehlerZaehleUndPruefe()
// fuer Meldungen, deren Text der Aufrufer selbst ausgibt). Dieselbe Meldung (Text ohne Zeilennummer) wird hoechstens
// MAX_GLEICH_AUSGABE-mal und nur mit verschiedenen Quellzeilen ausgegeben; jede weitere Wiederholung wird nur gezaehlt.
// Insgesamt erscheinen hoechstens MAX_FEHLER_AUSGABE Fehlerzeilen; weitere neue Meldungen werden nur gezaehlt. Am
// Programmende (atexit, auch bei exit() in einem Pass) folgen je eine Zeile fuer jede zusammengefasste Meldung und die
// Gesamtzusammenfassung.
#include "ca82_intern.h"

#define MAX_FEHLER_AUSGABE 20   // hoechstens so viele Fehlerzeilen insgesamt
#define MAX_GLEICH_AUSGABE 3    // dieselbe Meldung (andere Zeile) hoechstens so oft einzeln
#define MAX_FEHLER_TAB 64       // verschiedene Meldungen, die fuer die Zusammenfassung gemerkt werden
#define SCHLUESSEL_LEN 200

typedef struct {
    char schluessel[SCHLUESSEL_LEN];
    int anzahl;
    int ersteZeile;
    int letzteZeile;
    int gedruckt;                       // Anzahl einzeln ausgegebener Meldungen
    int zeilen[MAX_GLEICH_AUSGABE];     // deren Quellzeilen (0 = ohne Ort)
} FehlerEintrag;

static FehlerEintrag fehlerTab[MAX_FEHLER_TAB];
static int fehlerTabN = 0;
static int fehlerAusgegeben = 0;   // Anzahl ausgegebener Fehlerzeilen
static int fehlerGesamt = 0;       // Anzahl aller gemeldeten Fehler
static int fehlerUnterdrueckt = 0; // wegen der Obergrenze nicht ausgegeben

// Liefert 1, wenn die Meldung jetzt ausgegeben werden soll.
static int fehlerMeldungPruefen(int quellzeile, const char *schluessel) {
    fehlerGesamt++;
    FehlerEintrag *e = NULL;
    for (int i = 0; i < fehlerTabN; i++)
        if (strncmp(fehlerTab[i].schluessel, schluessel, SCHLUESSEL_LEN - 1) == 0) { e = &fehlerTab[i]; break; }
    if (!e) {
        if (fehlerTabN >= MAX_FEHLER_TAB || fehlerAusgegeben >= MAX_FEHLER_AUSGABE) {
            fehlerUnterdrueckt++;
            return 0;
        }
        e = &fehlerTab[fehlerTabN++];
        snprintf(e->schluessel, SCHLUESSEL_LEN, "%s", schluessel);
        e->ersteZeile = quellzeile;
        e->anzahl = e->gedruckt = 0;
    }
    e->anzahl++;
    e->letzteZeile = quellzeile;
    if (e->gedruckt >= MAX_GLEICH_AUSGABE) return 0;               // Wiederholung: zusammengefasst
    for (int i = 0; i < e->gedruckt; i++)
        if (e->zeilen[i] == quellzeile) return 0;                  // gleiche Meldung, gleiche Zeile: zusammengefasst
    if (fehlerAusgegeben >= MAX_FEHLER_AUSGABE) {
        fehlerUnterdrueckt++;
        return 0;
    }
    e->zeilen[e->gedruckt++] = quellzeile;
    fehlerAusgegeben++;
    return 1;
}

void fehlerMitOrt(int quellzeile, const char *text) {
    if (!fehlerMeldungPruefen(quellzeile, text)) return;
    fflush(stdout);   // Reihenfolge von STDOUT und STDERR auch bei Umleitung erhalten
    if (quellzeile > 0) fprintf(stderr, "%s:%d: %sFehler:%s %s\n", qDatei(quellzeile), qZeile(quellzeile), _violett, _normal, text);
    else                fprintf(stderr, "%s: %sFehler:%s %s\n", inputFileName, _violett, _normal, text);
}

// Zaehlt einen Fehler, dessen Text der Aufrufer selbst ausgibt (printFehler). schluessel: Meldungstext ohne
// Zeileninhalt. Liefert 1, wenn die Meldung ausgegeben werden darf, 0 bei Wiederholung oder erreichter Obergrenze.
int fehlerZaehleUndPruefe(const char *schluessel) {
    return fehlerMeldungPruefen(0, schluessel);
}

int anzahlFehler(void) {
    return fehlerGesamt;
}

// Wird mit atexit() registriert.
void fehlerZusammenfassung(void) {
    int wiederholt = 0;
    for (int i = 0; i < fehlerTabN; i++) {
        const FehlerEintrag *e = &fehlerTab[i];
        if (e->anzahl <= e->gedruckt) continue;
        wiederholt += e->anzahl - e->gedruckt;
        fflush(stdout);
        if (e->ersteZeile > 0 && e->letzteZeile != e->ersteZeile)
            fprintf(stderr, "%s: %d-mal gleiche Fehlermeldung (Zeilen %s bis %s, davon %d einzeln ausgegeben): %.100s%s\n", inputFileName, e->anzahl,
                    qOrt(e->ersteZeile), qOrt(e->letzteZeile), e->gedruckt, e->schluessel, strlen(e->schluessel) > 100 ? "..." : "");
        else if (e->ersteZeile > 0)
            fprintf(stderr, "%s: %d-mal gleiche Fehlermeldung (Zeile %s, davon %d einzeln ausgegeben): %.100s%s\n", inputFileName, e->anzahl,
                    qOrt(e->ersteZeile), e->gedruckt, e->schluessel, strlen(e->schluessel) > 100 ? "..." : "");
        else
            fprintf(stderr, "%s: %d-mal gleiche Fehlermeldung (davon %d einzeln ausgegeben): %.100s%s\n", inputFileName, e->anzahl, e->gedruckt,
                    e->schluessel, strlen(e->schluessel) > 100 ? "..." : "");
    }
    if (fehlerUnterdrueckt > 0 || wiederholt > 0) {
        fflush(stdout);
        fprintf(stderr, "%s: %d Fehler insgesamt", inputFileName, fehlerGesamt);
        if (wiederholt > 0)
            fprintf(stderr, ", %d gleiche Wiederholungen zusammengefasst", wiederholt);
        if (fehlerUnterdrueckt > 0)
            fprintf(stderr, ", %d weitere Fehlermeldungen unterdrückt (Obergrenze %d Fehlerzeilen)", fehlerUnterdrueckt, MAX_FEHLER_AUSGABE);
        fprintf(stderr, ".\n");
    }
}
