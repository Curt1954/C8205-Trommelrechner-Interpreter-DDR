// ca82_hilfen.c - Zeilenfelder, Meldungen mit Ort und kleine Textwerkzeuge
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"





// ########################################################################

// Oeffnet eine Ausgabedatei; bei Misserfolg Meldung mit Dateiname und Ursache auf STDERR und Abbruch
// (frueher wurde ein NULL-Zeiger weiterbenutzt und der Assembler stuerzte ab).
FILE *oeffneAusgabedatei(const char *pfad, const char *modus) {
    FILE *f = fopen(pfad, modus);
    if (f == NULL) {
        fflush(stdout);
        fprintf(stderr, "%s: %sFehler:%s Datei kann nicht geschrieben werden: %s\n", pfad, _violett, _normal, strerror(errno));
        exit(RC_FEHLER);
    }
    return f;
}

void resetParsedLinesArrays(lineElements zeilen[], int anzahl) {
    zeilen[anzahl].sp1[0] = '\0';
    zeilen[anzahl].sp2[0] = '\0';
    zeilen[anzahl].sp3[0] = '\0';
    zeilen[anzahl].sp4[0] = '\0';
}



void copyLineElements(lineElements *output, lineElements *ergebnis, int i) {
    STRKOPIE(output[i].sp1, ergebnis[i].sp1);
    STRKOPIE(output[i].sp2, ergebnis[i].sp2);
    STRKOPIE(output[i].sp3, ergebnis[i].sp3);
    STRKOPIE(output[i].sp4, ergebnis[i].sp4);
    output[i].srcLine = ergebnis[i].srcLine;
}


bool isValidLabel(const char *label) {
    // Prüfen, ob das Label existiert und nicht leer ist
    if (!label || strlen(label) == 0) {
        return false;
    }

    size_t len = strlen(label);

    // Wenn das letzte Zeichen ':' ist, ignorieren
    if (label[len - 1] == ':') {
        len--; // Länge reduzieren, um das ':' zu ignorieren
    }

    // Doku 2, <adresssymbol>: Das erste Zeichen ist ein Buchstabe (auch '_' wird akzeptiert), keine Ziffer.
    if (len > 0 && isdigit((unsigned char)label[0])) {
        return false;
    }

    // Überprüfung jedes Zeichens
    for (size_t i = 0; i < len; i++) {
        if (!isalpha(label[i]) && label[i] != ';' && label[i] != '_' && !isdigit(label[i])) {
            return false; // Ungültiges Zeichen gefunden
        }
    }

    return true; // Alle Zeichen sind gültig
}


void copyAndIncrementLineElements(int i) {
    pruefeZeilenfeld(lineCountAsmAufgeloestTemp);
    STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, lineAsmAufgeloest[i].sp1);
    STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, lineAsmAufgeloest[i].sp2);
    STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, lineAsmAufgeloest[i].sp3);
    STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, lineAsmAufgeloest[i].sp4);
    lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].srcLine = lineAsmAufgeloest[i].srcLine;
    
    lineCountAsmAufgeloestTemp++; 
}




void meldeFehlerP2(lineElements lineAsmAufgeloestTemp_p[], lineElements lineAsmAufgeloest_p[], int *lineCountAsmAufgeloest_p, int *i, const char *message) {
    pruefeZeilenfeld(*lineCountAsmAufgeloest_p);

    while (1) { 
        char *trimmed = lineAsmAufgeloestTemp_p[(*i)+1].sp1;
        size_t len_violett = strlen(_violett); // Länge von `_violett` berechnen
        trimmed += len_violett; // `_violett` überspringen

        if (*trimmed != '*') {
            break; // Schleife beenden, wenn kein '*' mehr da ist
        }
        STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp1, lineAsmAufgeloestTemp_p[(*i)+1].sp1);
        STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp2, lineAsmAufgeloestTemp_p[(*i)+1].sp2);
        STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp3, lineAsmAufgeloestTemp_p[(*i)+1].sp3);
        STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp4, lineAsmAufgeloestTemp_p[(*i)+1].sp4);
        lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].srcLine = lineAsmAufgeloestTemp_p[(*i)+1].srcLine;
        (*lineCountAsmAufgeloest_p)++;
        (*i)++;
    }

    char fehlertext_p[1024];
    snprintf(fehlertext_p, sizeof(fehlertext_p), ";%s*** (2) Fehler%s: %s\n", _violett, _normal, message);

    STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp1, fehlertext_p);
    STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp2, "");
    STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp3, "");
    STRKOPIE(lineAsmAufgeloest_p[*lineCountAsmAufgeloest_p].sp4, "");
    (*lineCountAsmAufgeloest_p)++;
}



