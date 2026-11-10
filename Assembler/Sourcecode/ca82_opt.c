// ca82_opt.c - Optimierer des Assemblers (Dokumentation Abschnitt 5)
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
//
// Ablauf: Pass 2 laeuft einmal (Probelauf) und liefert zu jeder Zeile den Befehlszaehler vor und nach der
// Zeile. Daraus bestimmt der Optimierer belegte und freie Zellen. Nur die vom Assembler erzeugten Literale werden
// als Textzeilen vor die equ10/equ40/equ100/spa-Zeile gesetzt, deren Sprungbereich die freie Zelle enthaelt.
// Zeilen des Programmierers (auch dw, auch in begin/bend) bleiben an ihrer Adresse (Doku 5.2, 5.4). Vorher
// verschiebt blockVerschieben die Bloecke mit begin RELOC-EQU und RELOC-ALL (Doku 5.4, ab 1.01-030, RELOC-ALL ab 1.03-011); bei FILL setzt der
// Optimierer Literale auch in die Luecke eines solchen Blocks. Danach laeuft Pass 2 noch
// einmal. Stimmen die Adressen aller unveraenderten Zeilen nicht mit dem Probelauf ueberein, verwirft der
// Optimierer sein Ergebnis und es gilt der Quelltext ohne Optimierung.
#include "ca82_intern.h"
#include <sys/stat.h>
#include <unistd.h>

int optAktiv = 1;                       // 0 = Aufruf mit --no-opt
int optLiteralsymbolImQuelltext = 0;    // 1 = der Quelltext benutzt selbst ein Literalsymbol (l0001 ...)
int pass2Wiederholung = 0;              // 1 = zweiter Pass-2-Lauf: keine Meldung, keine Warnung doppelt
unsigned int *optAdrVor = NULL;         // Befehlszaehler vor der Zeile (von Pass 2 gefuellt)
unsigned int *optAdrNach = NULL;        // Befehlszaehler nach der Zeile

#define OPT_ZELLEN 020000

// Ist tok an Stelle p ein eigenstaendiger Bezeichner l<4 Ziffern>?
int optHatLiteralsymbol(const char *s) {
    for (const char *p = s; *p; p++) {
        if (*p == ';') break;
        if (*p == 'l' && isdigit((unsigned char)p[1]) && isdigit((unsigned char)p[2]) && isdigit((unsigned char)p[3]) && isdigit((unsigned char)p[4])
            && !isalnum((unsigned char)p[5]) && p[5] != '_' && (p == s || (!isalnum((unsigned char)p[-1]) && p[-1] != '_'))) {
            return 1;
        }
    }
    return 0;
}

static int istSprungOp(const char *op, const char *operand) {
    if (strcmp(op, "spa") == 0) return 1;
    return (strcmp(op, "equ10") == 0 || strcmp(op, "equ40") == 0 || strcmp(op, "equ100") == 0) && operand[0] == '*';
}

static int istKommentarZeile(const lineElements *e) {
    if (e->sp1[0] == ';' || e->sp1[0] == '#' || e->sp1[0] == '$' || e->sp1[0] == '&' || strstr(e->sp1, "***") != NULL) return 1;
    return e->sp1[0] == '\0' && e->sp2[0] == '\0' && e->sp3[0] == '\0' && e->sp4[0] == '\0';
}

// Zeile ohne Zellenbelegung (Zaehlersprung, Steuerzeile)
static int belegtKeineZelle(const char *op) {
    static const char *keine[] = { "", "equ", "equ10", "equ40", "equ100", "spa", "start", "abs", "end", "begin", "bend", NULL };
    for (int k = 0; keine[k]; k++) if (strcmp(op, keine[k]) == 0) return 1;
    return 0;
}

// ---- begin RELOC-EQU [FILL]: Schluesselwoerter und Blockverschiebung (Doku 5.4, ab c82ass 1.01-030) ----

// Wertet den Operanden von begin aus (Woerter durch Leerraum getrennt, ohne Gross-/Kleinunterscheidung; der Bindestrich in
// RELOC-EQU und RELOC-ALL ist kein Minus). Erlaubt: RELOC-EQU oder RELOC-ALL (nur eines von beiden), FILL, jedes hoechstens einmal,
// RELOC-EQU bzw. RELOC-ALL vor FILL. *reloc: 0 = keines, 1 = RELOC-EQU, 2 = RELOC-ALL (ab 1.03-011: auch Bloecke ohne equ100/equ40 werden verschoben).
// Rueckgabe 0 = in Ordnung (*reloc, *fill gesetzt), 1 = Fehler mit Text in meldung.
int beginSchluesselwoerter(const char *operand, int *reloc, int *fill, char *meldung, size_t groesse) {
    *reloc = 0; *fill = 0;
    const char *p = (operand != NULL) ? operand : "";
    while (*p) {
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0' || *p == ';') break;
        char wort[64]; size_t k = 0;
        while (*p && *p != ' ' && *p != '\t' && *p != ';') { if (k < sizeof(wort) - 1) wort[k++] = *p; p++; }
        wort[k] = '\0';
        int istEqu = gleichOhneGrossKlein(wort, "RELOC-EQU"), istAll = gleichOhneGrossKlein(wort, "RELOC-ALL");
        if (istEqu || istAll) {
            const char *name = istEqu ? "RELOC-EQU" : "RELOC-ALL";
            if (*reloc == (istEqu ? 1 : 2)) { snprintf(meldung, groesse, "begin: Schlüsselwort %s steht doppelt.", name); return 1; }
            if (*reloc) { snprintf(meldung, groesse, "begin: RELOC-EQU und RELOC-ALL schließen einander aus; es darf nur eines von beiden stehen."); return 1; }
            if (*fill)  { snprintf(meldung, groesse, "begin: %s muss vor FILL stehen.", name); return 1; }
            *reloc = istEqu ? 1 : 2;
        } else if (gleichOhneGrossKlein(wort, "FILL")) {
            if (*fill)  { snprintf(meldung, groesse, "begin: Schlüsselwort FILL steht doppelt."); return 1; }
            *fill = 1;
        } else {
            snprintf(meldung, groesse, "begin: unbekanntes Schlüsselwort \"%s\" (erlaubt sind RELOC-EQU, RELOC-ALL und FILL).", wort);
            return 1;
        }
    }
    return 0;
}

// Ein verschobener Block (Indizes gelten im Feld lineAsmAufgeloestTemp nach der Verschiebung)
typedef struct { int beginIdx, bendIdx; unsigned int start, n, r; int fill; } OptBlock;
static OptBlock *optBloecke = NULL;
static int optBlockAnzahl = 0;
static int optBlockAb = -1;       // Index der ersten Zeile des ersten verschobenen Blocks, -1 = nichts verschoben

typedef struct { int von, bis, eq, ab, gruppe, fill; unsigned int n, r, start; } BlockKandidat;   // gruppe 1 = equ100 *, 2 = equ40 *, 4 = RELOC-ALL ohne equ (ab 1.03-011); ab = Index vor der ersten gezaehlten Zeile

