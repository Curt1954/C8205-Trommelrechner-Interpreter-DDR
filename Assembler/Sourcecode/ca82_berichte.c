// ca82_berichte.c - Version 1.03-009 (siehe ca82_version.h)
// Aufrufhilfe (Usage), Versionszeile und die Berichte nach dem Lauf: -WARN=SYM und --xref.
// Aus ca82ass.c ausgelagert; benutzt nur die Symboltabelle (ca82_symbole.h) und ca82_standards.
#include "ca82_standards.h"
#include "ca82_version.h"
#include "ca82_symbole.h"
#include "ca82_berichte.h"
#include "ca82_fluss.h"
#include "ca82_makros.h"
#include <errno.h>

void printUsage(const char *programName) {
    printf("Usage: %s -p Projektverzeichnis -s Quellcode-Datei [-o Objektdatei] [-t Testdatei] [-m Makrodatei] [-WARN=SYM,SPR,TOT,ALLE,NOSLIT] [--xref] [--makros] [--opsyms] [--ABSPR] [--no-opt] [--pass0] [--color | --no-color]\n", programName);
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
    printf("                           SPR  Sprungbefehle, deren Ziel ein Datenwort (dw, dwb, dwh, dwf, dwg, da) oder ein unbelegtes Wort ist.\n");
    printf("                           TOT  Befehle hinter einem unbedingten Sprung, auf die nichts verweist.\n");
    printf("                           ALLE alle drei.\n");
    printf("                           NOSLIT schaltet die (sonst immer eingeschaltete) Warnung ab, dass ein Symbol-Literal !x in einem\n");
    printf("                                Rechenausdruck steht; gehoert nicht zu ALLE.\n");
    printf("                         Die Meldungen stehen auch im .log (hinter der Symboltabelle).\n");
    printf("  --xref                 Gibt nach fehlerfreiem Lauf eine Querverweisliste aus: je Symbol Wert,\n");
    printf("                         Definitionszeile und alle Zeilen des Quelltexts, die es verwenden. Sie steht auch im .log.\n");
    printf("  --makros               Gibt nach fehlerfreiem Lauf die Makroliste aus: je aufgerufenem Makro die Zahl der\n");
    printf("                         Aufrufe und die Herkunft (Quelltext, c82ass.makros oder Projektdatei mit Zeile);\n");
    printf("                         dazu nicht aufgerufene Makros aus Quelltext und Projektdateien. Auch im .log.\n");
    printf("  ;#MACRODATEI1= bis ;#MACRODATEI9=<Pfad>\n");
    printf("                         Anweisung im Quelltext (keine Option): projektspezifische Makrodatei; Pfad relativ\n");
    printf("                         zur Quelldatei. Suchreihenfolge: Quelltext, Datei 1 bis 9, c82ass.makros.\n");
    printf("  ;#MAKROLOKAL=1         Anweisung im Quelltext (keine Option, nur einmal): $SET und $DIM in einem Makroaufruf legen lokale\n");
    printf("                         Variablen und Felder an (wie beim IBM-Makroassembler); $GLOBAL <name> vereinbart global. Ohne die Zeile\n");
    printf("                         (oder mit =0) sind sie global wie bisher.\n");
    printf("  ;#MAKROUMORDNEN=NO     Anweisung im Quelltext (keine Option, nur einmal): schaltet die Umordnung der Makro-Rumpfbloecke ab.\n");
    printf("                         Vorgabe ist an: der Optimierer verlegt die Rumpfbloecke der Makros mit $SPEC TYP=M hinter end und\n");
    printf("                         packt sie dicht (groesste zuerst), wenn die Endadresse dadurch kleiner wird; =YES nennt die Vorgabe.\n");
    printf("  ;#PRECOMMAND=<Wert>    Anweisung im Quelltext (keine Option, mehrfach erlaubt): <Wert> (Ziffern und Punkte, endet mit Punkt, z. B. 212000.) wird\n");
    printf("                         als Lochbilder vor das erste Wort des .obj-Streifens geschrieben, mehrere in der Reihenfolge des Quelltexts.\n");
    printf("  ;#POSTCOMMAND=<Wert>   wie PRECOMMAND, aber hinter das letzte Wort, noch vor das Endekennzeichen /. Bei --ABSPR ohne Wirkung.\n");
    printf("  --opsyms               Gibt die Standardtabelle der Namen fuer Operationscodes (c82ass.opsym) aus, ohne Assemblerlauf:\n");
    printf("                         je Name Code, Triaden B-A-Z, Nummer der Einzelbefehlsuebersicht und Bedeutung.\n");
    printf("                         Im Quelltext schreibt man einen Namen mit vorangestelltem Punkt im Operationscode-Feld (.LD).\n");
    printf("  ;#OPSYM=<Pfad>         Anweisung im Quelltext (keine Option, bis 9 Zeilen): weitere Namensdatei; Pfad relativ zur Quelldatei.\n");
    printf("                         Im Quelltext selbst vereinbart  NAME: opsym <code>  einen Namen ab dieser Zeile.\n");
    printf("  --ABSPR                Statt der .obj-Datei einen absolut adressierten, binaer im R300-Code codierten\n");
    printf("                         Lochstreifen <name>.kep fuer das Kleine Eingabeprogramm (KEP) erzeugen:\n");
    printf("                         Leitbefehl <start> 240: und Worte als Dualziffern (auch --ABSOLUTPROGRAMM, --ASBPR).\n");
    printf("  --no-opt, --NOOPT      Optimierer ausschalten: Literale bleiben hinter dem ersten end, dw-Zeilen an\n");
    printf("                         ihrer Adresse (sonst werden Literale in freie Zellen vor dem Programmende verlegt);\n");
    printf("                         keine Blockverschiebung (begin RELOC-EQU, RELOC-ALL), die Bloecke bleiben an ihrer Stelle.\n");
    printf("  --pass0                Nur Pass 0 (Makroaufloesung) ausfuehren, ohne Pass 1 bis 3, ohne Ausgabedateien (vorhandene bleiben\n");
    printf("                         liegen), ohne Berichte (-WARN, --xref, --makros). Farblos; alles, was sonst auf STDERR steht, geht auf\n");
    printf("                         STDOUT, die uebrige Ausgabe entfaellt. Es fehlen die Kopfmeldungen (Projektverzeichnis, Benutze fuer ...),\n");
    printf("                         und bei $NOTE steht nur der Text, ohne \"Hinweis: Makro <Name> (<Datei>:<Zeile>): \".\n");
    printf("  --probeausgabe         Zeigt die Ausgabe von $NOTE, $TRACE und $DUMP auch fuer die Probelaeufe von adr und abstand (sonst\n");
    printf("                         erscheint nur die des eigentlichen Laufs): je Zeile \"Probelauf <n>: \" davor. Ohne adr/abstand ohne Wirkung.\n");
    printf("  --color, --no-color    Farbige Ausgabe erzwingen bzw. abschalten. Ohne Angabe nur, wenn STDOUT und\n");
    printf("                         STDERR ein Terminal sind und die Umgebungsvariable NO_COLOR fehlt.\n");
    printf("  -h, --help             Diese Hilfe ausgeben.\n");
    printf("  --version              Die Versionsnummer ausgeben (steht auch in der ersten Ausgabezeile).\n");
}

