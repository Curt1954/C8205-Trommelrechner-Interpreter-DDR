// ca82_makros.c - Version 1.03-009 (siehe ca82_version.h)
// Makrodatei und Quelltextmakros einlesen, Makros aufloesen ($IF/$PR/$WDHL/$SPRUNG).
#include "ca82_typen.h"
#include "ca82_makros.h"
#include "ca82_intern.h"   // absprAktiv, schreibeLochbilder (PRECOMMAND/POSTCOMMAND, ab 1.03-009)
#include "ca82_version.h"
#include "ca82_symbole.h"
#include "ca82_berichte.h"
#include <stdarg.h>
#include <errno.h>

macroDefinitionen *macros;          // dynamisch zugewiesenes Array der Makrodefinitionen
int macroCount = 0;
int macroCapacity = INITIAL_SIZE;
char recursiv_macro[128] = "";

// Kopiert src nach out (Puffergroesse groesse), kuerzt bei Bedarf auf groesse-1 Zeichen und fuellt den Rest mit '\0'.
// Gleiche Wirkung wie strncpy(out, src, groesse - 1) mit anschliessendem Terminieren, aber ohne -Wstringop-truncation.
static void kopiereBegrenzt(char *out, size_t groesse, const char *src) {
    size_t len = strlen(src);
    if (len > groesse - 1) len = groesse - 1;
    memcpy(out, src, len);
    memset(out + len, 0, groesse - len);
}

int isNumeric(const char *str) {
    if (str[0] == '-' && isdigit((unsigned char)str[1])) str++;   // negative Zahl (Ergebnis von $CALC)
    if (*str == '\0') return 1;
    size_t n = 0;
    while (*str) {
        if (!isdigit(*str)) return 0; // Wenn ein Zeichen kein Digit ist, ist es nicht numerisch
        str++;
        n++;
    }
    return n <= 18;   // laengere Ziffernfolgen passen nicht sicher in 64 Bit und werden alphabetisch verglichen
}

int macroParameterCompare(const char *a, const char *b, const char *c) {
//printf("DEBUG: a=%s, b=%s, c=%s\n", a, b, c);

    if (isNumeric(a) && isNumeric(c)) { // Falls beide Parameter numerisch sind, vergleiche als Zahlen (64 Bit wie $CALC)
        long long valA = strtoll(a, NULL, 10);
        long long valC = strtoll(c, NULL, 10);

        if (strcmp(b, ">") == 0) return valA > valC;
        if (strcmp(b, "<") == 0) return valA < valC;
        if (strcmp(b, "=") == 0) return valA == valC;
        if (strcmp(b, ">=") == 0) return valA >= valC;
        if (strcmp(b, "<=") == 0) return valA <= valC;
        if (strcmp(b, "!=") == 0 || strcmp(b, "<>") == 0) return valA != valC;
    } else { // Falls nicht numerisch, vergleiche alphabetisch
        if (strcmp(b, ">") == 0) return strcmp(a, c) > 0;
        if (strcmp(b, "<") == 0) return strcmp(a, c) < 0;
        if (strcmp(b, "=") == 0) return strcmp(a, c) == 0;
        if (strcmp(b, ">=") == 0) return strcmp(a, c) >= 0;
        if (strcmp(b, "<=") == 0) return strcmp(a, c) <= 0;
        if (strcmp(b, "!=") == 0 || strcmp(b, "<>") == 0) return strcmp(a, c) != 0;
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


// Typpruefung fuer Makro-Parameter ($PRx: $TYPADR | $TYPKON | $TYPABS | $TYPSYM).
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
    if (strcmp(typ, "$TYPSYM") == 0) {
        if (!istSymbolName(arg)) {
            snprintf(meldung, meldungGroesse, "Wert \"%.100s\" ist kein Symbol (Buchstaben, Ziffern und _, nicht mit einer Ziffer beginnend)", arg);
            return 1;
        }
        return 0;
    }
    if (strcmp(typ, "$TYPABS") == 0) {
        for (int z = 0; z < lineCountAsm; z++) {
            char marke[256];
            kopiereBegrenzt(marke, sizeof(marke), linesAsm[z].sp1);
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
    snprintfGekuerzt(result, sizeof(result), "%.*s", (int)(end - start), start);
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
    kopiereBegrenzt(mtemp, sizeof(mtemp), ergebnis[i].sp1);   // Null-Termination ist enthalten
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
    "$IF", "$ELIF", "$ELSE", "$ENDIF", "$REPT", "$ENDREPT", "!$wdhl", "$wrzl", "$sm", "$inkb", "$ingb",
    "$irrz", "$irrs", "$trans", "$bm", "$vorl", "$irrb", "$tab", "$zr", "$wr",
    "!$wdhl_adr_e", "$TYPADR", "$TYPKON", "$TYPABS", "$TYPZAHL", "$TYPSYM", "$TYPTEXT", "$ERROR", "$WARN", "$DEFAULT", "$#", "$SET", "$INC", "$DIM", "$LOCAL", "$GLOBAL", "$WHILE", "$ENDWHILE", "$EXIT",
    "$SUBSTR", "$INDEX", "$UPPER", "$LOWER", "$STRCMP", "$ORD", "$CHR", "$VAL", "$VALO", "$VALB", "$VALH",
    "$NOTE", "$TRACE", "$DUMP", "$BLOCK", "$ENDBLOCK"
};
const int validMacroCount = sizeof(validMacroKeywords) / sizeof(validMacroKeywords[0]);

const char *restrictedKeywords[] = {
    "$PR1", "$PR2", "$PR3", "$PR4", "$PR5", "$PR6", "$PR7", "$PR8", "$PR9",
    "$IF", "$ELIF", "$ELSE", "$ENDIF", "$REPT", "$ENDREPT", "!$wdhl", "$wrzl", "$sm", "$inkb", "$ingb",
    "$irrz", "$irrs", "$trans", "$bm", "$vorl", "$irrb", "$tab", "$zr", "$wr",
    "!$wdhl_adr_e", "$TYPADR", "$TYPKON", "$TYPABS", "$TYPZAHL", "$TYPSYM", "$TYPTEXT", "$ERROR", "$WARN", "$DEFAULT", "$#", "$SET", "$INC", "$DIM", "$LOCAL", "$GLOBAL", "$WHILE", "$ENDWHILE", "$EXIT",
    "$SUBSTR", "$INDEX", "$UPPER", "$LOWER", "$STRCMP", "$ORD", "$CHR", "$VAL", "$VALO", "$VALB", "$VALH",
    "$NOTE", "$TRACE", "$DUMP", "$BLOCK", "$ENDBLOCK"
};
const int restrictedCount = sizeof(restrictedKeywords) / sizeof(restrictedKeywords[0]);

const char *validPR[] = {"$PR1", "$PR2", "$PR3", "$PR4", "$PR5", "$PR6", "$PR7", "$PR8", "$PR9"};
const char *validType[] = {"$TYPADR", "$TYPKON", "$TYPABS", "$TYPSYM"};   // $TYPZAHL und $TYPTEXT haben eigene Zweige

// ---------------------------------------------------------------------------------------------------------------
// Benannte Parameter (Doku 4.26): Hilfsfunktionen
// ---------------------------------------------------------------------------------------------------------------
#define MAKRO_NAME_MAX 24   // hoechste Laenge eines Parameternamens

static int makroBuchstabeUnter(int c) { return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '_'; }
static int makroBuchstabeZiffer(int c) { return makroBuchstabeUnter(c) || (c >= '0' && c <= '9'); }
static int makroZiffer(int c) { return c >= '0' && c <= '9'; }

// Laenge des Wortes [A-Za-z_][A-Za-z0-9_]* am Anfang von s; 0, wenn s nicht mit einem Buchstaben oder _ beginnt.
static size_t makroNameLaenge(const char *s) {
    size_t n = 0;
    if (!makroBuchstabeUnter((unsigned char)s[0])) return 0;
    while (makroBuchstabeZiffer((unsigned char)s[n])) n++;
    return n;
}

// Feste Woerter des Makrosystems (ohne das $): Schluesselwoerter, Funktionen, Typnamen und die Namen der dz-Sonderzeichen.
// Dazu kommen PR + 1 bis 2 Ziffern, LEN + Ziffer 1 bis 9, Z + Ziffer 1 bis 4 und CALCO + Ziffer 1 bis 9 und CALCB und CALCH + 1 bis 2 Ziffern (makroFestesWort).
static const char *const makroFesteWoerter[] = {
    "IF", "ELIF", "ELSE", "ENDIF", "REPT", "ENDREPT", "WHILE", "ENDWHILE", "EXIT", "LOCAL", "GLOBAL", "SET", "INC", "DIM", "DEFAULT",
    "CALC", "CALCO", "CALCB", "CALCH", "V", "P", "PR", "LEN", "Z", "INCLUDE", "NOTE", "WARN", "ERROR", "TRACE", "DUMP", "DEFINED", "MDEFINED", "PROBE", "AUFRUFNR",
    "SUBSTR", "INDEX", "UPPER", "LOWER", "STRCMP", "ORD", "CHR", "VAL", "VALO", "VALB", "VALH",
    "TYPADR", "TYPKON", "TYPABS", "TYPZAHL", "TYPSYM", "TYPTEXT", "ADRESSE",
    "wdhl", "wdhl_adr_e", "wrzl", "sm", "inkb", "ingb", "irrz", "irrs", "trans", "bm", "vorl", "irrb", "tab", "zr", "wr"
};

// 1, wenn die ersten len Zeichen von a und b gleich sind (ohneGrossKlein: ASCII-Buchstaben ohne Beachtung der Schreibweise)
static int makroWortGleich(const char *a, const char *b, size_t len, int ohneGrossKlein) {
    for (size_t i = 0; i < len; i++) {
        int x = (unsigned char)a[i], y = (unsigned char)b[i];
        if (ohneGrossKlein) {
            if (x >= 'A' && x <= 'Z') x += 'a' - 'A';
            if (y >= 'A' && y <= 'Z') y += 'a' - 'A';
        }
        if (x != y) return 0;
    }
    return 1;
}

// 1, wenn das Wort wort[0..len) ein festes Wort ist. In der MACRO-Zeile gilt ohneGrossKlein = 1, im Rumpf 0.
static int makroFestesWort(const char *wort, size_t len, int ohneGrossKlein) {
    for (size_t i = 0; i < sizeof(makroFesteWoerter) / sizeof(makroFesteWoerter[0]); i++) {
        if (strlen(makroFesteWoerter[i]) == len && makroWortGleich(wort, makroFesteWoerter[i], len, ohneGrossKlein)) return 1;
    }
    struct { const char *kopf; size_t kl; int ziffern; char von; char bis; } form[] = {
        { "PR", 2, 2, '0', '9' }, { "LEN", 3, 1, '1', '9' }, { "Z", 1, 1, '1', '4' }, { "CALCO", 5, 1, '1', '9' }, { "CALCB", 5, 2, '1', '9' }, { "CALCH", 5, 2, '1', '9' }
    };
    for (size_t i = 0; i < sizeof(form) / sizeof(form[0]); i++) {
        if (len <= form[i].kl || !makroWortGleich(wort, form[i].kopf, form[i].kl, ohneGrossKlein)) continue;
        size_t rest = len - form[i].kl;
        if (rest > (size_t)form[i].ziffern) continue;
        int ok = 1;
        for (size_t k = 0; k < rest; k++) {
            char c = wort[form[i].kl + k];
            if (!makroZiffer((unsigned char)c)) ok = 0;
            else if (k == 0 && (c < form[i].von || c > form[i].bis)) ok = 0;
        }
        if (form[i].kopf[0] == 'P' && rest == 1 && wort[form[i].kl] == '0') ok = 0;   // PR0 gibt es nicht
        if (ok) return 1;
    }
    return 0;
}

// Nummer (1-basiert) des Parameternamens wort[0..len) im Makro m; Gross- und Kleinschreibung zaehlen. 0 = kein Name dieses Makros.
static int makroNamenSuche(const macroDefinitionen *m, const char *wort, size_t len) {
    for (int k = 0; k < m->macroParameterAnzahl && k < MACRO_PARAMETER_ANZAHL; k++) {
        if (strlen(m->macroParameters[k]) == len && strncmp(m->macroParameters[k], wort, len) == 0) return k + 1;
    }
    return 0;
}

// $PR + 1 bis 2 Ziffern am Anfang von s: die Nummer; *laenge = Zeichenzahl der Angabe ($PR12 = 5; laenge darf NULL sein).
// 0 = keine $PR-Nummer (auch $PR0 und $PR05: eine fuehrende 0 gibt es nicht).
// Das Zeichen hinter der Nummer wird wie bisher nicht geprueft.
static int makroPrNummer(const char *s, int *laenge) {
    if (strncmp(s, "$PR", 3) != 0 || !makroZiffer((unsigned char)s[3]) || s[3] == '0') return 0;
    int n = s[3] - '0';
    int l = 4;
    if (makroZiffer((unsigned char)s[4])) { n = n * 10 + (s[4] - '0'); l = 5; }
    if (laenge != NULL) *laenge = l;
    return n;
}

// Bezeichnung des Parameters nr in Meldungen: "$name" bei benannten Makros, sonst "$nr".
static void makroParamBez(const macroDefinitionen *m, int nr, char *out, size_t n) {
    if (m != NULL && m->benannt == 1 && nr >= 1 && nr <= MACRO_PARAMETER_ANZAHL && m->macroParameters[nr - 1][0] != '\0') {
        snprintf(out, n, "$%.40s", m->macroParameters[nr - 1]);
    } else {
        snprintf(out, n, "$%d", nr);
    }
}

// Fehlerliste eines Makroaufrufs (Fehler der Makrodefinition und der $IF-Auswertung)
#define MAKRO_MAX_FEHLER 64
typedef struct {
    char tab[MAKRO_MAX_FEHLER][512];
    int zeile[MAKRO_MAX_FEHLER];   // Quelltextzeile, an der der Fehler entstand (nur im Quelltextmodus belegt, Doku 4.1)
    int anzahl;
} MakroFehler;

// Quelltextzeile, die gerade ausgewertet wird (gesetzt in makroBedingungenAuswerten, reptExpandiere und der $CALC-Schleife);
// meldeMakroFehler schreibt sie zum Fehler, damit ein Fehler im normalen Quelltext an seiner Zeile steht.
static int makroAktuelleZeile = 0;

// Eine Zeile der Makrodefinition, gekuerzt auf die Puffergroessen der Pruefungen
typedef struct {
    char sp1[256];
    char sp2[128];
    char sp3[256];
    char sp4[256];
} MakroZeile;

static void holeMakroZeile(const macroDefinitionen *m, int j, MakroZeile *z) {
    kopiereBegrenzt(z->sp1, sizeof(z->sp1), m->macroParsedLines[j].sp1);
    kopiereBegrenzt(z->sp2, sizeof(z->sp2), m->macroParsedLines[j].sp2);
    kopiereBegrenzt(z->sp3, sizeof(z->sp3), m->macroParsedLines[j].sp3);
    kopiereBegrenzt(z->sp4, sizeof(z->sp4), m->macroParsedLines[j].sp4);
}

static void meldeMakroFehler(MakroFehler *f, const char *format, const char *arg1, const char *arg2, const char *arg3) {
    if (f->anzahl >= MAKRO_MAX_FEHLER) {
        PRINT_FEHLER("%s", "Zu viele Fehler im Macro.");
        is_error = 1;
        return;
    }

    snprintf(f->tab[f->anzahl], 511, ";%s*** Fehler %s %s ", _violett, _normal, arg1);
    snprintf(f->tab[f->anzahl] + strlen(f->tab[f->anzahl]), 511 - strlen(f->tab[f->anzahl]), format, arg1, arg2, arg3);
    f->zeile[f->anzahl] = makroAktuelleZeile;
    f->anzahl++;
}

// Text der ersten Meldung in f ohne den Kopf ";<Farbe>*** Fehler <Farbe> " (fuer Fehler, die als Grund einer Direktive gemeldet werden, Doku 4.22)
static const char *makroFehlerText(const MakroFehler *f) {
    char kopf[96];
    snprintf(kopf, sizeof(kopf), ";%s*** Fehler %s %s ", _violett, _normal, "");
    size_t k = strlen(kopf);
    return strlen(f->tab[0]) >= k ? f->tab[0] + k : f->tab[0];
}


// ----------------------------------------------------------------------------------
// Rechenausdruecke im Makro: $CALC(ausdruck) liefert das Ergebnis dezimal, $CALCO(ausdruck) oktal mit fuehrender 0.
// Wirkt nach der Ersetzung der Parameter $1..$9 (Doku 4.2). Der Ausdruck enthaelt keine Leerzeichen.
//   Zahlen:     fuehrende 0 = oktal (z. B. 07640), sonst dezimal (z. B. 19)
//   Symbole:    Namen, die im Quelltext mit `abs <Zahl>` oder `equ <Zahl>` einen festen Zahlenwert haben (Doku 4.18, ab 1.00-062)
//   Operatoren: * / % (Rest)  |  + -  |  << >>  |  &  |  ^  |  |   (Rangfolge wie in C, links nach rechts), unaeres - + ~, Klammern ( )
// Ganzzahlen mit Vorzeichen (long long); Division und Rest durch 0 sowie nichtnumerische Zeichen sind Fehler.
typedef struct {
    const char *p;          // aktuelle Leseposition
    char fehler[240];       // erster Fehler (leer = kein Fehler)
    int tiefe;              // Schachtelungstiefe beim Aufloesen von Symbolen (abs/equ, die auf andere Symbole verweisen)
} MakroRechner;

static long long rechneOder(MakroRechner *r);
static int makroSymbolWert(const char *name, int tiefe, long long *wert, char *grund, size_t grundGroesse);
static int makroSymbolArt(const char *name, int tiefe, int *erste);
static int makroSymbolZellen(const char *name, int tiefe, long *zellen, char *grund, size_t grundGroesse);
static int makroBlockZellen(const char *von, const char *bis, long *zellen, char *grund, size_t grundGroesse);
static int macroSuche(const char *name);
int pruefeDbOperand(const char *operation, const char *operand, long *wert, char *meldung, size_t groesse);   // ca82_pass1.c (Regeln von Doku 3.3.1)
int adrWert(const char *name, long long *wert, char *grund, size_t gg);   // ca82_main.c: Adresse einer Marke fuer adr(s) und abstand(s,t) (Doku 4.23); 0 = ok, 1 = Fehler mit Grund
int adrNochImLauf(void);   // ca82_main.c: $PROBE (Doku 4.23, ab 1.01-020): 1 im Probelauf und bei --pass0, sonst 0
int adrDebugZeile(const char *zeile);   // ca82_main.c: --probeausgabe (Doku 4.24, ab 1.01-021): Zeile im Probelauf in die Debugdatei legen; 1 = abgelegt

static void rechnerFehler(MakroRechner *r, const char *text) {
    if (r->fehler[0] == '\0') snprintf(r->fehler, sizeof(r->fehler), "%s", text);
}

// Attributabfragen def(s), art(s), zellen(s), zellen(s,t), adr(s) und abstand(s,t) (Doku 4.23): r->p zeigt auf den Funktionsnamen. Das Argument
// ist ein Symbolname, hoechstens von einem Paar Klammern umgeben (ein $1 im Ausdruck wird eingeklammert eingesetzt: def($1) wird def((tab))).
// Fehler stehen im Rechner. adr und abstand (ab c82ass 1.01-018) holen die Adressen aus den Probelaeufen (adrWert, ca82_main.c); bei --pass0
// ist ihr Wert 0, ohne Meldung.
static long long rechneAttribut(MakroRechner *r) {
    int fkt = (strncmp(r->p, "def(", 4) == 0) ? 1 : (strncmp(r->p, "art(", 4) == 0) ? 2 : (strncmp(r->p, "zellen(", 7) == 0) ? 3 : (strncmp(r->p, "adr(", 4) == 0) ? 4 : 5;   // 1 = def, 2 = art, 3 = zellen, 4 = adr, 5 = abstand
    const char *fname = (fkt == 1) ? "def" : (fkt == 2) ? "art" : (fkt == 3) ? "zellen" : (fkt == 4) ? "adr" : "abstand";
    const char *q = r->p + strlen(fname) + 1;                             // hinter der oeffnenden Klammer
    int umklammert = 0;
    if (*q == '(') { umklammert = 1; q++; }
    const char *n0 = q;
    while (isalnum((unsigned char)*q) || *q == '_') q++;
    size_t laenge = (size_t)(q - n0);
    char meldung[200];
    if (laenge == 0) {
        if (*q == ')' || *q == '\0') snprintf(meldung, sizeof(meldung), "%s(): Der Symbolname fehlt", fname);
        else if (umklammert && *q == '(') snprintf(meldung, sizeof(meldung), "%s: Das Argument ist kein einzelner Symbolname (Operator, Komma, Leerraum und weitere Klammern sind nicht erlaubt)", fname);   // def(((s)))
        else snprintf(meldung, sizeof(meldung), "%s(...): Das Argument ist kein Symbolname (erlaubt: Buchstaben, Ziffern und _, nicht mit einer Ziffer beginnend)", fname);
        rechnerFehler(r, meldung);
        return 0;
    }
    if (laenge > MAX_LABEL_LENGTH) {
        snprintf(meldung, sizeof(meldung), "%s: Symbolname zu lang (höchstens %d Zeichen)", fname, MAX_LABEL_LENGTH);
        rechnerFehler(r, meldung);
        return 0;
    }
    char name[MAX_LABEL_LENGTH + 2];
    memcpy(name, n0, laenge);
    name[laenge] = '\0';
    if (isdigit((unsigned char)name[0])) {
        snprintf(meldung, sizeof(meldung), "%s: \"%.40s\" ist kein Symbolname (er darf nicht mit einer Ziffer beginnen)", fname, name);
        rechnerFehler(r, meldung);
        return 0;
    }
    if (*q == '\0') { rechnerFehler(r, "Klammer ) fehlt"); return 0; }
    if (fkt == 3 || fkt == 5) {   // zellen(von,bis): Zellenzahl des Blocks von Marke von bis vor Marke bis (Doku 4.23, ab c82ass 1.01-012); abstand(von,bis) (ab 1.01-018)
        const char *t1 = (umklammert && *q == ')') ? q + 1 : q;           // hinter dem ersten Argument (mit seiner Klammer)
        if (*t1 == ',') {
            const char *q2 = t1 + 1;
            int umkl2 = 0;
            if (*q2 == '(') { umkl2 = 1; q2++; }
            const char *m0 = q2;
            while (isalnum((unsigned char)*q2) || *q2 == '_') q2++;
            size_t laenge2 = (size_t)(q2 - m0);
            if (laenge2 == 0 && isspace((unsigned char)*q2)) {   // ab c82ass 1.01-013: Leerraum hinter dem Komma eigens melden (vorher irrefuehrend "zweiter Name fehlt")
                snprintf(meldung, sizeof(meldung), "%s(von,bis): Hinter dem Komma darf kein Leerraum stehen (%s(a,b), nicht %s(a, b))", fname, fname, fname);
                rechnerFehler(r, meldung);
                return 0;
            }
            if (laenge2 == 0) {
                snprintf(meldung, sizeof(meldung), "%s(von,bis): Der zweite Symbolname fehlt (erlaubt: Buchstaben, Ziffern und _, nicht mit einer Ziffer beginnend)", fname);
                rechnerFehler(r, meldung);
                return 0;
            }
            if (laenge2 > MAX_LABEL_LENGTH) {
                snprintf(meldung, sizeof(meldung), "%s: Symbolname zu lang (höchstens %d Zeichen)", fname, MAX_LABEL_LENGTH);
                rechnerFehler(r, meldung);
                return 0;
            }
            char name2[MAX_LABEL_LENGTH + 2];
            memcpy(name2, m0, laenge2);
            name2[laenge2] = '\0';
            if (isdigit((unsigned char)name2[0])) {
                snprintf(meldung, sizeof(meldung), "%s: \"%.40s\" ist kein Symbolname (er darf nicht mit einer Ziffer beginnen)", fname, name2);
                rechnerFehler(r, meldung);
                return 0;
            }
            if (*q2 == '\0') { rechnerFehler(r, "Klammer ) fehlt"); return 0; }
            if (umkl2) {
                if (*q2 != ')') {
                    snprintf(meldung, sizeof(meldung), "%s: Das Argument ist kein einzelner Symbolname (Operator, Komma, Leerraum und weitere Klammern sind nicht erlaubt)", fname);
                    rechnerFehler(r, meldung);
                    return 0;
                }
                q2++;
            }
            if (*q2 != ')') {
                snprintf(meldung, sizeof(meldung), "%s: Das Argument ist kein einzelner Symbolname (Operator, Komma, Leerraum und weitere Klammern sind nicht erlaubt; %s nimmt höchstens zwei Namen)", fname, fname);
                rechnerFehler(r, meldung);
                return 0;
            }
            if (umklammert && *q != ')') {   // erstes Argument war eingeklammert, aber nicht richtig geschlossen
                snprintf(meldung, sizeof(meldung), "%s: Das Argument ist kein einzelner Symbolname (Operator, Komma, Leerraum und weitere Klammern sind nicht erlaubt)", fname);
                rechnerFehler(r, meldung);
                return 0;
            }
            if (fkt == 5) {   // abstand(von,bis) = adr(bis) - adr(von), mit Vorzeichen (ab c82ass 1.01-018)
                r->p = q2 + 1;
                if (nurPass0Aktiv) return 0;   // --pass0: Adressen stehen in Pass 0 nicht fest, Wert 0 ohne Meldung
                long long av = 0, ab = 0;
                char ga[120];
                if (adrWert(name, &av, ga, sizeof(ga)) != 0 || adrWert(name2, &ab, ga, sizeof(ga)) != 0) {
                    snprintf(meldung, sizeof(meldung), "abstand(%.32s,%.32s): %s", name, name2, ga);
                    rechnerFehler(r, meldung);
                    return 0;
                }
                return ab - av;
            }
            long zb = 0;
            char gb[300];
            if (makroBlockZellen(name, name2, &zb, gb, sizeof(gb)) != 0) { rechnerFehler(r, gb); return 0; }
            r->p = q2 + 1;
            return zb;
        }
        if (fkt == 5 && *t1 == ')') {   // abstand(a) ohne zweiten Namen
            rechnerFehler(r, "abstand(von,bis): Das zweite Argument fehlt (abstand braucht zwei Symbolnamen, durch ein Komma getrennt)");
            return 0;
        }
    }
    if (*q != ')' || (umklammert && q[1] != ')')) {
        snprintf(meldung, sizeof(meldung), "%s: Das Argument ist kein einzelner Symbolname (Operator, Komma, Leerraum und weitere Klammern sind nicht erlaubt)", fname);
        rechnerFehler(r, meldung);
        return 0;
    }
    const char *ende = q + (umklammert ? 2 : 1);                          // hinter der schliessenden Klammer
    if (fkt == 4) {   // adr(s): Adresse der Marke s nach Pass 2 (ab c82ass 1.01-018)
        r->p = ende;
        if (nurPass0Aktiv) return 0;   // --pass0: Adressen stehen in Pass 0 nicht fest, Wert 0 ohne Meldung
        long long av = 0;
        char ga[120];
        if (adrWert(name, &av, ga, sizeof(ga)) != 0) {
            snprintf(meldung, sizeof(meldung), "adr(%.32s): %s", name, ga);
            rechnerFehler(r, meldung);
            return 0;
        }
        return av;
    }
    int erste = -1;
    int art = makroSymbolArt(name, r->tiefe + 1, &erste);
    long long v = 0;
    if (fkt == 1) v = (art != 0);
    else if (fkt == 2) v = art;
    else {
        long zellen = 0;
        char g[200];
        if (makroSymbolZellen(name, r->tiefe + 1, &zellen, g, sizeof(g)) != 0) { rechnerFehler(r, g); return 0; }
        v = zellen;
    }
    r->p = ende;
    return v;
}

static long long rechneAtom(MakroRechner *r) {
    if (r->fehler[0]) return 0;
    char c = *r->p;
    if (strncmp(r->p, "min(", 4) == 0 || strncmp(r->p, "max(", 4) == 0) {   // min(a,b) und max(a,b)
        int istMin = (r->p[1] == 'i');
        r->p += 4;
        long long a = rechneOder(r);
        if (r->fehler[0] == '\0' && *r->p != ',') { rechnerFehler(r, "Komma in min(a,b) bzw. max(a,b) fehlt"); return 0; }
        r->p++;
        long long b = rechneOder(r);
        if (r->fehler[0] == '\0' && *r->p != ')') { rechnerFehler(r, "Klammer ) fehlt"); return 0; }
        r->p++;
        return istMin ? (a < b ? a : b) : (a > b ? a : b);
    }
    if (r->tiefe == 0 && (strncmp(r->p, "def(", 4) == 0 || strncmp(r->p, "art(", 4) == 0 || strncmp(r->p, "zellen(", 7) == 0
                          || strncmp(r->p, "adr(", 4) == 0 || strncmp(r->p, "abstand(", 8) == 0)) {
        return rechneAttribut(r);   // def(s), art(s), zellen(s), adr(s), abstand(s,t) (Doku 4.23); nicht im Operanden eines abs-/equ-Symbols (tiefe > 0)
    }
    if (c == '(') {
        r->p++;
        long long v = rechneOder(r);
        if (*r->p != ')') { rechnerFehler(r, "Klammer ) fehlt"); return 0; }
        r->p++;
        return v;
    }
    if (c == '-') { r->p++; return -rechneAtom(r); }
    if (c == '+') { r->p++; return rechneAtom(r); }
    if (c == '~') { r->p++; return ~rechneAtom(r); }
    if (isdigit((unsigned char)c)) {
        const char *q = r->p;
        while (isalnum((unsigned char)*q)) q++;          // ganzes Wort, damit z. B. 12AB als Fehler erkannt wird
        int laenge = (int)(q - r->p);
        if (r->tiefe == 0 && r->p[0] == '0' && laenge > 1 && (r->p[1] == 'b' || r->p[1] == 'B')) {   // Binaerzahl 0b101 (Doku 4.27); nicht im Operanden eines abs-/equ-Symbols (tiefe > 0)
            long long bv = 0;
            if (laenge == 2) { rechnerFehler(r, "ungültige Binärzahl (nach 0b folgen die Ziffern 0 und 1)"); return 0; }
            for (int k = 2; k < laenge; k++) {
                int d = r->p[k] - '0';
                if (d != 0 && d != 1) { rechnerFehler(r, "ungültige Binärzahl (nach 0b folgen nur die Ziffern 0 und 1)"); return 0; }
                if (bv > (0x7fffffffffffffffLL - d) / 2) { rechnerFehler(r, "Zahl zu groß"); return 0; }
                bv = bv * 2 + d;
            }
            r->p = q;
            return bv;
        }
        if (r->tiefe == 0 && r->p[0] == '0' && laenge > 1 && (r->p[1] == 'x' || r->p[1] == 'X')) {   // Hexadezimalzahl 0x1F (Doku 4.28); nicht im Operanden eines abs-/equ-Symbols (tiefe > 0)
            long long hv = 0;
            if (laenge == 2) { rechnerFehler(r, "ungültige Hexadezimalzahl (nach 0x folgen die Ziffern 0 bis 9 und A bis F)"); return 0; }
            for (int k = 2; k < laenge; k++) {
                int hc = (unsigned char)r->p[k];
                int d = (hc >= '0' && hc <= '9') ? hc - '0' : (hc >= 'a' && hc <= 'f') ? hc - 'a' + 10 : (hc >= 'A' && hc <= 'F') ? hc - 'A' + 10 : -1;
                if (d < 0) { rechnerFehler(r, "ungültige Hexadezimalzahl (nach 0x folgen nur die Ziffern 0 bis 9 und A bis F)"); return 0; }
                if (hv > (0x7fffffffffffffffLL - d) / 16) { rechnerFehler(r, "Zahl zu groß"); return 0; }
                hv = hv * 16 + d;
            }
            r->p = q;
            return hv;
        }
        int oktal = (r->p[0] == '0' && laenge > 1);
        long long v = 0;
        for (int k = 0; k < laenge; k++) {
            int d = r->p[k] - '0';
            if (d < 0 || d > 9) { rechnerFehler(r, "ungültige Zahl"); return 0; }
            if (oktal && d > 7) { rechnerFehler(r, "ungültige Oktalzahl (Oktalzahlen beginnen mit 0 und enthalten nur 0-7)"); return 0; }
            long long basis = oktal ? 8 : 10;
            if (v > (0x7fffffffffffffffLL - d) / basis) { rechnerFehler(r, "Zahl zu groß"); return 0; }
            v = v * basis + d;
        }
        r->p = q;
        return v;
    }
    if (isalpha((unsigned char)c) || c == '_') {   // Symbol mit festem Zahlenwert (abs oder equ <Zahl>, Doku 4.18)
        const char *q = r->p;
        while (isalnum((unsigned char)*q) || *q == '_') q++;
        size_t laenge = (size_t)(q - r->p);
        char name[MAX_LABEL_LENGTH + 2];
        if (laenge > MAX_LABEL_LENGTH) { rechnerFehler(r, "Symbolname zu lang"); return 0; }
        memcpy(name, r->p, laenge);
        name[laenge] = '\0';
        long long v = 0;
        char g[160];
        if (makroSymbolWert(name, r->tiefe + 1, &v, g, sizeof(g)) != 0) { rechnerFehler(r, g); return 0; }
        r->p = q;
        return v;
    }
    if (c == '\0') rechnerFehler(r, "Ausdruck endet unerwartet");
    else           rechnerFehler(r, "unerlaubtes Zeichen (erlaubt: Zahlen, abs- und equ-Symbole mit Zahlenwert, + - * / % << >> < > <= >= == != & ^ | ~, min(a,b), max(a,b), def(s), art(s), zellen(s), adr(s), abstand(s,t) und Klammern)");
    return 0;
}

static long long rechneMal(MakroRechner *r) {
    long long v = rechneAtom(r);
    while (r->fehler[0] == '\0' && (*r->p == '*' || *r->p == '/' || *r->p == '%')) {
        char op = *r->p++;
        long long w = rechneAtom(r);
        if (op == '*') v *= w;
        else if (w == 0) { rechnerFehler(r, "Division durch 0"); return 0; }
        else if (op == '/') v /= w;
        else v %= w;
    }
    return v;
}

static long long rechnePlus(MakroRechner *r) {
    long long v = rechneMal(r);
    while (r->fehler[0] == '\0' && (*r->p == '+' || *r->p == '-')) {
        char op = *r->p++;
        long long w = rechneMal(r);
        v = (op == '+') ? v + w : v - w;
    }
    return v;
}

static long long rechneSchieb(MakroRechner *r) {
    long long v = rechnePlus(r);
    while (r->fehler[0] == '\0' && ((r->p[0] == '<' && r->p[1] == '<') || (r->p[0] == '>' && r->p[1] == '>'))) {
        int links = (r->p[0] == '<');
        r->p += 2;
        long long w = rechnePlus(r);
        if (w < 0 || w > 62) { rechnerFehler(r, "Schiebezahl muss 0 bis 62 sein"); return 0; }
        v = links ? (long long)((unsigned long long)v << w) : (v >> w);
    }
    return v;
}

// Vergleiche < > <= >= (Ergebnis 1 oder 0), dann == und != ; Rangfolge wie in C zwischen Schieben und &
static long long rechneVergl(MakroRechner *r) {
    long long v = rechneSchieb(r);
    while (r->fehler[0] == '\0' && (r->p[0] == '<' || r->p[0] == '>') && r->p[1] != r->p[0]) {
        int klein = (r->p[0] == '<');
        int gleich = (r->p[1] == '=');
        r->p += gleich ? 2 : 1;
        long long w = rechneSchieb(r);
        v = klein ? (gleich ? v <= w : v < w) : (gleich ? v >= w : v > w);
    }
    return v;
}

static long long rechneGleich(MakroRechner *r) {
    long long v = rechneVergl(r);
    while (r->fehler[0] == '\0' && ((r->p[0] == '=' && r->p[1] == '=') || (r->p[0] == '!' && r->p[1] == '='))) {
        int gl = (r->p[0] == '=');
        r->p += 2;
        long long w = rechneVergl(r);
        v = gl ? (v == w) : (v != w);
    }
    return v;
}

static long long rechneUnd(MakroRechner *r) {
    long long v = rechneGleich(r);
    while (r->fehler[0] == '\0' && *r->p == '&') { r->p++; v &= rechneGleich(r); }
    return v;
}

static long long rechneXor(MakroRechner *r) {
    long long v = rechneUnd(r);
    while (r->fehler[0] == '\0' && *r->p == '^') { r->p++; v ^= rechneUnd(r); }
    return v;
}

static long long rechneOder(MakroRechner *r) {
    long long v = rechneXor(r);
    while (r->fehler[0] == '\0' && *r->p == '|') { r->p++; v |= rechneXor(r); }
    return v;
}

// Wertet den Ausdruck aus. Rueckgabe 0 = ok (*wert gesetzt), 1 = Fehler (Grund in grund).
static int makroRechneT(const char *ausdruck, long long *wert, char *grund, size_t grundGroesse, int tiefe) {
    MakroRechner r;
    r.p = ausdruck;
    r.fehler[0] = '\0';
    r.tiefe = tiefe;
    long long v = rechneOder(&r);
    if (r.fehler[0] == '\0' && *r.p != '\0') {
        rechnerFehler(&r, (*r.p == ')') ? "Klammer ) ohne ( davor" : "unerlaubtes Zeichen");
    }
    if (r.fehler[0] != '\0') {
        snprintf(grund, grundGroesse, "%s (bei \"%.40s\")", r.fehler, r.p);
        return 1;
    }
    *wert = v;
    return 0;
}

static int makroRechne(const char *ausdruck, long long *wert, char *grund, size_t grundGroesse) {
    return makroRechneT(ausdruck, wert, grund, grundGroesse, 0);
}

// Zahlenwert eines Symbols fuer Rechenausdruecke im Makro (Doku 4.18). Pass 0 laeuft vor der Symboltabelle; deshalb sucht
// diese Funktion im Quelltext (linesAsm, ohne Makrodefinitionen) nach `<name>: abs <ausdruck>` oder `<name>: equ <ausdruck>`
// und wertet den Operanden mit demselben Rechner aus (Zahlen, weitere solche Symbole, Operatoren). Die Definition darf
// auch hinter dem Makroaufruf stehen. Nicht auswertbar sind `equ *` und Ausdruecke mit Labels (sie haengen von der
// Zellenzahl ab, die Pass 0 noch nicht kennt). Rueckgabe 0 = ok, sonst 1 mit Grund.
// Symbole, die ein Makro (oder eine $-Direktive im Quelltext) erzeugt hat (Doku 4.18, c82ass ab 1.01-011). Pass 0 laeuft vor der Symboltabelle
// und die Suche in linesAsm sieht nur den Quelltext ohne Makrodefinitionen; ein `<name>: abs <ausdruck>` oder `<name>: equ <ausdruck>`, das erst
// beim Aufloesen eines Makros entsteht, steht dort nicht. Deshalb merkt sich makroSymbolMerken jede erzeugte Zeile dieser Art, sobald sie
// entstanden ist (Name und Operand sind dann fertig: $1, $V(...) und $CALC(...) sind ersetzt), sofern sich der Operand als Zahl auswerten laesst.
// makroSymbolWert, makroSymbolArt und makroSymbolZellen fragen die Tabelle nach dem Quelltext. Das Symbol gilt erst ab dem Zeitpunkt, an dem
// seine Zeile entstanden ist (kein Vorgriff wie beim Quelltext); die erste Definition eines Namens gilt.
typedef struct { char name[MAX_LABEL_LENGTH + 2]; long long wert; int istAbs; } MakroErzeugtesSymbol;
static MakroErzeugtesSymbol *msym = NULL;
static int msymAnzahl = 0, msymKapazitaet = 0;

static int makroSymbolSuche(const char *name) {
    for (int k = 0; k < msymAnzahl; k++) if (strcmp(msym[k].name, name) == 0) return k;
    return -1;
}

static void makroSymbolMerken(const lineElements *z) {
    if (z->sp1[0] == '\0' || z->sp1[0] == ';') return;
    int istAbs = (strcmp(z->sp2, "abs") == 0);
    if (!istAbs && strcmp(z->sp2, "equ") != 0) return;
    char name[MAX_LABEL_LENGTH + 4];
    size_t nl = strlen(z->sp1);
    if (nl > 0 && z->sp1[nl - 1] == ':') nl--;
    if (nl == 0 || nl > MAX_LABEL_LENGTH) return;
    memcpy(name, z->sp1, nl);
    name[nl] = '\0';
    if (!isalpha((unsigned char)name[0]) && name[0] != '_') return;   // nur Namen, die $CALC als Symbol liest (kein %, $ usw.)
    for (size_t k = 1; k < nl; k++) if (!isalnum((unsigned char)name[k]) && name[k] != '_') return;
    const char *op = z->sp3;
    if (op[0] == '\0' || strcmp(op, "*") == 0) return;                 // equ * ist eine Adresse, kein Zahlenwert
    if (makroSymbolSuche(name) >= 0) return;
    long long w = 0;
    char g[160];
    if (makroRechneT(op, &w, g, sizeof(g), 1) != 0) return;            // nicht auswertbar (Label, unbekanntes Symbol): bleibt unsichtbar wie im Quelltext
    if (msymAnzahl >= msymKapazitaet) {
        int neuKap = msymKapazitaet == 0 ? 64 : 2 * msymKapazitaet;
        MakroErzeugtesSymbol *tmp = (MakroErzeugtesSymbol *)realloc(msym, (size_t)neuKap * sizeof(*tmp));
        if (!tmp) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
        msym = tmp;
        msymKapazitaet = neuKap;
    }
    strkopiere(msym[msymAnzahl].name, sizeof(msym[msymAnzahl].name), name);
    msym[msymAnzahl].wert = w;
    msym[msymAnzahl].istAbs = istAbs;
    msymAnzahl++;
}

#define MAKRO_SYMBOL_TIEFE_MAX 16
static int makroSymbolWert(const char *name, int tiefe, long long *wert, char *grund, size_t grundGroesse) {
    if (tiefe > MAKRO_SYMBOL_TIEFE_MAX) {
        snprintf(grund, grundGroesse, "Symbol \"%.40s\": Verweis zu tief oder zyklisch (mehr als %d Stufen)", name, MAKRO_SYMBOL_TIEFE_MAX);
        return 1;
    }
    int gefunden = 0;
    char detail[160] = "";
    for (int z = 0; z < lineCountAsm; z++) {
        char marke[256];
        STRKOPIE(marke, linesAsm[z].sp1);
        size_t ml = strlen(marke);
        if (ml > 0 && marke[ml - 1] == ':') marke[ml - 1] = '\0';
        if (strcmp(marke, name) != 0) continue;
        int istAbs = (strcmp(linesAsm[z].sp2, "abs") == 0);
        int istEqu = (strcmp(linesAsm[z].sp2, "equ") == 0);
        if (!istAbs && !istEqu) continue;
        gefunden = 1;
        const char *op = linesAsm[z].sp3;
        char g2[160];
        if (op[0] == '\0' || strcmp(op, "*") == 0) {
            snprintf(detail, sizeof(detail), "%s", op[0] ? "equ * ist eine Adresse, die erst nach Pass 0 feststeht" : "der Operand fehlt");
            continue;
        }
        if (makroRechneT(op, wert, g2, sizeof(g2), tiefe) == 0) return 0;
        if (strncmp(g2, "Symbol \"", 8) == 0) {   // Fehler eines weiteren Symbols in der Kette (auch Zyklus): unveraendert weitergeben
            char *bei = strstr(g2, " (bei \"");
            if (bei != NULL) *bei = '\0';
            snprintf(grund, grundGroesse, "%s", g2);
            return 1;
        }
        if (detail[0] == '\0') snprintf(detail, sizeof(detail), "%.5s %.60s: %.80s", linesAsm[z].sp2, op, g2);
    }
    int ms = makroSymbolSuche(name);   // von einem Makro erzeugt (Doku 4.18)
    if (ms >= 0) { *wert = msym[ms].wert; return 0; }
    if (gefunden) snprintf(grund, grundGroesse, "Symbol \"%.32s\" hat keinen festen Zahlenwert (%.80s)", name, detail);
    else          snprintf(grund, grundGroesse, "Symbol \"%.40s\" ist im Quelltext weder mit abs noch mit equ <Zahl> definiert", name);
    return 1;
}

// Art eines Symbols im Quelltext (Doku 4.23). Durchsucht wie makroSymbolWert linesAsm (Quelltext ohne Makrodefinitionen, auch hinter
// dem Aufruf und hinter end). Rueckgabe: 0 = nicht vorhanden, 1 = abs mit Zahlenwert, 2 = equ mit Zahlenwert, 3 = Adresse oder Wert, der erst
// nach Pass 0 feststeht (equ *, equ mit Labels, equ10, equ40, equ100, spa, abs oder equ ohne auswertbaren Operanden), 4 = Marke einer anderen
// Zeile. Entscheidend ist die erste Definition mit auswertbarem Operanden (wie makroSymbolWert); gibt es keine, die erste Zeile mit der Marke.
// *erste = Index der ersten Zeile mit der Marke (-1: keine). Die Marke einer opsym-Zeile ist kein Symbol (Doku 3.3.17).
static int makroSymbolArt(const char *name, int tiefe, int *erste) {
    int art = 0;
    *erste = -1;
    for (int z = 0; z < lineCountAsm; z++) {
        char marke[256];
        STRKOPIE(marke, linesAsm[z].sp1);
        size_t ml = strlen(marke);
        if (ml > 0 && marke[ml - 1] == ':') marke[ml - 1] = '\0';
        if (strcmp(marke, name) != 0) continue;
        const char *op2 = linesAsm[z].sp2;
        if (strcmp(op2, "opsym") == 0) continue;
        if (*erste < 0) *erste = z;
        int istAbs = (strcmp(op2, "abs") == 0);
        int istEqu = (strcmp(op2, "equ") == 0);
        if (istAbs || istEqu) {
            const char *op = linesAsm[z].sp3;
            long long w = 0;
            char g2[160];
            if (op[0] != '\0' && strcmp(op, "*") != 0 && makroRechneT(op, &w, g2, sizeof(g2), tiefe) == 0) return istAbs ? 1 : 2;
            if (art == 0) art = 3;
            continue;
        }
        if (strcmp(op2, "equ10") == 0 || strcmp(op2, "equ40") == 0 || strcmp(op2, "equ100") == 0 || strcmp(op2, "spa") == 0) {
            if (art == 0) art = 3;
            continue;
        }
        if (art == 0) art = 4;
    }
    if (art != 1 && art != 2) {   // sonst entscheidet ein von einem Makro erzeugtes abs oder equ mit Zahlenwert
        int ms = makroSymbolSuche(name);
        if (ms >= 0) return msym[ms].istAbs ? 1 : 2;
    }
    return art;
}

// Zellenzahl der Anweisung, die das Symbol als Marke traegt (Doku 4.23): db und dbn (Zahl nach 3.3.1, hoechstens 010000), Maschinenbefehl,
// Name mit Punkt, dw, dwb, dwh, dwf, dwg, da und dz eine Zelle. Alles andere ist ein Fehler mit Grund. Rueckgabe 0 = ok (*zellen gesetzt), sonst 1.
static int makroSymbolZellen(const char *name, int tiefe, long *zellen, char *grund, size_t gg) {
    int erste = -1;
    (void)makroSymbolArt(name, tiefe, &erste);
    if (erste < 0) {
        int ms = makroSymbolSuche(name);
        if (ms >= 0) snprintf(grund, gg, "Symbol \"%.32s\": %s definiert einen Wert und belegt keine Zelle", name, msym[ms].istAbs ? "abs" : "equ");
        else         snprintf(grund, gg, "Symbol \"%.32s\": nicht im Quelltext vorhanden", name);
        return 1;
    }
    const char *op = linesAsm[erste].sp2;
    if (op[0] == '\0') { snprintf(grund, gg, "Symbol \"%.32s\": steht allein auf einer Zeile und belegt keine Zelle", name); return 1; }
    if (strcmp(op, "db") == 0 || strcmp(op, "dbn") == 0) {
        long v = 0;
        char m[300];
        if (!pruefeDbOperand(op, linesAsm[erste].sp3, &v, m, sizeof(m))) {
            size_t l = strlen(m);
            if (l > 0 && m[l - 1] == '.') m[l - 1] = '\0';
            snprintf(grund, gg, "Symbol \"%.32s\": %.140s", name, m);
            return 1;
        }
        *zellen = v;
        return 0;
    }
    if (strcmp(op, "dw") == 0 || strcmp(op, "dwb") == 0 || strcmp(op, "dwh") == 0 || strcmp(op, "dwf") == 0 || strcmp(op, "dwg") == 0 || strcmp(op, "da") == 0 || strcmp(op, "dz") == 0 || strcmp(op, "kat5") == 0) { *zellen = 1; return 0; }
    if (strlen(op) == 3 && op[0] >= '0' && op[0] <= '7' && op[1] >= '0' && op[1] <= '7' && op[2] >= '0' && op[2] <= '7') { *zellen = 1; return 0; }
    if (op[0] == '.') { *zellen = 1; return 0; }   // markierter Name fuer einen Operationscode (3.3.17), vor Pass 0 noch nicht ersetzt
    if (strcmp(op, "dt") == 0 || strcmp(op, "dto") == 0 || strcmp(op, "dtm") == 0) {
        snprintf(grund, gg, "Symbol \"%.32s\": %.4s belegt eine Zellenzahl, die vom Zustand KB/GB abhängt", name, op);
        return 1;
    }
    if (strcmp(op, "kat4") == 0 || strcmp(op, "kat6") == 0) {
        snprintf(grund, gg, "Symbol \"%.32s\": %.4s belegt eine Zellenzahl, die vom Text abhängt", name, op);
        return 1;
    }
    if (strcmp(op, "abs") == 0 || strcmp(op, "equ") == 0 || strcmp(op, "equ10") == 0 || strcmp(op, "equ40") == 0 ||
        strcmp(op, "equ100") == 0 || strcmp(op, "spa") == 0) {
        snprintf(grund, gg, "Symbol \"%.32s\": %.6s definiert einen Wert und belegt keine Zelle", name, op);
        return 1;
    }
    if (strcmp(op, "start") == 0 || strcmp(op, "end") == 0 || strcmp(op, "begin") == 0 || strcmp(op, "bend") == 0) {
        snprintf(grund, gg, "Symbol \"%.32s\": %.6s belegt keine Zelle", name, op);
        return 1;
    }
    if (macroSuche(op) >= 0) {
        snprintf(grund, gg, "Symbol \"%.32s\": Marke auf dem Aufruf des Makros %.40s, die Zellenzahl steht erst nach dem Auflösen fest", name, op);
        return 1;
    }
    snprintf(grund, gg, "Symbol \"%.32s\": Operationscode \"%.40s\" ist weder Befehl noch Anweisung", name, op);
    return 1;
}

// Zellenzahl eines Blocks (Doku 4.23, c82ass ab 1.01-012): zellen(von,bis) summiert die Zellen der Quelltextzeilen ab der ersten Zeile mit der
// Marke von bis unmittelbar vor der ersten Zeile mit der Marke bis. Beide Marken muessen im Quelltext (linesAsm, ohne Makrodefinitionen) stehen,
// bis hinter von. Gezaehlt wird nur, was in Pass 0 sicher feststeht: Maschinenbefehl, dw/dwb/dwh/dwf/dwg/da/dz/kat5 und Namen mit Punkt je eine Zelle, db und dbn
// mit ihrer Zahl; Kommentarzeilen, Marke allein, abs und opsym null Zellen. Alles andere (dt, dto, dtm, kat4, kat6, equ-Arten, spa, start, end, begin, bend,
// Makroaufruf, $-Zeile, unbekannter Operationscode) ist ein Fehler mit Zeile und Grund, nie ein falscher Wert. Rueckgabe 0 = ok, sonst 1 mit Grund.
static int makroBlockMarke(const char *name, int *index) {
    *index = -1;
    for (int z = 0; z < lineCountAsm; z++) {
        char marke[256];
        STRKOPIE(marke, linesAsm[z].sp1);
        size_t ml = strlen(marke);
        if (ml > 0 && marke[ml - 1] == ':') marke[ml - 1] = '\0';
        if (strcmp(marke, name) != 0 || strcmp(linesAsm[z].sp2, "opsym") == 0) continue;
        *index = z;
        return 1;
    }
    return 0;
}

static int makroBlockZellen(const char *von, const char *bis, long *zellen, char *grund, size_t gg) {
    int zv = -1, zb = -1;
    const char *fehlt = NULL;
    if (!makroBlockMarke(von, &zv)) fehlt = von;
    else if (!makroBlockMarke(bis, &zb)) fehlt = bis;
    if (fehlt != NULL) {
        if (makroSymbolSuche(fehlt) >= 0) snprintf(grund, gg, "zellen(%.32s,%.32s): Symbol \"%.32s\" hat ein Makro erzeugt und steht nicht im Quelltext (ein Block braucht Marken im Quelltext)", von, bis, fehlt);
        else                              snprintf(grund, gg, "zellen(%.32s,%.32s): Symbol \"%.32s\" ist nicht im Quelltext vorhanden", von, bis, fehlt);
        return 1;
    }
    if (zb <= zv) {
        snprintf(grund, gg, "zellen(%.32s,%.32s): Die Marke \"%.32s\" muss im Quelltext hinter der Marke \"%.32s\" stehen", von, bis, bis, von);
        return 1;
    }
    long summe = 0;
    for (int z = zv; z < zb; z++) {
        const lineElements *l = &linesAsm[z];
        const char *op = l->sp2;
        if (l->sp1[0] == ';' || l->sp1[0] == '#' || l->sp1[0] == '&') continue;   // Kommentarzeile
        if (l->sp1[0] == '$') {
            snprintf(grund, gg, "zellen(%.32s,%.32s): Quelltextzeile %d ist eine $-Zeile, die Zellenzahl steht erst nach ihrer Auswertung fest", von, bis, l->srcLine);
            return 1;
        }
        if (op[0] == '\0' || strcmp(op, "abs") == 0 || strcmp(op, "opsym") == 0) continue;   // Marke allein, abs, opsym: keine Zelle
        long n = -1;
        const char *warum = NULL;
        if (strcmp(op, "db") == 0 || strcmp(op, "dbn") == 0) {
            char m[300];
            if (!pruefeDbOperand(op, l->sp3, &n, m, sizeof(m))) {
                size_t ml = strlen(m);
                if (ml > 0 && m[ml - 1] == '.') m[ml - 1] = '\0';
                snprintf(grund, gg, "zellen(%.32s,%.32s): Quelltextzeile %d: %.140s", von, bis, l->srcLine, m);
                return 1;
            }
        }
        else if (strcmp(op, "dw") == 0 || strcmp(op, "dwb") == 0 || strcmp(op, "dwh") == 0 || strcmp(op, "dwf") == 0 || strcmp(op, "dwg") == 0 || strcmp(op, "da") == 0 || strcmp(op, "dz") == 0 || strcmp(op, "kat5") == 0) n = 1;   // kat5: immer ein Wort (3.3.15, ab 1.03-001)
        else if (strlen(op) == 3 && op[0] >= '0' && op[0] <= '7' && op[1] >= '0' && op[1] <= '7' && op[2] >= '0' && op[2] <= '7') n = 1;
        else if (op[0] == '.') n = 1;   // markierter Name fuer einen Operationscode (3.3.17)
        else if (strcmp(op, "dt") == 0 || strcmp(op, "dto") == 0 || strcmp(op, "dtm") == 0) warum = "belegt eine Zellenzahl, die vom Zustand KB/GB abhängt";
        else if (strcmp(op, "kat4") == 0 || strcmp(op, "kat6") == 0) warum = "belegt eine Zellenzahl, die vom Text abhängt";
        else if (strcmp(op, "equ") == 0 || strcmp(op, "equ10") == 0 || strcmp(op, "equ40") == 0 || strcmp(op, "equ100") == 0 || strcmp(op, "spa") == 0 ||
                 strcmp(op, "start") == 0 || strcmp(op, "end") == 0 || strcmp(op, "begin") == 0 || strcmp(op, "bend") == 0) warum = "setzt oder verschiebt den Befehlszähler, ein Abstand ist so nicht bestimmbar";
        else if (macroSuche(op) >= 0) warum = "ist ein Makroaufruf, die Zellenzahl steht erst nach dem Auflösen fest";
        else warum = "ist weder Befehl noch Anweisung";
        if (warum != NULL) {
            snprintf(grund, gg, "zellen(%.32s,%.32s): Quelltextzeile %d: \"%.40s\" %s", von, bis, l->srcLine, op, warum);
            return 1;
        }
        summe += n;
    }
    *zellen = summe;
    return 0;
}

// $P(ausdruck) und $LEN(ausdruck): Nummer des Aufrufparameters (Doku 4.13, 4.26). k zeigt auf den Kopf ("$P(" bzw. "$LEN("),
// kopf ist sein Name ("$P" bzw. "$LEN", fuer die Meldungen), kopfLaenge seine Laenge mit Klammer (3 bzw. 5), e auf die passende ")".
// Rueckgabe 0 = ok (*pn = Nummer 1 bis paramAnzahl), sonst 1 mit Grund.
static int makroNummerAusdruck(const char *k, const char *e, const char *kopf, size_t kopfLaenge, int paramAnzahl, int *pn, char *grund, size_t gg) {
    char inner[256];
    size_t l = (size_t)(e - (k + kopfLaenge));
    if (l == 0 || l >= sizeof(inner)) { snprintf(grund, gg, "%s( ) braucht einen Ausdruck (höchstens 255 Zeichen)", kopf); return 1; }
    memcpy(inner, k + kopfLaenge, l);
    inner[l] = '\0';
    long long v = 0;
    char g2[200];
    if (makroRechne(inner, &v, g2, sizeof(g2)) != 0) { snprintf(grund, gg, "%s(%.60s): %.120s", kopf, inner, g2); return 1; }
    if (v < 1 || v > paramAnzahl) { snprintf(grund, gg, "%s(%.60s) = %lld: Parameter %lld wird nicht übergeben (übergeben: %d)", kopf, inner, v, v, paramAnzahl); return 1; }
    *pn = (int)v;
    return 0;
}

// $P(ausdruck): Parameter Nummer <ausdruck> des Aufrufs (Doku 4.13). k zeigt auf "$P(", e auf die passende ")".
static int makroPNummer(const char *k, const char *e, int paramAnzahl, int *pn, char *grund, size_t gg) {
    return makroNummerAusdruck(k, e, "$P", 3, paramAnzahl, pn, grund, gg);
}

// Passende schliessende Klammer zu der Klammer vor inhalt suchen; NULL, wenn sie fehlt.
static const char *makroKlammerEnde(const char *inhalt) {
    int tiefe = 1;
    for (const char *e = inhalt; *e != '\0'; e++) {
        if (*e == '(') tiefe++;
        else if (*e == ')' && --tiefe == 0) return e;
    }
    return NULL;
}

// Erste Fundstelle von $PROBE (ohne Klammern, Doku 4.23, ab c82ass 1.01-020): hinter dem Wort darf kein Buchstabe, keine Ziffer
// und kein _ folgen ($PROBE1 oder $PROBEX sind keine Funktion); NULL, wenn s keine enthaelt.
static const char *mvarProbeFund(const char *s) {
    const char *p = s;
    while ((p = strstr(p, "$PROBE")) != NULL) {
        unsigned char c = (unsigned char)p[6];
        if (!(isalnum(c) || c == '_')) return p;
        p += 6;
    }
    return NULL;
}

// Erste Fundstelle einer Funktion, die zur Assemblerzeit durch einen Wert ersetzt wird: $V( (Doku 4.7), $DEFINED( und
// $MDEFINED( (Doku 4.25, ab c82ass 1.01-006) und $PROBE (Doku 4.23, ab c82ass 1.01-020); NULL, wenn s keine enthaelt. Alle
// werden an denselben Stellen und zum selben Zeitpunkt ersetzt (mvarErsetzen).
static const char *mvarFund(const char *s) {
    const char *r = strstr(s, "$V(");
    const char *d = strstr(s, "$DEFINED(");
    const char *m = strstr(s, "$MDEFINED(");
    const char *q = mvarProbeFund(s);
    if (d != NULL && (r == NULL || d < r)) r = d;
    if (m != NULL && (r == NULL || m < r)) r = m;
    if (q != NULL && (r == NULL || q < r)) r = q;
    return r;
}

// Ersetzt jedes $P(ausdruck) in text durch den Aufrufparameter mit dieser Nummer. Fehler gehen nach f.
static void makroPErsetzen(char *text, size_t groesse, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f) {
    char *pos = text;
    while ((pos = strstr(pos, "$P(")) != NULL) {
        const char *e = makroKlammerEnde(pos + 3);
        if (e == NULL) {
            if (f) meldeMakroFehler(f, "%s%s: Klammer ) fehlt", "", "$P", "");
            return;
        }
        int pn = 0;
        char grund[300];
        if (mvarFund(pos + 3) != NULL && mvarFund(pos + 3) < e) { pos = (char *)e + 1; continue; }   // $V, $DEFINED, $MDEFINED erst spaeter
        if (makroPNummer(pos, e, paramAnzahl, &pn, grund, sizeof(grund)) != 0) {
            if (f) meldeMakroFehler(f, "%s%s: %s", "", "$P", grund);
            pos = (char *)e + 1;
            continue;
        }
        char rest[MACRO_PARAMETER_LAENGE * 2];
        snprintf(rest, sizeof(rest), "%s", e + 1);
        size_t vorn = (size_t)(pos - text);
        snprintf(text + vorn, groesse - vorn, "%s%s", paramArray[pn - 1], rest);
        pos = text + vorn + strlen(paramArray[pn - 1]);
    }
}

// Ersetzt jedes $LEN(ausdruck) in text durch die Zeichenzahl des Aufrufparameters mit dieser Nummer (Doku 4.26). Fehler gehen nach f.
static void makroLenErsetzen(char *text, size_t groesse, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f) {
    char *pos = text;
    while ((pos = strstr(pos, "$LEN(")) != NULL) {
        const char *e = makroKlammerEnde(pos + 5);
        if (e == NULL) {
            if (f) meldeMakroFehler(f, "%s%s: Klammer ) fehlt", "", "$LEN", "");
            return;
        }
        int pn = 0;
        char grund[300];
        if (mvarFund(pos + 5) != NULL && mvarFund(pos + 5) < e) { pos = (char *)e + 1; continue; }   // $V, $DEFINED, $MDEFINED erst spaeter
        if (makroNummerAusdruck(pos, e, "$LEN", 5, paramAnzahl, &pn, grund, sizeof(grund)) != 0) {
            if (f) meldeMakroFehler(f, "%s%s: %s", "", "$LEN", grund);
            pos = (char *)e + 1;
            continue;
        }
        char zahl[16];
        snprintf(zahl, sizeof(zahl), "%d", (int)strlen(paramArray[pn - 1]));
        char rest[MACRO_PARAMETER_LAENGE * 2];
        snprintf(rest, sizeof(rest), "%s", e + 1);
        size_t vorn = (size_t)(pos - text);
        snprintf(text + vorn, groesse - vorn, "%s%s", zahl, rest);
        pos = text + vorn + strlen(zahl);
    }
}

// $CALCB(...) und $CALCBn(...) / $CALCBnn(...) (Binaerausgabe, Doku 4.27): 1, wenn q mit einem solchen Kopf beginnt;
// *kopf = Laenge bis hinter die oeffnende Klammer, *breite = 0 (ohne Zahl) oder n = 1 bis 99 (Pruefung 1 bis 64 beim Auswerten)
static int makroCalcZKopf(const char *q, char art, size_t *kopf, int *breite) {
    if (strncmp(q, "$CALC", 5) != 0 || q[5] != art) return 0;
    if (q[6] == '(') { *kopf = 7; *breite = 0; return 1; }
    if (q[6] < '1' || q[6] > '9') return 0;
    if (q[7] == '(') { *kopf = 8; *breite = q[6] - '0'; return 1; }
    if (q[7] >= '0' && q[7] <= '9' && q[8] == '(') { *kopf = 9; *breite = (q[6] - '0') * 10 + (q[7] - '0'); return 1; }
    return 0;
}
static int makroCalcbKopf(const char *q, size_t *kopf, int *breite) { return makroCalcZKopf(q, 'B', kopf, breite); }   // $CALCB..., Doku 4.27
static int makroCalchKopf(const char *q, size_t *kopf, int *breite) { return makroCalcZKopf(q, 'H', kopf, breite); }   // $CALCH..., Doku 4.28

// Ersetzt in text (Kapazitaet groesse) jedes $CALC(...), $CALCO(...), $CALCB(...) und $CALCH(...) durch das Ergebnis. In den Ausdruecken werden vorher
// $1..$9 durch den in Klammern gesetzten Aufrufparameter ersetzt ($1*2 mit Parameter 3+4 ergibt (3+4)*2).
// Fehler werden in f gemeldet; der Text bleibt dann an dieser Stelle unveraendert.
static void makroCalcErsetzen(char *text, size_t groesse, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f) {
    if (strstr(text, "$CALC") == NULL) return;
    char *aus = malloc(groesse + 1);
    if (!aus) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    size_t n = 0;
    const char *q = text;
    aus[0] = '\0';
    while (*q != '\0') {
        int oktal = 0;
        size_t kopf = 0;
        int breite = 0;   // $CALCOn(...): oktal mit fuehrender 0 und genau n Ziffern (n = 1 bis 9); $CALCBn(...): binaer mit genau n Ziffern
        int binaer = 0;   // $CALCB(...) und $CALCBn(...): Binaerziffern ohne Praefix (Doku 4.27)
        int hexa = 0;     // $CALCH(...) und $CALCHn(...): Hexadezimalziffern 0-9 A-F ohne Praefix (Doku 4.28)
        if (makroCalcbKopf(q, &kopf, &breite)) { binaer = 1; }
        else if (makroCalchKopf(q, &kopf, &breite)) { hexa = 1; }
        else if (strncmp(q, "$CALCO", 6) == 0 && q[6] >= '1' && q[6] <= '9' && q[7] == '(') { oktal = 1; kopf = 8; breite = q[6] - '0'; }
        else if (strncmp(q, "$CALCO(", 7) == 0) { oktal = 1; kopf = 7; }
        else if (strncmp(q, "$CALC(", 6) == 0) { kopf = 6; }
        if (kopf == 0) {
            if (n + 1 < groesse) { aus[n++] = *q; aus[n] = '\0'; }
            q++;
            continue;
        }
        // passende schliessende Klammer suchen
        const char *inhalt = q + kopf;
        int tiefe = 1;
        const char *e = inhalt;
        while (*e != '\0' && tiefe > 0) {
            if (*e == '(') tiefe++;
            else if (*e == ')') tiefe--;
            if (tiefe > 0) e++;
        }
        if (tiefe != 0) {
            if (f) meldeMakroFehler(f, "%s%s: Klammer ) fehlt", "", oktal ? "$CALCO" : binaer ? "$CALCB" : hexa ? "$CALCH" : "$CALC", "");
            if (n + 1 < groesse) { aus[n++] = *q; aus[n] = '\0'; }
            q++;
            continue;
        }
        {   // Ausdruck mit Makro-Variable $V(name) (auch $DEFINED/$MDEFINED, Doku 4.25): wird erst nach der Auswertung von $SET/$INC berechnet (Doku 4.7)
            const char *vv = mvarFund(inhalt);
            if (vv != NULL && vv < e) {
                for (const char *k = q; k <= e && n + 1 < groesse; k++) { aus[n++] = *k; aus[n] = '\0'; }
                q = e + 1;
                continue;
            }
        }
        // Ausdruck kopieren und $1..$9 in Klammern einsetzen
        char ausdruck[512];
        size_t m = 0;
        ausdruck[0] = '\0';
        int paramFehler = 0;
        char pGrund[300] = "";
        for (const char *k = inhalt; k < e && m + 2 < sizeof(ausdruck); k++) {
            if (*k == '$' && k + 4 < e && strncmp(k, "$LEN", 4) == 0 && *(k + 4) >= '1' && *(k + 4) <= '9') {   // $LENn = Zeichenzahl von Parameter n
                int pn = *(k + 4) - '0';
                if (pn > paramAnzahl) { paramFehler = pn; break; }
                m += snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "%d", (int)strlen(paramArray[pn - 1]));
                k += 4;
            } else if (*k == '$' && k + 4 < e && strncmp(k, "$LEN(", 5) == 0) {   // $LEN(i) = Zeichenzahl von Parameter Nummer i (Doku 4.26)
                const char *pe = makroKlammerEnde(k + 5);
                int pn = 0;
                if (pe == NULL || pe > e || makroNummerAusdruck(k, pe, "$LEN", 5, paramAnzahl, &pn, pGrund, sizeof(pGrund)) != 0) {
                    if (pe == NULL || pe > e) snprintf(pGrund, sizeof(pGrund), "$LEN( ): Klammer ) fehlt");
                    paramFehler = -2;
                    break;
                }
                m += snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "%d", (int)strlen(paramArray[pn - 1]));
                k = pe;
            } else if (*k == '$' && k + 2 < e && *(k + 1) == 'P' && *(k + 2) == '(') {   // $P(i) = Parameter Nummer i
                const char *pe = makroKlammerEnde(k + 3);
                int pn = 0;
                if (pe == NULL || pe > e || makroPNummer(k, pe, paramAnzahl, &pn, pGrund, sizeof(pGrund)) != 0) {
                    if (pe == NULL || pe > e) snprintf(pGrund, sizeof(pGrund), "$P( ): Klammer ) fehlt");
                    paramFehler = -2;
                    break;
                }
                m += snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "(%s)", paramArray[pn - 1]);
                k = pe;
            } else if (*k == '$' && k + 1 < e && *(k + 1) >= '1' && *(k + 1) <= '9') {
                int pn = *(k + 1) - '0';
                if (pn > paramAnzahl) { paramFehler = pn; break; }
                m += snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "(%s)", paramArray[pn - 1]);
                k++;
            } else {
                ausdruck[m++] = *k;
                ausdruck[m] = '\0';
            }
        }
        if (m + 2 >= sizeof(ausdruck)) paramFehler = -1;
        char ergebnis[72];
        char grund[256];
        long long wert = 0;
        int rc = 0;
        if (paramFehler > 0) {
            snprintf(grund, sizeof(grund), "Parameter $%d wird nicht übergeben", paramFehler);
            rc = 1;
        } else if (paramFehler == -2) {
            snprintf(grund, sizeof(grund), "%.*s", (int)sizeof(grund) - 1, pGrund);   // pGrund hat 300 Byte, grund 256: gekuerzt, ohne Warnung
            rc = 1;
        } else if (paramFehler < 0) {
            snprintf(grund, sizeof(grund), "Ausdruck zu lang");
            rc = 1;
        } else {
            rc = makroRechne(ausdruck, &wert, grund, sizeof(grund));
            if (rc == 0 && oktal && wert < 0) {
                snprintf(grund, sizeof(grund), "negatives Ergebnis %lld ist oktal nicht darstellbar", wert);
                rc = 1;
            }
            if (rc == 0 && binaer && wert < 0) {
                snprintf(grund, sizeof(grund), "negatives Ergebnis %lld ist binär nicht darstellbar", wert);
                rc = 1;
            }
            if (rc == 0 && hexa && wert < 0) {
                snprintf(grund, sizeof(grund), "negatives Ergebnis %lld ist hexadezimal nicht darstellbar", wert);
                rc = 1;
            }
            if (rc == 0 && hexa && breite > 16) {
                snprintf(grund, sizeof(grund), "Breite %d liegt außerhalb von 1 bis 16", breite);
                rc = 1;
            }
            if (rc == 0 && hexa && breite > 0) {
                char tmp[32];
                snprintf(tmp, sizeof(tmp), "%llX", (unsigned long long)wert);
                if ((int)strlen(tmp) > breite) {
                    snprintf(grund, sizeof(grund), "Ergebnis %lld braucht mehr als %d Hexadezimalziffern", wert, breite);
                    rc = 1;
                }
            }
            if (rc == 0 && binaer && breite > 64) {
                snprintf(grund, sizeof(grund), "Breite %d liegt außerhalb von 1 bis 64", breite);
                rc = 1;
            }
            if (rc == 0 && binaer && breite > 0) {
                int stellen = 1;
                for (unsigned long long t = (unsigned long long)wert >> 1; t != 0; t >>= 1) stellen++;
                if (stellen > breite) {
                    snprintf(grund, sizeof(grund), "Ergebnis %lld braucht mehr als %d Binärziffern", wert, breite);
                    rc = 1;
                }
            }
            if (rc == 0 && !binaer && !hexa && breite > 0) {
                char tmp[32];
                snprintf(tmp, sizeof(tmp), "%llo", (unsigned long long)wert);
                if ((int)strlen(tmp) > breite) {
                    snprintf(grund, sizeof(grund), "Ergebnis %lld braucht mehr als %d Oktalziffern", wert, breite);
                    rc = 1;
                }
            }
        }
        if (rc != 0) {
            char kurz[300];
            snprintfGekuerzt(kurz, sizeof(kurz), "%.*s", (int)(e - q + 1 > 80 ? 80 : e - q + 1), q);
            if (f) meldeMakroFehler(f, "%s%s: %s", "", kurz, grund);
            if (n + 1 < groesse) { aus[n++] = *q; aus[n] = '\0'; }
            q++;
            continue;
        }
        if (binaer) {   // Binaerziffern, ohne Praefix; mit n genau n Stellen, sonst ohne fuehrende Nullen (0 ergibt 0)
            int stellen = 1;
            for (unsigned long long t = (unsigned long long)wert >> 1; t != 0; t >>= 1) stellen++;
            int ziel = (breite > stellen) ? breite : stellen;
            int i = 0;
            for (; i < ziel - stellen; i++) ergebnis[i] = '0';
            for (int b = stellen - 1; b >= 0; b--) ergebnis[i++] = (char)('0' + (int)(((unsigned long long)wert >> b) & 1ULL));
            ergebnis[i] = '\0';
        } else if (hexa) {   // Hexadezimalziffern, Grossbuchstaben, ohne Praefix; mit n genau n Stellen, sonst ohne fuehrende Nullen (0 ergibt 0)
            snprintfGekuerzt(ergebnis, sizeof(ergebnis), "%0*llX", breite, (unsigned long long)wert);
        } else if (oktal && breite > 0) {
            snprintfGekuerzt(ergebnis, sizeof(ergebnis), "0%0*llo", breite, (unsigned long long)wert);
        } else if (oktal) {
            if (wert == 0) snprintf(ergebnis, sizeof(ergebnis), "0");
            else           snprintf(ergebnis, sizeof(ergebnis), "0%llo", (unsigned long long)wert);
        } else {
            snprintf(ergebnis, sizeof(ergebnis), "%lld", wert);
        }
        size_t l = strlen(ergebnis);
        if (n + l < groesse) { memcpy(aus + n, ergebnis, l); n += l; aus[n] = '\0'; }
        q = e + 1;
    }
    snprintf(text, groesse, "%s", aus);
    free(aus);
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

    size_t calcbKopf = 0;
    int calcbBreite = 0;
    if (strncmp(word, "$CALC(", 6) == 0 || strncmp(word, "$CALCO(", 7) == 0 ||
        (strncmp(word, "$CALCO", 6) == 0 && word[6] >= '1' && word[6] <= '9' && word[7] == '(') ||
        makroCalcbKopf(word, &calcbKopf, &calcbBreite) || makroCalchKopf(word, &calcbKopf, &calcbBreite)) {
        return 1;   // Rechenausdruck $CALC(...) / $CALCO(...) / $CALCB(...) / $CALCH(...) (Doku 4.2, 4.27, 4.28)
    }
    if (strncmp(word, "$P(", 3) == 0 || strncmp(word, "$LEN(", 5) == 0) {
        return 1;   // $P(ausdruck) / $LEN(ausdruck): Parameter Nummer i, Zeichenzahl von Parameter i (Doku 4.26)
    }
    {
        int prLaenge = 0;
        if (makroPrNummer(word, &prLaenge) >= 1 && word[prLaenge] == '\0') return 1;   // $PR1 bis $PR32 als ganzes Wort (Doku 4.26)
    }

    char tempWord[256];
    kopiereBegrenzt(tempWord, sizeof(tempWord), word);   // Null-Terminierung ist enthalten
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

// Zerlegt die Parameterzeile des Makroaufrufs in Woerter (maximal 64); liefert die Anzahl.
// Ein Wort in "..." oder '...' (Anfuehrungszeichen am Wortanfang, schliessendes gleiches Zeichen vor Leerraum oder
// Zeilenende) bildet EINEN Parameter und darf Leerzeichen enthalten (Zeichenketten-Parameter, Doku 4.10); die
// Anfuehrungszeichen werden entfernt. Ohne schliessendes Zeichen gilt das Wort wie bisher bis zum naechsten Leerraum.
static int makroParameterZerlegen(char *aktuelleParameterZeile, char paramArray[64][MACRO_PARAMETER_LAENGE]) {
    char kopie[MACRO_PARAMETER_LAENGE];

    trimWhitespace(aktuelleParameterZeile);
    strncpy(kopie, aktuelleParameterZeile, MACRO_PARAMETER_LAENGE - 1);
    kopie[MACRO_PARAMETER_LAENGE - 1] = '\0';

    int anzahl = 0;
    char *p = kopie;
    while (anzahl < 64) {
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0') break;
        char *wort = p;
        if (*p == '"' || *p == '\'') {
            char *e = strchr(p + 1, *p);
            if (e != NULL && (e[1] == '\0' || e[1] == ' ' || e[1] == '\t')) {   // Zeichenkette, evtl. mit Leerzeichen
                *e = '\0';
                wort = p + 1;
                p = (e[1] == '\0') ? e + 1 : e + 2;
                snprintf(paramArray[anzahl], MACRO_PARAMETER_LAENGE, "%s", wort);
                anzahl++;
                continue;
            }
        }
        while (*p != '\0' && *p != ' ' && *p != '\t') p++;
        if (*p != '\0') *p++ = '\0';
        trimQuotes(wort);  // Entfernt "" oder ''
        snprintf(paramArray[anzahl], MACRO_PARAMETER_LAENGE, "%s", wort);
        anzahl++;
    }
    return anzahl;
}

// Schluesselwortparameter (Doku 4.30, ab c82ass 1.01-025): makroKwLeer[k] = 1, wenn der Schluesselwortparameter Nummer k beim Aufruf
// nicht angegeben war und eine leere Vorgabe hat; $PRk prueft diesen Wert nicht (gesetzt in loeseMacroAuf unmittelbar vor pruefeMakroDefinition).
static char makroKwLeer[100];

// Pruefung einer $PRx-Zeile der Makrodefinition: Typangabe ($TYPADR, $TYPKON, $TYPABS) oder Wertliste
// gegen den beim Aufruf uebergebenen Parameter
static void pruefePrZeile(const macroDefinitionen *m, const char *SP1, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f) {
    if (strlen(SP1) == 0) {
        return;
    }
    int prNummer = makroPrNummer(SP1, NULL);   // $PR1 bis $PR32 (Doku 4.26); $PR0 und $PR05 gelten nicht
    if (prNummer < 1) {
        return;
    }

    // Ein $PR? wurde gefunden: das naechste Wort in SP1 pruefen
    char pruefliste[256];
    kopiereBegrenzt(pruefliste, sizeof(pruefliste), SP1);

    entferneErstesWort(pruefliste);
    char rest[256] = "";
    STRKOPIE(rest, pruefliste);

    char *nextWord = strtok(rest, " \t");
    if (nextWord == NULL) {
        return;
    }

    if (strcmp(nextWord, "$TYPZAHL") == 0) {
        // $PRx $TYPZAHL <min> <max>: ganzzahliger Ausdruck (wie $CALC, ohne Leerzeichen) im Bereich min bis max
        char *wMin = strtok(NULL, " \t");
        char *wMax = strtok(NULL, " \t");
        char *wRest = strtok(NULL, " \t");
        long long vMin = 0, vMax = 0;
        char grund[256];
        if (wMin == NULL || wMax == NULL || (wRest != NULL && wRest[0] != ';')) {
            meldeMakroFehler(f, "$TYPZAHL erwartet genau zwei Grenzen (min max): %s%s%s", SP1, "", "");
        } else if (makroRechne(wMin, &vMin, grund, sizeof(grund)) != 0 || makroRechne(wMax, &vMax, grund, sizeof(grund)) != 0) {
            meldeMakroFehler(f, "$TYPZAHL: Grenze ungültig: %s%s%s", grund, "", "");
        } else if (vMin > vMax) {
            meldeMakroFehler(f, "$TYPZAHL: untere Grenze %s ist größer als die obere %s%s", wMin, wMax, "");
        } else {
            int parameterNummer = prNummer;
            if (parameterNummer >= 1 && parameterNummer <= paramAnzahl && !makroKwLeer[parameterNummer]) {
                const char *arg = paramArray[parameterNummer - 1];
                long long wert = 0;
                char paramBez[64];
                makroParamBez(m, parameterNummer, paramBez, sizeof(paramBez));
                if (makroRechne(arg, &wert, grund, sizeof(grund)) != 0) {
                    char meldung[400];
                    snprintf(meldung, sizeof(meldung), "Wert \"%.100s\" ist kein Zahlenausdruck: %s", arg, grund);
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, meldung, "");
                } else if (wert < vMin || wert > vMax) {
                    char meldung[400];
                    snprintf(meldung, sizeof(meldung), "Wert \"%.100s\" (= %lld) liegt nicht im Bereich %lld bis %lld", arg, wert, vMin, vMax);
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, meldung, "");
                }
            }
        }
        return;
    }

    if (strcmp(nextWord, "$TYPTEXT") == 0) {
        // $PRx $TYPTEXT [maxlaenge]: Zeichenkette, nicht leer, hoechstens maxlaenge Zeichen (Vorgabe 200), ohne Steuerzeichen
        char *wMax = strtok(NULL, " \t");
        char *wRest = (wMax != NULL && wMax[0] != ';') ? strtok(NULL, " \t") : NULL;
        long maxl = 200;
        int ok = 1;
        if (wMax != NULL && wMax[0] != ';') {
            char *endp = NULL;
            maxl = strtol(wMax, &endp, 10);
            if (*endp != '\0' || maxl < 1 || maxl > 200 || (wRest != NULL && wRest[0] != ';')) ok = 0;
        }
        if (!ok) {
            meldeMakroFehler(f, "$TYPTEXT erwartet höchstens eine Längenangabe (1 bis 200): %s%s%s", SP1, "", "");
        } else {
            int parameterNummer = prNummer;
            if (parameterNummer >= 1 && parameterNummer <= paramAnzahl && !makroKwLeer[parameterNummer]) {
                const char *arg = paramArray[parameterNummer - 1];
                char paramBez[64];
                makroParamBez(m, parameterNummer, paramBez, sizeof(paramBez));
                int steuer = 0;
                for (const char *q = arg; *q; q++) if ((unsigned char)*q < 32) steuer = 1;
                if (arg[0] == '\0') {
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, "Text ist leer", "");
                } else if (steuer) {
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, "Text enthält Steuerzeichen", "");
                } else if ((long)strlen(arg) > maxl) {
                    char meldung[300];
                    snprintf(meldung, sizeof(meldung), "Text hat %d Zeichen, erlaubt sind höchstens %ld", (int)strlen(arg), maxl);
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, meldung, "");
                }
            }
        }
        return;
    }

    int foundType = 0;
    for (int t = 0; t < (int)(sizeof(validType) / sizeof(validType[0])); t++) {
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
            int parameterNummer = prNummer;
            if (parameterNummer >= 1 && parameterNummer <= paramAnzahl && !makroKwLeer[parameterNummer]) {
                char typMeldung[256];
                if (pruefeMakroTyp(nextWord, paramArray[parameterNummer - 1], typMeldung, sizeof(typMeldung)) != 0) {
                    char paramBez[64];
                    makroParamBez(m, parameterNummer, paramBez, sizeof(paramBez));
                    meldeMakroFehler(f, "Parameter %s: %s", paramBez, typMeldung, "");
                }
            }
        }
    } else if (prNummer >= 1 && nextWord[0] != '$') {   // $...-Eintrag (z. B. $ADRESSE) = Typangabe, keine Wertliste
        // Wertliste (Doku 4): Der beim Aufruf uebergebene Parameter $x darf nur
        // einen der in der Liste $PRx genannten Werte annehmen.
        int parameterNummer = prNummer;
        if (parameterNummer >= 1 && parameterNummer <= paramAnzahl && !makroKwLeer[parameterNummer]) {
            char listeKopie[256];
            kopiereBegrenzt(listeKopie, sizeof(listeKopie), pruefliste);
            char *kommentar_p = strchr(listeKopie, ';');   // ; leitet einen Kommentar ein
            if (kommentar_p) *kommentar_p = '\0';
            int inListe = 0;
            char *lsave;
            for (char *w = strtok_r(listeKopie, " \t", &lsave); w != NULL; w = strtok_r(NULL, " \t", &lsave)) {
                if (strcmp(w, paramArray[parameterNummer - 1]) == 0) { inListe = 1; break; }
            }
            if (!inListe) {
                char paramBez[64];
                makroParamBez(m, parameterNummer, paramBez, sizeof(paramBez));
                meldeMakroFehler(f, "Parameter %s: Wert \"%s\" steht nicht in der Pruefliste", paramBez, paramArray[parameterNummer - 1], "");
            }
        }
    }
}

// Pruefung einer Zeile der Makrodefinition: Schluesselwoerter und $PRx
static void pruefeMakroZeile(const macroDefinitionen *m, int jj, char paramArray[64][MACRO_PARAMETER_LAENGE],
                             int paramAnzahl, MakroFehler *f) {
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
    int prNr = makroPrNummer(z.sp1, NULL);   // $PR1 bis $PR32 (Doku 4.26)
    if (prNr >= 1) {
        int parameterNummer = prNr;

        // Überprüfen, ob die Ziffer innerhalb der erlaubten Anzahl liegt
        if (parameterNummer > m->macroParameterAnzahl) {
            char maxParamStr[16];  // Puffer für die Zeichenkette
            snprintf(maxParamStr, sizeof(maxParamStr), "%d", m->macroParameterAnzahl);
            meldeMakroFehler(f, "Ungültiger Parameter: %s (Max. erlaubt: $PR%s)%s", z.sp1, maxParamStr, "");
        }
    }

    pruefePrZeile(m, z.sp1, paramArray, paramAnzahl, f);
}

// Prueft die ganze Makrodefinition (alle Zeilen) und sammelt die Fehler in f
static void pruefeMakroDefinition(const macroDefinitionen *m, char paramArray[64][MACRO_PARAMETER_LAENGE],
                                  int paramAnzahl, MakroFehler *f) {
    // Die Klammerung von $IF/$ELIF/$ELSE/$ENDIF und $REPT/$ENDREPT prueft die Auswertung beim Aufruf
    for (int jj = 0; jj < m->macroLineCount; jj++) {
        pruefeMakroZeile(m, jj, paramArray, paramAnzahl, f);
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
                PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s [Makro %.60s ruft sich selbst auf, im Quelltext Zeile %s]",
                             makroName, defName, qOrt(rufZeile));
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

// Ersetzt in einem Feld (Puffer feldGroesse) $CALC(...), $P(i), $LEN(i), $LENn und $1 bis $9 durch die Aufrufparameter. Das ist der Ablauf
// je Feld einer Zeile; die Zeichenkettenfunktionen (Doku 4.21) wenden ihn auf jedes Argument an. Rueckgabe 1, wenn das Ergebnis
// auf feldGroesse - 1 Zeichen gekuerzt werden musste.
static int makroFeldParameterErsetzen(char *feld, size_t feldGroesse, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *mf) {
    size_t originalLen = strlen(feld);
    char *newField = malloc(originalLen + 512); // Speicher für ursprüngliche Länge
    if (!newField) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    strkopiere(newField, originalLen + 512, feld);
    makroCalcErsetzen(newField, originalLen + 512, paramArray, paramAnzahl, (mf != NULL && mf->anzahl == 0) ? mf : NULL);   // $CALC(...) / $CALCO(...) zuerst
    makroPErsetzen(newField, originalLen + 512, paramArray, paramAnzahl, (mf != NULL && mf->anzahl == 0) ? mf : NULL);   // $P(i): Parameter Nummer i
    makroLenErsetzen(newField, originalLen + 512, paramArray, paramAnzahl, (mf != NULL && mf->anzahl == 0) ? mf : NULL);   // $LEN(i): Zeichenzahl von Parameter i

    for (int p = 0; p < paramAnzahl; p++) { // `$LENn` (Zeichenzahl von Parameter n) vor `$n`
        char lsearch[16], lzahl[16];
        snprintf(lsearch, sizeof(lsearch), "$LEN%d", p + 1);
        snprintf(lzahl, sizeof(lzahl), "%d", (int)strlen(paramArray[p]));
        char *lpos;
        while ((lpos = strstr(newField, lsearch)) != NULL) {
            size_t restLen = strlen(lpos + strlen(lsearch));
            memmove(lpos + strlen(lzahl), lpos + strlen(lsearch), restLen + 1);
            memcpy(lpos, lzahl, strlen(lzahl));
        }
    }
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
    int gekuerzt = (strlen(newField) >= feldGroesse);
    strncpy(feld, newField, feldGroesse - 1);
    feld[feldGroesse - 1] = '\0';
    free(newField); // Speicher nach der Bearbeitung freigeben
    return gekuerzt;
}

// Ersetzt $1 ... $n in allen Zeilen durch die beim Aufruf uebergebenen Parameter
static void makroParameterErsetzen(lineElements *result, int lineCount, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *mf) {
    for (int j = 0; j < lineCount; j++) {

        if (result[j].sp1[0] == '#' ||
            (result[j].sp1[0] == '$' && result[j].sp2[0] == '\0' && strncmp(result[j].sp1, "$IF", 3) != 0 &&   // sp2 gefuellt: Marke aus Parameter ("$1: abs 5"), schon zerlegt (1.01-031)
                                    strncmp(result[j].sp1, "$ELIF", 5) != 0 &&
                                    strncmp(result[j].sp1, "$ENDIF", 6) != 0 &&
                                    strncmp(result[j].sp1, "$ERROR", 6) != 0 &&
                                    strncmp(result[j].sp1, "$WARN", 5) != 0 &&
                                    strncmp(result[j].sp1, "$SET", 4) != 0 &&
                                    strncmp(result[j].sp1, "$INC", 4) != 0 &&
                                    strncmp(result[j].sp1, "$DIM", 4) != 0 &&
                                    strncmp(result[j].sp1, "$LOCAL", 6) != 0 &&
                                    strncmp(result[j].sp1, "$GLOBAL", 7) != 0 &&
                                    strncmp(result[j].sp1, "$WHILE", 6) != 0 &&
                                    strncmp(result[j].sp1, "$NOTE", 5) != 0 &&
                                    strncmp(result[j].sp1, "$DUMP", 5) != 0) ||
            result[j].sp1[0] == '&' ||
            (strlen(result[j].sp1) == 0 && strlen(result[j].sp2) == 0 &&
            strlen(result[j].sp3) == 0 && strlen(result[j].sp4) == 0))
        {
            continue;
        }

        char *fields[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };

        for (int f = 0; f < 4; f++) makroFeldParameterErsetzen(fields[f], MACRO_PARAMETER_LAENGE, paramArray, paramAnzahl, mf);   // sp1 - sp4
    }
}

static void makroZeileKopieren(lineElements *ziel, const lineElements *quelle) {
    STRKOPIE(ziel->sp1, quelle->sp1);
    STRKOPIE(ziel->sp2, quelle->sp2);
    STRKOPIE(ziel->sp3, quelle->sp3);
    STRKOPIE(ziel->sp4, quelle->sp4);
    ziel->srcLine = quelle->srcLine;
}

// ----------------------------------------------------------------------------------
// Schluesselwortzeilen der Makrodefinition: $REPT/$ENDREPT (Wiederholung), $IF/$ELIF/$ELSE/$ENDIF (Bedingung).
// Solche Zeilen beginnen mit '$'; die ganze Zeile steht in sp1 (processLine).

// 1, wenn das erste Wort in sp1 genau `wort` ist ("$IF" trifft "$IF a = b" und "$IF;..." , nicht "$IFX")
static int makroErstesWort(const lineElements *z, const char *wort) {
    const char *p = z->sp1;
    while (*p == ' ' || *p == '\t') p++;
    size_t n = strlen(wort);
    if (strncmp(p, wort, n) != 0) return 0;
    char c = p[n];
    return c == '\0' || c == ' ' || c == '\t' || c == ';';
}

// Zeiger hinter das erste Wort von sp1
static const char *makroRestNachWort(const lineElements *z) {
    const char *p = z->sp1;
    while (*p == ' ' || *p == '\t') p++;
    while (*p != '\0' && *p != ' ' && *p != '\t' && *p != ';') p++;
    return p;
}

// Meldet einen Fehler mit Makroname als Vorsatz (wie bei $IF) und frei formuliertem Text
static void makroMelde(MakroFehler *f, const char *makroName, const char *format, ...) {
    char msg[400];
    va_list ap;
    va_start(ap, format);
    vsnprintf(msg, sizeof(msg), format, ap);
    va_end(ap);
    meldeMakroFehler(f, "%.0s%s", makroName, msg, "");
}

// ----------------------------------------------------------------------------------
// $REPT <anzahl> ... $ENDREPT: der Rumpf wird <anzahl>-mal uebernommen; $Z1 (aeusserste Schleife) bis $Z4 stehen im
// Rumpf fuer die Nummer des Durchlaufs (0, 1, 2 ...). Die Wiederholung geschieht vor der Ersetzung der Aufrufparameter
// und vor der Auswertung von $IF; Schleifen duerfen bis zur Tiefe REPT_MAX_TIEFE geschachtelt sein.
#define REPT_MAX_TIEFE  4
#define REPT_MAX_ANZAHL 4096
#define REPT_MAX_ZEILEN 4096

typedef struct {
    lineElements *z;
    int n;
    int kap;
} ZeilenListe;

static void zlAnhaengen(ZeilenListe *l, const lineElements *e) {
    if (l->n >= l->kap) {
        int nk = l->kap ? 2 * l->kap : 64;
        lineElements *t = (lineElements *)realloc(l->z, (size_t)nk * sizeof(lineElements));
        if (!t) { fprintf(stderr, "Speicherfehler bei Realloc!\n"); exit(RC_FEHLER); }
        l->z = t;
        l->kap = nk;
    }
    l->z[l->n++] = *e;
}

// Ersetzt $Z<tiefe> in allen vier Feldern durch den Zaehlerwert; Rueckgabe 1, wenn ein Feld dadurch zu lang wurde
static int reptZaehlerErsetzen(lineElements *z, int tiefe, long long wert) {
    char such[32], num[32];
    snprintf(such, sizeof(such), "$Z%d", tiefe);
    snprintf(num, sizeof(num), "%lld", wert);
    char *felder[4] = { z->sp1, z->sp2, z->sp3, z->sp4 };
    int zuLang = 0;
    for (int f = 0; f < 4; f++) {
        if (strstr(felder[f], such) == NULL) continue;
        char neu[4 * MACRO_PARAMETER_LAENGE];
        size_t n = 0;
        for (const char *q = felder[f]; *q != '\0' && n + 40 < sizeof(neu); ) {
            if (strncmp(q, such, 3) == 0) {
                n += (size_t)snprintf(neu + n, sizeof(neu) - n, "%s", num);
                q += 3;
            } else {
                neu[n++] = *q++;
            }
        }
        neu[n] = '\0';
        if (n >= MACRO_PARAMETER_LAENGE) zuLang = 1;
        strkopiere(felder[f], MACRO_PARAMETER_LAENGE, neu);
    }
    return zuLang;
}

// Generische und lesbare lokale Labels (Doku 4.3, ab c82ass 1.00-064): <name>%[<zusatz>]: im Makro. <name> beginnt mit einem Buchstaben
// oder _, dann Buchstaben, Ziffern, _ (hoechstens ML_NAME_MAX Zeichen); ML<4 Ziffern> ist nur ein solcher Name (ML0001%).
// Der Assembler ersetzt je Aufruf das % durch drei Grossbuchstaben (schleife% -> schleifeDKR).
#define ML_NAME_MAX 24
#define ML_IDZ(c) (((c) >= 'a' && (c) <= 'z') || ((c) >= 'A' && (c) <= 'Z') || ((c) >= '0' && (c) <= '9') || (c) == '_')
#define ML_IDA(c) (((c) >= 'a' && (c) <= 'z') || ((c) >= 'A' && (c) <= 'Z') || (c) == '_')

// Laenge des Namens, wenn s mit <name>% beginnt (1 bis ML_NAME_MAX Zeichen), sonst 0
static int mlNameLaenge(const char *s) {
    if (!ML_IDA(s[0])) return 0;
    int n = 1;
    while (ML_IDZ(s[n])) n++;
    if (s[n] != '%' || n > ML_NAME_MAX) return 0;
    return n;
}

// Generische Labels in $REPT-Schleifen: Ein im Rumpf definiertes Label <name>%: (auch ML<4 Ziffern>%) erhaelt in jedem Durchlauf
// den Zusatz _<Zaehler> (ML0001%_0, ML0001%_1, schleife%_0, ...), ebenso jede Verwendung im Rumpf; Labels ausserhalb des Rumpfes
// bleiben unveraendert. Der Assembler ersetzt spaeter das % durch drei Buchstaben und behaelt den Zusatz.
#define REPT_MAX_ML 64

// Sammelt die Namen der im Rumpf (Marke in sp1) definierten Labels <name>%
static void reptMlDefiniert(const lineElements *z, int n, char namen[][ML_NAME_MAX + 1], int *anzahl) {
    for (int j = 0; j < n; j++) {
        const char *q = z[j].sp1;
        int len = mlNameLaenge(q);
        if (len > 0) {
            int da = 0;
            for (int k = 0; k < *anzahl; k++) if (strncmp(namen[k], q, (size_t)len) == 0 && namen[k][len] == '\0') da = 1;
            if (!da && *anzahl < REPT_MAX_ML) {
                memcpy(namen[*anzahl], q, (size_t)len);
                namen[*anzahl][len] = '\0';
                (*anzahl)++;
            }
        }
    }
}

// Haengt in allen Feldern an die Labels <name>% der Liste (samt vorhandenem Zusatz) den Zusatz _<k> an
static void reptMlSuffix(lineElements *z, char namen[][ML_NAME_MAX + 1], int anzahl, long long k) {
    if (anzahl == 0) return;
    char *felder[3] = { z->sp1, z->sp2, z->sp3 };
    for (int f = 0; f < 3; f++) {
        if (strchr(felder[f], '%') == NULL) continue;
        char neu[4 * MACRO_PARAMETER_LAENGE];
        size_t n = 0;
        const char *q = felder[f];
        while (*q != '\0' && n + 64 < sizeof(neu)) {
            int treffer = 0;
            int len = 0;
            if (q == felder[f] || !ML_IDZ(q[-1])) {   // nur am Wortanfang (ende% ist nicht der Anfang von weiterende%)
                len = mlNameLaenge(q);
                if (len > 0) {
                    for (int m = 0; m < anzahl; m++) if (strncmp(namen[m], q, (size_t)len) == 0 && namen[m][len] == '\0') treffer = 1;
                }
            }
            if (treffer) {
                memcpy(neu + n, q, (size_t)len + 1); n += (size_t)len + 1; q += len + 1;   // <name>%
                while (ML_IDZ(*q)) neu[n++] = *q++;   // vorhandener Zusatz
                n += (size_t)snprintf(neu + n, sizeof(neu) - n, "_%lld", k);
            } else {
                neu[n++] = *q++;
            }
        }
        neu[n] = '\0';
        strkopiere(felder[f], MACRO_PARAMETER_LAENGE, neu);
    }
}

static int mvarErsetzen(char *feld, char *grund, size_t gg);   // weiter unten (Makro-Variablen)

// Wertet die Anzahl hinter $REPT aus (Ausdruck ohne Leerzeichen, auch $CALC(...) und Parameter $1..$9). 0 = ok
static int reptAnzahl(const lineElements *z, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl,
                      MakroFehler *f, const char *op, long long *anzahl) {
    const char *p = makroRestNachWort(z);
    char text[512];
    size_t n = 0;
    while (*p == ' ' || *p == '\t') p++;
    while (*p != '\0' && *p != ';' && n + 1 < sizeof(text)) text[n++] = *p++;
    while (n > 0 && (text[n - 1] == ' ' || text[n - 1] == '\t')) n--;
    text[n] = '\0';

    if (n == 0) {
        makroMelde(f, op, "$REPT benötigt die Anzahl der Wiederholungen (Zahl oder Ausdruck ohne Leerzeichen).");
        return 1;
    }
    if (strchr(text, ' ') != NULL || strchr(text, '\t') != NULL) {
        makroMelde(f, op, "$REPT: Die Anzahl muss ein Ausdruck ohne Leerzeichen sein: %.80s", text);
        return 1;
    }
    if (strstr(text, "$Z") != NULL) {
        makroMelde(f, op, "$REPT: Der Zähler $Z1 bis $Z4 gilt nur innerhalb einer umschließenden $REPT-Schleife: %.80s", text);
        return 1;
    }
    if (mvarFund(text) != NULL) {   // Makro-Variable: Stand zu Beginn des Aufrufs (Schleifen werden vor $SET/$INC aufgeloest)
        char grundV[256];
        if (n >= MACRO_PARAMETER_LAENGE - 24) {
            makroMelde(f, op, "$REPT: Die Anzahl ist zu lang: %.80s", text);
            return 1;
        }
        if (mvarErsetzen(text, grundV, sizeof(grundV)) != 0) {
            makroMelde(f, op, "$REPT %.60s: %s", text, grundV);
            return 1;
        }
    }
    int vorher = f->anzahl;
    makroCalcErsetzen(text, sizeof(text), paramArray, paramAnzahl, f);
    if (f->anzahl != vorher) return 1;

    char ausdruck[1024];
    size_t m = 0;
    ausdruck[0] = '\0';
    for (const char *k = text; *k != '\0' && m + 2 < sizeof(ausdruck); k++) {
        if (*k == '$' && (strncmp(k, "$LEN(", 5) == 0 || strncmp(k, "$P(", 3) == 0)) {   // $LEN(i) = Zeichenzahl, $P(i) = Parameter Nummer i (Doku 4.26)
            int istLen = (k[2] == 'E');
            const char *kopf = istLen ? "$LEN" : "$P";
            const char *pe = makroKlammerEnde(k + (istLen ? 5 : 3));
            int pn = 0;
            char g2[300];
            if (pe == NULL) {
                makroMelde(f, op, "$REPT %.60s: %s( ): Klammer ) fehlt", text, kopf);
                return 1;
            }
            if (makroNummerAusdruck(k, pe, kopf, istLen ? 5 : 3, paramAnzahl, &pn, g2, sizeof(g2)) != 0) {
                makroMelde(f, op, "$REPT %.60s: %s", text, g2);
                return 1;
            }
            if (istLen) m += (size_t)snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "%d", (int)strlen(paramArray[pn - 1]));
            else        m += (size_t)snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "(%s)", paramArray[pn - 1]);
            k = pe;
        } else if (*k == '$' && strncmp(k, "$LEN", 4) == 0 && k[4] >= '1' && k[4] <= '9') {   // $LENn = Zeichenzahl von Parameter n
            int pn = k[4] - '0';
            if (pn > paramAnzahl) {
                makroMelde(f, op, "$REPT %.60s: Parameter $%d wird nicht übergeben", text, pn);
                return 1;
            }
            m += (size_t)snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "%d", (int)strlen(paramArray[pn - 1]));
            k += 4;
        } else if (*k == '$' && k[1] >= '1' && k[1] <= '9') {
            int pn = k[1] - '0';
            if (pn > paramAnzahl) {
                makroMelde(f, op, "$REPT %.60s: Parameter $%d wird nicht übergeben", text, pn);
                return 1;
            }
            m += (size_t)snprintfGekuerzt(ausdruck + m, sizeof(ausdruck) - m, "(%s)", paramArray[pn - 1]);
            k++;
        } else {
            ausdruck[m++] = *k;
            ausdruck[m] = '\0';
        }
    }
    char grund[256];
    long long wert = 0;
    if (makroRechne(ausdruck, &wert, grund, sizeof(grund)) != 0) {
        makroMelde(f, op, "$REPT %.60s: %s", text, grund);
        return 1;
    }
    if (wert < 0 || wert > REPT_MAX_ANZAHL) {
        makroMelde(f, op, "$REPT %.60s: Die Anzahl %lld liegt nicht im Bereich 0 bis %d", text, wert, REPT_MAX_ANZAHL);
        return 1;
    }
    *anzahl = wert;
    return 0;
}

// Uebernimmt die Zeilen q[von..bis) nach aus und loest dabei $REPT ... $ENDREPT auf; tiefe = Schachtelungstiefe der
// umschliessenden Schleifen (0 = aussen). Rueckgabe 0 = ok, -1 = Fehler (bereits in f gemeldet)
static int reptExpandiere(const lineElements *q, int von, int bis, int tiefe, ZeilenListe *aus,
                          char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, MakroFehler *f, const char *op) {
    for (int i = von; i < bis; i++) {
        makroAktuelleZeile = q[i].srcLine;
        if (makroErstesWort(&q[i], "$ENDREPT")) {
            makroMelde(f, op, "$ENDREPT ohne zugehöriges $REPT.");
            return -1;
        }
        if (!makroErstesWort(&q[i], "$REPT")) {
            zlAnhaengen(aus, &q[i]);
            continue;
        }

        int ende = -1, t = 1;
        for (int j = i + 1; j < bis; j++) {
            if (makroErstesWort(&q[j], "$REPT")) {
                t++;
            } else if (makroErstesWort(&q[j], "$ENDREPT")) {
                if (--t == 0) { ende = j; break; }
            }
        }
        if (ende < 0) {
            makroMelde(f, op, "$REPT ohne zugehöriges $ENDREPT.");
            return -1;
        }
        if (tiefe >= REPT_MAX_TIEFE) {
            makroMelde(f, op, "$REPT darf höchstens %d-fach geschachtelt werden.", REPT_MAX_TIEFE);
            return -1;
        }
        long long anzahl = 0;
        if (reptAnzahl(&q[i], paramArray, paramAnzahl, f, op, &anzahl) != 0) return -1;

        int laenge = ende - i - 1;
        if (anzahl == 0 || laenge == 0) {
            i = ende;
            continue;
        }
        if ((long long)aus->n + anzahl * laenge > REPT_MAX_ZEILEN) {
            makroMelde(f, op, "Die $REPT-Wiederholung erzeugt mehr als %d Zeilen.", REPT_MAX_ZEILEN);
            return -1;
        }
        char definiert[REPT_MAX_ML][ML_NAME_MAX + 1];   // im Rumpf definierte generische/lokale Labels (Namen vor dem %)
        int nDef = 0;
        reptMlDefiniert(&q[i + 1], laenge, definiert, &nDef);
        lineElements *tmp = (lineElements *)malloc((size_t)laenge * sizeof(lineElements));
        if (!tmp) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
        for (long long k = 0; k < anzahl; k++) {
            memcpy(tmp, &q[i + 1], (size_t)laenge * sizeof(lineElements));
            for (int m = 0; m < laenge; m++) {
                reptMlSuffix(&tmp[m], definiert, nDef, k);
                if (reptZaehlerErsetzen(&tmp[m], tiefe + 1, k) != 0) {
                    free(tmp);
                    makroMelde(f, op, "Eine Zeile wird durch die Ersetzung von $Z%d zu lang.", tiefe + 1);
                    return -1;
                }
            }
            if (reptExpandiere(tmp, 0, laenge, tiefe + 1, aus, paramArray, paramAnzahl, f, op) != 0) {
                free(tmp);
                return -1;
            }
        }
        free(tmp);
        i = ende;
    }
    return 0;
}

// Ein Zaehler $Z1 bis $Z4 in Marke, Operation oder Operand ausserhalb einer $REPT-Schleife ist ein Fehler
// (in Kommentarzeilen und Kommentaren bleibt der Text unveraendert).
static void reptRestzaehlerPruefen(const lineElements *z, int n, MakroFehler *f, const char *op) {
    if (z == NULL || f->anzahl > 0) return;
    for (int j = 0; j < n; j++) {
        const char c = z[j].sp1[0];
        if (c == ';' || c == '#' || c == '$' || c == '&') continue;
        makroAktuelleZeile = z[j].srcLine;
        const char *felder[3] = { z[j].sp1, z[j].sp2, z[j].sp3 };
        for (int k = 0; k < 3; k++) {
            for (const char *q = strstr(felder[k], "$Z"); q != NULL; q = strstr(q + 1, "$Z")) {
                if (q[2] >= '1' && q[2] <= '4') {
                    makroMelde(f, op, "Der Zähler $Z%c gilt nur innerhalb einer $REPT-Schleife (bei \"%.60s\").", q[2], felder[k]);
                    is_error0 = 1;
                    return;
                }
            }
        }
    }
}

// Stufe 1 des Makroaufrufs: $REPT-Schleifen aufloesen; result wird freigegeben. Bei einem Fehler bleiben die Zeilen
// unveraendert (der Fehler steht in f).
static lineElements *makroWiederholungenAufloesen(lineElements *result, int *lineCount,
                                                  char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl,
                                                  MakroFehler *f, const char *op) {
    int hatRept = 0;
    for (int j = 0; j < *lineCount && !hatRept; j++) {
        if (makroErstesWort(&result[j], "$REPT") || makroErstesWort(&result[j], "$ENDREPT")) hatRept = 1;
    }
    if (!hatRept) {
        reptRestzaehlerPruefen(result, *lineCount, f, op);
        return result;
    }

    ZeilenListe aus = { NULL, 0, 0 };
    if (reptExpandiere(result, 0, *lineCount, 0, &aus, paramArray, paramAnzahl, f, op) != 0) {
        is_error0 = 1;
        free(aus.z);
        return result;
    }
    free(result);
    reptRestzaehlerPruefen(aus.z, aus.n, f, op);
    if (aus.z == NULL) {   // alle Zeilen waren Schleifenrumpf mit 0 Durchlaeufen
        aus.z = (lineElements *)calloc(1, sizeof(lineElements));
        if (!aus.z) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    }
    *lineCount = aus.n;
    return aus.z;
}

// ----------------------------------------------------------------------------------
// Bedingungen: $IF <bed> ... [$ELIF <bed> ...] [$ELSE ...] $ENDIF, beliebig geschachtelt (bis IF_MAX_TIEFE).
// <bed> = a b c [(|&) d e f ...] mit hoechstens BED_MAX_BLOECKE Bloecken (a, c Werte; b > < = >= <= != <>);
// & bindet staerker als | (ab c82ass 1.01-031; vorher von links nach rechts); Klammern ( ) als eigene Woerter gruppieren.
#define IF_MAX_TIEFE     16
#define BED_MAX_BLOECKE  8
#define BED_MAX_TOKEN    64

typedef struct {
    char t[BED_MAX_TOKEN][128];
    int n;          // Anzahl Woerter
    int pos;        // aktuelle Position
    char fehler[300];
} BedParser;

static int bedAusdruck(BedParser *b, int *wert, int klammerTiefe);

static int bedFehler(BedParser *b, const char *format, ...) {
    va_list ap;
    va_start(ap, format);
    vsnprintf(b->fehler, sizeof(b->fehler), format, ap);
    va_end(ap);
    return -1;
}

static int bedGueltigerVergleich(const char *op) {
    return strcmp(op, ">") == 0 || strcmp(op, "<") == 0 || strcmp(op, "=") == 0 || strcmp(op, ">=") == 0 ||
           strcmp(op, "<=") == 0 || strcmp(op, "!=") == 0 || strcmp(op, "<>") == 0;
}

static int bedTerm(BedParser *b, int *wert, int klammerTiefe) {
    if (b->pos >= b->n) return bedFehler(b, "Die Bedingung ist unvollständig.");
    if (strcmp(b->t[b->pos], "(") == 0) {
        b->pos++;
        if (bedAusdruck(b, wert, klammerTiefe + 1) != 0) return -1;
        if (b->pos >= b->n || strcmp(b->t[b->pos], ")") != 0) return bedFehler(b, "Klammer ) fehlt.");
        b->pos++;
        return 0;
    }
    if (b->pos + 2 >= b->n) return bedFehler(b, "Die Bedingung ist unvollständig (a b c erwartet).");
    const char *a = b->t[b->pos], *op = b->t[b->pos + 1], *c = b->t[b->pos + 2];
    if (!bedGueltigerVergleich(op)) {
        return bedFehler(b, "Unbekanntes Vergleichszeichen \"%.20s\" (erlaubt: > < = >= <= != <>).", op);
    }
    *wert = macroParameterCompare(a, op, c) > 0 ? 1 : 0;
    b->pos += 3;
    return 0;
}

// Prüft, ob das Wort an der Position ein Verknüpfungszeichen ist; sonst Fehler "Der n. Parameter muss | oder & sein."
static int bedVerknuepfungPruefen(BedParser *b) {
    const char *verkn = b->t[b->pos];
    if (strcmp(verkn, "|") == 0 || strcmp(verkn, "&") == 0) return 0;
    int nr = 0;   // Nummer unter den Woertern ohne Klammern (wie bei der Anzahlpruefung)
    for (int k = 0; k <= b->pos; k++) {
        if (strcmp(b->t[k], "(") != 0 && strcmp(b->t[k], ")") != 0) nr++;
    }
    return bedFehler(b, "Der %d. Parameter muss | oder & sein.", nr);
}

// UND-Kette: term { & term }; & bindet staerker als | (ab c82ass 1.01-031)
static int bedUnd(BedParser *b, int *wert, int klammerTiefe) {
    if (bedTerm(b, wert, klammerTiefe) != 0) return -1;
    while (b->pos < b->n && strcmp(b->t[b->pos], ")") != 0) {
        if (bedVerknuepfungPruefen(b) != 0) return -1;
        if (b->t[b->pos][0] != '&') return 0;   // | beendet die UND-Kette
        b->pos++;
        int w2 = 0;
        if (bedTerm(b, &w2, klammerTiefe) != 0) return -1;
        *wert = *wert && w2;
    }
    return 0;
}

// ODER-Kette: undkette { | undkette }
static int bedAusdruck(BedParser *b, int *wert, int klammerTiefe) {
    if (bedUnd(b, wert, klammerTiefe) != 0) return -1;
    while (b->pos < b->n && strcmp(b->t[b->pos], ")") != 0) {
        if (bedVerknuepfungPruefen(b) != 0) return -1;
        b->pos++;   // das | (ein & kann hier nicht mehr stehen)
        int w2 = 0;
        if (bedUnd(b, &w2, klammerTiefe) != 0) return -1;
        *wert = *wert || w2;
    }
    return 0;
}

// Wertet die Bedingung hinter $IF/$ELIF aus. Rueckgabe 0 = ok (wert 0/1), sonst Fehlertext in grund
static int makroBedingungWert(const lineElements *z, int *wert, char *grund, size_t grundGroesse) {
    BedParser b;
    b.n = 0;
    b.pos = 0;
    b.fehler[0] = '\0';
    const char *p = makroRestNachWort(z);
    int zuViele = 0, ohneKlammer = 0;
    while (*p != '\0' && *p != ';') {
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0' || *p == ';') break;
        if (b.n >= BED_MAX_TOKEN) { zuViele = 1; break; }
        size_t l = 0;
        while (*p != '\0' && *p != ' ' && *p != '\t' && *p != ';') {
            if (l + 1 < sizeof(b.t[0])) b.t[b.n][l++] = *p;
            p++;
        }
        b.t[b.n][l] = '\0';
        if (strcmp(b.t[b.n], "(") != 0 && strcmp(b.t[b.n], ")") != 0) ohneKlammer++;
        b.n++;
    }
    int ok = !zuViele && ohneKlammer >= 3 && (ohneKlammer - 3) % 4 == 0 && ohneKlammer <= 3 + 4 * (BED_MAX_BLOECKE - 1);
    if (!ok) {
        snprintf(grund, grundGroesse, "$IF benötigt 3, 7, 11, 15, 19, 23, 27 oder 31 Parameter der Struktur a b c [|&] d e f [|&] ... (Klammern ( ) als eigene Wörter).");
        return 1;
    }
    int w = 0;
    if (bedAusdruck(&b, &w, 0) != 0) {
        snprintf(grund, grundGroesse, "%s", b.fehler);
        return 1;
    }
    if (b.pos < b.n) {   // nur ein ) ohne ( bleibt uebrig
        snprintf(grund, grundGroesse, "Klammer ) ohne ( davor.");
        return 1;
    }
    *wert = w;
    return 0;
}

typedef struct {
    int elternAktiv;   // die umschliessende Ebene ist aktiv
    int genommen;      // ein Zweig dieses $IF wurde schon genommen
    int aktiv;         // der gerade offene Zweig ist aktiv
    int imElse;        // $ELSE ist schon vorgekommen
    int istWhile;      // Rahmen eines $WHILE (Doku 4.19), nicht eines $IF
    int rueck;         // $WHILE: Zeilenindex der $WHILE-Zeile (Ziel des Rücksprungs bei $ENDWHILE)
    int durchlauf;     // $WHILE: Zahl der bisher begonnenen Durchläufe
    int zeile;         // Quelltextzeile des $IF bzw. $WHILE (fuer die Meldung "Fehlendes $ENDIF" im Quelltextmodus)
    char (*mlNamen)[ML_NAME_MAX + 1];   // $WHILE: im Rumpf definierte lokale Labels <name>% (Namen vor dem %), je Durchlauf mit eigenem Zusatz (Doku 4.19); NULL = keine
    int mlAnzahl;      // Zahl der Namen in mlNamen
} IfRahmen;

// $WHILE <bed> ... $ENDWHILE (Schleife mit Abbruchbedingung) und $EXIT (Makro vorzeitig verlassen), Doku 4.19.
// Beide wirken in der Auswertung der Bedingungen (makroBedingungenAuswerten), denn nur dort ändern sich die Makro-Variablen.
#define WHILE_MAX_DURCHLAEUFE 4096   // je $WHILE; mehr gilt als Endlosschleife (Fehler)

// Makro-Variablen ($SET, $INC, $V(name), Doku 4.7) und Felder ($DIM, $SET name(i), $V(name(i)), Doku 4.17): ganzzahlige Werte
// oder Texte, die ueber alle Makroaufrufe eines Assemblerlaufs erhalten bleiben
#define MVAR_MAX 64           // hoechstens 64 globale Variablen (Doku 4.7)
#define MFELD_MAX 16          // hoechstens 16 globale Felder (Doku 4.17)
#define MFELD_ELEM_MAX 256    // hoechstens 256 Elemente je Feld
#define MVAR_TEXT_MAX 1000    // hoechstens so viele Zeichen je Text einer Variablen (bis c82ass 1.01-014: 200; Doku 4.12)
#define MTEXT_PUFFER 4096     // Arbeitspuffer fuer Texte ($SET name "text", Argumente und Ergebnis der Zeichenkettenfunktionen, Doku 4.21);
                              // groesser als MVAR_TEXT_MAX, damit ein Zwischenergebnis (z. B. dreifach verkettet) noch Platz hat
#define MVAR_RUNDEN_MAX 1000  // hoechstens so viele $V(...) je Aufloesung eines Feldes (Selbstverweis, Doku 4.21)
#define MAKRO_KETTE_MAX 32   // Aufrufkette der Makros (Tiefe = Ebene der lokalen Variablen, Doku 4.20)
#define MLOKAL_VAR_MAX 64     // hoechstens 64 lokale Variablen je Makroaufruf, $LOCAL und mit ;#MAKROLOKAL=1 $SET gemeinsam (bis c82ass 1.01-031: 16; Doku 4.20, 4.31)
#define MLOKAL_FELD_MAX 16    // hoechstens 16 lokale Felder je Makroaufruf, $LOCAL und mit ;#MAKROLOKAL=1 $DIM gemeinsam (bis c82ass 1.01-031: 4)
#define MGLOB_JE_AUFRUF (MVAR_MAX + MFELD_MAX)   // hoechstens so viele Namen mit $GLOBAL je Makroaufruf (mehr Namen als globale Eintraege gibt es nicht)
#define MGLOB_TAB (MGLOB_JE_AUFRUF * MAKRO_KETTE_MAX)
#define MVAR_TAB (MVAR_MAX + MLOKAL_VAR_MAX * MAKRO_KETTE_MAX)
#define MFELD_TAB (MFELD_MAX + MLOKAL_FELD_MAX * MAKRO_KETTE_MAX)
typedef struct { long long wert; int istText; char text[MVAR_TEXT_MAX + 1]; } MVarWert;   // istText: Wert ist eine Zeichenkette ($SET name "text")
// ebene 0 = global; sonst lokal in dem Makroaufruf mit dieser Tiefe der Aufrufkette (makroKetteTiefe, Doku 4.20)
static int mReihe = 0;   // laufende Nummer der Anlage einer Variablen oder eines Feldes (Reihenfolge der Ausgabe von $DUMP, Doku 4.24)
static struct { char name[40]; int ebene; int reihe; long long wert; int istText; char text[MVAR_TEXT_MAX + 1]; int deklZeile; unsigned deklAusf; int provisorisch; } mvar[MVAR_TAB];   // deklZeile, deklAusf: nur bei lokalen Eintraegen ($LOCAL, Doku 4.20); provisorisch: globale Variable, die $GLOBAL mit 0 angelegt hat und die noch nie gesetzt wurde (ein folgendes $DIM macht daraus ein Feld, Doku 4.31)
static int mvarAnzahl = 0;
static struct { char name[40]; int ebene; int reihe; int anzahl; MVarWert *el; int deklZeile; unsigned deklAusf; } mfeld[MFELD_TAB];   // el: anzahl Elemente, vom Index 0 an
static int mfeldAnzahl = 0;

static int makroKetteTiefe;   // Definition weiter unten (Aufrufkette der Makros)

// Aufrufparameter des Makroaufrufs, der gerade aufgeloest wird (gesetzt und zurueckgestellt in loeseMacroAuf; NULL ausserhalb eines Aufrufs).
// Sie dienen mvarErsetzen, um ein $P(..) oder $LEN(..) nachzuholen, dessen Nummer erst nach dem Ersetzen von $V(..) feststeht
// (ab c82ass 1.01-015, Doku 4.13 und 4.17); im Quelltextmodus (makroKetteTiefe == 0) gibt es keine Aufrufparameter.
static char (*mAktParam)[MACRO_PARAMETER_LAENGE] = NULL;
static int mAktParamAnzahl = 0;

// Kopie von s auf dem Heap (der Aufrufer gibt sie mit free frei): der Rest einer Zeile, der bis zur Puffergroesse reichen kann
static char *mtextKopie(const char *s) {
    size_t n = strlen(s);
    char *k = (char *)malloc(n + 1);
    if (!k) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    memcpy(k, s, n + 1);
    return k;
}

// Lokale Eintraege des laufenden Aufrufs (Ebene = Tiefe der Aufrufkette); ausserhalb eines Aufrufs gibt es keine.
static int mLokalSuche(const char *name, int istFeld) {
    int e = makroKetteTiefe;
    if (e < 1) return -1;
    if (istFeld) { for (int k = 0; k < mfeldAnzahl; k++) if (mfeld[k].ebene == e && strcmp(mfeld[k].name, name) == 0) return k; }
    else         { for (int k = 0; k < mvarAnzahl;  k++) if (mvar[k].ebene == e  && strcmp(mvar[k].name, name) == 0)  return k; }
    return -1;
}

// Schalter ;#MAKROLOKAL=1 (ab c82ass 1.02-001, Doku 4.31): 1 = $SET und $DIM legen im Makroaufruf lokale Variablen und Felder an.
// Gesetzt von ladeMakroLokalSchalter (Pass 0, vor dem Aufloesen der Makros); ohne den Schalter bleibt alles wie bis 1.01-031.
static int mMakroLokal = 0;

// Namen, die der laufende Makroaufruf mit $GLOBAL als global vereinbart hat (ebene = Tiefe der Aufrufkette); sie enden mit dem Aufruf
static struct { char name[40]; int ebene; } mglob[MGLOB_TAB];
static int mglobAnzahl = 0;

// 1, wenn der laufende Makroaufruf den Namen mit $GLOBAL als global vereinbart hat (ausserhalb eines Aufrufs nie)
static int mGlobalVereinbart(const char *name) {
    const int e = makroKetteTiefe;
    if (e < 1) return 0;
    for (int k = 0; k < mglobAnzahl; k++) if (mglob[k].ebene == e && strcmp(mglob[k].name, name) == 0) return 1;
    return 0;
}

// Globale einfache Variable (Ebene 0) und globales Feld, ohne Ruecksicht auf lokale gleichen Namens; -1 = gibt es nicht
static int mvarGlobalSuche(const char *name) {
    for (int k = 0; k < mvarAnzahl; k++) if (mvar[k].ebene == 0 && strcmp(mvar[k].name, name) == 0) return k;
    return -1;
}
static int mfeldGlobalSuche(const char *name) {
    for (int k = 0; k < mfeldAnzahl; k++) if (mfeld[k].ebene == 0 && strcmp(mfeld[k].name, name) == 0) return k;
    return -1;
}

// Entfernt den Eintrag k der Variablentabelle (die Reihenfolge der uebrigen bleibt)
static void mvarEntfernen(int k) {
    for (int q = k; q + 1 < mvarAnzahl; q++) mvar[q] = mvar[q + 1];
    mvarAnzahl--;
}

// Sichtbare einfache Variable: erst die lokale des Aufrufs, sonst die globale (eine lokale Variable oder ein lokales Feld
// gleichen Namens verdeckt die globale beider Arten)
static int mvarSuche(const char *name) {
    int k = mLokalSuche(name, 0);
    if (k >= 0) return k;
    if (mLokalSuche(name, 1) >= 0) return -1;
    for (k = 0; k < mvarAnzahl; k++) if (mvar[k].ebene == 0 && strcmp(mvar[k].name, name) == 0) return k;
    return -1;
}

static int mfeldSuche(const char *name) {
    int k = mLokalSuche(name, 1);
    if (k >= 0) return k;
    if (mLokalSuche(name, 0) >= 0) return -1;
    for (k = 0; k < mfeldAnzahl; k++) if (mfeld[k].ebene == 0 && strcmp(mfeld[k].name, name) == 0) return k;
    return -1;
}

// Zerlegt "name" oder "name(index)": 0 = einfacher Name, 1 = Feldzugriff (basis, idx gefuellt), -1 = Fehler (grund gefuellt)
static int mfeldZerlegen(const char *s, char *basis, size_t bg, char *idx, size_t ig, char *grund, size_t gg) {
    const char *kl = strchr(s, '(');
    size_t bl = kl ? (size_t)(kl - s) : strlen(s);
    if (bl == 0 || bl >= bg || bl >= 40 || !isalpha((unsigned char)s[0])) { snprintf(grund, gg, "Variablenname %.60s ungültig", s); return -1; }
    snprintf(basis, bg, "%.*s", (int)bl, s);
    for (const char *c = basis; *c; c++) if (!isalnum((unsigned char)*c) && *c != '_') { snprintf(grund, gg, "Variablenname %s ungültig", basis); return -1; }
    if (kl == NULL) {
        if (strchr(s, ')') != NULL) { snprintf(grund, gg, "%.60s: Klammer ) ohne ( davor", s); return -1; }
        return 0;
    }
    const char *e = makroKlammerEnde(kl + 1);
    if (e == NULL) { snprintf(grund, gg, "%.60s: Klammer ) fehlt", s); return -1; }
    if (e[1] != '\0') { snprintf(grund, gg, "%.60s: hinter dem Index darf nichts mehr stehen (Klammer überzählig?)", s); return -1; }
    if (e == kl + 1) { snprintf(grund, gg, "%s(): Der Index fehlt", basis); return -1; }
    if ((size_t)(e - kl - 1) >= ig) { snprintf(grund, gg, "%s(...): Der Index ist zu lang", basis); return -1; }
    snprintf(idx, ig, "%.*s", (int)(e - kl - 1), kl + 1);
    return 1;
}

static int mvarErsetzen(char *feld, char *grund, size_t gg);   // gleich unten (Puffer MACRO_PARAMETER_LAENGE)
static int mvarErsetzenG(char *feld, size_t groesse, char *grund, size_t gg);   // gleich unten (Puffer beliebiger Groesse)

// Wertet den Index eines Feldzugriffs aus (Rechenausdruck, darf $V(...) enthalten), ohne ihn gegen ein Feld zu pruefen; 0 = ok
static int mfeldIndexWert(const char *feldName, const char *idx, long long *i, char *grund, size_t gg) {
    char puffer[MACRO_PARAMETER_LAENGE];
    STRKOPIE(puffer, idx);
    char g1[220];
    if (mvarFund(puffer) != NULL && mvarErsetzen(puffer, g1, sizeof(g1)) != 0) { snprintf(grund, gg, "%s", g1); return 1; }
    char g2[200];
    if (makroRechne(puffer, i, g2, sizeof(g2)) != 0) { snprintf(grund, gg, "%s(%.60s): Index ungültig: %.120s", feldName, idx, g2); return 1; }
    return 0;
}

// Wertet den Index eines Feldzugriffs aus und prueft ihn gegen das Feld f; 0 = ok
static int mfeldIndex(int f, const char *idx, long long *i, char *grund, size_t gg) {
    if (mfeldIndexWert(mfeld[f].name, idx, i, grund, gg) != 0) return 1;
    if (*i < 0 || *i >= mfeld[f].anzahl) {
        snprintf(grund, gg, "Feld %s: Index %lld liegt außerhalb von 0 bis %d (Anzahl %d)", mfeld[f].name, *i, mfeld[f].anzahl - 1, mfeld[f].anzahl);
        return 1;
    }
    return 0;
}

// $DEFINED(...) und $MDEFINED(...) (Doku 4.25, ab c82ass 1.01-006): pos zeigt in feld auf das $ der Funktion; die Funktion wird durch
// 1 oder 0 ersetzt, 0 = ok, sonst Fehlertext in grund. Das Argument wird erst von $V(...) (und anderen Funktionen dieser Art)
// befreit; ein Paar Klammern um das ganze Argument ist erlaubt. Ein Name, den es nicht gibt, ist kein Fehler (Ergebnis 0).
static int mvarExistenz(char *feld, size_t groesse, char *pos, char *grund, size_t gg) {
    int istM = (pos[1] == 'M');
    const char *fname = istM ? "$MDEFINED" : "$DEFINED";
    const char *arg0 = pos + strlen(fname) + 1;   // hinter der oeffnenden Klammer
    const char *ende = makroKlammerEnde(arg0);
    if (ende == NULL) { snprintf(grund, gg, "%s(...): Klammer ) fehlt", fname); return 1; }
    size_t n = (size_t)(ende - arg0);
    if (n == 0) { snprintf(grund, gg, "%s(): Das Argument fehlt", fname); return 1; }
    if (n >= MACRO_PARAMETER_LAENGE - 1) { snprintf(grund, gg, "%s(...): Das Argument ist zu lang", fname); return 1; }
    char arg[MACRO_PARAMETER_LAENGE];
    memcpy(arg, arg0, n);
    arg[n] = '\0';
    char g1[220];
    if (mvarFund(arg) != NULL && mvarErsetzen(arg, g1, sizeof(g1)) != 0) { snprintf(grund, gg, "%s(%.40s): %.150s", fname, arg, g1); return 1; }
    size_t al = strlen(arg);
    if (arg[0] == '(' && al > 2 && makroKlammerEnde(arg + 1) == arg + al - 1) {   // (x) -> x: ein $1 wird eingeklammert eingesetzt (Doku 4.2)
        memmove(arg, arg + 1, al - 2);
        arg[al - 2] = '\0';
    }
    if (arg[0] == '\0') { snprintf(grund, gg, "%s(): Das Argument fehlt", fname); return 1; }
    int ergebnis = 0;
    if (istM) {
        for (const char *c = arg; *c; c++) {
            if (*c == ':' || *c == ' ' || *c == '\t') { snprintf(grund, gg, "$MDEFINED(%.40s): Der Makroname steht ohne Doppelpunkt und ohne Leerraum", arg); return 1; }
        }
        ergebnis = (macroSuche(arg) >= 0);
    } else {
        const char *n0 = arg;
        int elemZahl = (n0[0] == '@');   // $DEFINED(@name): nur ein Feld
        if (elemZahl) n0++;
        char basis[40], idx[200], g2[300];
        int fz = mfeldZerlegen(n0, basis, sizeof(basis), idx, sizeof(idx), g2, sizeof(g2));
        if (fz < 0) { snprintf(grund, gg, "$DEFINED(%.40s): %.150s", arg, g2); return 1; }
        if (elemZahl) {
            if (fz == 1) { snprintf(grund, gg, "$DEFINED(@%s): nach @ steht nur der Feldname ohne Index", basis); return 1; }
            ergebnis = (mfeldSuche(basis) >= 0);
        } else if (fz == 1) {   // Feldelement: das Feld ist sichtbar und der Index liegt im Bereich; ein Index ausserhalb ist kein Fehler
            long long i = 0;
            if (mfeldIndexWert(basis, idx, &i, g2, sizeof(g2)) != 0) { snprintf(grund, gg, "$DEFINED(%.40s): %.150s", arg, g2); return 1; }
            int f = mfeldSuche(basis);
            ergebnis = (f >= 0 && i >= 0 && i < mfeld[f].anzahl);
        } else {
            ergebnis = (mvarSuche(basis) >= 0 || mfeldSuche(basis) >= 0);
        }
    }
    char *rest = mtextKopie(ende + 1);   // der Rest der Zeile kann bis zur Puffergroesse reichen
    size_t frei = groesse - (size_t)(pos - feld);
    snprintf(pos, frei, "%d%s", ergebnis, rest);
    free(rest);
    return 0;
}

// 1, wenn pos in feld innerhalb der Klammer eines $CALC(...), $CALCO(...), $CALCOn(...), $CALCB... oder $CALCH... steht
static int mvarImCalc(const char *feld, const char *pos) {
    for (const char *c = strstr(feld, "$CALC"); c != NULL && c < pos; c = strstr(c + 5, "$CALC")) {
        const char *k = c + 5;
        if (*k == 'O') { k++; if (*k >= '1' && *k <= '9') k++; }
        else if (*k == 'B' || *k == 'H') { k++; if (*k >= '1' && *k <= '9') { k++; if (*k >= '0' && *k <= '9') k++; } }   // $CALCB(...), $CALCBn(...), $CALCBnn(...), ebenso $CALCH...
        if (*k != '(') continue;
        const char *e = makroKlammerEnde(k + 1);
        if (e == NULL || e > pos) return 1;
    }
    return 0;
}

// Loest in feld ein $P(..) oder $LEN(..) auf, das mvarErsetzen uebrig gelassen hat, weil $V(..) in der Nummer stand (z. B.
// $P($V(i)): makroPErsetzen und makroLenErsetzen lassen so eine Stelle stehen, denn $V(..) hat erst jetzt seinen Wert). Die
// Nummer wird jetzt ausgerechnet und durch den Aufrufparameter ($P) bzw. dessen Zeichenzahl ($LEN) ersetzt (ab c82ass 1.01-015).
// Innerhalb von $CALC(...), $CALCO(...) und $CALCOn(...) steht der Parameter wie dort ueblich in Klammern (Doku 4.2).
// Gilt nur in einem Makroaufruf (mAktParam gesetzt), nicht im Quelltextmodus; 0 = ok, sonst Fehlertext in grund.
static int mvarParamNachholen(char *feld, size_t groesse, char *grund, size_t gg) {
    if (mAktParam == NULL || makroKetteTiefe == 0) return 0;
    char *pos = feld;
    for (;;) {
        char *p = strstr(pos, "$P(");
        char *l = strstr(pos, "$LEN(");
        int istLen = 0;
        if (l != NULL && (p == NULL || l < p)) { p = l; istLen = 1; }
        if (p == NULL) return 0;
        const char *kopf = istLen ? "$LEN" : "$P";
        const size_t kl = istLen ? 5 : 3;
        const char *e = makroKlammerEnde(p + kl);
        if (e == NULL) { snprintf(grund, gg, "%s( ): Klammer ) fehlt", kopf); return 1; }
        int pn = 0;
        char g2[300];
        if (makroNummerAusdruck(p, e, kopf, kl, mAktParamAnzahl, &pn, g2, sizeof(g2)) != 0) { snprintfGekuerzt(grund, gg, "%s: %.250s", kopf, g2); return 1; }
        char ersatz[MACRO_PARAMETER_LAENGE + 4];
        if (istLen) snprintf(ersatz, sizeof(ersatz), "%d", (int)strlen(mAktParam[pn - 1]));
        else if (mvarImCalc(feld, p)) snprintf(ersatz, sizeof(ersatz), "(%s)", mAktParam[pn - 1]);
        else snprintf(ersatz, sizeof(ersatz), "%s", mAktParam[pn - 1]);
        char *rest = mtextKopie(e + 1);
        size_t vorn = (size_t)(p - feld);
        size_t el = strlen(ersatz);
        if (vorn + el + strlen(rest) + 1 > groesse) {
            free(rest);
            snprintf(grund, gg, "%s(%.40s): Text passt nicht in die Zeile", kopf, mAktParam[pn - 1]);
            return 1;
        }
        snprintf(p, groesse - vorn, "%s%s", ersatz, rest);
        free(rest);
        pos = p + el;   // der eingesetzte Text wird nicht noch einmal durchsucht
    }
}

// Ersetzt jedes $V(name), $V(#name), $V(name(index)), $V(#name(index)) und $V(@name) in feld durch den Wert, ebenso $DEFINED(...) und
// $MDEFINED(...) durch 1 oder 0 (Doku 4.25); 0 = ok, sonst Fehlertext in grund. feld hat Platz fuer groesse Zeichen (mit dem Ende \0);
// mvarErsetzen nimmt MACRO_PARAMETER_LAENGE, die Texte der Zeichenkettenfunktionen und von $SET brauchen MTEXT_PUFFER (Doku 4.12, 4.21).
// Danach wird ein $P(..) oder $LEN(..) nachgeholt, dessen Nummer $V(..) enthielt (mvarParamNachholen).
static int mvarErsetzen(char *feld, char *grund, size_t gg) {
    return mvarErsetzenG(feld, MACRO_PARAMETER_LAENGE, grund, gg);
}

static int mvarErsetzenG(char *feld, size_t groesse, char *grund, size_t gg) {
    char *pos;
    int runden = 0;   // Rundengrenze: ein Text, der wieder $V(...) ergibt (Selbstverweis), haengte den Assembler sonst auf (bis 1.00-067)
    while ((pos = (char *)mvarFund(feld)) != NULL) {
        if (++runden > MVAR_RUNDEN_MAX) { snprintf(grund, gg, "$V(...): Auflösung ohne Ende (Selbstverweis?)"); return 1; }
        if (pos[1] == 'D' || pos[1] == 'M') {   // $DEFINED( oder $MDEFINED(
            if (mvarExistenz(feld, groesse, pos, grund, gg) != 0) return 1;
            continue;
        }
        if (pos[1] == 'P') {   // $PROBE (ohne Klammern): 1 im Probelauf und bei --pass0, sonst 0 (Doku 4.23)
            if (pos[6] == '(') { snprintf(grund, gg, "$PROBE steht ohne Klammern und ohne Argument"); return 1; }
            char *rest = mtextKopie(pos + 6);
            size_t frei = groesse - (size_t)(pos - feld);
            snprintf(pos, frei, "%d%s", adrNochImLauf() ? 1 : 0, rest);
            free(rest);
            continue;
        }
        const char *ende = makroKlammerEnde(pos + 3);
        if (ende == NULL || ende - pos - 3 <= 0 || ende - pos - 3 >= 200) { snprintf(grund, gg, "$V(name): Name oder Klammer ) fehlt"); return 1; }
        char name[200];
        snprintf(name, sizeof(name), "%.*s", (int)(ende - pos - 3), pos + 3);
        int laenge = (name[0] == '#');   // $V(#name): Zeichenzahl des Textes (Doku 4.12)
        int elemZahl = (name[0] == '@'); // $V(@name): Anzahl der Elemente eines Feldes (Doku 4.17)
        const char *n0 = name + laenge + elemZahl;
        char basis[40], idx[200];
        int fz = mfeldZerlegen(n0, basis, sizeof(basis), idx, sizeof(idx), grund, gg);
        if (fz < 0) { char g[300]; snprintfGekuerzt(g, sizeof(g), "$V(%.40s): %s", name, grund); snprintfGekuerzt(grund, gg, "%s", g); return 1; }
        long long zahl = 0;
        int istTxt = 0;
        const char *txt = "";
        if (elemZahl) {
            int f = mfeldSuche(basis);
            if (fz == 1) { snprintf(grund, gg, "$V(@%s): nach @ steht nur der Feldname ohne Index", basis); return 1; }
            if (f < 0) { snprintf(grund, gg, "Feld %s ist nicht vereinbart ($DIM fehlt)", basis); return 1; }
            zahl = mfeld[f].anzahl;
        } else if (fz == 1) {
            int f = mfeldSuche(basis);
            if (f < 0) { snprintf(grund, gg, "Feld %s ist nicht vereinbart ($DIM fehlt)", basis); return 1; }
            long long i;
            if (mfeldIndex(f, idx, &i, grund, gg) != 0) return 1;
            istTxt = mfeld[f].el[i].istText;
            txt = mfeld[f].el[i].text;
            zahl = mfeld[f].el[i].wert;
            if (laenge && !istTxt) { snprintf(grund, gg, "$V(#%s(%.40s)): Element enthält keinen Text", basis, idx); return 1; }
        } else {
            if (mfeldSuche(basis) >= 0) { snprintfGekuerzt(grund, gg, "$V(%s): %s ist ein Feld, der Index fehlt", name, basis); return 1; }
            int k = mvarSuche(basis);
            if (k < 0) { snprintf(grund, gg, "Variable %s ist nicht definiert ($SET fehlt)", basis); return 1; }
            if (laenge && !mvar[k].istText) { snprintf(grund, gg, "$V(#%s): Variable enthält keinen Text", basis); return 1; }
            istTxt = mvar[k].istText;
            txt = mvar[k].text;
            zahl = mvar[k].wert;
        }
        char *rest = mtextKopie(ende + 1);   // der Rest kann bis zur Puffergroesse reichen
        size_t frei = groesse - (size_t)(pos - feld);
        if (laenge) { snprintf(pos, frei, "%d%s", (int)strlen(txt), rest); free(rest); continue; }
        if (istTxt && strlen(txt) + strlen(rest) + 1 > frei) {
            free(rest);
            if (groesse > MACRO_PARAMETER_LAENGE) snprintfGekuerzt(grund, gg, "$V(%s): Text passt nicht in den Arbeitspuffer (höchstens %d Zeichen)", name, (int)groesse - 1);
            else snprintfGekuerzt(grund, gg, "$V(%s): Text passt nicht in die Zeile", name);
            return 1;
        }
        if (istTxt) snprintfGekuerzt(pos, frei, "%s%s", txt, rest);
        else snprintf(pos, frei, "%lld%s", zahl, rest);
        free(rest);
    }
    if (runden > 0) return mvarParamNachholen(feld, groesse, grund, gg);
    return 0;
}

// Ziel einer Zuweisung: einfache Variable (bei $SET wird sie angelegt) oder Feldelement; 0 = ok
typedef struct { long long *wert; int *istText; char *text; } MZiel;
static int mvarZiel(int istSet, const char *name, MZiel *z, char *grund, size_t gg) {
    char basis[40], idx[200];
    int fz = mfeldZerlegen(name, basis, sizeof(basis), idx, sizeof(idx), grund, gg);
    if (fz < 0) return 1;
    if (fz == 1) {
        int f = mfeldSuche(basis);
        if (f < 0) { snprintf(grund, gg, "Feld %s ist nicht vereinbart ($DIM fehlt)", basis); return 1; }
        long long i;
        if (mfeldIndex(f, idx, &i, grund, gg) != 0) return 1;
        z->wert = &mfeld[f].el[i].wert; z->istText = &mfeld[f].el[i].istText; z->text = mfeld[f].el[i].text;
        return 0;
    }
    // Mit ;#MAKROLOKAL=1 (Doku 4.31) legt $SET (und das Ziel einer Zeichenkettenfunktion) im Makroaufruf eine lokale Variable an, wenn der
    // Name hier weder lokal noch mit $GLOBAL vereinbart ist; sie verdeckt eine gleichnamige globale Variable oder ein globales Feld.
    // $INC und das Lesen bezeichnen die lokale Variable, sonst die globale, wenn es sie gibt. Im Quelltext ausserhalb eines Makros
    // ist alles global.
    const int lokalAnlegen = (istSet && mMakroLokal && makroKetteTiefe >= 1 && !mGlobalVereinbart(basis));
    if (lokalAnlegen ? (mLokalSuche(basis, 1) >= 0) : (mfeldSuche(basis) >= 0)) { snprintf(grund, gg, "%s: %s ist ein Feld, der Index fehlt", istSet ? "$SET" : "$INC", basis); return 1; }
    int k = lokalAnlegen ? mLokalSuche(basis, 0) : mvarSuche(basis);
    if (!istSet && k < 0) { snprintf(grund, gg, "$INC: Variable %s ist nicht definiert ($SET fehlt)", basis); return 1; }
    if (k < 0 && lokalAnlegen) {
        int nLokal = 0;
        for (int q = 0; q < mvarAnzahl; q++) if (mvar[q].ebene == makroKetteTiefe) nLokal++;
        if (nLokal >= MLOKAL_VAR_MAX) {
            snprintf(grund, gg, "Variable %s: mehr als %d lokale Variablen in einem Makroaufruf (auch die mit $SET angelegten zählen; global mit $GLOBAL)", basis, MLOKAL_VAR_MAX);
            return 1;
        }
        k = mvarAnzahl++;
        STRKOPIE(mvar[k].name, basis);
        mvar[k].ebene = makroKetteTiefe;
        mvar[k].reihe = ++mReihe;
        mvar[k].wert = 0;
        mvar[k].istText = 0;
        mvar[k].text[0] = '\0';
        mvar[k].deklZeile = -1;   // keine $LOCAL-Zeile: ein spaeteres $LOCAL fuer den Namen ist ein Fehler (Doku 4.31)
        mvar[k].deklAusf = 0;
        mvar[k].provisorisch = 0;
    } else if (k < 0) {
        int nGlobal = 0;
        for (int q = 0; q < mvarAnzahl; q++) if (mvar[q].ebene == 0) nGlobal++;
        if (nGlobal >= MVAR_MAX) { snprintf(grund, gg, "mehr als %d Makro-Variablen", MVAR_MAX); return 1; }
        k = mvarAnzahl++;
        STRKOPIE(mvar[k].name, basis);
        mvar[k].ebene = 0;
        mvar[k].reihe = ++mReihe;
        mvar[k].wert = 0;
        mvar[k].istText = 0;
        mvar[k].text[0] = '\0';
        mvar[k].provisorisch = 0;
    }
    mvar[k].provisorisch = 0;   // geschrieben (oder $INC): eine von $GLOBAL angelegte Variable ist nicht mehr unberuehrt
    z->wert = &mvar[k].wert; z->istText = &mvar[k].istText; z->text = mvar[k].text;
    return 0;
}

// Besteht der Wert eines $SET/$DIM ganz aus $CALC(...), wird der Inhalt der Klammer gerechnet (so geht $SET a(0) $CALC($V(a(1))+1))
static void mvarCalcAuspacken(char *ausdruck) {
    size_t n = strlen(ausdruck);
    if (strncmp(ausdruck, "$CALC(", 6) != 0 || n < 8 || ausdruck[n - 1] != ')') return;
    if (makroKlammerEnde(ausdruck + 6) != ausdruck + n - 1) return;   // die Klammer schliesst nicht am Ende
    memmove(ausdruck, ausdruck + 6, n - 7);
    ausdruck[n - 7] = '\0';
}

// $SET name ausdruck / $SET name "text" / $INC name [ausdruck] (name auch als name(index), Doku 4.17); Rueckgabe 0 = ok
static int mvarAusfuehren(int istSet, const char *rest, char *grund, size_t gg) {
    char kopie[256];
    STRKOPIE(kopie, rest);
    char *sv;
    char *name = strtok_r(kopie, " \t", &sv);
    char *ausdr = strtok_r(NULL, " \t", &sv);
    char *mehr = strtok_r(NULL, " \t", &sv);
    int istText = istSet && ausdr != NULL && (ausdr[0] == '"' || ausdr[0] == '\'');   // Text mit Leerzeichen: hinter dem ersten Wort steht mehr
    if (name == NULL || !isalpha((unsigned char)name[0]) || (!istText && mehr != NULL && mehr[0] != ';' && !(ausdr != NULL && ausdr[0] == ';')) ||   // $INC n ; Kommentar: Kommentar mit Leerzeichen ab 1.01-031 erlaubt
        
        (istSet && ausdr == NULL)) {
        snprintf(grund, gg, "%s erwartet <Name> %s (ohne Leerzeichen): %.100s", istSet ? "$SET" : "$INC", istSet ? "<Ausdruck>" : "[<Ausdruck>]", rest);
        return 1;
    }
    {   // Namen (und Index) vorab pruefen, damit ein ungueltiger Name vor allen Textfehlern gemeldet wird
        char basis[40], idx[200];
        if (mfeldZerlegen(name, basis, sizeof(basis), idx, sizeof(idx), grund, gg) < 0) return 1;
    }
    if (istText) {   // $SET name "text": Zeichenkette (Doku 4.12)
        const char *r = rest;
        while (*r == ' ' || *r == '\t') r++;
        r += strlen(name);
        while (*r == ' ' || *r == '\t') r++;
        char q = *r;
        const char *ende = strchr(r + 1, q);
        if (ende == NULL) { snprintf(grund, gg, "$SET %s: Anführungszeichen %c fehlt am Ende des Textes", name, q); return 1; }
        const char *nach = ende + 1;
        while (*nach == ' ' || *nach == '\t') nach++;
        if (*nach != '\0' && *nach != ';') { snprintf(grund, gg, "$SET %s: hinter dem Text darf nur ein Kommentar stehen: %.80s", name, nach); return 1; }
        size_t len = (size_t)(ende - (r + 1));
        char text[MTEXT_PUFFER];   // der Text darf beim Aufloesen von $V(...) laenger werden als die Zeile (Doku 4.12)
        if (len >= sizeof(text)) { snprintf(grund, gg, "$SET %s: Text hat %d Zeichen, erlaubt sind höchstens %d", name, (int)len, MVAR_TEXT_MAX); return 1; }
        memcpy(text, r + 1, len);
        text[len] = '\0';
        if (mvarFund(text) != NULL) {   // $V(...) im Text wird beim Setzen aufgeloest (Verkettung, Doku 4.21; vorher erst bei der Verwendung)
            char g1[300];
            if (mvarErsetzenG(text, sizeof(text), g1, sizeof(g1)) != 0) { snprintf(grund, gg, "$SET %.40s: %.240s", name, g1); return 1; }
            len = strlen(text);
        }
        if (strstr(text, "$CALC") != NULL) {   // $CALC(...), $CALCO(...), $CALCOn(...) im Text, nach dem Aufloesen von $V(...) (Doku 4.22); $1..$9 sind schon eingesetzt
            static char keineParameter[64][MACRO_PARAMETER_LAENGE];
            MakroFehler mf;
            memset(&mf, 0, sizeof(mf));
            makroCalcErsetzen(text, sizeof(text), keineParameter, 0, &mf);
            if (mf.anzahl > 0) { snprintf(grund, gg, "$SET %.40s: %.240s", name, makroFehlerText(&mf)); return 1; }
            len = strlen(text);
        }
        if (len > MVAR_TEXT_MAX) { snprintf(grund, gg, "$SET %s: Text hat %d Zeichen, erlaubt sind höchstens %d", name, (int)len, MVAR_TEXT_MAX); return 1; }
        MZiel z;
        if (mvarZiel(1, name, &z, grund, gg) != 0) return 1;
        *z.istText = 1;
        *z.wert = 0;
        memcpy(z.text, text, len + 1);
        return 0;
    }
    char ausdruck[256] = "1";
    if (ausdr != NULL && ausdr[0] != ';') STRKOPIE(ausdruck, ausdr);
    if (mvarErsetzen(ausdruck, grund, gg) != 0) return 1;
    mvarCalcAuspacken(ausdruck);
    long long v = 0;
    if (makroRechne(ausdruck, &v, grund, gg) != 0) return 1;
    MZiel z;
    if (mvarZiel(istSet, name, &z, grund, gg) != 0) return 1;
    if (!istSet && *z.istText) { snprintf(grund, gg, "$INC: Variable %s enthält einen Text, keine Zahl", name); return 1; }
    if (istSet) { *z.wert = v; *z.istText = 0; } else *z.wert += v;
    return 0;
}

// ----------------------------------------------------------------------------------
// Zeichenkettenfunktionen $SUBSTR $INDEX $UPPER $LOWER $STRCMP $ORD $CHR $VAL $VALO $VALB $VALH (Doku 4.21, 4.22, 4.27, 4.28).
// Form: $<NAME> <ziel> <argument> ...; Texte stehen in Anfuehrungszeichen, Zahlen sind Rechenausdruecke ohne Leerzeichen.
// Die Zeile wird zuerst in Ziel und Argumente zerlegt; danach werden $1..$9, $V(...) und $CALC(...) in jedem Argument aufgeloest.
enum { MSTR_SUBSTR = 1, MSTR_INDEX, MSTR_UPPER, MSTR_LOWER, MSTR_STRCMP, MSTR_ORD, MSTR_CHR, MSTR_VAL, MSTR_VALO, MSTR_VALB, MSTR_VALH, MSTR_ANZAHL = MSTR_VALH };
#define MSTR_ARGS_MAX 3
// art: T = Text in Anfuehrungszeichen, N = Zahl (Rechenausdruck), n = Zahl, darf fehlen (nur als letztes Argument)
static const struct { const char *name; const char *art; const char *form; } mstrTab[MSTR_ANZAHL + 1] = {
    { "", "", "" },
    { "$SUBSTR", "TNn", "$SUBSTR <Ziel> \"<Text>\" <Start> [<Anzahl>]" },
    { "$INDEX",  "TT",  "$INDEX <Ziel> \"<Text>\" \"<Suchtext>\"" },
    { "$UPPER",  "T",   "$UPPER <Ziel> \"<Text>\"" },
    { "$LOWER",  "T",   "$LOWER <Ziel> \"<Text>\"" },
    { "$STRCMP", "TT",  "$STRCMP <Ziel> \"<a>\" \"<b>\"" },
    { "$ORD",    "Tn",  "$ORD <Ziel> \"<Text>\" [<Position>]" },
    { "$CHR",    "N",   "$CHR <Ziel> <Code>" },
    { "$VAL",    "T",   "$VAL <Ziel> \"<Text>\"" },
    { "$VALO",   "T",   "$VALO <Ziel> \"<Text>\"" },
    { "$VALB",   "T",   "$VALB <Ziel> \"<Text>\"" },
    { "$VALH",   "T",   "$VALH <Ziel> \"<Text>\"" },
};

typedef struct { const char *roh; size_t n; int istText; char q; } MStrArg;   // roh: Inhalt ohne Anfuehrungszeichen (Text) bzw. das Wort (Zahl)

// Nummer der Direktive (1 bis MSTR_ANZAHL) oder 0, wenn die Zeile keine Zeichenkettenfunktion ist
static int mstrDirektive(const lineElements *z) {
    for (int k = 1; k <= MSTR_ANZAHL; k++) if (makroErstesWort(z, mstrTab[k].name)) return k;
    return 0;
}

// Zerlegt den Rest der Zeile (hinter dem Schluesselwort) in Ziel und Argumente; Rueckgabe 0 = ok, sonst 1 mit Grund
static int mstrZerlegen(int art, const char *rest, char *ziel, size_t zg, MStrArg *a, int *anz, char *grund, size_t gg) {
    const char *name = mstrTab[art].name;
    const char *form = mstrTab[art].form;
    const char *p = rest;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0' || *p == ';') { snprintf(grund, gg, "%s erwartet ein Ziel und Argumente: %s", name, form); return 1; }
    if (*p == '"' || *p == '\'') { snprintf(grund, gg, "%s: Das Ziel ist ein Variablenname, kein Text in Anführungszeichen: %.40s (Form: %s)", name, p, form); return 1; }
    const char *t0 = p;
    while (*p != '\0' && *p != ' ' && *p != '\t') p++;
    size_t zl = (size_t)(p - t0);
    if (zl >= zg) { snprintf(grund, gg, "%s: Das Ziel ist zu lang: %.40s", name, t0); return 1; }
    memcpy(ziel, t0, zl);
    ziel[zl] = '\0';
    int n = 0;
    const char *k = mstrTab[art].art;
    for (int i = 0; k[i] != '\0'; i++) {
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0' || *p == ';') {
            if (k[i] == 'n') break;   // dieses Argument darf fehlen
            snprintf(grund, gg, "%s %.40s: Es fehlt ein Argument (Form: %s)", name, ziel, form);
            return 1;
        }
        MStrArg *x = &a[n];
        if (*p == '"' || *p == '\'') {
            char q = *p;
            const char *e = strchr(p + 1, q);
            if (e == NULL) { snprintf(grund, gg, "%s %.40s: Anführungszeichen %c fehlt am Ende des Textes", name, ziel, q); return 1; }
            if (k[i] != 'T') { snprintf(grund, gg, "%s %.40s: Argument %d ist eine Zahl, ein Text in Anführungszeichen ist hier nicht erlaubt (Form: %s)", name, ziel, i + 1, form); return 1; }
            x->roh = p + 1;
            x->n = (size_t)(e - (p + 1));
            x->istText = 1;
            x->q = q;
            p = e + 1;
            if (*p != '\0' && *p != ' ' && *p != '\t' && *p != ';') {
                snprintf(grund, gg, "%s %.40s: hinter dem Text darf nur Leerraum oder ein Kommentar stehen: %.40s", name, ziel, p);
                return 1;
            }
        } else {
            const char *t = p;
            while (*p != '\0' && *p != ' ' && *p != '\t') p++;
            if (k[i] == 'T') {
                snprintf(grund, gg, "%s %.40s: Argument %d muss ein Text in Anführungszeichen sein (\"...\" oder '...'), steht aber: %.*s", name, ziel, i + 1, (int)(p - t) > 40 ? 40 : (int)(p - t), t);
                return 1;
            }
            x->roh = t;
            x->n = (size_t)(p - t);
            x->istText = 0;
            x->q = '\0';
        }
        n++;
    }
    while (*p == ' ' || *p == '\t') p++;
    if (*p != '\0' && *p != ';') {
        snprintf(grund, gg, "%s %.40s: hinter dem letzten Argument darf nur ein Kommentar stehen: %.60s (Form: %s)", name, ziel, p, form);
        return 1;
    }
    *anz = n;
    return 0;
}

// Fuehrt die Zeichenkettenfunktion der Zeile z aus. Rueckgabe 0 = ok, 1 = Fehler (Text in grund), 2 = Fehler, schon in f gemeldet.
static int mstrAusfuehren(int art, const lineElements *z, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl,
                          MakroFehler *f, char *grund, size_t gg) {
    const char *name = mstrTab[art].name;
    char ziel[MACRO_PARAMETER_LAENGE];
    MStrArg a[MSTR_ARGS_MAX];
    int anz = 0;
    char g[300];
    if (mstrZerlegen(art, makroRestNachWort(z), ziel, sizeof(ziel), a, &anz, grund, gg) != 0) return 1;
    {   // Ziel: Parameter einsetzen, Namen (und Index) pruefen, damit ein ungueltiges Ziel vor allen Argumentfehlern gemeldet wird
        int vorher = f->anzahl;
        makroFeldParameterErsetzen(ziel, sizeof(ziel), paramArray, paramAnzahl, (f->anzahl == 0) ? f : NULL);
        if (f->anzahl != vorher) return 2;
        char basis[40], idx[200];
        int fz = mfeldZerlegen(ziel, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g));
        if (fz < 0) { snprintf(grund, gg, "%s %.40s: %.200s", name, ziel, g); return 1; }
        if (fz == 0 && mfeldSuche(basis) >= 0) { snprintf(grund, gg, "%s %.40s: %.40s ist ein Feld, der Index fehlt", name, ziel, basis); return 1; }
    }
    char txt[MSTR_ARGS_MAX][MTEXT_PUFFER];   // aufgeloeste Argumente (ein Text darf beim Aufloesen laenger werden als die Zeile, Doku 4.21)
    long long zahl[MSTR_ARGS_MAX] = { 0, 0, 0 };
    for (int i = 0; i < anz; i++) {
        int vorher = f->anzahl;
        memcpy(txt[i], a[i].roh, a[i].n);
        txt[i][a[i].n] = '\0';
        if (makroFeldParameterErsetzen(txt[i], MTEXT_PUFFER, paramArray, paramAnzahl, (f->anzahl == 0) ? f : NULL) != 0) {
            snprintf(grund, gg, "%s %.40s: $V(...): Text passt nicht in den Arbeitspuffer (Argument %d, höchstens %d Zeichen)", name, ziel, i + 1, MTEXT_PUFFER - 1);
            return 1;
        }
        if (f->anzahl != vorher) return 2;
        if (mvarFund(txt[i]) != NULL && mvarErsetzenG(txt[i], MTEXT_PUFFER, g, sizeof(g)) != 0) { snprintf(grund, gg, "%s %.40s: %.200s", name, ziel, g); return 1; }
        if (!a[i].istText) {
            if (strstr(txt[i], "$CALC") != NULL) {   // $CALC(...) mit $V(...) wurde erst jetzt rechenbar
                makroCalcErsetzen(txt[i], MTEXT_PUFFER, paramArray, paramAnzahl, (f->anzahl == 0) ? f : NULL);
                if (f->anzahl != vorher) return 2;
            }
            if (makroRechne(txt[i], &zahl[i], g, sizeof(g)) != 0) {
                snprintf(grund, gg, "%s %.40s: Argument %d (%.60s) ist ungültig: %.140s", name, ziel, i + 1, txt[i], g);
                return 1;
            }
        } else {
            if (strstr(txt[i], "$CALC") != NULL) {   // $CALC... im Text, nach dem Aufloesen von $V(...) (Doku 4.22)
                MakroFehler mf;
                memset(&mf, 0, sizeof(mf));
                makroCalcErsetzen(txt[i], MTEXT_PUFFER, paramArray, paramAnzahl, &mf);
                if (mf.anzahl > 0) { snprintf(grund, gg, "%s %.40s: Argument %d: %.200s", name, ziel, i + 1, makroFehlerText(&mf)); return 1; }
            }
            if (strchr(txt[i], a[i].q) != NULL) {
                snprintf(grund, gg, "%s %.40s: Der Text enthält nach dem Auflösen das Anführungszeichen %c, mit dem er begrenzt ist; das andere Anführungszeichen (%c) nehmen",
                         name, ziel, a[i].q, a[i].q == '"' ? '\'' : '"');
                return 1;
            }
        }
    }

    char erg[MTEXT_PUFFER];
    int ergText = 0;
    long long ergZahl = 0;
    char m[200];   // Fehlertext der Funktion
    erg[0] = '\0';
    switch (art) {
    case MSTR_SUBSTR: {
        long long laenge = (long long)strlen(txt[0]);
        long long start = zahl[1];
        // Start 1 bis Laenge + 1: hinter dem letzten Zeichen beginnt der leere Rest; ein leerer Quelltext (Laenge 0) hat nur Start 1
        if (start < 1 || start > laenge + 1) { snprintf(m, sizeof(m), "Start %lld liegt außerhalb des Textes (erlaubt sind 1 bis %lld, Länge %lld plus 1 für den leeren Rest)", start, laenge + 1, laenge); goto fehler; }
        long long n = laenge - start + 1;
        if (anz > 2) {
            if (zahl[2] < 0) { snprintf(m, sizeof(m), "Anzahl %lld ist kleiner als 0", zahl[2]); goto fehler; }
            if (zahl[2] > laenge - start + 1) {
                snprintf(m, sizeof(m), "Das Ende (Start %lld, Anzahl %lld) liegt hinter dem Textende (Länge %lld)", start, zahl[2], laenge);
                goto fehler;
            }
            n = zahl[2];
        }
        memcpy(erg, txt[0] + start - 1, (size_t)n);
        erg[n] = '\0';
        ergText = 1;
        break;
    }
    case MSTR_INDEX: {
        if (txt[1][0] == '\0') { snprintf(m, sizeof(m), "Der Suchtext ist leer"); goto fehler; }
        const char *p = strstr(txt[0], txt[1]);
        ergZahl = p ? (long long)(p - txt[0]) + 1 : 0;
        break;
    }
    case MSTR_UPPER:
    case MSTR_LOWER:
        for (size_t q = 0; txt[0][q] != '\0'; q++) {
            char c = txt[0][q];
            if (art == MSTR_UPPER && c >= 'a' && c <= 'z') c = (char)(c - 'a' + 'A');
            if (art == MSTR_LOWER && c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            erg[q] = c;
        }
        erg[strlen(txt[0])] = '\0';
        ergText = 1;
        break;
    case MSTR_STRCMP: {
        int c = strcmp(txt[0], txt[1]);   // vergleicht als unsigned char, also byteweise
        ergZahl = (c < 0) ? -1 : (c > 0) ? 1 : 0;
        break;
    }
    case MSTR_ORD: {
        long long laenge = (long long)strlen(txt[0]);
        long long pos = (anz > 1) ? zahl[1] : 1;
        if (pos < 1 || pos > laenge) { snprintf(m, sizeof(m), "Position %lld liegt außerhalb des Textes (Länge %lld)", pos, laenge); goto fehler; }
        ergZahl = (unsigned char)txt[0][pos - 1];
        break;
    }
    case MSTR_CHR:
        if (zahl[0] < 32 || zahl[0] > 126) { snprintf(m, sizeof(m), "Code %lld liegt außerhalb von 32 bis 126", zahl[0]); goto fehler; }
        erg[0] = (char)zahl[0];
        erg[1] = '\0';
        ergText = 1;
        break;
    case MSTR_VAL:
    case MSTR_VALO:
    case MSTR_VALB:
    case MSTR_VALH: {   // $VAL dezimal, $VALO oktal (Doku 4.22), $VALB binaer (Doku 4.27), $VALH hexadezimal (Doku 4.28): gleiche Pruefung, andere Basis
        const int basis = (art == MSTR_VALH) ? 16 : (art == MSTR_VALB) ? 2 : (art == MSTR_VALO) ? 8 : 10;
        const char *s = txt[0];
        int neg = 0;
        if (*s == '-') { neg = 1; s++; }
        long long v = 0;
        int ok = (*s != '\0');
        for (; ok && *s != '\0'; s++) {
            int sc = (unsigned char)*s;
            int d = (sc >= '0' && sc <= '9') ? sc - '0' : (sc >= 'a' && sc <= 'f') ? sc - 'a' + 10 : (sc >= 'A' && sc <= 'F') ? sc - 'A' + 10 : -1;
            if (d < 0 || d >= basis) { ok = 0; break; }
            if (v > (0x7fffffffffffffffLL - d) / basis) { snprintf(m, sizeof(m), "Die Zahl %.40s liegt außerhalb des Zahlenbereichs", txt[0]); goto fehler; }
            v = v * basis + d;
        }
        if (!ok && basis == 2) { snprintf(m, sizeof(m), "Der Text \"%.40s\" ist keine binäre ganze Zahl (erlaubt sind die Ziffern 0 und 1, davor ein einzelnes -)", txt[0]); goto fehler; }
        if (!ok && basis == 16) { snprintf(m, sizeof(m), "Der Text \"%.40s\" ist keine hexadezimale ganze Zahl (erlaubt sind die Ziffern 0 bis 9 und A bis F oder a bis f, davor ein einzelnes -)", txt[0]); goto fehler; }
        if (!ok && basis == 8) { snprintf(m, sizeof(m), "Der Text \"%.40s\" ist keine oktale ganze Zahl (erlaubt sind die Ziffern 0 bis 7, davor ein einzelnes -)", txt[0]); goto fehler; }
        if (!ok) { snprintf(m, sizeof(m), "Der Text \"%.40s\" ist keine ganze Zahl (erlaubt sind Ziffern, davor ein einzelnes -)", txt[0]); goto fehler; }
        ergZahl = neg ? -v : v;
        break;
    }
    default:
        break;
    }
    if (ergText && strlen(erg) > MVAR_TEXT_MAX) {
        snprintf(m, sizeof(m), "Das Ergebnis hat %d Zeichen, erlaubt sind höchstens %d", (int)strlen(erg), MVAR_TEXT_MAX);
        goto fehler;
    }
    {
        MZiel zz;
        if (mvarZiel(1, ziel, &zz, g, sizeof(g)) != 0) { snprintf(grund, gg, "%s %.40s: %.200s", name, ziel, g); return 1; }
        if (ergText) {
            *zz.istText = 1;
            *zz.wert = 0;
            memcpy(zz.text, erg, strlen(erg) + 1);
        } else {
            *zz.istText = 0;
            *zz.wert = ergZahl;
            zz.text[0] = '\0';
        }
    }
    return 0;
fehler:
    snprintf(grund, gg, "%s %.40s: %s", name, ziel, m);
    return 1;
}

// $DIM name anzahl: vereinbart ein Feld mit anzahl Elementen (Index 0 bis anzahl-1), alle Elemente 0 (Doku 4.17); Rueckgabe 0 = ok
static int mfeldVereinbaren(const char *rest, char *grund, size_t gg) {
    char kopie[256];
    STRKOPIE(kopie, rest);
    char *sv;
    char *name = strtok_r(kopie, " \t", &sv);
    char *ausdr = strtok_r(NULL, " \t", &sv);
    char *mehr = strtok_r(NULL, " \t", &sv);
    if (name == NULL || ausdr == NULL || ausdr[0] == ';' || (mehr != NULL && mehr[0] != ';')) {
        snprintf(grund, gg, "$DIM erwartet <Name> <Anzahl> (ohne Leerzeichen): %.100s", rest);
        return 1;
    }
    char basis[40], idx[200];
    int fz = mfeldZerlegen(name, basis, sizeof(basis), idx, sizeof(idx), grund, gg);
    if (fz < 0) return 1;
    if (fz == 1) { snprintf(grund, gg, "$DIM %s: Beim Vereinbaren steht der Name ohne Klammer", name); return 1; }
    char ausdruck[256];
    STRKOPIE(ausdruck, ausdr);
    if (mvarErsetzen(ausdruck, grund, gg) != 0) return 1;
    mvarCalcAuspacken(ausdruck);
    long long n = 0;
    if (makroRechne(ausdruck, &n, grund, gg) != 0) return 1;
    if (n < 1 || n > MFELD_ELEM_MAX) { snprintf(grund, gg, "$DIM %s: Anzahl %lld ist ungültig (erlaubt sind 1 bis %d)", basis, n, MFELD_ELEM_MAX); return 1; }
    // $GLOBAL name, dann $DIM name n: Hat $GLOBAL den Namen nur als Variable mit 0 angelegt und wurde sie nie gesetzt, wird daraus ein Feld
    // (so legt ein Makro ein globales Feld an, Doku 4.31)
    const int glob = (makroKetteTiefe >= 1 && mGlobalVereinbart(basis));
    if (glob) {
        int kv = mvarGlobalSuche(basis);
        if (kv >= 0 && mvar[kv].provisorisch) mvarEntfernen(kv);
    }
    // Mit ;#MAKROLOKAL=1 (Doku 4.31) legt $DIM im Makroaufruf ein lokales Feld an, wenn der Name nicht mit $GLOBAL vereinbart ist
    const int lokalAnlegen = (mMakroLokal && makroKetteTiefe >= 1 && !glob);
    if (lokalAnlegen ? (mLokalSuche(basis, 0) >= 0) : (mvarSuche(basis) >= 0)) { snprintf(grund, gg, "$DIM %s: Der Name ist schon eine einfache Variable", basis); return 1; }
    int f = lokalAnlegen ? mLokalSuche(basis, 1) : mfeldSuche(basis);
    if (f >= 0) {
        if (mfeld[f].anzahl != (int)n) { snprintf(grund, gg, "$DIM %s: Anzahl %lld, früher vereinbart mit %d", basis, n, mfeld[f].anzahl); return 1; }
        memset(mfeld[f].el, 0, (size_t)n * sizeof(MVarWert));   // gleiche Größe: alle Elemente zurück auf 0
        return 0;
    }
    if (lokalAnlegen) {
        int nLokalF = 0;
        for (int q = 0; q < mfeldAnzahl; q++) if (mfeld[q].ebene == makroKetteTiefe) nLokalF++;
        if (nLokalF >= MLOKAL_FELD_MAX) {
            snprintf(grund, gg, "$DIM %s: mehr als %d lokale Felder in einem Makroaufruf (auch die mit $LOCAL angelegten zählen; global mit $GLOBAL)", basis, MLOKAL_FELD_MAX);
            return 1;
        }
        MVarWert *elL = (MVarWert *)calloc((size_t)n, sizeof(MVarWert));
        if (!elL) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
        f = mfeldAnzahl++;
        STRKOPIE(mfeld[f].name, basis);
        mfeld[f].ebene = makroKetteTiefe;
        mfeld[f].reihe = ++mReihe;
        mfeld[f].anzahl = (int)n;
        mfeld[f].el = elL;
        mfeld[f].deklZeile = -1;   // keine $LOCAL-Zeile (Doku 4.31)
        mfeld[f].deklAusf = 0;
        return 0;
    }
    int nGlobalF = 0;
    for (int q = 0; q < mfeldAnzahl; q++) if (mfeld[q].ebene == 0) nGlobalF++;
    if (nGlobalF >= MFELD_MAX) { snprintf(grund, gg, "mehr als %d Felder", MFELD_MAX); return 1; }
    MVarWert *el = (MVarWert *)calloc((size_t)n, sizeof(MVarWert));
    if (!el) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    f = mfeldAnzahl++;
    STRKOPIE(mfeld[f].name, basis);
    mfeld[f].ebene = 0;
    mfeld[f].reihe = ++mReihe;
    mfeld[f].anzahl = (int)n;
    mfeld[f].el = el;
    return 0;
}

// $LOCAL <name> | <name>(<anzahl>) ...: vereinbart lokale Variablen und Felder des laufenden Makroaufrufs, alle mit Wert 0
// (Doku 4.20); mehrere Namen auf einer Zeile erlaubt. Rueckgabe 0 = ok, sonst Fehlertext in grund.
// zeile: Index der $LOCAL-Zeile im Makrotext. Wird dieselbe Zeile in einem weiteren Durchlauf einer $WHILE-Schleife ausgefuehrt
// (ab c82ass 1.01-010), vereinbart sie ihre Namen erneut: Die Werte sind wieder 0, ein Feld mit anderer Anzahl wird neu angelegt.
// Ein Name, den eine andere Zeile (oder dieselbe Zeile zweimal) schon vereinbart hat, bleibt ein Fehler.
static unsigned mlokalAusfNr = 0;   // Nummer der laufenden Ausfuehrung einer $LOCAL-Zeile (trennt einen weiteren Durchlauf von einem doppelten Namen)

static int mlokalVereinbaren(const char *rest, char *grund, size_t gg, int zeile) {
    if (makroKetteTiefe < 1) { snprintf(grund, gg, "$LOCAL steht außerhalb eines Makroaufrufs"); return 1; }
    char kopie[512];
    STRKOPIE(kopie, rest);
    char *sv;
    char *tok = strtok_r(kopie, " \t", &sv);
    int anzahlNamen = 0;
    const unsigned meine = ++mlokalAusfNr;
    while (tok != NULL && tok[0] != ';') {
        anzahlNamen++;
        char basis[40], idx[200];
        int fz = mfeldZerlegen(tok, basis, sizeof(basis), idx, sizeof(idx), grund, gg);
        if (fz < 0) return 1;
        if (mGlobalVereinbart(basis)) {
            snprintf(grund, gg, "$LOCAL %s: Der Name ist in diesem Makroaufruf schon mit $GLOBAL als global vereinbart", basis);
            return 1;
        }
        const int lv = mLokalSuche(basis, 0), lf = mLokalSuche(basis, 1);
        int erneut = 0;   // 1: dieselbe Zeile hat den Namen in einem frueheren Durchlauf vereinbart
        if (lv >= 0 || lf >= 0) {
            erneut = (fz == 0 && lv >= 0 && mvar[lv].deklZeile == zeile && mvar[lv].deklAusf != meine) ||
                     (fz == 1 && lf >= 0 && mfeld[lf].deklZeile == zeile && mfeld[lf].deklAusf != meine);
            if (!erneut) {
                snprintf(grund, gg, "$LOCAL %s: Der Name ist in diesem Makroaufruf schon lokal vereinbart", basis);
                return 1;
            }
        }
        int nVar = 0, nFeld = 0;
        for (int q = 0; q < mvarAnzahl; q++) if (mvar[q].ebene == makroKetteTiefe) nVar++;
        for (int q = 0; q < mfeldAnzahl; q++) if (mfeld[q].ebene == makroKetteTiefe) nFeld++;
        if (fz == 0) {
            if (erneut) {
                mvar[lv].wert = 0;
                mvar[lv].istText = 0;
                mvar[lv].text[0] = '\0';
                mvar[lv].deklAusf = meine;
            } else {
                if (nVar >= MLOKAL_VAR_MAX) { snprintf(grund, gg, "$LOCAL %s: mehr als %d lokale Variablen in einem Makroaufruf (auch die mit $SET angelegten zählen)", basis, MLOKAL_VAR_MAX); return 1; }
                int k = mvarAnzahl++;
                STRKOPIE(mvar[k].name, basis);
                mvar[k].ebene = makroKetteTiefe;
                mvar[k].reihe = ++mReihe;
                mvar[k].wert = 0;
                mvar[k].istText = 0;
                mvar[k].text[0] = '\0';
                mvar[k].deklZeile = zeile;
                mvar[k].deklAusf = meine;
                mvar[k].provisorisch = 0;
            }
        } else {
            char ausdruck[256];
            STRKOPIE(ausdruck, idx);
            if (mvarErsetzen(ausdruck, grund, gg) != 0) return 1;
            mvarCalcAuspacken(ausdruck);
            long long n = 0;
            if (makroRechne(ausdruck, &n, grund, gg) != 0) return 1;
            if (n < 1 || n > MFELD_ELEM_MAX) { snprintf(grund, gg, "$LOCAL %s: Anzahl %lld ist ungültig (erlaubt sind 1 bis %d)", basis, n, MFELD_ELEM_MAX); return 1; }
            if (erneut) {
                if (mfeld[lf].anzahl == (int)n) {
                    memset(mfeld[lf].el, 0, (size_t)n * sizeof(MVarWert));   // gleiche Anzahl: alle Elemente zurueck auf 0
                } else {
                    MVarWert *el = (MVarWert *)calloc((size_t)n, sizeof(MVarWert));
                    if (!el) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
                    free(mfeld[lf].el);
                    mfeld[lf].el = el;
                    mfeld[lf].anzahl = (int)n;
                }
                mfeld[lf].deklAusf = meine;
            } else {
                if (nFeld >= MLOKAL_FELD_MAX) { snprintf(grund, gg, "$LOCAL %s: mehr als %d lokale Felder in einem Makroaufruf (auch die mit $DIM angelegten zählen)", basis, MLOKAL_FELD_MAX); return 1; }
                MVarWert *el = (MVarWert *)calloc((size_t)n, sizeof(MVarWert));
                if (!el) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
                int f = mfeldAnzahl++;
                STRKOPIE(mfeld[f].name, basis);
                mfeld[f].ebene = makroKetteTiefe;
                mfeld[f].reihe = ++mReihe;
                mfeld[f].anzahl = (int)n;
                mfeld[f].el = el;
                mfeld[f].deklZeile = zeile;
                mfeld[f].deklAusf = meine;
            }
        }
        tok = strtok_r(NULL, " \t", &sv);
    }
    if (anzahlNamen == 0) { snprintf(grund, gg, "$LOCAL erwartet mindestens einen Namen: $LOCAL <Name> [<Name>(<Anzahl>)] ..."); return 1; }
    return 0;
}

// $GLOBAL <name> ...: vereinbart einfache Variablen und Felder im laufenden Makroaufruf ausdruecklich als global (Gegenstueck zu $LOCAL,
// Doku 4.31). Gibt es den Namen noch nicht, entsteht eine globale Variable mit dem Wert 0 (ein Feld legt $DIM an; folgt $DIM, bevor die
// Variable gesetzt wurde, wird sie zum Feld). Derselbe Name darf im Aufruf mehrfach mit $GLOBAL stehen; ein Name, der im Aufruf schon
// lokal angelegt oder vereinbart ist, ist ein Fehler. Ohne ;#MAKROLOKAL=1 wirkt $GLOBAL genauso (Variablen sind dann ohnehin global).
// Rueckgabe 0 = ok, sonst Fehlertext in grund.
static int mglobalVereinbaren(const char *rest, char *grund, size_t gg) {
    if (makroKetteTiefe < 1) { snprintf(grund, gg, "$GLOBAL steht außerhalb eines Makroaufrufs"); return 1; }
    char kopie[512];
    STRKOPIE(kopie, rest);
    char *sv;
    char *tok = strtok_r(kopie, " \t", &sv);
    int anzahlNamen = 0;
    while (tok != NULL && tok[0] != ';') {
        anzahlNamen++;
        char basis[40], idx[200];
        int fz = mfeldZerlegen(tok, basis, sizeof(basis), idx, sizeof(idx), grund, gg);
        if (fz < 0) return 1;
        if (fz == 1) { snprintf(grund, gg, "$GLOBAL %s: Der Name steht ohne Klammer (ein Feld legt $DIM an)", tok); return 1; }
        if (mLokalSuche(basis, 0) >= 0 || mLokalSuche(basis, 1) >= 0) {
            snprintf(grund, gg, "$GLOBAL %s: Der Name ist in diesem Makroaufruf schon lokal angelegt oder vereinbart", basis);
            return 1;
        }
        if (!mGlobalVereinbart(basis)) {
            int nDieser = 0;
            for (int q = 0; q < mglobAnzahl; q++) if (mglob[q].ebene == makroKetteTiefe) nDieser++;
            if (nDieser >= MGLOB_JE_AUFRUF) { snprintf(grund, gg, "$GLOBAL %s: mehr als %d Namen mit $GLOBAL in einem Makroaufruf", basis, MGLOB_JE_AUFRUF); return 1; }
            if (mvarGlobalSuche(basis) < 0 && mfeldGlobalSuche(basis) < 0) {
                int nGlobal = 0;
                for (int q = 0; q < mvarAnzahl; q++) if (mvar[q].ebene == 0) nGlobal++;
                if (nGlobal >= MVAR_MAX) { snprintf(grund, gg, "$GLOBAL %s: mehr als %d Makro-Variablen", basis, MVAR_MAX); return 1; }
                int k = mvarAnzahl++;
                STRKOPIE(mvar[k].name, basis);
                mvar[k].ebene = 0;
                mvar[k].reihe = ++mReihe;
                mvar[k].wert = 0;
                mvar[k].istText = 0;
                mvar[k].text[0] = '\0';
                mvar[k].deklZeile = 0;
                mvar[k].deklAusf = 0;
                mvar[k].provisorisch = 1;
            }
            STRKOPIE(mglob[mglobAnzahl].name, basis);
            mglob[mglobAnzahl].ebene = makroKetteTiefe;
            mglobAnzahl++;
        }
        tok = strtok_r(NULL, " \t", &sv);
    }
    if (anzahlNamen == 0) { snprintf(grund, gg, "$GLOBAL erwartet mindestens einen Namen: $GLOBAL <Name> [<Name>] ..."); return 1; }
    return 0;
}

// Verwirft alle lokalen Variablen und Felder der Ebene (am Ende eines Makroaufrufs, auch nach einem Fehler oder $EXIT)
static void mlokalVerwerfen(int ebene) {
    int wg = 0;
    for (int k = 0; k < mglobAnzahl; k++) if (mglob[k].ebene != ebene) { if (wg != k) mglob[wg] = mglob[k]; wg++; }   // die $GLOBAL-Namen des Aufrufs enden mit ihm
    mglobAnzahl = wg;
    int w = 0;
    for (int k = 0; k < mvarAnzahl; k++) if (mvar[k].ebene != ebene) { if (w != k) mvar[w] = mvar[k]; w++; }
    mvarAnzahl = w;
    w = 0;
    for (int k = 0; k < mfeldAnzahl; k++) {
        if (mfeld[k].ebene == ebene) { free(mfeld[k].el); continue; }
        if (w != k) mfeld[w] = mfeld[k];
        w++;
    }
    mfeldAnzahl = w;
}

// ----------------------------------------------------------------------------------
// Hilfen zur Fehlersuche im Makro: $NOTE, $TRACE, $DUMP (Doku 4.24). Sie beobachten nur: kein Code, keine Aenderung einer Variablen,
// keine Warnung, kein Einfluss auf den Rueckgabecode. Die Ausgabe geht auf STDERR (gruen), nicht ins Listing, .dmp, .log und .test.
// Die Puffer haben MACRO_PARAMETER_LAENGE (256) Zeichen; wirksam sind darum hoechstens 255 Zeichen je Text (die Doku nennt 300).
// Der Wert einer Textvariablen (bis MVAR_TEXT_MAX Zeichen) wird in $TRACE und $DUMP auf 297 Zeichen gekuerzt (wertText mit 300 Byte): nur Anzeige.
#define SPUR_ZEILEN_MAX 10000   // hoechstens so viele Spurzeilen je Lauf
#define SPUR_TEXT_MAX 300       // hoechstens so viele Zeichen je Text einer Meldung (die Puffer sind kuerzer, siehe oben)
#define DUMP_ZIELE_MAX 128      // eine Zeile hat hoechstens 255 Zeichen, also hoechstens 128 Ziele
#define DUMP_PRO_ZEILE 16       // Elemente eines Feldes je Ausgabezeile

static int spurEbene = 0;        // 0 = Spur aus, sonst die Tiefe der Aufrufkette des Aufrufs, der $TRACE ON ausgefuehrt hat
static int spurGesamt = 0;       // bisher ausgegebene Spurzeilen dieses Laufs
static int spurAbgebrochen = 0;  // die Zeile "Ablaufspur ... abgebrochen" ist schon ausgegeben

// Eine Zeile auf STDERR, gruen; vorher STDOUT leeren, damit die Reihenfolge zum Listing passt.
// Ein Probelauf fuer adr/abstand, den der Aufrufer mit --probeausgabe gestartet hat (versteckte Option --adrdbg=), legt die Zeile
// statt auf STDERR in die Debugdatei; der Aufrufer zeigt sie nach dem Probelauf an (Doku 4.24, ab c82ass 1.01-021).
static void makroAusgabeZeile(const char *zeile) {
    if (adrDebugZeile(zeile)) return;
    fflush(stdout);
    fprintf(stderr, "%s%s%s\n", _gruen, zeile, _normal);
}

// "Hinweis: Makro <Name> (<Datei>:<Zeile>): <text>"; <Zeile> ist die Quelltextzeile des aeussersten Aufrufs
// Mit --pass0 steht nur <text> da (wie das sed 's/^Hinweis: [^(]*([^)]*): //' der Shell-Kette; Doku 3.1d)
static void makroHinweis(const char *makro, const char *text) {
    char zeile[2048];
    if (nurPass0Aktiv) snprintf(zeile, sizeof(zeile), "%s", text);
    else if (makroKetteTiefe == 0) snprintf(zeile, sizeof(zeile), "Hinweis: Quelltext (%s:%d): %s", qDatei(pass0AeussereZeile), qZeile(pass0AeussereZeile), text);   // Quelltextmodus (Doku 4.1)
    else snprintf(zeile, sizeof(zeile), "Hinweis: Makro %.60s (%s:%d): %s", makro, qDatei(pass0AeussereZeile), qZeile(pass0AeussereZeile), text);
    makroAusgabeZeile(zeile);
}

// Loest $V(...) und danach $CALC(...) in text (mindestens MACRO_PARAMETER_LAENGE Zeichen gross) auf; 0 = ok, sonst Fehlertext in grund
// (text bleibt dann unveraendert)
static int makroTextAufloesen(char *text, char *grund, size_t gg) {
    char arbeit[MACRO_PARAMETER_LAENGE];
    STRKOPIE(arbeit, text);
    if (mvarFund(arbeit) != NULL && mvarErsetzen(arbeit, grund, gg) != 0) return 1;
    if (strstr(arbeit, "$CALC") != NULL) {
        static char keineParameter[64][MACRO_PARAMETER_LAENGE];
        MakroFehler *mf = (MakroFehler *)calloc(1, sizeof(MakroFehler));   // gross: nicht auf den Stapel (die Auswertung ruft sich ueber verschachtelte Aufrufe selbst auf)
        if (!mf) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
        makroCalcErsetzen(arbeit, sizeof(arbeit), keineParameter, 0, mf);
        if (mf->anzahl > 0) {
            snprintf(grund, gg, "%.240s", makroFehlerText(mf));
            free(mf);
            return 1;
        }
        free(mf);
    }
    strkopiere(text, MACRO_PARAMETER_LAENGE, arbeit);
    return 0;
}

// $NOTE <text>: gibt den Text aus (Doku 4.24); der Text reicht bis zum Zeilenende, auch ein ; gehoert dazu
static void makroNote(const char *makro, const lineElements *z, MakroFehler *f) {
    const char *t = makroRestNachWort(z);
    while (*t == ' ' || *t == '\t') t++;
    char text[MACRO_PARAMETER_LAENGE], grund[300];
    STRKOPIE(text, t);
    if (makroTextAufloesen(text, grund, sizeof(grund)) != 0) {
        makroMelde(f, makro, "$NOTE: %s", grund);
        return;
    }
    if (strlen(text) > SPUR_TEXT_MAX) text[SPUR_TEXT_MAX] = '\0';
    makroHinweis(makro, text);
}

// $WARN <text> und $ERROR <text> (Doku 4.5): ein $V(...) im Text wird ersetzt (ab c82ass 1.01-005); ohne $V( bleibt der Text wie er ist
static void makroWarnError(const char *makro, const lineElements *z, int istErr, MakroFehler *f) {
    const char *t = makroRestNachWort(z);
    while (*t == ' ' || *t == '\t') t++;
    char text[MACRO_PARAMETER_LAENGE], grund[300];
    STRKOPIE(text, t);
    if (mvarFund(text) != NULL && makroTextAufloesen(text, grund, sizeof(grund)) != 0) {
        makroMelde(f, makro, "%s: %s", istErr ? "$ERROR" : "$WARN", grund);
        return;
    }
    if (istErr) makroMelde(f, makro, "$ERROR: %.300s", text);
    else if (makroKetteTiefe == 0) PRINT_WARNUNG("Quelltext (Zeile %s): $WARN %s", qOrt(pass0AeussereZeile), text);   // Quelltextmodus (Doku 4.1)
    else PRINT_WARNUNG("Makro %s: $WARN %s", makro, text);
}

// $TRACE ON / $TRACE OFF: nur in Grossbuchstaben, dahinter hoechstens ein Kommentar. Die Spur gilt fuer den laufenden Aufruf und alle
// Makros, die er aufruft; sie endet mit $TRACE OFF oder mit dem Ende des Aufrufs, der sie eingeschaltet hat (loeseMacroAuf).
static void makroTrace(const char *makro, const lineElements *z, MakroFehler *f) {
    const char *p = makroRestNachWort(z);
    while (*p == ' ' || *p == '\t') p++;
    const char *w0 = p;
    while (*p != '\0' && *p != ' ' && *p != '\t' && *p != ';') p++;
    size_t wl = (size_t)(p - w0);
    while (*p == ' ' || *p == '\t') p++;
    int ende = (*p == '\0' || *p == ';');
    if (ende && wl == 2 && strncmp(w0, "ON", 2) == 0) {
        if (spurEbene == 0) spurEbene = makroKetteTiefe;   // bei laufender Spur keine Aenderung
    } else if (ende && wl == 3 && strncmp(w0, "OFF", 3) == 0) {
        spurEbene = 0;
    } else {
        makroMelde(f, makro, "$TRACE: ON oder OFF erwartet");
    }
}

// ---- Ablaufspur ----

// Zeilentext fuer die Spur: Leerraum vorn weg, Kommentar (; ausserhalb von Anfuehrungszeichen) weg, Leerraum ausserhalb von
// Anfuehrungszeichen zu einem Leerzeichen, Ende abgeschnitten. Ein Anfuehrungszeichen ohne Gegenstueck gilt als gewoehnliches Zeichen.
static void spurNormalisieren(const char *q, char *aus, size_t an) {
    size_t n = 0;
    int leer = 1;   // zuletzt Leerraum (oder Zeilenanfang)
    while (*q == ' ' || *q == '\t') q++;
    while (*q != '\0' && n + 1 < an) {
        char c = *q;
        if (c == '"' || c == '\'') {
            const char *e = strchr(q + 1, c);
            if (e != NULL) {   // Text in Anfuehrungszeichen unveraendert uebernehmen
                for (; q <= e && n + 1 < an; q++) aus[n++] = *q;
                leer = 0;
                continue;
            }
        }
        if (c == ';') break;
        if (c == ' ' || c == '\t') {
            if (!leer) { aus[n++] = ' '; leer = 1; }
            q++;
            continue;
        }
        aus[n++] = c;
        leer = 0;
        q++;
    }
    while (n > 0 && aus[n - 1] == ' ') n--;
    aus[n] = '\0';
}

// Loest $V(...) und $CALC(...) im Spurtext auf (auf einer Kopie: misslingt es, bleibt der Text unaufgeloest). Bei den
// Zeichenkettenfunktionen sind die Aufrufparameter ($1 bis $9) noch nicht ersetzt (mitParametern = 1).
static void spurAufloesen(char *text, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, int mitParametern) {
    char arbeit[MACRO_PARAMETER_LAENGE], grund[300];
    STRKOPIE(arbeit, text);
    if (mitParametern) makroFeldParameterErsetzen(arbeit, MACRO_PARAMETER_LAENGE, paramArray, paramAnzahl, NULL);
    if (makroTextAufloesen(arbeit, grund, sizeof(grund)) == 0) strkopiere(text, MACRO_PARAMETER_LAENGE, arbeit);
}

// Eine Spurzeile ausgeben: "<Einrueckung>Spur <Makro> <nr>: <text>", Einrueckung 2 Leerzeichen je Aufruftiefe seit dem Einschalten.
// Nach SPUR_ZEILEN_MAX Zeilen folgt einmal der Hinweis, danach entfallen weitere Spurzeilen.
static void spurAusgabe(const char *makro, int nr, const char *text) {
    if (spurAbgebrochen) return;
    if (spurGesamt >= SPUR_ZEILEN_MAX) {
        spurAbgebrochen = 1;
        makroAusgabeZeile("Hinweis: Ablaufspur nach 10000 Zeilen abgebrochen, weitere Spurzeilen entfallen");
        return;
    }
    spurGesamt++;
    int einr = 2 * (makroKetteTiefe - spurEbene);
    if (einr < 0) einr = 0;
    char zeile[1700];
    snprintfGekuerzt(zeile, sizeof(zeile), "%*sSpur %.60s %d: %s", einr, "", makro, nr, text);
    makroAusgabeZeile(zeile);
}

// Zaehlt die Zeile mit (*nr) und gibt sie aus: "<zeile> => <wirkung>", ohne Wirkung nur "<zeile>"
static void spurSchreibe(const char *makro, int *nr, const char *zeile, const char *wirkung) {
    char text[1400];
    if (wirkung != NULL) snprintf(text, sizeof(text), "%s => %s", zeile, wirkung);
    else snprintf(text, sizeof(text), "%s", zeile);
    (*nr)++;
    spurAusgabe(makro, *nr, text);
}

// Bedingungszeile ($IF, $ELIF, $WHILE) mit schon aufgeloesten Variablen
static void spurBedingung(const char *makro, int *nr, const char *zeile, const char *wirkung) {
    char text[MACRO_PARAMETER_LAENGE];
    spurNormalisieren(zeile, text, sizeof(text));
    spurSchreibe(makro, nr, text, wirkung);
}

// Wert als Text fuer die Ausgabe: Zahl dezimal, Text in Anfuehrungszeichen.
// Passt der Text nicht in den Puffer (an Byte), wird er gekuerzt und das schliessende Anfuehrungszeichen entfaellt (nur Anzeige, gewollt).
// Das Kuerzen geschieht hier von Hand und nicht mit snprintf, weil gcc (-Wformat-truncation) die gewollte Kuerzung als Warnung meldet;
// das Ergebnis ist Zeichen fuer Zeichen dasselbe wie bei snprintf(aus, an, "\"%s\"", text).
static void wertText(int istText, long long wert, const char *text, char *aus, size_t an) {
    if (!istText) {
        snprintf(aus, an, "%lld", wert);
        return;
    }
    if (an == 0) return;
    size_t o = 0;
    if (o + 1 < an) aus[o++] = '"';
    while (*text != '\0' && o + 1 < an) aus[o++] = *text++;
    if (*text == '\0' && o + 1 < an) aus[o++] = '"';
    aus[o] = '\0';
}

// Stand eines Ziels (einfache Variable oder Feldelement) als Text; 0 = gefunden, 1 = es gibt das Ziel nicht (oder nicht auswertbar)
static int spurZielStand(const char *ziel, char *aus, size_t an, int *lokal) {
    char basis[40], idx[200], g[300];
    int fz = mfeldZerlegen(ziel, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g));
    if (fz < 0) return 1;
    if (fz == 1) {
        int fe = mfeldSuche(basis);
        long long i = 0;
        if (fe < 0 || mfeldIndex(fe, idx, &i, g, sizeof(g)) != 0) return 1;
        wertText(mfeld[fe].el[i].istText, mfeld[fe].el[i].wert, mfeld[fe].el[i].text, aus, an);
        *lokal = mfeld[fe].ebene > 0;
        return 0;
    }
    int k = mvarSuche(basis);
    if (k < 0) return 1;
    wertText(mvar[k].istText, mvar[k].wert, mvar[k].text, aus, an);
    *lokal = mvar[k].ebene > 0;
    return 0;
}

// Vorbereitung einer Spurzeile VOR der Ausfuehrung: der Zeilentext mit den Werten, mit denen gerechnet wird, und bei Anweisungen, die
// ein Ziel setzen, der alte Stand des Ziels.
typedef struct {
    char text[MACRO_PARAMETER_LAENGE];   // Zeilentext, aufgeloest
    char ziel[200];                      // Ziel (zweites Wort des Zeilentextes), nur bei zielSetzend
    char alt[300];                       // Stand des Ziels vor der Ausfuehrung
    int hatAlt;                          // 0 = das Ziel gab es vorher nicht
} SpurVor;

static void spurVorbereiten(const lineElements *z, int mitParametern, int zielSetzend,
                            char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, SpurVor *v) {
    spurNormalisieren(z->sp1, v->text, sizeof(v->text));
    spurAufloesen(v->text, paramArray, paramAnzahl, mitParametern);
    v->ziel[0] = '\0';
    v->alt[0] = '\0';
    v->hatAlt = 0;
    if (zielSetzend) {
        const char *p = v->text;
        while (*p != '\0' && *p != ' ') p++;   // das erste Wort ($SET, $INC, $SUBSTR ...) ueberspringen
        while (*p == ' ') p++;
        const char *z0 = p;
        while (*p != '\0' && *p != ' ') p++;
        snprintfGekuerzt(v->ziel, sizeof(v->ziel), "%.*s", (int)(p - z0), z0);
        int lokal = 0;
        v->hatAlt = (spurZielStand(v->ziel, v->alt, sizeof(v->alt), &lokal) == 0);
        // Mit ;#MAKROLOKAL=1 legt $SET (und das Ziel einer Zeichenkettenfunktion) im Makroaufruf eine neue lokale Variable an, wenn der Name
        // hier weder lokal noch mit $GLOBAL vereinbart ist: der Stand einer verdeckten globalen Variablen ist dann nicht der alte Stand
        // (Anzeige "(neu)"). $INC bleibt ausgenommen: es erhoeht die lokale, sonst die globale Variable.
        if (v->hatAlt && mMakroLokal && makroKetteTiefe >= 1) {
            const char *w = v->text;
            while (*w == ' ') w++;
            char basis[40], idx[200], g[300];
            if (strncmp(w, "$INC", 4) != 0 &&
                mfeldZerlegen(v->ziel, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g)) == 0 &&
                mLokalSuche(basis, 0) < 0 && !mGlobalVereinbart(basis)) v->hatAlt = 0;
        }
    }
}

// Wirkung einer Anweisung, die ein Ziel setzt: "<ziel>: <alt> -> <neu>", bei einem lokalen Ziel mit " (lokal)"; neues Ziel: alt = (neu)
static void spurZielWirkung(const SpurVor *v, char *aus, size_t an) {
    char neu[300];
    int lokal = 0;
    if (spurZielStand(v->ziel, neu, sizeof(neu), &lokal) != 0) snprintf(neu, sizeof(neu), "?");
    // Genauigkeiten: ein Text hat hoechstens MVAR_TEXT_MAX + 2 Zeichen (mit Anfuehrungszeichen), ein Ziel hoechstens Name (39) und Index;
    // zusammen hoechstens 555 Zeichen, der Puffer des Aufrufers hat 640
    snprintf(aus, an, "%.120s: %.210s -> %.210s%s", v->ziel, v->hatAlt ? v->alt : "(neu)", neu, lokal ? " (lokal)" : "");
}

// Text hinter dem ersten Wort der Zeile (ohne fuehrenden Leerraum)
static const char *spurRest(const char *text) {
    const char *p = text;
    while (*p != '\0' && *p != ' ') p++;
    while (*p == ' ') p++;
    return p;
}

// Wirkung von $LOCAL: "lokal vereinbart: <namen>", ein Feld als name(anzahl)
static void spurLokalWirkung(const char *text, char *aus, size_t an) {
    char kopie[MACRO_PARAMETER_LAENGE];
    STRKOPIE(kopie, spurRest(text));
    snprintf(aus, an, "lokal vereinbart:");
    char *sv = NULL;
    for (char *tok = strtok_r(kopie, " ", &sv); tok != NULL; tok = strtok_r(NULL, " ", &sv)) {
        char basis[40], idx[200], g[300];
        size_t n = strlen(aus);
        int fz = mfeldZerlegen(tok, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g));
        int fe = (fz == 1) ? mLokalSuche(basis, 1) : -1;
        if (fe >= 0) snprintfGekuerzt(aus + n, an - n, " %s(%d)", basis, mfeld[fe].anzahl);
        else snprintfGekuerzt(aus + n, an - n, " %.60s", fz >= 0 ? basis : tok);
    }
}

// Wirkung von $GLOBAL: "global vereinbart: <namen>"
static void spurGlobalWirkung(const char *text, char *aus, size_t an) {
    char kopie[MACRO_PARAMETER_LAENGE];
    STRKOPIE(kopie, spurRest(text));
    snprintf(aus, an, "global vereinbart:");
    char *sv = NULL;
    for (char *tok = strtok_r(kopie, " ", &sv); tok != NULL && tok[0] != ';'; tok = strtok_r(NULL, " ", &sv)) {
        size_t n = strlen(aus);
        snprintfGekuerzt(aus + n, an - n, " %.60s", tok);
    }
}

// Wirkung von $DIM: "Feld <name>(<anzahl>) vereinbart"
static void spurDimWirkung(const char *text, char *aus, size_t an) {
    char kopie[MACRO_PARAMETER_LAENGE], basis[40], idx[200], g[300];
    STRKOPIE(kopie, spurRest(text));
    char *sv = NULL;
    char *tok = strtok_r(kopie, " ", &sv);
    int fe = -1;
    if (tok != NULL && mfeldZerlegen(tok, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g)) >= 0) fe = mfeldSuche(basis);
    if (fe >= 0) snprintf(aus, an, "Feld %s(%d) vereinbart", mfeld[fe].name, mfeld[fe].anzahl);
    else snprintf(aus, an, "Feld vereinbart");
}

// Text einer erzeugten Zeile: Marke, Operation und Operand ohne leere Felder, ohne Kommentar; $CALC zuletzt aufgeloest
static void spurErzeugtText(const lineElements *z, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, char *aus, size_t an) {
    const char *fv[3] = { z->sp1, z->sp2, z->sp3 };
    size_t n = 0;
    aus[0] = '\0';
    for (int q = 0; q < 3; q++) {
        if (fv[q][0] == '\0') continue;
        n += (size_t)snprintf(aus + n, an - n, "%s%s", n > 0 ? " " : "", fv[q]);
        if (n >= an) { n = an - 1; break; }
    }
    if (strstr(aus, "$CALC") != NULL) makroCalcErsetzen(aus, an, paramArray, paramAnzahl, NULL);
    if (strlen(aus) > SPUR_TEXT_MAX) aus[SPUR_TEXT_MAX] = '\0';
}

// 1, wenn die erzeugte Zeile in die Spur gehoert: keine Kommentar-, Leer- oder Fehlerzeile (die MEND-Zeile ist schon ein Kommentar)
static int spurErzeugtZeile(const lineElements *z) {
    if (z->sp1[0] == ';') return 0;
    return z->sp1[0] != '\0' || z->sp2[0] != '\0' || z->sp3[0] != '\0';
}

// "ruft <Name> <parameter>": Aufruf eines Makros, vor dem Aufloesen des Aufrufs ausgegeben (danach folgt dessen Spur, eine Stufe eingerueckt)
static void spurRuft(const char *makro, int *nr, const lineElements *z) {
    char text[2 * MACRO_PARAMETER_LAENGE + 16];
    if (z->sp3[0] != '\0') snprintf(text, sizeof(text), "ruft %s %s", z->sp2, z->sp3);
    else snprintf(text, sizeof(text), "ruft %s", z->sp2);
    spurSchreibe(makro, nr, text, NULL);
}

// "erzeugt <zeile>": eine Zeile, die in den Quelltext kommt (ohne Kommentar, $CALC zuletzt aufgeloest)
static void spurErzeugt(const char *makro, int *nr, const lineElements *z, char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl) {
    char t[800], text[900];
    spurErzeugtText(z, paramArray, paramAnzahl, t, sizeof(t));
    snprintf(text, sizeof(text), "erzeugt %s", t);
    spurSchreibe(makro, nr, text, NULL);
}

// $ENDWHILE: die Bedingung des $WHILE (schon aufgeloest und normalisiert, beginnt mit "$WHILE") mit den jetzigen Werten, aber mit "$ENDWHILE" davor
static void spurEndWhile(const char *makro, int *nr, const char *norm, const char *wirkung) {
    char text[MACRO_PARAMETER_LAENGE + 8];
    snprintf(text, sizeof(text), "$ENDWHILE%s", strncmp(norm, "$WHILE", 6) == 0 ? norm + 6 : norm);
    spurSchreibe(makro, nr, text, wirkung);
}

// ---- $DUMP ----

enum { DZ_NICHT_DEF = 0, DZ_VAR, DZ_FELD, DZ_ELEMENT };
typedef struct { int art; int k; long long elem; } DumpZiel;                // k: Index in mvar (DZ_VAR) bzw. mfeld (DZ_FELD, DZ_ELEMENT)
typedef struct { int feld; int k; int gruppe; int reihe; } DumpEintrag;     // gruppe 0 = lokal, 1 = global
static DumpEintrag dumpTab[MVAR_TAB + MFELD_TAB];
static DumpZiel dumpZiele[DUMP_ZIELE_MAX];
static char *dumpTokens[DUMP_ZIELE_MAX];

static int dumpVergleich(const void *pa, const void *pb) {
    const DumpEintrag *a = (const DumpEintrag *)pa;
    const DumpEintrag *b = (const DumpEintrag *)pb;
    if (a->gruppe != b->gruppe) return a->gruppe - b->gruppe;
    return (a->reihe > b->reihe) - (a->reihe < b->reihe);
}

// Art eines Eintrags: lokal | global | global, verdeckt, bei einem Text zusaetzlich ", Text"
static void dumpArt(int ebene, const char *name, int istText, char *aus, size_t an) {
    if (ebene > 0) snprintf(aus, an, "lokal");
    else if (mLokalSuche(name, 0) >= 0 || mLokalSuche(name, 1) >= 0) snprintf(aus, an, "global, verdeckt");
    else snprintf(aus, an, "global");
    if (istText) {
        size_t n = strlen(aus);
        snprintf(aus + n, an - n, ", Text");
    }
}

// Ein Ziel pruefen und feststellen, was es ist; 0 = ok, sonst Fehlertext in grund. Ein Name, den es nicht gibt, ist kein Fehler.
static int dumpZielPruefen(const char *tok, DumpZiel *dz, char *grund, size_t gg) {
    char basis[40], idx[200], g[300];
    int fz = mfeldZerlegen(tok, basis, sizeof(basis), idx, sizeof(idx), g, sizeof(g));
    if (fz < 0) { snprintf(grund, gg, "$DUMP: %.250s", g); return 1; }
    dz->art = DZ_NICHT_DEF;
    dz->k = -1;
    dz->elem = 0;
    int fe = mfeldSuche(basis);
    if (fz == 1) {
        if (fe >= 0) {
            if (mfeldIndex(fe, idx, &dz->elem, g, sizeof(g)) != 0) { snprintf(grund, gg, "$DUMP: %.250s", g); return 1; }
            dz->art = DZ_ELEMENT;
            dz->k = fe;
            return 0;
        }
        if (mvarSuche(basis) >= 0) { snprintf(grund, gg, "$DUMP: %.40s ist eine einfache Variable, ein Index ist nicht erlaubt", basis); return 1; }
        return 0;
    }
    if (fe >= 0) { dz->art = DZ_FELD; dz->k = fe; return 0; }
    int k = mvarSuche(basis);
    if (k >= 0) { dz->art = DZ_VAR; dz->k = k; }
    return 0;
}

// "  <name> = <wert>  (<art>)"
static void dumpVariable(const char *name, int istText, long long wert, const char *text, const char *art) {
    char w[300], zeile[600];
    wertText(istText, wert, text, w, sizeof(w));
    snprintf(zeile, sizeof(zeile), "  %.60s = %s  (%s)", name, w, art);
    makroAusgabeZeile(zeile);
}

// Ein Feld: "  <n>(<anzahl>) = e0 e1 ..." mit hoechstens 16 Elementen je Zeile, Folgezeilen "  <n>(16..31) = ...", die Art steht in der letzten Zeile
static void dumpFeld(int fe, const char *art) {
    static char zeile[DUMP_PRO_ZEILE * (MVAR_TEXT_MAX + 4) + 200];
    int anz = mfeld[fe].anzahl;
    for (int von = 0; von < anz; von += DUMP_PRO_ZEILE) {
        int bis = von + DUMP_PRO_ZEILE;
        if (bis > anz) bis = anz;
        size_t n;
        if (von == 0) n = (size_t)snprintf(zeile, sizeof(zeile), "  %s(%d) =", mfeld[fe].name, anz);
        else n = (size_t)snprintf(zeile, sizeof(zeile), "  %s(%d..%d) =", mfeld[fe].name, von, bis - 1);
        for (int i = von; i < bis && n < sizeof(zeile); i++) {
            char w[300];
            wertText(mfeld[fe].el[i].istText, mfeld[fe].el[i].wert, mfeld[fe].el[i].text, w, sizeof(w));
            n += (size_t)snprintfGekuerzt(zeile + n, sizeof(zeile) - n, " %s", w);
        }
        if (bis >= anz && n < sizeof(zeile)) snprintf(zeile + n, sizeof(zeile) - n, "  (%s)", art);
        makroAusgabeZeile(zeile);
    }
}

// $DUMP [<ziel> ...] (Doku 4.24); rest = Text hinter $DUMP. Alle Ziele werden zuerst geprueft, erst dann folgt die Ausgabe.
// Rueckgabe 0 = ok, sonst Fehlertext in grund (nichts ausgegeben).
static int makroDump(const char *makro, const char *rest, char *grund, size_t gg) {
    char kopie[MACRO_PARAMETER_LAENGE];
    STRKOPIE(kopie, rest);
    char *sem = strchr(kopie, ';');
    if (sem != NULL) *sem = '\0';
    int n = 0;
    char *sv = NULL;
    for (char *tok = strtok_r(kopie, " \t", &sv); tok != NULL; tok = strtok_r(NULL, " \t", &sv)) {
        if (n >= DUMP_ZIELE_MAX) { snprintf(grund, gg, "$DUMP: mehr als %d Ziele", DUMP_ZIELE_MAX); return 1; }
        dumpTokens[n] = tok;
        if (dumpZielPruefen(tok, &dumpZiele[n], grund, gg) != 0) return 1;
        n++;
    }
    makroHinweis(makro, "$DUMP");
    char art[64];
    if (n > 0) {
        for (int i = 0; i < n; i++) {
            const DumpZiel *dz = &dumpZiele[i];
            if (dz->art == DZ_VAR) {
                dumpArt(mvar[dz->k].ebene, mvar[dz->k].name, mvar[dz->k].istText, art, sizeof(art));
                dumpVariable(mvar[dz->k].name, mvar[dz->k].istText, mvar[dz->k].wert, mvar[dz->k].text, art);
            } else if (dz->art == DZ_FELD) {
                dumpArt(mfeld[dz->k].ebene, mfeld[dz->k].name, 0, art, sizeof(art));
                dumpFeld(dz->k, art);
            } else if (dz->art == DZ_ELEMENT) {
                const MVarWert *el = &mfeld[dz->k].el[dz->elem];
                char name[100];
                snprintf(name, sizeof(name), "%.40s(%lld)", mfeld[dz->k].name, dz->elem);
                dumpArt(mfeld[dz->k].ebene, mfeld[dz->k].name, el->istText, art, sizeof(art));
                dumpVariable(name, el->istText, el->wert, el->text, art);
            } else {
                char zeile[300];
                snprintf(zeile, sizeof(zeile), "  %.200s = <nicht definiert>", dumpTokens[i]);
                makroAusgabeZeile(zeile);
            }
        }
        return 0;
    }
    // ohne Ziel: alles Sichtbare, zuerst die lokalen (Reihenfolge der Vereinbarung), dann die globalen (Reihenfolge der Anlage)
    int m = 0;
    for (int k = 0; k < mvarAnzahl; k++) {
        if (mvar[k].ebene != 0 && mvar[k].ebene != makroKetteTiefe) continue;
        dumpTab[m].feld = 0; dumpTab[m].k = k; dumpTab[m].gruppe = (mvar[k].ebene == 0); dumpTab[m].reihe = mvar[k].reihe; m++;
    }
    for (int k = 0; k < mfeldAnzahl; k++) {
        if (mfeld[k].ebene != 0 && mfeld[k].ebene != makroKetteTiefe) continue;
        dumpTab[m].feld = 1; dumpTab[m].k = k; dumpTab[m].gruppe = (mfeld[k].ebene == 0); dumpTab[m].reihe = mfeld[k].reihe; m++;
    }
    if (m == 0) { makroAusgabeZeile("  (keine Variablen)"); return 0; }
    qsort(dumpTab, (size_t)m, sizeof(dumpTab[0]), dumpVergleich);
    for (int i = 0; i < m; i++) {
        int k = dumpTab[i].k;
        if (dumpTab[i].feld) {
            dumpArt(mfeld[k].ebene, mfeld[k].name, 0, art, sizeof(art));
            dumpFeld(k, art);
        } else {
            dumpArt(mvar[k].ebene, mvar[k].name, mvar[k].istText, art, sizeof(art));
            dumpVariable(mvar[k].name, mvar[k].istText, mvar[k].wert, mvar[k].text, art);
        }
    }
    return 0;
}

// Im Quelltext (ausserhalb eines Makros, Doku 4.1) ist ein Label <name>% im Rumpf von $WHILE ein Fehler: Lokale Labels gibt es nur im
// Makro (Doku 4.3). Im Makro dagegen erhaelt jeder Durchlauf ein eigenes Label (ab c82ass 1.01-010, Doku 4.19, whileLabelsErsetzen).
// Normale Marken mit $V(name) (z. B. w$V(i):) sind in beiden Faellen erlaubt.
static void makroWhileLabelsPruefen(const lineElements *z, int n, MakroFehler *f, const char *op) {
    int tiefe = 0;
    for (int j = 0; j < n; j++) {
        if (makroErstesWort(&z[j], "$WHILE")) {
            tiefe++;
        } else if (makroErstesWort(&z[j], "$ENDWHILE")) {
            if (tiefe > 0) tiefe--;
        } else if (tiefe > 0 && z[j].sp1[0] != '$' && mlNameLaenge(z[j].sp1) > 0) {
            makroAktuelleZeile = z[j].srcLine;   // Fehlerort: die Zeile mit dem Label (Quelltextmodus)
            makroMelde(f, op, "Im Rumpf von $WHILE darf kein lokales Label mit %% definiert werden: %.60s (Marke mit $V(name) verwenden, z. B. w$V(i)).", z[j].sp1);
        }
    }
}

// Lokale Labels im Rumpf von $WHILE (Doku 4.19, ab c82ass 1.01-010): Ein Label <name>%:, das der Rumpf definiert, erhaelt in jedem
// Durchlauf einen eigenen Namen <name><3 Buchstaben>_<Nummer> (Nummer ab 0, wie der Zaehler bei $REPT, Doku 4.3); ebenso jede Verwendung
// im Rumpf. Bei verschachtelten Schleifen steht fuer jede Schleife, die das Label umschliesst, ein Zusatz (aeusserer zuerst), nach dem
// Zusatz, den $REPT schon angehaengt hat. Das % wird dabei gleich durch die drei Buchstaben des Aufrufs ersetzt, damit auch ein
// verschachtelter Aufruf, dem das Label als Parameter uebergeben wird, das fertige Label erhaelt. Labels ausserhalb des Rumpfes
// ersetzt macroSprung1Aufloesen wie bisher (der Vorlauf laesst die Labels im Rumpf von $WHILE aus).
static void makroLabelMerken(const char *name);   // weiter unten
static int istMlLabelDef(const char *s);          // weiter unten
char *generate_uuid(int seed);                    // weiter unten

// Index der $ENDWHILE-Zeile, die zu dem $WHILE in z[von] gehoert (n, wenn es keine gibt)
static int whileEndeSuchen(const lineElements *z, int n, int von) {
    int tiefe = 0;
    for (int j = von + 1; j < n; j++) {
        if (makroErstesWort(&z[j], "$WHILE")) {
            tiefe++;
        } else if (makroErstesWort(&z[j], "$ENDWHILE")) {
            if (tiefe == 0) return j;
            tiefe--;
        }
    }
    return n;
}

// Beim Eintritt in eine $WHILE-Schleife: die im Rumpf (einschliesslich geschachtelter Schleifen) definierten Labels <name>% sammeln
static void whileLabelsSammeln(IfRahmen *r, const lineElements *q, int n, int von) {
    r->mlNamen = NULL;
    r->mlAnzahl = 0;
    int laenge = whileEndeSuchen(q, n, von) - von - 1;
    if (laenge <= 0) return;
    char (*namen)[ML_NAME_MAX + 1] = (char (*)[ML_NAME_MAX + 1])calloc(REPT_MAX_ML, ML_NAME_MAX + 1);
    if (!namen) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    int anz = 0;
    reptMlDefiniert(&q[von + 1], laenge, namen, &anz);
    if (anz == 0) { free(namen); return; }
    r->mlNamen = namen;
    r->mlAnzahl = anz;
}

// 1, wenn der Rahmen eine $WHILE-Schleife ist, deren Rumpf das Label <name>% (q zeigt auf den Namen, len Zeichen) definiert
static int whileMlEnthaelt(const IfRahmen *r, const char *q, int len) {
    if (!r->istWhile) return 0;
    for (int m = 0; m < r->mlAnzahl; m++) {
        if (strncmp(r->mlNamen[m], q, (size_t)len) == 0 && r->mlNamen[m][len] == '\0') return 1;
    }
    return 0;
}

// Ersetzt in Marke, Operation und Operand der erzeugten Zeile z die Labels <name>% der offenen $WHILE-Schleifen st[0..sp-1]
// (seed = Nummer des Makroaufrufs, bestimmt die drei Buchstaben)
static void whileLabelsErsetzen(lineElements *z, const IfRahmen *st, int sp, int seed) {
    int hat = 0;
    for (int k = 0; k < sp; k++) if (st[k].istWhile && st[k].mlAnzahl > 0) hat = 1;
    if (!hat) return;
    const char c0 = z->sp1[0];
    if (c0 == ';' || c0 == '#' || c0 == '$' || c0 == '&') return;   // Kommentar- und Schluesselwortzeilen: kein Label
    char uuid[8];
    strkopiere(uuid, sizeof(uuid), generate_uuid(seed));
    const int istDef = istMlLabelDef(z->sp1);
    const int nl0 = mlNameLaenge(z->sp1);
    const int altes = (nl0 == 6 && z->sp1[0] == 'M' && z->sp1[1] == 'L' && isdigit((unsigned char)z->sp1[2]) &&
                       isdigit((unsigned char)z->sp1[3]) && isdigit((unsigned char)z->sp1[4]) && isdigit((unsigned char)z->sp1[5]));
    char *felder[3] = { z->sp1, z->sp2, z->sp3 };
    for (int f = 0; f < 3; f++) {
        if (strchr(felder[f], '%') == NULL) continue;
        char neu[4 * MACRO_PARAMETER_LAENGE];
        size_t n = 0;
        const char *q = felder[f];
        while (*q != '\0' && n + 96 < sizeof(neu)) {
            int len = 0;
            int treffer = 0;
            if (q == felder[f] || !ML_IDZ(q[-1])) {   // nur am Wortanfang (ende% ist nicht der Anfang von weiterende%)
                len = mlNameLaenge(q);
                if (len > 0) for (int k = 0; k < sp && !treffer; k++) treffer = whileMlEnthaelt(&st[k], q, len);
            }
            if (!treffer) {
                neu[n++] = *q++;
                continue;
            }
            const char *nm = q;
            memcpy(neu + n, nm, (size_t)len);   // <name>
            n += (size_t)len;
            n += (size_t)snprintf(neu + n, sizeof(neu) - n, "%s", uuid);   // % -> drei Buchstaben
            q += len + 1;
            while (ML_IDZ(*q) && n + 96 < sizeof(neu)) neu[n++] = *q++;   // vorhandener Zusatz (z. B. von $REPT)
            for (int k = 0; k < sp; k++) {   // Zusatz _<Durchlauf ab 0> je umschliessender Schleife, aeussere zuerst
                if (whileMlEnthaelt(&st[k], nm, len)) n += (size_t)snprintf(neu + n, sizeof(neu) - n, "_%d", st[k].durchlauf - 1);
            }
        }
        neu[n] = '\0';
        strkopiere(felder[f], MACRO_PARAMETER_LAENGE, neu);
    }
    if (istDef && !altes && strchr(z->sp1, '%') == NULL) {   // lesbares Label: in der Meldung "nie verwendet" wie die anderen nicht melden
        char gen[LABEL_SIZE];
        strkopiere(gen, sizeof(gen), z->sp1);
        size_t gl = strlen(gen);
        if (gl > 0 && gen[gl - 1] == ':') gen[gl - 1] = '\0';
        makroLabelMerken(gen);
    }
}

// Wertet $IF / $ELIF / $ELSE / $ENDIF aus und liefert die Zeilen des Makroaufrufs; result wird freigegeben.
// Bei einem Fehler (in f) werden alle Zeilen unveraendert uebernommen.
// $V(name) und $CALC(...) in einer $IF/$ELIF-Zeile: Die Variablen haben hier den Stand an der Stelle der Zeile (Doku 4.7).
static char mvarFehler[300];
static int makroBedingungVariablen(lineElements *z, int *unbenutzt) {
    (void)unbenutzt;
    char *fv[] = { z->sp1, z->sp2, z->sp3, z->sp4 };
    for (int q = 0; q < 4; q++) {
        if (mvarFund(fv[q]) == NULL) continue;
        if (mvarErsetzen(fv[q], mvarFehler, sizeof(mvarFehler)) != 0) return 1;
        if (strstr(fv[q], "$CALC") != NULL) {
            char dummy[64][MACRO_PARAMETER_LAENGE];
            MakroFehler mf; memset(&mf, 0, sizeof(mf));
            makroCalcErsetzen(fv[q], MACRO_PARAMETER_LAENGE, dummy, 0, &mf);
            if (mf.anzahl > 0) { snprintf(mvarFehler, sizeof(mvarFehler), "$CALC in der Bedingung: Ausdruck ungültig (%.200s)", fv[q]); return 1; }
        }
    }
    return 0;
}

// Hook des Pass 0: loest eine Zeile auf, die ein Makroaufruf ist (samt allen verschachtelten Aufrufen); NULL, wenn sie keiner ist.
lineElements *(*makroAufrufHook)(const lineElements *zeile, int *anzahl) = NULL;

// ---------------------------------------------------------------------------
// Gemeinsame Bloecke $BLOCK <name> ... $ENDBLOCK (ab c82ass 1.03-003, Doku 4.32): Der erste Block eines Namens in einer Klasse erzeugt
// seinen Text, jeder spaetere mit gleichem Namen und gleichem ausgeschriebenen Text erzeugt nichts. Anderer Text unter demselben Namen
// ist ein Fehler; gleicher Text unter anderem Namen (gleiche Klasse) ergibt einen Hinweis. Bei TYP=Aufruf werden Bloecke immer erzeugt.
// Der Text eines Blocks ist der Inhalt der Zeilen (sp1 bis sp3, ohne Kommentare) nach allen Ersetzungen.
#define BLOCK_NAME_MAX 64
typedef struct { char klasse[32]; char name[BLOCK_NAME_MAX]; unsigned long long hash; char *text; char makro[MACRO_PARAMETER_LAENGE]; } BlockEintrag;
static BlockEintrag *blockTab = NULL;
static int blockAnzahl = 0, blockKap = 0;

static unsigned long long blockHash(const char *t) {   // FNV-1a, 64 Bit
    unsigned long long h = 1469598103934665603ULL;
    for (; *t; t++) { h ^= (unsigned char)*t; h *= 1099511628211ULL; }
    return h;
}

// Text der Zeilen [von, bis) als eine Zeichenkette (Aufrufer gibt sie frei)
static char *blockText(const lineElements *z, int von, int bis) {
    size_t kap = 256, len = 0;
    char *t = (char *)malloc(kap);
    if (!t) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    t[0] = '\0';
    for (int i = von; i < bis; i++) {
        if (z[i].sp1[0] == ';') continue;   // Kommentarzeile
        const char *f[3] = { z[i].sp1, z[i].sp2, z[i].sp3 };
        size_t need = strlen(f[0]) + strlen(f[1]) + strlen(f[2]) + 4;
        while (len + need + 1 > kap) {
            kap *= 2;
            char *g = (char *)realloc(t, kap);
            if (!g) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
            t = g;
        }
        len += (size_t)snprintf(t + len, kap - len, "%s\t%s\t%s\n", f[0], f[1], f[2]);
    }
    return t;
}

static int blockNameGueltig(const char *n) {
    if (n[0] == '\0' || strlen(n) >= BLOCK_NAME_MAX) return 0;
    if (!(isalpha((unsigned char)n[0]) || n[0] == '_')) return 0;
    for (const char *p = n; *p; p++) if (!(isalnum((unsigned char)*p) || *p == '_')) return 0;
    return 1;
}

static lineElements *makroBloeckeAufloesen(lineElements *result, int *lineCount, const macroDefinitionen *m, MakroFehler *f, const char *op) {
    int n = *lineCount, w = 0, offen = 0, start = -1, verworfen = 0;   // verworfen: ein fehlerhaftes $BLOCK ist gemeldet, sein $ENDBLOCK folgt ohne zweite Meldung
    char name[BLOCK_NAME_MAX]; name[0] = '\0';
    char mname[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(m->macroName, mname, sizeof(mname));
    int merge = !(m->hatSpec && m->specTyp == 1);   // TYP=Aufruf: nie zusammenfassen
    for (int i = 0; i < n; i++) {
        lineElements *z = &result[i];
        int istB = makroErstesWort(z, "$BLOCK"), istE = makroErstesWort(z, "$ENDBLOCK");
        if (!istB && !istE) { if (w != i) result[w] = result[i]; w++; continue; }
        makroAktuelleZeile = z->srcLine;
        if (istB) {
            char rest[BLOCK_NAME_MAX + 64]; int rl = 0;
            const char *p = makroRestNachWort(z);
            while (*p == ' ' || *p == '\t') p++;
            while (*p && *p != ' ' && *p != '\t' && *p != ';' && rl < (int)sizeof(rest) - 1) rest[rl++] = *p++;
            rest[rl] = '\0';
            while (*p == ' ' || *p == '\t') p++;
            const int warOffen = offen;
            if (offen) makroMelde(f, op, "$BLOCK %s innerhalb des Blocks %s: Blöcke dürfen nicht verschachtelt sein.", rest, name);
            else if (!blockNameGueltig(rest)) makroMelde(f, op, "$BLOCK erwartet genau einen gültigen Blocknamen: $BLOCK <Name>.");
            else if (*p != '\0' && *p != ';') makroMelde(f, op, "$BLOCK %s: nach dem Blocknamen steht noch Text.", rest);
            else if (!m->hatSpec || m->specClass[0] == '\0') makroMelde(f, op, "$BLOCK %s: Das Makro %s hat keine CLASS in der $SPEC-Zeile; der Namensraum der Blöcke ist die Klasse.", rest, mname);
            else { offen = 1; start = w; snprintf(name, sizeof(name), "%.*s", BLOCK_NAME_MAX - 1, rest); }   // Laenge ist durch blockNameGueltig schon begrenzt
            if (warOffen || !offen) verworfen = 1;   // Fehler bei $BLOCK: das zugehoerige $ENDBLOCK folgt ohne zweite Meldung
            continue;   // die Markenzeile selbst wird nie uebernommen
        }
        // $ENDBLOCK
        const char *p = makroRestNachWort(z);
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '\0' && *p != ';') { makroMelde(f, op, "$ENDBLOCK hat keinen Operanden (Blöcke sind nicht verschachtelt)."); continue; }
        if (!offen) { if (verworfen) verworfen = 0; else makroMelde(f, op, "$ENDBLOCK ohne offenen $BLOCK."); continue; }
        offen = 0;
        if (!merge) continue;   // Zeilen bleiben, Marken entfallen
        char *text = blockText(result, start, w);
        unsigned long long h = blockHash(text);
        int k, gefunden = -1;
        for (k = 0; k < blockAnzahl; k++) if (strcmp(blockTab[k].klasse, m->specClass) == 0 && strcmp(blockTab[k].name, name) == 0) { gefunden = k; break; }
        if (gefunden >= 0) {
            if (blockTab[gefunden].hash == h && strcmp(blockTab[gefunden].text, text) == 0) w = start;   // gleicher Block: nichts erzeugen
            else makroMelde(f, op, "Block %s (Klasse %s): anderer Text als der Block gleichen Namens im Makro %s.", name, m->specClass, blockTab[gefunden].makro);
            free(text);
            continue;
        }
        for (k = 0; k < blockAnzahl; k++)
            if (blockTab[k].hash == h && strcmp(blockTab[k].klasse, m->specClass) == 0 && strcmp(blockTab[k].text, text) == 0) {
                PRINT_MSG("Hinweis: Die Blöcke %s (Makro %s) und %s (Makro %s) in der Klasse %s haben denselben Inhalt; gleicher Blockname würde sie zusammenfassen (Doku 4.32).",
                          blockTab[k].name, blockTab[k].makro, name, mname, m->specClass);
                break;
            }
        if (blockAnzahl >= blockKap) {
            blockKap = blockKap ? blockKap * 2 : 32;
            BlockEintrag *g = (BlockEintrag *)realloc(blockTab, (size_t)blockKap * sizeof(BlockEintrag));
            if (!g) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
            blockTab = g;
        }
        BlockEintrag *e = &blockTab[blockAnzahl++];
        snprintf(e->klasse, sizeof(e->klasse), "%s", m->specClass);
        snprintf(e->name, sizeof(e->name), "%s", name);
        snprintf(e->makro, sizeof(e->makro), "%s", mname);
        e->hash = h; e->text = text;   // der Text bleibt fuer spaetere Vergleiche stehen
    }
    if (offen) { makroMelde(f, op, "Der Block %s ist am Ende des Makros nicht mit $ENDBLOCK geschlossen.", name); }
    *lineCount = w;
    return result;
}

// seed: Nummer des Makroaufrufs (Labels <name>% im Rumpf von $WHILE, Doku 4.19); 0 im Quelltextmodus
static lineElements *makroBedingungenAuswerten(lineElements *result, int *lineCount, MakroFehler *f, const char *aktuellerOpCode,
                                               char paramArray[64][MACRO_PARAMETER_LAENGE], int paramAnzahl, int seed) {
    int n = *lineCount;
    lineElements *quelle = result;
    int kap = 2 * n + 1;   // Kapazitaet von `neu` (waechst, wenn verschachtelte Aufrufe an Ort und Stelle aufgeloest werden)
    lineElements *neu = (lineElements *)calloc((size_t)kap, sizeof(lineElements));
    if (!neu) {
        fprintf(stderr, "Speicherzuweisung tmp_result fehlgeschlagen!\n");
        free(quelle);
        exit(RC_FEHLER);
    }
    IfRahmen st[IF_MAX_TIEFE + 1];
    int sp = 0;
    int kk = 0;
    int fehler = (f->anzahl > 0);
    int beendet = 0;   // $EXIT wurde ausgeführt: alle weiteren Zeilen sind inaktiv, nur die MEND-Zeile bleibt (Doku 4.19)
    int spurNr = 0;    // Zaehler der gespurten Zeilen dieses Aufrufs (Doku 4.24)
    SpurVor spurVor;   // Vorbereitung der Spurzeile einer Anweisung
    char spurWirk[640];   // Wirkung der Anweisung fuer die Spurzeile (Ziel + alt + neu + " (lokal)" passen immer hinein, siehe spurZielWirkung)

    for (int j = 0; j < n && !fehler; j++) {
        lineElements *z = &quelle[j];
        makroAktuelleZeile = z->srcLine;
        if (makroKetteTiefe == 0) pass0AeussereZeile = z->srcLine;   // Quelltextmodus: Ort fuer $NOTE und $DUMP ist die Zeile selbst
        int aktiv = beendet ? 0 : ((sp == 0) ? 1 : st[sp - 1].aktiv);
        int istIf = makroErstesWort(z, "$IF");
        int istElif = makroErstesWort(z, "$ELIF");
        int istWhile = makroErstesWort(z, "$WHILE");
        int istEndWhile = makroErstesWort(z, "$ENDWHILE");

        if (istIf || istElif) {
            int w = 0;
            char grund[320];
            // Arbeitskopie: Die Zeile selbst bleibt unverändert, denn in einer $WHILE-Schleife wird sie mehrfach ausgewertet
            lineElements bed;
            makroZeileKopieren(&bed, z);
            if (istElif && sp == 0) {
                makroMelde(f, aktuellerOpCode, "$ELIF ohne vorheriges $IF.");
                fehler = 1;
            } else if (istElif && st[sp - 1].istWhile) {
                makroMelde(f, aktuellerOpCode, "$ELIF ohne vorheriges $IF (innerhalb von $WHILE).");
                fehler = 1;
            } else if (istElif && st[sp - 1].imElse) {
                makroMelde(f, aktuellerOpCode, "$ELIF hinter $ELSE.");
                fehler = 1;
            } else if (istIf && sp >= IF_MAX_TIEFE) {
                makroMelde(f, aktuellerOpCode, "$IF darf höchstens %d-fach geschachtelt werden (zusammen mit $WHILE).", IF_MAX_TIEFE);
                fehler = 1;
            } else if (!beendet && (aktiv || istElif) && makroBedingungVariablen(&bed, &w) != 0) {   // $V(name) in der Bedingung (Doku 4.7)
                makroMelde(f, aktuellerOpCode, "%s", mvarFehler);
                fehler = 1;
            } else if (!beendet && makroBedingungWert(&bed, &w, grund, sizeof(grund)) != 0) {
                makroMelde(f, aktuellerOpCode, "%s", grund);
                fehler = 1;
            } else if (istIf) {
                st[sp].elternAktiv = aktiv;
                st[sp].genommen = aktiv && w;
                st[sp].aktiv = aktiv && w;
                st[sp].imElse = 0;
                st[sp].istWhile = 0;
                st[sp].zeile = z->srcLine;
                st[sp].mlNamen = NULL;
                st[sp].mlAnzahl = 0;
                sp++;
                if (aktiv && spurEbene != 0) spurBedingung(aktuellerOpCode, &spurNr, bed.sp1, w ? "wahr" : "falsch");
            } else {
                IfRahmen *r = &st[sp - 1];
                int ausgewertet = r->elternAktiv && !r->genommen && !beendet;   // nur dann zaehlt die Bedingung des $ELIF
                r->aktiv = r->elternAktiv && !r->genommen && w;
                if (r->aktiv) r->genommen = 1;
                if (ausgewertet && spurEbene != 0) spurBedingung(aktuellerOpCode, &spurNr, bed.sp1, w ? "wahr" : "falsch");
            }
        } else if (makroErstesWort(z, "$ELSE")) {
            if (sp == 0 || st[sp - 1].istWhile) {
                makroMelde(f, aktuellerOpCode, "$ELSE ohne vorheriges $IF%s.", sp == 0 ? "" : " (innerhalb von $WHILE)");
                fehler = 1;
            } else if (st[sp - 1].imElse) {
                makroMelde(f, aktuellerOpCode, "Zweites $ELSE im selben $IF.");
                fehler = 1;
            } else {
                IfRahmen *r = &st[sp - 1];
                r->aktiv = r->elternAktiv && !r->genommen;
                r->genommen = 1;
                r->imElse = 1;
                if (r->aktiv && !beendet && spurEbene != 0) spurBedingung(aktuellerOpCode, &spurNr, z->sp1, "betreten");
            }
        } else if (makroErstesWort(z, "$ENDIF")) {
            if (sp == 0) {
                makroMelde(f, aktuellerOpCode, "$ENDIF ohne vorheriges $IF.");
                fehler = 1;
            } else if (st[sp - 1].istWhile) {
                makroMelde(f, aktuellerOpCode, "$ENDIF ohne vorheriges $IF: ein $WHILE ist noch offen (fehlendes $ENDWHILE?).");
                fehler = 1;
            } else {
                sp--;
            }
        } else if (istWhile) {
            // $WHILE <bed>: wie $IF; ist die Bedingung wahr, läuft der Rumpf, und $ENDWHILE springt hierher zurück (Doku 4.19)
            int w = 0;
            char grund[320];
            lineElements bed;
            makroZeileKopieren(&bed, z);
            if (sp >= IF_MAX_TIEFE) {
                makroMelde(f, aktuellerOpCode, "$WHILE darf höchstens %d-fach geschachtelt werden (zusammen mit $IF).", IF_MAX_TIEFE);
                fehler = 1;
            } else if (aktiv && makroBedingungVariablen(&bed, &w) != 0) {
                makroMelde(f, aktuellerOpCode, "$WHILE: %s", mvarFehler);
                fehler = 1;
            } else if (aktiv && makroBedingungWert(&bed, &w, grund, sizeof(grund)) != 0) {
                makroMelde(f, aktuellerOpCode, "$WHILE%s", strncmp(grund, "$IF", 3) == 0 ? grund + 3 : grund);
                fehler = 1;
            } else {
                st[sp].elternAktiv = aktiv;
                st[sp].genommen = aktiv && w;
                st[sp].aktiv = aktiv && w;
                st[sp].imElse = 0;
                st[sp].istWhile = 1;
                st[sp].rueck = j;
                st[sp].durchlauf = 1;
                st[sp].zeile = z->srcLine;
                st[sp].mlNamen = NULL;
                st[sp].mlAnzahl = 0;
                if (seed > 0 && aktiv && w) whileLabelsSammeln(&st[sp], quelle, n, j);   // lokale Labels des Rumpfes (Doku 4.19)
                sp++;
                if (aktiv && spurEbene != 0) spurBedingung(aktuellerOpCode, &spurNr, bed.sp1, w ? "wahr (Durchlauf 1)" : "falsch");
            }
        } else if (istEndWhile) {
            if (sp == 0) {
                makroMelde(f, aktuellerOpCode, "$ENDWHILE ohne vorheriges $WHILE.");
                fehler = 1;
            } else if (!st[sp - 1].istWhile) {
                makroMelde(f, aktuellerOpCode, "$ENDWHILE ohne vorheriges $WHILE: ein $IF ist noch offen (fehlendes $ENDIF?).");
                fehler = 1;
            } else {
                IfRahmen *r = &st[sp - 1];
                int weiter = 0;
                int bedGewertet = 0;   // die Bedingung wurde ausgewertet (der Rumpf lief): nur dann gibt es eine Spurzeile
                char endText[MACRO_PARAMETER_LAENGE];
                endText[0] = '\0';
                if (r->aktiv && !beendet) {   // der Rumpf lief: Bedingung mit dem jetzigen Stand der Variablen erneut auswerten
                    int w = 0;
                    char grund[320];
                    lineElements bed;
                    makroZeileKopieren(&bed, &quelle[r->rueck]);
                    if (makroBedingungVariablen(&bed, &w) != 0) {
                        makroMelde(f, aktuellerOpCode, "$WHILE: %s", mvarFehler);
                        fehler = 1;
                    } else if (makroBedingungWert(&bed, &w, grund, sizeof(grund)) != 0) {
                        makroMelde(f, aktuellerOpCode, "$WHILE%s", strncmp(grund, "$IF", 3) == 0 ? grund + 3 : grund);
                        fehler = 1;
                    } else {
                        weiter = w;
                        bedGewertet = 1;
                        if (spurEbene != 0) spurNormalisieren(bed.sp1, endText, sizeof(endText));
                    }
                }
                if (!fehler) {
                    if (weiter) {
                        if (r->durchlauf >= WHILE_MAX_DURCHLAEUFE) {
                            makroMelde(f, aktuellerOpCode, "$WHILE: mehr als %d Durchläufe (Endlosschleife?).", WHILE_MAX_DURCHLAEUFE);
                            fehler = 1;
                        } else {
                            r->durchlauf++;
                            j = r->rueck;   // weiter mit der ersten Zeile hinter $WHILE
                            if (bedGewertet && spurEbene != 0) {
                                snprintf(spurWirk, sizeof(spurWirk), "wahr (Durchlauf %d)", r->durchlauf);
                                spurEndWhile(aktuellerOpCode, &spurNr, endText, spurWirk);
                            }
                        }
                    } else {
                        if (bedGewertet && spurEbene != 0) {
                            snprintf(spurWirk, sizeof(spurWirk), "falsch (Ende nach %d Durchläufen)", r->durchlauf);
                            spurEndWhile(aktuellerOpCode, &spurNr, endText, spurWirk);
                        }
                        free(r->mlNamen);
                        r->mlNamen = NULL;
                        r->mlAnzahl = 0;
                        sp--;
                    }
                }
            }
        } else {
            const char *w = z->sp1;
            while (*w == ' ' || *w == '\t') w++;
            int blockMarke = aktiv && (makroErstesWort(z, "$BLOCK") || makroErstesWort(z, "$ENDBLOCK"));   // Doku 4.32: bleibt bis makroBloeckeAufloesen stehen
            if (blockMarke && makroKetteTiefe == 0) {
                makroMelde(f, aktuellerOpCode, "%s steht außerhalb eines Makroaufrufs.", makroErstesWort(z, "$BLOCK") ? "$BLOCK" : "$ENDBLOCK");
                fehler = 1;
                continue;
            }
            if (*w == '$' && !blockMarke) {   // $PRx und andere Schluesselwortzeilen erzeugen keine Ausgabe
                // $ERROR <text> und $WARN <text> (Doku 4.5): nur im erzeugten Zweig; Parameter sind schon ersetzt
                if (aktiv && makroErstesWort(z, "$DIM")) {   // Feld vereinbaren (Doku 4.17)
                    char grundD[300];
                    int spurAn = (spurEbene != 0);
                    if (spurAn) spurVorbereiten(z, 0, 0, paramArray, paramAnzahl, &spurVor);
                    if (mfeldVereinbaren(makroRestNachWort(z), grundD, sizeof(grundD)) != 0) makroMelde(f, aktuellerOpCode, "%s", grundD);
                    else if (spurAn) {
                        spurDimWirkung(spurVor.text, spurWirk, sizeof(spurWirk));
                        spurSchreibe(aktuellerOpCode, &spurNr, spurVor.text, spurWirk);
                    }
                    continue;
                }
                if (aktiv && makroErstesWort(z, "$LOCAL")) {   // lokale Variablen vereinbaren (Doku 4.20)
                    char grundL[300];
                    int spurAn = (spurEbene != 0);
                    if (spurAn) spurVorbereiten(z, 0, 0, paramArray, paramAnzahl, &spurVor);
                    if (mlokalVereinbaren(makroRestNachWort(z), grundL, sizeof(grundL), j) != 0) makroMelde(f, aktuellerOpCode, "%s", grundL);
                    else if (spurAn) {
                        spurLokalWirkung(spurVor.text, spurWirk, sizeof(spurWirk));
                        spurSchreibe(aktuellerOpCode, &spurNr, spurVor.text, spurWirk);
                    }
                    continue;
                }
                if (aktiv && makroErstesWort(z, "$GLOBAL")) {   // Namen ausdruecklich als global vereinbaren (Doku 4.31)
                    char grundG[300];
                    int spurAn = (spurEbene != 0);
                    if (spurAn) spurVorbereiten(z, 0, 0, paramArray, paramAnzahl, &spurVor);
                    if (mglobalVereinbaren(makroRestNachWort(z), grundG, sizeof(grundG)) != 0) makroMelde(f, aktuellerOpCode, "%s", grundG);
                    else if (spurAn) {
                        spurGlobalWirkung(spurVor.text, spurWirk, sizeof(spurWirk));
                        spurSchreibe(aktuellerOpCode, &spurNr, spurVor.text, spurWirk);
                    }
                    continue;
                }
                if (aktiv && makroErstesWort(z, "$EXIT")) {   // Makro vorzeitig verlassen (Doku 4.19)
                    if (makroKetteTiefe == 0) {   // Quelltextmodus (Doku 4.1): der Rest des Quelltexts wuerde wegfallen
                        makroMelde(f, aktuellerOpCode, "$EXIT steht außerhalb eines Makroaufrufs (im Quelltext würde der Rest des Quelltexts wegfallen).");
                        fehler = 1;
                        continue;
                    }
                    if (spurEbene != 0) spurBedingung(aktuellerOpCode, &spurNr, z->sp1, "Makro beendet");
                    beendet = 1;
                    continue;
                }
                int mstrArt = aktiv ? mstrDirektive(z) : 0;
                if (mstrArt != 0) {   // Zeichenkettenfunktionen (Doku 4.21)
                    char grundS[300];
                    int spurAn = (spurEbene != 0);
                    if (spurAn) spurVorbereiten(z, 1, 1, paramArray, paramAnzahl, &spurVor);   // $1 bis $9 sind hier noch nicht ersetzt
                    int rcS = mstrAusfuehren(mstrArt, z, paramArray, paramAnzahl, f, grundS, sizeof(grundS));
                    if (rcS == 1) makroMelde(f, aktuellerOpCode, "%s", grundS);
                    else if (rcS == 0 && spurAn) {
                        spurZielWirkung(&spurVor, spurWirk, sizeof(spurWirk));
                        spurSchreibe(aktuellerOpCode, &spurNr, spurVor.text, spurWirk);
                    }
                    continue;
                }
                int istSet = makroErstesWort(z, "$SET");
                if (aktiv && (istSet || makroErstesWort(z, "$INC"))) {
                    char grundV[300];
                    int spurAn = (spurEbene != 0);
                    if (spurAn) spurVorbereiten(z, 0, 1, paramArray, paramAnzahl, &spurVor);
                    if (mvarAusfuehren(istSet, makroRestNachWort(z), grundV, sizeof(grundV)) != 0) makroMelde(f, aktuellerOpCode, "%s", grundV);
                    else if (spurAn) {
                        spurZielWirkung(&spurVor, spurWirk, sizeof(spurWirk));
                        spurSchreibe(aktuellerOpCode, &spurNr, spurVor.text, spurWirk);
                    }
                    continue;
                }
                // Hilfen zur Fehlersuche (Doku 4.24): beobachten nur, keine Spurzeile fuer sie selbst
                if (aktiv && makroErstesWort(z, "$NOTE")) { makroNote(aktuellerOpCode, z, f); continue; }
                if (aktiv && makroErstesWort(z, "$TRACE")) { makroTrace(aktuellerOpCode, z, f); continue; }
                if (aktiv && makroErstesWort(z, "$DUMP")) {
                    char grundU[300];
                    if (makroDump(aktuellerOpCode, makroRestNachWort(z), grundU, sizeof(grundU)) != 0) makroMelde(f, aktuellerOpCode, "%s", grundU);
                    continue;
                }
                int istErr = makroErstesWort(z, "$ERROR");
                if (aktiv && (istErr || makroErstesWort(z, "$WARN"))) makroWarnError(aktuellerOpCode, z, istErr, f);
                continue;
            }
            // Die MEND-Zeile des Makros bleibt auch nach $EXIT erhalten
            int istMend = (sp == 0 && (strcmp(z->sp2, "macroende") == 0 || strcmp(z->sp2, "MACROENDE") == 0 ||
                                       strcmp(z->sp2, "MEND") == 0));
            if (!aktiv && !(beendet && istMend)) continue;
            if (kk + 8 >= ZEILEN_GRENZE) {   // z. B. eine $WHILE-Schleife mit sehr vielen Durchläufen
                makroMelde(f, aktuellerOpCode, "Das Makro erzeugt mehr als %d Zeilen (Endlosschleife in $WHILE?).", ZEILEN_GRENZE);
                fehler = 1;
                continue;
            }
            if (kk + 8 >= kap) {   // Schleifen lassen die Ausgabe über 2n+1 Zeilen wachsen
                int altKap = kap;
                kap = kap + kap / 2 + 16;
                lineElements *gr = (lineElements *)realloc(neu, (size_t)kap * sizeof(lineElements));
                if (!gr) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
                memset(gr + altKap, 0, (size_t)(kap - altKap) * sizeof(lineElements));   // makroZeileKopieren kopiert opname nicht
                neu = gr;
            }
            makroZeileKopieren(&neu[kk], z);
            if (seed > 0) whileLabelsErsetzen(&neu[kk], st, sp, seed);   // Labels <name>% im Rumpf von $WHILE: je Durchlauf eigenes Label (Doku 4.19)
            int fVorher = f->anzahl;   // Fehler beim Aufloesen dieser Zeile: keine Spurzeile
            int spurGerufen = 0;       // "ruft <Name>" ist schon ausgegeben
            {
                char *fv[] = { neu[kk].sp1, neu[kk].sp2, neu[kk].sp3, neu[kk].sp4 };
                for (int q = 0; q < 4; q++) {
                    char grundV[300];
                    if (makroKetteTiefe == 0 && (q == 3 || z->sp1[0] == ';')) continue;   // Quelltextmodus: Kommentare bleiben unveraendert (Doku 4.1)
                    if (mvarFund(fv[q]) != NULL && mvarErsetzen(fv[q], grundV, sizeof(grundV)) != 0) makroMelde(f, aktuellerOpCode, "%s", grundV);
                }
            }
            if (istMend) {
                STRKOPIE(neu[kk].sp1, ";+++");
                STRKOPIE(neu[kk].sp2, "MEND");
            }
            // Verschachtelter Makroaufruf: sofort an dieser Stelle aufloesen (Quelltextreihenfolge). Damit wirken $SET/$INC/$V
            // und die Labelnummern in der Reihenfolge der Zeilen, nicht erst nach allen Aufrufen der aeusseren Ebene.
            if (makroAufrufHook != NULL && neu[kk].sp1[0] != ';' && neu[kk].sp2[0] != '\0' && !isdigit((unsigned char)neu[kk].sp2[0])) {
                char *fa[] = { neu[kk].sp1, neu[kk].sp2, neu[kk].sp3, neu[kk].sp4 };
                for (int q = 0; q < 4; q++) {
                    if (makroKetteTiefe == 0 && q == 3) continue;   // Quelltextmodus: Kommentar bleibt unveraendert
                    if (strstr(fa[q], "$CALC") != NULL) makroCalcErsetzen(fa[q], MACRO_PARAMETER_LAENGE, paramArray, paramAnzahl, f);
                }
                if (spurEbene != 0 && f->anzahl == fVorher && macroSuche(neu[kk].sp2) >= 0) {   // vor dem Aufruf, sonst stuende die Spur des Aufgerufenen davor
                    spurRuft(aktuellerOpCode, &spurNr, &neu[kk]);
                    spurGerufen = 1;
                }
                int an = 0;
                lineElements *sub = makroAufrufHook(&neu[kk], &an);
                if (sub != NULL) {
                    if (kk + an + (n - j) + 8 >= ZEILEN_GRENZE) {
                        meldeZuVieleZeilen(neu[kk].srcLine);
                        exit(RC_FEHLER);
                    }
                    if (kk + an + (n - j) + 8 > kap) {
                        int altKap = kap;
                        kap = kk + an + (n - j) + 8 + kap / 2;
                        lineElements *gr = (lineElements *)realloc(neu, (size_t)kap * sizeof(lineElements));
                        if (!gr) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
                        memset(gr + altKap, 0, (size_t)(kap - altKap) * sizeof(lineElements));
                        neu = gr;
                    }
                    memcpy(&neu[kk], sub, (size_t)an * sizeof(lineElements));
                    kk += an;
                    free(sub);
                    continue;
                }
            }
            if (f->anzahl == fVorher) makroSymbolMerken(&neu[kk]);   // erzeugtes abs/equ mit Zahlenwert: ab jetzt fuer $CALC sichtbar (Doku 4.18)
            if (spurEbene != 0 && !spurGerufen && f->anzahl == fVorher && spurErzeugtZeile(&neu[kk]))
                spurErzeugt(aktuellerOpCode, &spurNr, &neu[kk], paramArray, paramAnzahl);
            kk++;
        }
    }
    for (int q = 0; q < sp; q++) free(st[q].mlNamen);   // offene $WHILE-Rahmen (Fehler oder fehlendes $ENDWHILE)
    if (!fehler && sp > 0) {
        makroAktuelleZeile = st[sp - 1].zeile;   // Quelltextmodus: die Zeile des offenen $IF bzw. $WHILE
        if (st[sp - 1].istWhile) makroMelde(f, aktuellerOpCode, "Fehlendes $ENDWHILE für ein $WHILE.");
        else makroMelde(f, aktuellerOpCode, "Fehlendes $ENDIF für ein $IF.");
        fehler = 1;
    }
    if (fehler) {
        is_error0 = 1;
        kk = 0;
        for (int j = 0; j < n; j++) {
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
        result[*lineCount].makroInst = 0;
        (*lineCount)++;
    }
    return result;
}

// !$wdhl und !$wdhl_adr_e: jede Wiederholungsanweisung des Makros wird in eine Befehlszeile aufgeloest (Doku 4.16).
//   !$wdhl <Loeschen> <Resultat> <Operation> <Anzahl> <Adresse>   fuenf Operanden auf der Zeile (c82ass ab 1.00-059)
//   !$wdhl <Adresse>                                               alte Form: Loeschen, Resultat, Operation und Anzahl kommen aus $1 bis $4 des Makros
//   !$wdhl_adr_e <Anzahl> <Nullspur>                               Linksverschiebung ueber die Nullspur (Befehl 644)
// Vorher wurde nur die erste solche Zeile bearbeitet und immer $1 bis $5 des Makros gelesen.
static int makroWdhlWorte(const char *sp3, char w[6][MACRO_PARAMETER_LAENGE]) {
    int n = 0;
    const char *p = sp3;
    while (*p != '\0') {
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0') break;
        const char *anf = p;
        while (*p != '\0' && *p != ' ' && *p != '\t') p++;
        if (n < 6) {
            size_t len = (size_t)(p - anf);
            if (len >= MACRO_PARAMETER_LAENGE) len = MACRO_PARAMETER_LAENGE - 1;
            memcpy(w[n], anf, len);
            w[n][len] = '\0';
        }
        n++;
    }
    return n;
}

static int makroWdhlIstEiner(const char *wort, const char *const liste[]) {
    for (int k = 0; liste[k] != NULL; k++) if (strcmp(wort, liste[k]) == 0) return 1;
    return 0;
}

// Prueft die fuenf Operanden einer !$wdhl-Zeile; Rueckgabe 0 = in Ordnung, sonst Fehlertext in grund.
static int makroWdhlPruefen(char w[6][MACRO_PARAMETER_LAENGE], char *grund, size_t grundGroesse) {
    static const char *const loe[] = { "JA", "NE", NULL };
    static const char *const res[] = { "LI", "RE", "ZL", "OHNE", NULL };
    static const char *const ops[] = { "KON", "ADD", "SUB", "BADD", NULL };
    if (!makroWdhlIstEiner(w[0], loe)) { snprintf(grund, grundGroesse, "Löschen \"%.40s\" ungültig (JA oder NE)", w[0]); return 1; }
    if (!makroWdhlIstEiner(w[1], res)) { snprintf(grund, grundGroesse, "Resultatsbehandlung \"%.40s\" ungültig (LI, RE, ZL oder OHNE)", w[1]); return 1; }
    if (!makroWdhlIstEiner(w[2], ops)) { snprintf(grund, grundGroesse, "Operation \"%.40s\" ungültig (KON, ADD, SUB oder BADD)", w[2]); return 1; }
    int anz = berechneOperand(w[3]);
    if (!isdigit((unsigned char)w[3][0]) || anz < 1 || anz > 32) { snprintf(grund, grundGroesse, "Anzahl \"%.40s\" ungültig (1 bis 32)", w[3]); return 1; }
    if (!isdigit((unsigned char)w[4][0])) { snprintf(grund, grundGroesse, "Adresse \"%.40s\" ungültig (Zahl, oktal mit führender 0 oder dezimal; kein Symbol)", w[4]); return 1; }
    return 0;
}

static void makroWdhlAufloesen(lineElements *result, int lineCount, char paramArray[64][MACRO_PARAMETER_LAENGE],
                               MakroFehler *f, const char *makroName) {
    for (int i_in = 0; i_in < lineCount && (result[i_in].sp1[0] != '\0' || result[i_in].sp2[0] != '\0' || result[i_in].sp3[0] != '\0'); i_in++) {   // Obergrenze: kein Lesen hinter dem Array
        char tempLine[256] = "";
        char label[MACRO_PARAMETER_LAENGE];
        int ist_adr_e = strcmp(result[i_in].sp2, "!$wdhl_adr_e") == 0;
        int ist_wdhl  = strcmp(result[i_in].sp2, "!$wdhl") == 0;
        if (!ist_adr_e && !ist_wdhl) continue;
        if (strstr(result[i_in].sp3, "$PR") != NULL) continue;   // wie bisher: noch nicht aufgeloeste Pruefzeile
        STRKOPIE(label, result[i_in].sp1);                       // ein Label der Zeile bleibt erhalten
        int aufgeloest = 0;

        if (ist_adr_e) {
            STRKOPIE(tempLine, result[i_in].sp2);
            STRANHANG(tempLine, " ");
            STRANHANG(tempLine, result[i_in].sp3);
            verarbeiteZeile_wdhl_adr_e(tempLine);
            aufgeloest = 1;
        } else {
            char w[6][MACRO_PARAMETER_LAENGE] = { "", "", "", "", "", "" };
            int n = makroWdhlWorte(result[i_in].sp3, w);
            if (n == 5) {                                        // neue Form: alle fuenf Werte stehen auf der Zeile
                char grund[200];
                if (makroWdhlPruefen(w, grund, sizeof(grund)) != 0) {
                    makroMelde(f, makroName, "!$wdhl: %s", grund);
                } else {
                    STRKOPIE(tempLine, result[i_in].sp2);
                    aufgeloest = verarbeiteZeile_wdhl(tempLine, w[0], w[1], w[2], w[3], w[4]) == 0;
                }
            } else if (n <= 1) {                                 // alte Form: Parameter $1 bis $5 des Makros
                STRKOPIE(tempLine, result[i_in].sp2);
                aufgeloest = verarbeiteZeile_wdhl(tempLine, paramArray[0], paramArray[1], paramArray[2], paramArray[3], paramArray[4]) == 0;
            } else {
                makroMelde(f, makroName, "!$wdhl erwartet fünf Operanden (Löschen Resultat Operation Anzahl Adresse), nicht %d", n);
            }
        }

        if (aufgeloest) {
            int muell = i_in;
            processLine(tempLine, result, &muell);
            if (result[i_in].sp1[0] == '\0') STRKOPIE(result[i_in].sp1, label);
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

// Liest die $DEFAULT-Zeilen des Makros ($DEFAULT <nr> <wert>, Doku 4.6): vorhanden[k] = 1 und wert[k] fuer jeden Parameter k mit Vorgabe.
// Rueckgabe 0 = ok; sonst Fehlertext in grund (zu viele, falsche oder doppelte $DEFAULT-Zeilen).
static int makroDefaultsLesen(const macroDefinitionen *m, int vorhanden[MACRO_PARAMETER_ANZAHL + 1],
                              char wert[MACRO_PARAMETER_ANZAHL + 1][MACRO_PARAMETER_LAENGE], char *grund, size_t grundGroesse) {
    int soll = m->macroParameterAnzahl;
    for (int j = 0; j < m->macroLineCount; j++) {
        const char *p = m->macroParsedLines[j].sp1;
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, "$DEFAULT", 8) != 0 || !(p[8] == '\0' || p[8] == ' ' || p[8] == '\t')) continue;
        char kopie[256];
        STRKOPIE(kopie, p);
        char *sv;
        strtok_r(kopie, " \t", &sv);                     // $DEFAULT
        char *nr = strtok_r(NULL, " \t", &sv);
        char *w = strtok_r(NULL, " \t", &sv);
        char *rest = strtok_r(NULL, " \t", &sv);
        int k = 0;
        if (nr != NULL && nr[0] >= '1' && nr[0] <= '9') {   // Nummer mit ein oder zwei Ziffern, ohne fuehrende 0 (Doku 4.26)
            if (nr[1] == '\0') k = nr[0] - '0';
            else if (isdigit((unsigned char)nr[1]) && nr[2] == '\0') k = (nr[0] - '0') * 10 + (nr[1] - '0');
        }
        if (k < 1 || k > soll || k > MACRO_PARAMETER_ANZAHL || w == NULL || (rest != NULL && rest[0] != ';')) {
            snprintf(grund, grundGroesse, "$DEFAULT erwartet <Nummer 1 bis %d> <Wert ohne Leerzeichen>: %.100s", soll, p);
            return 1;
        }
        if (vorhanden[k]) {
            char bez[64];
            makroParamBez(m, k, bez, sizeof(bez));
            snprintf(grund, grundGroesse, "$DEFAULT für Parameter %s steht mehrfach", bez);
            return 1;
        }
        vorhanden[k] = 1;
        STRKOPIE(wert[k], w);
    }
    return 0;
}

// Vorgabewerte ($DEFAULT <nr> <wert>, Doku 4.6): Wurden weniger Parameter uebergeben als das Makro vereinbart,
// ergaenzt die Funktion die fehlenden aus den $DEFAULT-Zeilen. Rueckgabe 0 = ok; sonst Fehlertext in grund.
// *anzahl ist danach die vereinbarte Parameterzahl; *uebergeben die Zahl der wirklich uebergebenen Parameter ($#).
static int makroDefaultsEinsetzen(const macroDefinitionen *m, char paramArray[64][MACRO_PARAMETER_LAENGE],
                                  int *anzahl, int *uebergeben, char *grund, size_t grundGroesse) {
    int soll = m->macroParameterAnzahl;
    int vorhanden[MACRO_PARAMETER_ANZAHL + 1] = {0};
    char wert[MACRO_PARAMETER_ANZAHL + 1][MACRO_PARAMETER_LAENGE];
    *uebergeben = *anzahl;
    if (makroDefaultsLesen(m, vorhanden, wert, grund, grundGroesse) != 0) return 1;
    if (*anzahl > soll && !m->variabel) {
        snprintf(grund, grundGroesse, "erwartet %d Parameter, aber %d wurden übergeben!", soll, *anzahl);
        return 1;
    }
    if (*anzahl > MACRO_PARAMETER_ANZAHL) {
        snprintf(grund, grundGroesse, "höchstens %d Parameter zulässig, aber %d wurden übergeben!", MACRO_PARAMETER_ANZAHL, *anzahl);
        return 1;
    }
    for (int k = *anzahl + 1; k <= soll && k <= MACRO_PARAMETER_ANZAHL; k++) {
        if (!vorhanden[k]) {
            char bez[64];
            makroParamBez(m, k, bez, sizeof(bez));
            snprintf(grund, grundGroesse, "erwartet %s%d Parameter, aber %d wurden übergeben! (für %s gibt es kein $DEFAULT)", m->variabel ? "mindestens " : "", soll, *anzahl, bez);
            return 1;
        }
        STRKOPIE(paramArray[k - 1], wert[k]);
    }
    if (*anzahl < soll) *anzahl = soll;
    return 0;
}

// Aufruf eines Makros mit Schluesselwortparametern (Doku 4.30, ab c82ass 1.01-025): zerlegt die Parameterzeile des Aufrufs, ordnet die
// Positionsoperanden der Reihe nach den Positionsparametern zu (die Schluesselwortoperanden zaehlen dabei nicht mit), setzt die angegebenen
// Schluesselwoerter und fuer die weggelassenen deren Vorgabe aus der MACRO-Zeile. Die Parameter liegen danach in der Reihenfolge der
// Vereinbarung in paramArray (Nummern $1 bis $9, $P(k) wie bisher), weitere Positionsoperanden eines Makros mit + dahinter.
// Ein Operand name=wert ist nur in so einem Makro ein Schluesselwortoperand; Operanden in Anfuehrungszeichen sind immer Positionswerte.
// *anzahl = Zahl der belegten Parameter, *uebergeben = Zahl der Positionsoperanden ($#). Rueckgabe 0 = ok; sonst Fehlertext in grund.
static int makroSchluesselEinsetzen(const macroDefinitionen *m, const char *zeile, char paramArray[64][MACRO_PARAMETER_LAENGE],
                                    int *anzahl, int *uebergeben, char *grund, size_t gg) {
    const int soll = m->macroParameterAnzahl;
    int rc = 1;
    char mname[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(m->macroName, mname, sizeof(mname));
    int posNr[MACRO_PARAMETER_ANZAHL];   // Nummern (0-basiert) der Positionsparameter in der Reihenfolge der Vereinbarung
    int npos = 0;
    for (int k = 0; k < soll && k < MACRO_PARAMETER_ANZAHL; k++) if (!m->schluessel[k]) posNr[npos++] = k;

    char (*pos)[MACRO_PARAMETER_LAENGE] = (char (*)[MACRO_PARAMETER_LAENGE])malloc(64 * (size_t)MACRO_PARAMETER_LAENGE);
    char (*kwWert)[MACRO_PARAMETER_LAENGE] = (char (*)[MACRO_PARAMETER_LAENGE])malloc((size_t)(MACRO_PARAMETER_ANZAHL + 1) * MACRO_PARAMETER_LAENGE);
    if (pos == NULL || kwWert == NULL) {
        fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
    int kwGegeben[MACRO_PARAMETER_ANZAHL + 1] = {0};
    int dvorhanden[MACRO_PARAMETER_ANZAHL + 1] = {0};
    char (*dwert)[MACRO_PARAMETER_LAENGE] = (char (*)[MACRO_PARAMETER_LAENGE])malloc((size_t)(MACRO_PARAMETER_ANZAHL + 1) * MACRO_PARAMETER_LAENGE);
    if (dwert == NULL) {
        fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
    if (makroDefaultsLesen(m, dvorhanden, dwert, grund, gg) != 0) goto ende;

    {   // 1. Zerlegen: Positionsoperanden in pos, Schluesselwortoperanden in kwWert
        char kopie[MACRO_PARAMETER_LAENGE];
        strkopiere(kopie, sizeof(kopie), zeile);
        trimWhitespace(kopie);
        int np = 0;
        char *p = kopie;
        while (1) {
            while (*p == ' ' || *p == '\t') p++;
            if (*p == '\0') break;
            char *wort = p;
            char *name = NULL;     // gesetzt bei name=wert
            char *wert = NULL;
            int inQuotes = 0;
            if (*p == '"' || *p == '\'') {   // Zeichenkette als Positionswert (wie bei Makros ohne Schluesselwoerter)
                char *e = strchr(p + 1, *p);
                if (e != NULL && (e[1] == '\0' || e[1] == ' ' || e[1] == '\t')) {
                    *e = '\0';
                    wort = p + 1;
                    p = (e[1] == '\0') ? e + 1 : e + 2;
                    inQuotes = 1;
                }
            }
            if (!inQuotes) {
                size_t nl = makroNameLaenge(p);
                if (nl > 0 && p[nl] == '=' && (p[nl + 1] == '"' || p[nl + 1] == '\'')) {   // name="Text mit Leerzeichen oder ="
                    char *e = strchr(p + nl + 2, p[nl + 1]);
                    if (e != NULL && (e[1] == '\0' || e[1] == ' ' || e[1] == '\t')) {
                        *e = '\0';
                        name = p;
                        p[nl] = '\0';
                        wert = p + nl + 2;
                        p = (e[1] == '\0') ? e + 1 : e + 2;
                        inQuotes = 1;
                    }
                }
            }
            if (!inQuotes) {   // Wort bis zum naechsten Leerraum
                while (*p != '\0' && *p != ' ' && *p != '\t') p++;
                if (*p != '\0') *p++ = '\0';
                size_t nl = makroNameLaenge(wort);
                if (nl > 0 && wort[nl] == '=') {
                    name = wort;
                    wort[nl] = '\0';
                    wert = wort + nl + 1;
                    trimQuotes(wert);
                    if (wert[0] == '\0') {
                        snprintf(grund, gg, "Makro %.60s: Schluesselwort '%.40s' hat keinen Wert (ein leerer Wert wird als %.40s=\"\" geschrieben)", mname, name, name);
                        goto ende;
                    }
                    if (wert[0] == '=') {
                        snprintf(grund, gg, "Makro %.60s: Schluesselwort '%.40s': der Wert darf nicht mit = beginnen (Text mit = steht in Anfuehrungszeichen)", mname, name);
                        goto ende;
                    }
                } else if (wort[0] == '=') {
                    snprintf(grund, gg, "Makro %.60s: Operand '%.60s': vor dem = fehlt der Name des Schluesselworts", mname, wort);
                    goto ende;
                } else {
                    trimQuotes(wort);
                }
            }
            if (name == NULL) {
                if (np < 64) snprintf(pos[np++], MACRO_PARAMETER_LAENGE, "%s", wort);
                continue;
            }
            int k = makroNamenSuche(m, name, strlen(name));
            if (k == 0) {
                char bekannt[256] = "";
                for (int q = 0; q < soll && q < MACRO_PARAMETER_ANZAHL; q++) {
                    if (!m->schluessel[q]) continue;
                    size_t bl = strlen(bekannt);
                    if (bl + strlen(m->macroParameters[q]) + 3 < sizeof(bekannt)) snprintfGekuerzt(bekannt + bl, sizeof(bekannt) - bl, "%s%s", bl > 0 ? ", " : "", m->macroParameters[q]);
                }
                snprintf(grund, gg, "Makro %.60s: Unbekanntes Schluesselwort '%.40s' (bekannt: %s)", mname, name, bekannt);
                goto ende;
            }
            if (!m->schluessel[k - 1]) {
                snprintf(grund, gg, "Makro %.60s: '%.40s' ist ein Positionsparameter, kein Schluesselwort", mname, name);
                goto ende;
            }
            if (kwGegeben[k]) {
                snprintf(grund, gg, "Makro %.60s: Schluesselwort '%.40s' steht doppelt im Aufruf", mname, name);
                goto ende;
            }
            kwGegeben[k] = 1;
            snprintf(kwWert[k], MACRO_PARAMETER_LAENGE, "%s", wert);
        }
        *uebergeben = np;

        // 2. Positionsoperanden den Positionsparametern zuordnen (weitere bei +: hinter den benannten Parametern)
        if (np > npos && !m->variabel) {
            snprintf(grund, gg, "Makro %.60s: erwartet %d Parameter, aber %d wurden übergeben!", mname, npos, np);
            goto ende;
        }
        if (soll + (np > npos ? np - npos : 0) > MACRO_PARAMETER_ANZAHL) {
            snprintf(grund, gg, "Makro %.60s: höchstens %d Parameter zulässig, aber %d wurden übergeben!", mname, MACRO_PARAMETER_ANZAHL, soll + np - npos);
            goto ende;
        }
        for (int j = 0; j < np; j++) {
            int ziel = (j < npos) ? posNr[j] : soll + (j - npos);
            snprintf(paramArray[ziel], MACRO_PARAMETER_LAENGE, "%s", pos[j]);
        }
        for (int j = np; j < npos; j++) {   // weggelassene Positionsparameter: $DEFAULT oder Fehler
            int k = posNr[j] + 1;
            if (!dvorhanden[k]) {
                char bez[64];
                makroParamBez(m, k, bez, sizeof(bez));
                snprintf(grund, gg, "Makro %.60s: erwartet %s%d Parameter, aber %d wurden übergeben! (für %s gibt es kein $DEFAULT)", mname, m->variabel ? "mindestens " : "", npos, np, bez);
                goto ende;
            }
            snprintf(paramArray[k - 1], MACRO_PARAMETER_LAENGE, "%s", dwert[k]);
        }

        // 3. Schluesselwortparameter: angegebener Wert oder Vorgabe
        memset(makroKwLeer, 0, sizeof(makroKwLeer));
        for (int k = 1; k <= soll && k <= MACRO_PARAMETER_ANZAHL; k++) {
            if (!m->schluessel[k - 1]) continue;
            if (kwGegeben[k]) {
                snprintf(paramArray[k - 1], MACRO_PARAMETER_LAENGE, "%s", kwWert[k]);
            } else {
                snprintf(paramArray[k - 1], MACRO_PARAMETER_LAENGE, "%s", m->vorgabe[k - 1]);
                if (m->vorgabe[k - 1][0] == '\0') makroKwLeer[k] = 1;   // eine leere Vorgabe prueft $PR nicht
            }
        }
        *anzahl = soll + (np > npos ? np - npos : 0);
    }
    rc = 0;
ende:
    free(pos);
    free(kwWert);
    free(dwert);
    return rc;
}

// Ersetzt $# in allen Zeilen durch die Zahl der beim Aufruf uebergebenen Parameter
static void makroAnzahlErsetzen(lineElements *result, int lineCount, int uebergeben) {
    char zahl[16];
    snprintf(zahl, sizeof(zahl), "%d", uebergeben);
    for (int j = 0; j < lineCount; j++) {
        char *fields[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };
        for (int f = 0; f < 4; f++) {
            char *pos;
            while ((pos = strstr(fields[f], "$#")) != NULL) {
                char rest[MACRO_PARAMETER_LAENGE];
                STRKOPIE(rest, pos + 2);
                snprintf(pos, MACRO_PARAMETER_LAENGE - (size_t)(pos - fields[f]), "%s%s", zahl, rest);
            }
        }
    }
}

// Ersetzt $AUFRUFNR (Doku 4.29, ab c82ass 1.01-024) in allen Zeilen durch die laufende Nummer dieses Makroaufrufs (dezimal, die Zahl,
// aus der die Buchstaben der %-Labels entstehen). Wortgrenze wie $PROBE: $AUFRUFNRX, $AUFRUFNR1 und $AUFRUFNR_ bleiben stehen;
// $AUFRUFNR( ist ein Fehler. Im Kommentarfeld und in Kommentarzeilen wird ersetzt wie bei $#, aber nie gemeldet.
static void makroAufrufNrErsetzen(lineElements *result, int lineCount, int nr, MakroFehler *f, const char *makroName) {
    char zahl[16];
    snprintf(zahl, sizeof(zahl), "%d", nr);
    for (int j = 0; j < lineCount; j++) {
        int kommentarZeile = (result[j].sp1[0] == ';');
        char *fields[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };
        for (int fi = 0; fi < 4; fi++) {
            char *pos = fields[fi];
            while ((pos = strstr(pos, "$AUFRUFNR")) != NULL) {
                unsigned char c = (unsigned char)pos[9];
                if (isalnum(c) || c == '_') { pos += 9; continue; }
                if (c == '(') {
                    if (!kommentarZeile && fi != 3) {
                        makroAktuelleZeile = result[j].srcLine;
                        makroMelde(f, makroName, "$AUFRUFNR steht ohne Klammern und ohne Argument");
                    }
                    pos += 9;
                    continue;
                }
                char rest[MACRO_PARAMETER_LAENGE];
                STRKOPIE(rest, pos + 9);
                snprintf(pos, MACRO_PARAMETER_LAENGE - (size_t)(pos - fields[fi]), "%s%s", zahl, rest);
                pos += strlen(zahl);
            }
        }
    }
}

// bearbeitet nur die Zeile lineCount die den Macronamen enthält !!!
// prüft aber den ganzen Macro und gibt ALLE seine generierten zeilen zurück
// Aufrufkette der Makros, die gerade aufgeloest werden (aeusserster Aufruf zuerst). Dient dem Erkennen indirekter Rekursion
// (A ruft B, B ruft A) und begrenzt die Schachtelungstiefe.
static char makroKette[MAKRO_KETTE_MAX][MACRO_PARAMETER_LAENGE];
static int makroKetteTiefe = 0;

// Kette "A -> B -> C" fuer Meldungen
static void makroKetteText(char *ziel, size_t groesse, const char *letzter) {
    ziel[0] = '\0';
    for (int k = 0; k < makroKetteTiefe; k++) {
        stranhaengen(ziel, groesse, makroKette[k]);
        stranhaengen(ziel, groesse, " -> ");
    }
    stranhaengen(ziel, groesse, letzter);
}

// Zeilen, deren erstes Wort ein Parameter- oder Rechenausdruck ist ($1 bis $9, $P(..), $V(..), $DEFINED(..), $MDEFINED(..), $PROBE, $CALC.., $LENn), sind keine
// Schluesselwortzeilen, sondern Anweisungen mit einer Operation aus einem Parameter (z. B. "$1 $2" mit dem Aufruf "OP 211 zahl").
// processLine legt jede Zeile, die mit '$' beginnt, ganz in sp1; hier wird sie in Operation (sp2), Operand (sp3) und Kommentar (sp4) zerlegt.
// Frueher wurde eine solche Zeile beim Aufloesen kommentarlos verworfen.
static void makroOperationAusParameter(lineElements *result, int lineCount) {
    for (int j = 0; j < lineCount; j++) {
        char *t = result[j].sp1;
        while (*t == ' ' || *t == '\t') t++;
        int param = (t[0] == '$') && (isdigit((unsigned char)t[1]) || strncmp(t, "$P(", 3) == 0 || strncmp(t, "$V(", 3) == 0 ||
                                      strncmp(t, "$DEFINED(", 9) == 0 || strncmp(t, "$MDEFINED(", 10) == 0 ||
                                      mvarProbeFund(t) == t ||
                                      strncmp(t, "$CALC", 5) == 0 || strncmp(t, "$LEN", 4) == 0);
        if (!param) continue;
        if (result[j].sp2[0] != '\0' || result[j].sp3[0] != '\0' || result[j].sp4[0] != '\0') continue;
        char text[MACRO_PARAMETER_LAENGE];
        STRKOPIE(text, t);
        char *p = text;
        char *e = p;
        while (*e != '\0' && *e != ' ' && *e != '\t' && *e != ';') e++;
        char rest[MACRO_PARAMETER_LAENGE];
        STRKOPIE(rest, e);
        *e = '\0';
        STRKOPIE(result[j].sp1, "");
        char *r = rest;
        if (e > p && e[-1] == ':') {   // Marke aus einem Parameter ("$1: abs 5", ab c82ass 1.01-031): Marke nach sp1, dahinter Operation, Operand, Kommentar
            STRKOPIE(result[j].sp1, p);
            while (*r == ' ' || *r == '\t') r++;
            char *w = r;
            while (*w != '\0' && *w != ' ' && *w != '\t' && *w != ';') w++;
            char rest2[MACRO_PARAMETER_LAENGE];
            STRKOPIE(rest2, w);
            *w = '\0';
            STRKOPIE(result[j].sp2, r);
            STRKOPIE(rest, rest2);
            r = rest;
        } else {
            STRKOPIE(result[j].sp2, p);
        }
        while (*r == ' ' || *r == '\t') r++;
        char *sem = strchr(r, ';');
        STRKOPIE(result[j].sp4, sem ? sem : "");
        if (sem) *sem = '\0';
        trimWhitespace(r);
        STRKOPIE(result[j].sp3, r);
    }
}

int makroLetzteInstanz = 0;   // Instanznummer des zuletzt beendeten Aufrufs eines TYP=M-Makros mit $SPEC (0 = keine); fuer die Kommentarzeile in pass0AufrufAufloesen

lineElements* loeseMacroAuf(macroDefinitionen *macros_p, int *macroCount_p, char *aktuellerOpCode, char *aktuelleParameterZeile, int *lineCount , char *label) {

    *lineCount = 0;

    size_t len = strlen(aktuellerOpCode);
    if (len > 0 && aktuellerOpCode[len - 1] == ':') {
        aktuellerOpCode[len - 1] = '\0';
    }

    // Parameterfeld auf dem Heap: loeseMacroAuf ruft sich ueber verschachtelte Makroaufrufe selbst auf (Stapelgroesse, Windows 1 MB)
    char (*AsmParamArray)[MACRO_PARAMETER_LAENGE] = (char (*)[MACRO_PARAMETER_LAENGE])malloc(64 * (size_t)MACRO_PARAMETER_LAENGE);
    if (!AsmParamArray) {
        fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
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

        macros_p[i].aufrufe++;   // Aufrufzaehler fuer die Makroliste (--makros)
        lineElements *result = (lineElements *)calloc(1, sizeof(lineElements));
        if (!result) {
            fprintf(stderr, "Speicherzuweisung result fehlgeschlagen!\n");
            exit(RC_FEHLER);
        }

        // Benannte Parameter (Doku 4.26): Sind die Namen oder der Rumpf fehlerhaft, ist das schon bei der Definition gemeldet;
        // der Aufruf entfaellt ohne Folgefehler (lineCount 0, der Lauf endet nach Pass 0 mit Rueckgabecode 16).
        if (macros_p[i].benannt < 0) {
            free(AsmParamArray);
            return result;
        }

        // Rekursion: Steht der Makroname schon in der Aufrufkette (A ruft B, B ruft A), wird er nicht noch einmal aufgeloest.
        // (Der direkte Selbstaufruf wird in makroZeilenUebernehmen gemeldet.)
        {
            int zyklus = 0;
            for (int k = 0; k < makroKetteTiefe; k++) if (strcmp(makroKette[k], zuPruefenderMacro) == 0) zyklus = 1;
            if (zyklus || makroKetteTiefe >= MAKRO_KETTE_MAX) {
                char kette[1024];
                makroKetteText(kette, sizeof(kette), zuPruefenderMacro);
                is_error0 = 1;
                if (zyklus) PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s [Aufrufkette: %s]", zuPruefenderMacro, kette);
                else PRINT_FEHLER("Makroaufrufe sind zu tief verschachtelt (höchstens %d Ebenen) [Aufrufkette: %s]", MAKRO_KETTE_MAX, kette);
                free(AsmParamArray);
                return result;   // lineCount = 0: der Aufruf entfaellt, der Lauf endet nach Pass 0 mit Rueckgabecode 16
            }
        }

        // Im makro
        int uebergeben = AsmParamCount;
        memset(makroKwLeer, 0, sizeof(makroKwLeer));
        {
            char grund[512];   // 512: Meldung "Unbekanntes Schluesselwort ... (bekannt: ...)" kann bis rund 405 Zeichen lang werden
            int rcParam = (macros_p[i].benannt == 1 && macros_p[i].schluesselAnzahl > 0)
                ? makroSchluesselEinsetzen(&macros_p[i], aktuelleParameterZeile, AsmParamArray, &AsmParamCount, &uebergeben, grund, sizeof(grund))   // Doku 4.30
                : makroDefaultsEinsetzen(&macros_p[i], AsmParamArray, &AsmParamCount, &uebergeben, grund, sizeof(grund));
            if (rcParam != 0) {
                MELDE_FEHLER("%s", grund);
                is_error0 = 1;
                free(AsmParamArray);
                return result;
            }
        }

        // Laufende Nummer dieses Aufrufs (in der Reihenfolge der Aufloesung): bestimmt die Buchstaben der generischen Labels
        seed_value++;
        if (seed_value > seed_max) {
            PRINT_FEHLER("Mehr als %i Macros können nicht verarbeitet werden.", seed_value);
            exit(RC_FEHLER);
        }
        int meinSeed = seed_value;

        STRKOPIE(makroKette[makroKetteTiefe], zuPruefenderMacro);
        makroKetteTiefe++;
        // Aufrufparameter dieses Aufrufs fuer mvarErsetzen ($P(..) und $LEN(..) hinter $V(..), ab c82ass 1.01-015); ein verschachtelter
        // Aufruf stellt den Stand des aeusseren am Ende wieder her (zwischen hier und dem Ende gibt es kein return)
        char (*alterParam)[MACRO_PARAMETER_LAENGE] = mAktParam;
        const int alteParamAnzahl = mAktParamAnzahl;
        mAktParam = AsmParamArray;
        mAktParamAnzahl = AsmParamCount;

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
        makroOperationAusParameter(result, *lineCount);
        makroAnzahlErsetzen(result, *lineCount, uebergeben);
        makroAufrufNrErsetzen(result, *lineCount, meinSeed, &fehler, aktuellerOpCode);
        result = makroWiederholungenAufloesen(result, lineCount, AsmParamArray, AsmParamCount, &fehler, aktuellerOpCode);
        makroParameterErsetzen(result, *lineCount, AsmParamArray, AsmParamCount, &fehler);
        // Generische Labels (ML<4 Ziffern>%...) dieses Aufrufs jetzt ersetzen, damit ein verschachtelter Aufruf, dem ein solches Label als
        // Parameter uebergeben wird, schon das fertige Label erhaelt. Ungueltige Labels werden erst unten gemeldet ($V in der Marke kann
        // ein Label erst nach der Bedingungsauswertung gueltig machen).
        macroSprung1Aufloesen(&result, lineCount, aktuellerOpCode, meinSeed, 0);
        result = makroBedingungenAuswerten(result, lineCount, &fehler, aktuellerOpCode, AsmParamArray, AsmParamCount, meinSeed);
        for (int j = 0; j < *lineCount; j++) {   // $CALC mit $V(name): jetzt, da die Variablen ersetzt sind
            char *fv[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };
            for (int q = 0; q < 4; q++) if (strstr(fv[q], "$CALC") != NULL) makroCalcErsetzen(fv[q], MACRO_PARAMETER_LAENGE, AsmParamArray, AsmParamCount, &fehler);
        }
        {
            char wdhlName[MACRO_PARAMETER_LAENGE];
            macroNameOhneDoppelpunkt(macros_p[i].macroName, wdhlName, sizeof(wdhlName));
            makroWdhlAufloesen(result, *lineCount, AsmParamArray, &fehler, wdhlName);   // vor den Fehlerzeilen: eigene Fehler der Aufloesung kommen mit
        }
        result = makroBloeckeAufloesen(result, lineCount, &macros_p[i], &fehler, aktuellerOpCode);   // $BLOCK/$ENDBLOCK (Doku 4.32)
        makroHerkunftAnhaengen(&fehler, &macros_p[i]);
        result = makroFehlerAnhaengen(result, lineCount, &fehler);
        makroLabelUebernehmen(result, lineCount, equIndex, label);
        macroSprung1Aufloesen(&result, lineCount, aktuellerOpCode, meinSeed, 1);
        // Herkunftsfeld (Doku 5.6): bei $SPEC TYP=M tragen ALLE Zeilen dieses Aufrufs die Nummer dieser Aufloesung (meinSeed), auch die
        // Zeilen eines inneren TYP=M-Aufrufs: das Feld nennt den aeussersten TYP=M-Aufruf, ein Block ist ein zusammenhaengender Lauf gleicher
        // Nummer, und ein innerer Block wandert mit dem aeusseren. Ein TYP=M-Aufruf in einem Makro ohne $SPEC oder mit TYP=A/E behaelt seine
        // eigene Nummer (eigener Block).
        makroLetzteInstanz = 0;
        if (macros_p[i].hatSpec && macros_p[i].specTyp == 0) {
            for (int j = 0; j < *lineCount; j++) result[j].makroInst = meinSeed;
            makroLetzteInstanz = meinSeed;
        }
        mAktParam = alterParam;
        mAktParamAnzahl = alteParamAnzahl;
        mlokalVerwerfen(makroKetteTiefe);   // lokale Variablen dieses Aufrufs enden mit ihm (Doku 4.20)
        if (spurEbene == makroKetteTiefe) spurEbene = 0;   // die Spur endet mit dem Aufruf, der sie eingeschaltet hat, auch bei Fehler und $EXIT (Doku 4.24)
        makroKetteTiefe--;
        free(AsmParamArray);
        return result;
    }

    free(AsmParamArray);
    *lineCount = 0;
    return NULL;
}


// $CALC(...) im Quelltext vor der Auswertung der Bedingungen: wie makroParameterErsetzen im Makroaufruf (gleiche Auswahl der Zeilen:
// Direktivzeilen nur $IF, $ELIF, $ENDIF, $ERROR, $WARN, $SET, $INC, $DIM, $LOCAL, $GLOBAL, $WHILE, $NOTE, $DUMP), aber ohne Aufrufparameter
// ($1 bis $9, $P, $LEN bleiben Text) und ohne Kommentare (Kommentarzeilen und Kommentarfeld bleiben unveraendert, Doku 4.1).
static void quelltextCalcErsetzen(lineElements *z, int n, char keineParameter[64][MACRO_PARAMETER_LAENGE], MakroFehler *f) {
    for (int j = 0; j < n; j++) {
        const char *s1 = z[j].sp1;
        if (s1[0] == '#' || s1[0] == '&' || s1[0] == ';') continue;
        if (s1[0] == '$' && strncmp(s1, "$IF", 3) != 0 && strncmp(s1, "$ELIF", 5) != 0 && strncmp(s1, "$ENDIF", 6) != 0 &&
            strncmp(s1, "$ERROR", 6) != 0 && strncmp(s1, "$WARN", 5) != 0 && strncmp(s1, "$SET", 4) != 0 &&
            strncmp(s1, "$INC", 4) != 0 && strncmp(s1, "$DIM", 4) != 0 && strncmp(s1, "$LOCAL", 6) != 0 &&
            strncmp(s1, "$GLOBAL", 7) != 0 && strncmp(s1, "$WHILE", 6) != 0 && strncmp(s1, "$NOTE", 5) != 0 && strncmp(s1, "$DUMP", 5) != 0) continue;
        makroAktuelleZeile = z[j].srcLine;
        char *fv[] = { z[j].sp1, z[j].sp2, z[j].sp3 };
        for (int q = 0; q < 3; q++) {
            if (strstr(fv[q], "$CALC") != NULL) makroCalcErsetzen(fv[q], MACRO_PARAMETER_LAENGE, keineParameter, 0, (f->anzahl == 0) ? f : NULL);
        }
    }
}

// 1, wenn text ein $AUFRUFNR als ganzes Wort enthaelt (hinter dem Wort kein Buchstabe, keine Ziffer, kein _; Doku 4.29)
static int quelltextHatAufrufNr(const char *text) {
    const char *p = text;
    while ((p = strstr(p, "$AUFRUFNR")) != NULL) {
        unsigned char c = (unsigned char)p[9];
        if (!(isalnum(c) || c == '_')) return 1;
        p += 9;
    }
    return 0;
}

// $AUFRUFNR im normalen Quelltext (ausserhalb eines Makroaufrufs, Doku 4.29, ab c82ass 1.01-024): Fehler wie bei $EXIT und $LOCAL;
// das Wort wird danach durch 0 ersetzt, damit kein Folgefehler "Operand ungueltig" entsteht. Kommentarzeilen und Kommentarfeld bleiben unveraendert.
static void quelltextAufrufNrPruefen(lineElements *z, int n, MakroFehler *f) {
    for (int j = 0; j < n; j++) {
        if (z[j].sp1[0] == ';' || z[j].sp1[0] == '#' || z[j].sp1[0] == '&') continue;
        char *fv[] = { z[j].sp1, z[j].sp2, z[j].sp3 };
        for (int q = 0; q < 3; q++) {
            char *pos = fv[q];
            while ((pos = strstr(pos, "$AUFRUFNR")) != NULL) {
                unsigned char c = (unsigned char)pos[9];
                if (isalnum(c) || c == '_') { pos += 9; continue; }
                makroAktuelleZeile = z[j].srcLine;
                makroMelde(f, "(Quelltext)", "$AUFRUFNR steht außerhalb eines Makroaufrufs");
                char rest[MACRO_PARAMETER_LAENGE];
                STRKOPIE(rest, pos + 9);
                snprintf(pos, MACRO_PARAMETER_LAENGE - (size_t)(pos - fv[q]), "0%s", rest);
                pos += 1;
            }
        }
    }
}

// ----------------------------------------------------------------------------------
// $-Direktiven im normalen Quelltext (Doku 4.1): $IF/$ELIF/$ELSE/$ENDIF, $REPT/$ENDREPT, $WHILE/$ENDWHILE, $SET, $INC, $DIM, $ERROR,
// $WARN, $NOTE, $DUMP und die Zeichenkettenfunktionen wirken wie im Makrorumpf: der Quelltext gilt als Rumpf eines Makros ohne
// Parameter. Die Auswertung laeuft nur, wenn mindestens eine Zeile mit $ beginnt; sonst bleibt linesAsm unveraendert und alle
// Programme ohne $-Zeile werden wie bisher uebersetzt. Aufrufe von Makros im Quelltext loest der Auswerter dabei an Ort und
// Stelle auf (makroAufrufHook), damit $SET und Aufrufe in Quelltextreihenfolge wirken. Die Auswertung laeuft auf einer Kopie,
// denn def(), art(), zellen() und abs/equ-Symbole in $CALC lesen den ganzen unveraenderten Quelltext (linesAsm).
// Die Direktivzeilen selbst entfallen (auch im Listing). Kommentare (Kommentarzeilen und Kommentarfeld) bleiben unveraendert.
// $EXIT, $LOCAL, $GLOBAL und $TRACE wirken im Quelltext nicht (Fehler bzw. Meldung wie ausserhalb eines Makros).
// Fehler stehen im Listing an der Zeile, an der sie entstanden (so zeigt der Fehlerort auf STDERR die Quelltextzeile); entfaellt diese
// Zeile im Ergebnis (Direktivzeile), steht sie im Fehlerfall als Kommentarzeile vor der Fehlermeldung.
void quelltextDirektivenAuswerten(void) {
    int hat = 0;
    for (int i = 0; i < lineCountAsm && !hat; i++) {
        const char *p = linesAsm[i].sp1;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '$') hat = 1;
        if (!hat && linesAsm[i].sp1[0] != ';' && (quelltextHatAufrufNr(linesAsm[i].sp1) || quelltextHatAufrufNr(linesAsm[i].sp2) || quelltextHatAufrufNr(linesAsm[i].sp3))) hat = 1;   // $AUFRUFNR im Quelltext (Doku 4.29)
    }
    if (!hat) return;

    const char *name = "(Quelltext)";
    int n = lineCountAsm;
    lineElements *arbeit = (lineElements *)malloc((size_t)(n > 0 ? n : 1) * sizeof(lineElements));
    MakroFehler *fehler = (MakroFehler *)calloc(1, sizeof(MakroFehler));   // gross: nicht auf den Stapel
    char (*keineParameter)[MACRO_PARAMETER_LAENGE] = (char (*)[MACRO_PARAMETER_LAENGE])calloc(64, (size_t)MACRO_PARAMETER_LAENGE);
    if (!arbeit || !fehler || !keineParameter) {
        fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
    lineElements *orig = (lineElements *)malloc((size_t)(n > 0 ? n : 1) * sizeof(lineElements));   // unveraenderter Quelltext: Text der Direktivzeile fuer die Ankerzeile einer Fehlermarke
    if (!orig) {
        fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }
    memcpy(orig, linesAsm, (size_t)n * sizeof(lineElements));
    memcpy(arbeit, linesAsm, (size_t)n * sizeof(lineElements));
    int lineCount = n;
    makroAktuelleZeile = 0;

    quelltextAufrufNrPruefen(arbeit, lineCount, fehler);
    arbeit = makroWiederholungenAufloesen(arbeit, &lineCount, keineParameter, 0, fehler, name);
    quelltextCalcErsetzen(arbeit, lineCount, keineParameter, fehler);
    makroWhileLabelsPruefen(arbeit, lineCount, fehler, name);
    arbeit = makroBedingungenAuswerten(arbeit, &lineCount, fehler, name, keineParameter, 0, 0);
    for (int j = 0; j < lineCount; j++) {   // $CALC mit $V(name): jetzt, da die Variablen ersetzt sind (nicht in Kommentaren)
        if (arbeit[j].sp1[0] == ';') continue;
        makroAktuelleZeile = arbeit[j].srcLine;
        char *fv[] = { arbeit[j].sp1, arbeit[j].sp2, arbeit[j].sp3 };
        for (int q = 0; q < 3; q++) if (strstr(fv[q], "$CALC") != NULL) makroCalcErsetzen(fv[q], MACRO_PARAMETER_LAENGE, keineParameter, 0, fehler);
    }

    // Ergebnis nach linesAsm. Eine Fehlerzeile steht im Listing an der Stelle der Zeile, an der der Fehler entstand; den Fehlerort
    // auf STDERR bildet meldeListingFehlerAufStderr aus der Quellzeile der naechstvorhergehenden echten Programmzeile (srcLine).
    //   - Steht im Ergebnis noch eine Zeile mit der Quelltextzeile des Fehlers (z. B. $CALC im Operanden), kommt die Fehlerzeile
    //     hinter die letzte Zeile dieser Quelltextzeile.
    //   - Entfaellt die Zeile (die Direktivzeile selbst: $ERROR, $INC, $LOCAL, $SET ...), steht an ihrer Stelle (vor der ersten
    //     Zeile mit hoeherer Quelltextzeile) eine Ankerzeile: die Direktivzeile als Kommentar mit ihrer srcLine, dahinter die Fehlerzeile.
    //   - Ohne Quelltextzeile (0) kommt die Fehlerzeile ans Ende.
    int gesamt = lineCount + 2 * fehler->anzahl;
    if (gesamt >= PROGRAMMZEILEN) {
        meldeZuVieleZeilen(0);
        exit(RC_FEHLER);
    }
    int vor[MAKRO_MAX_FEHLER];      // Index der Zeile in arbeit, vor der Fehler k eingefuegt wird (lineCount = am Ende)
    int anker[MAKRO_MAX_FEHLER];    // 1: vor Fehler k gehoert eine Ankerzeile (seine Quelltextzeile entfaellt im Ergebnis)
    for (int k = 0; k < fehler->anzahl; k++) {
        int zl = fehler->zeile[k];
        vor[k] = lineCount;
        anker[k] = 0;
        if (zl <= 0) continue;
        int gefunden = 0;
        for (int j = 0; j < lineCount && !gefunden; j++) {
            if (arbeit[j].srcLine != zl) continue;
            if (j + 1 >= lineCount || arbeit[j + 1].srcLine != zl) { vor[k] = j + 1; gefunden = 1; }
        }
        if (gefunden) continue;
        anker[k] = 1;
        for (int j = 0; j < lineCount; j++) {
            if (arbeit[j].srcLine > zl) { vor[k] = j; break; }
        }
    }
    int ankerZeile[MAKRO_MAX_FEHLER];   // Quelltextzeilen, zu denen schon eine Ankerzeile steht
    int ankerAnzahl = 0;
    int w = 0;
    for (int j = 0; j <= lineCount; j++) {
        for (int k = 0; k < fehler->anzahl; k++) {
            if (vor[k] != j) continue;
            int zl = fehler->zeile[k];
            if (anker[k]) {
                int da = 0;
                for (int a = 0; a < ankerAnzahl; a++) if (ankerZeile[a] == zl) da = 1;
                if (!da) {
                    ankerZeile[ankerAnzahl++] = zl;
                    memset(&linesAsm[w], 0, sizeof(lineElements));
                    for (int i = 0; i < n; i++) {
                        if (orig[i].srcLine != zl) continue;
                        char text[4 * MACRO_PARAMETER_LAENGE + 8];
                        snprintf(text, sizeof(text), ";%s%s%s%s%s%s%s", orig[i].sp1,
                                 orig[i].sp2[0] ? " " : "", orig[i].sp2, orig[i].sp3[0] ? " " : "", orig[i].sp3,
                                 orig[i].sp4[0] ? " " : "", orig[i].sp4);
                        STRKOPIE(linesAsm[w].sp1, text);
                        break;
                    }
                    linesAsm[w].srcLine = zl;
                    w++;
                }
            }
            memset(&linesAsm[w], 0, sizeof(lineElements));
            STRKOPIE(linesAsm[w].sp1, fehler->tab[k]);
            is_error0 = 1;
            w++;
        }
        if (j < lineCount) linesAsm[w++] = arbeit[j];
    }
    lineCountAsm = w;
    free(arbeit);
    free(orig);
    free(fehler);
    free(keineParameter);
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

    // Eindeutige Abbildung seed -> 3 Grossbuchstaben (26^3 = 17576 Werte, seed_max = 17000):
    //   a = seed mod 26, b1 = (seed / 26) mod 26, b2 = seed / 676
    //   Buchstabe i = (3a + 7i + [0, b1, b2]) mod 26
    // Fuer seed < 26 (b1 = b2 = 0) entspricht das der frueheren Abbildung (3*seed mod 26, dann + 7 je Stelle);
    // dort blieben bisher nur 26 verschiedene Suffixe uebrig, ab dem 27. Aufruf kollidierten die Labels.
    int s = seed < 0 ? 0 : seed % 17576;
    int a = s % 26;
    int b1 = (s / 26) % 26;
    int b2 = s / 676;
    int value = (3 * a) % 26;

    uuid[0] = charset[value % 26];
    uuid[1] = charset[(value + 7 + b1) % 26];
    uuid[2] = charset[(value + 14 + b2) % 26];
    uuid[3] = '\0'; // Nullterminator für gültigen String
    return uuid;
}

// -----------------------------------

// macht aus einem aufgelösten Macro in ERGEBNIS relative sprünge
// 1, wenn s mit einer Definition <name>%<Zusatz>: beginnt (Zusatz aus Buchstaben, Ziffern, _ ; z. B. ML0001%_2: oder schleife%:)
static int istMlLabelDef(const char *s) {
    int n = mlNameLaenge(s);
    if (n == 0) return 0;
    const char *q = s + n + 1;
    while (ML_IDZ(*q)) q++;
    return *q == ':';
}

// Von c82ass erzeugte lokale Labels (<name> + 3 Buchstaben + Zusatz), die nicht dem Muster ML<4 Ziffern> folgen;
// sie werden in der Meldung "nie verwendet" wie die ML-Labels nicht gemeldet (ca82_berichte.c)
static char (*erzeugteLabels)[LABEL_SIZE] = NULL;
static int erzeugteAnzahl = 0, erzeugteKapazitaet = 0;

static void makroLabelMerken(const char *name) {
    if (erzeugteAnzahl >= erzeugteKapazitaet) {
        int neuKap = erzeugteKapazitaet == 0 ? 256 : 2 * erzeugteKapazitaet;
        char (*tmp)[LABEL_SIZE] = (char (*)[LABEL_SIZE])realloc(erzeugteLabels, (size_t)neuKap * sizeof(*tmp));
        if (!tmp) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
        erzeugteLabels = tmp;
        erzeugteKapazitaet = neuKap;
    }
    strkopiere(erzeugteLabels[erzeugteAnzahl++], LABEL_SIZE, name);
}

int makroIstErzeugtesLabel(const char *name) {
    for (int k = 0; k < erzeugteAnzahl; k++) if (strcmp(erzeugteLabels[k], name) == 0) return 1;
    return 0;
}

// seed: Nummer des Makroaufrufs (bestimmt die Buchstaben); meldeUngueltig = 0: ungueltige Labels (mit % und :) nicht melden und
// unveraendert lassen (Vorlauf vor der Bedingungsauswertung), 1: melden (Endlauf)
void macroSprung1Aufloesen(lineElements **ergebnis, int *lineCount, char *mna, int seed, int meldeUngueltig) {

    MacroLabel *labelTable = (MacroLabel *)malloc(MAX_LABELS * sizeof(MacroLabel));   // Heap: Stapelgroesse bei verschachtelten Aufrufen
    if (!labelTable) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    int labelCount = 0;

    char *uuid = generate_uuid(seed);
    
    void modify_text(char *text, const char *uuid_in) {
        char temp[256];  
        char *pos = strchr(text, '%');  // Suche nach '%'

        if (pos) {
            size_t prefix_len = pos - text;  // Länge des Textes vor '%'
            snprintf(temp, sizeof(temp), "%.*s%s%s", (int)prefix_len, text, uuid_in, pos + 1);
            strkopiere(text, MACRO_PARAMETER_LAENGE, temp); 
        }
    }

    // Ersetzt ALLE Verwendungen von label_mit (<name>% mit Zusatz, ohne Doppelpunkt) durch <name> + uuid + Zusatz
    // (frueher nur die erste: "000 ML0001%+ML0001%" blieb halb ersetzt);
    // jeder Treffer muss am Ende ein Wortende haben (ML0001%_1 ist nicht der Anfang von ML0001%_10) und am Anfang ein Wortanfang
    // (ende% ist nicht der Schluss von weiterende%)
    void modify_text2(char *erg, const char *label_mit, const char *label_ohne, const char *uuid_in) {
        char temp[2 * MACRO_PARAMETER_LAENGE];
        size_t lm = strlen(label_mit);
        size_t o = 0;
        const char *p = erg;
        int geaendert = 0;
        while (*p != '\0' && o + 1 < sizeof(temp)) {
            const char *pos = strstr(p, label_mit);
            while (pos != NULL && (ML_IDZ(pos[lm]) || (pos > erg && ML_IDZ(pos[-1])))) pos = strstr(pos + 1, label_mit);
            if (pos == NULL) break;
            int n = snprintfGekuerzt(temp + o, sizeof(temp) - o, "%.*s%s%s%s", (int)(pos - p), p, label_ohne, uuid_in, label_mit + strlen(label_ohne) + 1);
            if (n < 0 || (size_t)n >= sizeof(temp) - o) { o = sizeof(temp) - 1; break; }
            o += (size_t)n;
            p = pos + lm;
            geaendert = 1;
        }
        if (!geaendert) return;
        snprintf(temp + o, sizeof(temp) - o, "%s", p);
        strkopiere(erg, MACRO_PARAMETER_LAENGE, temp);
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
    int whileTiefe = 0;   // Tiefe der offenen $WHILE-Rumpfe: Labels <name>% darin entstehen erst bei der Auswertung der Schleife (Doku 4.19)
    for (int kk = 0; kk < origCount; kk++) {
        lineElements *zeile = &(*ergebnis)[kk];
        const int imWhile = (whileTiefe > 0);
        if (makroErstesWort(zeile, "$WHILE")) whileTiefe++;
        else if (makroErstesWort(zeile, "$ENDWHILE") && whileTiefe > 0) whileTiefe--;

        if (zeile->sp1[0] == ';') {
            output[outCount++] = *zeile;
        }
        else if (zeile->sp1[0] == '$' || zeile->sp1[0] == '#' || zeile->sp1[0] == '&') {
            output[outCount++] = *zeile;   // Schluesselwortzeile ($IF, $ERROR ...): kein Label
        }
        else if (strchr(zeile->sp1, ':') && strchr(zeile->sp1, '%') && !istMlLabelDef(zeile->sp1)) {
            if (!meldeUngueltig) { output[outCount++] = *zeile; continue; }
            is_error0 = 1;
            output[outCount++] = *zeile;
            lineElements fehler = *zeile;
            macroFehlerausgabe(&fehler, 0, "Macrolabel muß aus einem Namen (Buchstabe oder `_` zuerst, dann Buchstaben, Ziffern, `_`; höchstens 24 Zeichen), `%` und einem Doppelpunkt bestehen (z.B.: ML0004%: oder schleife%:):", mna);
            output[outCount++] = fehler;
        }
        else if (imWhile && !meldeUngueltig && istMlLabelDef(zeile->sp1)) {
            output[outCount++] = *zeile;   // Label im Rumpf von $WHILE: bleibt im Vorlauf unveraendert, jeder Durchlauf erhaelt ein eigenes (whileLabelsErsetzen)
        }
        else if (istMlLabelDef(zeile->sp1))
        {
            // original-label mit doppelpunkt
            if (labelCount >= MAX_LABELS) { output[outCount++] = *zeile; continue; }
            STRKOPIE(labelTable[labelCount].label, zeile->sp1);
            labelCount++;
            // modifiziertes Label MIT Doppelpunkt.
            lineElements geaendert = *zeile;
            modify_text(geaendert.sp1, uuid);
            {   // lesbare Labels (nicht ML<4 Ziffern>) fuer die Meldung "nie verwendet" merken
                int nl = mlNameLaenge(zeile->sp1);
                int altes = (nl == 6 && zeile->sp1[0] == 'M' && zeile->sp1[1] == 'L' && isdigit((unsigned char)zeile->sp1[2]) &&
                             isdigit((unsigned char)zeile->sp1[3]) && isdigit((unsigned char)zeile->sp1[4]) && isdigit((unsigned char)zeile->sp1[5]));
                if (!altes) {
                    char gen[LABEL_SIZE];
                    strkopiere(gen, sizeof(gen), geaendert.sp1);
                    size_t gl = strlen(gen);
                    if (gl > 0 && gen[gl - 1] == ':') gen[gl - 1] = '\0';
                    makroLabelMerken(gen);
                }
            }
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
                { char *pc = strchr(label_ohne, '%'); if (pc) *pc = '\0'; }   // Name vor dem %
                STRKOPIE(label_mit,labelTable[k].label);
                if (label_mit[0] != '\0') label_mit[strlen(label_mit) - 1] = '\0';
                modify_text2(tempErgebnis[i].sp3, label_mit, label_ohne, uuid);
           }
        }
        copyLineElements(*ergebnis, tempErgebnis, i);
    }

    free(output);
    free(tempErgebnis);
    free(labelTable);
}

// -------------------

// Makroname ohne abschließenden Doppelpunkt (für Vergleiche und Meldungen)
static void macroNameOhneDoppelpunkt(const char *name, char *out, size_t groesse) {
    // kein strncpy: vermeidet -Wstringop-truncation (Name wird bewusst auf groesse-1 Zeichen gekuerzt)
    size_t len = strlen(name);
    if (len > groesse - 1) len = groesse - 1;
    memcpy(out, name, len);
    out[len] = '\0';
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

// Naechstes Wort der Namensliste hinter MACRO: bis zum naechsten Leerraum; bei name="Text mit Leerzeichen" (Vorgabe in Anfuehrungszeichen,
// schliessendes gleiches Zeichen vor Leerraum oder Ende) bis hinter das schliessende Zeichen (Doku 4.30). Setzt ein Endezeichen hinter das Wort,
// *pp zeigt danach hinter das Wort; NULL, wenn kein Wort mehr folgt.
static char *makroNamenWort(char **pp) {
    char *p = *pp;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0') { *pp = p; return NULL; }
    char *w = p;
    size_t nl = makroNameLaenge(p);
    if (nl > 0 && p[nl] == '=' && (p[nl + 1] == '"' || p[nl + 1] == '\'')) {
        char *e = strchr(p + nl + 2, p[nl + 1]);
        if (e != NULL && (e[1] == '\0' || e[1] == ' ' || e[1] == '\t')) {
            p = e + 1;
            if (*p != '\0') *p++ = '\0';
            *pp = p;
            return w;
        }
    }
    while (*p != '\0' && *p != ' ' && *p != '\t') p++;
    if (*p != '\0') *p++ = '\0';
    *pp = p;
    return w;
}

// Liest die Namensliste hinter MACRO (Doku 4.26) in m->macroParameters. params: die Angabe ohne Randleerraum (wird zerlegt),
// ort: Ortsangabe fuer die Meldung. Rueckgabe: Zahl der Namen. Ein Fehler wird einmal je Makro gemeldet (is_error0 = 1)
// und setzt m->benannt = -1; die Grenze 9 gilt nur fuer die Schreibweise mit Zahl.
// Ein Wort name=vorgabe vereinbart einen Schluesselwortparameter (Doku 4.30, ab c82ass 1.01-025): m->schluessel[k] = 1, m->vorgabe[k] = Vorgabe
// (ohne umschliessende Anfuehrungszeichen, leer erlaubt), m->schluesselAnzahl zaehlt sie. Er zaehlt wie jeder Name in der Reihenfolge der Vereinbarung.
static int makroNamenLesen(macroDefinitionen *m, const char *meldeName, char *params, const char *ort) {
    int n = 0;
    int plus = 0;
    char *sv = params;
    char grund[400] = "";
    m->benannt = 1;
    for (char *w = makroNamenWort(&sv); w != NULL && grund[0] == '\0'; w = makroNamenWort(&sv)) {
        size_t len = strlen(w);
        const char *gleich = strchr(w, '=');
        size_t nlen = (gleich != NULL) ? (size_t)(gleich - w) : len;   // Laenge des Namens (bei name=vorgabe ohne die Vorgabe)
        if (plus) {
            snprintf(grund, sizeof(grund), "Das Zeichen + steht nur als letztes Wort");
        } else if (len == 1 && w[0] == '+') {
            plus = 1;
            m->variabel = 1;
        } else if (strspn(w, "0123456789") == len) {
            snprintf(grund, sizeof(grund), "Hinter MACRO stehen Namen und die Zahl %.60s", w);
        } else if (makroNameLaenge(w) != nlen || nlen == 0 || nlen > MAKRO_NAME_MAX) {
            snprintf(grund, sizeof(grund), "Parametername '%.60s' ist ungueltig (Buchstabe oder _, dann Buchstaben, Ziffern oder _, hoechstens %d Zeichen)", w, MAKRO_NAME_MAX);
        } else if (makroFestesWort(w, nlen, 1)) {
            snprintf(grund, sizeof(grund), "Parametername '%.*s' ist ein festes Wort", (int)nlen, w);
        } else {
            for (int k = 0; k < n && k < MACRO_PARAMETER_ANZAHL; k++) {
                if (strlen(m->macroParameters[k]) == nlen && strncmp(m->macroParameters[k], w, nlen) == 0) {
                    snprintf(grund, sizeof(grund), "Parametername '%.*s' steht doppelt", (int)nlen, w);
                    break;
                }
            }
            if (grund[0] == '\0') {
                if (n < MACRO_PARAMETER_ANZAHL) {
                    snprintf(m->macroParameters[n], MACRO_PARAMETER_LAENGE, "%.*s", (int)nlen, w);
                    if (gleich != NULL) {   // Schluesselwortparameter name=vorgabe
                        const char *v = gleich + 1;
                        size_t vl = strlen(v);
                        m->schluessel[n] = 1;
                        if (vl >= 2 && (v[0] == '"' || v[0] == '\'') && v[vl - 1] == v[0]) snprintfGekuerzt(m->vorgabe[n], MACRO_PARAMETER_LAENGE, "%.*s", (int)(vl - 2), v + 1);
                        else snprintf(m->vorgabe[n], MACRO_PARAMETER_LAENGE, "%s", v);
                    }
                }
                if (gleich != NULL) m->schluesselAnzahl++;
                n++;
            }
        }
    }
    if (grund[0] == '\0' && n > MACRO_PARAMETER_ANZAHL) {
        snprintf(grund, sizeof(grund), "%d Parameternamen angegeben, zulaessig sind maximal %d", n, MACRO_PARAMETER_ANZAHL);
    }
    if (grund[0] != '\0') {
        is_error0 = 1;
        m->benannt = -1;
        PRINT_FEHLER("Makro %s: %s%s", meldeName, grund, ort);
        return 0;
    }
    return n;
}

// Uebersetzt in einer Zeile des Rumpfs (ein Feld) jedes $name in $k (k = 1 bis 9) bzw. $P(k) (k ab 10); $P(name) in $P(k),
// $LEN(name) in $LEN(k) (immer die Klammerform, damit $LEN(a)5 nicht zu $LEN15 wird) und $PR(name) in $PRk (Doku 4.26).
// Feste Woerter, $ vor Ziffer, Klammer, # oder Sonderzeichen und $P(...) / $LEN(...) mit einem Ausdruck bleiben stehen.
// Rueckgabe 0 = ok (Ergebnis in aus), 1 = Fehler mit Grund (aus unbrauchbar).
static int makroNamenFeld(const macroDefinitionen *m, const char *ein, char *aus, size_t ausGroesse, char *grund, size_t gg) {
    size_t n = 0;
    const char *q = ein;
    aus[0] = '\0';
    {   // $DEFAULT name wert: der Name hinter $DEFAULT hat kein $ und wird durch seine Nummer ersetzt (Ziffern bleiben)
        const char *d = ein;
        while (*d == ' ' || *d == '\t') d++;
        if (strncmp(d, "$DEFAULT", 8) == 0 && (d[8] == ' ' || d[8] == '\t')) {
            const char *w = d + 8;
            while (*w == ' ' || *w == '\t') w++;
            size_t len = makroNameLaenge(w);
            if (len > 0 && (w[len] == '\0' || w[len] == ' ' || w[len] == '\t')) {
                int k = makroNamenSuche(m, w, len);
                if (k == 0) {
                    snprintfGekuerzt(grund, gg, "$DEFAULT: Unbekannter Parametername %.*s", (int)len, w);
                    return 1;
                }
                size_t vorn = (size_t)(w - ein);
                if (vorn + 8 < ausGroesse) {
                    memcpy(aus, ein, vorn);
                    n = vorn + (size_t)snprintf(aus + vorn, ausGroesse - vorn, "%d", k);
                    q = w + len;
                }
            }
        }
    }
    while (*q != '\0') {
        if (n + 8 >= ausGroesse) break;
        if (*q != '$') { aus[n++] = *q++; aus[n] = '\0'; continue; }
        const char *w = q + 1;
        size_t len = makroNameLaenge(w);
        if (len == 0) { aus[n++] = *q++; aus[n] = '\0'; continue; }          // $ vor Ziffer, Klammer, # oder Sonderzeichen bleibt
        int istP = (len == 1 && w[0] == 'P'), istLen = (len == 3 && strncmp(w, "LEN", 3) == 0), istPr = (len == 2 && strncmp(w, "PR", 2) == 0);
        if (w[len] == '(' && (istP || istLen || istPr)) {                    // $P(name), $LEN(name), $PR(name)
            const char *i2 = w + len + 1;
            while (*i2 == ' ' || *i2 == '\t') i2++;
            size_t nl = makroNameLaenge(i2);
            const char *i3 = i2 + nl;
            while (*i3 == ' ' || *i3 == '\t') i3++;
            if (nl > 0 && *i3 == ')') {
                int k = makroNamenSuche(m, i2, nl);
                if (k > 0) {
                    n += (size_t)snprintf(aus + n, ausGroesse - n, istP ? "$P(%d)" : istLen ? "$LEN(%d)" : "$PR%d", k);
                    q = i3 + 1;
                    continue;
                }
                if (istPr) {
                    snprintfGekuerzt(grund, gg, "$PR(%.*s): kein Parametername dieses Makros", (int)nl, i2);
                    return 1;
                }
            } else if (istPr) {
                snprintf(grund, gg, "$PR( ) erwartet einen Parameternamen");
                return 1;
            }
            // $P(...) und $LEN(...) mit einem Ausdruck: bleibt stehen, die Namen darin werden einzeln ersetzt
        }
        if (makroFestesWort(w, len, 0)) {
            memcpy(aus + n, q, len + 1);
            n += len + 1;
            aus[n] = '\0';
            q = w + len;
            continue;
        }
        int k = makroNamenSuche(m, w, len);
        if (k == 0) {
            snprintfGekuerzt(grund, gg, "Unbekannter Parametername $%.*s", (int)len, w);
            return 1;
        }
        n += (size_t)snprintf(aus + n, ausGroesse - n, k <= 9 ? "$%d" : "$P(%d)", k);
        q = w + len;
    }
    if (*q != '\0' || n >= MACRO_PARAMETER_LAENGE) {
        snprintf(grund, gg, "Die Zeile ist nach dem Ersetzen der Parameternamen laenger als %d Zeichen", MACRO_PARAMETER_LAENGE - 1);
        return 1;
    }
    return 0;
}

// 1, wenn die (uebersetzte) Zeile ein $DEFAULT fuer einen Schluesselwortparameter ist (Doku 4.30): dessen Vorgabe steht schon in der MACRO-Zeile.
static int makroDefaultSchluesselFehler(const macroDefinitionen *m, const char *zeile, char *grund, size_t gg) {
    if (m->schluesselAnzahl <= 0) return 0;
    const char *d = zeile;
    while (*d == ' ' || *d == '\t') d++;
    if (strncmp(d, "$DEFAULT", 8) != 0 || !(d[8] == ' ' || d[8] == '\t')) return 0;
    d += 8;
    while (*d == ' ' || *d == '\t') d++;
    int k = 0;
    if (d[0] >= '1' && d[0] <= '9') {
        if (d[1] < '0' || d[1] > '9') k = d[0] - '0';
        else if (d[2] < '0' || d[2] > '9') k = (d[0] - '0') * 10 + (d[1] - '0');
    }
    if (k >= 1 && k <= MACRO_PARAMETER_ANZAHL && m->schluessel[k - 1]) {
        snprintf(grund, gg, "$DEFAULT fuer den Schluesselwortparameter %.40s ist nicht erlaubt (die Vorgabe steht in der MACRO-Zeile)", m->macroParameters[k - 1]);
        return 1;
    }
    return 0;
}

// Uebersetzt den Rumpf des Makros idx nach dem MEND (Doku 4.26): jedes $name wird zu $k bzw. $P(k). Kommentarzeilen mit ;
// und die Kommentarfelder werden mit uebersetzt (ein unbekanntes $wort ist auch dort ein Fehler), Zeilen mit # oder & nicht.
// Ein Fehler wird je Zeile gemeldet (is_error0 = 1) und setzt benannt = -1: der Aufruf des Makros entfaellt dann ohne Folgefehler.
static void makroNamenUebersetzen(int idx) {
    macroDefinitionen *m = &macros[idx];
    if (m->benannt != 1) return;
    char meldeName[MACRO_PARAMETER_LAENGE];
    strkopiere(meldeName, sizeof(meldeName), m->macroName);
    size_t ml = strlen(meldeName);
    if (ml > 0 && meldeName[ml - 1] == ':') meldeName[ml - 1] = '\0';
    int fehler = 0;
    for (int j = 0; j < m->macroLineCount; j++) {
        lineElements *z = &m->macroParsedLines[j];
        if (z->sp1[0] == '#' || z->sp1[0] == '&') continue;
        char *felder[4] = { z->sp1, z->sp2, z->sp3, z->sp4 };
        for (int f = 0; f < 4; f++) {
            if (strchr(felder[f], '$') == NULL) continue;
            char neu[4 * MACRO_PARAMETER_LAENGE];
            char grund[300];
            int rcFeld = makroNamenFeld(m, felder[f], neu, sizeof(neu), grund, sizeof(grund));
            if (rcFeld == 0 && f == 0) rcFeld = makroDefaultSchluesselFehler(m, neu, grund, sizeof(grund));
            if (rcFeld != 0) {
                char ort[MACRO_PARAMETER_LAENGE + 64];
                if (m->ausQuelltext) {
                    snprintf(ort, sizeof(ort), " [im Quelltext Zeile %s]", qOrt(z->srcLine > 0 ? z->srcLine : m->defZeile));
                } else {
                    snprintf(ort, sizeof(ort), " [definiert in %.200s:%d]", m->defDatei, m->defZeile);
                }
                is_error0 = 1;
                fehler = 1;
                PRINT_FEHLER("Makro %s: %s (Zeile: %.60s)%s", meldeName, grund, felder[f], ort);
                break;
            }
            strkopiere(felder[f], MACRO_PARAMETER_LAENGE, neu);
        }
    }
    if (fehler) m->benannt = -1;
}

// Legt ein Makro im Array `macros` an (gemeinsam genutzt von Makrodatei und Quelltext).
//   name:              Makroname wie in der Definition
//   paramsIn:          Rest hinter MACRO (Anzahl oder Wortliste), ggf. leer
//   zeilenKapazitaet:  Platz für die geparsten Makrozeilen
//   ausQuelltext:      Herkunft (1 = Quelltext, 0 = Makrodatei)
//   ersetzeIdx:        >= 0: das vorhandene Makro an dieser Stelle ersetzen, sonst -1 (neu anlegen)
//   ort:               Ortsangabe fuer Meldungen zu den Parameternamen (Doku 4.26), z. B. " [definiert in x.macro:12]"
// Rückgabe: Index des Makros.
static int macroAnlegen(const char *name, const char *paramsIn, int zeilenKapazitaet, int ausQuelltext, int ersetzeIdx, const char *ort) {
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
    macros[macroIndex].herkunft = ausQuelltext ? 1 : 0;
    macros[macroIndex].defDatei[0] = '\0';
    macros[macroIndex].defZeile = 0;
    macros[macroIndex].aufrufe = 0;
    macros[macroIndex].hatSpec = 0;      // $SPEC (Doku 4.32): Vorgaben TYP=Macro, ACTION=None, keine Klasse
    macros[macroIndex].specTyp = 0;
    macros[macroIndex].specClass[0] = '\0';
    macros[macroIndex].specAktion = 0;
    macros[macroIndex].benannt = 0;
    macros[macroIndex].schluesselAnzahl = 0;
    memset(macros[macroIndex].schluessel, 0, sizeof(macros[macroIndex].schluessel));

    char params[256];
    strncpy(params, paramsIn, sizeof(params) - 1);
    params[sizeof(params) - 1] = '\0';
    int paramCount = 0;
    macros[macroIndex].variabel = 0;
    {   // "MACRO n+" oder "MACRO +": n feste Parameter, danach beliebig viele (Doku 4.13)
        size_t pl = strlen(params);
        while (pl > 0 && (params[pl - 1] == ' ' || params[pl - 1] == '\t' || params[pl - 1] == '\r' || params[pl - 1] == '\n')) params[--pl] = '\0';
        if (pl > 0 && params[pl - 1] == '+' && strspn(params, "0123456789") == pl - 1) {
            macros[macroIndex].variabel = 1;
            params[pl - 1] = '\0';
            if (params[0] == '\0') STRKOPIE(params, "0");
        }
    }
    if (params[0] != '\0') {
        if (strspn(params, "0123456789") == strlen(params)) {
            paramCount = atoi(params);
        } else {   // Namen hinter MACRO (Doku 4.26)
            char meldeName[MACRO_PARAMETER_LAENGE];
            strncpy(meldeName, name, sizeof(meldeName) - 1);
            meldeName[sizeof(meldeName) - 1] = '\0';
            size_t meldeLen = strlen(meldeName);
            if (meldeLen > 0 && meldeName[meldeLen - 1] == ':') meldeName[meldeLen - 1] = '\0';
            paramCount = makroNamenLesen(&macros[macroIndex], meldeName, params, ort);
        }
    }
    // Doku 4: Es sind maximal 9 Parameter zulaessig ($1 ... $9); bei Namen gilt die Grenze 32 (Doku 4.26).
    if (paramCount > 9 && macros[macroIndex].benannt == 0) {
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

// $INCLUDE <Pfad> im Makrorumpf (Doku 4.14): die Zeilen der Datei werden an dieser Stelle in den Rumpf des Makros
// uebernommen. Der Pfad ist relativ zur Datei, die das $INCLUDE enthaelt (sonst wie angegeben); Tiefe hoechstens 4.
// Die eingebundene Datei enthaelt nur Rumpfzeilen (kein MACRO, kein MEND). Fehler: Meldung, is_error0 = 1.
#define MAKRO_INCLUDE_TIEFE 4
static void makroIncludeLesen(const char *zeile, const char *basisDatei, int basisZeile, int tiefe, int macroIndex) {
    char pfad[1024];
    const char *p = zeile + 8;                       // hinter "$INCLUDE"
    while (*p == ' ' || *p == '\t') p++;
    snprintf(pfad, sizeof(pfad), "%s", p);
    char *sem = strchr(pfad, ';');
    if (sem && (sem == pfad || sem[-1] == ' ' || sem[-1] == '\t')) *sem = '\0';
    size_t l = strlen(pfad);
    while (l > 0 && (pfad[l - 1] == ' ' || pfad[l - 1] == '\t' || pfad[l - 1] == '\r' || pfad[l - 1] == '\n')) pfad[--l] = '\0';
    if (l >= 2 && (pfad[0] == '"' || pfad[0] == '\'') && pfad[l - 1] == pfad[0]) { memmove(pfad, pfad + 1, l - 2); pfad[l - 2] = '\0'; }
    if (pfad[0] == '\0') {
        PRINT_FEHLER("%s Zeile %d: $INCLUDE braucht einen Pfad.", basisDatei, basisZeile);
        is_error0 = 1;
        return;
    }
    if (tiefe > MAKRO_INCLUDE_TIEFE) {
        PRINT_FEHLER("%s Zeile %d: $INCLUDE '%s' ist zu tief verschachtelt (höchstens %d).", basisDatei, basisZeile, pfad, MAKRO_INCLUDE_TIEFE);
        is_error0 = 1;
        return;
    }
    char voll[2048] = "";
    FILE *inc = NULL;
    int absolut = (pfad[0] == '/' || pfad[0] == '\\' || (isalpha((unsigned char)pfad[0]) && pfad[1] == ':'));
    if (!absolut) {
        snprintf(voll, sizeof(voll), "%s", basisDatei);
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
        PRINT_FEHLER("%s Zeile %d: $INCLUDE '%s' konnte nicht geöffnet werden: %s", basisDatei, basisZeile, pfad, strerror(errno));
        is_error0 = 1;
        return;
    }
    char zl[1024];
    int n = 0;
    while (fgets(zl, sizeof(zl), inc)) {
        n++;
        const char *t = zl;
        while (*t == ' ' || *t == '\t') t++;
        if (strncmp(t, "$INCLUDE", 8) == 0 && (t[8] == ' ' || t[8] == '\t')) {
            makroIncludeLesen(t, voll, n, tiefe + 1, macroIndex);
        } else {
            processLine(zl, macros[macroIndex].macroParsedLines, &(macros[macroIndex].macroLineCount));
        }
    }
    fclose(inc);
}

// ---------------------------------------------------------------------------
// Spezifikationszeile $SPEC (ab c82ass 1.03-002, Doku 4.32):
//   $SPEC [TYP={Macro|Aufruf|LoadMakro|Eingebettet|M|A|L|E}] [CLASS=<Grossbuchstaben, Ziffern, _>] [ACTION={None|Load}]
// Je Makro hoechstens eine Zeile, als erste Zeile des Rumpfs unmittelbar hinter MACRO (Kommentar- und Leerzeilen zaehlen nicht).
// Angaben in beliebiger Reihenfolge, jede hoechstens einmal, Schreibweise genau wie gezeigt. Die Zeile wird nicht in den Rumpf
// uebernommen. Vorgaben: TYP=Macro, ACTION=None, keine Klasse. TYP=LoadMakro und ACTION=Load werden gespeichert, haben noch keine Wirkung. TYP=Eingebettet (E, ab 1.03-004): Assembler-Hilfskonstrukt ohne Einmalerzeugungs-Pruefung, wie TYP=Aufruf ohne Warnung ($BLOCK nach den bestehenden Regeln).
// ---------------------------------------------------------------------------
static int specFehlerDatei = 0;   // Fehler in $SPEC-Zeilen der Makrodateien (c82ass.makros und ;#MACRODATEIn=); pass0 fragt sie ab

int makroSpecFehler(void) { return specFehlerDatei; }

// 1, wenn der Text (ohne fuehrenden Leerraum) mit dem Schluesselwort $SPEC als ganzem Wort beginnt
static int makroTextIstSpec(const char *t) {
    return strncmp(t, "$SPEC", 5) == 0 && (t[5] == ' ' || t[5] == '\t' || t[5] == '\0' || t[5] == '\n' || t[5] == '\r' || t[5] == ';');
}

// 1, wenn die Rumpfzeile Kommentar oder leer ist (zaehlt fuer die Stellung der $SPEC-Zeile nicht als Zeile)
static int makroZeileIstKommentarOderLeer(const lineElements *z) {
    if (z->sp1[0] == ';' || z->sp1[0] == '#') return 1;
    return z->sp1[0] == '\0' && z->sp2[0] == '\0' && z->sp3[0] == '\0' && z->sp4[0] == '\0';
}

// Wertet den Text hinter $SPEC aus und traegt ihn in das Makro ein. ort = Ortsangabe fuer die Meldungen ("Makrodatei x, Zeile n" oder
// "Zeile n"). begonnen = 1, wenn vor der Zeile schon eine Rumpfzeile steht, die weder Kommentar noch leer ist. Rueckgabe: Zahl der Fehler.
static int makroSpecAuswerten(macroDefinitionen *mk, const char *rest, const char *ort, int begonnen) {
    char name[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(mk->macroName, name, sizeof(name));
    if (mk->hatSpec) {
        PRINT_FEHLER("%s: Makro %s hat mehr als eine Spezifikationszeile $SPEC (je Makro genau eine, Doku 4.32).", ort, name);
        return 1;
    }
    if (begonnen) {
        PRINT_FEHLER("%s: $SPEC im Makro %s steht nicht unmittelbar hinter der MACRO-Zeile (Kommentar- und Leerzeilen dürfen davor stehen, Doku 4.32).", ort, name);
        return 1;
    }
    char text[512];
    snprintf(text, sizeof(text), "%s", rest);
    char *semi = strchr(text, ';');
    if (semi) *semi = '\0';
    int fehler = 0, sTyp = 0, sCls = 0, sAkt = 0;
    int typ = 0, akt = 0;
    char cls[32] = "";
    char *save = NULL;
    for (char *tok = strtok_r(text, " \t\r\n", &save); tok; tok = strtok_r(NULL, " \t\r\n", &save)) {
        char *gl = strchr(tok, '=');
        if (!gl) {
            PRINT_FEHLER("%s: $SPEC im Makro %s: '%s' ist keine Angabe der Form SCHLÜSSEL=WERT (erlaubt: TYP, CLASS, ACTION, Doku 4.32).", ort, name, tok);
            fehler++; continue;
        }
        *gl = '\0';
        const char *key = tok, *val = gl + 1;
        if (strcmp(key, "TYP") == 0) {
            if (sTyp++) { PRINT_FEHLER("%s: $SPEC im Makro %s: TYP steht mehr als einmal.", ort, name); fehler++; continue; }
            if (strcmp(val, "Macro") == 0 || strcmp(val, "M") == 0) typ = 0;
            else if (strcmp(val, "Aufruf") == 0 || strcmp(val, "A") == 0) typ = 1;
            else if (strcmp(val, "LoadMakro") == 0 || strcmp(val, "L") == 0) typ = 2;
            else if (strcmp(val, "Eingebettet") == 0 || strcmp(val, "E") == 0) typ = 3;
            else { PRINT_FEHLER("%s: $SPEC im Makro %s: TYP=%s ist ungültig (erlaubt: Macro, Aufruf, LoadMakro, Eingebettet oder M, A, L, E).", ort, name, val); fehler++; }
        } else if (strcmp(key, "ACTION") == 0) {
            if (sAkt++) { PRINT_FEHLER("%s: $SPEC im Makro %s: ACTION steht mehr als einmal.", ort, name); fehler++; continue; }
            if (strcmp(val, "None") == 0) akt = 0;
            else if (strcmp(val, "Load") == 0) akt = 1;
            else { PRINT_FEHLER("%s: $SPEC im Makro %s: ACTION=%s ist ungültig (erlaubt: None, Load).", ort, name, val); fehler++; }
        } else if (strcmp(key, "CLASS") == 0) {
            if (sCls++) { PRINT_FEHLER("%s: $SPEC im Makro %s: CLASS steht mehr als einmal.", ort, name); fehler++; continue; }
            size_t n = strlen(val);
            int ok = (n > 0 && n < sizeof(cls));
            for (size_t i = 0; ok && i < n; i++) if (!((val[i] >= 'A' && val[i] <= 'Z') || (val[i] >= '0' && val[i] <= '9') || val[i] == '_')) ok = 0;
            if (ok) snprintf(cls, sizeof(cls), "%s", val);
            else { PRINT_FEHLER("%s: $SPEC im Makro %s: CLASS=%s ist ungültig (Großbuchstaben, Ziffern und _, 1 bis %d Zeichen).", ort, name, val, (int)sizeof(cls) - 1); fehler++; }
        } else {
            PRINT_FEHLER("%s: $SPEC im Makro %s: Schlüsselwort '%s' ist unbekannt (erlaubt: TYP, CLASS, ACTION; Groß- und Kleinschreibung zählt).", ort, name, key);
            fehler++;
        }
    }
    if (fehler == 0) {
        mk->hatSpec = 1;
        mk->specTyp = typ;
        mk->specAktion = akt;
        snprintf(mk->specClass, sizeof(mk->specClass), "%s", cls);
    }
    return fehler;
}

// Warnung (Doku 4.32): Ein Makro mit $SPEC und TYP=Macro erzeugt seinen Rumpf nur einmal; erkennbar ist das am $GLOBAL-Merker
// oder am $BLOCK im Rumpf. Fehlt beides, wird gewarnt. Bei TYP=Aufruf und TYP=Eingebettet wird nichts geprueft.
static void makroSpecPruefen(const macroDefinitionen *mk, const char *ort) {
    if (!mk->hatSpec || mk->specTyp != 0) return;
    for (int j = 0; j < mk->macroLineCount; j++) {
        const char *s1 = mk->macroParsedLines[j].sp1;
        if (strncmp(s1, "$GLOBAL", 7) == 0 || strncmp(s1, "$BLOCK", 6) == 0) return;
    }
    char name[MACRO_PARAMETER_LAENGE];
    macroNameOhneDoppelpunkt(mk->macroName, name, sizeof(name));
    PRINT_WARNUNG("%s: Makro %s hat $SPEC mit TYP=Macro, der Rumpf enthält aber weder $GLOBAL noch $BLOCK: eine Einmalerzeugung ist nicht erkennbar (Doku 4.32).", ort, name);
}

// 1, wenn die Zeile einer Makrodatei das Makroende ist: Operation MEND, MACROENDE oder macroende (als ganzes Wort, ein Label davor ist
// erlaubt). Kommentarzeilen (;, #) und Schluesselwortzeilen ($, &) sowie Woerter, die MEND nur enthalten (z. B. "AMEND" in einem
// Kommentar), sind kein Makroende (frueher beendete jedes Vorkommen der Zeichenfolge MEND in der Zeile das Makro).
static int makroZeileIstEnde(const char *zeile) {
    const char *p = zeile;
    while (*p == ' ' || *p == '\t') p++;
    if (*p == ';' || *p == '#' || *p == '$' || *p == '&' || *p == '\0' || *p == '\n' || *p == '\r') return 0;
    for (int wort = 0; wort < 2; wort++) {
        const char *e = p;
        while (*e != '\0' && *e != ' ' && *e != '\t' && *e != ';' && *e != '\n' && *e != '\r') e++;
        size_t n = (size_t)(e - p);
        if (wort == 0 && n > 0 && p[n - 1] == ':') {   // Label: das naechste Wort ist die Operation
            p = e;
            while (*p == ' ' || *p == '\t') p++;
            continue;
        }
        return (n == 4 && strncmp(p, "MEND", 4) == 0) || (n == 9 && (strncmp(p, "MACROENDE", 9) == 0 || strncmp(p, "macroende", 9) == 0));
    }
    return 0;
}

// Liest die Makrodefinitionen aus einer geoeffneten Makrodatei ins Array `macros` (schliesst die Datei nicht).
// Die Zeile `name MACRO <Parameter>` endet beim ersten ';' (Kommentar), wie der Operand im Quelltext (ab 1.01-007).
//   herkunft 0: c82ass.makros (ein doppelter Name ist ein Fehler, das zweite Makro wird uebersprungen)
//   herkunft 2: projektspezifische Makrodatei (;#MACRODATEIn=): ein gleichnamiges Makro aus c82ass.makros wird fuer diesen
//               Lauf ersetzt (Warnung); ein gleichnamiges Makro einer Datei mit kleinerer Nummer bleibt bestehen (Warnung).
static void makroDateiEinlesen(FILE *macroFile, const char *macroFileName, int herkunft) {
    char lineBuffer[1024];
    int macroActive = 0;
    int macroIndex = -1;
    int dateiZeile = 0;   // Zeilennummer in der Makrodatei (fuer Fehlerorte)
    int rumpfBegonnen = 0;   // 1, sobald im Rumpf eine Zeile steht, die weder Kommentar noch leer ist ($SPEC muss davor stehen, Doku 4.32)

    while (fgets(lineBuffer, sizeof(lineBuffer), macroFile)) {
        dateiZeile++;
        if (*lineBuffer == '\0' || strcmp(lineBuffer, "\n") == 0) {
            continue;
        }

        // Extrahiere den Makronamen und überprüfe auf Duplikate
        char name[MACRO_PARAMETER_LAENGE] = "", macro[16] = "", params[256] = "";

        {   // "name: MACRO;Kommentar" ohne Leerzeichen (ab 1.01-031 wie im Quelltext erlaubt): hinter MACRO ein Leerzeichen einfuegen
            char *q = lineBuffer;
            while (*q == ' ' || *q == '\t') q++;
            while (*q != '\0' && *q != ' ' && *q != '\t') q++;   // Name
            while (*q == ' ' || *q == '\t') q++;
            if (strncmp(q, "MACRO;", 6) == 0 && strlen(lineBuffer) + 1 < sizeof(lineBuffer)) {
                memmove(q + 6, q + 5, strlen(q + 5) + 1);
                q[5] = ' ';
            }
        }
        int scannedFields = sscanf(lineBuffer, "%255s %15s %255[^\n]", name, macro, params);   // Feldbreiten: macro[16] lief über
        if (scannedFields >= 2 && strcmp(macro, "MACRO") == 0) {
            // Kommentar hinter MACRO (ab 1.01-007, Doku 4.9): Wie im Quelltext endet die Parameterangabe beim ersten ';';
            // der Leerraum davor faellt weg. Ohne diese Kuerzung zaehlte jedes Wort des Kommentars als Parameter.
            {
                char *semikolon = strchr(params, ';');
                if (semikolon) *semikolon = '\0';
                size_t pl = strlen(params);
                while (pl > 0 && (params[pl - 1] == ' ' || params[pl - 1] == '\t' || params[pl - 1] == '\r')) params[--pl] = '\0';
            }
            int vorhanden = macroSuche(name);
            int ersetze = -1;      // >= 0: vorhandenes Makro aus c82ass.makros ersetzen
            int ueberspringe = 0;
            if (vorhanden >= 0) {
                char klar[MACRO_PARAMETER_LAENGE];
                macroNameOhneDoppelpunkt(name, klar, sizeof(klar));
                if (herkunft == 2 && macros[vorhanden].herkunft == 0) {
                    PRINT_WARNUNG("Makro %s aus c82ass.makros wird für diesen Lauf durch die Definition in der Makrodatei %s (Zeile %d) ersetzt.", klar, macroFileName, dateiZeile);
                    ersetze = vorhanden;
                } else if (herkunft == 2 && macros[vorhanden].herkunft == 2 && strcmp(macros[vorhanden].defDatei, macroFileName) != 0) {
                    PRINT_WARNUNG("Makro %s ist schon in der Makrodatei %s definiert; die Definition in %s (Zeile %d) wird ignoriert.", klar, macros[vorhanden].defDatei, macroFileName, dateiZeile);
                    ueberspringe = 1;
                } else {
                    fprintf(stderr, "Fehler: Makro '%s' wurde bereits definiert! Überspringe bis zum Ende des Makros.\n", name);
                    ueberspringe = 1;
                }
            }

            if (ueberspringe) {
                // Überspringe alle Zeilen bis zum nächsten Makroende
                while (fgets(lineBuffer, sizeof(lineBuffer), macroFile)) {
                    dateiZeile++;
                    if (makroZeileIstEnde(lineBuffer)) {
                        break;
                    }
                }
                continue;
            }

            // Falls kein Duplikat gefunden wurde (oder ersetzt wird), speichere das neue Makro
            char ort[MACRO_PARAMETER_LAENGE + 64];
            snprintf(ort, sizeof(ort), " [definiert in %.200s:%d]", macroFileName, dateiZeile);
            macroIndex = macroAnlegen(name, params, MACRODEFINITIONEN, 0, ersetze, ort);
            macros[macroIndex].herkunft = herkunft;
            snprintf(macros[macroIndex].defDatei, sizeof(macros[macroIndex].defDatei), "%s", macroFileName);
            macros[macroIndex].defZeile = dateiZeile;
            macroActive = 1;
            rumpfBegonnen = 0;
            continue;
        }

        // Falls wir in einem Makro sind
        if (macroActive) {
            {   // $SPEC: Spezifikationszeile des Makros (Doku 4.32); sie kommt nicht in den Rumpf
                const char *t = lineBuffer;
                while (*t == ' ' || *t == '\t') t++;
                if (makroTextIstSpec(t)) {
                    char ort[MACRO_PARAMETER_LAENGE + 300];
                    snprintf(ort, sizeof(ort), "Makrodatei %.200s, Zeile %d", macroFileName, dateiZeile);
                    specFehlerDatei += makroSpecAuswerten(&macros[macroIndex], t + 5, ort, rumpfBegonnen);
                    rumpfBegonnen = 1;   // eine weitere $SPEC-Zeile wird als zweite gemeldet (hatSpec), eine fehlerhafte als falsch platziert
                    continue;
                }
                if (*t != ';' && *t != '#' && *t != '\0' && *t != '\n' && *t != '\r') rumpfBegonnen = 1;
            }
            {   // $INCLUDE <Pfad>: Zeilen einer anderen Datei in den Rumpf uebernehmen (Doku 4.14)
                const char *t = lineBuffer;
                while (*t == ' ' || *t == '\t') t++;
                if (strncmp(t, "$INCLUDE", 8) == 0 && (t[8] == ' ' || t[8] == '\t')) {
                    makroIncludeLesen(t, macroFileName, dateiZeile, 1, macroIndex);
                    continue;
                }
            }
            if (makroZeileIstEnde(lineBuffer)) {
                processLine(lineBuffer, macros[macroIndex].macroParsedLines, &(macros[macroIndex].macroLineCount));  
                macroActive = 0;
                makroNamenUebersetzen(macroIndex);   // benannte Parameter: $name -> $k (Doku 4.26)
                {
                    char ort[MACRO_PARAMETER_LAENGE + 300];
                    snprintf(ort, sizeof(ort), "Makrodatei %.200s, Zeile %d", macroFileName, macros[macroIndex].defZeile);
                    makroSpecPruefen(&macros[macroIndex], ort);
                }
                continue;
            }

            // Bearbeitet nur die 1. Zeile des Macros
            processLine(lineBuffer, macros[macroIndex].macroParsedLines, &(macros[macroIndex].macroLineCount)); 
        }
    }
    if (macroActive) makroNamenUebersetzen(macroIndex);   // MEND fehlt: der Rumpf wird trotzdem uebersetzt (Doku 4.26)
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

    makroDateiEinlesen(macroFile, macroFileName, 0);
    fclose(macroFile);
}

// Anweisung ;#MAKROLOKAL=1 (oder =0) im Quelltext (Kommentarzeile, ab c82ass 1.02-001, Doku 4.31): schaltet fuer den ganzen Lauf ein, dass
// $SET und $DIM in einem Makroaufruf lokale Variablen und Felder anlegen (Vorgabe 0 = global wie bisher). Die Zeile darf nur einmal
// vorkommen (auch =0 zaehlt), in der Hauptdatei und in $INCLUDE-Dateien. ;#MAKROLOKALX und aehnliche Woerter sind kein Pragma.
// Muss vor dem Einlesen der Makrodateien und dem Aufloesen der Makros laufen. Rueckgabe: Anzahl der Fehler (Meldungen sind schon ausgegeben).
int ladeMakroLokalSchalter(void) {
    static const char marke[] = "#MAKROLOKAL";
    int fehler = 0;
    int gesehenZeile = 0;   // Quelltextzeile der ersten Anweisung, 0 = noch keine
    mMakroLokal = 0;
    for (int i = 0; i < lineCountAsm; i++) {
        const char *p = linesAsm[i].sp1;
        if (*p != ';') continue;
        p++;
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, marke, sizeof(marke) - 1) != 0) continue;
        p += sizeof(marke) - 1;
        if (*p != '=' && *p != ' ' && *p != '\t' && *p != '\0' && *p != '\r') continue;   // ;#MAKROLOKALX: kein Pragma
        if (gesehenZeile != 0) {
            PRINT_FEHLER("Zeile %s: ;#MAKROLOKAL steht schon in Zeile %s (die Anweisung darf nur einmal vorkommen).", qOrt(linesAsm[i].srcLine), qOrt(gesehenZeile));
            fehler++;
            continue;
        }
        gesehenZeile = linesAsm[i].srcLine;
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '=') {
            PRINT_FEHLER("Zeile %s: ;#MAKROLOKAL ohne '=' (Syntax ;#MAKROLOKAL=1).", qOrt(linesAsm[i].srcLine));
            fehler++;
            continue;
        }
        p++;
        while (*p == ' ' || *p == '\t') p++;
        const char wert = *p;
        const char *q = p + 1;
        while (*q == ' ' || *q == '\t' || *q == '\r') q++;
        if ((wert != '0' && wert != '1') || (*q != '\0' && *q != ';')) {
            char rest[80];
            snprintf(rest, sizeof(rest), "%.60s", p);
            size_t l = strlen(rest);
            while (l > 0 && (rest[l - 1] == ' ' || rest[l - 1] == '\t' || rest[l - 1] == '\r')) rest[--l] = '\0';
            PRINT_FEHLER("Zeile %s: ;#MAKROLOKAL=%s ist ungueltig (erlaubt sind ;#MAKROLOKAL=1 und ;#MAKROLOKAL=0).", qOrt(linesAsm[i].srcLine), rest);
            fehler++;
            continue;
        }
        mMakroLokal = (wert == '1');
    }
    return fehler;
}

// Schalter ;#MAKROUMORDNEN=YES oder =NO im Quelltext (ab c82ass 1.03-007, Doku 5.6): YES = der Optimierer verlegt die Rumpfbloecke von
// Makros mit $SPEC TYP=M hinter end; NO = nicht. Ohne die Zeile gilt MAKRO_UMORDNEN_VORGABE. Die Zeile darf nur einmal vorkommen, in der
// Hauptdatei und in $INCLUDE-Dateien; Gross-/Kleinschreibung des Werts ist gleich. Mit --no-opt gibt es ohnehin keine Umordnung.
// Muss vor dem Optimierer laufen (Pass 0). Rueckgabe: Anzahl der Fehler (Meldungen sind schon ausgegeben).
int ladeMakroUmordnenSchalter(void) {
    static const char marke[] = "#MAKROUMORDNEN";
    int fehler = 0;
    int gesehenZeile = 0;   // Quelltextzeile der ersten Anweisung, 0 = noch keine
    optMakroUmordnen = MAKRO_UMORDNEN_VORGABE;
    for (int i = 0; i < lineCountAsm; i++) {
        const char *p = linesAsm[i].sp1;
        if (*p != ';') continue;
        p++;
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, marke, sizeof(marke) - 1) != 0) continue;
        p += sizeof(marke) - 1;
        if (*p != '=' && *p != ' ' && *p != '\t' && *p != '\0' && *p != '\r') continue;   // ;#MAKROUMORDNENX: kein Pragma
        if (gesehenZeile != 0) {
            PRINT_FEHLER("Zeile %s: ;#MAKROUMORDNEN steht schon in Zeile %s (die Anweisung darf nur einmal vorkommen).", qOrt(linesAsm[i].srcLine), qOrt(gesehenZeile));
            fehler++;
            continue;
        }
        gesehenZeile = linesAsm[i].srcLine;
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '=') {
            PRINT_FEHLER("Zeile %s: ;#MAKROUMORDNEN ohne '=' (Syntax ;#MAKROUMORDNEN=YES oder ;#MAKROUMORDNEN=NO).", qOrt(linesAsm[i].srcLine));
            fehler++;
            continue;
        }
        p++;
        while (*p == ' ' || *p == '\t') p++;
        char wort[8];
        size_t l = 0;
        while (p[l] != '\0' && p[l] != ' ' && p[l] != '\t' && p[l] != ';' && p[l] != '\r' && l < sizeof(wort) - 1) { wort[l] = (char)tolower((unsigned char)p[l]); l++; }
        wort[l] = '\0';
        const char *q = p + l;
        while (*q == ' ' || *q == '\t' || *q == '\r') q++;
        int ja = (strcmp(wort, "yes") == 0), nein = (strcmp(wort, "no") == 0);
        if ((!ja && !nein) || (*q != '\0' && *q != ';')) {
            char rest[80];
            snprintf(rest, sizeof(rest), "%.60s", p);
            size_t r = strlen(rest);
            while (r > 0 && (rest[r - 1] == ' ' || rest[r - 1] == '\t' || rest[r - 1] == '\r')) rest[--r] = '\0';
            PRINT_FEHLER("Zeile %s: ;#MAKROUMORDNEN=%s ist ungueltig (erlaubt sind ;#MAKROUMORDNEN=YES und ;#MAKROUMORDNEN=NO).", qOrt(linesAsm[i].srcLine), rest);
            fehler++;
            continue;
        }
        optMakroUmordnen = ja;
    }
    return fehler;
}

// Anweisungen ;#PRECOMMAND=<Wert> und ;#POSTCOMMAND=<Wert> im Quelltext (ab c82ass 1.03-009, Doku 3.1e): Befehlsworte fuer den .obj-Lochstreifen.
// <Wert> besteht aus den Ziffern 0 bis 9 und Punkten und endet mit einem Punkt (z. B. 212000.). Er wird unveraendert als Lochbilder geschrieben:
// alle PRECOMMAND in der Reihenfolge des Quelltexts vor das erste Wort, alle POSTCOMMAND hinter das letzte Wort, noch vor das Endekennzeichen "/".
// Beide duerfen mehrfach vorkommen, in der Hauptdatei und in $INCLUDE-Dateien. Bei --ABSPR (.kep statt .obj) werden sie nicht ausgegeben.
#define OBJBEF_MAX 64          // hoechstens so viele Anweisungen je Art
#define OBJBEF_LEN 80          // hoechstens so viele Zeichen je Wert
static char objPre[OBJBEF_MAX][OBJBEF_LEN + 1];
static char objPost[OBJBEF_MAX][OBJBEF_LEN + 1];
static int objPreAnz = 0, objPostAnz = 0;

// Liest alle Zeilen ;#<name>=<Wert> nach arr; Rueckgabe: Anzahl Fehler.
static int ladeObjBefehlArt(const char *marke, char arr[][OBJBEF_LEN + 1], int *anz) {
    const size_t ml = strlen(marke);
    int fehler = 0;
    *anz = 0;
    for (int i = 0; i < lineCountAsm; i++) {
        const char *p = linesAsm[i].sp1;
        if (*p != ';') continue;
        p++;
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, marke, ml) != 0) continue;
        p += ml;
        if (*p != '=' && *p != ' ' && *p != '\t' && *p != '\0' && *p != '\r') continue;   // ;#PRECOMMANDX: kein Pragma
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '=') {
            PRINT_FEHLER("Zeile %s: ;%s ohne '=' (Syntax ;%s=<Ziffern und Punkte>, z. B. ;%s=212000.).", qOrt(linesAsm[i].srcLine), marke, marke, marke);
            fehler++;
            continue;
        }
        p++;
        while (*p == ' ' || *p == '\t') p++;
        size_t l = 0;
        while (p[l] != '\0' && p[l] != ' ' && p[l] != '\t' && p[l] != ';' && p[l] != '\r') l++;
        const char *q = p + l;
        while (*q == ' ' || *q == '\t' || *q == '\r') q++;
        int ok = (l > 0 && *q == '\0') || (l > 0 && *q == ';');
        for (size_t k = 0; ok && k < l; k++) if (!((p[k] >= '0' && p[k] <= '9') || p[k] == '.')) ok = 0;
        if (!ok || p[l - 1] != '.') {
            PRINT_FEHLER("Zeile %s: ;%s=%.60s ist ungueltig (erlaubt sind Ziffern 0 bis 9 und Punkte; der Wert muss mit einem Punkt enden, z. B. ;%s=212000.).",
                         qOrt(linesAsm[i].srcLine), marke, l > 0 ? p : "", marke);
            fehler++;
            continue;
        }
        if (l > OBJBEF_LEN) {
            PRINT_FEHLER("Zeile %s: ;%s: der Wert hat %d Zeichen, erlaubt sind hoechstens %d.", qOrt(linesAsm[i].srcLine), marke, (int)l, OBJBEF_LEN);
            fehler++;
            continue;
        }
        if (*anz >= OBJBEF_MAX) {
            PRINT_FEHLER("Zeile %s: ;%s kommt zu oft vor (hoechstens %d Zeilen).", qOrt(linesAsm[i].srcLine), marke, OBJBEF_MAX);
            fehler++;
            continue;
        }
        memcpy(arr[*anz], p, l);
        arr[*anz][l] = '\0';
        (*anz)++;
    }
    return fehler;
}

int ladeObjBefehle(void) {
    int fehler = ladeObjBefehlArt("#PRECOMMAND", objPre, &objPreAnz);
    fehler += ladeObjBefehlArt("#POSTCOMMAND", objPost, &objPostAnz);
    if (absprAktiv && (objPreAnz > 0 || objPostAnz > 0))
        PRINT_WARNUNG("%s", "Bei --ABSPR werden ;#PRECOMMAND und ;#POSTCOMMAND nicht ausgegeben (es gibt keinen .obj-Streifen, nur .kep).");
    return fehler;
}

void schreibeObjPre(FILE *f)  { for (int i = 0; i < objPreAnz; i++)  schreibeLochbilder(f, objPre[i]); }
void schreibeObjPost(FILE *f) { for (int i = 0; i < objPostAnz; i++) schreibeLochbilder(f, objPost[i]); }

// Anweisungen ;#MACRODATEI1=<pfad> bis ;#MACRODATEI9=<pfad> im Quelltext (Kommentarzeile): projektspezifische Makrodateien.
// Der Pfad ist der Rest der Zeile (ohne Randleerraum). Ein relativer Pfad wird zuerst im Verzeichnis der Quelldatei,
// dann im Arbeitsverzeichnis gesucht. Die Dateien werden in der Reihenfolge 1 bis 9 geladen, nach c82ass.makros und vor den
// Makros im Quelltext. Suchreihenfolge eines Makros daher: Quelltext, MACRODATEI1 bis 9, c82ass.makros.
// Rueckgabe: Anzahl der Fehler (Meldungen sind schon ausgegeben).
int ladeProjektMakrodateien(void) {
    extern char inputFileName[1024];
    static const char marke[] = "#MACRODATEI";
    char pfad[10][1024];
    int  zeile[10];
    int  fehler = 0;
    for (int n = 0; n < 10; n++) { pfad[n][0] = '\0'; zeile[n] = 0; }

    for (int i = 0; i < lineCountAsm; i++) {
        const char *p = linesAsm[i].sp1;
        if (*p != ';') continue;
        p++;
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, marke, sizeof(marke) - 1) != 0) continue;
        p += sizeof(marke) - 1;
        if (*p < '1' || *p > '9' || (p[1] != '=' && p[1] != ' ' && p[1] != '\t')) {
            PRINT_FEHLER("Zeile %s: ;#MACRODATEI muss ;#MACRODATEI1=<Pfad> bis ;#MACRODATEI9=<Pfad> lauten.", qOrt(linesAsm[i].srcLine));
            fehler++;
            continue;
        }
        int n = *p - '0';
        p++;
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '=') {
            PRINT_FEHLER("Zeile %s: ;#MACRODATEI%d ohne '=' (Syntax ;#MACRODATEI%d=<Pfad>).", qOrt(linesAsm[i].srcLine), n, n);
            fehler++;
            continue;
        }
        p++;
        while (*p == ' ' || *p == '\t') p++;
        char rest[1024];
        snprintf(rest, sizeof(rest), "%s", p);
        size_t l = strlen(rest);
        while (l > 0 && (rest[l - 1] == ' ' || rest[l - 1] == '\t' || rest[l - 1] == '\r')) rest[--l] = '\0';
        if (rest[0] == '\0') {
            PRINT_FEHLER("Zeile %s: ;#MACRODATEI%d ohne Pfad.", qOrt(linesAsm[i].srcLine), n);
            fehler++;
            continue;
        }
        if (pfad[n][0] != '\0') {
            PRINT_FEHLER("Zeile %s: ;#MACRODATEI%d ist schon in Zeile %s angegeben.", qOrt(linesAsm[i].srcLine), n, qOrt(zeile[n]));
            fehler++;
            continue;
        }
        snprintf(pfad[n], sizeof(pfad[n]), "%s", rest);
        zeile[n] = linesAsm[i].srcLine;
    }

    for (int n = 1; n <= 9; n++) {
        if (pfad[n][0] == '\0') continue;
        FILE *f = NULL;
        char voll[2048] = "";
        int absolut = (pfad[n][0] == '/' || pfad[n][0] == '\\' || (isalpha((unsigned char)pfad[n][0]) && pfad[n][1] == ':'));
        if (!absolut) {
            // erst im Verzeichnis der Quelldatei
            snprintf(voll, sizeof(voll), "%s", inputFileName);
            char *slash = strrchr(voll, '/');
            char *bslash = strrchr(voll, '\\');
            if (bslash && (!slash || bslash > slash)) slash = bslash;
            if (slash) {
                slash[1] = '\0';
                size_t rest = sizeof(voll) - strlen(voll) - 1;
                strncat(voll, pfad[n], rest);
                f = fopen(voll, "r");
            }
        }
        if (!f) {
            snprintf(voll, sizeof(voll), "%s", pfad[n]);   // sonst wie angegeben (Arbeitsverzeichnis oder absolut)
            f = fopen(voll, "r");
        }
        if (!f) {
            PRINT_FEHLER("Zeile %s: Makrodatei ;#MACRODATEI%d '%s' konnte nicht geoeffnet werden (gesucht im Verzeichnis der Quelldatei und im Arbeitsverzeichnis): %s",
                         qOrt(zeile[n]), n, pfad[n], strerror(errno));
            fehler++;
            continue;
        }
        makroDateiEinlesen(f, voll, 2);
        fclose(f);
    }
    return fehler;
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
        if (vorhanden >= 0 && macros[vorhanden].herkunft == 2) {
            PRINT_WARNUNG("Makro %s aus der Makrodatei %s wird für diesen Lauf durch die Definition im Quelltext ersetzt.", defName, macros[vorhanden].defDatei);
        } else if (vorhanden >= 0) {
            PRINT_WARNUNG("Makro %s aus der Makrodatei wird für diesen Lauf durch die Definition im Quelltext ersetzt.", defName);
        }

        // Rumpf einschließlich MEND-Zeile übernehmen, genau wie bei den Makros der Makrodatei
        char ortQ[64];
        snprintf(ortQ, sizeof(ortQ), " [im Quelltext Zeile %s]", qOrt(linesAsm[i].srcLine));
        int idx = macroAnlegen(linesAsm[i].sp1, linesAsm[i].sp3, ende - i, 1, vorhanden, ortQ);
        memcpy(macros[idx].macroParsedLines, &linesAsm[i + 1], (ende - i) * sizeof(lineElements));
        macros[idx].macroLineCount = ende - i;
        macros[idx].defZeile = linesAsm[i].srcLine;   // Zeile der MACRO-Anweisung im Quelltext
        {   // $SPEC (Doku 4.32): Spezifikationszeile auswerten und aus dem Rumpf nehmen (sie wird zur Kommentarzeile)
            int begonnen = 0;
            for (int k = 0; k < macros[idx].macroLineCount; k++) {
                lineElements *z = &macros[idx].macroParsedLines[k];
                if (makroTextIstSpec(z->sp1)) {   // Direktivzeilen ($...) stehen als ganze Zeile in sp1
                    char rest[MACRO_PARAMETER_LAENGE + 8];
                    snprintf(rest, sizeof(rest), "%s", z->sp1 + 5);
                    char ort[64];
                    snprintf(ort, sizeof(ort), "Zeile %s", qOrt(z->srcLine));
                    fehler += makroSpecAuswerten(&macros[idx], rest, ort, begonnen);
                    snprintf(z->sp1, sizeof(z->sp1), ";$SPEC (Spezifikationszeile, Doku 4.32)");
                    z->sp2[0] = z->sp3[0] = z->sp4[0] = '\0';
                    begonnen = 1;
                } else if (!makroZeileIstKommentarOderLeer(z)) {
                    begonnen = 1;
                }
            }
            char ort[64];
            snprintf(ort, sizeof(ort), "Zeile %s", qOrt(linesAsm[i].srcLine));
            makroSpecPruefen(&macros[idx], ort);
        }
        makroNamenUebersetzen(idx);                   // benannte Parameter: $name -> $k (Doku 4.26)

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


// Herkunft eines Makros als Text: "Quelltext, Zeile n", "Projektdatei <Pfad>, Zeile n" oder "<Pfad von c82ass.makros>, Zeile n".
static void makroHerkunftFormat(int herkunft, const char *datei, int zeile, char *ziel, size_t n) {
    if (herkunft == 1) {
        if (zeile > 0) snprintf(ziel, n, "Quelltext, Zeile %s", qOrt(zeile));
        else snprintf(ziel, n, "Quelltext");
    } else if (herkunft == 2) {
        snprintf(ziel, n, "Projektdatei %s, Zeile %d", datei, zeile);
    } else {
        snprintf(ziel, n, "%s, Zeile %d", datei[0] ? datei : "c82ass.makros", zeile);
    }
}

// Herkunft des Makros "opcode" (Name ohne Doppelpunkt) fuer die Aufrufzeile im Listing (--makros).
// Rueckgabe 1 = Makro gefunden, ziel enthaelt den Text; 0 = unbekannt, ziel leer.
int makroHerkunftFuerAufruf(const char *opcode, char *ziel, size_t n) {
    if (n > 0) ziel[0] = '\0';
    for (int i = 0; i < macroCount; i++) {
        char name[MACRO_PARAMETER_LAENGE];
        macroNameOhneDoppelpunkt(macros[i].macroName, name, sizeof(name));
        if (strcmp(name, opcode) != 0) continue;
        makroHerkunftFormat(macros[i].herkunft, macros[i].defDatei, macros[i].defZeile, ziel, n);
        return 1;
    }
    return 0;
}

// ---------------------------------------------------------------------------
// Makroliste (--makros): welche Makros wurden in diesem Lauf wie oft aufgerufen und woher stammen sie.
// Die Makrotabelle wird nach Pass 0 freigegeben, deshalb wird die Liste vorher gesichert.
// ---------------------------------------------------------------------------
typedef struct {
    char name[MACRO_PARAMETER_LAENGE];
    int aufrufe;
    int herkunft;
    char datei[1024];
    int zeile;
} MakroListenEintrag;

static MakroListenEintrag *makroListe = NULL;
static int makroListeAnzahl = 0;

// Sichert Name, Aufrufzahl und Herkunft aller Makros (auch der nicht aufgerufenen).
void makroListeSichern(void) {
    free(makroListe);
    makroListe = NULL;
    makroListeAnzahl = 0;
    if (macroCount <= 0) return;
    makroListe = (MakroListenEintrag *)calloc((size_t)macroCount, sizeof(MakroListenEintrag));
    if (!makroListe) return;
    for (int i = 0; i < macroCount; i++) {
        macroNameOhneDoppelpunkt(macros[i].macroName, makroListe[i].name, sizeof(makroListe[i].name));
        makroListe[i].aufrufe = macros[i].aufrufe;
        makroListe[i].herkunft = macros[i].herkunft;
        snprintf(makroListe[i].datei, sizeof(makroListe[i].datei), "%s", macros[i].defDatei);
        makroListe[i].zeile = macros[i].defZeile;
    }
    makroListeAnzahl = macroCount;
}

// Gibt die Makroliste aus (STDOUT und .log): zuerst die aufgerufenen, dann die nicht aufgerufenen Makros
// der Quelltext- und Projektdateien (c82ass.makros wird nur mit den aufgerufenen Makros aufgefuehrt).
void makroListeAusgeben(void) {
    berichtPrintf("Makroliste\n\n");
    berichtPrintf("%-24s | %7s | %s\n", "Makro", "Aufrufe", "Herkunft");
    berichtPrintf("%-24s | %7s | %s\n", "------------------------", "-------", "--------");
    int ausgegeben = 0;
    for (int durchlauf = 0; durchlauf < 2; durchlauf++) {
        for (int i = 0; i < makroListeAnzahl; i++) {
            MakroListenEintrag *m = &makroListe[i];
            if (durchlauf == 0 && m->aufrufe == 0) continue;
            if (durchlauf == 1 && (m->aufrufe != 0 || m->herkunft == 0)) continue;
            char herkunft[1200];
            makroHerkunftFormat(m->herkunft, m->datei, m->zeile, herkunft, sizeof(herkunft));
            berichtPrintf("%-24s | %7d | %s\n", m->name, m->aufrufe, herkunft);
            ausgegeben++;
        }
    }
    if (ausgegeben == 0) berichtPrintf("(keine Makros aufgerufen)\n");
    free(makroListe);
    makroListe = NULL;
    makroListeAnzahl = 0;
}