// Zellenzahl einer Textanweisung (dt, dto, dtm, kat4, kat5, kat6) mit denselben Zaehlfunktionen wie Pass 2 (Text aus \...\ oder Operand).
// *zustand ist der KB/GB-Zustand der Textzaehlung (zFlag: 0 = GB, 1 = KB) vor der Zeile; dt, dto und dtm veraendern ihn (Doku 3.3.5),
// kat4 bis kat6 nicht. Der globale Zustand zFlag bleibt unberuehrt. Rueckgabe -1, wenn op keine Textanweisung ist.
static int textZellen(const lineElements *e, const char *op, int *zustand) {
    char operand[sizeof(e->sp3)];
    char textkonst[1024] = "";
    char puffer[1024];
    snprintf(operand, sizeof(operand), "%s", e->sp3);
    extractBackslashContent(operand, textkonst);          // schneidet aus der Kopie aus, die Zeile bleibt unveraendert
    snprintf(puffer, sizeof(puffer), "%s", textkonst[0] != '\0' ? textkonst : operand);
    if (strcmp(op, "kat4") == 0) return zaehleKat4(puffer);
    if (strcmp(op, "kat5") == 0) return zaehleKat5(puffer);
    if (strcmp(op, "kat6") == 0) return zaehleKat6(puffer);
    int kbgb;
    if (strcmp(op, "dt") == 0) kbgb = 0;
    else if (strcmp(op, "dto") == 0) kbgb = 1;
    else if (strcmp(op, "dtm") == 0) kbgb = 2;
    else return -1;
    int alt = zFlag;
    zFlag = *zustand;
    int n = zaehleText(puffer, kbgb);
    *zustand = zFlag;
    zFlag = alt;
    return n;
}

// Zellenzahl der Zeilen zwischen der equ-Zeile eq und der bend-Zeile bis (Regeln von zellen(von,bis), Doku 4.23: db/dbn mit ihrer Zahl,
// Befehl und dw, dwb, dwh, dwf, dwg, da, dz je eine Zelle, Marke allein 0; ab 1.02-003 auch dt, dto, dtm, kat4, kat5, kat6 mit den
// Zaehlfunktionen von Pass 2; kat5 ist ab 1.03-001 immer eine Zelle). *zustand ist der KB/GB-Zustand vor dem Block und nach dem Block der Zustand dahinter. Rueckgabe 1 = bestimmbar,
// 0 = nicht (dann bleibt der Block, wo er ist, ohne Meldung).
static int blockZellen(const lineElements *z, int eq, int bis, unsigned int *nOut, int *zustand) {
    unsigned int n = 0;
    for (int k = eq + 1; k < bis; k++) {
        if (istKommentarZeile(&z[k])) continue;
        const char *op = z[k].sp2;
        if (op[0] == '\0') continue;
        if (strcmp(op, "db") == 0 || strcmp(op, "dbn") == 0) {
            long w = 0; char m[256];
            if (!pruefeDbOperand(op, z[k].sp3, &w, m, sizeof(m))) return 0;
            n += (unsigned int)w;
        } else if (strcmp(op, "dw") == 0 || strcmp(op, "dwb") == 0 || strcmp(op, "dwh") == 0 || strcmp(op, "dwf") == 0 || strcmp(op, "dwg") == 0 || strcmp(op, "da") == 0 || strcmp(op, "dz") == 0) {
            n++;
        } else if (strcmp(op, "dt") == 0 || strcmp(op, "dto") == 0 || strcmp(op, "dtm") == 0 || strcmp(op, "kat4") == 0 || strcmp(op, "kat5") == 0 || strcmp(op, "kat6") == 0) {
            n += (unsigned int)textZellen(&z[k], op, zustand);
        } else if (isKeywordMatch(op) == 1) {
            n++;   // Maschinenbefehl
        } else {
            return 0;
        }
    }
    *nOut = n;
    return 1;
}

