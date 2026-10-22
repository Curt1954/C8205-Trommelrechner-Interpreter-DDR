// ca82_makros.c - Version 1.00-030 (siehe ca82_version.h)
// Makrodatei und Quelltextmakros einlesen, Makros aufloesen ($IF/$PR/$WDHL/$SPRUNG).
#include "ca82_typen.h"
#include "ca82_makros.h"
#include "ca82_version.h"
#include "ca82_symbole.h"
#include "ca82_berichte.h"
#include <stdarg.h>
#include <errno.h>

macroDefinitionen *macros;          // dynamisch zugewiesenes Array der Makrodefinitionen
int macroCount = 0;
int macroCapacity = INITIAL_SIZE;
char recursiv_macro[128] = "";

int isNumeric(const char *str) {
    while (*str) {
        if (!isdigit(*str)) return 0; // Wenn ein Zeichen kein Digit ist, ist es nicht numerisch
        str++;
    }
    return 1; // Alles sind Ziffern -> Numerisch
}

int macroParameterCompare(const char *a, const char *b, const char *c) {
//printf("DEBUG: a=%s, b=%s, c=%s\n", a, b, c);

    if (isNumeric(a) && isNumeric(c)) { // Falls beide Parameter numerisch sind, vergleiche als Zahlen
        int valA = atoi(a);
        int valC = atoi(c);

        if (strcmp(b, ">") == 0) return valA > valC;
        if (strcmp(b, "<") == 0) return valA < valC;
        if (strcmp(b, "=") == 0) return valA == valC;
        if (strcmp(b, ">=") == 0) return valA >= valC;
        if (strcmp(b, "<=") == 0) return valA <= valC;
    } else { // Falls nicht numerisch, vergleiche alphabetisch
        if (strcmp(b, ">") == 0) return strcmp(a, c) > 0;
        if (strcmp(b, "<") == 0) return strcmp(a, c) < 0;
        if (strcmp(b, "=") == 0) return strcmp(a, c) == 0;
        if (strcmp(b, ">=") == 0) return strcmp(a, c) >= 0;
        if (strcmp(b, "<=") == 0) return strcmp(a, c) <= 0;
    }

    return -1; // Ungültiger Vergleichsoperator
}

#define DATEINAME "c82ass.makros"
// Pfad der Makrodatei; mit Option -m aenderbar. Ohne -m: Arbeitsverzeichnis, sonst Sourcecode/.
static char makroDateiPfad[1024] = DATEINAME;
static int  makroDateiVomBenutzer = 0;

// Setzt den Pfad der Makrodatei (Option -m). Rueckgabe: 0 = ok, -1 = Pfad zu lang.
int makroDateiSetzen(const char *pfad) {
    if (snprintf(makroDateiPfad, sizeof(makroDateiPfad), "%s", pfad) >= (int)sizeof(makroDateiPfad)) return -1;
    makroDateiVomBenutzer = 1;
    return 0;
}

const char *makroDateiName(void) {
    return makroDateiPfad;
}
unsigned int  macrozaehler=1;

int countWords(const char *str) {
    int count = 0;
    int inWord = 0;

    while (*str) {
        if (isspace(*str)) {
            inWord = 0;  // Zeichen ist Leerzeichen → außerhalb eines Wortes
        } else if (!inWord) {
            inWord = 1;  // Erstes Zeichen eines neuen Wortes erkannt
            count++;     // Wortanzahl erhöhen
        }
        str++;  // Nächstes Zeichen prüfen
    }

    return count;
}


// Typpruefung fuer Makro-Parameter ($PRx: $TYPADR | $TYPKON | $TYPABS).
// Geprueft wird der beim Makroaufruf uebergebene Wert `arg`. Rueckgabe 0 = in Ordnung, sonst
// 1 = Fehler; `meldung` enthaelt dann den Text. Die Pruefung laeuft in Pass 0, also bevor die
// Symboltabelle existiert: Sie ist deshalb rein syntaktisch, bei $TYPABS wird zusaetzlich im
// Quelltext nach der Zeile `<arg>: abs ...` gesucht.
static int istSymbolName(const char *t) {
    size_t n = strlen(t);
    if (n == 0 || n > MAX_LABEL_LENGTH) return 0;
    if (!(isalpha((unsigned char)t[0]) || t[0] == '_')) return 0;
    for (size_t k = 1; k < n; k++) {
        if (!(isalnum((unsigned char)t[k]) || t[k] == '_')) return 0;
    }
    return 1;
}

static int pruefeMakroTyp(const char *typ, const char *arg, char *meldung, size_t meldungGroesse) {
    if (strcmp(typ, "$TYPADR") == 0) {
        int ok = 0;
        if (arg[0] == '*') {            // Sternadresse: `*` oder `*+3`, `*-1`
            ok = 1;
            for (const char *q = arg + 1; *q; q++) {
                if (!strchr("+-*/0123456789", *q)) { ok = 0; break; }
            }
        } else {
            ok = istSymbolName(arg);
        }
        if (!ok) {
            snprintf(meldung, meldungGroesse, "Wert \"%s\" ist keine symbolische Adresse (Label oder *)", arg);
            return 1;
        }
        return 0;
    }
    if (strcmp(typ, "$TYPKON") == 0) {
        size_t n = strlen(arg);
        int nurZiffern = (n > 0);
        for (size_t k = 0; k < n; k++) {
            if (!isdigit((unsigned char)arg[k])) { nurZiffern = 0; break; }
        }
        if (!nurZiffern) {
            snprintf(meldung, meldungGroesse, "Wert \"%.100s\" ist keine Konstante", arg);
            return 1;
        }
        int oktal = (arg[0] == '0');
        for (size_t k = 0; k < n; k++) {
            if (arg[k] > '7') oktal = 0;
        }
        if (!oktal) {
            snprintf(meldung, meldungGroesse, "Wert \"%.100s\" ist keine Oktalkonstante (Oktalzahlen beginnen mit 0 und enthalten nur 0-7)", arg);
            return 1;
        }
        return 0;
    }
    if (strcmp(typ, "$TYPABS") == 0) {
        for (int z = 0; z < lineCountAsm; z++) {
            char marke[256];
            strncpy(marke, linesAsm[z].sp1, sizeof(marke) - 1);
            marke[sizeof(marke) - 1] = '\0';
            size_t ml = strlen(marke);
            if (ml > 0 && marke[ml - 1] == ':') marke[ml - 1] = '\0';
            if (strcmp(marke, arg) == 0 && strcmp(linesAsm[z].sp2, "abs") == 0) return 0;
        }
        snprintf(meldung, meldungGroesse, "Wert \"%s\" ist nicht als ABSOLUT (abs) definiert", arg);
        return 1;
    }
    return 0;
}

char *getSubstringUntilSpace(const char *str, int offset) {
    static char result[256]; // Speicher für das gefundene Wort
    const char *start = str + offset;

    // Überspringe führende Leerzeichen
    while (*start && isspace(*start)) {
        start++;
    }

    // Finde das Ende des Wortes
    const char *end = start;
    while (*end && !isspace(*end)) {
        end++;
    }

    // Kopiere das gefundene Wort in `result`
    snprintf(result, sizeof(result), "%.*s", (int)(end - start), start);
    return result;
}

void extractFromSecondWord(char *destination, const char *source, size_t destSize) {
    const char *start = source;
    int wordCount = 0;

    while (*start) {
        if (isspace((unsigned char)*start)) {
            wordCount++;
            while (isspace((unsigned char)*start)) start++;
            if (wordCount == 1) break;
        } else {
            start++;
        }
    }

    strncpy(destination, start, destSize - 1);
    destination[destSize - 1] = '\0';
}


// ----------------------------

void macroFehlerausgabe(lineElements *ergebnis, int i, const char *fehlermeldung, const char *mna) {
    (void)mna;
    char mtemp[128];

    // Sicheres Kopieren von ergebnis[i].sp1 in mtemp mit Begrenzung
    strncpy(mtemp, ergebnis[i].sp1, sizeof(mtemp) - 1);
    mtemp[sizeof(mtemp) - 1] = '\0';  // Null-Termination erzwingen
    // Setze die Fehlermeldung in ergebnis[i].sp1
    snprintf(ergebnis[i].sp1, sizeof(ergebnis[i].sp1), ";%s*** Fehler%s %s %s <--.", _violett, _normal, fehlermeldung, mtemp);
    // Setze die anderen Felder auf leere Strings
    STRKOPIE(ergebnis[i].sp2, "");
    STRKOPIE(ergebnis[i].sp3, "");
    STRKOPIE(ergebnis[i].sp4, "");
}

