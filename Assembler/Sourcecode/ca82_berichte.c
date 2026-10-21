// ca82_berichte.c - Version 1.00-026 (siehe ca82_version.h)
// Aufrufhilfe (Usage), Versionszeile und die Berichte nach dem Lauf: -WARN=SYM und --xref.
// Aus ca82ass.c ausgelagert; benutzt nur die Symboltabelle (ca82_symbole.h) und ca82_standards.
#include "ca82_standards.h"
#include "ca82_version.h"
#include "ca82_symbole.h"
#include "ca82_berichte.h"
#include "ca82_fluss.h"
#include <errno.h>

void printUsage(const char *programName) {
    printf("Usage: %s -p Projektverzeichnis -s Quellcode-Datei [-o Objektdatei] [-t Testdatei] [-m Makrodatei] [-WARN=SYM,SPR,TOT,ALLE] [--xref] [--color | --no-color]\n", programName);
    printf("       %s -h | --help | --version\n", programName);
    printf("\n");
    printf("  -p Projektverzeichnis  Verzeichnis mit dem Quelltext; dorthin werden auch die Ausgabedateien\n");
    printf("                         (.log .obj .mqo .sym .dmp .test) geschrieben. Ohne -p gilt der zuletzt\n");
    printf("                         benutzte Wert aus der Datei 'projekdetails' im aktuellen Verzeichnis.\n");
    printf("  -s Quellcode-Datei     Assembler-Quelltext im Projektverzeichnis; die Endung .asm darf entfallen.\n");
    printf("                         Ohne -s gilt ebenfalls der zuletzt benutzte Wert aus 'projekdetails'.\n");
    printf("  -o Pfad | Datei        Ablageort der .obj-Datei statt des Projektverzeichnisses. Verzeichnis\n");
    printf("                         (existiert, oder endet auf / bzw. \\): Dateiname aus -s mit Endung .obj.\n");
    printf("                         Sonst Dateiname mit oder ohne Pfad (relativ zum aktuellen Verzeichnis),\n");
    printf("                         unveraendert uebernommen. Das Verzeichnis muss existieren.\n");
    printf("  -t Pfad | Datei        wie -o, aber fuer die .test-Datei (Endung .test).\n");
    printf("  -m Makrodatei          Pfad der Makrodatei statt 'c82ass.makros' (sonst: aktuelles Verzeichnis,\n");
    printf("                         ersatzweise 'Sourcecode/'). Mit -m wird nur dieser Pfad benutzt.\n");
    printf("  -WARN=liste            Zusaetzliche Warnungen; Werte durch Komma getrennt (Gross-/Kleinschreibung egal):\n");
    printf("                           SYM  Symbole, die definiert, aber nirgends verwendet werden.\n");
    printf("                           SPR  Sprungbefehle, deren Ziel ein Datenwort (dw, da) oder ein unbelegtes Wort ist.\n");
    printf("                           TOT  Befehle hinter einem unbedingten Sprung, auf die nichts verweist.\n");
    printf("                           ALLE alle drei.\n");
    printf("                         Die Meldungen stehen auch im .log (hinter der Symboltabelle).\n");
    printf("  --xref                 Gibt nach fehlerfreiem Lauf eine Querverweisliste aus: je Symbol Wert,\n");
    printf("                         Definitionszeile und alle Zeilen des Quelltexts, die es verwenden. Sie steht auch im .log.\n");
    printf("  --color, --no-color    Farbige Ausgabe erzwingen bzw. abschalten. Ohne Angabe nur, wenn STDOUT und\n");
    printf("                         STDERR ein Terminal sind und die Umgebungsvariable NO_COLOR fehlt.\n");
    printf("  -h, --help             Diese Hilfe ausgeben.\n");
    printf("  --version              Die Versionsnummer ausgeben (steht auch in der ersten Ausgabezeile).\n");
}

// ------------------------------------------
// Warnoption -WARN=SYM: unbenutzte Symbole melden
// ------------------------------------------

int xrefAktiv = 0; // 1 = Aufruf mit --xref (Querverweisliste)
int warnSym = 0;   // 1 = Aufruf mit -WARN=SYM