// Verschiebt die Bloecke mit begin RELOC-EQU, deren erste Anweisung equ100 * (Gruppe 1) oder equ40 * (Gruppe 2) ist, dicht unter 07600
// (Doku 5.4, Anforderung F3 bis F6, F10). Laeuft nach Pass 1 und vor dem ersten Pass-2-Lauf. Bei jeder Unstimmigkeit verschiebt sie
// nichts; die Meldung kommt dann aus Pass 2 (Fehler am begin: Marke 4 in verlegt).
static void blockVerschieben(void) {
    int n = lineCountAsmAufgeloestTemp;
    lineElements *z = lineAsmAufgeloestTemp;
    optBlockAnzahl = 0; optBlockAb = -1;
    BlockKandidat *b = malloc(sizeof(BlockKandidat) * (size_t)(n / 2 + 1));
    if (!b) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    int nb = 0;
    for (int i = 0; i < n; i++) {
        if (istKommentarZeile(&z[i]) || strcmp(z[i].sp2, "begin") != 0) continue;
        int reloc = 0, fill = 0; char m[256];
        if (beginSchluesselwoerter(z[i].sp3, &reloc, &fill, m, sizeof(m)) != 0 || !reloc) continue;
        // Ende des Blocks suchen; ein begin davor oder kein bend: kein Kandidat
        int bis = -1, eq = -1, markeVorEqu = 0;
        for (int j = i + 1; j < n; j++) {
            if (istKommentarZeile(&z[j])) continue;
            if (strcmp(z[j].sp2, "begin") == 0) break;
            if (strcmp(z[j].sp2, "bend") == 0) { bis = j; break; }
            if (z[j].sp2[0] == '\0') { if (eq < 0 && isValidLabel(z[j].sp1)) markeVorEqu = 1; continue; }
            if (eq < 0) eq = j;
        }
        if (bis < 0) continue;
        int i0 = i;
        i = bis;   // hinter dem Block weitersuchen
        if (eq < 0) continue;
        int gruppe = 0;
        if (strcmp(z[eq].sp2, "equ100") == 0 && z[eq].sp3[0] == '*') gruppe = 1;
        else if (strcmp(z[eq].sp2, "equ40") == 0 && z[eq].sp3[0] == '*') gruppe = 2;
        if (gruppe != 0) {
            if (markeVorEqu || isValidLabel(z[i0].sp1)) continue;   // Marke auf begin oder vor der equ-Zeile: Fehler aus Pass 2, kein Verschieben
        } else if (reloc == 2) {
            gruppe = 4;   // RELOC-ALL: Block ohne equ100/equ40 wird ohne Ausrichtung verschoben (Marken auf begin und vor der ersten Anweisung bleiben richtig, weil das equ vor dem begin steht)
        } else {
            continue;     // RELOC-EQU ohne equ100/equ40 als erste Anweisung: bleibt, wo er ist (A5)
        }
        unsigned int zellen = 0;
        int probe = 0;   // nur zur Pruefung, ob der Block bestimmbar und nicht leer ist; die wahre Zahl (vom KB/GB-Zustand abhaengig) folgt unten
        int ab = (gruppe == 4) ? eq - 1 : eq;   // Gruppe 4: die erste Anweisung zaehlt mit; eq - 1 >= i0 (das begin steht davor)
        if (!blockZellen(z, ab, bis, &zellen, &probe) || zellen == 0) continue;
        unsigned int raster = (gruppe == 1) ? 0100u : (gruppe == 2) ? 040u : 1u;
        b[nb].von = i0; b[nb].bis = bis; b[nb].eq = (gruppe == 4) ? -1 : eq; b[nb].ab = ab; b[nb].gruppe = gruppe; b[nb].fill = fill;
        b[nb].n = zellen; b[nb].r = (zellen + raster - 1) / raster * raster; b[nb].start = 0;
        nb++;
    }
    if (nb <= 0) { free(b); return; }

    // Wahre Zellenzahl der Bloecke: dt, dto und dtm zaehlen je nach KB/GB-Zustand (zFlag). Pass 2 laeuft in der neuen Reihenfolge ab (zuerst alle
    // uebrigen Zeilen in Quelltextreihenfolge, dann Gruppe 1, dann Gruppe 2) und beginnt bei GB; derselbe Zustandsfluss gilt hier (Doku 5.4).
    {
        unsigned char *inBl = calloc((size_t)n + 1, 1);
        if (!inBl) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
        for (int k = 0; k < nb; k++) for (int j = b[k].von; j <= b[k].bis; j++) inBl[j] = 1;
        int zustand = 0;
        for (int i = 0; i < n; i++) {
            if (inBl[i] || istKommentarZeile(&z[i])) continue;
            (void)textZellen(&z[i], z[i].sp2, &zustand);   // fuehrt den Zustand nach; Rueckgabe hier ohne Belang
        }
        free(inBl);
        for (int g = 1; g <= 4; g += (g == 2) ? 2 : 1) {   // Reihenfolge der Gruppen: 1, 2, 4
            for (int k = 0; k < nb; k++) {
                if (b[k].gruppe != g) continue;
                unsigned int zellen = 0;
                if (!blockZellen(z, b[k].ab, b[k].bis, &zellen, &zustand)) zellen = b[k].n;   // kann nicht eintreten: schon bestimmbar
                unsigned int raster = (g == 1) ? 0100u : (g == 2) ? 040u : 1u;
                b[k].n = zellen; b[k].r = (zellen + raster - 1) / raster * raster;
            }
        }
    }

    // Anfaenge: Gruppe 1 in Quelltextreihenfolge nach unten ab 07600, danach Gruppe 2 darunter (F10)
    unsigned int oben = 07600;
    for (int g = 1; g <= 2; g++) {
        for (int k = 0; k < nb; k++) {
            if (b[k].gruppe != g) continue;
            if (b[k].r > oben) { z[b[k].von].verlegt = 4; free(b); return; }   // Anfang kleiner als 0: nichts verschieben, Pass 2 meldet es
            oben -= b[k].r;
            b[k].start = oben;
        }
    }
    // Gruppe 4 (RELOC-ALL ohne equ, ab 1.03-011): ohne Ausrichtung, groesster Block zuerst (bei Gleichstand der erste im Quelltext).
    // Jeder Block kommt in die erste Luecke hinter einem ausgerichteten Block ohne FILL (Zellen n bis r), in die er passt; sonst dicht
    // unter die bisherigen Bloecke. Die Zeilenfolge bleibt die Quelltextreihenfolge, die Adresse legt das vorgesetzte equ fest.
    {
        unsigned int *lueckeNext = calloc((size_t)nb + 1, sizeof(unsigned int)), *lueckeEnde = calloc((size_t)nb + 1, sizeof(unsigned int));
        char *gesetzt = calloc((size_t)nb + 1, 1);
        if (!lueckeNext || !lueckeEnde || !gesetzt) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
        for (int k = 0; k < nb; k++) {
            if (b[k].gruppe == 4 || b[k].fill || b[k].r <= b[k].n) continue;
            lueckeNext[k] = b[k].start + b[k].n; lueckeEnde[k] = b[k].start + b[k].r;
        }
        for (;;) {
            int x = -1;
            for (int k = 0; k < nb; k++) if (b[k].gruppe == 4 && !gesetzt[k] && (x < 0 || b[k].n > b[x].n)) x = k;
            if (x < 0) break;
            int platz = 0;
            for (int k = 0; k < nb && !platz; k++) {
                if (lueckeEnde[k] > lueckeNext[k] && lueckeEnde[k] - lueckeNext[k] >= b[x].n) {
                    b[x].start = lueckeNext[k]; lueckeNext[k] += b[x].n; platz = 1;
                }
            }
            if (!platz) {
                if (b[x].n > oben) { z[b[x].von].verlegt = 4; free(b); free(lueckeNext); free(lueckeEnde); free(gesetzt); return; }
                oben -= b[x].n;
                b[x].start = oben;
            }
            gesetzt[x] = 1;
        }
        free(lueckeNext); free(lueckeEnde); free(gesetzt);
    }

    // Zeilen umordnen: alle uebrigen Zeilen, dahinter die Bloecke (Gruppe 1, dann Gruppe 2, je in Quelltextreihenfolge) (A3)
    pruefeZeilenfeld(n + nb);   // Gruppe 4 setzt vor jedes begin ein equ
    lineElements *neu = malloc(sizeof(lineElements) * (size_t)(n + nb + 1));
    unsigned char *imBlock = calloc((size_t)n + 1, 1);
    optBloecke = malloc(sizeof(OptBlock) * (size_t)nb);
    if (!neu || !imBlock || !optBloecke) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    for (int k = 0; k < nb; k++) for (int j = b[k].von; j <= b[k].bis; j++) imBlock[j] = 1;
    int m = 0;
    for (int i = 0; i < n; i++) if (!imBlock[i]) neu[m++] = z[i];
    optBlockAb = m;
    for (int g = 1; g <= 4; g += (g == 2) ? 2 : 1) {   // Reihenfolge der Gruppen: 1, 2, 4
        for (int k = 0; k < nb; k++) {
            if (b[k].gruppe != g) continue;
            if (g == 4) {   // equ <Adresse> vor dem begin: die Marken auf begin und vor der ersten Anweisung behalten so die Blockadresse
                memset(&neu[m], 0, sizeof(lineElements));
                strcpy(neu[m].sp2, "equ");
                snprintf(neu[m].sp3, sizeof(neu[m].sp3), "0%o", b[k].start);
                strcpy(neu[m].sp4, "; RELOC-ALL: Block verschoben");
                neu[m].srcLine = z[b[k].von].srcLine;
                m++;
            }
            int anfang = m;
            for (int j = b[k].von; j <= b[k].bis; j++) {
                neu[m] = z[j];
                if (j == b[k].eq) {
                    char alt[16], altKomm[160];
                    snprintfGekuerzt(alt, sizeof(alt), "%s", z[j].sp2);
                    snprintfGekuerzt(altKomm, sizeof(altKomm), "%s", z[j].sp4);
                    strcpy(neu[m].sp2, "equ");
                    snprintf(neu[m].sp3, sizeof(neu[m].sp3), "0%o", b[k].start);
                    if (altKomm[0] == ';') snprintf(neu[m].sp4, sizeof(neu[m].sp4), "; vorher %s *   %s", alt, altKomm + 1);
                    else snprintf(neu[m].sp4, sizeof(neu[m].sp4), "; vorher %s *", alt);
                    neu[m].verlegt = g;
                }
                m++;
            }
            optBloecke[optBlockAnzahl].beginIdx = anfang;
            optBloecke[optBlockAnzahl].bendIdx = m - 1;
            optBloecke[optBlockAnzahl].start = b[k].start;
            optBloecke[optBlockAnzahl].n = b[k].n;
            optBloecke[optBlockAnzahl].r = b[k].r;
            optBloecke[optBlockAnzahl].fill = b[k].fill;
            optBlockAnzahl++;
        }
    }
    memcpy(lineAsmAufgeloestTemp, neu, sizeof(lineElements) * (size_t)m);
    lineCountAsmAufgeloestTemp = m;
    free(neu); free(imBlock); free(b);
}

