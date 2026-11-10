// ca82_opsym.c - Namen fuer Operationscodes (OPSYM), Version siehe ca82_version.h
// Teil des C8205-Assemblers c82ass. Doku: Assemblerdokumentation 3.3.17, Anforderung C8205_Anforderung_OPSYM.md.
//
// Ein markierter Name steht im Operationscode-Feld mit vorangestelltem Punkt (.LD, .STO, .JMP). Der Punkt ist in
// Symbolen nicht erlaubt; der Namensraum ist deshalb von Anweisungen, Makros und Symbolen getrennt.
// Die Namen werden nach Pass 0 (also im Quelltext und in den Makrorümpfen) durch den dreistelligen Oktalcode
// ersetzt; alle weiteren Paesse sehen nur den Code. Der Name bleibt in lineElements.opname und erscheint
// nur in Listing, .dmp und .test (copyAndIncrementLineElementsX); .mqo, .obj, .kep, .sym und .log tragen den Code.
//
// Quellen der Namen:
//   - Standardtabelle c82ass.opsym (wird beim ersten markierten Namen geladen; Suche: aktuelles Verzeichnis, sonst
//     Sourcecode/ (wie c82ass.makros), zuletzt neben dem Programm: Verzeichnis des Binarys, dann dessen ../Sourcecode/
//     (ab 1.00-066; damit findet auch ein Aufruf aus einem anderen Verzeichnis die Tabelle)),
//   - Namensdateien ;#OPSYM=<Pfad> im Quelltext (bis 9 Zeilen; Pfad relativ zur Quelldatei),
//   - Zeilen  NAME: opsym <code>  im Quelltext (gelten ab dieser Zeile).
#include "ca82_intern.h"

#define OPSYM_NAME_MAX   8      // Zeichen je Name
#define OPSYM_MAX        1024   // Namen insgesamt
#define OPSYM_QUELLEN    12     // Standardtabelle + 9 Namensdateien + Reserve
#define OPSYM_PRAGMAS    9      // ;#OPSYM=-Zeilen
#define OPSYM_STANDARD   "c82ass.opsym"

typedef struct {
    char name[OPSYM_NAME_MAX + 1];   // Grossbuchstaben, ohne Punkt
    int  code;                       // 0 bis 0777
    int  quelle;                     // Index in quellen[]; -1 = Zeile "NAME: opsym <code>" im Quelltext
    int  zeile;                      // Zeile in der Namensdatei bzw. im Quelltext
    char kommentar[200];             // Text hinter ';' (beginnt in der Standardtabelle mit "Nr. <n>")
} OpsymEintrag;

static OpsymEintrag tab[OPSYM_MAX];
static int          tabN = 0;
static char         quellen[OPSYM_QUELLEN][1024];   // gelesene Namensdateien (Pfad wie geoeffnet)
static int          quellenN = 0;
static int          standardFehlt = 0;   // 1 = Standardtabelle nicht ladbar (einmal gemeldet; keine Folgemeldungen je Name)

// ---------------------------------------------------------------------------------------------------------------
// Hilfen

// Fehlermeldung mit Ort (Datei:Zeile des Quelltexts); beendet Pass 0 spaeter ueber is_error0.
static void opsymFehler(int quellzeile, const char *format, ...) {
    char text[600];
    va_list ap;
    va_start(ap, format);
    vsnprintf(text, sizeof(text), format, ap);
    va_end(ap);
    is_error0 = 1;
    fehlerMitOrt(quellzeile, text);
}

// Name nach 3.2 ohne Doppelpunkt: Buchstabe oder '_' zuerst, dann Buchstaben, Ziffern, '_'; hoechstens 8 Zeichen.
static int opsymNameGueltig(const char *s) {
    size_t l = strlen(s);
    if (l == 0 || l > OPSYM_NAME_MAX) return 0;
    if (!(isalpha((unsigned char)s[0]) || s[0] == '_')) return 0;
    for (size_t i = 1; i < l; i++) {
        if (!(isalnum((unsigned char)s[i]) || s[i] == '_')) return 0;
    }
    return 1;
}