// ------------------------------------------
// Warnoption -WARN=SYM: unbenutzte Symbole melden
// ------------------------------------------

int xrefAktiv = 0; // 1 = Aufruf mit --xref (Querverweisliste)
int makrolisteAktiv = 0;   // 1 = Aufruf mit --makros (Makroliste und Herkunft je Aufruf im Listing)
int warnSym = 0;   // 1 = Aufruf mit -WARN=SYM
int warnNoSlit = 0;   // 1 = Aufruf mit -WARN=NOSLIT: keine Warnung, wenn ein Symbol-Literal !x in einem Ausdruck steht (ab 1.03-006)

// Wertet alle Parameter der Form -WARN=<liste> aus. <liste> sind durch Komma getrennte Schluesselwoerter
// (Gross-/Kleinschreibung egal): SYM, SPR, TOT, ALLE und NOSLIT.
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
            } else if (gleichOhneGrossKlein(wort, "NOSLIT")) {
                warnNoSlit = 1;
            } else if (gleichOhneGrossKlein(wort, "ALLE")) {
                warnSym = warnSpr = warnTot = 1;
            } else {
                PRINT_WARNUNG("Unbekannter Wert '%s' bei -WARN= (erlaubt: SYM, SPR, TOT, ALLE, NOSLIT).", wort);
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
    if (makroIstErzeugtesLabel(name)) return 1;   // aus einem lesbaren lokalen Label <name>% erzeugt (Doku 4.3)
    return 0;
}