// ---- Makro-Umordnung: Rumpfbloecke von TYP=M-Makros hinter end verlegen (Doku 5.6, ab c82ass 1.03-007) ----

int optMakroUmordnen = MAKRO_UMORDNEN_VORGABE;   // ;#MAKROUMORDNEN=YES/NO im Quelltext setzt den Wert (ladeMakroUmordnenSchalter, Doku 5.6)

// Ein Rumpfblock: zusammenhaengender Lauf von Zeilen mit gleichem makroInst ungleich 0 (aeusserster TYP=M-Aufruf, ca82_typen.h)
typedef struct {
    int inst;                  // Aufrufnummer (makroInst)
    int von, bis;              // Zeilenindex im Feld lineAsmAufgeloestTemp, einschliesslich
    int gruppe;                // 1 = erste Anweisung equ100 *, 2 = equ40 *, 4 = keines von beiden (Gruppe 3 = bleibt, kommt hier nicht vor)
    unsigned int n;            // Zellen vom Anfang bis zur letzten belegenden Zeile (Gruppe 1, 2: ab dem aufgerundeten Anfang)
    unsigned int r;            // n aufgerundet auf 0100 (Gruppe 1) bzw. 040 (Gruppe 2), sonst n
} MakroBlock;

// Zeile, die als "erste Anweisung" nicht zaehlt und den Befehlszaehler nicht beruehrt: Kommentar, Marke allein, abs und das vom
// Makroaufruf erzeugte "<Marke> equ *" (ca82_makros.c, Label des Makroaufrufs)
static int istDurchsichtig(const lineElements *e) {
    if (istKommentarZeile(e)) return 1;
    const char *op = e->sp2;
    if (op[0] == '\0' || strcmp(op, "abs") == 0) return 1;
    if (strcmp(op, "equ") == 0 && e->sp3[0] == '*' && (e->sp3[1] == '\0' || e->sp3[1] == ' ' || e->sp3[1] == ';')) return 1;
    return 0;
}

// Gruppe eines Blocks nach Doku 5.6. Rueckgabe 1 oder 2 (*eq = Index der equ-Zeile), 4 oder 0 = der Block bleibt, wo er ist.
// Hindernisse: begin, bend, start, end (Doku 5.4, Annahme 95), spa, equ mit absolutem Operanden (der Zaehler waere absolut gesetzt),
// equ100 * oder equ40 * hinter der ersten Anweisung (Gruppe 3), dt, dto, dtm (sie fuehren den KB/GB-Zustand der Textzaehlung; eine
// Umordnung wuerde ihn fuer die uebrigen Zeilen aendern).
static int makroBlockGruppe(const lineElements *z, int von, int bis, int *eq) {
    int erste = 1, gruppe = 4;
    *eq = -1;
    for (int k = von; k <= bis; k++) {
        if (istDurchsichtig(&z[k])) continue;
        const char *op = z[k].sp2;
        if (strcmp(op, "begin") == 0 || strcmp(op, "bend") == 0 || strcmp(op, "start") == 0 || strcmp(op, "end") == 0 || strcmp(op, "spa") == 0) return 0;
        if (strcmp(op, "dt") == 0 || strcmp(op, "dto") == 0 || strcmp(op, "dtm") == 0) return 0;
        if (strcmp(op, "equ") == 0 && z[k].sp3[0] != '*') return 0;
        if (strcmp(op, "equ100") == 0 || strcmp(op, "equ40") == 0) {
            if (!erste) return 0;
            gruppe = (strcmp(op, "equ100") == 0) ? 1 : 2;
            *eq = k;
        }
        erste = 0;
    }
    return gruppe;
}

// Ist e die von Pass 1 angehaengte Zeile zum Eintrag k der Literaltabelle? (Marke = Literalname; dw, da, bei einem !-Literal auch dbn.)
// Dieselbe Bedingung gilt in optimiereZeilen und in makroEinfuegeStelle.
static int istLiteralZeile(const lineElements *e, int k) {
    if (strcmp(e->sp1, literalTable[k].literalName) != 0) return 0;
    return strcmp(e->sp2, "dw") == 0 || strcmp(e->sp2, "da") == 0 || (literalTable[k].literalValue[0] == '!' && strcmp(e->sp2, "dbn") == 0);
}

// Einfuegestelle der verlegten Rumpfbloecke (Doku 5.6): Index der ersten von Pass 1 angehaengten Literalzeile. Bei endIdx >= 0 (Index des
// ersten end) beginnt die Suche hinter dem end, sonst bei Zeile 0 (ohne end ist das Programm alles vor den Literalzeilen). Gibt es keine
// Literalzeile, ist es der Index der ersten Zeile der verschobenen RELOC-Bloecke (optBlockAb), sonst die Zeilenzahl. Die Literalzeilen
// stehen immer vor den RELOC-Bloecken (blockVerschieben). Einfuegen vor dem Rueckgabewert = hinter end/Quelltextende, vor den Literalen.
static int makroEinfuegeStelle(int endIdx) {
    lineElements *z = lineAsmAufgeloestTemp;
    int erste = (optBlockAb >= 0) ? optBlockAb : lineCountAsmAufgeloestTemp;
    int ab = (endIdx >= 0) ? endIdx + 1 : 0;
    for (int k = 0; k < literalCount; k++) {
        for (int i = ab; i < erste; i++) {
            if (istLiteralZeile(&z[i], k)) { erste = i; break; }
        }
    }
    return erste;
}