static void opsymGross(char *ziel, size_t groesse, const char *s) {
    size_t i = 0;
    for (; s[i] != '\0' && i + 1 < groesse; i++) ziel[i] = (char)toupper((unsigned char)s[i]);
    ziel[i] = '\0';
}

// Dreistelliger Oktalcode 000 bis 777 (genau drei Ziffern 0 bis 7).
static int opsymCode(const char *s, int *code) {
    if (strlen(s) != 3) return 0;
    for (int i = 0; i < 3; i++) if (s[i] < '0' || s[i] > '7') return 0;
    *code = (s[0] - '0') * 64 + (s[1] - '0') * 8 + (s[2] - '0');
    return 1;
}

static OpsymEintrag *opsymSuche(const char *nameGross) {
    for (int i = 0; i < tabN; i++) if (strcmp(tab[i].name, nameGross) == 0) return &tab[i];
    return NULL;
}

static int opsymQuelleNeu(const char *pfad) {
    if (quellenN >= OPSYM_QUELLEN) return OPSYM_QUELLEN - 1;
    STRKOPIE(quellen[quellenN], pfad);
    return quellenN++;
}

// Beschreibt die Herkunft eines Eintrags fuer Meldungen.
static void opsymHerkunft(const OpsymEintrag *e, char *ziel, size_t groesse) {
    if (e->quelle >= 0) snprintf(ziel, groesse, "Namensdatei %s, Zeile %d", quellen[e->quelle], e->zeile);
    else                snprintf(ziel, groesse, "Quelltextzeile %s", qOrt(e->zeile));
}