// ----------------------------

const char *validMacroKeywords[] = {
    "$1", "$2", "$3", "$4", "$5", "$6", "$7", "$8", "$9",
    "$PR1", "$PR2", "$PR3", "$PR4", "$PR5", "$PR6", "$PR7", "$PR8", "$PR9",
    "$IF", "$ELIF", "$ENDIF", "!$wdhl", "$wrzl", "$sm", "$inkb", "$ingb",
    "$irrz", "$irrs", "$trans", "$bm", "$vorl", "$irrb", "$tab", "$zr", "$wr",
    "!$wdhl_adr_e", "$TYPADR", "$TYPKON", "$TYPABS"
};
const int validMacroCount = sizeof(validMacroKeywords) / sizeof(validMacroKeywords[0]);

const char *restrictedKeywords[] = {
    "$PR1", "$PR2", "$PR3", "$PR4", "$PR5", "$PR6", "$PR7", "$PR8", "$PR9",
    "$IF", "$ELIF", "$ENDIF", "!$wdhl", "$wrzl", "$sm", "$inkb", "$ingb",
    "$irrz", "$irrs", "$trans", "$bm", "$vorl", "$irrb", "$tab", "$zr", "$wr",
    "!$wdhl_adr_e", "$TYPADR", "$TYPKON", "$TYPABS"
};
const int restrictedCount = sizeof(restrictedKeywords) / sizeof(restrictedKeywords[0]);

const char *validPR[] = {"$PR1", "$PR2", "$PR3", "$PR4", "$PR5", "$PR6", "$PR7", "$PR8", "$PR9"};
const char *validType[] = {"$TYPADR", "$TYPKON", "$TYPABS"};

// Fehlerliste eines Makroaufrufs (Fehler der Makrodefinition und der $IF-Auswertung)
#define MAKRO_MAX_FEHLER 64
typedef struct {
    char tab[MAKRO_MAX_FEHLER][512];
    int anzahl;
} MakroFehler;

// Eine Zeile der Makrodefinition, gekuerzt auf die Puffergroessen der Pruefungen
typedef struct {
    char sp1[256];
    char sp2[128];
    char sp3[256];
    char sp4[256];
} MakroZeile;

static void holeMakroZeile(const macroDefinitionen *m, int j, MakroZeile *z) {
    strncpy(z->sp1, m->macroParsedLines[j].sp1, sizeof(z->sp1) - 1);
    z->sp1[sizeof(z->sp1) - 1] = '\0';
    strncpy(z->sp2, m->macroParsedLines[j].sp2, sizeof(z->sp2) - 1);
    z->sp2[sizeof(z->sp2) - 1] = '\0';
    strncpy(z->sp3, m->macroParsedLines[j].sp3, sizeof(z->sp3) - 1);
    z->sp3[sizeof(z->sp3) - 1] = '\0';
    strncpy(z->sp4, m->macroParsedLines[j].sp4, sizeof(z->sp4) - 1);
    z->sp4[sizeof(z->sp4) - 1] = '\0';
}

static void meldeMakroFehler(MakroFehler *f, const char *format, const char *arg1, const char *arg2, const char *arg3) {
    if (f->anzahl >= MAKRO_MAX_FEHLER) {
        PRINT_FEHLER("%s", "Zu viele Fehler im Macro.");
        is_error = 1;
        return;
    }

    snprintf(f->tab[f->anzahl], 511, ";%s*** Fehler %s %s ", _violett, _normal, arg1);
    snprintf(f->tab[f->anzahl] + strlen(f->tab[f->anzahl]), 511 - strlen(f->tab[f->anzahl]), format, arg1, arg2, arg3);
    f->anzahl++;
}

// Entfernt "..." oder '...' um einen Parameter
static void trimQuotes(char *param) {
    size_t len = strlen(param);
    if (len > 1 && ((param[0] == '"' && param[len - 1] == '"') || (param[0] == '\'' && param[len - 1] == '\''))) {
        memmove(param, param + 1, len - 2);
        param[len - 2] = '\0';
    }
}

static int isValidMacroKeyword(char *word) {
    if ((strstr(word, "$") == NULL) || ( strlen(word) == 0 ) ) {
        return 2; // Kein Makro-Schlüsselwort enthalten, auch gültig
    }

    trimWhitespace(word); // Entferne überflüssige Leerzeichen

    char tempWord[256];
    strncpy(tempWord, word, sizeof(tempWord));
    tempWord[sizeof(tempWord) - 1] = '\0';  // Null-Terminierung sicherstellen
    int found = 0;
    int mfound = 0;
    char *token = strtok(tempWord, " \t"); // Zerlege die Zeichenkette
    while (token != NULL) {
        found = 0; // Setzt den Status auf "nicht gefunden"

        for (int k = 0; k < validMacroCount; k++) {
            if (strcmp(token, validMacroKeywords[k]) == 0) {
                found = 1; // Gültiges Schlüsselwort gefunden
                break;
            }
        }
        mfound += found;

        token = strtok(NULL, " \t"); // Nächstes Wort holen
        if ( token == NULL ) {
          if (mfound > 0) { mfound = 1; };
          return mfound; // Ungültiges Makro gefunden
        }
    }
    return 1; // Alle Wörter sind gültige Makros
}

// Streicht das erste Wort samt Leerraum davor und danach
static void entferneErstesWort(char *pruefliste_in) {
    int i_in = 0, j = 0;
    while (pruefliste_in[i_in] == ' ' || pruefliste_in[i_in] == '\t') {
        i_in++;
    }
    while (pruefliste_in[i_in] != ' ' && pruefliste_in[i_in] != '\t' && pruefliste_in[i_in] != '\0') {
        i_in++;
    }
    while (pruefliste_in[i_in] == ' ' || pruefliste_in[i_in] == '\t') {
        i_in++;
    }
    while (pruefliste_in[i_in] != '\0') {
        pruefliste_in[j++] = pruefliste_in[i_in++];
    }
    pruefliste_in[j] = '\0';
}

// Zerlegt die Parameterzeile des Makroaufrufs in Woerter (maximal 64); liefert die Anzahl
static int makroParameterZerlegen(char *aktuelleParameterZeile, char paramArray[64][MACRO_PARAMETER_LAENGE]) {
    char kopie[MACRO_PARAMETER_LAENGE];

    trimWhitespace(aktuelleParameterZeile);
    strncpy(kopie, aktuelleParameterZeile, MACRO_PARAMETER_LAENGE - 1);
    kopie[MACRO_PARAMETER_LAENGE - 1] = '\0';

    int anzahl = 0;
    char *wort = strtok(kopie, " \t");
    while (wort != NULL && anzahl < 64) {
        trimQuotes(wort);  // Entfernt "" oder ''
        strncpy(paramArray[anzahl], wort, MACRO_PARAMETER_LAENGE - 1);
        paramArray[anzahl][MACRO_PARAMETER_LAENGE - 1] = '\0';
        anzahl++;
        wort = strtok(NULL, " \t");
    }
    return anzahl;
}