// Teilt die Rumpfbloecke der TYP=M-Makros ein. Voraussetzung: Probelauf 1 ist gelaufen (optAdrVor/optAdrNach gueltig), blockVerschieben ist
// gelaufen. Nur Bloecke vor dem ersten end (ohne end: vor den Literalzeilen), ausserhalb von begin/bend und ausserhalb der verschobenen
// RELOC-Bloecke. Die Groesse kommt aus dem Probelauf. Rueckgabe: Anzahl der verlegbaren Bloecke, *out (mit free freizugeben) in
// Quelltextreihenfolge; *einfuegeOut = Einfuegestelle (Zeilenindex, vor dem die Bloecke wieder eingesetzt werden, makroEinfuegeStelle).
static int makroBloeckeEinteilen(MakroBlock **out, int *einfuegeOut) {
    int n = lineCountAsmAufgeloestTemp;
    lineElements *z = lineAsmAufgeloestTemp;
    int schranke = (optBlockAb >= 0) ? optBlockAb : n;     // ab hier: verschobene RELOC-Bloecke
    int endIdx = -1;
    for (int i = 0; i < schranke; i++) if (!istKommentarZeile(&z[i]) && strcmp(z[i].sp2, "end") == 0) { endIdx = i; break; }
    int ins = makroEinfuegeStelle(endIdx);
    int grenze = (endIdx >= 0) ? endIdx : ins;   // Zeilen davor sind das Programm
    *out = NULL;
    *einfuegeOut = ins;
    MakroBlock *b = malloc(sizeof(MakroBlock) * (size_t)(grenze / 2 + 2));
    if (!b) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    int nb = 0, imBegin = 0;
    for (int i = 0; i < grenze; i++) {
        if (!istKommentarZeile(&z[i])) {
            if (strcmp(z[i].sp2, "begin") == 0) imBegin = 1;
            else if (strcmp(z[i].sp2, "bend") == 0) imBegin = 0;
        }
        if (z[i].makroInst == 0) continue;
        int j = i;
        while (j + 1 < grenze && z[j + 1].makroInst == z[i].makroInst) j++;
        int von = i, bis = j, vorBegin = imBegin;
        // begin/bend innerhalb des Laufs nachfuehren, damit imBegin hinter dem Block stimmt (der Block selbst bleibt dann ohnehin)
        for (int k = von; k <= bis; k++) {
            if (istKommentarZeile(&z[k])) continue;
            if (strcmp(z[k].sp2, "begin") == 0) imBegin = 1;
            else if (strcmp(z[k].sp2, "bend") == 0) imBegin = 0;
        }
        i = bis;
        if (vorBegin) continue;
        int eq = -1;
        int gruppe = makroBlockGruppe(z, von, bis, &eq);
        if (gruppe == 0) continue;
        int a = -1, e = -1, erstReal = -1;       // erste und letzte belegende Zeile, erste nicht durchsichtige Zeile
        for (int k = von; k <= bis; k++) {
            if (istKommentarZeile(&z[k])) continue;
            if (erstReal < 0 && !istDurchsichtig(&z[k])) erstReal = k;
            if (belegtKeineZelle(z[k].sp2)) continue;
            if (a < 0) a = k;
            e = k;
        }
        if (a < 0) continue;                      // keine belegende Zeile (zweiter Aufruf mit $GLOBAL): nichts zu verlegen
        unsigned int anfang = (gruppe == 4) ? optAdrVor[erstReal] : optAdrNach[eq];
        if (optAdrNach[e] <= anfang) continue;
        b[nb].inst = z[von].makroInst; b[nb].von = von; b[nb].bis = bis; b[nb].gruppe = gruppe;
        b[nb].n = optAdrNach[e] - anfang;
        b[nb].r = (gruppe == 1) ? (b[nb].n + 0100u - 1) / 0100u * 0100u : (gruppe == 2) ? (b[nb].n + 040u - 1) / 040u * 040u : b[nb].n;
        nb++;
    }
    // dieselbe Nummer in zwei getrennten Laeufen: unbekannte Lage der Zeilen, beide bleiben
    for (int x = 0; x < nb; x++) {
        int doppelt = 0;
        for (int y = 0; y < nb; y++) if (y != x && b[y].inst == b[x].inst) doppelt = 1;
        if (doppelt) b[x].gruppe = 0;
    }
    int m = 0;
    for (int x = 0; x < nb; x++) if (b[x].gruppe != 0) b[m++] = b[x];
    if (m == 0) { free(b); return 0; }
    *out = b;
    return m;
}

// Endadresse eines Probelaufs: hoechste belegte Zelle + 1 ausserhalb der verschobenen RELOC-Bloecke (Doku 5.6). Die Literalzeilen hinter
// end zaehlen mit (ohne die spaetere Literalumordnung).
static unsigned int makroEndAdresse(void) {
    int n = lineCountAsmAufgeloestTemp;
    int schranke = (optBlockAb >= 0) ? optBlockAb : n;
    unsigned int e = 0;
    for (int i = 0; i < schranke; i++) {
        if (istKommentarZeile(&lineAsmAufgeloestTemp[i]) || belegtKeineZelle(lineAsmAufgeloestTemp[i].sp2)) continue;
        if (optAdrNach[i] > e) e = optAdrNach[i];
    }
    return e;
}

static unsigned int aufrunden(unsigned int x, unsigned int g) {
    return (x + g - 1) / g * g;
}

// Zellen, die ein Block ab Zaehler cur belegt, einschliesslich der Ausrichtungsluecke vor ihm (Gruppe 1: bis zur 0100-Grenze, Gruppe 2: bis 040)
static unsigned int makroVerbrauch(const MakroBlock *b, unsigned int cur) {
    if (b->gruppe == 1) return aufrunden(cur, 0100) - cur + b->n;
    if (b->gruppe == 2) return aufrunden(cur, 040) - cur + b->n;
    return b->n;
}

// Der groesste noch nicht gesetzte Block der Gruppe 4 (und bei mitGruppe2 auch der Gruppe 2), dessen Verbrauch ab cur hoechstens luecke ist;
// bei Gleichstand der erste in Quelltextreihenfolge. -1 = keiner.
static int makroPasst(const MakroBlock *mb, int m, const char *gesetzt, unsigned int cur, unsigned int luecke, int mitGruppe2) {
    int best = -1;
    unsigned int bestV = 0;
    for (int x = 0; x < m; x++) {
        if (gesetzt[x] || !(mb[x].gruppe == 4 || (mitGruppe2 && mb[x].gruppe == 2))) continue;
        unsigned int v = makroVerbrauch(&mb[x], cur);
        if (v <= luecke && v > bestV) { best = x; bestV = v; }
    }
    return best;
}

// Der noch nicht gesetzte Block der Gruppe g mit dem groessten r (Gruppe 4: n); bei Gleichstand der erste. -1 = keiner.
static int makroGroesster(const MakroBlock *mb, int m, const char *gesetzt, int g) {
    int best = -1;
    for (int x = 0; x < m; x++) {
        if (gesetzt[x] || mb[x].gruppe != g) continue;
        if (best < 0 || mb[x].r > mb[best].r) best = x;
    }
    return best;
}