// Wertet alle Parameter der Form -WARN=<liste> aus. <liste> sind durch Komma getrennte Schluesselwoerter
// (Gross-/Kleinschreibung egal). Bisher gibt es nur SYM.
void verarbeiteWarnOptionen(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        if (argv[i] == NULL || !beginntOhneGrossKlein(argv[i], "-WARN=")) continue;
        char liste[256];
        strncpy(liste, argv[i] + 6, sizeof(liste) - 1);
        liste[sizeof(liste) - 1] = '\0';
        for (char *wort = strtok(liste, ","); wort != NULL; wort = strtok(NULL, ",")) {
            if (gleichOhneGrossKlein(wort, "SYM")) {
                warnSym = 1;
            } else if (gleichOhneGrossKlein(wort, "SPR")) {
                warnSpr = 1;
            } else if (gleichOhneGrossKlein(wort, "TOT")) {
                warnTot = 1;
            } else if (gleichOhneGrossKlein(wort, "ALLE")) {
                warnSym = warnSpr = warnTot = 1;
            } else {
                PRINT_WARNUNG("Unbekannter Wert '%s' bei -WARN= (erlaubt: SYM, SPR, TOT, ALLE).", wort);
            }
        }
    }
}

// Vom Assembler selbst erzeugte Symbole sind keine Benutzersymbole und werden nicht gemeldet:
//   - Literalsymbole (l0001, l0002, ...) aus #- und @-Literalen,
//   - Makro-Labels (ML0001 + dreibuchstabige Kennung, z. B. ML0004MTA), die aus Makroexpansionen stammen.
static int istErzeugtesSymbol(const char *name) {
    if (isLiteralInTable(name)) return 1;
    if (strlen(name) == 9 && strncmp(name, "ML", 2) == 0) {
        int ok = 1;
        for (int k = 2; k < 6; k++) if (!isdigit((unsigned char)name[k])) ok = 0;
        for (int k = 6; k < 9; k++) if (!isupper((unsigned char)name[k])) ok = 0;
        if (ok) return 1;
    }
    return 0;
}

// Sucht die Zeile im Quelltext, in der das Symbol als Label (erstes Wort in Spalte 1) definiert wird.
// Rueckgabe: Zeilennummer (ab 1) oder 0, wenn nicht gefunden (z. B. Label stammt aus einem Makro).
static int findeDefinitionszeile(const char *name) {
    FILE *f = fopen(inputFileName, "r");
    if (!f) return 0;
    char zeile[2048];
    int nr = 0, gefunden = 0;
    size_t len = strlen(name);
    while (fgets(zeile, sizeof(zeile), f)) {
        nr++;
        if (zeile[0] == ' ' || zeile[0] == '\t' || zeile[0] == ';' || zeile[0] == '#' ||
            zeile[0] == '\n' || zeile[0] == '\r' || zeile[0] == '\0') continue;
        if (strncmp(zeile, name, len) == 0 &&
            (zeile[len] == ':' || zeile[len] == ' ' || zeile[len] == '\t' || zeile[len] == '\n' || zeile[len] == '\r' || zeile[len] == '\0')) {
            gefunden = 1;
            break;
        }
    }
    fclose(f);
    return gefunden ? nr : 0;
}

typedef struct {
    int zeile;      // Definitionszeile im Quelltext, 0 = unbekannt
    int index;      // Index in symbolTable
} UnbenutztesSymbol;

static int vergleicheUnbenutzte(const void *a, const void *b) {
    const UnbenutztesSymbol *x = (const UnbenutztesSymbol *)a;
    const UnbenutztesSymbol *y = (const UnbenutztesSymbol *)b;
    // bekannte Zeilen zuerst in Quelltextreihenfolge, unbekannte danach nach Wert
    if ((x->zeile == 0) != (y->zeile == 0)) return (x->zeile == 0) ? 1 : -1;
    if (x->zeile != y->zeile) return x->zeile - y->zeile;
    int ax = symbolTable[x->index].address & ~BITMASK;
    int ay = symbolTable[y->index].address & ~BITMASK;
    return ax - ay;
}

