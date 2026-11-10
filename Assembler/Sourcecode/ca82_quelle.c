// ca82_quelle.c - Einlesen der Quelltextzeilen (Pragmas, Kommentare, Wiederholungsadressen)
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"



// Text-Anweisungen: Der Operand ist ein Text (Zeichenfolge, ggf. in \...\), kein Zahlen- oder
// Adressausdruck. Dort sind ';' und '#' (Doku 2, <sonderzeichen>) einfache Textzeichen, und ein
// fuehrendes '#' leitet kein Literal ein.
int istTextAnweisung(const char *operation) {
    return strcmp(operation, "dt") == 0 || strcmp(operation, "dto") == 0 || strcmp(operation, "dtm") == 0
           || strcmp(operation, "kat4") == 0 || strcmp(operation, "kat5") == 0 || strcmp(operation, "kat6") == 0;
}

// Liefert die Position, an der der Operand endet: das erste ';' (Kommentarbeginn) bzw. das
// Zeilenende ab "rest". Bei dt, dto und dtm gilt (Doku 2, <kommentar>): "Innerhalb der \-Zeichen
// von dt wird ; nicht als Kommentar betrachtet." Steht vor dem ersten ';' ein '\' und gibt es
// dahinter ein schliessendes '\', so wird ein ';' dazwischen zum Text gerechnet, z. B.
//     dt  \ab;cd\   ; Kommentar      -> Text "ab;cd", Kommentar "; Kommentar"
// Ohne schliessendes '\' (oder bei einem ';' vor dem ersten '\') bleibt es beim ersten ';'.
// Die Auswahl der \...\-Grenzen entspricht extractBackslashContent(): erster bis zweiter '\'.
static char *findeOperandEnde(const char *operation, char *rest) {
    char *suchStart = rest;
    if (istTextAnweisung(operation)) {
        char *erstesEnde = strpbrk(rest, ";\n");
        char *b1 = strchr(rest, '\\');
        if (b1 && (!erstesEnde || b1 < erstesEnde)) {
            char *b2 = strchr(b1 + 1, '\\');
            if (b2) suchStart = b2 + 1;   // Kommentar frühestens hinter dem schliessenden '\'
        }
    }
    return strpbrk(suchStart, ";\n");
}