// Packen (Doku 5.6): bestimmt die Reihenfolge der Bloecke ab dem geschaetzten Zaehler cur. Nur die Reihenfolge, es entsteht kein equ.
// Phase A: Gruppe-1-Bloecke nach r absteigend; vor jedem die Luecke bis zur 0100-Grenze mit dem groessten passenden Block der Gruppe 2
// oder 4 fuellen. Phase B: restliche Gruppe-2-Bloecke nach r absteigend, die Luecke bis 040 mit Gruppe 4 fuellen. Phase C: Rest Gruppe 4.
// ordnung[0..m-1] = Blockindizes in der neuen Reihenfolge.
static void makroPacken(const MakroBlock *mb, int m, unsigned int cur, int *ordnung) {
    char *gesetzt = calloc((size_t)m + 1, 1);
    if (!gesetzt) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    int k = 0, x;
    while ((x = makroGroesster(mb, m, gesetzt, 1)) >= 0) {
        int f;
        while ((f = makroPasst(mb, m, gesetzt, cur, aufrunden(cur, 0100) - cur, 1)) >= 0) {
            gesetzt[f] = 1; ordnung[k++] = f; cur += makroVerbrauch(&mb[f], cur);
        }
        gesetzt[x] = 1; ordnung[k++] = x; cur += makroVerbrauch(&mb[x], cur);
    }
    while ((x = makroGroesster(mb, m, gesetzt, 2)) >= 0) {
        int f;
        while ((f = makroPasst(mb, m, gesetzt, cur, aufrunden(cur, 040) - cur, 0)) >= 0) {
            gesetzt[f] = 1; ordnung[k++] = f; cur += makroVerbrauch(&mb[f], cur);
        }
        gesetzt[x] = 1; ordnung[k++] = x; cur += makroVerbrauch(&mb[x], cur);
    }
    while ((x = makroGroesster(mb, m, gesetzt, 4)) >= 0) {
        gesetzt[x] = 1; ordnung[k++] = x; cur += makroVerbrauch(&mb[x], cur);
    }
    free(gesetzt);
}

// Setzt die Zeilen um: erst die Zeilen vor der Einfuegestelle ohne die Bloecke, dann die Bloecke in der Reihenfolge ordnung, dann der Rest.
// orig ist die Zeilenfolge vor jeder Umordnung (n Zeilen); das Ergebnis steht in lineAsmAufgeloestTemp. Die Zeilenzahl aendert sich nicht.
static void makroZeilenUmordnen(const lineElements *orig, int n, const MakroBlock *mb, int m, const int *ordnung, int ins) {
    lineElements *neu = malloc(sizeof(lineElements) * (size_t)(n + 1));
    char *imBlock = calloc((size_t)n + 1, 1);
    if (!neu || !imBlock) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    for (int x = 0; x < m; x++) for (int k = mb[x].von; k <= mb[x].bis; k++) imBlock[k] = 1;
    int j = 0;
    for (int i = 0; i < ins; i++) if (!imBlock[i]) neu[j++] = orig[i];
    for (int q = 0; q < m; q++) for (int k = mb[ordnung[q]].von; k <= mb[ordnung[q]].bis; k++) neu[j++] = orig[k];
    for (int i = ins; i < n; i++) neu[j++] = orig[i];
    memcpy(lineAsmAufgeloestTemp, neu, sizeof(lineElements) * (size_t)j);
    free(neu); free(imBlock);
}

static long dateiGroesse(const char *name);
static void pass2Zuruecksetzen(void);

// Makro-Umordnung (Doku 5.6) auf Grundlage von Probelauf 1 (optAdrVor/optAdrNach, Zeilenfeld). Die Bloecke wandern hinter end (vor die
// Literale), gepackt nach makroPacken. Probelauf 2 (stumm) misst das Ergebnis; die Umordnung gilt nur, wenn er fehlerfrei ist und die
// Endadresse kleiner wird als im Original. Sonst kommt das Original zurueck und pass2 laeuft darauf erneut. Das Original ist der Text
// vor Probelauf 1 (vorLauf1): so ist nach dem Verwerfen alles wie nach einem ersten Lauf ohne Umordnung (auch die Marken mit Doppelpunkt). Danach gehoeren Zeilenfeld,
// optAdrVor/optAdrNach und alle Pass-2-Ergebnisse zum zuletzt gelaufenen pass2 (wie nach dem Probelauf 1).
// Der Zaehler an der Einfuegestelle haengt nur vom Text davor ab. Probelauf 2 zeigt ihn genau; weicht er von der Schaetzung ab, wird
// einmal mit dem genauen Wert neu gepackt (dritter Lauf).
static void makroUmordnen(char *logName, char *symName, long logGroesse, const lineElements *vorLauf1, int vorAnzahl) {
    MakroBlock *mb = NULL;
    int ins = 0;
    int m = makroBloeckeEinteilen(&mb, &ins);
    if (m == 0) return;
    int n = lineCountAsmAufgeloestTemp;
    if (n != vorAnzahl) { free(mb); return; }   // Zeilenzahl nach Probelauf 1 unerwartet geaendert: nicht umordnen
    lineElements *orig = malloc(sizeof(lineElements) * (size_t)(n + 1));
    int *ordnung = malloc(sizeof(int) * (size_t)m);
    if (!orig || !ordnung) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    memcpy(orig, vorLauf1, sizeof(lineElements) * (size_t)n);   // Text VOR Probelauf 1: pass2 kuerzt in addSymbol den Doppelpunkt der Marke in der Zeile selbst
    unsigned int e0 = makroEndAdresse();
    unsigned int pcIns = (ins < n) ? optAdrVor[ins] : optAdrNach[n - 1];
    unsigned int entfernt = 0;
    int zeilen = 0;
    for (int x = 0; x < m; x++) { entfernt += optAdrNach[mb[x].bis] - optAdrVor[mb[x].von]; zeilen += mb[x].bis - mb[x].von + 1; }
    unsigned int cur = (pcIns > entfernt) ? pcIns - entfernt : 0;     // Schaetzung; Probelauf 2 liefert den genauen Wert
    int insNeu = ins - zeilen;                                         // Index der ersten verlegten Zeile im neuen Text
    int fehler = 0;
    for (int versuch = 0; versuch < 2; versuch++) {
        makroPacken(mb, m, cur, ordnung);
        makroZeilenUmordnen(orig, n, mb, m, ordnung, ins);
        if (logGroesse >= 0 && truncate(logName, logGroesse) != 0) { /* Log bleibt laenger: nur Schoenheitsfehler */ }
        pass2Zuruecksetzen();
        pass2Wiederholung = 1;
        pass2Stumm = 1;
        pass2(logName, symName);
        pass2Stumm = 0;
        if (is_error2 != 0) { fehler = 1; break; }
        unsigned int echt = optAdrVor[insNeu];
        if (echt == cur) break;
        cur = echt;
    }
    int uebernehmen = !fehler && makroEndAdresse() < e0;
    if (!uebernehmen) {
        memcpy(lineAsmAufgeloestTemp, orig, sizeof(lineElements) * (size_t)n);
        if (logGroesse >= 0 && truncate(logName, logGroesse) != 0) { }
        pass2Zuruecksetzen();
        pass2Wiederholung = 1;
        pass2(logName, symName);
    }
    pass2Wiederholung = 0;
    free(orig); free(ordnung); free(mb);
}