// Wird nach erfolgreichem Pass 3 aufgerufen (alle Operanden sind dann ausgewertet): meldet jedes Symbol,
// das definiert, aber in keinem Operanden und keinem Ausdruck verwendet wurde.
// Als Verwendung zaehlt auch das Vorkommen im Ausdruck eines anderen Symbols (z. B. a: equ b+1 verwendet b).
void pruefeUnbenutzteSymbole(void) {
    static UnbenutztesSymbol liste[MAX_SYMBOLS];
    int anzahl = 0;
    for (int i = 0; i < symbolCount; i++) {
        if (symbolTable[i].verwendet) continue;
        if (istErzeugtesSymbol(symbolTable[i].symbol)) continue;
        liste[anzahl].index = i;
        liste[anzahl].zeile = findeDefinitionszeile(symbolTable[i].symbol);
        anzahl++;
    }
    qsort(liste, anzahl, sizeof(liste[0]), vergleicheUnbenutzte);

    fflush(stdout);   // stdout (gepuffert) und stderr (Warnungen) sollen auch bei Umleitung in der richtigen Reihenfolge erscheinen
    berichtPrintf("Pruefung auf unbenutzte Symbole (-WARN=SYM)\n");
    fflush(stdout);
    const char *quelle = strrchr(inputFileName, '/');
    quelle = quelle ? quelle + 1 : inputFileName;
    for (int k = 0; k < anzahl; k++) {
        const Symbol *sym = &symbolTable[liste[k].index];
        if (liste[k].zeile > 0) {
            PRINT_WARNUNG("Symbol '%s' (%04o, %s Zeile %d) ist definiert, wird aber nie verwendet.",
                          sym->symbol, (unsigned)(sym->address & ~BITMASK), quelle, liste[k].zeile);
        } else {
            PRINT_WARNUNG("Symbol '%s' (%04o) ist definiert, wird aber nie verwendet.",
                          sym->symbol, (unsigned)(sym->address & ~BITMASK));
        }
    }
    if (anzahl == 0) {
        berichtPrintf("Keine unbenutzten Symbole.\n");
    } else {
        berichtPrintf(anzahl == 1 ? "1 unbenutztes Symbol.\n" : "%d unbenutzte Symbole.\n", anzahl);
    }
    berichtPrintf("\n");
}
// ------------------------------------------
// Querverweisliste (--xref): je Symbol Wert, Definitionszeile und alle Zeilen, in denen der Name vorkommt.
// Grundlage ist der Quelltext (.asm) selbst: Kommentare ab ';' werden ignoriert, Namen gelten nur als
// ganze Woerter. Die Operanden der Makroexpansionen stehen im Listing und zaehlen deshalb mit: Ein Symbol,
// das ein Makro in seinem Rumpf verwendet, gilt als verwendet in der Zeile des Makroaufrufs. Vom Assembler
// erzeugte Symbole (Literale, Makro-Labels) stehen nicht in der Liste.
// ------------------------------------------
typedef struct {
    int index;       // Index in symbolTable
    int defZeile;    // Zeile der Definition (Name steht in Spalte 1), 0 = nicht gefunden
    int anzahl;      // Anzahl Verwendungen (Zeilen)
    int kapazitaet;
    int *zeilen;     // Zeilennummern der Verwendungen (je Zeile hoechstens einmal)
} XrefEintrag;

static int vergleicheXrefName(const void *a, const void *b) {
    return strcmp(symbolTable[((const XrefEintrag *)a)->index].symbol, symbolTable[((const XrefEintrag *)b)->index].symbol);
}

static void xrefMerke(XrefEintrag *e, int zeile) {
    for (int k = 0; k < e->anzahl; k++) if (e->zeilen[k] == zeile) return;   // je Zeile nur einmal
    if (e->anzahl == e->kapazitaet) {
        int neu = e->kapazitaet ? 2 * e->kapazitaet : 8;
        int *z = (int *)realloc(e->zeilen, (size_t)neu * sizeof(int));
        if (!z) { fprintf(stderr, "Speicherzuweisung fuer Querverweisliste fehlgeschlagen!\n"); exit(RC_FEHLER); }
        e->zeilen = z;
        e->kapazitaet = neu;
    }
    e->zeilen[e->anzahl++] = zeile;
}

// Operanden aus Makroexpansionen (von Pass 0 gemeldet, nur mit --xref): Zeile = Zeile des Makroaufrufs.
typedef struct { int zeile; char *text; } MakroOperand;
static MakroOperand *makroOperanden = NULL;
static int makroOperandenAnzahl = 0, makroOperandenKapazitaet = 0;

void xrefMerkeMakroOperand(int quellzeile, const char *operand) {
    if (quellzeile <= 0 || operand == NULL || operand[0] == '\0') return;
    if (makroOperandenAnzahl > 0 && makroOperanden[makroOperandenAnzahl - 1].zeile == quellzeile &&
        strcmp(makroOperanden[makroOperandenAnzahl - 1].text, operand) == 0) return;
    if (makroOperandenAnzahl == makroOperandenKapazitaet) {
        int neu = makroOperandenKapazitaet ? 2 * makroOperandenKapazitaet : 256;
        MakroOperand *p = (MakroOperand *)realloc(makroOperanden, (size_t)neu * sizeof(MakroOperand));
        if (!p) { fprintf(stderr, "Speicherzuweisung fuer Querverweisliste fehlgeschlagen!\n"); exit(RC_FEHLER); }
        makroOperanden = p;
        makroOperandenKapazitaet = neu;
    }
    makroOperanden[makroOperandenAnzahl].zeile = quellzeile;
    makroOperanden[makroOperandenAnzahl].text = strdup(operand);
    if (!makroOperanden[makroOperandenAnzahl].text) { fprintf(stderr, "Speicherzuweisung fuer Querverweisliste fehlgeschlagen!\n"); exit(RC_FEHLER); }
    makroOperandenAnzahl++;
}

