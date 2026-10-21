// ca82_fluss.c - Version 1.00-026 (siehe ca82_version.h)
// Ablaufpruefungen nach Pass 3 (nur mit -WARN=SPR bzw. -WARN=TOT; sie aendern weder .obj noch .log noch .dmp):
//
//   SPR  Ein Sprungbefehl (unbedingt, bedingt oder mit Rueckkehrabsicht) fuehrt auf eine Adresse, an der kein
//        Befehl steht, sondern ein Datenwort (dw mit Wert ungleich 0, da) oder ein Wort, das der Assembler gar
//        nicht belegt. Nicht gemeldet werden Ziele, die als Befehl dienen koennen: dz, dt, dto und dtm erzeugen
//        Ausgabebefehle; db, dbn und dw 0 reservieren Zellen, in die das Programm zur Laufzeit etwa den
//        Ruecksprungbefehl schreibt (Sprung mit Rueckkehrabsicht). Auch Sprungbefehle, die ein Lade- oder
//        Speicherbefehl anspricht (Adresskonstante in Befehlsform, z. B. '000 feld'), werden nicht gemeldet.
//   TOT  Ein Befehl steht unmittelbar hinter einem unbedingten Sprung, und nichts verweist darauf: keine Marke,
//        die irgendwo verwendet wird, kein Operand und kein da-Wort mit dieser Adresse, nicht die Startadresse.
//        Der Befehl kann nur ueber Adressrechnung des Programms erreicht werden - meist ist er toter Code.
//        Nicht gemeldet wird ein unbedingter Sprung hinter einem unbedingten Sprung: so sehen Sprungtabellen aus,
//        die das Programm durch berechnete Adressen anspringt (die C8205 kennt keinen indirekten Sprung). Ebenso
//        nicht, wenn der Sprungbefehl selbst von einem Lade- oder Speicherbefehl angesprochen wird: das Programm
//        ueberschreibt ihn dann zur Laufzeit.
//
// Beide Pruefungen sind Hinweise. Programme, die Befehle zur Laufzeit in Datenworte schreiben oder Sprungadressen
// berechnen, loesen sie zu Recht aus, ohne dass ein Fehler vorliegt.
#include "ca82_intern.h"
#include "ca82_fluss.h"

#define TROMMEL 010000   // Adressen 0000 bis 7777

int warnSpr = 0;
int warnTot = 0;

enum { LEER = 0, BEFEHL = 1, DATEN = 2, PLATZHALTER = 3, AUSGABE = 4 };
enum { KEIN_SPRUNG = 0, UNBEDINGT = 1, BEDINGT = 2, RUECKKEHR = 3 };

typedef struct {
    unsigned char art;        // LEER, BEFEHL, DATEN (dw<>0, da), PLATZHALTER (db, dbn, dw 0), AUSGABE (dz, dt, dto, dtm)
    unsigned char sprung;     // nur bei BEFEHL: KEIN_SPRUNG, UNBEDINGT, BEDINGT, RUECKKEHR
    unsigned char verweis;    // 1 = ein Operand mit relativer Adresse zeigt hierher
    unsigned char datenverweis; // 1 = ein Lade-/Speicherbefehl oder ein da-Wort zeigt hierher (Zelle wird gelesen oder veraendert)
    char          datenart[4];// bei DATEN: dw oder da
    short         opcode;     // bei BEFEHL: Operationscode als Zahl (oktal gelesen)
    int           ziel;       // bei Sprung: Zieladresse, sonst -1
    int           zeile;      // Index in lineAsmAufgeloest
} Wort;

static Wort trommel[TROMMEL];

void flussZuruecksetzen(void) {
    memset(trommel, 0, sizeof(trommel));
    for (int a = 0; a < TROMMEL; a++) trommel[a].ziel = -1;
}

// Art des Sprungs nach dem Operationscode B A Z (Befehlstyp, Operationsart, Zusatz); siehe Befehlsliste 4.3.
static int sprungArt(int code) {
    int b = (code >> 6) & 7, a = (code >> 3) & 7, z = code & 7;
    if (b > 1) return KEIN_SPRUNG;
    switch (a) {
        case 0: return UNBEDINGT;                            // 000-007, 100-107
        case 2: return z >= 4 ? RUECKKEHR : KEIN_SPRUNG;     // 024-027, 124-127 (Z<4: Stopp)
        case 4: case 5: return BEDINGT;                      // Negativ-, Positivsprung; Vergleichersprung 1, 2
        case 6: return (b == 0 && z >= 4) ? RUECKKEHR : KEIN_SPRUNG;   // 064-067 (060-063: bedingter Stopp)
        case 7: return BEDINGT;                              // Ueberlauf-, Vergleichersprung 3
        default: return KEIN_SPRUNG;
    }
}