typedef struct { int equIdx; unsigned int a, n, next; int luecke; } Sprung;

static int vergleicheSprung(const void *x, const void *y) {
    const Sprung *a = (const Sprung *)x, *b = (const Sprung *)y;
    return (a->a > b->a) - (a->a < b->a);
}

// Schiebt den Zeiger eines Sprungbereichs ueber belegte Zellen auf die naechste freie Zelle (ab 1.00-042: auch hinter belegten Zellen)
// Rueckgabe 1 = freie Zelle bei s->next, 0 = Bereich erschoepft
static int naechsteFreieZelle(Sprung *s, const unsigned char *belegt) {
    while (s->next < s->n && belegt[s->next]) s->next++;
    return s->next < s->n;
}

// Setzt die Zeilen um. Rueckgabe 1 = etwas veraendert (Erwartung in *erwartet, Herkunft in *herkunft, Laenge in *neuAnzahl)
static int optimiereZeilen(int **erwartetOut, int *neuAnzahlOut) {
    int n = lineCountAsmAufgeloestTemp;
    lineElements *z = lineAsmAufgeloestTemp;
    unsigned char *belegt = calloc(OPT_ZELLEN, 1);
    int *verlegtNach = malloc(sizeof(int) * (size_t)n);      // Sprung-Index (Zeile des equ), -1 = nicht verlegt
    unsigned int *ziel = calloc((size_t)n, sizeof(unsigned int));
    int *nachZeile = malloc(sizeof(int) * (size_t)n);
    if (!belegt || !verlegtNach || !ziel || !nachZeile) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    for (int i = 0; i < n; i++) { verlegtNach[i] = -1; nachZeile[i] = -1; }

    // erstes end bestimmen (Literalbereich beginnt danach); ohne end: hinter dem Quelltext
    int endIdx = -1;
    for (int i = 0; i < n; i++) if (strcmp(z[i].sp2, "end") == 0) { endIdx = i; break; }
    // Literalzeilen finden: Label gleich literalName der Tabelle, hinter end
    int *litZeile = malloc(sizeof(int) * (size_t)(literalCount + 1));
    for (int k = 0; k < literalCount; k++) {
        litZeile[k] = -1;
        for (int i = (endIdx >= 0 ? endIdx + 1 : 0); i < n; i++) {
            if (istLiteralZeile(&z[i], k)) { litZeile[k] = i; break; }
        }
    }
    int codeEnde = (endIdx >= 0) ? endIdx : n;     // Zeilen vor dem Literalbereich
    if (endIdx < 0) {
        int erste = n;
        for (int k = 0; k < literalCount; k++) if (litZeile[k] >= 0 && litZeile[k] < erste) erste = litZeile[k];
        codeEnde = erste;
    }

    // Belegung
    for (int i = 0; i < n; i++) {
        if (istKommentarZeile(&z[i]) || belegtKeineZelle(z[i].sp2)) continue;
        for (unsigned int c = optAdrVor[i]; c < optAdrNach[i] && c < OPT_ZELLEN; c++) belegt[c] = 1;
    }
    // Sprungbereiche vor dem Literalbereich
    Sprung *sp = calloc((size_t)n + 1 + (size_t)optBlockAnzahl, sizeof(Sprung));
    int ns = 0;
    int imBlock = 0;   // 1 innerhalb von begin/bend: dort darf der Optimierer nichts einsetzen (F1)
    for (int i = 0; i < codeEnde; i++) {
        if (istKommentarZeile(&z[i])) continue;
        if (strcmp(z[i].sp2, "begin") == 0) imBlock = 1;
        else if (strcmp(z[i].sp2, "bend") == 0) imBlock = 0;
        if (imBlock || !istSprungOp(z[i].sp2, z[i].sp3)) continue;
        if (optAdrNach[i] > optAdrVor[i] && optAdrNach[i] - optAdrVor[i] <= 077) {
            sp[ns].equIdx = i; sp[ns].a = optAdrVor[i]; sp[ns].n = optAdrNach[i]; sp[ns].next = sp[ns].a; sp[ns].luecke = 0; ns++;
        }
    }
    qsort(sp, (size_t)ns, sizeof(Sprung), vergleicheSprung);
    // Luecken verschobener Bloecke mit FILL: Zellen hinter dem Blockende bis zur Grenze, gekuerzt vor der ersten belegten Zelle (Doku 5.4).
    // Sie folgen hinter den Sprungbereichen, in aufsteigender Adresse; die Literale kommen vor die bend-Zeile des Blocks.
    int ns0 = ns;
    for (int k = 0; k < optBlockAnzahl; k++) {
        if (!optBloecke[k].fill) continue;
        unsigned int von = optBloecke[k].start + optBloecke[k].n, bis = von, grenze = optBloecke[k].start + optBloecke[k].r;
        if (grenze > OPT_ZELLEN) grenze = OPT_ZELLEN;
        while (bis < grenze && !belegt[bis]) bis++;
        if (bis <= von) continue;
        sp[ns].equIdx = optBloecke[k].bendIdx; sp[ns].a = von; sp[ns].n = bis; sp[ns].next = von; sp[ns].luecke = 1; ns++;
    }
    qsort(sp + ns0, (size_t)(ns - ns0), sizeof(Sprung), vergleicheSprung);
    // freie Zellen je Sprungbereich: der Zeiger next springt beim Verteilen ueber belegte Zellen (naechsteFreieZelle)
    int veraendert = 0;
    int *anzahlJeSprung = calloc((size_t)ns + 1, sizeof(int));

    if (ns > 0 && !optLiteralsymbolImQuelltext) {
        // 1. Literale in Tabellenreihenfolge
        for (int k = 0; k < literalCount; k++) {
            if (litZeile[k] < 0) continue;
            int g = -1;
            for (int h = 0; h < ns; h++) {
                if (naechsteFreieZelle(&sp[h], belegt)) { g = h; break; }
            }
            if (g < 0) break;
            int i = litZeile[k];
            verlegtNach[i] = g; ziel[i] = sp[g].next; belegt[sp[g].next] = 1; sp[g].next++; anzahlJeSprung[g]++;
            nachZeile[i] = k;   // Reihenfolge der Verlegung (nur fuer Sortierung innerhalb eines Sprungs)
            veraendert = 1;
        }
    }

    int rc = 0;
    if (veraendert) {
        // Neue Zeilenfolge aufbauen
        lineElements *neu = malloc(sizeof(lineElements) * (size_t)(2 * n + 16));
        int *erw = malloc(sizeof(int) * (size_t)(2 * n + 16));   // erwarteter Befehlszaehler vor der Zeile, -1 = keine Pruefung
        if (!neu || !erw) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
        int m = 0;
        for (int i = 0; i < n; i++) {
            // vor einer Sprungzeile die hierher verlegten Zeilen einsetzen (aufsteigende Zielzelle)
            for (int h = 0; h < ns; h++) {
                if (sp[h].equIdx != i || anzahlJeSprung[h] == 0) continue;
                unsigned int zaehler = sp[h].a;   // Befehlszaehler im ausgegebenen Text
                for (unsigned int c = sp[h].a; c < sp[h].next; c++) {
                    for (int q = 0; q < n; q++) {
                        if (verlegtNach[q] == h && ziel[q] == c) {
                            if (c != zaehler) {   // belegte Zellen uebersprungen: Zaehler mit equ vorsetzen
                                memset(&neu[m], 0, sizeof(lineElements));
                                strcpy(neu[m].sp2, "equ");
                                snprintf(neu[m].sp3, sizeof(neu[m].sp3), "0%o", c);
                                strcpy(neu[m].sp4, "; Optimierer: belegte Zellen uebersprungen");
                                neu[m].srcLine = z[q].srcLine;
                                erw[m] = -1; m++;
                            }
                            neu[m] = z[q]; erw[m] = (int)c;
                            if (sp[h].luecke) neu[m].verlegt = 3;   // Literal in der Luecke eines verschobenen Blocks (darf im Block stehen)
                            m++;
                            zaehler = c + 1;
                            break;
                        }
                    }
                }
            }
            if (verlegtNach[i] >= 0) {
                continue;   // Literalzeile: entfaellt am alten Platz
            }
            neu[m] = z[i];
            // geprueft werden die Zeilen vor dem Literalbereich und die Zeilen der verschobenen Bloecke (ihre Adressen sind durch equ fest);
            // der Literalbereich dazwischen wird nicht geprueft
            int pruefen = (i < codeEnde) || (optBlockAb >= 0 && i >= optBlockAb);
            erw[m] = (pruefen && !istKommentarZeile(&z[i]) && !belegtKeineZelle(z[i].sp2)) ? (int)optAdrVor[i] : -1;
            m++;
        }
        memcpy(lineAsmAufgeloestTemp, neu, sizeof(lineElements) * (size_t)m);
        lineCountAsmAufgeloestTemp = m;
        *erwartetOut = erw;
        *neuAnzahlOut = m;
        free(neu);
        rc = 1;
    }
    free(belegt); free(verlegtNach); free(ziel); free(nachZeile); free(litZeile); free(sp); free(anzahlJeSprung);
    return rc;
}