// Funktionsprototyp
void toLowerCase(char *str);
void toLowerCase(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] = tolower((unsigned char)str[i]);
    }
}

void trim(char *str) {
    char *start = str;
    while (*start == ' ' || *start == '\t') start++;
    char *end = start + strlen(start) - 1;
    while (end > start && (*end == ' ' || *end == '\t' || *end == '\n')) end--;
    *(end + 1) = '\0';
    memmove(str, start, strlen(start) + 1);   // in place: Quelle liegt im Ziel
}


void removeTrailingSpaces(char *line) {
    int len = strlen(line);
    while (len > 0 && line[len - 1] == ' ') {
        len--;
    }
    line[len] = '\0';
}

void printHexLine(const char *line) {
    while (*line != '\0') {
        printf("%02X ", (unsigned char)*line);
        line++;
    }
    printf("00\n"); // Null-Terminierung (\0) anzeigen
}

void cleanLine(char *line) {
    char *src = line, *dst = line;
    // Entferne alle '\n'
    while (*src != '\0') {
        if (*src != '\n') {
            *dst++ = *src;
        }
        src++;
    }
    *dst = '\0';
    // Entferne alle trailing Leerzeichen
    size_t len = strlen(line);
    while (len > 0 && line[len - 1] == ' ') {
        len--;
    }
    line[len] = '\0';
}

void printAdressError(const char *label, char *typ, char *text, char *line) {
    PRINT_FEHLER("bei Operand: %s %s %s in Zeile: `%s`", label, typ, text, line);
    printf("%s%s%s\n\n",_weiss, line,_normal);
    printf("    ");
}
void printLabelError(const char *label, char *typ, char *text, char *line) {
    PRINT_FEHLER("bei Labeldefinition: %s %s %s", label, typ, text);
    printf("%s%s%s\n\n",_weiss, line,_normal);
    printf("    ");
}
void printLabelWarning(const char *label, char *typ, char *text) {
    PRINT_WARNUNG("bei Labeldefinition: %s %s %s\n\n", label, typ, text);
}
void printMacroParameterWarning(const char *label, char *typ, char *text, char *line) {
    PRINT_WARNUNG("bei Macrodefinition: %s %s %s", label ? label : "",  typ ? typ : "", text);
    printf("%s%s%s\n",_weiss, line,_normal);
}
void printMacroParameterError(const char *label, char *typ, char *text, char *line) {
    PRINT_FEHLER("bei Macrodefinition: %s %s %s", label ? label : "", typ ? typ : "", text);
    printf("%s%s%s\n",_weiss, line ? line : "" , _normal);
}

// ##############################

int macroIfAufloesen(lineElements *macroline, int *imIf, int * inBedingung);

void trimLeadingSpaces(char *line) {
    char *start = line;
    
    // Überspringe führende Leerzeichen
    while ((*start == ' ') || (*start == '\t'))   {
        start++;
    }

    // Prüfe, ob die bereinigte Zeichenkette mit einem der gewünschten Zeichen beginnt
    if (*start == ';' || *start == '#' || *start == '&' || *start == '$' || *start == '*' || *start == '&') {
        memmove(line, start, strlen(start) + 1);  // Verschiebt den relevanten Teil nach vorne
    }
}


void printAssemblerzeilenArray() {
    void trim_p(char *str) {
        char *end;
        while (isspace((unsigned char)*str)) str++;
        if (*str == 0) return;
        end = str + strlen(str) - 1;
        while (end > str && isspace((unsigned char)*end)) end--;
        *(end + 1) = '\0';
    }

    int maxSp1 = 0, maxSp2 = 0, maxSp3 = 0;

    for (int i = 0; i < PROGRAMMZEILEN; i++) {
        if (linesAsm[i].sp1[0] != ';' && linesAsm[i].sp1[0] != '#' && linesAsm[i].sp1[0] != '$'  && linesAsm[i].sp1[0] != '*'  && linesAsm[i].sp1[0] != '&') {
            int lenSp1 = strlen(linesAsm[i].sp1);
            if (lenSp1 > maxSp1) maxSp1 = lenSp1;
        }

        int lenSp2 = strlen(linesAsm[i].sp2);
        int lenSp3 = strlen(linesAsm[i].sp3);

        if (lenSp2 > maxSp2) maxSp2 = lenSp2;
        if (lenSp3 > maxSp3) maxSp3 = lenSp3;
    }

    for (int i = 0; i < PROGRAMMZEILEN; i++) {
        if (strlen(linesAsm[i].sp1) == 0 && strlen(linesAsm[i].sp2) == 0 &&
            strlen(linesAsm[i].sp3) == 0 && strlen(linesAsm[i].sp4) == 0) {
            break;
        }
        trim_p(linesAsm[i].sp4);
        printf("%04d: %-*s %-*s %-*s %s\n", 
               i + 1, maxSp1, linesAsm[i].sp1, maxSp2, linesAsm[i].sp2, maxSp3, linesAsm[i].sp3, linesAsm[i].sp4);
    }
}