// Traegt einen Namen ein. Derselbe Name mit demselben Code ist erlaubt (nichts geschieht), mit anderem Code ein
// Fehler (O-25). Rueckgabe: 0 = in Ordnung, 1 = Fehler (schon gemeldet).
static int opsymEintragen(const char *nameGross, int code, int quelle, int zeile, const char *kom, int quellzeile) {
    OpsymEintrag *alt = opsymSuche(nameGross);
    if (alt != NULL) {
        if (alt->code == code) return 0;
        char wo[1100], neu[1100];
        opsymHerkunft(alt, wo, sizeof(wo));
        OpsymEintrag e;
        e.quelle = quelle; e.zeile = zeile;
        opsymHerkunft(&e, neu, sizeof(neu));
        opsymFehler(quellzeile, "Name %s ist doppelt mit verschiedenem Code vergeben: %03o (%s) und %03o (%s).",
                    nameGross, alt->code, wo, code, neu);
        return 1;
    }
    if (tabN >= OPSYM_MAX) {
        opsymFehler(quellzeile, "Zu viele Namen für Operationscodes (höchstens %d).", OPSYM_MAX);
        return 1;
    }
    OpsymEintrag *e = &tab[tabN++];
    STRKOPIE(e->name, nameGross);
    e->code = code;
    e->quelle = quelle;
    e->zeile = zeile;
    STRKOPIE(e->kommentar, kom);
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------
// Namensdatei lesen: Zeilen "<NAME> <code> [; Kommentar]", Leerzeilen und Kommentarzeilen mit ';'

static void opsymLiesDatei(FILE *f, int quelle, int quellzeile) {
    char zeile[1024];
    int nr = 0;
    while (fgets(zeile, sizeof(zeile), f) != NULL) {
        nr++;
        char kom[200] = "";
        char *sem = strchr(zeile, ';');
        if (sem != NULL) {
            char *k = sem + 1;
            while (*k == ' ' || *k == '\t') k++;
            STRKOPIE(kom, k);
            trimWhitespace(kom);
            *sem = '\0';
        }
        // Byte-Order-Mark am Dateianfang uebergehen
        char *z = zeile;
        if (nr == 1 && (unsigned char)z[0] == 0xEF && (unsigned char)z[1] == 0xBB && (unsigned char)z[2] == 0xBF) z += 3;
        char wort[3][128];
        int n = sscanf(z, "%127s %127s %127s", wort[0], wort[1], wort[2]);
        if (n <= 0) continue;
        if (n != 2) {
            opsymFehler(quellzeile, "Namensdatei %s, Zeile %d: erwartet wird <NAME> <code> (dreistelliger Oktalcode), optional mit Kommentar hinter ';'.",
                        quellen[quelle], nr);
            continue;
        }
        char name[OPSYM_NAME_MAX + 1];
        int code = 0;
        if (!opsymNameGueltig(wort[0])) {
            opsymFehler(quellzeile, "Namensdatei %s, Zeile %d: Name '%s' ist ungültig (Buchstabe oder _ zuerst, dann Buchstaben, Ziffern, _; höchstens %d Zeichen).",
                        quellen[quelle], nr, wort[0], OPSYM_NAME_MAX);
            continue;
        }
        if (!opsymCode(wort[1], &code)) {
            opsymFehler(quellzeile, "Namensdatei %s, Zeile %d: Code '%s' ist kein dreistelliger Oktalcode (000 bis 777).",
                        quellen[quelle], nr, wort[1]);
            continue;
        }
        opsymGross(name, sizeof(name), wort[0]);
        opsymEintragen(name, code, quelle, nr, kom, quellzeile);
    }
}

// Verzeichnis des laufenden Programms mit abschliessendem Schraegstrich (leer, wenn nicht ermittelbar). Wird in main()
// einmal gesetzt und nur fuer die Suche der Standardtabelle neben dem Binary benutzt (ab 1.00-066).
static char programmVerz[1024] = "";

void opsymProgrammpfadSetzen(const char *argv0) {
    char pfad[1024] = "";
#ifdef _WIN32
    DWORD n = GetModuleFileNameA(NULL, pfad, (DWORD)sizeof(pfad));
    if (n == 0 || n >= (DWORD)sizeof(pfad)) pfad[0] = '\0';
#else
    ssize_t n = readlink("/proc/self/exe", pfad, sizeof(pfad) - 1);
    if (n > 0) pfad[n] = '\0'; else pfad[0] = '\0';
#endif
    if (pfad[0] == '\0' && argv0 != NULL) snprintf(pfad, sizeof(pfad), "%s", argv0);   // sonst der Aufrufpfad
    char *slash = strrchr(pfad, '/');
#ifdef _WIN32
    char *bslash = strrchr(pfad, '\\');
    if (bslash && (!slash || bslash > slash)) slash = bslash;
#endif
    if (slash == NULL) { programmVerz[0] = '\0'; return; }   // Aufruf ueber PATH ohne Pfad: nichts zu suchen
    slash[1] = '\0';
    snprintf(programmVerz, sizeof(programmVerz), "%s", pfad);
}

// Oeffnet die Standardtabelle: erst im aktuellen Verzeichnis, sonst unter Sourcecode/ (wie c82ass.makros), zuletzt neben
// dem Programm (<Verzeichnis des Binarys>c82ass.opsym, dann <Verzeichnis des Binarys>../Sourcecode/c82ass.opsym).
static FILE *opsymOeffneStandard(char *pfad, size_t groesse) {
    snprintf(pfad, groesse, "%s", OPSYM_STANDARD);
    FILE *f = fopen(pfad, "r");
    if (f == NULL) {
        snprintf(pfad, groesse, "Sourcecode/%s", OPSYM_STANDARD);
        f = fopen(pfad, "r");
    }
    if (f == NULL && programmVerz[0] != '\0') {
        snprintf(pfad, groesse, "%s%s", programmVerz, OPSYM_STANDARD);
        f = fopen(pfad, "r");
        if (f == NULL) {
            snprintf(pfad, groesse, "%s../Sourcecode/%s", programmVerz, OPSYM_STANDARD);
            f = fopen(pfad, "r");
        }
    }
    return f;
}

// Standardtabelle laden. Rueckgabe: 0 = geladen, 1 = Fehler (gemeldet).
static int opsymLadeStandard(int quellzeile) {
    char pfad[1100];
    FILE *f = opsymOeffneStandard(pfad, sizeof(pfad));
    if (f == NULL) {
        opsymFehler(quellzeile, "Die Standardtabelle %s für markierte Namen konnte weder im aktuellen Verzeichnis noch unter Sourcecode/ noch neben dem Programm geöffnet werden.",
                    OPSYM_STANDARD);
        standardFehlt = 1;
        return 1;
    }
    int q = opsymQuelleNeu(pfad);
    opsymLiesDatei(f, q, quellzeile);
    fclose(f);
    return 0;
}

// Namensdatei aus ;#OPSYM=<Pfad>: relativ zur Quelldatei, sonst wie angegeben (Arbeitsverzeichnis oder absolut).
static void opsymLadeProjektdatei(const char *pfad, int quellzeile) {
    FILE *f = NULL;
    char voll[10240] = "";
    int absolut = (pfad[0] == '/' || pfad[0] == '\\' || (isalpha((unsigned char)pfad[0]) && pfad[1] == ':'));
    if (!absolut) {
        snprintf(voll, sizeof(voll), "%s", inputFileName);
        char *slash = strrchr(voll, '/');
        char *bslash = strrchr(voll, '\\');
        if (bslash && (!slash || bslash > slash)) slash = bslash;
        if (slash) {
            slash[1] = '\0';
            size_t rest = sizeof(voll) - strlen(voll) - 1;
            strncat(voll, pfad, rest);
            f = fopen(voll, "r");
        }
    }
    if (f == NULL) {
        snprintfGekuerzt(voll, sizeof(voll), "%s", pfad);
        f = fopen(voll, "r");
    }
    if (f == NULL) {
        opsymFehler(quellzeile, ";#OPSYM '%s': Namensdatei konnte nicht geöffnet werden (gesucht im Verzeichnis der Quelldatei und im Arbeitsverzeichnis): %s",
                    pfad, strerror(errno));
        return;
    }
    int q = opsymQuelleNeu(voll);
    opsymLiesDatei(f, q, quellzeile);
    fclose(f);
}

// ---------------------------------------------------------------------------------------------------------------
// Pragma ;#OPSYM=<Pfad> erkennen. Rueckgabe: 0 = keine OPSYM-Zeile, 1 = Pfad in pfad, -1 = Syntaxfehler (gemeldet).
static int opsymPragma(const lineElements *z, char *pfad, size_t groesse) {
    static const char marke[] = "#OPSYM";
    const char *p = z->sp1;
    if (*p != ';') return 0;
    p++;
    while (*p == ' ' || *p == '\t') p++;
    if (strncmp(p, marke, sizeof(marke) - 1) != 0) return 0;
    p += sizeof(marke) - 1;
    if (*p != '=' && *p != ' ' && *p != '\t') return 0;   // z. B. ;#OPSYMBOL ist kein Pragma dieser Art
    while (*p == ' ' || *p == '\t') p++;
    if (*p != '=') {
        opsymFehler(z->srcLine, ";#OPSYM ohne '=' (Syntax ;#OPSYM=<Pfad>).");
        return -1;
    }
    p++;
    while (*p == ' ' || *p == '\t') p++;
    snprintf(pfad, groesse, "%s", p);
    size_t l = strlen(pfad);
    while (l > 0 && (pfad[l - 1] == ' ' || pfad[l - 1] == '\t' || pfad[l - 1] == '\r')) pfad[--l] = '\0';
    if (pfad[0] == '\0') {
        opsymFehler(z->srcLine, ";#OPSYM ohne Pfad.");
        return -1;
    }
    return 1;
}

// Kommentar-, Pragma- und Fehlerzeilen sowie Leerzeilen tragen keinen Operationscode.
static int opsymKeinBefehl(const lineElements *z) {
    char c = z->sp1[0];
    if (c == ';' || c == '#' || c == '$' || c == '&') return 1;
    if (strstr(z->sp1, "***") != NULL) return 1;
    return z->sp2[0] == '\0';
}

// Liste der geladenen Namensquellen fuer die Meldung "unbekannt".
static void opsymQuellenText(char *ziel, size_t groesse) {
    ziel[0] = '\0';
    for (int i = 0; i < quellenN; i++) {
        if (i > 0) stranhaengen(ziel, groesse, ", ");
        stranhaengen(ziel, groesse, quellen[i]);
    }
    if (quellenN == 0) snprintf(ziel, groesse, "keine");
}

// ---------------------------------------------------------------------------------------------------------------
// Aufruf am Ende von Pass 0: ersetzt alle markierten Namen in lineAsmAufgeloest durch den Code (O-20).
void opsymErsetzeNamen(void) {
    int n = lineCountAsmAufgeloest;
    int erstesMarkiert = -1;
    char pfade[OPSYM_PRAGMAS][1024];
    int  pfadZeile[OPSYM_PRAGMAS];
    int  pfadN = 0;

    // Vorlauf: opname leeren, Pragmas sammeln, ersten markierten Namen finden
    for (int i = 0; i < n; i++) {
        lineAsmAufgeloest[i].opname[0] = '\0';
        char pfad[1024];
        int r = opsymPragma(&lineAsmAufgeloest[i], pfad, sizeof(pfad));
        if (r > 0) {
            if (pfadN >= OPSYM_PRAGMAS) {
                opsymFehler(lineAsmAufgeloest[i].srcLine, "Mehr als %d Zeilen ;#OPSYM=<Pfad>.", OPSYM_PRAGMAS);
            } else {
                STRKOPIE(pfade[pfadN], pfad);
                pfadZeile[pfadN] = lineAsmAufgeloest[i].srcLine;
                pfadN++;
            }
            continue;
        }
        if (r < 0) continue;
        if (erstesMarkiert < 0 && !opsymKeinBefehl(&lineAsmAufgeloest[i]) &&
            lineAsmAufgeloest[i].sp2[0] == '.' && lineAsmAufgeloest[i].sp2[1] != '\0') {
            erstesMarkiert = i;
        }
    }

    // Ohne markierte Namen, Pragmas und opsym-Zeilen bleibt alles wie bisher; die Standardtabelle wird nicht geoeffnet (O-03).
    if (erstesMarkiert >= 0) opsymLadeStandard(lineAsmAufgeloest[erstesMarkiert].srcLine);
    for (int k = 0; k < pfadN; k++) opsymLadeProjektdatei(pfade[k], pfadZeile[k]);

    // Hauptlauf in Quelltextreihenfolge: opsym-Zeilen vereinbaren Namen (ab dieser Zeile), markierte Namen werden ersetzt.
    for (int i = 0; i < n; i++) {
        lineElements *z = &lineAsmAufgeloest[i];
        if (opsymKeinBefehl(z)) continue;

        if (gleichOhneGrossKlein(z->sp2, "opsym")) {
            char name[OPSYM_NAME_MAX + 1] = "";
            int code = 0;
            char marke[MACRO_PARAMETER_LAENGE];
            STRKOPIE(marke, z->sp1);
            size_t ml = strlen(marke);
            if (ml > 0 && marke[ml - 1] == ':') marke[--ml] = '\0';
            if (ml == 0 || !opsymNameGueltig(marke)) {
                opsymFehler(z->srcLine, "opsym verlangt vor dem Wort einen Namen mit Doppelpunkt (NAME: opsym <code>; Buchstabe oder _ zuerst, höchstens %d Zeichen).", OPSYM_NAME_MAX);
            } else if (!opsymCode(z->sp3, &code)) {
                opsymFehler(z->srcLine, "opsym %s: '%s' ist kein dreistelliger Oktalcode (000 bis 777).", marke, z->sp3);
            } else {
                opsymGross(name, sizeof(name), marke);
                opsymEintragen(name, code, -1, z->srcLine, "", z->srcLine);
            }
            // Die Zeile belegt nichts und ist kein Symbol: sie wird zur Kommentarzeile.
            char text[MACRO_PARAMETER_LAENGE];
            snprintf(text, sizeof(text), ";%s %s %s", z->sp1, z->sp2, z->sp3);
            STRKOPIE(z->sp1, text);
            STRKOPIE(z->sp2, "");
            STRKOPIE(z->sp3, "");
            continue;
        }

        if (z->sp2[0] == '.' && z->sp2[1] != '\0') {
            char name[OPSYM_NAME_MAX + 2];
            OpsymEintrag *e = NULL;
            if (opsymNameGueltig(z->sp2 + 1)) {
                opsymGross(name, sizeof(name), z->sp2 + 1);
                e = opsymSuche(name);
            }
            if (e == NULL && standardFehlt) continue;   // Ursache ist schon gemeldet
            if (e == NULL) {
                char quellText[1100];
                opsymQuellenText(quellText, sizeof(quellText));
                opsymFehler(z->srcLine, "Operationscode %s ist unbekannt (geladene Namensdateien: %s).", z->sp2, quellText);
                continue;
            }
            STRKOPIE(z->opname, z->sp2);
            snprintf(z->sp2, sizeof(z->sp2), "%03o", (unsigned)e->code);
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Anzeigename fuer Listing, .dmp und .test: der Name wird nur gezeigt, wenn er zur Zeile passt (der Code in sp2 ist der
// Code des Namens). Schuetzt gegen Reste in wiederverwendeten oder nicht initialisierten Zeilenfeldern.
const char *opsymAnzeigeName(const lineElements *z) {
    if (z->opname[0] != '.' || memchr(z->opname, '\0', sizeof(z->opname)) == NULL) return NULL;
    char name[OPSYM_NAME_MAX + 2];
    if (!opsymNameGueltig(z->opname + 1)) return NULL;
    opsymGross(name, sizeof(name), z->opname + 1);
    const OpsymEintrag *e = opsymSuche(name);
    if (e == NULL) return NULL;
    char code[8];
    snprintfGekuerzt(code, sizeof(code), "%03o", (unsigned)e->code);
    return strcmp(code, z->sp2) == 0 ? z->opname : NULL;
}

// ---------------------------------------------------------------------------------------------------------------
// Option --opsyms: Standardtabelle auf STDOUT (O-30). Rueckgabe: RC_OK oder RC_FEHLER.
int opsymAusgabe(void) {
    char pfad[1100];
    FILE *f = opsymOeffneStandard(pfad, sizeof(pfad));
    if (f == NULL) {
        PRINT_FEHLER("Die Standardtabelle %s konnte weder im aktuellen Verzeichnis noch unter Sourcecode/ noch neben dem Programm geöffnet werden.", OPSYM_STANDARD);
        return RC_FEHLER;
    }
    int q = opsymQuelleNeu(pfad);
    opsymLiesDatei(f, q, 0);
    fclose(f);
    if (is_error0 != 0) return RC_FEHLER;

    printf("Namen für Operationscodes (Standardtabelle %s); im Quelltext mit vorangestelltem Punkt schreiben, z. B. .LD\n", pfad);
    printf("%-8s %-4s %-6s %-5s %s\n", "Name", "Code", "B·A·Z", "Nr.", "Bedeutung");
    for (int i = 0; i < tabN; i++) {
        const OpsymEintrag *e = &tab[i];
        char nr[16] = "-";
        const char *text = e->kommentar;
        if (strncmp(text, "Nr.", 3) == 0) {
            const char *p = text + 3;
            while (*p == ' ') p++;
            int l = 0;
            while (isdigit((unsigned char)p[l]) && l < 10) { nr[l] = p[l]; l++; }
            if (l > 0) { nr[l] = '\0'; text = p + l; while (*text == ' ') text++; }
        }
        printf("%-8s %03o  %d·%d·%d  %-5s %s\n", e->name, (unsigned)e->code,
               (e->code >> 6) & 7, (e->code >> 3) & 7, e->code & 7, nr, text);
    }
    return RC_OK;
}