// Pruefung einer $PRx-Zeile der Makrodefinition: Typangabe ($TYPADR, $TYPKON, $TYPABS) oder Wertliste
// gegen den beim Aufruf uebergebenen Parameter
static void pruefePrZeile(const char *SP1, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f) {
    int foundPR = 0;
    if (strlen(SP1) == 0) {
        return;
    }
    for (int pr = 0; pr < 9; pr++) {
        if (strncmp(SP1, validPR[pr], 4) == 0) {
            foundPR = 1;
            break;
        }
    }
    if (!foundPR) {
        return;
    }

    // Ein $PR? wurde gefunden: das naechste Wort in SP1 pruefen
    char pruefliste[256];
    strncpy(pruefliste, SP1, sizeof(pruefliste) - 1);
    pruefliste[sizeof(pruefliste) - 1] = '\0';

    entferneErstesWort(pruefliste);
    char rest[256] = "";
    STRKOPIE(rest, pruefliste);

    char *nextWord = strtok(rest, " \t");
    if (nextWord == NULL) {
        return;
    }

    int foundType = 0;
    for (int t = 0; t < 3; t++) {
        if (strcmp(nextWord, validType[t]) == 0) {
            foundType = 1;
            break;
        }
    }

    if (foundType) {
        // $TYPADR, $TYPKON oder $TYPABS gefunden: pruefen, ob danach noch weitere Zeichen folgen
        char *nextWord22 = strtok(NULL, " \t"); // Versuche, ein weiteres Wort zu holen
        if (nextWord22 != NULL) {
            meldeMakroFehler(f, "Ungültige Zeichen nach %s %s%s", SP1, nextWord22, "");
        } else {
            // Typpruefung ($TYPADR, $TYPKON, $TYPABS) des beim Aufruf uebergebenen Wertes
            int parameterNummer = SP1[3] - '0';
            if (parameterNummer >= 1 && parameterNummer <= paramAnzahl) {
                char typMeldung[256];
                if (pruefeMakroTyp(nextWord, paramArray[parameterNummer - 1], typMeldung, sizeof(typMeldung)) != 0) {
                    char paramBez[16];
                    snprintf(paramBez, sizeof(paramBez), "$%d", parameterNummer);
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, typMeldung, "");
                }
            }
        }
    } else if (isdigit((unsigned char)SP1[3]) && nextWord[0] != '$') {   // $...-Eintrag (z. B. $ADRESSE) = Typangabe, keine Wertliste
        // Wertliste (Doku 4): Der beim Aufruf uebergebene Parameter $x darf nur
        // einen der in der Liste $PRx genannten Werte annehmen.
        int parameterNummer = SP1[3] - '0';
        if (parameterNummer >= 1 && parameterNummer <= paramAnzahl) {
            char listeKopie[256];
            strncpy(listeKopie, pruefliste, sizeof(listeKopie) - 1);
            listeKopie[sizeof(listeKopie) - 1] = '\0';
            char *kommentar_p = strchr(listeKopie, ';');   // ; leitet einen Kommentar ein
            if (kommentar_p) *kommentar_p = '\0';
            int inListe = 0;
            char *lsave;
            for (char *w = strtok_r(listeKopie, " \t", &lsave); w != NULL; w = strtok_r(NULL, " \t", &lsave)) {
                if (strcmp(w, paramArray[parameterNummer - 1]) == 0) { inListe = 1; break; }
            }
            if (!inListe) {
                char paramBez[16];
                snprintf(paramBez, sizeof(paramBez), "$%d", parameterNummer);
                meldeMakroFehler(f, "Parameter %s: Wert \"%s\" steht nicht in der Pruefliste", paramBez, paramArray[parameterNummer - 1], "");
            }
        }
    }
}

// Pruefung einer Zeile der Makrodefinition: Schluesselwoerter, $PRx und Zaehlung der $IF-Bloecke
static void pruefeMakroZeile(const macroDefinitionen *m, int jj, char paramArray[64][MACRO_PARAMETER_LAENGE],
                             int paramAnzahl, MakroFehler *f, int *ifCount) {
    MakroZeile z;
    holeMakroZeile(m, jj, &z);

    trimWhitespace(z.sp1);
    trimWhitespace(z.sp2);
    trimWhitespace(z.sp3);

    char *trimmed = z.sp1;
    while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Entfernt Leerzeichen & Tabs

    // **Überspringe Kommentarzeilen**
    if (*trimmed == ';' || *trimmed == '#' || *trimmed == '*' || *trimmed == '&' ) {
        return;
    }

    // Nur gültige Makro-Schlüsselwörter erlauben
    char combinedString[1024];  // Puffer für die zusammengesetzte Zeichenkette
    snprintf(combinedString, sizeof(combinedString), "%s %s %s", z.sp1, z.sp2, z.sp3);

    char *saveptr;
    char *token = strtok_r(combinedString, " \t", &saveptr);
    int erg = 0;

    while (token != NULL) {
        erg += isValidMacroKeyword(token);
        token = strtok_r(NULL, " \t", &saveptr); // Nächstes Token holen
    }
    if (erg == 0) {
        meldeMakroFehler(f, "Ungültiges Makro-Schlüsselwort: %s %s %s", z.sp1, z.sp2, z.sp3);
        return;
    }

    // **Überprüfung: Jedes Schlüsselwort nur einmal pro Zeile**
    int keywordTracker[sizeof(restrictedKeywords) / sizeof(restrictedKeywords[0])];
    memset(keywordTracker, 0, sizeof(keywordTracker));

    char *tokens[] = {z.sp1, z.sp2, z.sp3};
    for (int t = 0; t < 3; t++) {
        for (int k = 0; k < restrictedCount; k++) {
            if (strcmp(tokens[t], restrictedKeywords[k]) == 0) {
                if (keywordTracker[k] > 0) {
                    meldeMakroFehler(f, "Makro-Schlüsselwort mehrfach in einer Zeile: %s %s%s", tokens[t], "", "");
                }
                keywordTracker[k]++;
            }
        }
    }

    // Prüfe, ob bei "$PR?"  ? < macroparameteranzahl
    if (strncmp(z.sp1, "$PR", 3) == 0 && isdigit((unsigned char)z.sp1[3])) {
        int parameterNummer = z.sp1[3] - '0';  // Konvertiere Zeichen zu einer Zahl

        // Überprüfen, ob die Ziffer innerhalb der erlaubten Anzahl liegt
        if (parameterNummer > m->macroParameterAnzahl) {
            char maxParamStr[16];  // Puffer für die Zeichenkette
            snprintf(maxParamStr, sizeof(maxParamStr), "%d", m->macroParameterAnzahl);
            meldeMakroFehler(f, "Ungültiger Parameter: %s (Max. erlaubt: $PR%s)%s", z.sp1, maxParamStr, "");
        }
    }

    pruefePrZeile(z.sp1, paramArray, paramAnzahl, f);

    if ( (strcmp(z.sp1, "$IF") == 0) || (strncmp(z.sp1, "$EL", 3) == 0) ) {
        (*ifCount)++;
    }

    char *commentStart = strchr(z.sp1, ';'); // Suche das erste Semikolon
    if (commentStart != NULL) {
        *commentStart = '\0'; // Setze Null-Terminierung direkt nach `$ENDIF`
    }

    // Prüfe auf $ENDIF (jetzt ohne Kommentar)
    if ( strncmp(z.sp1, "$ELIF", 5) == 0 ) {
        if (*ifCount == 0) {
            meldeMakroFehler(f, "$ENDIF ohne vorheriges $IF: %s %s%s", z.sp1, "", "");
        } else {
            (*ifCount)--;
        }
    }
}

// Prueft die ganze Makrodefinition (alle Zeilen) und sammelt die Fehler in f
static void pruefeMakroDefinition(const macroDefinitionen *m, char paramArray[64][MACRO_PARAMETER_LAENGE],
                                  int paramAnzahl, MakroFehler *f) {
    int ifCount = 0;  // Zählt offene $IF-Blöcke

    for (int jj = 0; jj < m->macroLineCount; jj++) {
        pruefeMakroZeile(m, jj, paramArray, paramAnzahl, f, &ifCount);
    }

    // Falls nach der Schleife noch offene $IF-Blöcke existieren, Fehler ausgeben
    if (ifCount > 0) {
        meldeMakroFehler(f, "Fehlendes $ENDIF für ein $IF %s%s%s", "", "", "");
    }

    // prüfe Verwendung von $1..$9 auf < parameteranzahl (über alle Zeilen dieses Makros)
    for (int jj = 0; jj < m->macroLineCount; jj++) {
        MakroZeile z;
        holeMakroZeile(m, jj, &z);
        trimWhitespace(z.sp1);
        trimWhitespace(z.sp2);
        trimWhitespace(z.sp3);

        char *tokens[] = {z.sp1, z.sp2, z.sp3};
        for (int t = 0; t < 3; t++) {
            if (tokens[t][0] == '$' && isdigit((unsigned char)tokens[t][1])) {  // Prüfe ob $1, $2, ..., $9
                int paramNum = tokens[t][1] - '0';  // Extrahiere die Ziffer
                if (paramNum > m->macroParameterAnzahl) {
                    char maxParamStr[16];  // Puffer für die Zeichenkette
                    snprintf(maxParamStr, sizeof(maxParamStr), "%d", m->macroParameterAnzahl);

                    meldeMakroFehler(f, "Ungültiger Makro-Parameter: %s (Max. erlaubt: $%s)%s", tokens[t], maxParamStr, "");
                }
            }
        }
    }
}

static lineElements *makroResultVergroessern(lineElements *result, int lineCount) {
    lineElements *temp = (lineElements *)realloc(result, ((size_t)lineCount + 1) * sizeof(lineElements));
    if (!temp) {
        fprintf(stderr, "Speicherfehler bei Realloc!\n");
        exit(RC_FEHLER);
    }
    return temp;
}

