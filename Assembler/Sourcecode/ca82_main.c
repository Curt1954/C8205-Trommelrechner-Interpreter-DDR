// ca82_main.c - Hauptprogramm: Optionen, Dateinamen, Ablauf der Paesse
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"
#include "ca82_fluss.h"


// ------------------------------------------


static char projektVerzeichnis[512] = {0};

static char quellcodeDatei[512] = "";

static char logFileName[1024] = "";
static char machineCodeFileName[1024] = "";
static char hilfsFileName[1024] = "";
static char symFileName[1024] = "";
static char testFileName[1024] = "";
static char dmpFileName[1024] = "";



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
        ergebnis = snprintf(ziel, zielGroesse, "%s%s%.*s%s", wert, endetMitTrenner ? "" : "/",
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
static void bildeDateinamen(int argc, char *argv[]) {
    const char *punkt = strrchr(quellcodeDatei, '.');
    int namensLaenge = punkt ? (int)(punkt - quellcodeDatei) : (int)strlen(quellcodeDatei);

    snprintf(inputFileName, sizeof(inputFileName), "%s/%s", projektVerzeichnis, quellcodeDatei);
    snprintf(logFileName, sizeof(logFileName), "%s/%.*s.log", projektVerzeichnis, namensLaenge, quellcodeDatei);
    snprintf(machineCodeFileName, sizeof(machineCodeFileName), "%s/%.*s.obj", projektVerzeichnis, namensLaenge, quellcodeDatei);
    snprintf(hilfsFileName, sizeof(hilfsFileName), "%s/%.*s.mqo", projektVerzeichnis, namensLaenge, quellcodeDatei);
    snprintf(symFileName, sizeof(symFileName), "%s/%.*s.sym", projektVerzeichnis, namensLaenge, quellcodeDatei);
    snprintf(testFileName, sizeof(testFileName), "%s/%.*s.test", projektVerzeichnis, namensLaenge, quellcodeDatei);
    snprintf(dmpFileName, sizeof(dmpFileName), "%s/%.*s.dmp", projektVerzeichnis, namensLaenge, quellcodeDatei);

    // Optional: eigener Ablageort fuer .obj (-o) und .test (-t) statt des Projektverzeichnisses
    ermittleAusgabeDatei(argc, argv, "-o", ".obj",  quellcodeDatei, machineCodeFileName, sizeof(machineCodeFileName));
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

// Meldungen am Ende eines erfolgreichen Laufs (Warnungen, Querverweisliste, Ausgabedateien).
static void meldeErfolg(void) {
    // Berichte (-WARN=..., --xref) stehen zusaetzlich im .log (angehaengt hinter Listing und Symboltabelle)
    if (warnSym || warnSpr || warnTot || xrefAktiv) {
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
    if (objWortAnzahl == 0) {
        printf("\n");
        PRINT_WARNUNG("%s", "Das Programm enthaelt keine Befehle und keine Daten; die Objektdatei ist leer.");
    }
    if (berichtLog) { fclose(berichtLog); berichtLog = NULL; }
    printf("\n");
    printf("Ausgabe als Minimalprogramm-Objektdatei nach: %s\n", machineCodeFileName);
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
    gibMakrosFrei();
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
    pass2( logFileName, symFileName);
    if (is_error2 != 0) {
        printf("\n");
        meldeListingFehlerAufStderr(lineAsmAufgeloest, lineCountAsmAufgeloest);
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
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
    argc = bereinigeParameter(argc, argv);

    greetings();
    for (int i = 1; i < argc; i++) if (argv[i] != NULL && strcmp(argv[i], "--xref") == 0) xrefAktiv = 1;
    verarbeiteWarnOptionen(argc, argv);
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--version") == 0) {
            return RC_OK;   // die Versionszeile hat greetings() schon ausgegeben
        }
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printUsage(argv[0]);
            return RC_OK;
        }
    }

    if (pruefeOptionen(argc, argv) != RC_OK) return RC_FEHLER;

    pruefeProjektverzeichnis(argc, argv, projektVerzeichnis, printUsage);
    pruefeDatei(argc, argv, "-s", ".asm", projektVerzeichnis, quellcodeDatei);
    bildeDateinamen(argc, argv);

    // Prüfung, ob die Datei existiert
    if (!doesPathExist(inputFileName)) {
        PRINT_FEHLER("Die Quellcode-Datei existiert nicht: %s", inputFileName);
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER);
    }

    entferneAlteErgebnisse();
    return assembliere();
}