// löst eine Stringzeile in die .SPx-Struktur auf und gibt diese zurück.
void processLine(char *line, lineElements linesAsm_p[], int *lineCount) {
    int posIndex = 0;

    // Aktuelle Zeile initialisieren
    resetParsedLinesArrays(linesAsm_p, *lineCount);
    trimLeadingSpaces(line);

    while (*line) {

        if ((posIndex == 0) && ((*line == ';') || (*line == '#') || (*line == '$')  || (*line == '&') )) {
            STRKOPIE(linesAsm_p[*lineCount].sp1, line);
            removeNewlines(linesAsm_p[*lineCount].sp1);
            trimWhitespace(linesAsm_p[*lineCount].sp1);
            (*lineCount)++;
            return;
        }

        if ((*line != ' ') && (*line != '\t') && (*line != ';') && (*line != '#')  && (*line != '$')  && (*line != '&') && (posIndex == 0)) {
            char *colonPos = strchr(line, ':');
            if (colonPos) {
                int labelLength = colonPos - line + 1;  // +1, um `:` einzuschließen
                strncpy(linesAsm_p[*lineCount].sp1, line, labelLength);
                linesAsm_p[*lineCount].sp1[labelLength] = '\0'; // Nullterminierung
                removeNewlines(linesAsm_p[*lineCount].sp1);
                trimWhitespace(linesAsm_p[*lineCount].sp1);
                line = colonPos + 1;
                posIndex = labelLength;  // Kein `+1`, da `:` bereits enthalten ist
            }
        }

        while (*line && isspace((unsigned char)*line)) line++;

        char *nextSpace = strpbrk(line, " \t\n");
        if (nextSpace) {
            if ((*line == ';') && (posIndex > 0)) {
                STRKOPIE(linesAsm_p[*lineCount].sp4, line);
                removeNewlines(linesAsm_p[*lineCount].sp4);
                trimWhitespace(linesAsm_p[*lineCount].sp4);
                (*lineCount)++;
                return;
            }

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }
            char *nextSpace_in = strpbrk(line, " \t\n;");
            int wordLength = nextSpace_in ? (int)(nextSpace_in - line) : (int)strlen(line);

            strncpy(linesAsm_p[*lineCount].sp2, line, wordLength);
            linesAsm_p[*lineCount].sp2[wordLength] = '\0';
            removeNewlines(linesAsm_p[*lineCount].sp2);
            trimWhitespace(linesAsm_p[*lineCount].sp2);

            posIndex += wordLength;
            line += wordLength; 

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }

            char *restEnd = findeOperandEnde(linesAsm_p[*lineCount].sp2, line);
            int restLength = restEnd ? (int)(restEnd - line) : (int)strlen(line);
            strncpy(linesAsm_p[*lineCount].sp3, line, restLength);
            linesAsm_p[*lineCount].sp3[restLength] = '\0';
            removeNewlines(linesAsm_p[*lineCount].sp3);
            trimWhitespace(linesAsm_p[*lineCount].sp3);
            posIndex += restLength;
            line += restLength;
            removeNewlines(line);
            if (strlen(line) == 0) {
                (*lineCount)++;
                return;
            }
        }

        if ((*line == ';') && (posIndex > 0)) {
            STRKOPIE(linesAsm_p[*lineCount].sp4, line);
            removeNewlines(linesAsm_p[*lineCount].sp4);
            trimWhitespace(linesAsm_p[*lineCount].sp4);
            (*lineCount)++;
            return;
        }

        // nur Operationscode angegeben
        if (( strlen(line) > 0) ) {
            char *semi = strchr(line, ';');   // "MACRO;Kommentar" ohne Leerzeichen: Kommentar abtrennen (ab 1.01-031; vorher war der ganze Text der Operationscode)
            if (semi != NULL && semi != line) {
                STRKOPIE(linesAsm_p[*lineCount].sp4, semi);
                removeNewlines(linesAsm_p[*lineCount].sp4);
                trimWhitespace(linesAsm_p[*lineCount].sp4);
                *semi = '\0';
            }
            STRKOPIE(linesAsm_p[*lineCount].sp2, line);
            removeNewlines(linesAsm_p[*lineCount].sp2);
            trimWhitespace(linesAsm_p[*lineCount].sp2);
            (*lineCount)++;
            return;
        }

//        if (*line == '\n' || *line == '\0') {
            (*lineCount)++;
            return;
//        }
    }

    (*lineCount)++;
}

// Pragma   ;#; LEITADRESSE xx
//   - steht als Kommentarzeile im Quelltext und muss VOR `start` stehen,
//   - darf keinmal oder genau einmal vorkommen (Standard ohne Pragma: 01),
//   - xx ist zweistellig und liegt zwischen 00 und 09.
// Wirkung: Alle Befehle und Konstanten, die im Objektcode (.obj) bisher mit dem Kennzeichen 01 erzeugt
// wurden, erhalten stattdessen den Wert xx (siehe schreibeObjZeile).
// Bei xx = 00 entfaellt ausserdem die Kennzeichenzeile "21 0000 <zahl>" des start-Operanden (siehe pass3).
// Liefert 1, wenn die Zeile ein LEITADRESSE-Pragma ist (auch ein fehlerhaftes), sonst 0.
// Bezeichnung der gerade gelesenen Datei fuer Meldungen: "der Quelldatei" (Hauptdatei) oder "der eingebundenen Datei '<Pfad>'"
// ($INCLUDE im Quelltext, Doku 4.14); ladeIstHaupt = 1 in der Hauptdatei.
static char ladeBez[1100] = "der Quelldatei";
static int ladeIstHaupt = 1;

