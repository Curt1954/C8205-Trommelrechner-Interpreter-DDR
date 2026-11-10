// ca82_main.c - Hauptprogramm: Optionen, Dateinamen, Ablauf der Paesse
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"
#include "ca82_fluss.h"
#ifndef _WIN32
#include <sys/wait.h>
#endif


// ------------------------------------------


static char projektVerzeichnis[512] = {0};

// --ABSPR / --ABSOLUTPROGRAMM / --ASBPR (Gross-/Kleinschreibung egal)
static int istAbsprOption(const char *a) {
    return gleichOhneGrossKlein(a, "--ABSPR") || gleichOhneGrossKlein(a, "--ABSOLUTPROGRAMM") || gleichOhneGrossKlein(a, "--ASBPR");
}

static char quellcodeDatei[512] = "";

static char logFileName[1024] = "";
static char machineCodeFileName[1024] = "";
static char hilfsFileName[1024] = "";
static char symFileName[1024] = "";
static char testFileName[1024] = "";
static char dmpFileName[1024] = "";
static char adr1Datei[1024] = "";      // Dateien der Probelaeufe fuer adr/abstand (siehe unten)
static char adr2Datei[1024] = "";
static char adrLogDatei[1024] = "";
static char adrDbgDatei[1024] = "";      // Debugdatei der Probelaeufe (--probeausgabe, ab 1.01-021)



// Funktion, um sicherzustellen, dass eine Datei eine Endung hat
void ensureFileExtension(char *fileName, const char *defaultExtension, size_t maxSize) {
    if (strchr(fileName, '.') == NULL) { // Prüfen, ob keine Dateiendung vorhanden ist
        size_t currentLength = strlen(fileName);
        if (currentLength + strlen(defaultExtension) >= maxSize) {
            PRINT_FEHLER("Puffer für Dateiname ist zu klein, um die Erweiterung hinzuzufügen: %s", fileName);
            PRINT_FEHLER("%s", "Abbruch.");
            exit(RC_FEHLER); // Abbruch bei Pufferoverflow
        }
        stranhaengen(fileName, maxSize, defaultExtension); // .asm anhängen
    }
}

// ----------------------------------------
// Optionale Ausgabeorte: -o fuer die .obj-Datei, -t fuer die .test-Datei.
// Ist der Schalter nicht angegeben, bleibt <ziel> unveraendert (Standardort: Projektverzeichnis).
// Ist er angegeben, gilt statt des Standardorts der angegebene Pfad:
//   - Verzeichnis (existiert bereits oder endet auf '/' bzw. '\\'): der Dateiname wird aus -s gebildet
//     (Name der Quellcode-Datei ohne Endung + <endung>);
//   - sonst Dateiname mit oder ohne Pfad (relativ zum aktuellen Verzeichnis), unveraendert uebernommen.
// Das Verzeichnis muss existieren; es wird nicht angelegt.
static void ermittleAusgabeDatei(int argc, char *argv[], const char *schalter, const char *endung,
                                 const char *quellcodeDatei_p, char *ziel, size_t zielGroesse) {
    const char *wert = NULL;
    for (int i = 1; i < argc; i++) {
        if (argv[i] != NULL && strcmp(argv[i], schalter) == 0) {
            if (i + 1 >= argc || argv[i + 1] == NULL || argv[i + 1][0] == '\0' || argv[i + 1][0] == '-') {
                PRINT_FEHLER("Parameter %s ohne Pfad oder Dateiname.", schalter);
                PRINT_FEHLER("%s", "Abbruch.");
                exit(RC_FEHLER);
            }
            wert = argv[i + 1];
            break;
        }
    }
    if (wert == NULL) return;

    size_t laenge = strlen(wert);
    int endetMitTrenner = (wert[laenge - 1] == '/' || wert[laenge - 1] == '\\');
    int ergebnis;

    if (endetMitTrenner || isDirectory(wert)) {
        if (!isDirectory(wert)) {
            PRINT_FEHLER("Das Verzeichnis '%s' fuer Parameter %s existiert nicht.", wert, schalter);
            PRINT_FEHLER("%s", "Abbruch.");
            exit(RC_FEHLER);
        }
        const char *punkt = strrchr(quellcodeDatei_p, '.');
        int namensLaenge = punkt ? (int)(punkt - quellcodeDatei_p) : (int)strlen(quellcodeDatei_p);
        ergebnis = snprintfGekuerzt(ziel, zielGroesse, "%s%s%.*s%s", wert, endetMitTrenner ? "" : "/",
                                    namensLaenge, quellcodeDatei_p, endung);
    } else {
        const char *sep1 = strrchr(wert, '/');
        const char *sep2 = strrchr(wert, '\\');
        const char *sep = (sep1 && sep2) ? (sep1 > sep2 ? sep1 : sep2) : (sep1 ? sep1 : sep2);
        if (sep != NULL) {
            char verzeichnis[1024];
            size_t dl = (size_t)(sep - wert);
            if (dl == 0) dl = 1;                       // Wurzelverzeichnis "/"
            if (dl >= sizeof(verzeichnis)) dl = sizeof(verzeichnis) - 1;
            memcpy(verzeichnis, wert, dl);
            verzeichnis[dl] = '\0';
            if (!isDirectory(verzeichnis)) {
                PRINT_FEHLER("Das Verzeichnis '%s' fuer Parameter %s existiert nicht.", verzeichnis, schalter);
                PRINT_FEHLER("%s", "Abbruch.");
                exit(RC_FEHLER);
            }
        }
        ergebnis = snprintf(ziel, zielGroesse, "%s", wert);
    }
    if (ergebnis < 0 || (size_t)ergebnis >= zielGroesse) {
        PRINT_FEHLER("Der Pfad fuer Parameter %s ist zu lang.", schalter);
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }
}


// ----------------------------------------

// Schneidet Umleitungszeichen ab ('>' am Parameteranfang) und legt fest, ob Farbcodes ausgegeben werden:
// nur wenn STDOUT und STDERR Terminals sind und NO_COLOR nicht gesetzt ist; --color / --no-color erzwingen es.
static int bereinigeParameter(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '>') {
            argv[i] = NULL;       // alles ab diesem Parameter entfernen
            argc = i;
            break;
        }
    }
    farbeAktiv = isatty(1) && isatty(2) && getenv("NO_COLOR") == NULL;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--color") == 0)    farbeAktiv = 1;
        if (strcmp(argv[i], "--no-color") == 0) farbeAktiv = 0;
    }
    return argc;
}

// --pass0 (Gross-/Kleinschreibung egal)
static int istPass0Option(const char *a) {
    return gleichOhneGrossKlein(a, "--pass0");
}