void flussMerkeBefehl(int adresse, const char *opcode, int hatZiel, int ziel, int zielAbsolut, int zeile) {
    if (adresse < 0 || adresse >= TROMMEL || opcode == NULL || strlen(opcode) != 3) return;
    for (int k = 0; k < 3; k++) if (opcode[k] < '0' || opcode[k] > '7') return;
    int code = (opcode[0] - '0') * 64 + (opcode[1] - '0') * 8 + (opcode[2] - '0');
    Wort *w = &trommel[adresse];
    w->art = BEFEHL;
    w->opcode = (short)code;
    w->zeile = zeile;
    w->sprung = (unsigned char)sprungArt(code);
    // Ein absoluter Operand (K1=00) liegt ausserhalb des verschieblichen Programms und zaehlt nicht als Verweis.
    // Operand 0000 (z. B. '020 0') ist meist nur ein Platzhalter und verweist auf nichts.
    if (hatZiel && !zielAbsolut && ziel > 0 && ziel < TROMMEL) {
        trommel[ziel].verweis = 1;
        if (w->sprung == KEIN_SPRUNG) trommel[ziel].datenverweis = 1;
        else w->ziel = ziel;
    }
}

// Ist der Operand eine Null (0, 00, 000 ...)? Dann ist das dw-Wort ein Platzhalter, den das Programm fuellt.
static int istNullOperand(int zeile) {
    if (zeile < 0 || zeile >= lineCountAsmAufgeloest) return 0;
    const char *p = lineAsmAufgeloest[zeile].sp3;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0') return 0;
    while (*p == '0') p++;
    return *p == '\0' || *p == ' ' || *p == '\t' || *p == ';';
}

void flussMerkeDaten(int von, int bis, const char *operation, int zeile) {
    int art;
    if (strcmp(operation, "dw") == 0)        art = istNullOperand(zeile) ? PLATZHALTER : DATEN;
    else if (strcmp(operation, "da") == 0)   art = DATEN;
    else if (strcmp(operation, "db") == 0 || strcmp(operation, "dbn") == 0) art = PLATZHALTER;
    else                                     art = AUSGABE;   // dz, dt, dto, dtm
    for (int a = von; a < bis && a < TROMMEL; a++) {
        if (a < 0) continue;
        Wort *w = &trommel[a];
        w->art = (unsigned char)art;
        w->zeile = zeile;
        STRKOPIE(w->datenart, operation);
    }
}

void flussMerkeVerweis(int adresse) {
    if (adresse >= 0 && adresse < TROMMEL) { trommel[adresse].verweis = 1; trommel[adresse].datenverweis = 1; }
}

// ---- gemeinsame Hilfen ----

static int quellzeileVon(int index) {
    if (index < 0 || index >= lineCountAsmAufgeloest) return 0;
    return lineAsmAufgeloest[index].srcLine;
}

// Name eines vom Benutzer vergebenen Symbols an dieser Adresse (sonst NULL).
static const char *symbolBei(int adresse) {
    for (int i = 0; i < symbolCount; i++) {
        if ((symbolTable[i].address & BITMASK) != 0) continue;
        if (symbolTable[i].address != adresse) continue;
        if (isLiteralInTable(symbolTable[i].symbol)) continue;
        return symbolTable[i].symbol;
    }
    return NULL;
}

typedef struct {
    int zeile;      // Quelltextzeile, 0 = unbekannt
    int adresse;
    char text[400];
} Meldung;

static int vergleicheMeldung(const void *a, const void *b) {
    const Meldung *x = (const Meldung *)a, *y = (const Meldung *)b;
    if ((x->zeile == 0) != (y->zeile == 0)) return (x->zeile == 0) ? 1 : -1;
    if (x->zeile != y->zeile) return x->zeile - y->zeile;
    return x->adresse - y->adresse;
}

static void gibMeldungenAus(Meldung *liste, int anzahl, const char *ueberschrift, const char *keine, const char *einzahl, const char *mehrzahl) {
    qsort(liste, (size_t)anzahl, sizeof(liste[0]), vergleicheMeldung);
    fflush(stdout);
    berichtPrintf("%s\n", ueberschrift);
    fflush(stdout);
    for (int k = 0; k < anzahl; k++) meldeWarnungOrt(liste[k].zeile, liste[k].text);
    if (anzahl == 0) berichtPrintf("%s\n", keine);
    else if (anzahl == 1) berichtPrintf("%s\n", einzahl);
    else berichtPrintf(mehrzahl, anzahl);
    berichtPrintf("\n");
}

static const char *datenartText(const Wort *w) {
    if (w->art == DATEN) return strcmp(w->datenart, "da") == 0 ? "ein Adresswort (da)" : "ein Datenwort (dw)";
    return "ein Wort, das der Assembler nicht belegt";
}

static const char *operandVon(int index) {
    static char puffer[64];
    if (index < 0 || index >= lineCountAsmAufgeloest) return "";
    const char *s = lineAsmAufgeloest[index].sp3;
    while (*s == ' ' || *s == '\t') s++;
    snprintf(puffer, sizeof(puffer), "%.60s", s);
    return puffer;
}