static int verarbeiteLeitadressePragma(const char *zeile, int zeilennr, int startGesehen) {
    const char *p = zeile;
    while (*p == ' ' || *p == '\t') p++;
    if (strncmp(p, ";#;", 3) != 0) return 0;
    p += 3;
    while (*p == ' ' || *p == '\t') p++;

    char wort[32];
    size_t n = 0;
    while (isalnum((unsigned char)*p) || *p == '_') {
        if (n < sizeof(wort) - 1) wort[n++] = *p;
        p++;
    }
    wort[n] = '\0';
    if (!gleichOhneGrossKlein(wort, "LEITADRESSE")) return 0;   // anderes ";#;"-Kommentar: bleibt Kommentar

    while (*p == ' ' || *p == '\t') p++;

    if (!ladeIstHaupt) {
        PRINT_FEHLER("Zeile %d %s: Das Pragma LEITADRESSE steht nur in der Hauptdatei, nicht in einer mit $INCLUDE eingebundenen Datei.", zeilennr, ladeBez);
        is_error = 1;
        return 1;
    }
    if (startGesehen) {
        PRINT_FEHLER("Zeile %d %s: Das Pragma LEITADRESSE muss vor `start` stehen.", zeilennr, ladeBez);
        is_error = 1;
        return 1;
    }
    if (leitadressePragmaGesetzt) {
        PRINT_FEHLER("Zeile %d %s: Das Pragma LEITADRESSE darf nur einmal vorkommen.", zeilennr, ladeBez);
        is_error = 1;
        return 1;
    }
    leitadressePragmaGesetzt = 1;

    // Wert: genau zwei Ziffern 00 ... 09; danach nur noch Leerraum oder ein Kommentar (;).
    int wertOk = isdigit((unsigned char)p[0]) && isdigit((unsigned char)p[1])
                 && (p[2] == '\0' || p[2] == ' ' || p[2] == '\t' || p[2] == ';' || p[2] == '\r' || p[2] == '\n');
    int wert = wertOk ? (p[0] - '0') * 10 + (p[1] - '0') : 0;
    if (!wertOk || wert < 0 || wert > 9) {
        PRINT_FEHLER("Zeile %d %s: Das Pragma LEITADRESSE erwartet einen zweistelligen Wert von 00 bis 09 (z. B. ;#; LEITADRESSE 02).", zeilennr, ladeBez);
        is_error = 1;
        return 1;
    }
    leitadresseKennzeichen = wert;
    return 1;
}

// Blockkommentar: Eine Zeile, die ab Spalte 1 genau ``` enthaelt (danach nur Leerraum), eroeffnet bzw.
// beendet einen Blockkommentar. Alles dazwischen (und die beiden ```-Zeilen selbst) wird wie ein
// Kommentar ueberlesen und erzeugt keine Programmzeile.
static int istBlockkommentarGrenze(const char *s) {
    if (strncmp(s, "```", 3) != 0) return 0;
    for (s += 3; *s; s++) {
        if (*s != ' ' && *s != '\t' && *s != '\r' && *s != '\n') return 0;
    }
    return 1;
}

// ---------------------------------------------------------------------------------------------------------------
// $INCLUDE im Quelltext (Doku 4.14): Die Zeilen der eingebundenen Datei kommen an der Stelle der $INCLUDE-Zeile nach
// linesAsm, als stuenden sie im Quelltext. srcLine zaehlt fortlaufend ueber ALLE gelesenen Dateien (ohne $INCLUDE ist
// das genau die Zeilennummer der Datei); die Tabelle quellAbschnitte bildet eine solche Nummer auf Datei und Zeile in
// der Datei ab. Alle Meldungen mit Ort laufen ueber qDatei/qZeile/qOrt.
#define QUELL_INCLUDE_TIEFE 4

typedef struct { int ab; int datei; int versatz; } QuellAbschnitt;   // Zeile in der Datei = nr - versatz, gueltig ab nr = ab
static QuellAbschnitt *quellAbschnitte = NULL;
static int quellAbschnittN = 0, quellAbschnittKap = 0;
static char **quellDateien = NULL;       // Index 0 = Hauptdatei (inputFileName), danach die eingebundenen Dateien
static int quellDateiN = 0, quellDateiKap = 0;
static char **quellTexte = NULL;         // Text jeder gelesenen Zeile (Index = fortlaufende Nummer, 0 unbenutzt)
static int quellTextN = 0, quellTextKap = 0;
static int quellZaehler = 0;             // fortlaufende Nummer der zuletzt gelesenen Zeile
static int includeBenutzt = 0;           // 1, sobald eine Datei eingebunden wurde