// Sucht die Zeile im Quelltext, in der das Symbol als Label (erstes Wort in Spalte 1) definiert wird.
// Rueckgabe: Zeilennummer (ab 1) oder 0, wenn nicht gefunden (z. B. Label stammt aus einem Makro).
static int findeDefinitionszeile(const char *name) {
    // Quelltext einschliesslich der mit $INCLUDE eingebundenen Dateien (fortlaufende Nummern, Doku 4.14)
    int gefunden = 0, nr = 0;
    size_t len = strlen(name);
    for (nr = 1; nr <= quellZeilenAnzahl(); nr++) {
        const char *zeile = quellZeilenText(nr);
        if (zeile[0] == ' ' || zeile[0] == '\t' || zeile[0] == ';' || zeile[0] == '#' ||
            zeile[0] == '\n' || zeile[0] == '\r' || zeile[0] == '\0') continue;
        if (strncmp(zeile, name, len) == 0 &&
            (zeile[len] == ':' || zeile[len] == ' ' || zeile[len] == '\t' || zeile[len] == '\n' || zeile[len] == '\r' || zeile[len] == '\0')) {
            gefunden = 1;
            break;
        }
    }
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
    for (int k = 0; k < anzahl; k++) {
        const Symbol *sym = &symbolTable[liste[k].index];
        if (liste[k].zeile > 0) {
            const char *quelle = strrchr(qDatei(liste[k].zeile), '/');
            quelle = quelle ? quelle + 1 : qDatei(liste[k].zeile);
            PRINT_WARNUNG("Symbol '%s' (%04o, %s Zeile %d) ist definiert, wird aber nie verwendet.",
                          sym->symbol, (unsigned)(sym->address & ~BITMASK), quelle, qZeile(liste[k].zeile));
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

// Ort in der Querverweisliste: Zeile der Hauptdatei als Zahl, Zeile einer eingebundenen Datei (Doku 4.14) als <Datei>:<Zeile>.
// Die Makro-Zeilen aus Makrodateien tragen keine Quelltextzeile (nr <= 0 wird nicht gezeigt).
static void xrefOrtText(int nr, char *ziel, size_t n) {
    if (strcmp(qDatei(nr), inputFileName) == 0) snprintf(ziel, n, "%d", qZeile(nr));
    else snprintf(ziel, n, "%s:%d", qDatei(nr), qZeile(nr));
}

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

    // Der Quelltext liegt zeilenweise im Speicher (alle Dateien, auch die mit $INCLUDE eingebundenen)
    char zeile[2048];
    for (int nr = 1; nr <= quellZeilenAnzahl(); nr++) {
        snprintf(zeile, sizeof(zeile), "%s", quellZeilenText(nr));
        char *kom = strchr(zeile, ';');
        if (kom) *kom = '\0';
        xrefScanne(liste, n, zeile, nr, 1);
    }
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
        char defText[1200];
        if (liste[k].defZeile > 0) xrefOrtText(liste[k].defZeile, defText, sizeof(defText));
        else snprintf(defText, sizeof(defText), "-");
        berichtPrintf("%-*s %04o  %-6s", MAX_SYMBOL_LENGTH - 1, sym->symbol, (unsigned)(sym->address & ~BITMASK), defText);
        if (liste[k].anzahl == 0) {
            berichtPrintf(" (nie verwendet)");
        } else {
            for (int z = 0; z < liste[k].anzahl; z++) {
                char ortText[1200];
                xrefOrtText(liste[k].zeilen[z], ortText, sizeof(ortText));
                berichtPrintf(" %s", ortText);
            }
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