static void macroNameOhneDoppelpunkt(const char *name, char *out, size_t groesse);

// Haengt alle Zeilen der Makrodefinition (ohne Kommentar- und Leerzeilen) an result an
static lineElements *makroZeilenUebernehmen(const macroDefinitionen *m, const char *makroName, lineElements *result, int *lineCount) {
    for (int j = 0; j < m->macroLineCount; j++) {

        if (m->macroParsedLines[j].sp1[0] == '#' || m->macroParsedLines[j].sp1[0] == '&' ||
            ( strlen(m->macroParsedLines[j].sp1) == 0 && strlen(m->macroParsedLines[j].sp2) == 0 &&
              strlen(m->macroParsedLines[j].sp3) == 0 && strlen(m->macroParsedLines[j].sp4) == 0))
        {
            continue;
        }

        if (strcmp(makroName, m->macroParsedLines[j].sp2) == 0) {
            is_error0 = 1;
            char defName[MACRO_PARAMETER_LAENGE];
            macroNameOhneDoppelpunkt(m->macroName, defName, sizeof(defName));
            int rufZeile = m->macroParsedLines[j].srcLine;   // Zeile des Selbstaufrufs (nur bei Makros im Quelltext bekannt)
            if (m->defDatei[0] != '\0' && m->defZeile > 0) {
                PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s [Makro %.60s ruft sich selbst auf; definiert in %.200s:%d]",
                             makroName, defName, m->defDatei, m->defZeile);
            } else if (rufZeile > 0) {
                PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s [Makro %.60s ruft sich selbst auf, im Quelltext Zeile %d]",
                             makroName, defName, rufZeile);
            } else {
                PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s [Makro %.60s ruft sich selbst auf]", makroName, defName);
            }
            return result;   // kein Abbruch: die Uebernahme dieses Makros endet, weitere Fehler im Quelltext werden noch gemeldet
        }

        // Setzt ALLE Zeilen der MacroDefinition Zeile für Zeile in die Rückgabe, erweitert RESULT damit automatisch zu einem Array
        result = makroResultVergroessern(result, *lineCount);
        result[*lineCount] = m->macroParsedLines[j];
        (*lineCount)++;
    }
    return result;
}

// Ersetzt $1 ... $n in allen Zeilen durch die beim Aufruf uebergebenen Parameter
static void makroParameterErsetzen(lineElements *result, int lineCount, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl) {
    for (int j = 0; j < lineCount; j++) {

        if (result[j].sp1[0] == '#' ||
            (result[j].sp1[0] == '$' && strncmp(result[j].sp1, "$IF", 3) != 0 &&
                                    strncmp(result[j].sp1, "$ELIF", 5) != 0 &&
                                    strncmp(result[j].sp1, "$ENDIF", 6) != 0) ||
            result[j].sp1[0] == '&' ||
            (strlen(result[j].sp1) == 0 && strlen(result[j].sp2) == 0 &&
            strlen(result[j].sp3) == 0 && strlen(result[j].sp4) == 0))
        {
            continue;
        }

        char *fields[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };

        for (int f = 0; f < 4; f++) { // Durch sp1 - sp4 iterieren
            size_t originalLen = strlen(fields[f]);
            char *newField = malloc(originalLen + 512); // Speicher für ursprüngliche Länge
            if (!newField) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
            strkopiere(newField, originalLen + 512, fields[f]);

            for (int p = 0; p < paramAnzahl; p++) { // `$1` entspricht Index `0`, `$2` → `1` usw.
                char search[16];
                snprintf(search, sizeof(search), "$%d", p + 1); // `$N` → `paramArray[N-1]`

                char *pos;
                while ((pos = strstr(newField, search)) != NULL) { // Wiederholt ersetzen
                    size_t newSize = strlen(newField) - strlen(search) + strlen(paramArray[p]) + 1;
                    char *updatedField = malloc(newSize + 100);
                    if (!updatedField) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }

                    // Kopiere alles bis zum gefundenen `$N`
                    strncpy(updatedField, newField, pos - newField);
                    updatedField[pos - newField] = '\0';

                    // Füge den Ersatzwert ein
                    stranhaengen(updatedField, newSize + 100, paramArray[p]);

                    // Füge den restlichen String nach `$N` an
                    stranhaengen(updatedField, newSize + 100, pos + strlen(search) );

                    free(newField); // Alten Speicher freigeben
                    newField = updatedField;
                }
            }

            // Sicherstellen, dass das letzte Zeichen nicht abgeschnitten wird
            strncpy(fields[f], newField, MACRO_PARAMETER_LAENGE - 1);
            fields[f][MACRO_PARAMETER_LAENGE - 1] = '\0';

            free(newField); // Speicher nach der Bearbeitung freigeben
        }
    }
}

static void makroZeileKopieren(lineElements *ziel, const lineElements *quelle) {
    STRKOPIE(ziel->sp1, quelle->sp1);
    STRKOPIE(ziel->sp2, quelle->sp2);
    STRKOPIE(ziel->sp3, quelle->sp3);
    STRKOPIE(ziel->sp4, quelle->sp4);
    ziel->srcLine = quelle->srcLine;
}

// Wertet $IF / $ELIF / $ENDIF aus und liefert die Zeilen des Makroaufrufs; result wird freigegeben.
// Bei einem Fehler in $IF bleibt an der Stelle eine Leerzeile; alle weiteren Zeilen werden unveraendert
// uebernommen (Die Schleife laeuft nur ueber die urspruenglichen Zeilen. Frueher wurde ihr Ende
// mitgezaehlt und dadurch hinter das Zeilenfeld gelesen.)
static lineElements *makroBedingungenAuswerten(lineElements *result, int *lineCount, MakroFehler *f, const char *aktuellerOpCode) {
    int n = *lineCount;
    int imIf = 0;
    int inBedingung = 0;
    int grc = 0;
    int kk = 0;
    char firstWord[10];  // Speicher für das erste Wort

    lineElements *quelle = result;
    lineElements *neu = (lineElements *)calloc(2 * (size_t)n + 1, sizeof(lineElements));
    if (!neu) {
        fprintf(stderr, "Speicherzuweisung tmp_result fehlgeschlagen!\n");
        free(quelle);
        exit(RC_FEHLER);
    }

    for (int j = 0; j < n; j++) {
        if ( imIf == 2 ) { imIf = 0; }
        int rc = macroIfAufloesen( &quelle[j], &imIf, &inBedingung);
        if (rc < 0) {
            grc = -1;
            is_error0 = 1;
            kk++;
            if (rc == -1) {
               meldeMakroFehler(f, "$IF darf nicht geschachtelt werden.", aktuellerOpCode, "", "");
            } else if (rc == -2) {
               meldeMakroFehler(f, "$IF benötigt 3, 7, 11 oder 15 Parameter der Struktur a b c [|&] d e f [|&] g h i [|&] j k l.", aktuellerOpCode, "", "");
            } else if (rc == -3) {
               meldeMakroFehler(f, "Der 4. Parameter muss | oder & sein.", aktuellerOpCode, "", "");
            } else if (rc == -4) {
               meldeMakroFehler(f, "Der 8. Parameter muss | oder & sein.", aktuellerOpCode, "", "");
            } else if (rc == -5) {
               meldeMakroFehler(f, "Der 12. Parameter muss | oder & sein.", aktuellerOpCode, "", "");
            } else {
               meldeMakroFehler(f, "Macro: Unspezifischer Fehler.", aktuellerOpCode, "", "");
            }
        }

        if ( grc == 0 && f->anzahl == 0) {
            if ( imIf == 1 ) {  // in $IF
                if (inBedingung > 0 ) {
                    if (sscanf(quelle[j].sp1, "%9s", firstWord) == 1) {  // Extrahiere das erste Wort
                        if (strcmp(firstWord, "$IF") != 0 && strcmp(firstWord, "$ELIF") != 0) {
                            makroZeileKopieren(&neu[kk], &quelle[j]);
                            kk++;
                        }
                    } else {
                        //sp1 ist leer
                        makroZeileKopieren(&neu[kk], &quelle[j]);
                        kk++;
                    }
                }
            } else {
                if (sscanf(quelle[j].sp1, " %9s", firstWord) != 1 || firstWord[0] != '$') {
                    makroZeileKopieren(&neu[kk], &quelle[j]);
                    if (strcmp(quelle[j].sp2, "macroende") == 0 ||
                        strcmp(quelle[j].sp2, "MACROENDE") == 0 ||
                        strcmp(quelle[j].sp2, "MEND") == 0) {

                        STRKOPIE(neu[kk].sp1, ";+++");
                        STRKOPIE(neu[kk].sp2, "MEND");
                        STRKOPIE(neu[j].sp1, ";+++");
                        STRKOPIE(neu[j].sp2, "MEND");
                    }
                    kk++;
                }
            }
        } else {
            makroZeileKopieren(&neu[kk], &quelle[j]);
            kk++;
        }
    }

    free(quelle);
    *lineCount = kk;
    return neu;
}