static void *quellWachsen(void *p, int *kap, int n, size_t gr) {
    if (n < *kap) return p;
    int neuKap = *kap ? *kap * 2 : 256;
    void *q = realloc(p, (size_t)neuKap * gr);
    if (!q) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    *kap = neuKap;
    return q;
}

static void quellAbschnittNeu(int ab, int datei, int versatz) {
    quellAbschnitte = quellWachsen(quellAbschnitte, &quellAbschnittKap, quellAbschnittN, sizeof(QuellAbschnitt));
    quellAbschnitte[quellAbschnittN].ab = ab;
    quellAbschnitte[quellAbschnittN].datei = datei;
    quellAbschnitte[quellAbschnittN].versatz = versatz;
    quellAbschnittN++;
}

static int quellDateiMerken(const char *name) {
    quellDateien = quellWachsen(quellDateien, &quellDateiKap, quellDateiN, sizeof(char *));
    quellDateien[quellDateiN] = strdup(name);
    return quellDateiN++;
}

// Merkt den Text der Zeile nr (ohne Zeilenende) fuer Querverweisliste und Fehlersuche im Quelltext.
static void quellTextMerken(int nr, const char *text) {
    while (quellTextN <= nr) {
        quellTexte = quellWachsen(quellTexte, &quellTextKap, quellTextN, sizeof(char *));
        quellTexte[quellTextN++] = NULL;
    }
    free(quellTexte[nr]);
    char *k = strdup(text);
    if (k) {
        size_t l = strlen(k);
        while (l > 0 && (k[l - 1] == '\n' || k[l - 1] == '\r')) k[--l] = '\0';
    }
    quellTexte[nr] = k;
}

int quellZeilenAnzahl(void) { return quellTextN > 0 ? quellTextN - 1 : 0; }
const char *quellZeilenText(int nr) { return (nr > 0 && nr < quellTextN && quellTexte[nr]) ? quellTexte[nr] : ""; }

static int quellAbschnittFuer(int nr) {
    int a = -1;
    for (int i = 0; i < quellAbschnittN; i++) { if (quellAbschnitte[i].ab <= nr) a = i; else break; }
    return a;
}

// Datei und Zeile in der Datei zur fortlaufenden Nummer nr. Ohne $INCLUDE (oder bei nr <= 0) gilt nr unveraendert.
const char *qDatei(int nr) {
    if (!includeBenutzt || nr <= 0) return inputFileName;
    int a = quellAbschnittFuer(nr);
    return (a < 0 || quellAbschnitte[a].datei <= 0) ? inputFileName : quellDateien[quellAbschnitte[a].datei];
}
int qZeile(int nr) {
    if (!includeBenutzt || nr <= 0) return nr;
    int a = quellAbschnittFuer(nr);
    return a < 0 ? nr : nr - quellAbschnitte[a].versatz;
}
// Ort als Text fuer "Zeile %s": "12" in der Hauptdatei, "3 von 'inc/x.asm'" in einer eingebundenen Datei.
const char *qOrt(int nr) {
    static char puffer[4][1200];
    static int next = 0;
    char *b = puffer[next++ & 3];
    int a = (includeBenutzt && nr > 0) ? quellAbschnittFuer(nr) : -1;
    if (a >= 0 && quellAbschnitte[a].datei > 0)
        snprintf(b, 1200, "%d von '%s'", nr - quellAbschnitte[a].versatz, quellDateien[quellAbschnitte[a].datei]);
    else
        snprintf(b, 1200, "%d", qZeile(nr));
    return b;
}

// Ist die Zeile (nach Leerraum) eine $INCLUDE-Zeile? $INCLUDE als ganzes Wort (Leerraum oder Zeilenende dahinter).
static int istIncludeZeile(const char *line) {
    while (*line == ' ' || *line == '\t') line++;
    if (strncmp(line, "$INCLUDE", 8) != 0) return 0;
    return line[8] == ' ' || line[8] == '\t' || line[8] == '\0' || line[8] == '\r' || line[8] == '\n';
}

// Ist die Zeile ein Pragma ;#MACRODATEI... oder ;#OPSYM..., das nur in der Hauptdatei gilt?
static int istHauptdateiPragma(const char *line) {
    while (*line == ' ' || *line == '\t') line++;
    if (*line != ';') return 0;
    line++;
    while (*line == ' ' || *line == '\t') line++;
    return strncmp(line, "#MACRODATEI", 11) == 0 || strncmp(line, "#OPSYM", 6) == 0;
}