// Schalter --pass0: gleicht der Shell-Umleitung 2>&1 >/dev/null. STDERR geht auf das echte STDOUT,
// alles, was sonst auf STDOUT steht (Versionszeile, "Pass 0", Listing), geht ins Null-Geraet.
// Die Kopfmeldungen (printMsg) und den Kopf der $NOTE-Hinweise (makroHinweis) laesst der Programmtext selbst weg.
#ifdef _WIN32
#define NULL_GERAET "NUL"
#else
#define NULL_GERAET "/dev/null"
#endif
static void leiteAusgabeFuerPass0um(void) {
    fflush(stdout);
    fflush(stderr);
    int echtesStdout = dup(1);
    int nul = open(NULL_GERAET, O_WRONLY);
    if (echtesStdout < 0 || nul < 0 || dup2(nul, 1) < 0 || dup2(echtesStdout, 2) < 0) {
        fprintf(stderr, "Fehler: Die Ausgabe fuer --pass0 konnte nicht umgeleitet werden.\n");
        exit(RC_FEHLER);
    }
    close(nul);
    close(echtesStdout);
    nurPass0Aktiv = 1;
    farbeAktiv = 0;   // farblos, wie bei --no-color
}

// Prueft alle Optionen. Unbekannte Optionen werden nicht stillschweigend ignoriert: sonst laeuft der
// Assembler mit den gespeicherten Parametern (projekdetails) womoeglich auf dem falschen Projekt.
// Rueckgabe: RC_OK = Optionen in Ordnung, sonst RC_FEHLER (Meldung und Usage sind schon ausgegeben).
static int pruefeOptionen(int argc, char *argv[]) {
    int unbekannt = 0;
    fflush(stdout);   // Reihenfolge von STDOUT und STDERR auch bei Umleitung erhalten
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (strcmp(a, "-p") == 0 || strcmp(a, "-s") == 0 || strcmp(a, "-o") == 0 || strcmp(a, "-t") == 0 || strcmp(a, "-m") == 0) {
            if (i + 1 >= argc) {
                PRINT_FEHLER("Option '%s' erwartet einen Wert.", a);
                printf("\n");
                printUsage(argv[0]);
                return RC_FEHLER;
            }
            if (strcmp(a, "-m") == 0) {
                if (makroDateiSetzen(argv[i + 1]) != 0) {
                    PRINT_FEHLER("%s", "Der Pfad fuer Parameter -m ist zu lang.");
                    return RC_FEHLER;
                }
            }
            i++;   // der naechste Parameter ist der Wert (auch wenn er mit '-' beginnt)
            continue;
        }
        if (strcmp(a, "--color") == 0 || strcmp(a, "--no-color") == 0) continue;
        if (strcmp(a, "--xref") == 0) continue;
        if (gleichOhneGrossKlein(a, "--makros")) continue;
        if (gleichOhneGrossKlein(a, "--opsyms")) continue;
        if (istPass0Option(a)) continue;
        if (istAbsprOption(a)) continue;
        if (gleichOhneGrossKlein(a, "--no-opt") || gleichOhneGrossKlein(a, "--NOOPT")) continue;
        if (strncmp(a, "--adrein=", 9) == 0 || strncmp(a, "--adraus=", 9) == 0 || strncmp(a, "--adrdbg=", 9) == 0) continue;   // versteckte Optionen der Probelaeufe fuer adr/abstand
        if (gleichOhneGrossKlein(a, "--probeausgabe")) continue;   // Hinweise, Spur und Abzug der Probelaeufe anzeigen (ab 1.01-021)
        if (beginntOhneGrossKlein(a, "-WARN=")) continue;
        if (a[0] == '-') {
            PRINT_FEHLER("Unbekannte Option '%s'.", a);
            unbekannt = 1;
        } else {
            PRINT_WARNUNG("Unerwartetes Argument '%s' wird ignoriert.", a);
        }
    }
    if (unbekannt) {
        printf("\n");
        printUsage(argv[0]);
        return RC_FEHLER;
    }
    return RC_OK;
}

// Bildet aus dem Projektverzeichnis und dem Namen der Quellcodedatei alle Dateinamen der Ausgabe;
// -o und -t koennen .obj und .test an einen anderen Ort legen.
static void dateinameBilden(char *ziel, size_t groesse, const char *format, ...) __attribute__((format(printf, 3, 4)));
// Bildet einen Dateinamen; passt er nicht in den Puffer, Fehlermeldung und Abbruch (frueher wurde der Name still gekuerzt).
static void dateinameBilden(char *ziel, size_t groesse, const char *format, ...) {
    va_list ap;
    va_start(ap, format);
    int n = vsnprintf(ziel, groesse, format, ap);
    va_end(ap);
    if (n < 0 || (size_t)n >= groesse) {
        PRINT_FEHLER("Ein Dateiname waere laenger als %d Zeichen (Quellcode-Datei oder Projektverzeichnis zu lang).", (int)groesse - 1);
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }
}