// ---- -WARN=SPR ----

void pruefeSprungziele(void) {
    static Meldung liste[TROMMEL];
    int n = 0;
    for (int a = 0; a < TROMMEL; a++) {
        const Wort *w = &trommel[a];
        if (w->art != BEFEHL || w->sprung == KEIN_SPRUNG || w->ziel < 0) continue;
        const Wort *z = &trommel[w->ziel];
        if (z->art != DATEN && z->art != LEER) continue;   // Befehle, Ausgabebefehle und Platzhalter sind zulaessige Ziele
        if (w->datenverweis) continue;                      // der Sprungbefehl selbst wird gelesen oder ueberschrieben: Datenzelle
        Meldung *m = &liste[n++];
        m->zeile = quellzeileVon(w->zeile);
        m->adresse = a;
        char ort[80] = "";
        if (z->art != LEER && quellzeileVon(z->zeile) > 0) snprintf(ort, sizeof(ort), ", Zeile %d", quellzeileVon(z->zeile));
        snprintf(m->text, sizeof(m->text), "Sprung '%03o %s' (Adresse %04o) fuehrt auf %04o: dort liegt kein Befehl, sondern %s%s.",
                 w->opcode, operandVon(w->zeile), (unsigned)a, (unsigned)w->ziel, datenartText(z), ort);
    }
    gibMeldungenAus(liste, n, "Pruefung der Sprungziele (-WARN=SPR)", "Alle Sprungziele sind Befehle.",
                    "1 Sprungziel ist kein Befehl.", "%d Sprungziele sind keine Befehle.\n");
}

// ---- -WARN=TOT ----

// Verweist irgendetwas auf diese Adresse? Ein Operand, ein verwendetes Symbol oder die Startadresse.
static int hatVerweis(int adresse) {
    if (adresse == 0 || adresse == (int)startAdresse) return 1;
    if (trommel[adresse].verweis) return 1;
    for (int i = 0; i < symbolCount; i++) {
        if ((symbolTable[i].address & BITMASK) != 0) continue;
        if (symbolTable[i].address == adresse && symbolTable[i].verwendet) return 1;
    }
    return 0;
}

void pruefeToterCode(void) {
    static Meldung liste[TROMMEL];
    int n = 0;
    for (int a = 1; a < TROMMEL; a++) {
        const Wort *vor = &trommel[a - 1];
        if (trommel[a].art != BEFEHL || vor->art != BEFEHL || vor->sprung != UNBEDINGT) continue;
        if (trommel[a].sprung == UNBEDINGT) continue;   // Sprungtabelle (berechnete Adresse)
        if (vor->datenverweis) continue;                // der Sprung wird zur Laufzeit ueberschrieben (z. B. durch einen Ausgabebefehl)
        if (hatVerweis(a)) continue;
        // Anfang eines toten Abschnitts: alle folgenden Befehle ohne Verweis gehoeren dazu.
        int ende = a;
        while (ende + 1 < TROMMEL && trommel[ende + 1].art == BEFEHL && !hatVerweis(ende + 1)) ende++;
        Meldung *m = &liste[n++];
        m->zeile = quellzeileVon(trommel[a].zeile);
        m->adresse = a;
        const char *marke = symbolBei(a);
        char zusatz[160] = "";
        if (marke) snprintf(zusatz, sizeof(zusatz), " (die Marke '%.40s' wird nirgends verwendet)", marke);
        int vorZeile = quellzeileVon(vor->zeile);
        char vorText[60] = "";
        if (vorZeile > 0) snprintf(vorText, sizeof(vorText), " in Zeile %d", vorZeile);
        if (ende == a + 1)
            snprintf(m->text, sizeof(m->text), "Befehl bei %04o ist vermutlich nicht erreichbar: er steht hinter dem unbedingten Sprung%s und nichts verweist darauf%s; ebenso der folgende Befehl bei %04o.",
                     (unsigned)a, vorText, zusatz, (unsigned)ende);
        else if (ende > a)
            snprintf(m->text, sizeof(m->text), "Befehl bei %04o ist vermutlich nicht erreichbar: er steht hinter dem unbedingten Sprung%s und nichts verweist darauf%s; ebenso die %d folgenden Befehle bis %04o.",
                     (unsigned)a, vorText, zusatz, ende - a, (unsigned)ende);
        else
            snprintf(m->text, sizeof(m->text), "Befehl bei %04o ist vermutlich nicht erreichbar: er steht hinter dem unbedingten Sprung%s und nichts verweist darauf%s.",
                     (unsigned)a, vorText, zusatz);
        a = ende;
    }
    gibMeldungenAus(liste, n, "Pruefung auf nicht erreichbaren Code (-WARN=TOT)", "Kein nicht erreichbarer Code gefunden.",
                    "1 Abschnitt mit nicht erreichbarem Code.", "%d Abschnitte mit nicht erreichbarem Code.\n");
}