static int startGesehenGlobal = 0;   // 1, sobald die Anweisung `start` gelesen wurde (Pragma LEITADRESSE muss davor stehen)
static int ladeDatei(const char *pfad, int dateiIdx, int tiefe);

// Wertet eine $INCLUDE-Zeile aus und liest die Datei. nr = fortlaufende Nummer der $INCLUDE-Zeile, dateiZeile = Zeile in
// der einbindenden Datei, basis = Pfad der einbindenden Datei.
static void ladeInclude(const char *line, const char *basis, int nr, int dateiZeile, int tiefe) {
    char pfad[1024];
    const char *p = line;
    while (*p == ' ' || *p == '\t') p++;
    p += 8;                                          // hinter "$INCLUDE"
    while (*p == ' ' || *p == '\t') p++;
    snprintf(pfad, sizeof(pfad), "%s", p);
    char *sem = strchr(pfad, ';');
    if (sem && (sem == pfad || sem[-1] == ' ' || sem[-1] == '\t')) *sem = '\0';
    size_t l = strlen(pfad);
    while (l > 0 && (pfad[l - 1] == ' ' || pfad[l - 1] == '\t' || pfad[l - 1] == '\r' || pfad[l - 1] == '\n')) pfad[--l] = '\0';
    if (l >= 2 && (pfad[0] == '"' || pfad[0] == '\'') && pfad[l - 1] == pfad[0]) { memmove(pfad, pfad + 1, l - 2); pfad[l - 2] = '\0'; }
    if (pfad[0] == '\0') {
        PRINT_FEHLER("Zeile %d %s: $INCLUDE braucht einen Pfad.", dateiZeile, ladeBez);
        is_error = 1;
        return;
    }
    if (tiefe > QUELL_INCLUDE_TIEFE) {
        PRINT_FEHLER("Zeile %d %s: $INCLUDE '%s' ist zu tief verschachtelt (höchstens %d; ein Kreis wird so abgefangen).", dateiZeile, ladeBez, pfad, QUELL_INCLUDE_TIEFE);
        is_error = 1;
        return;
    }
    char voll[2048] = "";
    FILE *inc = NULL;
    int absolut = (pfad[0] == '/' || pfad[0] == '\\' || (isalpha((unsigned char)pfad[0]) && pfad[1] == ':'));
    if (!absolut) {
        snprintf(voll, sizeof(voll), "%s", basis);
        char *slash = strrchr(voll, '/');
        char *bslash = strrchr(voll, '\\');
        if (bslash && (!slash || bslash > slash)) slash = bslash;
        if (slash) {
            slash[1] = '\0';
            strncat(voll, pfad, sizeof(voll) - strlen(voll) - 1);
            inc = fopen(voll, "r");
        }
    }
    if (!inc) {
        snprintf(voll, sizeof(voll), "%s", pfad);
        inc = fopen(voll, "r");
    }
    if (!inc) {
        PRINT_FEHLER("Zeile %d %s: $INCLUDE '%s' konnte nicht geöffnet werden: %s", dateiZeile, ladeBez, pfad, strerror(errno));
        is_error = 1;
        return;
    }
    fclose(inc);

    // Kommentarzeile im Listing vor den eingebundenen Zeilen (wie ";+++ <Aufruf>" bei Makros)
    {
        char kom[1300];
        snprintf(kom, sizeof(kom), ";+++ $INCLUDE %s", pfad);
        lineElements *z = &linesAsm[lineCountAsm];
        resetParsedLinesArrays(linesAsm, lineCountAsm);
        STRKOPIE(z->sp1, kom);
        z->srcLine = nr;
        lineCountAsm++;
    }
    includeBenutzt = 1;
    int idx = quellDateiMerken(voll);
    char bezAlt[1100];
    snprintf(bezAlt, sizeof(bezAlt), "%s", ladeBez);
    int hauptAlt = ladeIstHaupt;
    snprintf(ladeBez, sizeof(ladeBez), "der eingebundenen Datei '%s'", pfad);
    ladeIstHaupt = 0;
    quellAbschnittNeu(quellZaehler + 1, idx, quellZaehler);
    ladeDatei(voll, idx, tiefe);
    snprintf(ladeBez, sizeof(ladeBez), "%s", bezAlt);
    ladeIstHaupt = hauptAlt;
    quellAbschnittNeu(quellZaehler + 1, quellAbschnitte[quellAbschnittFuer(nr)].datei, quellZaehler - dateiZeile);
}