static void bildeDateinamen(int argc, char *argv[]) {
    const char *punkt = strrchr(quellcodeDatei, '.');
    int namensLaenge = punkt ? (int)(punkt - quellcodeDatei) : (int)strlen(quellcodeDatei);

    dateinameBilden(inputFileName, sizeof(inputFileName), "%s/%s", projektVerzeichnis, quellcodeDatei);
    dateinameBilden(logFileName, sizeof(logFileName), "%s/%.*s.log", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(machineCodeFileName, sizeof(machineCodeFileName), "%s/%.*s%s", projektVerzeichnis, namensLaenge, quellcodeDatei, absprAktiv ? ".kep" : ".obj");
    dateinameBilden(hilfsFileName, sizeof(hilfsFileName), "%s/%.*s.mqo", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(symFileName, sizeof(symFileName), "%s/%.*s.sym", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(testFileName, sizeof(testFileName), "%s/%.*s.test", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(dmpFileName, sizeof(dmpFileName), "%s/%.*s.dmp", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(adr1Datei, sizeof(adr1Datei), "%s/%.*s.adr1", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(adr2Datei, sizeof(adr2Datei), "%s/%.*s.adr2", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(adrLogDatei, sizeof(adrLogDatei), "%s/%.*s.adrlog", projektVerzeichnis, namensLaenge, quellcodeDatei);
    dateinameBilden(adrDbgDatei, sizeof(adrDbgDatei), "%s/%.*s.adrdbg", projektVerzeichnis, namensLaenge, quellcodeDatei);

    // Optional: eigener Ablageort fuer .obj (-o) und .test (-t) statt des Projektverzeichnisses
    ermittleAusgabeDatei(argc, argv, "-o", absprAktiv ? ".kep" : ".obj",  quellcodeDatei, machineCodeFileName, sizeof(machineCodeFileName));
    ermittleAusgabeDatei(argc, argv, "-t", ".test", quellcodeDatei, testFileName,        sizeof(testFileName));

    ensureFileExtension(inputFileName, ".asm", sizeof(inputFileName));
}

// Entfernt Ergebnisdateien eines frueheren Laufs, damit nach einem Fehler keine veralteten Dateien liegen bleiben.
static void entferneAlteErgebnisse(void) {
    remove(logFileName);
    remove(machineCodeFileName);
    remove(hilfsFileName);
    remove(symFileName);
    remove(testFileName);
    remove(dmpFileName);
}


static void gibMakrosFrei(void) {
    for (int i = 0; i < macroCount; i++) {
        free(macros[i].macroParsedLines);
    }
    free(macros);
    macros = NULL;
}

// ----------------------------------------
// Adressen fuer adr(name) und abstand(von,bis) (ab c82ass 1.01-018, Doku 4.23).
// Pass 0 kennt keine Adressen. Der erste Gebrauch von adr oder abstand startet daher Probelaeufe: der Assembler ruft
// sich selbst mit denselben Argumenten plus den versteckten Optionen --adrein=<Datei> und --adraus=<Datei> auf.
// Ein Probelauf endet nach Pass 2 und schreibt die Adressen aller Marken (ohne Literalmarken) in die Ausgabetabelle.
// Lauf 1 hat keine Eingabetabelle (alle Werte 0), Lauf z liest die Ausgabe von Lauf z-1; gleichen sich Eingabe und
// Ausgabe, ist die Tabelle fertig (hoechstens ADR_MAX_LAEUFE Laeufe). Der eigentliche Lauf rechnet dann mit ihr und
// prueft nach Pass 2, dass die abgefragten Marken die benutzten Adressen haben.
#define ADR_MAX_LAEUFE 8
#define ADR_BEFEHL_GROESSE 16384
#define ADR_LOG_ZEILEN 100

typedef struct {
    char name[MAX_SYMBOL_LENGTH];
    long wert;
} AdrEintrag;

typedef struct {
    AdrEintrag *e;
    int n;
    int kap;
} AdrTabelle;

static char adrEinDatei[1024] = "";      // --adrein=: Eingabetabelle eines Probelaufs
static char adrAusDatei[1024] = "";      // --adraus=: gesetzt = dieser Lauf ist ein Probelauf
static char adrDbgZiel[1024] = "";       // --adrdbg=: Debugdatei, in die dieser Probelauf $NOTE, $TRACE und $DUMP schreibt (nur mit --adraus=)
static FILE *adrDbgF = NULL;             // die geoeffnete Debugdatei (erst beim ersten Schreiben)
static int probeAusgabeAktiv = 0;        // 1 = --probeausgabe: der Aufrufer zeigt die Debugausgabe jedes Probelaufs an
static AdrTabelle adrTab = {NULL, 0, 0}; // Tabelle, aus der adrWert liest (Probelauf: Eingabe, sonst die fertige Tabelle)
static AdrTabelle adrBenutzt = {NULL, 0, 0};   // (Name, benutzter Wert) jeder Abfrage des eigentlichen Laufs
static int adrTabFertig = 0;
static int adrLaeufe = 0;
static int adrArgc = 0;
static char **adrArgv = NULL;
static char adrBefehl[ADR_BEFEHL_GROESSE] = "";

static void adrTabelleFreigeben(AdrTabelle *t) {
    free(t->e);
    t->e = NULL;
    t->n = 0;
    t->kap = 0;
}

static void adrFreigeben(void) {
    if (adrDbgF != NULL) { fclose(adrDbgF); adrDbgF = NULL; }
    adrTabelleFreigeben(&adrTab);
    adrTabelleFreigeben(&adrBenutzt);
    if (adrArgv != NULL) {
        for (int i = 0; i < adrArgc; i++) free(adrArgv[i]);
        free(adrArgv);
        adrArgv = NULL;
    }
    adrArgc = 0;
}

// Sichert die Argumente (nach bereinigeParameter) fuer die Probelaeufe.
static void adrArgumenteSichern(int argc, char *argv[]) {
    adrArgv = (char **)calloc((size_t)argc + 1, sizeof(char *));
    if (adrArgv == NULL) {
        PRINT_FEHLER("%s", "Speicherzuweisung fehlgeschlagen.");
        exit(RC_FEHLER);
    }
    for (int i = 0; i < argc; i++) {
        adrArgv[i] = strdup(argv[i] != NULL ? argv[i] : "");
        if (adrArgv[i] == NULL) {
            adrArgc = i;
            adrFreigeben();
            PRINT_FEHLER("%s", "Speicherzuweisung fehlgeschlagen.");
            exit(RC_FEHLER);
        }
    }
    adrArgc = argc;
}

static void adrTabelleAnfuegen(AdrTabelle *t, const char *name, long wert) {
    if (t->n >= t->kap) {
        int kapNeu = t->kap == 0 ? 64 : t->kap * 2;
        AdrEintrag *p = (AdrEintrag *)realloc(t->e, (size_t)kapNeu * sizeof(AdrEintrag));
        if (p == NULL) {
            PRINT_FEHLER("%s", "Speicherzuweisung fehlgeschlagen.");
            exit(RC_FEHLER);
        }
        t->e = p;
        t->kap = kapNeu;
    }
    snprintf(t->e[t->n].name, sizeof(t->e[t->n].name), "%s", name);
    t->e[t->n].wert = wert;
    t->n++;
}

static int adrEintragVergleich(const void *a, const void *b) {
    return strcmp(((const AdrEintrag *)a)->name, ((const AdrEintrag *)b)->name);
}

static void adrTabelleSortieren(AdrTabelle *t) {
    if (t->n > 1) qsort(t->e, (size_t)t->n, sizeof(AdrEintrag), adrEintragVergleich);
}

static const AdrEintrag *adrTabelleSuche(const AdrTabelle *t, const char *name) {
    if (t->n == 0 || strlen(name) >= MAX_SYMBOL_LENGTH) return NULL;
    AdrEintrag schluessel;
    snprintf(schluessel.name, sizeof(schluessel.name), "%s", name);
    return (const AdrEintrag *)bsearch(&schluessel, t->e, (size_t)t->n, sizeof(AdrEintrag), adrEintragVergleich);
}

// Oktalschreibweise (mindestens 4 Stellen, negativ mit '-') in einen Puffer von mindestens 32 Zeichen.
static void adrOktal(long wert, char *puffer, size_t groesse) {
    snprintf(puffer, groesse, "%s%04lo", wert < 0 ? "-" : "", (unsigned long)(wert < 0 ? -wert : wert));
}

// Liest eine Tabelle "name oktalwert" je Zeile. Rueckgabe 0 = ok, sonst 1 mit Text in grund.
static int adrTabelleLesen(const char *datei, AdrTabelle *t, char *grund, size_t gg) {
    FILE *f = fopen(datei, "r");
    if (f == NULL) {
        snprintf(grund, gg, "Die Adresstabelle '%s' konnte nicht geoeffnet werden.", datei);
        return 1;
    }
    char zeile[160];
    int nr = 0;
    while (fgets(zeile, sizeof(zeile), f) != NULL) {
        nr++;
        size_t l = strlen(zeile);
        while (l > 0 && (zeile[l - 1] == '\n' || zeile[l - 1] == '\r')) zeile[--l] = '\0';
        if (l == 0) continue;
        char *blank = strchr(zeile, ' ');
        if (blank == NULL || blank == zeile || (size_t)(blank - zeile) >= MAX_SYMBOL_LENGTH) {
            snprintf(grund, gg, "Die Adresstabelle '%s' ist in Zeile %d fehlerhaft.", datei, nr);
            fclose(f);
            return 1;
        }
        *blank = '\0';
        char *ende = NULL;
        long wert = strtol(blank + 1, &ende, 8);
        if (ende == blank + 1 || *ende != '\0') {
            snprintf(grund, gg, "Die Adresstabelle '%s' ist in Zeile %d fehlerhaft.", datei, nr);
            fclose(f);
            return 1;
        }
        adrTabelleAnfuegen(t, zeile, wert);
    }
    fclose(f);
    adrTabelleSortieren(t);
    return 0;
}

// Schreibt die Adressen aller Marken (ohne Literalmarken) nach Namen sortiert. Rueckgabe 0 = ok.
static int adrTabelleSchreiben(const char *datei) {
    AdrTabelle t = {NULL, 0, 0};
    for (int i = 0; i < symbolCount; i++) {
        if (literalCount > 0 && isLiteralInTable(symbolTable[i].symbol)) continue;
        adrTabelleAnfuegen(&t, symbolTable[i].symbol, (long)symbolTable[i].address);
    }
    adrTabelleSortieren(&t);
    FILE *f = fopen(datei, "w");
    if (f == NULL) {
        adrTabelleFreigeben(&t);
        return 1;
    }
    for (int i = 0; i < t.n; i++) {
        char o[40];
        adrOktal(t.e[i].wert, o, sizeof(o));
        fprintf(f, "%s %s\n", t.e[i].name, o);
    }
    int rc = (fclose(f) != 0);
    adrTabelleFreigeben(&t);
    return rc;
}

// Vergleicht zwei sortierte Tabellen. Rueckgabe 0 = gleich, sonst 1 mit der ersten Abweichung als Text.
static int adrTabellenVergleich(const AdrTabelle *vor, const AdrTabelle *neu, char *text, size_t g) {
    int i = 0, k = 0;
    char o1[40], o2[40];
    while (i < vor->n || k < neu->n) {
        int c = (i >= vor->n) ? 1 : (k >= neu->n) ? -1 : strcmp(vor->e[i].name, neu->e[k].name);
        if (c == 0) {
            if (vor->e[i].wert != neu->e[k].wert) {
                adrOktal(vor->e[i].wert, o1, sizeof(o1));
                adrOktal(neu->e[k].wert, o2, sizeof(o2));
                snprintfGekuerzt(text, g, "Marke \"%s\": Adresse %s im vorigen Probelauf, %s im letzten", vor->e[i].name, o1, o2);
                return 1;
            }
            i++;
            k++;
        } else if (c < 0) {
            adrOktal(vor->e[i].wert, o1, sizeof(o1));
            snprintfGekuerzt(text, g, "Marke \"%s\": Adresse %s im vorigen Probelauf, fehlt im letzten", vor->e[i].name, o1);
            return 1;
        } else {
            adrOktal(neu->e[k].wert, o2, sizeof(o2));
            snprintfGekuerzt(text, g, "Marke \"%s\": fehlt im vorigen Probelauf, Adresse %s im letzten", neu->e[k].name, o2);
            return 1;
        }
    }
    return 0;
}

// Haengt s an den Befehlspuffer an. Rueckgabe 0 = ok, 1 = Puffer zu klein.
static int adrAnhaengen(size_t *len, const char *s) {
    size_t l = strlen(s);
    if (*len + l + 1 > sizeof(adrBefehl)) return 1;
    memcpy(adrBefehl + *len, s, l + 1);
    *len += l;
    return 0;
}

// Haengt ein Argument mit Anfuehrungszeichen an (POSIX: '...' mit '\'' fuer ein ', Windows: "..." ohne " und %).
static int adrArgumentAnhaengen(size_t *len, const char *s) {
#ifdef _WIN32
    if (strchr(s, '"') != NULL || strchr(s, '%') != NULL) return 1;
    if (adrAnhaengen(len, "\"") != 0) return 1;
    size_t l = strlen(s), rueck = 0;
    while (rueck < l && s[l - 1 - rueck] == '\\') rueck++;
    if (adrAnhaengen(len, s) != 0) return 1;
    for (size_t i = 0; i < rueck; i++) if (adrAnhaengen(len, "\\") != 0) return 1;   // Rueckstriche vor dem schliessenden " verdoppeln
    return adrAnhaengen(len, "\"");
#else
    if (adrAnhaengen(len, "'") != 0) return 1;
    for (const char *p = s; *p != '\0'; p++) {
        if (*p == '\'') { if (adrAnhaengen(len, "'\\''") != 0) return 1; }
        else { char z[2] = {*p, '\0'}; if (adrAnhaengen(len, z) != 0) return 1; }
    }
    return adrAnhaengen(len, "'");
#endif
}

// Baut die Kommandozeile eines Probelaufs. Rueckgabe 0 = ok, 1 = Fehler (zu lang oder Zeichen nicht darstellbar).
static int adrKommandozeile(int mitEingabe) {
    size_t len = 0;
    adrBefehl[0] = '\0';
#ifdef _WIN32
    if (adrAnhaengen(&len, "\"") != 0) return 1;
#endif
    for (int i = 0; i < adrArgc; i++) {
        if (i > 0 && adrAnhaengen(&len, " ") != 0) return 1;
        if (adrArgumentAnhaengen(&len, adrArgv[i]) != 0) return 1;
    }
    char opt[1100];
    if (mitEingabe) {
        snprintf(opt, sizeof(opt), "--adrein=%s", adr1Datei);
        if (adrAnhaengen(&len, " ") != 0 || adrArgumentAnhaengen(&len, opt) != 0) return 1;
    }
    snprintf(opt, sizeof(opt), "--adraus=%s", adr2Datei);
    if (adrAnhaengen(&len, " ") != 0 || adrArgumentAnhaengen(&len, opt) != 0) return 1;
    if (probeAusgabeAktiv) {   // --probeausgabe: der Probelauf legt $NOTE, $TRACE und $DUMP in diese Datei
        snprintf(opt, sizeof(opt), "--adrdbg=%s", adrDbgDatei);
        if (adrAnhaengen(&len, " ") != 0 || adrArgumentAnhaengen(&len, opt) != 0) return 1;
    }
    if (adrAnhaengen(&len, " > " NULL_GERAET " 2> ") != 0 || adrArgumentAnhaengen(&len, adrLogDatei) != 0) return 1;
#ifdef _WIN32
    if (adrAnhaengen(&len, "\"") != 0) return 1;
#endif
    return 0;
}

static void adrAufraeumen(void) {
    remove(adr1Datei);
    remove(adr2Datei);
    remove(adrLogDatei);
    remove(adrDbgDatei);
    entferneAlteErgebnisse();   // .log, .sym der Probelaeufe
}

static void adrAbbruch(void) {
    adrAufraeumen();
    PRINT_FEHLER("%s", "Abbruch.");
    adrFreigeben();
    exit(RC_FEHLER);
}

// Fuehrt Probelauf nr aus. Rueckgabe: Rueckgabewert des Laufs, -1 wenn er nicht gestartet werden konnte.
// Zeigt die Debugausgabe eines Probelaufs (--probeausgabe): jede Zeile mit "Probelauf <nr>: " davor, gruen wie die Ausgabe des
// eigentlichen Laufs. Die Zeilen stehen vor einer eventuellen Fehlermeldung des Probelaufs.
static void adrDebugAnzeigen(int nr) {
    FILE *f = fopen(adrDbgDatei, "r");
    if (f == NULL) return;   // der Probelauf hat nichts ausgegeben
    char zeile[4096];
    int anfang = 1;
    fflush(stdout);
    while (fgets(zeile, sizeof(zeile), f) != NULL) {
        size_t l = strlen(zeile);
        int ende = (l > 0 && zeile[l - 1] == '\n');
        if (ende) zeile[l - 1] = '\0';
        if (anfang) fprintf(stderr, "%sProbelauf %d: ", _gruen, nr);
        fputs(zeile, stderr);
        if (ende) fprintf(stderr, "%s\n", _normal);
        anfang = ende;
    }
    if (!anfang) fprintf(stderr, "%s\n", _normal);   // letzte Zeile ohne Zeilenende
    fclose(f);
}

static int adrProbelauf(int nr) {
    if (adrKommandozeile(nr > 1) != 0) return -1;
    fflush(stdout);
    fflush(stderr);
    remove(adr2Datei);
    if (probeAusgabeAktiv) remove(adrDbgDatei);
    int rc = system(adrBefehl);
    if (probeAusgabeAktiv) adrDebugAnzeigen(nr);
#ifndef _WIN32
    if (rc == -1) return -1;
    if (WIFEXITED(rc)) return WEXITSTATUS(rc);
    if (WIFSIGNALED(rc)) return 128 + WTERMSIG(rc);
#endif
    return rc;
}

static void adrProbelaufFehler(int nr, int rc) {
    if (rc == -1) {
        PRINT_FEHLER("Probelauf %d fuer adr/abstand konnte nicht gestartet werden (Kommandozeile zu lang oder nicht darstellbar).", nr);
    } else {
        PRINT_FEHLER("Probelauf %d fuer adr/abstand fehlgeschlagen (Rueckgabewert %d).", nr, rc);
        PRINT_FEHLER("Kommandozeile: %s", adrBefehl);
        FILE *f = fopen(adrLogDatei, "r");
        if (f != NULL) {
            char zeile[1024];
            int z = 0;
            while (z < ADR_LOG_ZEILEN && fgets(zeile, sizeof(zeile), f) != NULL) {
                fputs(zeile, stderr);
                z++;
            }
            fclose(f);
        }
    }
    adrAbbruch();
}

#define ADR_VERLAUF_MARKEN 20

// Diagnose bei fehlender Konvergenz: Adressen jeder wechselnden Marke ueber alle Probelaeufe und, falls vorhanden, der Zyklus.
// h[0..n-1] sind die Ausgabetabellen der Probelaeufe 1..n.
static void adrVerlaufMelden(const AdrTabelle *h, int n) {
    char zeile[512], o[40];
    int gezeigt = 0, weitere = 0;
    PRINT_FEHLER("Verlauf der Adressen fuer adr/abstand (Probelauf 1 bis %d), nur Marken mit wechselnden Werten:", n);
    for (int t = 0; t < n; t++) {
        for (int i = 0; i < h[t].n; i++) {
            const char *name = h[t].e[i].name;
            int erste = 1, wechselt = 0;
            for (int j = 0; j < t && erste; j++) if (adrTabelleSuche(&h[j], name) != NULL) erste = 0;
            if (!erste) continue;                       // Name schon aus einem frueheren Lauf behandelt
            const AdrEintrag *e0 = adrTabelleSuche(&h[0], name);
            for (int j = 1; j < n && !wechselt; j++) {
                const AdrEintrag *ej = adrTabelleSuche(&h[j], name);
                if ((e0 == NULL) != (ej == NULL) || (e0 != NULL && e0->wert != ej->wert)) wechselt = 1;
            }
            if (!wechselt) continue;
            if (gezeigt >= ADR_VERLAUF_MARKEN) { weitere++; continue; }
            int l = snprintfGekuerzt(zeile, sizeof(zeile), "  Marke \"%s\":", name);
            for (int j = 0; j < n && l > 0 && (size_t)l < sizeof(zeile); j++) {
                const AdrEintrag *ej = adrTabelleSuche(&h[j], name);
                if (ej != NULL) adrOktal(ej->wert, o, sizeof(o)); else snprintf(o, sizeof(o), "fehlt");
                l += snprintfGekuerzt(zeile + l, sizeof(zeile) - (size_t)l, " %s", o);
            }
            PRINT_FEHLER("%s", zeile);
            gezeigt++;
        }
    }
    if (weitere > 0) PRINT_FEHLER("  ... und %d weitere Marken mit wechselnden Werten.", weitere);
    char text[64];
    for (int j = n - 2; j >= 0; j--) {
        if (adrTabellenVergleich(&h[j], &h[n - 1], text, sizeof(text)) == 0) {
            PRINT_FEHLER("Die Tabelle von Probelauf %d gleicht der von Probelauf %d: die Adressen wiederholen sich im Zyklus der Laenge %d.", n, j + 1, n - 1 - j);
            return;
        }
    }
    PRINT_FEHLER("Die Tabellen wiederholen sich nicht innerhalb von %d Probelaeufen (kein Zyklus erkannt).", n);
}

// Startet die Probelaeufe und laedt die fertige Tabelle nach adrTab.
static void adrTabelleBeschaffen(void) {
    AdrTabelle hist[ADR_MAX_LAEUFE];             // Ausgabetabelle jedes Probelaufs, fuer die Diagnose bei fehlender Konvergenz
    char text[600], grund[400];
    int n = 0, fertig = 0;
    for (int i = 0; i < ADR_MAX_LAEUFE; i++) { hist[i].e = NULL; hist[i].n = 0; hist[i].kap = 0; }
    for (int nr = 1; nr <= ADR_MAX_LAEUFE; nr++) {
        int rc = adrProbelauf(nr);
        if (rc != 0) {
            for (int i = 0; i < n; i++) adrTabelleFreigeben(&hist[i]);
            adrProbelaufFehler(nr, rc);
        }
        adrLaeufe = nr;
        if (adrTabelleLesen(adr2Datei, &hist[nr - 1], grund, sizeof(grund)) != 0) {
            PRINT_FEHLER("Probelauf %d fuer adr/abstand: %s", nr, grund);
            for (int i = 0; i < nr; i++) adrTabelleFreigeben(&hist[i]);
            adrAbbruch();
        }
        n = nr;
        if (nr >= 2 && adrTabellenVergleich(&hist[nr - 2], &hist[nr - 1], text, sizeof(text)) == 0) {
            fertig = 1;
            break;
        }
        if (nr == ADR_MAX_LAEUFE) {
            adrTabellenVergleich(&hist[nr - 2], &hist[nr - 1], text, sizeof(text));
            break;
        }
        remove(adr1Datei);                // Ausgabe dieses Laufs = Eingabe des naechsten
        if (rename(adr2Datei, adr1Datei) != 0) {
            PRINT_FEHLER("Die Adresstabelle '%s' konnte nicht umbenannt werden.", adr2Datei);
            for (int i = 0; i < n; i++) adrTabelleFreigeben(&hist[i]);
            adrAbbruch();
        }
    }
    if (!fertig) {
        PRINT_FEHLER("Die Adressen fuer adr/abstand konvergieren nach %d Probelaeufen nicht: %s", ADR_MAX_LAEUFE, text);
        adrVerlaufMelden(hist, n);
        for (int i = 0; i < n; i++) adrTabelleFreigeben(&hist[i]);
        adrAbbruch();
    }
    adrTabelleFreigeben(&adrTab);
    adrTab = hist[n - 1];                 // fertige Tabelle uebernehmen, die uebrigen freigeben
    hist[n - 1].e = NULL; hist[n - 1].n = 0; hist[n - 1].kap = 0;
    for (int i = 0; i < n; i++) adrTabelleFreigeben(&hist[i]);
    adrAufraeumen();
    printf("Adressen fuer adr/abstand: %d Probelaeufe, %d Marken.\n", adrLaeufe, adrTab.n);
}

static void adrBenutztMerken(const char *name, long wert) {
    for (int i = 0; i < adrBenutzt.n; i++) {
        if (strcmp(adrBenutzt.e[i].name, name) == 0) return;
    }
    adrTabelleAnfuegen(&adrBenutzt, name, wert);
}

// Nach Pass 2 des eigentlichen Laufs: Hat jede abgefragte Marke die benutzte Adresse? Rueckgabe 0 = ja.
static int adrPruefeNachPass2(void) {
    int fehler = 0;
    for (int i = 0; i < adrBenutzt.n; i++) {
        int gefunden = 0;
        for (int k = 0; k < symbolCount; k++) {
            if (strcmp(symbolTable[k].symbol, adrBenutzt.e[i].name) != 0) continue;
            gefunden = 1;
            if ((long)symbolTable[k].address != adrBenutzt.e[i].wert) {
                char o1[40], o2[40];
                adrOktal((long)symbolTable[k].address, o1, sizeof(o1));
                adrOktal(adrBenutzt.e[i].wert, o2, sizeof(o2));
                PRINT_FEHLER("adr/abstand: Die Adresse der Marke \"%s\" ist nach Pass 2 %s, abgefragt und verwendet wurde %s.", adrBenutzt.e[i].name, o1, o2);
                fehler = 1;
            }
            break;
        }
        if (!gefunden) {
            PRINT_FEHLER("adr/abstand: Die Marke \"%s\" kommt nach Pass 2 nicht in der Symboltabelle vor.", adrBenutzt.e[i].name);
            fehler = 1;
        }
    }
    return fehler;
}

// Wertet --adrein= und --adraus= aus (versteckte Optionen der Probelaeufe) und liest die Eingabetabelle.
static void adrOptionenAuswerten(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (a == NULL) continue;
        if (strcmp(a, "-p") == 0 || strcmp(a, "-s") == 0 || strcmp(a, "-o") == 0 || strcmp(a, "-t") == 0 || strcmp(a, "-m") == 0) {
            i++;
            continue;
        }
        char *ziel = NULL;
        if (gleichOhneGrossKlein(a, "--probeausgabe")) { probeAusgabeAktiv = 1; continue; }
        if (strncmp(a, "--adrein=", 9) == 0) ziel = adrEinDatei;
        else if (strncmp(a, "--adraus=", 9) == 0) ziel = adrAusDatei;
        else if (strncmp(a, "--adrdbg=", 9) == 0) ziel = adrDbgZiel;
        if (ziel == NULL) continue;
        size_t l = strlen(a + 9);
        if (l == 0 || l >= 1024) {
            PRINT_FEHLER("Die Option '%.20s' braucht einen Dateinamen mit 1 bis 1023 Zeichen.", a);
            PRINT_FEHLER("%s", "Abbruch.");
            exit(RC_FEHLER);
        }
        memcpy(ziel, a + 9, l + 1);
    }
    if (adrEinDatei[0] != '\0' && adrAusDatei[0] == '\0') {
        PRINT_FEHLER("%s", "Die Option --adrein= gilt nur zusammen mit --adraus=.");
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }
    if (adrDbgZiel[0] != '\0' && adrAusDatei[0] == '\0') {
        PRINT_FEHLER("%s", "Die Option --adrdbg= gilt nur zusammen mit --adraus=.");
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }
    if (adrEinDatei[0] != '\0') {
        char grund[400];
        if (adrTabelleLesen(adrEinDatei, &adrTab, grund, sizeof(grund)) != 0) {
            PRINT_FEHLER("%s", grund);
            PRINT_FEHLER("%s", "Abbruch.");
            adrFreigeben();
            exit(RC_FEHLER);
        }
    }
}

// Adresse einer Marke fuer adr(name) und abstand(von,bis) (aufgerufen aus ca82_makros.c).
// Rueckgabe 0 = ok (Wert in *wert), 1 = Fehler (Grund in grund). Bei --pass0 immer 0 mit Wert 0.
int adrWert(const char *name, long long *wert, char *grund, size_t gg) {
    if (nurPass0Aktiv) {
        *wert = 0;
        return 0;
    }
    int probe = (adrAusDatei[0] != '\0');
    if (!probe && !adrTabFertig) {
        adrTabFertig = 1;
        adrTabelleBeschaffen();
    }
    const AdrEintrag *e = adrTabelleSuche(&adrTab, name);
    if (e == NULL) {
        *wert = 0;
        if (probe) return 0;   // Probelauf: fehlende Marke (auch in Lauf 1) = 0, ohne Meldung
        snprintf(grund, gg, "die Marke \"%.32s\" kommt nach Pass 2 nicht in der Symboltabelle vor", name);
        return 1;
    }
    *wert = e->wert;
    if (!probe) adrBenutztMerken(name, e->wert);
    return 0;
}

// 1, solange adr und abstand in diesem Lauf noch keine endgueltigen Adressen liefern: in einem Probelauf (1 bis 8, --adraus=)
// und bei --pass0, wo sie 0 liefern; sonst 0, auch in einem Quelltext ohne adr und abstand. Aufgerufen aus ca82_makros.c fuer
// $PROBE (ab c82ass 1.01-020, Doku 4.23).
int adrNochImLauf(void) {
    return (adrAusDatei[0] != '\0') || nurPass0Aktiv;
}

// Legt eine Zeile von $NOTE, $TRACE oder $DUMP in die Debugdatei, wenn dieser Lauf ein Probelauf mit --adrdbg= ist (Aufruf aus
// makroAusgabeZeile, ca82_makros.c; ab c82ass 1.01-021, Doku 4.24). Rueckgabe 1 = abgelegt, 0 = nicht: die Zeile geht dann wie bisher
// auf STDERR. Die Datei wird erst beim ersten Schreiben geoeffnet (angehaengt: der Aufrufer loescht sie vor jedem Probelauf); ist
// sie nicht zu oeffnen, bleibt es beim bisherigen Verhalten.
int adrDebugZeile(const char *zeile) {
    if (adrDbgZiel[0] == '\0') return 0;
    if (adrDbgF == NULL) {
        adrDbgF = fopen(adrDbgZiel, "a");
        if (adrDbgF == NULL) { adrDbgZiel[0] = '\0'; return 0; }
    }
    fprintf(adrDbgF, "%s\n", zeile);
    fflush(adrDbgF);
    return 1;
}

// Meldungen am Ende eines erfolgreichen Laufs (Warnungen, Querverweisliste, Ausgabedateien).
static void meldeErfolg(void) {
    // Berichte (-WARN=..., --xref) stehen zusaetzlich im .log (angehaengt hinter Listing und Symboltabelle)
    if (warnSym || warnSpr || warnTot || xrefAktiv || makrolisteAktiv) {
        berichtLog = fopen(logFileName, "a");
        if (berichtLog) fprintf(berichtLog, "\n");
        else PRINT_WARNUNG("Die Berichte konnten nicht an '%s' angehaengt werden.", logFileName);
    }
    if (warnSym) {
        printf("\n");
        pruefeUnbenutzteSymbole();
    }
    if (warnSpr) {
        printf("\n");
        pruefeSprungziele();
    }
    if (warnTot) {
        printf("\n");
        pruefeToterCode();
    }
    if (xrefAktiv) {
        printf("\n");
        erzeugeQuerverweisliste();
    }
    if (makrolisteAktiv) {
        printf("\n");
        makroListeAusgeben();
    }
    if (objWortAnzahl == 0) {
        printf("\n");
        PRINT_WARNUNG("%s", "Das Programm enthaelt keine Befehle und keine Daten; die Objektdatei ist leer.");
    }
    if (absprAktiv && absprBahnAnzahl > 0) {
        printf("\n");
        PRINT_WARNUNG("Bei --ABSPR werden %d Wort(e) auf die Zellen 0002 bis 0037 geladen und ueberschreiben das KEP (nur 0000 und 0001, die Sprungzellen, sind erlaubt):", absprBahnAnzahl);
        for (int i = 0; i < absprBahnAnzahl && i < 64; i++) PRINT_WARNUNG("  Wort auf Zelle %04lo", absprBahnAdresse[i]);
        if (absprBahnAnzahl > 64) {
            char rest[64];
            snprintf(rest, sizeof(rest), "  ... und %d weitere", absprBahnAnzahl - 64);
            PRINT_WARNUNG("%s", rest);
        }
    }
    if (absprAktiv && leitadresseKennzeichen == 0 && startAdresse != 0) {
        printf("\n");
        PRINT_WARNUNG("Bei --ABSPR mit Pragma LEITADRESSE 00 wird die Startadresse %04o nicht auf die Operanden addiert: der Leitbefehl lautet %o 240, die Operanden bleiben unveraendert.", startAdresse, startAdresse);
        PRINT_WARNUNG("%s", "Ist der Quelltext relativ geschrieben, das Pragma weglassen; ist er absolut geschrieben, start ohne Operand verwenden.");
    }
    if (absprAktiv && absprAnzahl0209 > 0) {
        printf("\n");
        PRINT_WARNUNG("Bei --ABSPR werden %d Zeilen mit Kennzeichen 02..09 (Pragma LEITADRESSE) nicht umgesetzt und fehlen in der .kep-Datei.", absprAnzahl0209);
    }
    if (absprAktiv && absprAnzahl01 == 0) {
        printf("\n");
        if (leitadresseKennzeichen == 0)
            PRINT_MSG("%s", "Hinweis: --ABSPR mit Pragma LEITADRESSE 00: Der Quelltext gilt als absolut adressiert, es wird keine Adresse umgerechnet.");
        else
            PRINT_WARNUNG("%s", "Im Objektcode fuer --ABSPR gibt es kein Kennzeichen 01 mehr (Pragma LEITADRESSE oder keine Befehle): es wird keine Adresse umgerechnet.");
    }
    if (berichtLog) { fclose(berichtLog); berichtLog = NULL; }
    printf("\n");
    if (absprAktiv) printf("Ausgabe als absolut adressierter KEP-Lochstreifen (binaer, R300-Code) nach: %s\n", machineCodeFileName);
    else printf("Ausgabe als binaer codierte Objektdatei (R300-Lochstreifen) nach: %s\n", machineCodeFileName);
    printf("Ausgabe der formatierten Speicherbelegung nach: %s\n", dmpFileName);
    printf("Ausgabe der Testdatei (Spalten 1,3,4,5 fuer K1=00/01) nach: %s\n", testFileName);
}

// Fuehrt Einlesen und die Paesse 0 bis 3 aus. Rueckgabe: RC_OK oder RC_FEHLER.
static int assembliere(void) {
    // Kleine anfangen mit macroCapacity
    macros = (macroDefinitionen *)malloc(macroCapacity * sizeof(macroDefinitionen));
    if (!macros) {
        fprintf(stderr, "Speicherzuweisung für Makros fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }

    resetParsedLinesArrays(lineAsmAufgeloest, lineCountAsmAufgeloest);
    resetParsedLinesArrays(lineAsmAufgeloestTemp, lineCountAsmAufgeloestTemp);

    // Einlesen
    ladeAssemblerZeilen(inputFileName);
    if ((is_error_abs != 0) || (is_error != 0)) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch.");
        gibMakrosFrei();
        return RC_FEHLER;
    }
    printf("\n");
    if (leitadressePragmaGesetzt) {
        PRINT_MSG("Leitadresse: %02d", leitadresseKennzeichen);
    }

    printf("\n");
    printf("Pass 0\n");
    pass0();
    if ( (is_error != 0)) {
        printf("\n");
        meldeListingFehlerAufStderr(lineAsmAufgeloest, lineCountAsmAufgeloest);
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
        gibMakrosFrei();
        return RC_FEHLER;
    }
    if (makrolisteAktiv) makroListeSichern();
    gibMakrosFrei();
    if (nurPass0Aktiv) return RC_OK;   // --pass0: Pass 1 bis 3, Ausgabedateien und Berichte entfallen
    printf("\n");

    printf("Pass 1\n");
    pass1(logFileName);  //.mac .log
    if ((is_error != 0)) {
        printf("\n");
        meldeListingFehlerAufStderr(lineAsmAufgeloestTemp, lineCountAsmAufgeloestTemp);
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
        return RC_FEHLER;
    }
    printf("\n");

    printf("Pass 2\n");
    pass2MitOptimierer( logFileName, symFileName);
    if (is_error2 != 0) {
        printf("\n");
        meldeListingFehlerAufStderr(lineAsmAufgeloest, lineCountAsmAufgeloest);
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
        return RC_FEHLER;
    }
    if (adrAusDatei[0] != '\0') {   // Probelauf fuer adr/abstand: Adressen ablegen, kein Pass 3, keine Ergebnisdateien
        if (adrTabelleSchreiben(adrAusDatei) != 0) {
            PRINT_FEHLER("Die Adresstabelle '%s' konnte nicht geschrieben werden.", adrAusDatei);
            return RC_FEHLER;
        }
        return RC_OK;
    }
    if (adrBenutzt.n > 0 && adrPruefeNachPass2() != 0) {   // abgefragte Marken muessen die benutzte Adresse haben
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch.");
        return RC_FEHLER;
    }
    printf("\n");

    printf("Pass 3\n");
    pass3( machineCodeFileName, hilfsFileName, dmpFileName, testFileName);
    if (is_error3 != 0) {
        printf("\n");
        // Unvollstaendige Ergebnisdateien nicht liegen lassen (sonst koennten sie versehentlich geladen werden).
        // .log, .sym und .dmp bleiben fuer die Fehlersuche erhalten.
        remove(machineCodeFileName);
        remove(hilfsFileName);
        remove(testFileName);
        PRINT_FEHLER("%s", "Abbruch. Keine Objekt-, mqo- und Testdatei erzeugt (.log, .sym, .dmp zur Fehlersuche vorhanden).");
        return RC_FEHLER;
    }
    if (is_error != 0) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch.");
        return RC_FEHLER;
    }
    meldeErfolg();
    return RC_OK;
}

int main(int argc, char *argv[]) {
    atexit(fehlerZusammenfassung);   // Zusammenfassung der Fehler auch bei exit() mitten in einem Pass
    opsymProgrammpfadSetzen(argv[0]);   // Ort des Programms merken: die Standardtabelle c82ass.opsym wird auch neben dem Binary gesucht
    argc = bereinigeParameter(argc, argv);
    adrArgumenteSichern(argc, argv);   // fuer die Probelaeufe von adr/abstand

    // --pass0 gilt nur fuer einen Assemblerlauf, nicht zusammen mit -h, --help, --version oder --opsyms
    int pass0Wunsch = 0, nurAuskunft = 0;
    for (int i = 1; i < argc; i++) {
        if (argv[i] == NULL) continue;
        if (istPass0Option(argv[i])) pass0Wunsch = 1;
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "--version") == 0 || gleichOhneGrossKlein(argv[i], "--opsyms")) nurAuskunft = 1;
    }
    if (pass0Wunsch && !nurAuskunft) leiteAusgabeFuerPass0um();

    greetings();
    for (int i = 1; i < argc; i++) if (argv[i] != NULL && strcmp(argv[i], "--xref") == 0) xrefAktiv = 1;
    for (int i = 1; i < argc; i++) if (argv[i] != NULL && gleichOhneGrossKlein(argv[i], "--makros")) makrolisteAktiv = 1;
    verarbeiteWarnOptionen(argc, argv);
    for (int i = 1; i < argc; i++) if (argv[i] != NULL && istAbsprOption(argv[i])) absprAktiv = 1;
    for (int i = 1; i < argc; i++) if (argv[i] != NULL && (gleichOhneGrossKlein(argv[i], "--no-opt") || gleichOhneGrossKlein(argv[i], "--NOOPT"))) optAktiv = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--version") == 0) {
            return RC_OK;   // die Versionszeile hat greetings() schon ausgegeben
        }
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printUsage(argv[0]);
            return RC_OK;
        }
        if (gleichOhneGrossKlein(argv[i], "--opsyms")) {
            return opsymAusgabe();   // Standardtabelle der Namen fuer Operationscodes, ohne Assemblerlauf
        }
    }

    if (pruefeOptionen(argc, argv) != RC_OK) return RC_FEHLER;

    adrOptionenAuswerten(argc, argv);
    pruefeProjektverzeichnis(argc, argv, projektVerzeichnis, printUsage);
    pruefeDatei(argc, argv, "-s", ".asm", projektVerzeichnis, quellcodeDatei, sizeof(quellcodeDatei));
    bildeDateinamen(argc, argv);

    // Prüfung, ob die Datei existiert
    if (!doesPathExist(inputFileName)) {
        PRINT_FEHLER("Die Quellcode-Datei existiert nicht: %s", inputFileName);
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }

    if (!nurPass0Aktiv && adrAusDatei[0] == '\0') entferneAlteErgebnisse();   // --pass0 schreibt nichts und laesst vorhandene Ergebnisse liegen; ein Probelauf loescht nichts
    int rc = assembliere();
    adrFreigeben();
    return rc;
}