// ----------------------------------------

// Schutz vor Ueberlauf der festen Zeilenfelder (Literalzeilen, Fehlermarken, Textzeichen aus dt/dto/dtm):
// Bricht mit Meldung ab, bevor ein Feld mit PROGRAMMZEILEN Eintraegen beschrieben wird.
void pruefeZeilenfeld(int belegt) {
    if (belegt >= PROGRAMMZEILEN - 8) {
        fflush(stdout);
        fprintf(stderr, "%s: %sFehler:%s Das interne Zeilenfeld ist voll (mehr als %d Zeilen einschliesslich Literalen, Fehlermarken und Textzeichen). Abbruch.\n",
                inputFileName, _violett, _normal, PROGRAMMZEILEN);
        exit(RC_FEHLER);
    }
}

// Meldung, wenn der Quelltext (einschliesslich Makroexpansion) die feste Zeilengrenze ueberschreitet.
void meldeZuVieleZeilen(int quellzeile) {
    char text[200];
    snprintf(text, sizeof(text), "Zu viele Zeilen: Quelltext einschliesslich Makroexpansion darf hoechstens %d Zeilen haben.", ZEILEN_GRENZE);
    fehlerMitOrt(quellzeile, text);
}

void meldeWarnungOrt(int quellzeile, const char *text) {
    fflush(stdout);
    if (quellzeile > 0) fprintf(stderr, "%s:%d: %sWarnung:%s %s\n", inputFileName, quellzeile, _gelb, _normal, text);
    else                fprintf(stderr, "%s: %sWarnung:%s %s\n", inputFileName, _gelb, _normal, text);
    if (berichtLog) {
        if (quellzeile > 0) fprintf(berichtLog, "%s:%d: Warnung: %s\n", inputFileName, quellzeile, text);
        else                fprintf(berichtLog, "%s: Warnung: %s\n", inputFileName, text);
    }
}

// Gibt die im Listing erzeugten Fehlermarken (";*** ... Fehler: text") zusaetzlich auf STDERR aus,
// im Format  datei:zeile: Fehler: text. Die Zeile ist die Quellzeile der naechstvorhergehenden
// echten Programmzeile (srcLine). Fuer Fehler aus Pass 0 bis 2, die sonst nur im Listing stehen.
void meldeListingFehlerAufStderr(lineElements zeilen[], int anzahl) {
    size_t lv = strlen(_violett), ln = strlen(_normal);
    int letzteZeile = 0;
    fflush(stdout);
    for (int i = 0; i < anzahl; i++) {
        const char *sp1 = zeilen[i].sp1;
        int istMarke = 0;
        if (sp1[0] == ';' && strncmp(sp1 + 1, _violett, lv) == 0 && strncmp(sp1 + 1 + lv, "*** ", 4) == 0) istMarke = 1;
        if (!istMarke) {
            if (zeilen[i].srcLine > 0) letzteZeile = zeilen[i].srcLine;
            continue;
        }
        const char *p = strstr(sp1, "Fehler");
        if (p == NULL || p - sp1 > 20) continue;           // Warnungen u. a. nicht melden
        p += 6;
        if (strncmp(p, _normal, ln) == 0) p += ln;
        if (*p == ':') p++;
        while (*p == ' ') p++;
        char text[512];
        STRKOPIE(text, p);
        size_t tl = strlen(text);
        while (tl > 0 && (text[tl - 1] == '\n' || text[tl - 1] == ' ')) text[--tl] = '\0';
        fehlerMitOrt(letzteZeile, text);
    }
}