// Liest eine Datei (Hauptdatei oder $INCLUDE) Zeile fuer Zeile nach linesAsm. Rueckgabe 0 = ok, 1 = Abbruch (Zeilengrenze).
static int ladeDatei(const char *pfad, int dateiIdx, int tiefe) {
    (void)dateiIdx;
    FILE *inputFile = fopen(pfad, "r");
    if (!inputFile) {
        fprintf(stderr, "Fehler: Datei '%s' konnte nicht geöffnet werden!\n", pfad);
        exit(RC_FEHLER); // Programm beenden, falls Datei nicht geöffnet werden konnte
    }

    char line[1024];
    int zeilennr = 0;           // Zeilennummer in DIESER Datei
    int vorigeZeileOffen = 0;   // 1 = vorige fgets-Teilzeile hatte kein Zeilenende (Zeile laenger als Puffer)
    int imBlockkommentar = 0;   // 1 = zwischen zwei ```-Zeilen
    int blockkommentarStart = 0; // Zeile (dieser Datei), in der der offene Blockkommentar begann
    int abbruch = 0;
    while (fgets(line, sizeof(line), inputFile)) {
        int hatZeilenende = (strchr(line, '\n') != NULL);

        if (vorigeZeileOffen) {            // Rest einer bereits gemeldeten, zu langen Zeile ueberspringen
            vorigeZeileOffen = !hatZeilenende;
            continue;
        }
        if (zeilennr == 0 && (unsigned char)line[0] == 0xEF && (unsigned char)line[1] == 0xBB && (unsigned char)line[2] == 0xBF) {
            memmove(line, line + 3, strlen(line + 3) + 1);   // UTF-8-Bytefolgemarke (BOM, z. B. aus dem Windows-Editor) ueberspringen
        }
        zeilennr++;
        quellZaehler++;
        int nr = quellZaehler;   // fortlaufende Nummer (srcLine)
        quellTextMerken(nr, line);

        // Blockkommentar (```-Zeilen und alles dazwischen) - auch zu lange Zeilen darin sind kein Fehler
        int istGrenze = istBlockkommentarGrenze(line);
        if (istGrenze || imBlockkommentar) {
            if (!hatZeilenende && !feof(inputFile)) vorigeZeileOffen = 1;
            if (istGrenze) {
                imBlockkommentar = !imBlockkommentar;
                if (imBlockkommentar) blockkommentarStart = zeilennr;
            }
            continue;
        }

        if (*line == '\0' || strcmp(line, "\n") == 0) {
            continue;
        }

        removeNewlines(line);

        // Die internen Zeilenpuffer (elementType) fassen nur MAX_QUELLZEILE Zeichen (Bytes).
        // Laengere Zeilen wuerden einen Pufferueberlauf (Absturz) ausloesen -> sauber melden.
        size_t laenge = strlen(line);
        if (laenge > 0 && line[laenge - 1] == '\r') {
            line[--laenge] = '\0';
        }
        if (!hatZeilenende && !feof(inputFile)) {
            vorigeZeileOffen = 1;
            laenge = MAX_QUELLZEILE + 1;   // laenger als der Lesepuffer, also sicher zu lang
        }
        if (laenge > MAX_QUELLZEILE) {
            PRINT_FEHLER("Zeile %d %s ist zu lang (mehr als %d Zeichen); bitte kuerzen oder umbrechen.", zeilennr, ladeBez, MAX_QUELLZEILE);
            is_error = 1;
            continue;
        }
        if (lineCountAsm >= ZEILEN_GRENZE) {
            meldeZuVieleZeilen(nr);
            is_error = 1;
            abbruch = 1;
            break;
        }
        if (istIncludeZeile(line)) {
            quellTextMerken(nr, ";");   // der Dateiname soll in der Querverweisliste kein Symbol treffen
            ladeInclude(line, pfad, nr, zeilennr, tiefe + 1);
            continue;
        }
        if (!ladeIstHaupt && istHauptdateiPragma(line)) {
            PRINT_FEHLER("Zeile %d %s: ;#MACRODATEI und ;#OPSYM gelten nur in der Hauptdatei, nicht in einer mit $INCLUDE eingebundenen Datei.", zeilennr, ladeBez);
            is_error = 1;
            continue;
        }
        verarbeiteLeitadressePragma(line, zeilennr, startGesehenGlobal);   // vor processLine: line wird dort veraendert
        int zeilenVorher = lineCountAsm;
        {
            int vorher = lineCountAsm;
            processLine(line, linesAsm, &lineCountAsm);
            for (int k = vorher; k < lineCountAsm; k++) linesAsm[k].srcLine = nr;
        }
        if (lineCountAsm > zeilenVorher && gleichOhneGrossKlein(linesAsm[lineCountAsm - 1].sp2, "start")) {
            startGesehenGlobal = 1;
        }
    }
    fclose(inputFile);

    if (imBlockkommentar) {
        PRINT_FEHLER("Zeile %d %s: Der Blockkommentar (```) wird bis zum Dateiende nicht geschlossen.", blockkommentarStart, ladeBez);
        is_error = 1;
    }
    return abbruch;
}