// Fehler in einem Makro der Makrodatei: Herkunft (Makro, Datei, Zeile der Definition) anhaengen,
// denn die Fehlerzeile selbst zeigt auf den Makroaufruf im Quelltext.
static void makroHerkunftAnhaengen(MakroFehler *f, const macroDefinitionen *m) {
    if (m->defZeile <= 0 || m->defDatei[0] == '\0') return;
    char name[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(m->macroName, name, sizeof(name));
    for (int k = 0; k < f->anzahl; k++) {
        size_t len = strlen(f->tab[k]);
        snprintf(f->tab[k] + len, sizeof(f->tab[k]) - len, " [Makro %.60s, definiert in %.200s:%d]",
                 name, m->defDatei, m->defZeile);
    }
}

// Haengt die gesammelten Fehler als Zeilen an result an
static lineElements *makroFehlerAnhaengen(lineElements *result, int *lineCount, const MakroFehler *f) {
    for (int i_in = 0; i_in < f->anzahl; i_in++) {
        is_error0 = 1;
        result = makroResultVergroessern(result, *lineCount);
        STRKOPIE(result[*lineCount].sp1 , f->tab[i_in]);
        (*lineCount)++;
    }
    return result;
}

// !$wdhl und !$wdhl_adr_e: die Wiederholungsanweisung wird in Zeilen aufgeloest
static void makroWdhlAufloesen(lineElements *result, int lineCount, char paramArray[64][MACRO_PARAMETER_LAENGE]) {
    char tempLine[256] = "";
    int ober_i = 0;

    for (int i_in = 0; i_in < lineCount && (result[i_in].sp1[0] != '\0' || result[i_in].sp2[0] != '\0' || result[i_in].sp3[0] != '\0'); i_in++) {   // Obergrenze: kein Lesen hinter dem Array
        if (result[i_in].sp2[0] != '\0' && strstr(result[i_in].sp2, "!$wdhl_adr_e") != NULL) {
            STRKOPIE(tempLine, result[i_in].sp2);
            STRANHANG(tempLine, " ");
            STRANHANG(tempLine, result[i_in].sp3);
            ober_i = i_in;
            break;
        }
        if (result[i_in].sp2[0] != '\0' && strstr(result[i_in].sp2, "!$wdhl") != NULL) {
            STRKOPIE(tempLine, result[i_in].sp2);
            ober_i = i_in;
            break;
        }
    }

    if ((strstr(tempLine, "$PR") == NULL) ) {
        if (strstr(tempLine, "!$wdhl_adr_e") != NULL) {
            verarbeiteZeile_wdhl_adr_e(tempLine);
            int muell = ober_i;
            processLine(tempLine, result, &muell);

        } else if (strcmp(tempLine, "!$wdhl") == 0) {
            int rc_in = verarbeiteZeile_wdhl(tempLine, paramArray[0], paramArray[1], paramArray[2], paramArray[3], paramArray[4]);
            if (rc_in == 0) {
                int muell = ober_i;
                processLine(tempLine, result, &muell);
            }
        }
    }
}

// Label des Makroaufrufs: Hat die erste erzeugte Anweisung kein eigenes Label, entfaellt die
// equ-Zeile und die erste Anweisung erhaelt das Label des Aufrufs. (Nicht bei equ/spa/abs/start/end,
// dort wuerde das Label sonst einen anderen Wert als die Adresse bekommen.)
static void makroLabelUebernehmen(lineElements *result, int *lineCount, int equIndex, const char *label) {
    if (equIndex < 0) {
        return;
    }
    int erste = -1;
    for (int q = equIndex + 1; q < *lineCount; q++) {
        if (result[q].sp1[0] == ';') continue;   // Kommentarzeilen ueberspringen
        erste = q;
        break;
    }
    if (erste >= 0 && result[erste].sp1[0] == '\0' && result[erste].sp2[0] != '\0' &&
        strncmp(result[erste].sp2, "equ", 3) != 0 &&
        strcmp(result[erste].sp2, "spa") != 0 &&
        strcmp(result[erste].sp2, "abs") != 0 &&
        strcmp(result[erste].sp2, "start") != 0 &&
        strcmp(result[erste].sp2, "end") != 0) {
        STRKOPIE(result[erste].sp1, label);
        for (int q = equIndex; q < *lineCount - 1; q++) {
            result[q] = result[q + 1];
        }
        (*lineCount)--;
    }
}

// bearbeitet nur die Zeile lineCount die den Macronamen enthält !!!
// prüft aber den ganzen Macro und gibt ALLE seine generierten zeilen zurück
lineElements* loeseMacroAuf(macroDefinitionen *macros_p, int *macroCount_p, char *aktuellerOpCode, char *aktuelleParameterZeile, int *lineCount , char *label) {

    *lineCount = 0;

    size_t len = strlen(aktuellerOpCode);
    if (len > 0 && aktuellerOpCode[len - 1] == ':') {
        aktuellerOpCode[len - 1] = '\0';
    }

    char AsmParamArray[64][MACRO_PARAMETER_LAENGE];
    int AsmParamCount = makroParameterZerlegen(aktuelleParameterZeile, AsmParamArray);

    // Die Schleife bearbeitet alle aktuellerOpCode's die Macronamen sind.
    // Durch alle MACROs
    for (int i = 0; i < *macroCount_p; i++) {
        char zuPruefenderMacro[MACRO_PARAMETER_LAENGE];
        STRKOPIE(zuPruefenderMacro, macros_p[i].macroName);

        size_t tempLen = strlen(zuPruefenderMacro);
        if (tempLen > 0 && zuPruefenderMacro[tempLen - 1] == ':') {
            zuPruefenderMacro[tempLen - 1] = '\0';
        }

        if (strcmp(aktuellerOpCode, zuPruefenderMacro) != 0) {
            continue;
        }

        lineElements *result = (lineElements *)calloc(1, sizeof(lineElements));
        if (!result) {
            fprintf(stderr, "Speicherzuweisung result fehlgeschlagen!\n");
            exit(RC_FEHLER);
        }

        // Im makro
        if (AsmParamCount != macros_p[i].macroParameterAnzahl) {
            MELDE_FEHLER("erwartet %d Parameter, aber %d wurden übergeben!", macros_p[i].macroParameterAnzahl, AsmParamCount);
            is_error0 = 1;
            return result;
        }

        int equIndex = -1;  // Position der automatisch erzeugten equ-Zeile (-1 = keine)
        if ( strlen(label) > 0 ) {
            // Label für Macroaufruf
            result = makroResultVergroessern(result, *lineCount);
            equIndex = *lineCount;
            STRKOPIE(result[*lineCount].sp1, label);
            STRKOPIE(result[*lineCount].sp2, "equ");
            STRKOPIE(result[*lineCount].sp3, "*");
            STRKOPIE(result[*lineCount].sp4, "; automatisch generiert");
            result[*lineCount].srcLine = 0;
            (*lineCount)++;
        }

        MakroFehler fehler;
        fehler.anzahl = 0;
        pruefeMakroDefinition(&macros_p[i], AsmParamArray, AsmParamCount, &fehler);

        result = makroZeilenUebernehmen(&macros_p[i], zuPruefenderMacro, result, lineCount);
        makroParameterErsetzen(result, *lineCount, AsmParamArray, AsmParamCount);
        result = makroBedingungenAuswerten(result, lineCount, &fehler, aktuellerOpCode);
        makroHerkunftAnhaengen(&fehler, &macros_p[i]);
        result = makroFehlerAnhaengen(result, lineCount, &fehler);
        makroWdhlAufloesen(result, *lineCount, AsmParamArray);
        makroLabelUebernehmen(result, lineCount, equIndex, label);
        return result;
    }

    *lineCount = 0;
    return NULL;
}


// ----------------------------------------------------------------------------------


int beginntMitSemikolon(const char *line) {
    while (*line && isspace((unsigned char)*line)) {  // Ignoriert führende Leerzeichen
        line++;
    }
    if (*line == ';') {
        return 1;  // Semikolon gefunden
    } else {
        return 0;  // Kein Semikolon am Anfang
    }
}

// Ersetzen der Definitionsstelle eines Macrolabels, wenn enthalten
void replaceMacroLabel(char *input, const char *label, int labelLineNumber, int currentLineNumber) {
    if (strlen(label) == 0) { return; }
    int offset = labelLineNumber - currentLineNumber;
    char replacement[16];  // Platz für *±nnnn

    if (offset < 0) {
        snprintf(replacement, sizeof(replacement), "*-%d", -offset);
    } else {
        snprintf(replacement, sizeof(replacement), "*+%d", offset);
    }

    char *pos = strstr(input, label);
    if (!pos) {
        return;   
    }

    char output[256];  
    size_t labelLen = strlen(label);
    size_t prefixLen = pos - input;

    strncpy(output, input, prefixLen);
    output[prefixLen] = '\0';

    strncat(output, replacement, sizeof(output) - strlen(output) - 1);
    strncat(output, pos + labelLen, sizeof(output) - strlen(output) - 1);
    strncpy(input, output, 256);  
}

// -----------------------------------

int seed_value = 0;
int seed_max = 17000;

char* generate_uuid(int seed) {
    static char uuid[4]; // 3 Buchstaben + Nullterminator
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"; // Nur englische Großbuchstaben

    // Erzeuge eine reproduzierbare Zufallszahl basierend auf dem Seed
    int value = seed * 2654435761 % 26; // Eine einfache Hash-Funktion für Varianz

    for (int i = 0; i < 3; i++) {
        uuid[i] = charset[(value + i * 7) % 26]; // Modifizierte Berechnung für Variation
    }
    
    uuid[3] = '\0'; // Nullterminator für gültigen String
    return uuid;
}

// -----------------------------------

// macht aus einem aufgelösten Macro in ERGEBNIS relative sprünge
void macroSprung1Aufloesen(lineElements **ergebnis, int *lineCount, char *mna) {

    MacroLabel labelTable[MAX_LABELS];  
    int labelCount = 0;

    char *uuid = generate_uuid(seed_value);
    
    void modify_text(char *text, const char *uuid_in) {
        char temp[256];  
        char *pos = strchr(text, '%');  // Suche nach '%'

        if (pos) {
            size_t prefix_len = pos - text;  // Länge des Textes vor '%'
            snprintf(temp, sizeof(temp), "%.*s%s%s", (int)prefix_len, text, uuid_in, pos + 1);
            strkopiere(text, MACRO_PARAMETER_LAENGE, temp); 
        }
    }

    void modify_text2(char *erg, const char *label_mit, const char *label_ohne, const char *uuid_in) {
        char temp[256]; 
        char *pos = strstr(erg, label_mit);  // Suche nach label_mit

        if (pos) {
            size_t prefix_len = pos - erg;  // Länge des Textes vor label_mit
            snprintf(temp, sizeof(temp), "%.*s%s%s%s", (int)prefix_len, erg, label_ohne, uuid_in, pos + strlen(label_mit));
            strkopiere(erg, MACRO_PARAMETER_LAENGE, temp);  
        }
    }



    // Pro Eingabezeile kann hoechstens eine Fehlerzeile hinzukommen, daher doppelte Kapazitaet.
    int origCount = *lineCount;
    int kapazitaet = 2 * origCount + 1;
    lineElements *output = (lineElements *)malloc(kapazitaet * sizeof(lineElements));
    lineElements *tempErgebnis = (lineElements *)malloc(kapazitaet * sizeof(lineElements));
    if (!output || !tempErgebnis) {
        fprintf(stderr, "Speicherzuweisung für `output` oder `tempErgebnis` fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }

    // **Erster Durchlauf: Makro-Labels sammeln**
    // outCount zaehlt die Zeilen in `output`; bei einem ungueltigen Makro-Label wird hinter der
    // Zeile eine Fehlerzeile eingefuegt (die Folgezeilen bleiben unveraendert).
    int outCount = 0;
    for (int kk = 0; kk < origCount; kk++) {
        lineElements *zeile = &(*ergebnis)[kk];

        if (zeile->sp1[0] == ';') {
            output[outCount++] = *zeile;
        }
        else if (strchr(zeile->sp1, ':') && strchr(zeile->sp1, '%') &&
                (strncmp(zeile->sp1, "ML", 2) != 0 ||
                !isdigit((unsigned char)zeile->sp1[2]) ||
                !isdigit((unsigned char)zeile->sp1[3]) ||
                !isdigit((unsigned char)zeile->sp1[4]) ||
                !isdigit((unsigned char)zeile->sp1[5]) ||
                zeile->sp1[6] != '%' ||
                zeile->sp1[7] != ':')) {
            is_error0 = 1;
            output[outCount++] = *zeile;
            lineElements fehler = *zeile;
            macroFehlerausgabe(&fehler, 0, "Macrolabel muß mit `ML`, vier Ziffern und `%` beginnen und einen Doppelpunkt haben (z.B.: ML0004%:):", mna);
            output[outCount++] = fehler;
        }
        else if (strncmp(zeile->sp1, "ML", 2) == 0 &&
            isdigit((unsigned char)zeile->sp1[2]) && isdigit((unsigned char)zeile->sp1[3]) &&
            isdigit((unsigned char)zeile->sp1[4]) && isdigit((unsigned char)zeile->sp1[5]) &&
            zeile->sp1[6] == '%' && zeile->sp1[7] == ':')
        {
            // original-label mit doppelpunkt
            STRKOPIE(labelTable[labelCount].label, zeile->sp1);
            labelCount++;
            // modifiziertes Label MIT Doppelpunkt.
            lineElements geaendert = *zeile;
            modify_text(geaendert.sp1, uuid);
            output[outCount++] = geaendert;
        } else {
            output[outCount++] = *zeile;
        }
    }

    // **Zweiter Durchlauf: Makro-Labels in Zeilen ersetzen**
    for (int i = 0; i < outCount; i++) {
        copyLineElements(tempErgebnis, output, i);
    }

    // Ergebnisfeld bei Bedarf fuer die eingefuegten Fehlerzeilen vergroessern
    if (outCount > origCount) {
        lineElements *temp = (lineElements *)realloc(*ergebnis, (outCount + 1) * sizeof(lineElements));
        if (!temp) {
            free(*ergebnis);
            fprintf(stderr, "Speicherfehler!\n");
            exit(RC_FEHLER);
        }
        *ergebnis = temp;
    }
    *lineCount = outCount;

    for (int i = 0; i < *lineCount; i++) {
        if ( (strlen(tempErgebnis[i].sp3) > 0) && (strstr(tempErgebnis[i].sp3, "%") != NULL) ) { 
           for (int k = 0; k < labelCount; k++) {
                char label_ohne[LABEL_SIZE];
                char label_mit[LABEL_SIZE];
                STRKOPIE(label_ohne,labelTable[k].label);
                if (strlen(label_ohne) >= 2) label_ohne[strlen(label_ohne) - 2] = '\0';
                STRKOPIE(label_mit,labelTable[k].label);
                if (label_mit[0] != '\0') label_mit[strlen(label_mit) - 1] = '\0';
                modify_text2(tempErgebnis[i].sp3, label_mit, label_ohne, uuid);
           }
        }
        copyLineElements(*ergebnis, tempErgebnis, i);
    }

    free(output);
    free(tempErgebnis);
}

// -------------------

// Makroname ohne abschließenden Doppelpunkt (für Vergleiche und Meldungen)
static void macroNameOhneDoppelpunkt(const char *name, char *out, size_t groesse) {
    strncpy(out, name, groesse - 1);
    out[groesse - 1] = '\0';
    size_t len = strlen(out);
    if (len > 0 && out[len - 1] == ':') {
        out[len - 1] = '\0';
    }
}

// Index des Makros mit diesem Namen (Doppelpunkt am Namensende wird ignoriert) oder -1
static int macroSuche(const char *name) {
    char a[MACRO_PARAMETER_LAENGE], b[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(name, a, sizeof(a));
    for (int i = 0; i < macroCount; i++) {
        macroNameOhneDoppelpunkt(macros[i].macroName, b, sizeof(b));
        if (strcmp(a, b) == 0) {
            return i;
        }
    }
    return -1;
}

// Legt ein Makro im Array `macros` an (gemeinsam genutzt von Makrodatei und Quelltext).
//   name:              Makroname wie in der Definition
//   paramsIn:          Rest hinter MACRO (Anzahl oder Wortliste), ggf. leer
//   zeilenKapazitaet:  Platz für die geparsten Makrozeilen
//   ausQuelltext:      Herkunft (1 = Quelltext, 0 = Makrodatei)
//   ersetzeIdx:        >= 0: das vorhandene Makro an dieser Stelle ersetzen, sonst -1 (neu anlegen)
// Rückgabe: Index des Makros.
static int macroAnlegen(const char *name, const char *paramsIn, int zeilenKapazitaet, int ausQuelltext, int ersetzeIdx) {
    int macroIndex;
    if (ersetzeIdx >= 0) {
        macroIndex = ersetzeIdx;
        free(macros[macroIndex].macroParsedLines);
    } else {
        if (macroCount >= macroCapacity) {
            macroCapacity *= GROWTH_FACTOR;
            macroDefinitionen *temp = (macroDefinitionen *)realloc(macros, macroCapacity * sizeof(macroDefinitionen));
            if (!temp) {
                fprintf(stderr, "Speichererweiterung fehlgeschlagen!\n");
                exit(RC_FEHLER);
            }
            macros = temp;
        }
        macroIndex = macroCount++;
    }
    macros[macroIndex].macroParsedLines = (lineElements *)calloc(zeilenKapazitaet, sizeof(lineElements));
    if (!macros[macroIndex].macroParsedLines) {
        fprintf(stderr, "Speicherzuweisung für Makrozeilen fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
    STRKOPIE(macros[macroIndex].macroName, name);
    STRKOPIE(macros[macroIndex].macro, "MACRO");
    macros[macroIndex].macroLineCount = 0;
    macros[macroIndex].ausQuelltext = ausQuelltext;
    macros[macroIndex].defDatei[0] = '\0';
    macros[macroIndex].defZeile = 0;

    char params[256];
    strncpy(params, paramsIn, sizeof(params) - 1);
    params[sizeof(params) - 1] = '\0';
    int paramCount = 0;
    if (params[0] != '\0') {
        if (strspn(params, "0123456789") == strlen(params)) {
            paramCount = atoi(params);
        } else {
            char *token = strtok(params, " ");
            while (token && paramCount < MACRO_PARAMETER_ANZAHL) {
                STRKOPIE(macros[macroIndex].macroParameters[paramCount], token);
                paramCount++;
                token = strtok(NULL, " ");
            }
        }
    }
    // Doku 4: Es sind maximal 9 Parameter zulaessig ($1 ... $9).
    if (paramCount > 9) {
        is_error0 = 1;
        char meldeName[MACRO_PARAMETER_LAENGE];
        strncpy(meldeName, name, sizeof(meldeName) - 1);
        meldeName[sizeof(meldeName) - 1] = '\0';
        size_t meldeLen = strlen(meldeName);
        if (meldeLen > 0 && meldeName[meldeLen - 1] == ':') meldeName[meldeLen - 1] = '\0';
        PRINT_FEHLER("Makro %s: %d Parameter angegeben, zulaessig sind maximal 9.", meldeName, paramCount);
    }
    macros[macroIndex].macroParameterAnzahl = paramCount;
    return macroIndex;
}

// Läd alle MAcros aus der Datei ins Array `macros`
void erzeugeMacroArray(const char *macroFileName) {
    // Zuerst im aktuellen Arbeitsverzeichnis suchen ...
    FILE *macroFile = fopen(macroFileName, "r");

    // Mit -m ist der Pfad ausdruecklich vorgegeben: keine Ersatzsuche, klare Fehlermeldung.
    if (!macroFile && makroDateiVomBenutzer) {
        PRINT_FEHLER("Makrodatei '%s' (Option -m) konnte nicht geoeffnet werden: %s", macroFileName, strerror(errno));
        exit(RC_FEHLER);
    }

    // ... falls dort nicht vorhanden, alternativ im Verzeichnis "Sourcecode" suchen
    char alternativerPfad[1024];
    if (!macroFile) {
        snprintf(alternativerPfad, sizeof(alternativerPfad), "Sourcecode/%s", macroFileName);
        macroFile = fopen(alternativerPfad, "r");
        if (macroFile) {
            macroFileName = alternativerPfad;
        }
    }

    if (!macroFile) {
        fprintf(stderr, "Fehler: Datei '%s' konnte weder im aktuellen Verzeichnis noch unter 'Sourcecode/%s' geöffnet werden!\n", macroFileName, macroFileName);
        exit(RC_FEHLER);
    }

    char lineBuffer[1024];
    int macroActive = 0;
    int macroIndex = -1;
    int dateiZeile = 0;   // Zeilennummer in der Makrodatei (fuer Fehlerorte)

    while (fgets(lineBuffer, sizeof(lineBuffer), macroFile)) {
        dateiZeile++;
        if (*lineBuffer == '\0' || strcmp(lineBuffer, "\n") == 0) {
            continue;
        }

        // Extrahiere den Makronamen und überprüfe auf Duplikate
        char name[MACRO_PARAMETER_LAENGE] = "", macro[16] = "", params[256] = "";

        int scannedFields = sscanf(lineBuffer, "%255s %15s %255[^\n]", name, macro, params);   // Feldbreiten: macro[16] lief über
        if (scannedFields >= 2 && strcmp(macro, "MACRO") == 0) {
            if (macroSuche(name) >= 0) {
                fprintf(stderr, "Fehler: Makro '%s' wurde bereits definiert! Überspringe bis zum Ende des Makros.\n", name);

                // Überspringe alle Zeilen bis zum nächsten Makroende
                while (fgets(lineBuffer, sizeof(lineBuffer), macroFile)) {
                    dateiZeile++;
                    if (strstr(lineBuffer, "macroende") || strstr(lineBuffer, "MACROENDE") || strstr(lineBuffer, "MEND")) {
                        break;
                    }
                }
                continue;
            }

            // Falls kein Duplikat gefunden wurde, speichere das neue Makro
            macroIndex = macroAnlegen(name, params, MACRODEFINITIONEN, 0, -1);
            snprintf(macros[macroIndex].defDatei, sizeof(macros[macroIndex].defDatei), "%s", macroFileName);
            macros[macroIndex].defZeile = dateiZeile;
            macroActive = 1;
            continue;
        }

        // Falls wir in einem Makro sind
        if (macroActive) {
            if (strstr(lineBuffer, "macroende") || strstr(lineBuffer, "MACROENDE") || strstr(lineBuffer, "MEND")) {
                processLine(lineBuffer, macros[macroIndex].macroParsedLines, &(macros[macroIndex].macroLineCount));  
                macroActive = 0;
                continue;
            }

            // Bearbeitet nur die 1. Zeile des Macros
            processLine(lineBuffer, macros[macroIndex].macroParsedLines, &(macros[macroIndex].macroLineCount)); 
        }
    }

    fclose(macroFile);

}

// ----------------

static int istMacroBeginn(const char *sp2) {
    return strcmp(sp2, "MACRO") == 0;
}

static int istMacroEnde(const char *sp2) {
    return strcmp(sp2, "MEND") == 0 || strcmp(sp2, "MACROENDE") == 0 || strcmp(sp2, "macroende") == 0;
}

// Sucht im bereits geparsten Quelltext (linesAsm) nach Makrodefinitionen
//     NAME:  MACRO [n]  ...  MEND
// legt sie im Array `macros` an (wie die Makros der Makrodatei) und ersetzt die Definition im Quelltext
// durch eine Kommentarzeile. Ein gleichnamiges Makro der Makrodatei wird für diesen Lauf ersetzt
// (die Makrodatei selbst bleibt unverändert); ein zweites gleichnamiges Makro im Quelltext ist ein Fehler.
// Pro Fehlerursache wird genau eine Meldung ausgegeben.
// Rückgabe: Anzahl der Fehler.
int sammleQuelltextMakros(void) {
    int fehler = 0;
    int aus = 0;   // Schreibindex des bereinigten Quelltextes
    int i = 0;

    while (i < lineCountAsm) {
        if (istMacroEnde(linesAsm[i].sp2)) {
            PRINT_FEHLER("%s", "Makrodefinition im Quelltext: MEND ohne zugehöriges MACRO.");
            fehler++; i++;
            continue;
        }
        if (!istMacroBeginn(linesAsm[i].sp2)) {
            if (aus != i) linesAsm[aus] = linesAsm[i];
            aus++; i++;
            continue;
        }

        // Definition beginnt bei Zeile i; Ende unter Beachtung der Schachtelungstiefe suchen
        char defName[MACRO_PARAMETER_LAENGE];
        macroNameOhneDoppelpunkt(linesAsm[i].sp1, defName, sizeof(defName));

        int tiefe = 1, ende = -1, verschachtelt = -1;
        for (int j = i + 1; j < lineCountAsm; j++) {
            if (istMacroBeginn(linesAsm[j].sp2)) {
                if (verschachtelt < 0) verschachtelt = j;
                tiefe++;
            } else if (istMacroEnde(linesAsm[j].sp2)) {
                if (--tiefe == 0) { ende = j; break; }
            }
        }

        if (verschachtelt >= 0) {
            char innen[MACRO_PARAMETER_LAENGE];
            macroNameOhneDoppelpunkt(linesAsm[verschachtelt].sp1, innen, sizeof(innen));
            PRINT_FEHLER("Makrodefinition im Quelltext: %s beginnt innerhalb der Definition von %s (Schachtelung ist nicht erlaubt; fehlt ein MEND?).",
                         innen[0] ? innen : "(ohne Namen)", defName[0] ? defName : "(ohne Namen)");
            fehler++;
            i = (ende >= 0) ? ende + 1 : lineCountAsm;
            continue;
        }
        if (ende < 0) {
            PRINT_FEHLER("Makrodefinition im Quelltext: Fehlendes MEND für %s.", defName[0] ? defName : "(ohne Namen)");
            fehler++;
            i = lineCountAsm;
            continue;
        }
        if (defName[0] == '\0') {
            PRINT_FEHLER("%s", "Makrodefinition im Quelltext: MACRO ohne Namen (Syntax: NAME:  MACRO [Parameteranzahl]).");
            fehler++;
            i = ende + 1;
            continue;
        }

        int vorhanden = macroSuche(linesAsm[i].sp1);
        if (vorhanden >= 0 && macros[vorhanden].ausQuelltext) {
            PRINT_FEHLER("Makrodefinition im Quelltext: %s ist im Quelltext bereits definiert.", defName);
            fehler++;
            i = ende + 1;
            continue;
        }
        if (vorhanden >= 0) {
            PRINT_WARNUNG("Makro %s aus der Makrodatei wird für diesen Lauf durch die Definition im Quelltext ersetzt.", defName);
        }

        // Rumpf einschließlich MEND-Zeile übernehmen, genau wie bei den Makros der Makrodatei
        int idx = macroAnlegen(linesAsm[i].sp1, linesAsm[i].sp3, ende - i, 1, vorhanden);
        memcpy(macros[idx].macroParsedLines, &linesAsm[i + 1], (ende - i) * sizeof(lineElements));
        macros[idx].macroLineCount = ende - i;

        // Definition im Quelltext durch Kommentarzeile ersetzen (defName wurde vorher gesichert)
        snprintf(linesAsm[aus].sp1, sizeof(linesAsm[aus].sp1), ";+++ Makrodefinition %.200s im Quelltext (%d Zeilen)", defName, ende - i - 1);
        linesAsm[aus].sp2[0] = linesAsm[aus].sp3[0] = linesAsm[aus].sp4[0] = '\0';
        aus++;
        i = ende + 1;
    }
    lineCountAsm = aus;
    return fehler;
}

void printAllMacros() {
    for (int i = 0; i < macroCount; i++) {
        printf("\nMakro %d:\n", i + 1);
        printf("Name: %s\n", macros[i].macroName);
        printf("Typ: %s\n", macros[i].macro);
        printf("Parameteranzahl: %d\n", macros[i].macroParameterAnzahl);
        
        // Ausgabe der Makro-Parameter, falls vorhanden
        if (macros[i].macroParameterAnzahl > 0) {
            printf("Parameter: ");
            for (int p = 0; p < macros[i].macroParameterAnzahl; p++) {
                printf("%s ", macros[i].macroParameters[p]);
            }
            printf("\n");
        } else {
            printf("Keine Parameter\n");
        }

        printf("Zeilenanzahl: %d\n", macros[i].macroLineCount);
        printf("Makro-Inhalt:\n");

        for (int j = 0; j < macros[i].macroLineCount; j++) {
            // Sicherstellen, dass keine leeren Zeilen ausgegeben werden
            if (strlen(macros[i].macroParsedLines[j].sp1) == 0 &&
                strlen(macros[i].macroParsedLines[j].sp2) == 0 &&
                strlen(macros[i].macroParsedLines[j].sp3) == 0 &&
                strlen(macros[i].macroParsedLines[j].sp4) == 0) {
                continue;
            }

            printf("%s | %s | %s | %s\n",
                   macros[i].macroParsedLines[j].sp1,
                   macros[i].macroParsedLines[j].sp2,
                   macros[i].macroParsedLines[j].sp3,
                   macros[i].macroParsedLines[j].sp4);
        }

        printf("--------------------------------------------------\n");
    }
}



int macroIfAufloesen(lineElements *ergebnis, int *imIf, int * inBedingung) {
 
    char tempLine[256];


    if (strncmp(ergebnis->sp1, "$", 1) == 0) {
        // Macro $IF - Anweisung $ELIF $ENDIF
        if ( *imIf == 2 ) { *imIf = 0; } 
        if ( *imIf == 1 && ( strstr(ergebnis->sp1, "$IF") ) ) {
            return -1; // PRINT_FEHLER("MACRO: $IF darf nicht geschachtelt werden: %s",tempLine);
        }

        // $IF ...

        STRKOPIE(tempLine, ergebnis->sp1);


        char firstWord[10];  // Speicher für das erste Wort
        if (sscanf(tempLine, "%9s", firstWord) == 1) {  // Extrahiere das erste Wort
            if (strcmp(firstWord, "$IF") == 0 || strcmp(firstWord, "$ELIF") == 0) {

                *imIf = 1;
                // Rest der Zeile extrahieren und prüfen, ob sie 3, 7, 11 oder 15 Parameter enthält
                // Alle Felder 128 Byte und mit Feldbreite gelesen; frueher waren die Operatorfelder 2 Byte
                // gross, ein laengeres Wort an dieser Stelle ueberschrieb den Stack.
                char a[128] = "", b[128] = "", c[128] = "", op[128] = "", d[128] = "", e[128] = "", f[128] = "";
                char op3[128] = "", g[128] = "", h[128] = "", i[128] = "", op4[128] = "", j[128] = "", k[128] = "", l[128] = "";
                int count = sscanf(tempLine, "%*s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s %127s",
                                    a, b, c, op, d, e, f, op3, g, h, i, op4, j, k, l);

                if (count != 3 && count != 7 && count != 11 && count != 15) {
                    return -2; // PRINT_FEHLER("MACRO: $IF benötigt 3, 7, 11 oder 15 Parameter der Struktur a b c [|&] d e f [|&] g h i [|&] j k l: %s", tempLine);
                }

                // Bei 3 Parametern normaler Vergleich
                if (count == 3) {
                    *inBedingung = macroParameterCompare(a, b, c);
                } else { // Erweiterter Vergleich mit logischen Operatoren
                    if (strcmp(op, "|") != 0 && strcmp(op, "&") != 0) {
                        return -3; // PRINT_FEHLER("MACRO: Der 4. Parameter muss | oder & sein: %s", tempLine);
                    }

                    int cond1 = macroParameterCompare(a, b, c);
                    int cond2 = macroParameterCompare(d, e, f);
                    int result = (strcmp(op, "|") == 0) ? (cond1 || cond2) : (cond1 && cond2);

                    // Falls eine dritte Bedingung existiert, wird sie zusätzlich verknüpft
                    if (count >= 11) {
                        if (strcmp(op3, "|") != 0 && strcmp(op3, "&") != 0) {
                            return -4; // PRINT_FEHLER("MACRO: Der 8. Parameter muss | oder & sein: %s", tempLine);
                        }

                        int cond3 = macroParameterCompare(g, h, i);
                        result = (strcmp(op3, "|") == 0) ? (result || cond3) : (result && cond3);
                    }

                    // Falls eine vierte Bedingung existiert, wird sie ebenfalls verknüpft
                    if (count == 15) {
                        if (strcmp(op4, "|") != 0 && strcmp(op4, "&") != 0) {
                            return -5;  // PRINT_FEHLER("MACRO: Der 12. Parameter muss | oder & sein: %s", tempLine);
                        }

                        int cond4 = macroParameterCompare(j, k, l);
                        result = (strcmp(op4, "|") == 0) ? (result || cond4) : (result && cond4);
                    }

                    *inBedingung = result;
                }
            }
            if ( strstr(tempLine, "$ENDIF")) {
                *imIf = 2;
            }
        }
    }
    return 0;
}