// Sucht in text (ein Operand oder eine Quellzeile ohne Kommentar) alle Symbolnamen und merkt sie fuer Zeile nr.
// istQuelle: text ist eine Quellzeile; ein Name in Spalte 1 ist dann die Definition.
static void xrefScanne(XrefEintrag *liste, int n, const char *zeile, int nr, int istQuelle) {
    const char *p = zeile;
    while (*p) {
        if (isalpha((unsigned char)*p) || *p == '_') {
            const char *q = p;
            while (isalnum((unsigned char)*q) || *q == '_') q++;
            size_t len = (size_t)(q - p);
            if (len < MAX_SYMBOL_LENGTH) {
                char name[MAX_SYMBOL_LENGTH];
                memcpy(name, p, len);
                name[len] = '\0';
                int lo = 0, hi = n - 1;
                while (lo <= hi) {   // Binaersuche in der nach Namen sortierten Liste
                    int mid = (lo + hi) / 2;
                    int c = strcmp(name, symbolTable[liste[mid].index].symbol);
                    if (c == 0) {
                        if (istQuelle && p == zeile && liste[mid].defZeile == 0) liste[mid].defZeile = nr;
                        else xrefMerke(&liste[mid], nr);
                        break;
                    }
                    if (c < 0) hi = mid - 1; else lo = mid + 1;
                }
            }
            p = q;
        } else if (isdigit((unsigned char)*p)) {
            while (isalnum((unsigned char)*p) || *p == '_') p++;   // Zahlen (auch 0x.., Oktal) ueberspringen
        } else {
            p++;
        }
    }
}

static int vergleicheInt(const void *a, const void *b) {
    return *(const int *)a - *(const int *)b;
}

void erzeugeQuerverweisliste(void) {
    XrefEintrag *liste = (XrefEintrag *)calloc(MAX_SYMBOLS, sizeof(XrefEintrag));
    if (!liste) { fprintf(stderr, "Speicherzuweisung fuer Querverweisliste fehlgeschlagen!\n"); exit(RC_FEHLER); }
    int n = 0;
    for (int i = 0; i < symbolCount; i++) {
        if (istErzeugtesSymbol(symbolTable[i].symbol)) continue;
        liste[n++].index = i;
    }
    qsort(liste, n, sizeof(liste[0]), vergleicheXrefName);

    FILE *f = fopen(inputFileName, "r");
    if (!f) {
        PRINT_WARNUNG("Querverweisliste: Quelltext '%s' kann nicht gelesen werden.", inputFileName);
        free(liste);
        return;
    }
    char zeile[2048];
    int nr = 0;
    while (fgets(zeile, sizeof(zeile), f)) {
        nr++;
        char *kom = strchr(zeile, ';');
        if (kom) *kom = '\0';
        xrefScanne(liste, n, zeile, nr, 1);
    }
    fclose(f);
    for (int k = 0; k < makroOperandenAnzahl; k++) {
        xrefScanne(liste, n, makroOperanden[k].text, makroOperanden[k].zeile, 0);
        free(makroOperanden[k].text);
    }
    free(makroOperanden);
    makroOperanden = NULL;
    makroOperandenAnzahl = makroOperandenKapazitaet = 0;
    for (int k = 0; k < n; k++) if (liste[k].anzahl > 1) qsort(liste[k].zeilen, (size_t)liste[k].anzahl, sizeof(int), vergleicheInt);

    berichtPrintf("Querverweisliste (--xref)\n");
    berichtPrintf("%-*s %-5s %-6s %s\n", MAX_SYMBOL_LENGTH - 1, "Symbol", "Wert", "Def.", "Verwendet in Zeile");
    for (int k = 0; k < n; k++) {
        const Symbol *sym = &symbolTable[liste[k].index];
        char defText[16];
        if (liste[k].defZeile > 0) snprintf(defText, sizeof(defText), "%d", liste[k].defZeile);
        else snprintf(defText, sizeof(defText), "-");
        berichtPrintf("%-*s %04o  %-6s", MAX_SYMBOL_LENGTH - 1, sym->symbol, (unsigned)(sym->address & ~BITMASK), defText);
        if (liste[k].anzahl == 0) {
            berichtPrintf(" (nie verwendet)");
        } else {
            for (int z = 0; z < liste[k].anzahl; z++) berichtPrintf(" %d", liste[k].zeilen[z]);
        }
        berichtPrintf("\n");
        free(liste[k].zeilen);
    }
    free(liste);
    if (n == 0) berichtPrintf("Keine Symbole.\n");
    berichtPrintf("\n");
}

void greetings(void) {
    printf("C8205 Assembler C82aas Version %s\n", ASM_VERSION);
}