void ladeAssemblerZeilen(const char *inputFileName_p) {
    quellDateiMerken(inputFileName_p);        // Index 0 = Hauptdatei
    quellAbschnittNeu(1, 0, 0);
    ladeDatei(inputFileName_p, 0, 0);
    //printAssemblerzeilenArray() ;
}


// ------------------------------








// ######################################################

const int trommel_sektor_map[32] = {
    0, 015, 032, 07, 024, 01, 016, 033, 010, 025, 02,
    017, 034, 011, 026, 03, 020, 035, 012, 027, 04, 021,
    036, 013, 030, 05, 022, 037, 014, 031, 06, 023
};

unsigned int berechneWiederholAdr(int anzahl, unsigned int basisAdr ) {
    // Wiederholungsbefehl: n Zellen von der Startzelle bis Sektor 023; die Folgezellen liegen je 13 Sektoren weiter (Tabelle
    // trommel_sektor_map = 13*i mod 32). Startsektor fuer n Wiederholungen = map[32 - n] (n = 1..32; vorher 31 - n - 1 = 2 zu wenig).
    if (anzahl < 1) anzahl = 1;
    if (anzahl > 32) anzahl = 32;
    int x = 32 - anzahl;
    unsigned int sektor = trommel_sektor_map[x] + basisAdr;

    return sektor;
}

int berechneOperand(const char *operand_str) {
    int zahl1, zahl2;
    char op;

    // Versuch, einen mathematischen Ausdruck zu parsen: z.B. "9-1" oder "-5+3"
    if (sscanf(operand_str, "%d %c %d", &zahl1, &op, &zahl2) == 3) {
        switch (op) {
            case '+': return zahl1 + zahl2;
            case '-': return zahl1 - zahl2;
            case '*': return zahl1 * zahl2;
            case '/': return zahl2 != 0 ? zahl1 / zahl2 : 0; // Division durch 0 vermeiden
            default: fprintf(stderr, "Fehler: Unbekannter Operator '%c'\n", op); return 0;
        }
    }

    // Falls kein Operator gefunden wurde, einfach die Zahl konvertieren
    return strtol(operand_str, NULL, 10);
}