static long dateiGroesse(const char *name) {
    struct stat st;
    if (stat(name, &st) != 0) return -1;
    return (long)st.st_size;
}

static void optBloeckeFreigeben(void) {
    free(optBloecke); optBloecke = NULL; optBlockAnzahl = 0; optBlockAb = -1;
}

static void pass2Zuruecksetzen(void) {
    symbolCount = 0;
    lineCountAsmAufgeloest = 0;
    line_ausgegeben = 0;
    startAdresse = 0;
    is_error2 = 0;
}

// Pass 2 mit Optimierer. Ohne --no-opt: Probelauf, Makro-Umordnung (Doku 5.6), Umordnung der Literale, zweiter Lauf, Pruefung.
static void pass2MitOptimiererLauf(char *logName, char *symName) {
    for (int i = 0; i < lineCountAsmAufgeloestTemp; i++) lineAsmAufgeloestTemp[i].verlegt = 0;   // keine Optimierermarke (Doku 5.4)
    if (!optAktiv) { pass2(logName, symName); return; }   // --no-opt: keine Blockverschiebung (F9)

    optBlockAnzahl = 0; optBlockAb = -1;
    blockVerschieben();   // nach Pass 1, vor dem ersten Pass-2-Lauf (sonst meldete Pass 2 einen Ueberlauf im unverschobenen Layout)

    int n0 = lineCountAsmAufgeloestTemp;
    optAdrVor = calloc((size_t)(2 * n0 + 16), sizeof(unsigned int));
    optAdrNach = calloc((size_t)(2 * n0 + 16), sizeof(unsigned int));
    long logGroesse = dateiGroesse(logName);
    lineElements *vorLauf1 = NULL;   // Text vor dem ersten Lauf, nur fuer die Makro-Umordnung (pass2 veraendert Zeilen: Doppelpunkt der Marken)
    if (optMakroUmordnen) {
        vorLauf1 = malloc(sizeof(lineElements) * (size_t)(n0 + 1));
        if (!vorLauf1) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
        memcpy(vorLauf1, lineAsmAufgeloestTemp, sizeof(lineElements) * (size_t)n0);
    }
    pass2(logName, symName);
    if (is_error2 != 0 || optLiteralsymbolImQuelltext) { free(vorLauf1); free(optAdrVor); free(optAdrNach); optAdrVor = optAdrNach = NULL; optBloeckeFreigeben(); return; }

    if (optMakroUmordnen) makroUmordnen(logName, symName, logGroesse, vorLauf1, n0);   // Doku 5.6; danach gilt der zuletzt gelaufene pass2 als "erster Lauf"
    free(vorLauf1);

    lineElements *sicherung = malloc(sizeof(lineElements) * (size_t)(n0 + 1));
    if (!sicherung) { fprintf(stderr, "Speicherfehler im Optimierer!\n"); exit(RC_FEHLER); }
    memcpy(sicherung, lineAsmAufgeloestTemp, sizeof(lineElements) * (size_t)n0);

    int *erwartet = NULL, m = 0;
    if (!optimiereZeilen(&erwartet, &m)) {
        free(sicherung); free(optAdrVor); free(optAdrNach); optAdrVor = optAdrNach = NULL; optBloeckeFreigeben();
        return;   // nichts zu verlegen: Ergebnis des ersten Laufs gilt
    }

    // zweiter Lauf auf dem umgeordneten Quelltext
    if (logGroesse >= 0 && truncate(logName, logGroesse) != 0) { /* Log bleibt laenger: nur Schoenheitsfehler */ }
    pass2Zuruecksetzen();
    pass2Wiederholung = 1;
    pass2(logName, symName);
    int ok = (is_error2 == 0);
    for (int q = 0; ok && q < m; q++) {
        if (erwartet[q] >= 0 && optAdrVor[q] != (unsigned int)erwartet[q]) ok = 0;
    }
    if (!ok) {
        // Ergebnis verwerfen: Quelltext ohne Optimierung
        memcpy(lineAsmAufgeloestTemp, sicherung, sizeof(lineElements) * (size_t)n0);
        lineCountAsmAufgeloestTemp = n0;
        if (logGroesse >= 0 && truncate(logName, logGroesse) != 0) { }
        pass2Zuruecksetzen();
        pass2(logName, symName);
    }
    pass2Wiederholung = 0;
    free(erwartet); free(sicherung); free(optAdrVor); free(optAdrNach);
    optAdrVor = optAdrNach = NULL;
    optBloeckeFreigeben();
}

// pass2Wiederholung und pass2Stumm stehen auf jedem Rueckweg wieder auf 0 (die Aufrufer wissen nichts von den Probelaeufen).
void pass2MitOptimierer(char *logName, char *symName) {
    pass2MitOptimiererLauf(logName, symName);
    pass2Wiederholung = 0;
    pass2Stumm = 0;
}