void verarbeiteZeile_wdhl_adr_e(char *tempLine) {
    char *start = strstr(tempLine, "!$wdhl_adr_e");

    // Suche nach dem Operand (erste Zahl nach !#wdhl")
    start += 12; // Springt hinter "!#wdhl_adr_e"
    while (*start == ' ') start++; // Ignoriere Leerzeichen

    char operand_str[MAX_LINE_LENGTH];
    char basis_str[MAX_LINE_LENGTH] = "";
    sscanf(start, "%s %s", operand_str, basis_str);
    // Zweiter Operand: Anfang der Spur, auf der der Wiederholungsbefehl laeuft (oktal mit fuehrender 0, sonst dezimal).
    // Das Programm stellt diese Spur selbst bereit (eine Nullspur ist nirgends vorausgesetzt).
    unsigned int basis_adr = 0;
    if (basis_str[0] == '\0') {
        fprintf(stderr, "Fehler: !$wdhl_adr_e ohne Spuradresse (zweiter Operand)\n");
    } else {
        basis_adr = (unsigned int) strtol(basis_str, NULL, basis_str[0] == '0' ? 8 : 10);
    }

    // Berechne den Wert des Operanden
    //int operand_value = strtol(operand_str, NULL, 10) - 1; // `9-1` → `8`
    int operand_value = berechneOperand(operand_str);
    unsigned int sektor_address = berechneWiederholAdr(operand_value, basis_adr);

    // Erstelle die neue Zeile mit der oktalen Sektoradresse (mit Vornull)
    char neueZeile[MAX_LINE_LENGTH];
    snprintf(neueZeile, sizeof(neueZeile), "     !$wdhl_adr_e   %05o     ; %d mal Linksverschiebung", sektor_address, operand_value);
    strkopiere(tempLine, MACRO_PARAMETER_LAENGE, neueZeile);

    char *pos = strstr(tempLine, "!$wdhl_adr_e");
    if (pos != NULL) {
        // Länge des zu ersetzenden Substrings ermitteln
        size_t lenAlt = strlen("!$wdhl_adr_e");
        size_t lenNeu = strlen("644");

        // Verschiebt den restlichen Text nach links, falls nötig
        memmove(pos + lenNeu, pos + lenAlt, strlen(pos + lenAlt) + 1);
        memcpy(pos, "644", lenNeu);
    }
}

int verarbeiteZeile_wdhl(char *tempLine, char *loe, char *resu, char *opcode, char *anzahl, char *adresse) {
    char op[32]={0};
    int rc = 0 ;

    int berechneOpString(char *opStr, char *rStr, char *loe_p, char *result) {
        (void)rStr;
        int rc_in = 0;
        char *OPCODE[]              = { "KON", "ADD", "SUB", "BADD" };
        int OP_Table[]              = { 060, 061, 062, 063 };
        int R_Zuordnung[]           = { 04, 02, 06, 0 };
        int R_Zuordnung_Loe[]       = { 05, 03, 07, 01 };

        int opNum = -1, rNum = -1;

        for (size_t i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                opNum = OP_Table[i];
                break;
            }
        }

        if ( opNum == -1 ) { return -1; }

        // R-Zuordnung basierend auf LOE (JA vs NE)
        int *R_Table = (strcmp(loe_p, "JA") == 0) ? R_Zuordnung_Loe : R_Zuordnung;
        for (size_t i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                rNum = R_Table[i];
                break;
            }
        }

        if ( rNum == -1 ) { return -1; }

        // Falls beide Werte gefunden wurden, erstelle den Ziffernstring
        if (opNum != -1 && rNum != -1) {
            snprintfGekuerzt(result, 10, "%o%o", opNum, rNum);
        } else {
            strkopiere(result, 32, "Macro gen. Op-Code Mismatch ??"); // Fehlerfall
            rc_in = -1;
        }

        return rc_in;
    }

    rc = berechneOpString(opcode, resu, loe, op);
    if ( (rc == -1 ) || ( rc == -2 ) ) { return rc; }

    unsigned int basis_adr;
    if ( adresse[0] == '0' ) {
       basis_adr = strtol(adresse, NULL, 8);
    } else { 
       basis_adr = strtol(adresse, NULL, 10);
    }

    int anz = berechneOperand(anzahl);
    unsigned int sektor_address = berechneWiederholAdr(anz, basis_adr);

    char neueZeile[MAX_LINE_LENGTH];
    snprintf(neueZeile, sizeof(neueZeile), "     !#wdhl   %05o     ; %d mal Linksverschiebung", (unsigned int)  sektor_address, anz);
    strkopiere(tempLine, MACRO_PARAMETER_LAENGE, neueZeile);

    char *pos = strstr(tempLine, "!#wdhl");
    if (pos != NULL) {
        memmove(pos + 3, pos + 6, strlen(pos + 6) + 1);
        memcpy(pos, op, 3);
    }
    if ( (rc == -3 )  ) { return rc; }
    return 0;
}
