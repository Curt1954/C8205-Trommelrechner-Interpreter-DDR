#include "ca82_standards.h"
#include "c8205_op_codes.c"
#include <stdarg.h>
#include <errno.h>

#define BITMASK 010000000000  
#define EQU_ELEMENTS 4096

char fehlertext[4096];

// Maximale Laenge einer Quelltextzeile in Bytes (interne Puffer: MACRO_PARAMETER_LAENGE = 256 inkl. Endezeichen)
#define MAX_QUELLZEILE 255

#define MACRO_PARAMETER_ANZAHL 32
#define MACRO_PARAMETER_LAENGE 256

#define PROGRAMMZEILEN 8192
#define MACRODEFINITIONEN 4096

typedef struct {
    char label[LABEL_SIZE];
    int lineNumber;
} MacroLabel;

typedef char elementType[MACRO_PARAMETER_LAENGE];
typedef struct {
    elementType sp1;
    elementType sp2;
    elementType sp3;
    elementType sp4;
} lineElements;

lineElements linesAsm[PROGRAMMZEILEN];  //2 MB
int lineCountAsm = 0; 

typedef struct {
    char macroName[MACRO_PARAMETER_LAENGE];
    char macro[16];
    int macroParameterAnzahl;
    char macroParameters[MACRO_PARAMETER_ANZAHL][MACRO_PARAMETER_LAENGE]; 
    int macroLineCount;
    lineElements *macroParsedLines;  
    int ausQuelltext;                // 1 = im Quelltext definiert, 0 = aus der Makrodatei
} macroDefinitionen;

#define INITIAL_SIZE 10   // Starte mit 10 Makros
#define GROWTH_FACTOR 2   // Verdopple die Größe bei Bedarf
macroDefinitionen *macros; // Zeiger auf ein dynamisch zugewiesenes Array
int macroCount = 0;
int macroCapacity = INITIAL_SIZE;  // Aktuelle Größe des Arrays
char recursiv_macro[128]="";



// ########################################################################

void resetParsedLinesArrays(lineElements lineAsmAufgeloest[], int lineCountAsmAufgeloest) {
    lineAsmAufgeloest[lineCountAsmAufgeloest].sp1[0] = '\0';
    lineAsmAufgeloest[lineCountAsmAufgeloest].sp2[0] = '\0';
    lineAsmAufgeloest[lineCountAsmAufgeloest].sp3[0] = '\0';
    lineAsmAufgeloest[lineCountAsmAufgeloest].sp4[0] = '\0';
}

lineElements lineAsmAufgeloest[PROGRAMMZEILEN];
int lineCountAsmAufgeloest = 0; 

lineElements lineAsmAufgeloestTemp[PROGRAMMZEILEN];
int lineCountAsmAufgeloestTemp = 0; 

typedef struct {
    char sp0[32];
    elementType sp1;
    elementType sp2;
    elementType sp3;
    elementType sp4;
    int adr;        // Trommeladresse der Zeile (nur gueltig, wenn adrValid == 1)
    int adrValid;   // 1 = Zeile traegt eine Adresse, die sp0 nicht enthaelt (dt/dto/dtm)
} lineElementsX;

lineElementsX lineAsmAufgeloestX[PROGRAMMZEILEN];
int lineCountAsmAufgeloestX = 0; 


void copyLineElements(lineElements *output, lineElements *ergebnis, int i) {
    strcpy(output[i].sp1, ergebnis[i].sp1);
    strcpy(output[i].sp2, ergebnis[i].sp2);
    strcpy(output[i].sp3, ergebnis[i].sp3);
    strcpy(output[i].sp4, ergebnis[i].sp4);
}

#define MELDE_FEHLER(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Fehler%s: " format, _violett, _normal, __VA_ARGS__); \
        strcpy(result[*lineCount].sp1, fehlertext); \
        (*lineCount)++; \
    } while (0)

#define MELDE_WARNUNG(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Warnung%s: " format, _gelb, _normal, __VA_ARGS__); \
        strcpy(result[*lineCount].sp1, fehlertext); \
        (*lineCount)++; \
    } while (0)

#define REALLOC_RESULT \
    do { \
        lineElements *temp = (lineElements *)realloc(result, (*lineCount + 1) * sizeof(lineElements)); \
        if (!temp) { \
            fprintf(stderr, "Speicherfehler bei Realloc!\n"); \
            exit(RC_FEHLER); \
        } \
        result = temp; \
    } while (0)

#define REALLOC_ERGEBNIS \
    lineElements *temp = (lineElements *)realloc(*ergebnis, (*lineCount + 1) * sizeof(lineElements)); \
    if (!temp) { \
        free(*ergebnis); \
        fprintf(stderr, "Speicherfehler!\n"); \
        exit(RC_FEHLER); \
    } \
    *ergebnis = temp;

//Pointer-Varianten
#define REALLOC_RESULT2 \
    do { \
        lineElements *temp = (lineElements *)realloc(*result, (*lineCount + 1) * sizeof(lineElements)); \
        if (!temp) { \
            free(*result); \
            return -1; /* Gebe einen Fehlercode zurück, statt NULL wei die übergeordnete Funktion es so will*/ \
        } \
        *result = temp; \
    } while (0)

#define MELDE_FEHLER2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Fehler%s: " format, _violett, _normal, __VA_ARGS__); \
        strcpy((*result)[*lineCount].sp1, fehlertext); \
        strcpy((*result)[*lineCount].sp2, ""); \
        strcpy((*result)[*lineCount].sp3, ""); \
        strcpy((*result)[*lineCount].sp4, ""); \
        (*lineCount)++; \
    } while (0)

#define MELDE_WARNUNG2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Warnung%s: " format, _gelb, _normal, __VA_ARGS__); \
        strcpy((*result)[*lineCount].sp1, fehlertext); \
        strcpy((*result)[*lineCount].sp2, ""); \
        strcpy((*result)[*lineCount].sp3, ""); \
        strcpy((*result)[*lineCount].sp4, ""); \
        (*lineCount)++; \
    } while (0)



// ----------------------------
//

#define MELDE_FEHLER_P1(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 1 Fehler%s: " format , _violett, _normal, __VA_ARGS__); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, fehlertext); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, ""); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, ""); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, ""); \
        lineCountAsmAufgeloestTemp++; \
    } while (0)

#define MELDE_WARNUNG_P1(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 1 Warnung%s: " format , _gelb, _normal, __VA_ARGS__); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, fehlertext); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, ""); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, ""); \
        strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, ""); \
        lineCountAsmAufgeloestTemp++; \
    } while (0)



#define MELDE_FEHLER_P2(i, message) \
    meldeFehlerP2(lineAsmAufgeloestTemp, lineAsmAufgeloest, &lineCountAsmAufgeloest, &i, message)

#define MELDE_WARNUNG_P2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 2 Warnung%s: " format , _gelb, _normal, __VA_ARGS__); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, fehlertext); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, ""); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, ""); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, ""); \
        lineCountAsmAufgeloest++; \
    } while (0)

#define MELDE_MSG_P2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 2 Hinweis%s: " format "\n", _gruen, _normal, __VA_ARGS__); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, fehlertext); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, ""); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, ""); \
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, ""); \
        lineCountAsmAufgeloest++; \
    } while (0)

// ------------------------------
int is_error  = 0;
int is_error0 = 0;
int is_error1 = 0;
int is_error2 = 0;
int is_error3 = 0;
int is_error_abs = 0;
int printHell = 0;

// Pragma ";#; LEITADRESSE xx": Kennzeichen, das im Objektcode (.obj) und im Listing (STDOUT, .dmp) anstelle von 01 ausgegeben wird.
// Standard 01, erlaubt sind 01 bis 09.
int leitadresseKennzeichen = 1;
int leitadressePragmaGesetzt = 0;   // 1, wenn das Pragma im Quelltext angegeben war

unsigned int absolutadresse;

typedef struct {
    char literalName[MAX_SYMBOL_LENGTH];  
    char literalValue[MAX_LINE_LENGTH];   
    unsigned int relativAdresse;          
} Literal;
Literal literalTable[MAX_LITERALS];

typedef struct {
    char symbol[MAX_SYMBOL_LENGTH]; 
    int address;
    unsigned int relativAdresse;
    char orig_operation[MAX_SYMBOL_LENGTH]; 
} Symbol;
Symbol symbolTable[MAX_SYMBOLS];
int symbolCount = 0, literalCount = 0;

unsigned int sternadresseBearbeiten(char *xoperand, char *line, int *errorFlag, unsigned int programCounter);
unsigned int evaluateAddress(char *operand, char *line, int *errorFlag, int *raAdr, char *label, unsigned int programCounter, unsigned int *absolutadresse);
int isSymbol(char *token);

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
    strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, lineAsmAufgeloest[i].sp1);
    strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, lineAsmAufgeloest[i].sp2);
    strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, lineAsmAufgeloest[i].sp3);
    strcpy(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, lineAsmAufgeloest[i].sp4);
    
    lineCountAsmAufgeloestTemp++; 
}

int isLiteralInTable(const char *name) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalName, name) == 0) {
            return 1; // Literal gefunden
        }
    }
    return 0; // Literal nicht vorhanden
}

int isLiteralInTableRelativAdresse(const char *name) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalName, name) == 0) {
            return literalTable[i].relativAdresse;
        }
    }
    return -1; // Literal nicht vorhanden
}


void meldeFehlerP2(lineElements lineAsmAufgeloestTemp[], lineElements lineAsmAufgeloest[], int *lineCountAsmAufgeloest, int *i, const char *message) {

    while (1) { 
        char *trimmed = lineAsmAufgeloestTemp[(*i)+1].sp1;
        size_t len_violett = strlen(_violett); // Länge von `_violett` berechnen
        trimmed += len_violett; // `_violett` überspringen

        if (*trimmed != '*') {
            break; // Schleife beenden, wenn kein '*' mehr da ist
        }
        strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp1, lineAsmAufgeloestTemp[(*i)+1].sp1);
        strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp2, lineAsmAufgeloestTemp[(*i)+1].sp2);
        strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp3, lineAsmAufgeloestTemp[(*i)+1].sp3);
        strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp4, lineAsmAufgeloestTemp[(*i)+1].sp4);
        (*lineCountAsmAufgeloest)++;
        (*i)++;
    }

    char fehlertext[1024];
    snprintf(fehlertext, sizeof(fehlertext), ";%s*** (2) Fehler%s: %s\n", _violett, _normal, message);

    strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp1, fehlertext);
    strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp2, "");
    strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp3, "");
    strcpy(lineAsmAufgeloest[*lineCountAsmAufgeloest].sp4, "");
    (*lineCountAsmAufgeloest)++;
}

// HINWEIS (Bereinigung): Die Parameter hießen zuvor in der Deklaration "operand, operation",
// wurden aber von ALLEN Aufrufstellen konsequent in der Reihenfolge "operation, operand" befüllt.
// Funktional war das unproblematisch (der frühere Parameter "operand" wurde im Funktionskörper
// gar nicht benutzt), aber irreführend. Hier an die tatsächliche Verwendung angepasst:
// "operation" ist der Mnemonic/die Anweisung (z. B. "da", "dw"), "operand" ist der Adressausdruck
// (z. B. "a", "zvektor"), der bei vorwärtsreferenzierten Symbolen später von resolveSymbols()
// ausgewertet und für orig_operation benötigt wird.
void addSymbol(char *symbol, int address, int relativAdresse, char *operation, char *operand, int nr, int i) {
    char message[1024];
    strtok(symbol, ":"); // Entfernt ':' am Ende

    if (symbolCount >= MAX_SYMBOLS) {
        sprintf(message, "(%i): Symbol-Tabelle ist voll. Symbol '%s' konnte nicht hinzugefügt werden.\n", nr, symbol);
        MELDE_FEHLER_P2(i, message );
        is_error2 = 1; 
        return;
    }

    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, symbol) == 0) {
            if ( strcmp(operation, "abs") == 0 ) {
                return;  
            }
            sprintf(message, "(%i): Symbol existiert bereits. Symbol '%s' konnte nicht hinzugefügt werden.\n", nr, symbol);
            MELDE_FEHLER_P2(i, message );
            is_error2 = 1; 
            return;
        }
    }

    unsigned int  relAdr =  isLiteralInTableRelativAdresse( symbol) ;
    if (relAdr != -1 ) {
       symbolTable[symbolCount].relativAdresse = relAdr;
    } else { 
       symbolTable[symbolCount].relativAdresse = relativAdresse;
    }

    strcpy(symbolTable[symbolCount].symbol, symbol);
    symbolTable[symbolCount].address = address;
    if ( strstr(operand,";") != 0) {
       strcpy(symbolTable[symbolCount].orig_operation , "");
    } else {
       strcpy(symbolTable[symbolCount].orig_operation , operand);
    }
    symbolCount++;
    //sprintf(message, "(%i): Symbol '%s' hinzugefügt.",nr, symbol);
    //MELDE_MSG_P2("%s", message );
}


const char* getLiteralNameByValue(const char *value) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalValue, value) == 0) {
            return literalTable[i].literalName; // Literal gefunden, Name zurückgeben
        }
    }
    return ""; // Kein passendes Literal gefunden
}

const char* addLiteral(char *literalName, char *literalValue, unsigned int relativAdresse) {
    if (literalCount >= MAX_LITERALS) {
        MELDE_FEHLER_P1("Literal-Tabelle ist voll. Literal '%s' konnte nicht hinzugefügt werden.", literalName);
        is_error  = 1;
        return ""; 
    }

    if (isLiteralInTable( literalName) == 1 ) { return ""; }  // Literal schon vorhanden
    static char oldName[256];
    strcpy (oldName, getLiteralNameByValue(literalValue) );
    if ( strlen(oldName) > 0 ) { return (strlen(oldName) > 0) ? oldName : ""; }

    strcpy(literalTable[literalCount].literalName, literalName);
    strcpy(literalTable[literalCount].literalValue, literalValue);
    literalTable[literalCount].relativAdresse = relativAdresse;
    literalCount++;

    return "";
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
    strcpy(str, start);
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
    void trim(char *str) {
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
        trim(linesAsm[i].sp4);
        printf("%04d: %-*s %-*s %-*s %s\n", 
               i + 1, maxSp1, linesAsm[i].sp1, maxSp2, linesAsm[i].sp2, maxSp3, linesAsm[i].sp3, linesAsm[i].sp4);
    }
}


// Text-Anweisungen: Der Operand ist ein Text (Zeichenfolge, ggf. in \...\), kein Zahlen- oder
// Adressausdruck. Dort sind ';' und '#' (Doku 2, <sonderzeichen>) einfache Textzeichen, und ein
// fuehrendes '#' leitet kein Literal ein.
static int istTextAnweisung(const char *operation) {
    return strcmp(operation, "dt") == 0 || strcmp(operation, "dto") == 0 || strcmp(operation, "dtm") == 0;
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
void processLine(char *line, lineElements linesAsm[], int *lineCount) {
    int posIndex = 0;

    // Aktuelle Zeile initialisieren
    resetParsedLinesArrays(linesAsm, *lineCount);
    trimLeadingSpaces(line);

    while (*line) {

        if ((posIndex == 0) && ((*line == ';') || (*line == '#') || (*line == '$')  || (*line == '&') )) {
            strcpy(linesAsm[*lineCount].sp1, line);
            removeNewlines(linesAsm[*lineCount].sp1);
            trimWhitespace(linesAsm[*lineCount].sp1);
            (*lineCount)++;
            return;
        }

        if ((*line != ' ') && (*line != '\t') && (*line != ';') && (*line != '#')  && (*line != '$')  && (*line != '&') && (posIndex == 0)) {
            char *colonPos = strchr(line, ':');
            if (colonPos) {
                int labelLength = colonPos - line + 1;  // +1, um `:` einzuschließen
                strncpy(linesAsm[*lineCount].sp1, line, labelLength);
                linesAsm[*lineCount].sp1[labelLength] = '\0'; // Nullterminierung
                removeNewlines(linesAsm[*lineCount].sp1);
                trimWhitespace(linesAsm[*lineCount].sp1);
                line = colonPos + 1;
                posIndex = labelLength;  // Kein `+1`, da `:` bereits enthalten ist
            }
        }

        while (*line && isspace((unsigned char)*line)) line++;

        char *nextSpace = strpbrk(line, " \t\n");
        if (nextSpace) {
            if ((*line == ';') && (posIndex > 0)) {
                strcpy(linesAsm[*lineCount].sp4, line);
                removeNewlines(linesAsm[*lineCount].sp4);
                trimWhitespace(linesAsm[*lineCount].sp4);
                (*lineCount)++;
                return;
            }

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }
            char *nextSpace = strpbrk(line, " \t\n;");
            int wordLength = nextSpace ? (nextSpace - line) : strlen(line);

            strncpy(linesAsm[*lineCount].sp2, line, wordLength);
            linesAsm[*lineCount].sp2[wordLength] = '\0';
            removeNewlines(linesAsm[*lineCount].sp2);
            trimWhitespace(linesAsm[*lineCount].sp2);

            posIndex += wordLength;
            line += wordLength; 

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }

            char *restEnd = findeOperandEnde(linesAsm[*lineCount].sp2, line);
            int restLength = restEnd ? (restEnd - line) : strlen(line);
            strncpy(linesAsm[*lineCount].sp3, line, restLength);
            linesAsm[*lineCount].sp3[restLength] = '\0';
            removeNewlines(linesAsm[*lineCount].sp3);
            trimWhitespace(linesAsm[*lineCount].sp3);
            posIndex += restLength;
            line += restLength;
            removeNewlines(line);
            if (strlen(line) == 0) {
                (*lineCount)++;
                return;
            }
        }

        if ((*line == ';') && (posIndex > 0)) {
            strcpy(linesAsm[*lineCount].sp4, line);
            removeNewlines(linesAsm[*lineCount].sp4);
            trimWhitespace(linesAsm[*lineCount].sp4);
            (*lineCount)++;
            return;
        }

        // nur Operationscode angegeben
        if (( strlen(line) > 0) ) {
            strcpy(linesAsm[*lineCount].sp2, line);
            removeNewlines(linesAsm[*lineCount].sp2);
            trimWhitespace(linesAsm[*lineCount].sp2);
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

// Vergleich ohne Beachtung der Gross-/Kleinschreibung (nur fuer Pragma-Schluesselwort und start).
static int gleichOhneGrossKlein(const char *a, const char *b) {
    while (*a && *b) {
        if (toupper((unsigned char)*a) != toupper((unsigned char)*b)) return 0;
        a++; b++;
    }
    return *a == '\0' && *b == '\0';
}

// Pragma   ;#; LEITADRESSE xx
//   - steht als Kommentarzeile im Quelltext und muss VOR `start` stehen,
//   - darf keinmal oder genau einmal vorkommen (Standard ohne Pragma: 01),
//   - xx ist zweistellig und liegt zwischen 01 und 09.
// Wirkung: Alle Befehle und Konstanten, die im Objektcode (.obj) bisher mit dem Kennzeichen 01 erzeugt
// wurden, erhalten stattdessen den Wert xx (siehe schreibeObjZeile).
// Liefert 1, wenn die Zeile ein LEITADRESSE-Pragma ist (auch ein fehlerhaftes), sonst 0.
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

    if (startGesehen) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE muss vor `start` stehen.", zeilennr);
        is_error = 1;
        return 1;
    }
    if (leitadressePragmaGesetzt) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE darf nur einmal vorkommen.", zeilennr);
        is_error = 1;
        return 1;
    }
    leitadressePragmaGesetzt = 1;

    // Wert: genau zwei Ziffern 01 ... 09; danach nur noch Leerraum oder ein Kommentar (;).
    int wertOk = isdigit((unsigned char)p[0]) && isdigit((unsigned char)p[1])
                 && (p[2] == '\0' || p[2] == ' ' || p[2] == '\t' || p[2] == ';' || p[2] == '\r' || p[2] == '\n');
    int wert = wertOk ? (p[0] - '0') * 10 + (p[1] - '0') : 0;
    if (!wertOk || wert < 1 || wert > 9) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE erwartet einen zweistelligen Wert von 01 bis 09 (z. B. ;#; LEITADRESSE 02).", zeilennr);
        is_error = 1;
        return 1;
    }
    leitadresseKennzeichen = wert;
    return 1;
}

void ladeAssemblerZeilen(const char *inputFileName) {
    FILE *inputFile = fopen(inputFileName, "r");
    if (!inputFile) {
        fprintf(stderr, "Fehler: Datei '%s' konnte nicht geöffnet werden!\n", inputFileName);
        exit(RC_FEHLER); // Programm beenden, falls Datei nicht geöffnet werden konnte
    }

    char line[1024];
    int zeilennr = 0;
    int vorigeZeileOffen = 0;   // 1 = vorige fgets-Teilzeile hatte kein Zeilenende (Zeile laenger als Puffer)
    int startGesehen = 0;       // 1, sobald die Anweisung `start` gelesen wurde (Pragma LEITADRESSE muss davor stehen)
    while (fgets(line, sizeof(line), inputFile)) {
        int hatZeilenende = (strchr(line, '\n') != NULL);

        if (vorigeZeileOffen) {            // Rest einer bereits gemeldeten, zu langen Zeile ueberspringen
            vorigeZeileOffen = !hatZeilenende;
            continue;
        }
        zeilennr++;

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
            PRINT_FEHLER("Zeile %d der Quelldatei ist zu lang (mehr als %d Zeichen); bitte kuerzen oder umbrechen.", zeilennr, MAX_QUELLZEILE);
            is_error = 1;
            continue;
        }
        verarbeiteLeitadressePragma(line, zeilennr, startGesehen);   // vor processLine: line wird dort veraendert
        int zeilenVorher = lineCountAsm;
        processLine(line, linesAsm, &lineCountAsm);
        if (lineCountAsm > zeilenVorher && gleichOhneGrossKlein(linesAsm[lineCountAsm - 1].sp2, "start")) {
            startGesehen = 1;
        }
    }
    fclose(inputFile); 

    //printAssemblerzeilenArray() ;
}


// ------------------------------

typedef struct {
    char *key;   
    char *value; 
} EquEntry;

EquEntry equ_tabelle[EQU_ELEMENTS];  
int equ_fuellstand = 0;

int appendToEquTable(const char *key, const char *value) {
    if ((equ_fuellstand < EQU_ELEMENTS) && (strlen(key) != 0)){
        equ_tabelle[equ_fuellstand].key = strdup(key);
        equ_tabelle[equ_fuellstand].value = strdup(value);
        equ_fuellstand++;
        return 0;
    }
    return -1; 
}

int sucheInEquTabelle(const char *suchbegriff) {
    for (int i = 0; i < equ_fuellstand; i++) {  
        if (strcmp(equ_tabelle[i].key, suchbegriff) == 0) {
            return 1;  
        }
    }
    return 0;  
}

typedef struct {
    char *key;   
    char *value; 
} AbsEntry;

AbsEntry abs_tabelle[EQU_ELEMENTS];  
int abs_fuellstand = 0;

// Zahl einer abs-Definition: fuehrende 0 = oktal, sonst dezimal (Doku 2, <oktalzahl>/<dezimalzahl>).
// Liefert 1 und den Wert, wenn der ganze String eine solche Zahl ist, sonst 0.
static int absZahlWert(const char *text, long *wert) {
    char *ende;
    if (text == NULL || *text == '\0') return 0;
    int basis = (text[0] == '0' && text[1] != '\0') ? 8 : 10;
    *wert = strtol(text, &ende, basis);
    return *ende == '\0';
}

// Gleicher Wert: numerisch, damit abs 010 und abs 8 als gleich gelten; Texte, die keine reine Zahl
// sind, werden wie bisher als Zeichenfolge verglichen.
static int absWerteGleich(const char *a, const char *b) {
    long wa, wb;
    if (absZahlWert(a, &wa) && absZahlWert(b, &wb)) return wa == wb;
    return strcmp(a, b) == 0;
}

int appendToAbsTable(const char *key, const char *value) {
    char key_copy[256];  
    strncpy(key_copy, key, sizeof(key_copy) - 1);
    key_copy[sizeof(key_copy) - 1] = '\0';  

    // Falls `key` auf ":" endet, entferne es
    size_t len = strlen(key_copy);
    if (len > 0 && key_copy[len - 1] == ':') {
        key_copy[len - 1] = '\0';
    }

    // Überprüfe, ob der modifizierte Schlüssel existiert
    for (int i = 0; i < abs_fuellstand; i++) {
        if (strcmp(abs_tabelle[i].key, key_copy) == 0) {
            if (absWerteGleich(abs_tabelle[i].value, value)) {
                return 0;  // Kein Update notwendig
            } else {
                return -1;  // Beenden ohne Änderung
            }
        }
    }

    // Falls der Schlüssel nicht existiert, füge ihn hinzu
    if (abs_fuellstand < EQU_ELEMENTS) {
        abs_tabelle[abs_fuellstand].key = strdup(key_copy);  // Verwende die bereinigte Kopie
        abs_tabelle[abs_fuellstand].value = strdup(value);
        abs_fuellstand++;
        return 0;
    }

    return -2;  // Tabelle ist voll, kein neuer Eintrag möglich
}

int sucheInAbsTabelle(const char *suchbegriff) {
    // Lokale Kopie erstellen
    char suchbegriff_copy[256];  // Speicher groß genug wählen
    strncpy(suchbegriff_copy, suchbegriff, sizeof(suchbegriff_copy) - 1);
    suchbegriff_copy[sizeof(suchbegriff_copy) - 1] = '\0'; // Null-Terminierung sicherstellen

    // Falls `suchbegriff_copy` auf `':'` endet, entfernen
    size_t len = strlen(suchbegriff_copy);
    if (len > 0 && suchbegriff_copy[len - 1] == ':') {
        suchbegriff_copy[len - 1] = '\0';
    }

    // Suche mit der modifizierten Kopie
    for (int i = 0; i < abs_fuellstand; i++) { 
        if (strcmp(abs_tabelle[i].key, suchbegriff_copy) == 0) {
            return 1;  //gefunden
        }
    }
    return 0;  
}


// ######################################################

const int trommel_sektor_map[32] = {
    0, 015, 032, 07, 024, 01, 016, 033, 010, 025, 02,
    017, 034, 011, 026, 03, 020, 035, 012, 027, 04, 021,
    036, 013, 030, 05, 022, 037, 014, 031, 06, 023
};

unsigned int berechneWiederholAdr(int anzahl, unsigned int basisAdr ) {
    int x = 31 - anzahl - 1;
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
    sscanf(start, "%s", operand_str);

    // Berechne den Wert des Operanden
    //int operand_value = strtol(operand_str, NULL, 10) - 1; // `9-1` → `8`
    int operand_value = berechneOperand(operand_str);
    unsigned int sektor_address = berechneWiederholAdr(operand_value, 07700);

    // Erstelle die neue Zeile mit der oktalen Sektoradresse (mit Vornull)
    char neueZeile[MAX_LINE_LENGTH];
    snprintf(neueZeile, sizeof(neueZeile), "     !$wdhl_adr_e   %05o     ; %d mal Linksverschiebung", sektor_address, operand_value);
    strcpy(tempLine, neueZeile);

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
    char *start = strstr(tempLine, "!$wdhl");
    char op[12]={0};
    int rc = 0 ;

    int berechneOpString(char *opStr, char *rStr, char *loe, char *result) {
        int rc = 0;
        char *OPCODE[]              = { "KON", "ADD", "SUB", "BADD" };
        int OP_Table[]              = { 060, 061, 062, 063 };
        int R_Zuordnung[]           = { 04, 02, 06, 0 };
        int R_Zuordnung_Loe[]       = { 05, 03, 07, 01 };

        int opNum = -1, rNum = -1;

        for (int i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                opNum = OP_Table[i];
                break;
            }
        }

        if ( opNum == -1 ) { return -1; }

        // R-Zuordnung basierend auf LOE (JA vs NE)
        int *R_Table = (strcmp(loe, "JA") == 0) ? R_Zuordnung_Loe : R_Zuordnung;
        for (int i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                rNum = R_Table[i];
                break;
            }
        }

        if ( rNum == -1 ) { return -1; }

        // Falls beide Werte gefunden wurden, erstelle den Ziffernstring
        if (opNum != -1 && rNum != -1) {
            snprintf(result, 10, "%o%o", opNum, rNum);
        } else {
            strcpy(result, "Macro gen. Op-Code Mismatch ??"); // Fehlerfall
            rc = -1;
        }

        return rc;
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
    strcpy(tempLine, neueZeile);

    char *pos = strstr(tempLine, "!#wdhl");
    if (pos != NULL) {
        memmove(pos + 3, pos + 6, strlen(pos + 6) + 1);
        memcpy(pos, op, 3);
    }
    if ( (rc == -3 )  ) { return rc; }
    return 0;
}

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
            snprintf(meldung, meldungGroesse, "Wert \"%s\" ist keine Konstante", arg);
            return 1;
        }
        int oktal = (arg[0] == '0');
        for (size_t k = 0; k < n; k++) {
            if (arg[k] > '7') oktal = 0;
        }
        if (!oktal) {
            snprintf(meldung, meldungGroesse, "Wert \"%s\" ist keine Oktalkonstante (Oktalzahlen beginnen mit 0 und enthalten nur 0-7)", arg);
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

#define SET_SP_VALUES(i, j) \
    do { \
        strncpy(SP1, macros[i].macroParsedLines[j].sp1, sizeof(SP1) - 1); \
        SP1[sizeof(SP1) - 1] = '\0'; \
        strncpy(SP2, macros[i].macroParsedLines[j].sp2, sizeof(SP2) - 1); \
        SP2[sizeof(SP2) - 1] = '\0'; \
        strncpy(SP3, macros[i].macroParsedLines[j].sp3, sizeof(SP3) - 1); \
        SP3[sizeof(SP3) - 1] = '\0'; \
        strncpy(SP4, macros[i].macroParsedLines[j].sp4, sizeof(SP4) - 1); \
        SP4[sizeof(SP4) - 1] = '\0'; \
    } while (0)


// ----------------------------

void macroFehlerausgabe(lineElements *ergebnis, int i, const char *fehlermeldung, const char *mna) {
    char mtemp[128];

    // Sicheres Kopieren von ergebnis[i].sp1 in mtemp mit Begrenzung
    strncpy(mtemp, ergebnis[i].sp1, sizeof(mtemp) - 1);
    mtemp[sizeof(mtemp) - 1] = '\0';  // Null-Termination erzwingen
    // Setze die Fehlermeldung in ergebnis[i].sp1
    snprintf(ergebnis[i].sp1, sizeof(ergebnis[i].sp1), ";%s*** Fehler%s %s %s <--.", _violett, _normal, fehlermeldung, mtemp);
    // Setze die anderen Felder auf leere Strings
    strcpy(ergebnis[i].sp2, "");
    strcpy(ergebnis[i].sp3, "");
    strcpy(ergebnis[i].sp4, "");
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

// bearbeitet nur die Zeile lineCount die den Macronamen enthält !!!
// prüft aber den ganzen Macro und gibt ALLE seine generierten zeilen zurück
lineElements* loeseMacroAuf(macroDefinitionen *macros, int *macroCount, char *aktuellerOpCode, char *aktuelleParameterZeile, int *lineCount , char *label) {

    lineElements *result = NULL;
    lineElements *tmp_result = NULL;

    *lineCount = 0;
    int imIf = 0;
    int inBedingung = 0;

    char fehlertab[64][512];
    int  fehlertab_count=0;
    char message[512];

    void trimQuotes(char *param) {
        size_t len = strlen(param);
        if (len > 1 && ((param[0] == '"' && param[len - 1] == '"') || (param[0] == '\'' && param[len - 1] == '\''))) {
            memmove(param, param + 1, len - 2);
            param[len - 2] = '\0';
        }
    }

    int isValidMacroKeyword(char *word) {
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

    void logMacroError(const char *format, const char *arg1, const char *arg2, const char *arg3) {
        if (fehlertab_count >= 64) {
            PRINT_FEHLER("%s", "Zu viele Fehler im Macro.");
            is_error = 1;
            return;
        }

        snprintf(fehlertab[fehlertab_count], 511, ";%s*** Fehler %s %s ", _violett, _normal, arg1);
        snprintf(fehlertab[fehlertab_count] + strlen(fehlertab[fehlertab_count]), 511 - strlen(fehlertab[fehlertab_count]), format, arg1, arg2, arg3);
        fehlertab_count++;
    }


    result = (lineElements *)malloc(sizeof(lineElements));
    if (!result) {
        fprintf(stderr, "Speicherzuweisung result fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }

    size_t len = strlen(aktuellerOpCode);
    if (aktuellerOpCode[len - 1] == ':') {
        aktuellerOpCode[len - 1] = '\0';
    }

    char AsmParamKopZl[MACRO_PARAMETER_LAENGE];
    char AsmParamArray[64][MACRO_PARAMETER_LAENGE]; 

    trimWhitespace(aktuelleParameterZeile);
    strncpy(AsmParamKopZl, aktuelleParameterZeile, MACRO_PARAMETER_LAENGE - 1);
    AsmParamKopZl[MACRO_PARAMETER_LAENGE - 1] = '\0';

    int AsmParamCount = 0;
    char *AsmParam = strtok(AsmParamKopZl, " \t");
    while (AsmParam != NULL && AsmParamCount < 64) {
        trimQuotes(AsmParam);  // Entfernt "" oder ''
        strncpy(AsmParamArray[AsmParamCount], AsmParam, MACRO_PARAMETER_LAENGE - 1);
        AsmParamArray[AsmParamCount][MACRO_PARAMETER_LAENGE - 1] = '\0';
        AsmParamCount++;
        AsmParam = strtok(NULL, " \t");
    }

    int rc=0;
    int grc=0;
    // Die Schleife bearbeitet alle aktuellerOpCode's die Macronamen sind.
    // Durch alle MACROs
    for (int i = 0; i < *macroCount; i++) {
        char zuPruefenderMacro[MACRO_PARAMETER_LAENGE];
        strcpy(zuPruefenderMacro, macros[i].macroName); 

        size_t tempLen = strlen(zuPruefenderMacro);
        if (zuPruefenderMacro[tempLen - 1] == ':') {
            zuPruefenderMacro[tempLen - 1] = '\0';
        }


        if (strcmp(aktuellerOpCode, zuPruefenderMacro) == 0) {
            char SP1[256], SP2[128], SP3[256], SP4[256];

            // Im makro
            if (AsmParamCount != macros[i].macroParameterAnzahl) {
                REALLOC_RESULT;              
                MELDE_FEHLER("erwartet %d Parameter, aber %d wurden übergeben!", macros[i].macroParameterAnzahl, AsmParamCount);
                is_error0 = 1;
                return result;
            }

            int found = 1;  // gefunden
            int equIndex = -1;  // Position der automatisch erzeugten equ-Zeile (-1 = keine)
            if ( strlen(label) > 0 ) { 
                // Label für Macroaufruf
                REALLOC_RESULT;  
                equIndex = *lineCount;
                strcpy(result[*lineCount].sp1, label);
                strcpy(result[*lineCount].sp2, "equ");
                strcpy(result[*lineCount].sp3, "*");
                strcpy(result[*lineCount].sp4, "; automatisch generiert"); 
                (*lineCount)++;
            }


            int ifCount = 0;  // Zählt offene $IF-Blöcke
            int insideIfBlock = 0; // Ist aktuell innerhalb eines $IF-Blocks

            for (int jj = 0; jj < macros[i].macroLineCount; jj++) {
                SET_SP_VALUES(i, jj);

                trimWhitespace(SP1);
                trimWhitespace(SP2);
                trimWhitespace(SP3);

                char *trimmed = SP1;
                while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Entfernt Leerzeichen & Tabs

                // **Überspringe Kommentarzeilen**
                if (*trimmed == ';' || *trimmed == '#' || *trimmed == '*' || *trimmed == '&' ) {
                    continue; // Springt zur nächsten Zeile
                }


                // Nur gültige Makro-Schlüsselwörter erlauben
                char combinedString[1024];  // Puffer für die zusammengesetzte Zeichenkette
                snprintf(combinedString, sizeof(combinedString), "%s %s %s", SP1, SP2, SP3);

                char *saveptr;
                char *token = strtok_r(combinedString, " \t", &saveptr);
                int erg=0;

                while (token != NULL) {
                    erg += isValidMacroKeyword(token);
                    token = strtok_r(NULL, " \t", &saveptr); // Nächstes Token holen
                }
                if (erg == 0) { 
                    logMacroError("Ungültiges Makro-Schlüsselwort: %s %s %s", SP1, SP2, SP3);
                    continue;
                }


                // **Überprüfung: Jedes Schlüsselwort nur einmal pro Zeile**
                int keywordTracker[restrictedCount]; 
                memset(keywordTracker, 0, sizeof(keywordTracker)); 

                char *tokens[] = {SP1, SP2, SP3};
                for (int t = 0; t < 3; t++) {
                    for (int k = 0; k < restrictedCount; k++) {
                        if (strcmp(tokens[t], restrictedKeywords[k]) == 0) {
                            if (keywordTracker[k] > 0) {
                                logMacroError("Makro-Schlüsselwort mehrfach in einer Zeile: %s %s%s", tokens[t],"","");
                            }
                            keywordTracker[k]++;
                        }
                    }
                }


                // Prüfe, ob bei "$PR?"  ? < macroparameteranzahl  
                if (strncmp(SP1, "$PR", 3) == 0 && isdigit(SP1[3])) {  
                    int parameterNummer = SP1[3] - '0';  // Konvertiere Zeichen zu einer Zahl

                    // Überprüfen, ob die Ziffer innerhalb der erlaubten Anzahl liegt
                    if (parameterNummer > macros[i].macroParameterAnzahl) {
                        char maxParamStr[10];  // Puffer für die Zeichenkette
                        snprintf(maxParamStr, sizeof(maxParamStr), "%d", macros[i].macroParameterAnzahl);
                        logMacroError("Ungültiger Parameter: %s (Max. erlaubt: $PR%s)%s", SP1, maxParamStr, "");
                    }
                }

//mkl
                // $PR?  **Prüfe, ob SP1 eines der gültigen $PR-Werte enthält**
                int foundPR = 0;
                if (strlen(SP1) > 0) {
                    for (int pr = 0; pr < 9; pr++) {
                        if (strncmp(SP1, validPR[pr], 4) == 0) {
                            foundPR = 1;
                            break;
                        }
                    }

                    // Falls ein $PR? gefunden wurde, prüfe das nächste Wort in SP1
                    if (foundPR) {
                        char pruefliste[256];  // Stelle sicher, dass genug Speicher da ist
                        strncpy(pruefliste, SP1, sizeof(pruefliste) - 1);
                        pruefliste[sizeof(pruefliste) - 1] = '\0';

                        void entferneErstesWort(char *pruefliste) {
                            int i = 0, j = 0;
                            while (pruefliste[i] == ' ' || pruefliste[i] == '\t') {
                                i++;
                            }
                            while (pruefliste[i] != ' ' && pruefliste[i] != '\t' && pruefliste[i] != '\0') {
                                i++;
                            }
                            while (pruefliste[i] == ' ' || pruefliste[i] == '\t') {
                                i++;
                            }
                            while (pruefliste[i] != '\0') {
                                pruefliste[j++] = pruefliste[i++];
                            }
                            pruefliste[j] = '\0'; 
                        }
                        entferneErstesWort(pruefliste);
                        char rest[256] = "";  
                        strcpy(rest, pruefliste);  

                        char *nextWord = strtok(rest, " \t"); 
                        //nextWord = strtok(NULL, " \t"); // Hole das nächste Wort
                        if (nextWord != NULL) {
                            int foundType = 0;
                            for (int t = 0; t < 3; t++) {
                                if (strcmp(nextWord, validType[t]) == 0) {
                                    foundType = 1;
                                    break;
                                }
                            }

                            // Falls $TYPADR, $TYPKON oder $TYPABS gefunden wurde, prüfe, ob danach noch weitere Zeichen folgen
                            if (foundType) {
                                char *nextWord22 = strtok(NULL, " \t"); // Versuche, ein weiteres Wort zu holen
                                if (nextWord22 != NULL) {
                                    logMacroError("Ungültige Zeichen nach %s %s%s", SP1, nextWord22,"");
                                } else {
                                    // Typpruefung ($TYPADR, $TYPKON, $TYPABS) des beim Aufruf uebergebenen Wertes
                                    int parameterNummer = SP1[3] - '0';
                                    if (parameterNummer >= 1 && parameterNummer <= AsmParamCount) {
                                        char typMeldung[256];
                                        if (pruefeMakroTyp(nextWord, AsmParamArray[parameterNummer - 1], typMeldung, sizeof(typMeldung)) != 0) {
                                            char paramBez[16];
                                            snprintf(paramBez, sizeof(paramBez), "$%d", parameterNummer);
                                            logMacroError("Parameter %s: %s", paramBez, typMeldung, "");
                                        }
                                    }
                                }
                            } else if (isdigit((unsigned char)SP1[3]) && nextWord[0] != '$') {   // $...-Eintrag (z. B. $ADRESSE) = Typangabe, keine Wertliste
                                // Wertliste (Doku 4): Der beim Aufruf uebergebene Parameter $x darf nur
                                // einen der in der Liste $PRx genannten Werte annehmen.
                                int parameterNummer = SP1[3] - '0';
                                if (parameterNummer >= 1 && parameterNummer <= AsmParamCount) {
                                    char listeKopie[256];
                                    strncpy(listeKopie, pruefliste, sizeof(listeKopie) - 1);
                                    listeKopie[sizeof(listeKopie) - 1] = '\0';
                                    char *kommentar = strchr(listeKopie, ';');   // ; leitet einen Kommentar ein
                                    if (kommentar) *kommentar = '\0';
                                    int inListe = 0;
                                    char *lsave;
                                    for (char *w = strtok_r(listeKopie, " \t", &lsave); w != NULL; w = strtok_r(NULL, " \t", &lsave)) {
                                        if (strcmp(w, AsmParamArray[parameterNummer - 1]) == 0) { inListe = 1; break; }
                                    }
                                    if (!inListe) {
                                        char paramBez[16];
                                        snprintf(paramBez, sizeof(paramBez), "$%d", parameterNummer);
                                        logMacroError("Parameter %s: Wert \"%s\" steht nicht in der Pruefliste", paramBez, AsmParamArray[parameterNummer - 1], "");
                                    }
                                }
                            }
                        }
                    }
                }

                if ( (strcmp(SP1, "$IF") == 0) || (strncmp(SP1, "$EL", 3) == 0) ) {
                   insideIfBlock = 1;
                   ifCount++;
                }

                char *commentStart = strchr(SP1, ';'); // Suche das erste Semikolon
                if (commentStart != NULL) {
                    *commentStart = '\0'; // Setze Null-Terminierung direkt nach `$ENDIF`
                }

                // Prüfe auf $ENDIF (jetzt ohne Kommentar)
                if ( (strcmp(SP1, "$ELIF") == 0) || (strncmp(SP1, "$ELIF", 5) == 0) ) {
                //if (strcmp(SP1, "$ENDIF") == 0) {
                    if (ifCount == 0) {
                        logMacroError("$ENDIF ohne vorheriges $IF: %s %s%s", SP1,"","");
                    } else {
                        ifCount--;
                        if (ifCount == 0) {
                            insideIfBlock = 0;
                        }
                    }
                }

            }

            // Falls nach der Schleife noch offene $IF-Blöcke existieren, Fehler ausgeben
            if (ifCount > 0) {
                logMacroError("Fehlendes $ENDIF für ein $IF %s%s%s", "", "", "");
            }

            // prüfe Verwendung von $1..$9 auf < parameteranzahl (über alle Zeilen dieses Makros)
            for (int jj = 0; jj < macros[i].macroLineCount; jj++) {
                SET_SP_VALUES(i, jj);
                trimWhitespace(SP1);
                trimWhitespace(SP2);
                trimWhitespace(SP3);

                char *tokens[] = {SP1, SP2, SP3};
                for (int t = 0; t < 3; t++) {
                    if (tokens[t][0] == '$' && isdigit(tokens[t][1])) {  // Prüfe ob $1, $2, ..., $9
                        int paramNum = tokens[t][1] - '0';  // Extrahiere die Ziffer
                        if (paramNum > macros[i].macroParameterAnzahl) {
                            char maxParamStr[10];  // Puffer für die Zeichenkette
                            snprintf(maxParamStr, sizeof(maxParamStr), "%d", macros[i].macroParameterAnzahl);

                            logMacroError("Ungültiger Makro-Parameter: %s (Max. erlaubt: $%s)%s", tokens[t], maxParamStr,"");
                        }
                    }
                }
            }


            //Übernahme in die Ausgabe
            for (int j = 0; j < macros[i].macroLineCount; j++) {

                if (macros[i].macroParsedLines[j].sp1[0] == '#' || macros[i].macroParsedLines[j].sp1[0] == '&' || 
                    ( strlen(macros[i].macroParsedLines[j].sp1) == 0 && strlen(macros[i].macroParsedLines[j].sp2) == 0 && 
                      strlen(macros[i].macroParsedLines[j].sp3) == 0 && strlen(macros[i].macroParsedLines[j].sp4) == 0)) 
                {
                    continue;
                }

                if (strcmp(zuPruefenderMacro, macros[i].macroParsedLines[j].sp2) == 0) {
                    is_error0 = 1;
                    PRINT_FEHLER("Rekursiver Macro-Aufruf von: %s\n", zuPruefenderMacro);
                    exit(RC_FEHLER);
                }

                if (found) {
                    // Setzt ALLE Zeilen der MacroDefinition Zeile für Zeile in die Rückgabe, erweitert RESULT damit automatisch zu einem Array
                    REALLOC_RESULT;  
                    result[*lineCount] = macros[i].macroParsedLines[j]; 

                    (*lineCount)++;
                }
            }


            #undef SET_SP_VALUES


            // Bearbeitet alle Zeilen der Ausgabe im Array RESULT , formale Parameter im ganzen Macro ersetzen 
            for (int j = 0; j < *lineCount; j++) {

                if (result[j].sp1[0] == '#' || 
                    (result[j].sp1[0] == '$' && strncmp(result[j].sp1, "$IF", 3) != 0 && 
                                            strncmp(result[j].sp1, "$ELIF", 5) != 0 && 
                                            strncmp(result[j].sp1, "$ENDIF", 6) != 0) || 
                    result[j].sp1[0] == '&' || 
                    (strlen(result[j].sp1) == 0 && strlen(result[j].sp2) == 0 &&
                    strlen(result[j].sp3) == 0 && strlen(result[j].sp4) == 0))
                {
                    continue;
                } else { 
                    char *fields[] = { result[j].sp1, result[j].sp2, result[j].sp3, result[j].sp4 };

                    for (int f = 0; f < 4; f++) { // Durch sp1 - sp4 iterieren
                        size_t originalLen = strlen(fields[f]);
                        char *newField = malloc(originalLen + 512); // Speicher für ursprüngliche Länge
                        strcpy(newField, fields[f]);

                        for (int p = 0; p < AsmParamCount; p++) { // `$1` entspricht Index `0`, `$2` → `1` usw.
                            char search[16];
                            snprintf(search, sizeof(search), "$%d", p + 1); // `$N` → `AsmParamArray[N-1]`

                            char *pos;
                            while ((pos = strstr(newField, search)) != NULL) { // Wiederholt ersetzen
                                size_t newSize = strlen(newField) - strlen(search) + strlen(AsmParamArray[p]) + 1;
                                char *updatedField = malloc(newSize + 100); // Hier **+1**, um sicherzugehen

                                // Kopiere alles bis zum gefundenen `$N`
                                strncpy(updatedField, newField, pos - newField);
                                updatedField[pos - newField] = '\0';

                                // Füge den Ersatzwert ein
                                strcat(updatedField, AsmParamArray[p]);

                                // Füge den restlichen String nach `$N` an
                                strcat(updatedField, pos + strlen(search) );

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

            tmp_result = (lineElements *)malloc(*lineCount * sizeof(lineElements));
            if (!tmp_result) {
                fprintf(stderr, "Speicherzuweisung tmp_result fehlgeschlagen!\n");
                free(result);
                exit(RC_FEHLER);
            }

            memcpy(tmp_result, result, *lineCount *sizeof(lineElements));
            memset(result, 0, *lineCount * sizeof(lineElements)); // Setzt alle Bytes auf 0

            int kk=0;
            char firstWord[10];  // Speicher für das erste Wort
            for (int j = 0; j < *lineCount; j++) {
                if ( imIf == 2 ) { imIf = 0; }
                rc = macroIfAufloesen( &tmp_result[j], &imIf, &inBedingung);
                if (rc < 0) {
                    grc=-1;
                    is_error0 = 1;
                    REALLOC_RESULT;
                    (*lineCount)++;
                    kk++;
                    if (rc == -1) {
                       logMacroError("$IF darf nicht geschachtelt werden.", aktuellerOpCode,"","");
                    } else if (rc == -2) {
                       logMacroError("$IF benötigt 3, 7, 11 oder 15 Parameter der Struktur a b c [|&] d e f [|&] g h i [|&] j k l.", aktuellerOpCode,"","");
                    } else if (rc == -3) {
                       logMacroError("Der 4. Parameter muss | oder & sein.", aktuellerOpCode,"","");
                    } else if (rc == -4) {
                       logMacroError("Der 8. Parameter muss | oder & sein.", aktuellerOpCode,"","");
                    } else if (rc == -5) {
                       logMacroError("Der 12. Parameter muss | oder & sein.", aktuellerOpCode,"","");
                    } else {
                       logMacroError("Macro: Unspezifischer Fehler.", aktuellerOpCode,"","");
                    }
                   //break;
                }

                if ( grc == 0 && fehlertab_count == 0) { 
                    if ( imIf == 1 ) {  // in $IF
                        if (inBedingung > 0 ) {
                            if (sscanf(tmp_result[j].sp1, "%9s", firstWord) == 1) {  // Extrahiere das erste Wort
                                if (strcmp(firstWord, "$IF") != 0 && strcmp(firstWord, "$ELIF") != 0) {
                                    strcpy(result[kk].sp1, tmp_result[j].sp1);
                                    strcpy(result[kk].sp2, tmp_result[j].sp2);
                                    strcpy(result[kk].sp3, tmp_result[j].sp3);
                                    strcpy(result[kk].sp4, tmp_result[j].sp4);
                                    kk++;
                                }
                            } else {
                                //sp1 ist leer
                                strcpy(result[kk].sp1, tmp_result[j].sp1);
                                strcpy(result[kk].sp2, tmp_result[j].sp2);
                                strcpy(result[kk].sp3, tmp_result[j].sp3);
                                strcpy(result[kk].sp4, tmp_result[j].sp4);
                                kk++;
                            }
                        }
                    } else {
                        if (sscanf(tmp_result[j].sp1, " %9s", firstWord) != 1 || firstWord[0] != '$') {
                            strcpy(result[kk].sp1, tmp_result[j].sp1);
                            strcpy(result[kk].sp2, tmp_result[j].sp2);
                            strcpy(result[kk].sp3, tmp_result[j].sp3);
                            strcpy(result[kk].sp4, tmp_result[j].sp4);
                            if (strcmp(tmp_result[j].sp2, "macroende") == 0 || 
                                strcmp(tmp_result[j].sp2, "MACROENDE") == 0 || 
                                strcmp(tmp_result[j].sp2, "MEND") == 0) {

                                strcpy(result[kk].sp1, ";+++");
                                strcpy(result[kk].sp2, "MEND");
                                strcpy(result[j].sp1, ";+++");
                                strcpy(result[j].sp2, "MEND");
                            }
                            kk++;
                        }
                    }
                } else {
                    strcpy(result[kk].sp1, tmp_result[j].sp1);
                    strcpy(result[kk].sp2, tmp_result[j].sp2);
                    strcpy(result[kk].sp3, tmp_result[j].sp3);
                    strcpy(result[kk].sp4, tmp_result[j].sp4);
                    kk++;
                }
            }


            (*lineCount)=kk;

            for (int i = 0; i < fehlertab_count; i++) {
                is_error0 = 1;

                // Speicher sicher erweitern
                lineElements *ttemp = (lineElements *)realloc(result, (*lineCount + 1) * sizeof(lineElements));
                if (!ttemp) {
                    fprintf(stderr, "Speicherfehler bei Realloc!\n");
                    exit(RC_FEHLER);
                }
                result = ttemp; 

                if (fehlertab_count >= 64) {
                    PRINT_FEHLER("%s","Zu viele Fehler im Macro."); 
                    is_error0 = 1;
                    break; 
                }

                strcpy(result[*lineCount].sp1 , fehlertab[i]);  
                (*lineCount)++;
            }


            char tempLine[256] = "";
            int ober_i = 0;

            for (int i = 0; i < *lineCount && (result[i].sp1[0] != '\0' || result[i].sp2[0] != '\0' || result[i].sp3[0] != '\0'); i++) {   // Obergrenze: kein Lesen hinter dem Array
                if (result[i].sp2[0] != '\0' && strstr(result[i].sp2, "!$wdhl_adr_e") != NULL) { 
                    strcpy(tempLine, result[i].sp2);
                    strcat(tempLine, " ");
                    strcat(tempLine, result[i].sp3);
                    ober_i = i;
                    break;
                }
                if (result[i].sp2[0] != '\0' && strstr(result[i].sp2, "!$wdhl") != NULL) { 
                    strcpy(tempLine, result[i].sp2);
                    ober_i = i;
                    break;
                }
            }

            if ((strstr(tempLine, "$PR") == NULL) ) {
                if (strstr(tempLine, "!$wdhl_adr_e") != NULL) {
                    verarbeiteZeile_wdhl_adr_e(tempLine);
                    int muell=ober_i;
                    processLine(tempLine, result, &muell);  

                } else if (strcmp(tempLine, "!$wdhl") == 0) {
                    int rc = verarbeiteZeile_wdhl(tempLine, AsmParamArray[0], AsmParamArray[1], AsmParamArray[2], AsmParamArray[3], AsmParamArray[4]);
                    if (rc == 0) {
                        int muell=ober_i;
                        processLine(tempLine, result, &muell);  
                    }
                }
            }

            // Label des Makroaufrufs: Hat die erste erzeugte Anweisung kein eigenes Label, entfaellt die
            // equ-Zeile und die erste Anweisung erhaelt das Label des Aufrufs. (Nicht bei equ/abs/start/end,
            // dort wuerde das Label sonst einen anderen Wert als die Adresse bekommen.)
            if (equIndex >= 0) {
                int erste = -1;
                for (int q = equIndex + 1; q < *lineCount; q++) {
                    if (result[q].sp1[0] == ';') continue;   // Kommentarzeilen ueberspringen
                    erste = q;
                    break;
                }
                if (erste >= 0 && result[erste].sp1[0] == '\0' && result[erste].sp2[0] != '\0' &&
                    strncmp(result[erste].sp2, "equ", 3) != 0 &&
                    strcmp(result[erste].sp2, "abs") != 0 &&
                    strcmp(result[erste].sp2, "start") != 0 &&
                    strcmp(result[erste].sp2, "end") != 0) {
                    strcpy(result[erste].sp1, label);
                    for (int q = equIndex; q < *lineCount - 1; q++) {
                        result[q] = result[q + 1];
                    }
                    (*lineCount)--;
                }
            }
            return result;
        }
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
    int lineCounter = 0;
    char message[256];

    char *uuid = generate_uuid(seed_value);
    
    void modify_text(char *text, const char *uuid) {
        char temp[256];  
        char *pos = strchr(text, '%');  // Suche nach '%'

        if (pos) {
            size_t prefix_len = pos - text;  // Länge des Textes vor '%'
            snprintf(temp, sizeof(temp), "%.*s%s%s", (int)prefix_len, text, uuid, pos + 1);
            strcpy(text, temp); 
        }
    }

    void modify_text2(char *erg, const char *label_mit, const char *label_ohne, const char *uuid) {
        char temp[256]; 
        char *pos = strstr(erg, label_mit);  // Suche nach label_mit

        if (pos) {
            size_t prefix_len = pos - erg;  // Länge des Textes vor label_mit
            snprintf(temp, sizeof(temp), "%.*s%s%s%s", (int)prefix_len, erg, label_ohne, uuid, pos + strlen(label_mit));
            strcpy(erg, temp);  
        }
    }

    void replace_label(char *target, const char *old_label, const char *new_label) {
        char temp[256]; 
        char *pos = strstr(target, old_label); // Suche nach old_label

        if (pos) {
            // Kopiere den Teil vor old_label in temp
            size_t prefix_len = pos - target;
            snprintf(temp, sizeof(temp), "%.*s%s%s", (int)prefix_len, target, new_label, pos + strlen(old_label));
            strcpy(target, temp); 
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
            strcpy(labelTable[labelCount].label, zeile->sp1);
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
                strcpy(label_ohne,labelTable[k].label);
                label_ohne[strlen(label_ohne) - 2] = '\0';
                strcpy(label_mit,labelTable[k].label);
                label_mit[strlen(label_mit) - 1] = '\0';
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
    strcpy(macros[macroIndex].macroName, name);
    strcpy(macros[macroIndex].macro, "MACRO");
    macros[macroIndex].macroLineCount = 0;
    macros[macroIndex].ausQuelltext = ausQuelltext;

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
                strcpy(macros[macroIndex].macroParameters[paramCount], token);
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

    while (fgets(lineBuffer, sizeof(lineBuffer), macroFile)) {
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
                    if (strstr(lineBuffer, "macroende") || strstr(lineBuffer, "MACROENDE") || strstr(lineBuffer, "MEND")) {
                        break;
                    }
                }
                continue;
            }

            // Falls kein Duplikat gefunden wurde, speichere das neue Makro
            macroIndex = macroAnlegen(name, params, MACRODEFINITIONEN, 0, -1);
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
static int sammleQuelltextMakros(void) {
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


void printFormattedAsmListing(lineElements lineAsmAufgeloest[], int lineCountAsmAufgeloest) {
    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;


    // Berechnung der maximalen Spaltenbreite für sp1, sp2, sp3
    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        char *trimmed = lineAsmAufgeloest[i].sp1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Entfernt Leerzeichen & Tabs

        // **Überspringe Kommentarzeilen**
        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&' || *trimmed == '\0') {
            continue; // Springt zur nächsten Zeile
        }

        // Berechnung der maximalen Breite
        int len1 = strlen(trimmed);
        if (len1 > maxWidth1) maxWidth1 = len1;

        int len2 = strlen(lineAsmAufgeloest[i].sp2);
        int len3 = strlen(lineAsmAufgeloest[i].sp3);

        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    if (maxWidth1 < 16) maxWidth1 = 16;
    if (maxWidth2 < 10) maxWidth2 = 10;
    if (maxWidth3 < 20) maxWidth3 = 20;

    char formatString[256];
    snprintf(formatString, sizeof(formatString), "%%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        char *trimmed = lineAsmAufgeloest[i].sp1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&' ) {
            // Direkte Ausgabe ohne feste Spaltenbreite
            printf("%s %s %s %s\n",
                lineAsmAufgeloest[i].sp1,
                lineAsmAufgeloest[i].sp2,
                lineAsmAufgeloest[i].sp3,
                lineAsmAufgeloest[i].sp4);
        } else {
            // Formatierte Ausgabe mit dynamischer Spaltenbreite
            printf(formatString,
                lineAsmAufgeloest[i].sp1,
                lineAsmAufgeloest[i].sp2,
                lineAsmAufgeloest[i].sp3,
                lineAsmAufgeloest[i].sp4);
        }
    }
}


// Entfernt ANSI-Farbcodes (ESC [ <Ziffern und ;> m) aus text (in place).
static void entferneFarbcodes(char *text) {
    char *r = text, *w = text;
    while (*r) {
        if (*r == '\033' && r[1] == '[') {
            const char *q = r + 2;
            while ((*q >= '0' && *q <= '9') || *q == ';') q++;
            if (*q == 'm') { r = (char *)q + 1; continue; }
        }
        *w++ = *r++;
    }
    *w = '\0';
}

// Ersetzt in der Adress-/Kennzeichenspalte des Listings (sp0, z. B. "0007: 01 2006 241" oder "      01 2006 241")
// das Kennzeichen 01 durch den Wert des Pragmas LEITADRESSE (Standard 01 = keine Aenderung).
// Die Ersetzung erfolgt an Ort und Stelle (zwei Zeichen durch zwei Zeichen), die Spaltenbreite bleibt gleich.
static void ersetzeKennzeichen01(char *sp0) {
    if (leitadresseKennzeichen == 1) return;
    char *p = sp0;
    while (*p == ' ') p++;
    char *q = p;
    while (*q >= '0' && *q <= '7') q++;
    if (q > p && *q == ':') {          // Adressspalte "<oktalzahl>:" ueberspringen
        p = q + 1;
        while (*p == ' ') p++;
    }
    if (p[0] == '0' && p[1] == '1' && (p[2] == ' ' || p[2] == '\0')) {
        p[0] = (char)('0' + leitadresseKennzeichen / 10);
        p[1] = (char)('0' + leitadresseKennzeichen % 10);
    }
}

// Schreibt das formatierte Listing nach f. Mit ohneFarben = 1 (Datei .dmp) werden die ANSI-Farbcodes
// vorher aus den Feldern entfernt und die Spaltenbreiten aus dem Text ohne Farbcodes berechnet;
// frueher standen in der .dmp bei Fehlerlaeufen Escape-Sequenzen (z. B. um die Marke EE).
static void schreibeListingX(FILE *f, int ohneFarben, lineElementsX lineAsmAufgeloest[], int lineCountAsmAufgeloest) {
    char b0[sizeof(lineAsmAufgeloest[0].sp0)];
    char b1[sizeof(lineAsmAufgeloest[0].sp1)];
    char b2[sizeof(lineAsmAufgeloest[0].sp2)];
    char b3[sizeof(lineAsmAufgeloest[0].sp3)];
    char b4[sizeof(lineAsmAufgeloest[0].sp4)];
    const char *s0, *s1, *s2, *s3, *s4;

#define HOLE_FELDER(idx) \
    do { \
        s0 = lineAsmAufgeloest[idx].sp0; s1 = lineAsmAufgeloest[idx].sp1; s2 = lineAsmAufgeloest[idx].sp2; \
        s3 = lineAsmAufgeloest[idx].sp3; s4 = lineAsmAufgeloest[idx].sp4; \
        if (ohneFarben) { \
            snprintf(b0, sizeof(b0), "%s", s0); entferneFarbcodes(b0); s0 = b0; \
            snprintf(b1, sizeof(b1), "%s", s1); entferneFarbcodes(b1); s1 = b1; \
            snprintf(b2, sizeof(b2), "%s", s2); entferneFarbcodes(b2); s2 = b2; \
            snprintf(b3, sizeof(b3), "%s", s3); entferneFarbcodes(b3); s3 = b3; \
            snprintf(b4, sizeof(b4), "%s", s4); entferneFarbcodes(b4); s4 = b4; \
        } \
        if (leitadresseKennzeichen != 1) { \
            if (s0 != b0) snprintf(b0, sizeof(b0), "%s", s0); \
            ersetzeKennzeichen01(b0); s0 = b0; \
        } \
    } while (0)

    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;

    // **1. Schritt: Maximale Breiten für sp1, sp2, sp3 berechnen**
    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        HOLE_FELDER(i);
        // Prüfen, ob sp1 ignoriert werden soll
        const char *trimmed = s1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed != ';' && *trimmed != '#' && *trimmed != '$'  && *trimmed != '*' && *trimmed != '&') { // Zeilen mit `$` ausschließen
            int len1 = strlen(s1);
            if (len1 > maxWidth1) maxWidth1 = len1;
        }

        int len2 = strlen(s2);
        int len3 = strlen(s3);

        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    char formatString[256];
    snprintf(formatString, sizeof(formatString), "%%-20s %%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        HOLE_FELDER(i);
        const char *trimmed = s1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&') {
            // Direkte Ausgabe ohne feste Spaltenbreite
            fprintf(f, "%-20s %s %s %s %s\n", s0, s1, s2, s3, s4);
        } else {
            // Formatierte Ausgabe mit dynamischer Spaltenbreite
            fprintf(f, formatString, s0, s1, s2, s3, s4);
        }
    }
#undef HOLE_FELDER
}

void printFormattedAsmListingX(lineElementsX lineAsmAufgeloest[], int lineCountAsmAufgeloest, FILE *dmpFile) {
    schreibeListingX(stdout, 0, lineAsmAufgeloest, lineCountAsmAufgeloest);       // Bildschirm: mit Farben
    if (dmpFile) {
        schreibeListingX(dmpFile, 1, lineAsmAufgeloest, lineCountAsmAufgeloest);  // .dmp: ohne Farbcodes
    }
}

// ---------------------------------------------------


void pass0() {
    printf("Verarbeite 'c82ass.makros', Erzeuge Macroersetzungen\n\n");
    is_error0 = 0;

    erzeugeMacroArray("c82ass.makros");

    int in_macro = 0;
    int quelltext_errors = sammleQuelltextMakros();   // Makrodefinitionen im Quelltext
    int macro_errors = quelltext_errors;
    char old_mname[256]="";

    for (int i = 0; i < macroCount; i++) {
        for (int j = 0; j < macros[i].macroLineCount; j++) {
            // Prüfe, ob eine neue MACRO-Deklaration beginnt
            if (  (strcmp(old_mname,"" ) == 0 ) || strcmp(macros[i].macroName,old_mname ) != 0 ) { 
                strcpy(old_mname, macros[i].macroName);
                // Falls ein vorheriges MACRO nicht geschlossen wurde, FEHLER MELDEN!
                if (in_macro) {
                    PRINT_FEHLER("%s", "MACRO ohne MEND oder MACROENDE.");
                    macro_errors++;
                }

                // Prüfe, ob das MACRO in `.sp1` einen Namen hat
                if (strlen(macros[i].macroName) == 0) {
                    PRINT_FEHLER("%s", "MACRO ohne Namen.");
                    macro_errors++;
                }

                in_macro = 1; // Ein neues Makro wurde geöffnet
            } 

            // Prüfe auf gültiges Makro-Ende
            if (in_macro && 
                (strcmp(macros[i].macroParsedLines[j].sp2, "MEND") == 0 ||
                strcmp(macros[i].macroParsedLines[j].sp2, "MACROENDE") == 0 ||
                strcmp(macros[i].macroParsedLines[j].sp2, "macroende") == 0)) {
                in_macro = 0; // Makro korrekt geschlossen
            }

        }

        // Falls das letzte Makro nicht geschlossen wurde, FEHLER MELDEN!
        if (in_macro) {
            PRINT_FEHLER("Fehlerndes MEND in MACRO %s .",old_mname);
            macro_errors++;
            in_macro = 0; 
        }
    }

    // Fehler-Ausgabe
    if (macro_errors > 0) {
        is_error = 1;
        PRINT_FEHLER("%d fehlerhafte Makrodefinition(en) (Makrodatei oder Quelltext).\n", macro_errors);
        if (macro_errors > quelltext_errors) {
            printAllMacros();    // Auflistung nur, wenn die Makrodatei Fehler enthält (wie bisher)
        }
        exit(RC_FEHLER);
    }


/*
    // ist jetzt global
    // lineAsmAufgeloest und wird dynamisch vergrößert
    // Füllstand ist in lineCountAsmAufgeloest, ebenfalls global
    lineElements lineAsmAufgeloest[PROGRAMMZEILEN];
    int lineCountAsmAufgeloest = 0; 
    resetParsedLinesArrays(lineAsmAufgeloest, lineCountAsmAufgeloest);
*/

    int wdhlg = 1;
    while ( wdhlg > 0 )
    {
        // Schleife durch alle Zeilen der .asm Datei, um die Macros zu finden und zu prüfen
        for (int asmZeilenNr = 0; asmZeilenNr < lineCountAsm; asmZeilenNr++) {
            
            if ( beginntMitSemikolon(linesAsm[asmZeilenNr].sp1) == 1 ) {
                lineAsmAufgeloest[lineCountAsmAufgeloest++] = linesAsm[asmZeilenNr];
                continue;
            }
            if (linesAsm[asmZeilenNr].sp1[0] == '\0' && linesAsm[asmZeilenNr].sp2[0] == '\0' &&
                linesAsm[asmZeilenNr].sp3[0] == '\0' && linesAsm[asmZeilenNr].sp4[0] == '\0') 
            {
                strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest++].sp1 , "");
                continue;
            }

            char operationscode[128] = "";
            char aktuelleParameterZeile[1024] = "";
            char label[256];

            strcpy(label,linesAsm[asmZeilenNr].sp1);
            strcpy(aktuelleParameterZeile, linesAsm[asmZeilenNr].sp3);
            strcpy(operationscode,linesAsm[asmZeilenNr].sp2);

            int lineCount=0;
            lineElements *ergebnis = loeseMacroAuf(macros, &macroCount, operationscode, aktuelleParameterZeile, &lineCount, label );

            if (ergebnis != NULL) {

                seed_value++;  //Anzahl der aufgelösten Macros
                if ( seed_value > seed_max ) {
                    PRINT_FEHLER("Mehr als %i Macros können nicht verarbeitet werden.",seed_value);
                    exit(RC_FEHLER);
                }
                // Statt Macroaufruf den aufgelösten Macro übernehmen
                char macroAufrufLine[1024];
                sprintf(macroAufrufLine, "%-20s %-20s %-20s %-20s", linesAsm[asmZeilenNr].sp1, 
                                linesAsm[asmZeilenNr].sp2, linesAsm[asmZeilenNr].sp3, linesAsm[asmZeilenNr].sp4);

                strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, ";+++ ");
                strcat(lineAsmAufgeloest[lineCountAsmAufgeloest++].sp1, macroAufrufLine);

                // ergebnis enthält den aufgelösten macro mit lineCount Zeilen
                macroSprung1Aufloesen(&ergebnis, &lineCount, operationscode);


                for (int i = 0; i < lineCount; i++) {
                    //lineAsmAufgeloest[lineCountAsmAufgeloest++] = ergebnis[i];
                    memcpy(&lineAsmAufgeloest[lineCountAsmAufgeloest], &ergebnis[i], sizeof(lineElements));
                    lineCountAsmAufgeloest++;
                }

            } else {
                // Assemblerzeile direkt übernehmen
                lineAsmAufgeloest[lineCountAsmAufgeloest++] = linesAsm[asmZeilenNr];
            }

            free(ergebnis); 
            ergebnis = NULL;
        }

    // --------------------

        int is_treffer = 0; 
        
        if (lineCountAsmAufgeloest > 0) {
            for (int j = 0; j < lineCountAsmAufgeloest; j++) {  
                char trimmedSp2[MACRO_PARAMETER_LAENGE];
                strncpy(trimmedSp2, lineAsmAufgeloest[j].sp1, MACRO_PARAMETER_LAENGE);
                if (  ((trimmedSp2[0] == ';') || (trimmedSp2[0] == '#') || (trimmedSp2[0] == '$')  || (trimmedSp2[0] == '&') || (strstr(trimmedSp2, "***") != NULL) ) ) {
                    continue;
                }
                strncpy(trimmedSp2, lineAsmAufgeloest[j].sp2, MACRO_PARAMETER_LAENGE);
                trimWhitespace(trimmedSp2);  // Entferne unnötige Leerzeichen

                // Falls `trimmedSp2` leer ist oder mit einer Ziffer beginnt, überspringe die innere Schleife
                if (strlen(trimmedSp2) == 0 || isdigit(trimmedSp2[0])) {
                    continue;
                }

                for (int i = 0; i < macroCount; i++) {  
                    // Bereinige `macroName`, falls es mit `:` endet
                    char macroNameCleaned[MACRO_PARAMETER_LAENGE];
                    strncpy(macroNameCleaned, macros[i].macroName, MACRO_PARAMETER_LAENGE);

                    size_t len = strlen(macroNameCleaned);
                    if (len > 0 && macroNameCleaned[len - 1] == ':') {
                        macroNameCleaned[len - 1] = '\0';
                    }

                    if (strcmp(trimmedSp2, macroNameCleaned) == 0) { 
                        is_treffer = 1;  
                        break;  
                    }  
                }

                if (is_treffer == 1) {  
                    break;  
                }
            }
        }

        // **Hier wdhlg nur zurücksetzen, wenn kein Treffer gefunden wurde**
        if (is_treffer == 0) {
            wdhlg = 0;  // Schleife beenden
        } else {
            memcpy(linesAsm, lineAsmAufgeloest, sizeof(lineElements) * PROGRAMMZEILEN);
            lineCountAsm = lineCountAsmAufgeloest;
            lineCountAsmAufgeloest = 0; 
        }

    }

//mkl
//is_error0 = 1;
    if ( is_error0 != 0) {
       printFormattedAsmListing(lineAsmAufgeloest, lineCountAsmAufgeloest);
       PFend();
       PRINT_WARNUNG("%s","Compilierung endete mit FEHLERn.\n");
       exit(RC_FEHLER);
    }
}

// ----------------------------------------------------

int macroIfAufloesen(lineElements *ergebnis, int *imIf, int * inBedingung) {
 
    char tempLine[256];


    if (strncmp(ergebnis->sp1, "$", 1) == 0) {
        // Macro $IF - Anweisung $ELIF $ENDIF
        if ( *imIf == 2 ) { *imIf = 0; } 
        if ( *imIf == 1 && ( strstr(ergebnis->sp1, "$IF") ) ) {
            return -1; // PRINT_FEHLER("MACRO: $IF darf nicht geschachtelt werden: %s",tempLine);
        }

        // $IF ...

        strcpy(tempLine, ergebnis->sp1);


        char firstWord[10];  // Speicher für das erste Wort
        if (sscanf(tempLine, "%9s", firstWord) == 1) {  // Extrahiere das erste Wort
            if (strcmp(firstWord, "$IF") == 0 || strcmp(firstWord, "$ELIF") == 0) {

                *imIf = 1;
                // Rest der Zeile extrahieren und prüfen, ob sie 3, 7, 11 oder 15 Parameter enthält
                char a[128] = "", b[128] = "", c[128] = "", op[2] = "", d[128] = "", e[128] = "", f[128] = "";
                char op3[2] = "", g[128] = "", h[128] = "", i[128] = "", op4[2] = "", j[128] = "", k[128] = "", l[128] = "";
                int count = sscanf(tempLine, "%*s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s",
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

int isKeywordMatch(const char *token) {
    static const char *keywords[] = {
        "start", "equ", "abs", "end", "dw", "da", "dt",
        "dto", "dtm", "dz", "dbn", "db", "equ10", "equ40", "equ100"
    };
    if (!token) return 1;  // Falls token NULL ist, nicht zutreffend

    // Schrittweise Prüfung der Schlüsselwörter
    int keyword_count = 15;
    for (size_t i = 0; i < keyword_count; i++) {
        if (strcmp(token, keywords[i]) == 0) {
            return 0;  // Treffer
        }
    }
    return 1;  // Kein Treffer
}

int isValidSp3_keinLiteralEnthalten(const char *sp3) {
    if (!sp3 || sp3[0] == '\0') return 1; // Leer? Dann gültig

    const char *hashPos = strchr(sp3, '#'); // Sucht das erste `#`
    
    if (!hashPos) return 1; // Falls kein `#` existiert, ist es gültig

    // Prüft, ob vor `#` ein `;` oder `\` steht
    const char *ptr;
    for (ptr = sp3; ptr < hashPos; ptr++) {
        if (*ptr == ';' || *ptr == '\\') return 0; // Ungültig, wenn `#` danach kommt
    }

    return 1; // Falls kein `#` vor `;` oder `\` steht, ist es gültig
}


// Erzeugen der Literal-Definitionen am Programmende
void processLiteralEntry(lineElements lineAsmAufgeloestTemp[], int *lineCountAsmAufgeloestTemp, Literal literalTable[], int i) {
    char type[3]; // Platz für "dw" oder "da"

    if (literalTable[i].literalValue[0] == '#') {
        memmove(literalTable[i].literalValue, literalTable[i].literalValue + 1, strlen(literalTable[i].literalValue));
        strcpy(type, "dw");
    } else if (literalTable[i].literalValue[0] == '@') {
        memmove(literalTable[i].literalValue, literalTable[i].literalValue + 1, strlen(literalTable[i].literalValue));
        strcpy(type, "da");
    } else {
        strcpy(type, "dw");
    }

    strcpy(lineAsmAufgeloestTemp[*lineCountAsmAufgeloestTemp].sp1, literalTable[i].literalName);
    strcpy(lineAsmAufgeloestTemp[*lineCountAsmAufgeloestTemp].sp2, type);
    strcpy(lineAsmAufgeloestTemp[*lineCountAsmAufgeloestTemp].sp3, literalTable[i].literalValue);
    strcpy(lineAsmAufgeloestTemp[*lineCountAsmAufgeloestTemp].sp4, "");
    (*lineCountAsmAufgeloestTemp)++;
}


// ----------------------------------------------------

// Prueft den Operanden von db/dbn gemaess Doku (<zahl> ::= <oktalzahl> | <dezimalzahl>):
//   oktalzahl   = fuehrende 0, nur Ziffern 0-7 ("0" allein ist zulaessig)
//   dezimalzahl = [+|-] Ziffer 1-9, danach Ziffern 0-9
// Alles andere (abc, 5x, 3+1, 09, #5, leer) ist ein Fehler; frueher wurde es stillschweigend als
// 0 oder als der gueltige Zahlenanfang gelesen und verschob alle folgenden Adressen.
// Rueckgabe 1 = gueltig (Anzahl in *wert), 0 = ungueltig (Text in meldung).
static int pruefeDbOperand(const char *operation, const char *operand, long *wert, char *meldung, size_t groesse) {
    const char *p = (operand != NULL) ? operand : "";
    if (*p == '\0') {
        snprintf(meldung, groesse, "%s: Operand fehlt (erwartet wird eine Zahl).", operation);
        return 0;
    }
    int oktal = (p[0] == '0');
    const char *q = p;
    if (!oktal && (*q == '+' || *q == '-')) q++;
    int gueltig = (*q != '\0');
    if (oktal) {
        for (; *q; q++) if (*q < '0' || *q > '7') { gueltig = 0; break; }
    } else {
        if (*q < '1' || *q > '9') gueltig = 0;
        for (; gueltig && *q; q++) if (*q < '0' || *q > '9') gueltig = 0;
    }
    if (!gueltig) {
        snprintf(meldung, groesse,
                 "%s: Operand \"%s\" ist keine gültige Zahl (Oktalzahl mit führender 0 oder Dezimalzahl).",
                 operation, operand);
        return 0;
    }
    errno = 0;
    long v = strtol(p, NULL, oktal ? 8 : 10);
    if (v < 0) {
        snprintf(meldung, groesse, "%s: Operand \"%s\" darf nicht negativ sein.", operation, operand);
        return 0;
    }
    if (errno == ERANGE || v > 010000) {
        snprintf(meldung, groesse, "%s: Operand \"%s\" ist zu groß (die Trommel hat nur 010000 Speicherplätze).",
                 operation, operand);
        return 0;
    }
    *wert = v;
    return 1;
}

// Baut aus den Zeilenelementen den Text der Quellzeile fuer Fehlermeldungen (Pass 1 hat keine
// fertige Zeile; frueher erschien dort "in Zeile: ``").
static void baueMeldeZeile(char *ziel, size_t groesse, const lineElements *z) {
    ziel[0] = '\0';
    const char *teile[3] = { z->sp1, z->sp2, z->sp3 };
    for (int k = 0; k < 3; k++) {
        if (teile[k][0] == '\0') continue;
        if (ziel[0] != '\0') strncat(ziel, " ", groesse - strlen(ziel) - 1);
        strncat(ziel, teile[k], groesse - strlen(ziel) - 1);
    }
}

void pass1(char *symbolLogFile) {
    printf("Löse Literale auf \n");

     //.mac  .log
    FILE *symbolLog = fopen(symbolLogFile, "w");  // .log
    char line[MAX_LINE_LENGTH]={0};

    int end_war=0;

    // ist jetzt global
    // lineAsmAufgeloest und wird dynamisch vergrößert
    // Füllstand ist in lineCountAsmAufgeloest, ebenfalls global
    // lineElements lineAsmAufgeloestTemp[PROGRAMMZEILEN];
    // int lineCountAsmAufgeloestTemp = 0; 
 
    unsigned int relativAdresse = 0000;

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {

        // übergehen
        if (  ((lineAsmAufgeloest[i].sp1[0] == ';') || (lineAsmAufgeloest[i].sp1[0] == '#') || (lineAsmAufgeloest[i].sp1[0] == '$')  ||
                (lineAsmAufgeloest[i].sp1[0] == '&') || (strstr(lineAsmAufgeloest[i].sp1, "***") != NULL)   ) ) {
            copyAndIncrementLineElements(i);
            continue;
        }
 
        // Leerzeile
        if (lineAsmAufgeloest[i].sp1[0] == '\0' && lineAsmAufgeloest[i].sp2[0] == '\0' &&
            lineAsmAufgeloest[i].sp3[0] == '\0' && lineAsmAufgeloest[i].sp4[0] == '\0') 
        {
            copyAndIncrementLineElements(i);
            continue;
        }


        // dt/dto/dtm: Ein Operand, der mit '#' beginnt, ist KEIN Text, sondern die Schreibweise eines
        // Literals (Doku 2, <literal> ::= #<werteausdruck>). Soll ein Text mit '#' am Anfang ausgegeben
        // werden, muss er in \...\ stehen (dt \#ab\). Ein '#' innerhalb des Textes (dt a#b) bleibt Text.
        if ( istTextAnweisung(lineAsmAufgeloest[i].sp2) && lineAsmAufgeloest[i].sp3[0] == '#' ) {
            baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
            printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "beginnt mit # und ist daher kein Text; Text mit # braucht \\...\\", line);
            MELDE_FEHLER_P1("Operand %s ist kein Text (beginnt mit #); Text mit # muss in \\...\\ stehen.", lineAsmAufgeloest[i].sp3);
            is_error1 = 1;
        }

        // irgendwo ein Literal enthalten ?
        // Nicht bei dt/dto/dtm: Dort ist der Operand ein Text; ein '#' innerhalb des Textes ist ein
        // Textzeichen, ein fuehrendes '#' wird oben als Fehler gemeldet (dt # schrieb frueher "l0001"),
        // ein '@' wird von der Zeichenpruefung in Pass 3 gemeldet.
        if ( !istTextAnweisung(lineAsmAufgeloest[i].sp2) &&
             (lineAsmAufgeloest[i].sp3[0] == '#' || lineAsmAufgeloest[i].sp3[0] == '@')) {
            char oldName[256]="";
            char literalValue[256];
            char literalName[50];
            if (lineAsmAufgeloest[i].sp3[1] == '0' && strchr(lineAsmAufgeloest[i].sp3, '+') == NULL && strchr(lineAsmAufgeloest[i].sp3, '-') == NULL) {
                //oktal
                sprintf(literalValue, "%012lo", (unsigned long int) strtol(lineAsmAufgeloest[i].sp3 + 1, NULL, 8));
            } else {
                // dezimal
                strncpy(literalValue, lineAsmAufgeloest[i].sp3, sizeof(literalValue) - 1);
                literalValue[sizeof(literalValue) - 1] = '\0';
            }
            literalCount;
            sprintf(literalName, "l%04d", literalCount+1);

            strcpy(oldName , addLiteral(literalName, literalValue, relativAdresse+1));
            if (oldName[0] == '\0') {
               strcpy(oldName, literalName) ;
            }
            if (oldName[0] != '\0') { 
                strcpy(lineAsmAufgeloest[i].sp3, oldName);
            } 
        } 


        //  equ equ10 equ40 equ100
        if (strstr(lineAsmAufgeloest[i].sp2, "equ") != NULL) {  
            appendToEquTable(lineAsmAufgeloest[i].sp1, lineAsmAufgeloest[i].sp3);
            copyAndIncrementLineElements(i);
            if (strcmp(lineAsmAufgeloest[i].sp3, "") == 0) {
                MELDE_FEHLER_P1("Operand %s fehlt bei equ", lineAsmAufgeloest[i].sp3);
                is_error1 = 1;
            }

        }

        // abs
        if ( strcmp(lineAsmAufgeloest[i].sp2, "abs") == 0 ) {
            int rc = appendToAbsTable(lineAsmAufgeloest[i].sp1, lineAsmAufgeloest[i].sp3);
            copyAndIncrementLineElements(i);
            if (strcmp(lineAsmAufgeloest[i].sp3, "") == 0) {
                MELDE_FEHLER_P1("Operand %s fehlt bei abs", lineAsmAufgeloest[i].sp3);
                is_error1 = 1;
            }
            if ( rc == -1 ) {
                MELDE_FEHLER_P1("abs Definition %s existiert schon mit anderem Wert.",lineAsmAufgeloest[i].sp1);
                is_error1 = 1; 
            } else if (rc != 0 ) {
                MELDE_FEHLER_P1("abs Definition %s kann nicht aufgenommen werden. Tabelle voll.",lineAsmAufgeloest[i].sp1);
                is_error1 = 1;
            }
        }

        // sonstige Assembler-Anweisungen
        if ( isKeywordMatch(lineAsmAufgeloest[i].sp2) == 0 ) {
            if (!( (strstr(lineAsmAufgeloest[i].sp2, "equ") != NULL) ||  (strstr(lineAsmAufgeloest[i].sp2, "abs") != NULL) )) {  
               copyAndIncrementLineElements(i);
            }
            // Text-Anweisungen ausgenommen: Ein '#' im dt-Text (z. B. dt \a#b\) ist ein Sonderzeichen.
            if (!istTextAnweisung(lineAsmAufgeloest[i].sp2) &&
                !isValidSp3_keinLiteralEnthalten(lineAsmAufgeloest[i].sp3)) {
                baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
                printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "darf kein #-Literal sein", line);
                MELDE_FEHLER_P1("Operand %s darf kein #-Literal enthalten.",lineAsmAufgeloest[i].sp3);
                is_error1 = 1;
            }
        } else {
            // oktale Operationscodes
            copyAndIncrementLineElements(i);
        }
            

        // end
        // Die Literale werden einmalig hinter dem ersten end ausgegeben. end_war wird jetzt beim
        // Erkennen von end gesetzt (frueher nur innerhalb der Literalschleife) und die Schleife
        // wird nicht mehr verlassen: Zeilen hinter end (abs, equ) werden weiter ausgewertet, auch
        // wenn das Programm Literale enthaelt. Ausserdem erscheint die Warnung "end fehlt" nicht
        // mehr faelschlich, wenn end vorhanden ist, aber kein Literal.
        if ( strcmp(lineAsmAufgeloest[i].sp2, "end") == 0 && end_war == 0 ) {
            end_war=1;
            for (int i = 0; i < literalCount; i++) {
                processLiteralEntry( lineAsmAufgeloestTemp, &lineCountAsmAufgeloestTemp, literalTable, i);
            }
        }
    }
    
    if ( end_war == 0 ) {
        // es gab kein end im quellcode
        for (int i = 0; i < literalCount; i++) {
            processLiteralEntry( lineAsmAufgeloestTemp, &lineCountAsmAufgeloestTemp, literalTable, i);
        }
        MELDE_WARNUNG_P1("end - Anweisung %s fehlt.","");
    }


    if ( literalCount > 0 ) { 
        fprintf(symbolLog, "Literaltabelle\n\n");
        fprintf(symbolLog, "Symbol                             | RelAddr | Literalwert\n");
        fprintf(symbolLog, "-----------------------------------| ------- | -----------\n");
        for (int i = 0; i < literalCount; i++) {
            fprintf(symbolLog,"%-35s|  %04o   | %s\n", literalTable[i].literalName, literalTable[i].relativAdresse, literalTable[i].literalValue); 
        }
    }

    if ( equ_fuellstand > 0 ) { 
        fprintf(symbolLog, "\n\n");

        fprintf(symbolLog, "EQU-Definitionen\n\n");
        fprintf(symbolLog, "Symbol                             |   Wert  \n");
        fprintf(symbolLog, "-----------------------------------| --------\n");

        for (int i = 0; i < equ_fuellstand; i++) {
            fprintf(symbolLog,"%-35s|  %s\n", equ_tabelle[i].key, equ_tabelle[i].value);
        }
    }

    if ( abs_fuellstand > 0 ) { 
        fprintf(symbolLog, "\n\n");

        fprintf(symbolLog, "ABS-Definitionen\n\n");
        fprintf(symbolLog, "Symbol                             |   Wert  \n");
        fprintf(symbolLog, "-----------------------------------| --------\n");

        for (int i = 0; i < abs_fuellstand; i++) {
            fprintf(symbolLog,"%-35s|  %s\n", abs_tabelle[i].key, abs_tabelle[i].value);
        }
    }

    fprintf(symbolLog, "\n\n");
    fclose(symbolLog);
 
    if (is_error1 != 0) {
       is_error2 = 1;
    }

}

// ####################################

void swap(Symbol *a, Symbol *b) {
    Symbol temp = *a;
    *a = *b;
    *b = temp;
}

void bubbleSortBySymbol(Symbol symbolTable[], int symbolCount) {
    for (int i = 0; i < symbolCount - 1; i++) {
        for (int j = 0; j < symbolCount - i - 1; j++) {
            if (strcmp(symbolTable[j].symbol, symbolTable[j + 1].symbol) > 0) {
                swap(&symbolTable[j], &symbolTable[j + 1]);
            }
        }
    }
}

void bubbleSortByAddress(Symbol symbolTable[], int symbolCount) {
    for (int i = 0; i < symbolCount - 1; i++) {
        for (int j = 0; j < symbolCount - i - 1; j++) {
            if (symbolTable[j].address > symbolTable[j + 1].address) {
                swap(&symbolTable[j], &symbolTable[j + 1]);
            }
        }
    }
}

void sanitizeLabel(char *label) {
    if (label == NULL || strlen(label) == 0) {
        return; 
    }

    if (isspace(label[0])) {
        label[0] = '\0'; 
    }
}


int line_ausgegeben=0;
void printLineIfNotPrinted(const char *line) {
    if (line_ausgegeben == 0) {
        printf("%s\n", line);
        line_ausgegeben = 1;
    }
}

void testeAdress(char *label, char *line) {
    char message[100];
    if (strlen(label) > MAX_SYMBOL_LENGTH) {
        printLineIfNotPrinted(line);
        is_error2=1;
        sprintf(message, " ist länger als %d Zeichen.", MAX_LABEL_LENGTH);
        printLabelError(label, "Label", message, line);
        //char temp[sizeof(label)+1];
        memmove(label + 1, label, strlen(label) + 1);
        label[0] = ';';
    }
    if (isValidLabel(label) == false ) {
        printLineIfNotPrinted(line);
        is_error2=1;
        sprintf(message, "   Label: \"%s\" enthält unzulässige Zeichen", label);
        printLabelError(label, "", message, line);
    }
    char *pos = strstr(line, label); // Finde das Label in der Zeile
    if (pos) {
        pos += strlen(label); // Springe hinter das Label
        
        // Prüfe, ob direkt danach ein Doppelpunkt steht
        if (*pos == ':') {
            pos++; // Überspringe den Doppelpunkt
            
            // Überspringe Leerzeichen und Tabs nach dem Doppelpunkt
            while (*pos == ' ' || *pos == '\t') {
                pos++;
            }
        
            // Prüfe, ob noch ein Substring folgt
            if (*pos == '\0') {
                printLineIfNotPrinted(line);
                is_error2 = 1; 
                sprintf(message, "   Label: \"%s\" steht ohne Operation in der Zeile.", label);
                printLabelError(label, "", message, line);
            }
        }
    }
}


void extractBackslashContent(char *line, char *textkonst) {
    char *start = strchr(line, '\\');  // Finde ersten Backslash
    if (!start) return;  // Falls kein Backslash gefunden, nichts tun

    char *end = strchr(start + 1, '\\');  // Finde zweiten Backslash
    if (!end) return;  // Falls kein zweiter Backslash gefunden, nichts tun

    // Extrahiere den Inhalt zwischen den Backslashes
    size_t len = end - start + 1;
    strncpy(textkonst, start, len);
    textkonst[len] = '\0';

    // Entferne den extrahierten Teil aus `line`
    memmove(start, end + 1, strlen(end + 1) + 1);
}


// ############################################


unsigned int startAdresse = 0;
int zaehleText(char operand[], int no_kbgb);

void pass2(char *symbolLogFile, char *symFileName) {
    printf("Löse Symbole auf nach %s und %s\n", symbolLogFile, symFileName);

    FILE *symbolLog = fopen(symbolLogFile, "a");
    FILE *symFile = fopen(symFileName, "w+");

    // lineAsmAufgeloest und wird dynamisch vergrößert
    lineCountAsmAufgeloest = 0;
    // lineElements lineAsmAufgeloestTemp[PROGRAMMZEILEN];
    // lineCountAsmAufgeloestTemp = x;

    char line[MAX_LINE_LENGTH];
    char message[1024];
    unsigned int programCounter = 0;
    unsigned int relativAdresse = 0;
    char operation[256];
    char operand[256];
    char label[256];

    line_ausgegeben=0;

    int is_start = 0;
    int is_error = 0;
    int raAdr=0;


    void copyAndIncrementLineElements2(int i) {
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, lineAsmAufgeloestTemp[i].sp1);
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, lineAsmAufgeloestTemp[i].sp2);
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, lineAsmAufgeloestTemp[i].sp3);
        strcpy(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, lineAsmAufgeloestTemp[i].sp4);
        lineCountAsmAufgeloest++; 
    }

    relativAdresse = 0000;

    for (int i = 0; i < lineCountAsmAufgeloestTemp; i++) {

        // übergehen
        if (  ((lineAsmAufgeloestTemp[i].sp1[0] == ';') || (lineAsmAufgeloestTemp[i].sp1[0] == '#') || (lineAsmAufgeloestTemp[i].sp1[0] == '$')  ||
                (lineAsmAufgeloestTemp[i].sp1[0] == '&') || (strstr(lineAsmAufgeloestTemp[i].sp1, "***") != NULL)  ) ) {
            copyAndIncrementLineElements2(i);
            continue;
        }

        // Leerzeile
        if (lineAsmAufgeloestTemp[i].sp1[0] == '\0' && lineAsmAufgeloestTemp[i].sp2[0] == '\0' &&
            lineAsmAufgeloestTemp[i].sp3[0] == '\0' && lineAsmAufgeloestTemp[i].sp4[0] == '\0') 
        {
            copyAndIncrementLineElements2(i);
            continue;
        }

        char textkonst[1024]="";
        // Zeile zuerst kopieren: extractBackslashContent schneidet den \...\-Text
        // aus sp3 heraus, Pass 3 braucht ihn aber noch in lineAsmAufgeloest.
        copyAndIncrementLineElements2(i);
        extractBackslashContent(lineAsmAufgeloestTemp[i].sp3,textkonst);


        strcpy(operation, lineAsmAufgeloestTemp[i].sp2);
        strcpy(operand, lineAsmAufgeloestTemp[i].sp3);
        strcpy(label, "");
        if ( isValidLabel(lineAsmAufgeloestTemp[i].sp1) )  {  
            strcpy(label, lineAsmAufgeloestTemp[i].sp1);
            if (strlen(label) > MAX_SYMBOL_LENGTH) {
               printLineIfNotPrinted(line);
               is_error2 = 1;
               sprintf(message, "Label ist länger als %d Zeichen.", MAX_LABEL_LENGTH);
               MELDE_FEHLER_P2(i, message );
               memmove(label + 1, label, strlen(label) + 1);
               label[0] = ';';
               if ( strlen(operation) < 1 ) { 
                  is_error2 = 1;
                  sprintf(message, "Label: \"%s\" ohne `Operation`.", label);
                  MELDE_FEHLER_P2(i, message );
               }
            }
        } else if ( lineAsmAufgeloestTemp[i].sp1[0] != '\0' ) {
            // Ein Label, das nicht gueltig ist (Ziffer am Anfang, Zeichen wie - . oder ae), wurde frueher
            // still verworfen und fehlte dann ohne Meldung in .sym und Symboltabelle.
            is_error2 = 1;
            sprintf(message, "Label \"%s\" ist unzulaessig: erlaubt sind Buchstaben, Ziffern und _, das erste Zeichen ist keine Ziffer.", lineAsmAufgeloestTemp[i].sp1);
            MELDE_FEHLER_P2(i, message );
        }


        if ( ( programCounter > 0 ) && ( is_start == 0 ) ) {
            is_error2 = 1;
            MELDE_FEHLER_P2(i, "Opertionscode `start` fehlt als erste Anweisung.");
        }


        if (operation && isKeywordMatch(operation) == 1  /* nicht gefunden */) { 
            if ( isValidLabel(lineAsmAufgeloestTemp[i].sp1) )  {  
                addSymbol(lineAsmAufgeloestTemp[i].sp1, programCounter, relativAdresse, lineAsmAufgeloestTemp[i].sp2, lineAsmAufgeloestTemp[i].sp3,1,i);
            }
            programCounter++;
        }

        if (strcmp(operation, "start") == 0) {
            if ( is_start > 0 ) {
                is_error2 = 1;
                MELDE_FEHLER_P2(i, "Opertionscode `start` darf nur einmal vorkommen.");
            }
            is_start = 1;
            programCounter = 0;
            if (strlen(label) > 0) {
                // Doku 3.7: Ein Label vor `start` ist ein Fehler (frueher nur still verworfen).
                is_error2 = 1;
                sprintf(message, "Ein Label: \"%s\" vor `start` ist nicht zulaessig.", label);
                MELDE_FEHLER_P2(i, message );
            }
            if (operand && !strchr(operand, ';')) {
                raAdr=relativAdresse;
                startAdresse = evaluateAddress(operand, "", &is_error, &raAdr, label, programCounter, &absolutadresse);
                PRINT_MSG("Startadresse: %04o",startAdresse);
                if (( absolutadresse != 0 ) || (is_error != 0 ))  {
                    is_error2 = 1;
                    MELDE_FEHLER_P2(i, "Operand hinter `start` ist keine Konstante.");
                }
            }
        }

        if (operation && strstr(operation, "equ") != NULL) {
            if (operand) {
                char *currentPos = operand;
                raAdr=relativAdresse;
                unsigned int address = 0;
                if (*currentPos == '*') {   
                    address = sternadresseBearbeiten(operand, line, &is_error, programCounter) ;
                    if (strcmp(operation, "equ100") == 0) {
                        address = (address + 0100 - 1) & ~(0100 - 1); // Aufrunden auf nächste 0100
                    } else if (strcmp(operation, "equ40") == 0) {
                        address = (address + 0040 - 1) & ~(0040 - 1); // Aufrunden auf nächste 0040
                    } else if (strcmp(operation, "equ10") == 0) {
                        address = (address + 0010 - 1) & ~(0010 - 1); // Aufrunden auf nächste 0010
                    }      
                    programCounter = address;
                } else {
                    address = evaluateAddress(operand, "", &is_error, &raAdr, label, programCounter, &absolutadresse);
                    if ( is_error != 0) {is_error2=1; printHell = 1; }
                    programCounter = address;
                }
                if (  isValidLabel(label) ) {
                    addSymbol(label, address, relativAdresse, operation, operand,2,i);  
                }
                relativAdresse = programCounter;
            } else {
                is_error2 = 1;
                sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                MELDE_FEHLER_P2(i, message );
            }
        }

        if (operation && strcmp(operation, "abs") == 0) {
            if (operand) {
                raAdr=relativAdresse;
                unsigned int address = evaluateAddress(operand, "", &is_error, &raAdr, label, programCounter, &absolutadresse);
                if (( absolutadresse != 0 ) || (is_error != 0 ))  {
                    is_error2 = 1;
                    sprintf(message, "Operand: \"%s\" ist keine Konstante.", operand);
                    MELDE_FEHLER_P2(i, message );
                }
    
                if ( isValidLabel(label) ) {
                    addSymbol(label, address, relativAdresse, operation, operand,3,i);  
                }
                relativAdresse = programCounter;
            } else {
                is_error2 = 1;
                sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                MELDE_FEHLER_P2(i, message );
            }
        }

        if (operation && strcmp(operation, "db") == 0) {
            if (  isValidLabel(label) ) { 
                addSymbol(label, programCounter, relativAdresse, operation, operand,4,i);
            }
            {
                long byteCount = 0;
                if ( pruefeDbOperand(operation, operand, &byteCount, message, sizeof(message)) ) {
                    programCounter += (unsigned int)byteCount;
                } else {
                    is_error2 = 1;
                    MELDE_FEHLER_P2(i, message );
                }
            }
        }

        if (operation && strcmp(operation, "dbn") == 0) {
            if (  isValidLabel(label)) { 
                addSymbol(label, programCounter, relativAdresse, operation, operand,5,i);
            }
            {
                long byteCount = 0;
                if ( pruefeDbOperand(operation, operand, &byteCount, message, sizeof(message)) ) {
                    programCounter += (unsigned int)byteCount;
                } else {
                    is_error2 = 1;
                    MELDE_FEHLER_P2(i, message );
                }
            }
        }

        if ( operation ) { 
            if ( strcmp(operation, "dt") == 0  ) {
                if (  isValidLabel(label) ) { 
                    addSymbol(label, programCounter, relativAdresse, operation, operand,6,i);
                }

                if (textkonst[0] != '\0') {
                    programCounter += zaehleText(textkonst,0);
                } else { 
                    if (operand) {
                        programCounter += zaehleText(operand,0);
                    } else {
                        is_error2 = 1;
                        sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                        MELDE_FEHLER_P2(i, message );
                    }
                }
            }
        }

        if ( strcmp(operation, "dto") == 0 ) {
            if (  isValidLabel(label) ) { 
                addSymbol(label, programCounter, relativAdresse, operation, operand,7,i);
            }
            if (textkonst[0] != '\0') {
                programCounter += zaehleText(textkonst,1);
            } else { 
                if (operand) {
                    programCounter += zaehleText(operand,1);
                } else { 
                    is_error2 = 1;
                    sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                    MELDE_FEHLER_P2(i, message );
                }
            }
        }

        if ( strcmp(operation, "dtm") == 0 ) {
            if (  isValidLabel(label) ) { 
                addSymbol(label, programCounter, relativAdresse, operation, operand,8,i);
            }
            if (textkonst[0] != '\0') {
                programCounter += zaehleText(textkonst,2);
            } else { 
                if (operand) {
                    programCounter += zaehleText(operand,2);
                } else {
                    is_error2 = 1;
                    sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                    MELDE_FEHLER_P2(i, message );
                }
            }
        }

        if (operation && strcmp(operation, "dz") == 0) {
            if (  isValidLabel(label) ) { 
                addSymbol(label, programCounter, relativAdresse, operation, operand,9,i);
            }
            if (operand) {
                programCounter++;
            } else {
                is_error2 = 1;
                sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                MELDE_FEHLER_P2(i, message );
            }
        }

        if (operation && strcmp(operation, "dw") == 0) {
            if (operand) {
                char *currentPos = operand;
                raAdr=relativAdresse;

                if (*currentPos == '*') {    
    relativAdresse = sternadresseBearbeiten(operand, line, &is_error, programCounter) ;
                } else {
                    relativAdresse = evaluateAddress(operand, line, &is_error, &raAdr, label, programCounter, &absolutadresse);
                    if (( is_error != -2 ) && ( is_error != 0 )) { 
                        sprintf(message, "Operand: \"%s\" hat eine ungültige Konstante.", operand);
                        MELDE_FEHLER_P2(i, message );
                    } else {
                        if ( is_error == -2 ) {
                            // Der <werteausdruck> von dw darf Symbole enthalten (Doku 3.3), auch spaeter definierte.
                            // Er wird erst in Pass 3 ausgewertet, wenn alle Symbole bekannt sind; deshalb hier kein
                            // "spaetes Symbol" (BITMASK) mehr, das den Operanden in resolveSymbols() durch eine Zahl
                            // ersetzt haette (ohne Pruefung auf relative Adressen, und nur bei dw-Zeilen mit Marke).
                            if (  isValidLabel(label) ) {
                                addSymbol(label, programCounter , relativAdresse, operation, operand,10,i);
                            }
                        } else {
                            if ( is_error != 0 ) {
                                is_error2 = 1;
                            } else {
                                if ( isValidLabel(label) ) {
                                    addSymbol(label, programCounter, relativAdresse, operation, operand,11,i);
                                }
                            } 
                        }
                    }
                }    
                programCounter++;

            } else {
                is_error2 = 1;
                sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                MELDE_FEHLER_P2(i, message );
            }
        }

        if (operation && strcmp(operation, "da") == 0) {
            if (operand) {
                char *currentPos = operand;
                raAdr=relativAdresse;

                if (*currentPos == '*') {   
                    relativAdresse = sternadresseBearbeiten(operand, line, &is_error, programCounter) ;
                } else {
                    relativAdresse = evaluateAddress(operand, line, &is_error, &raAdr, label, programCounter, &absolutadresse);
                    if (( is_error != -2 ) && ( is_error != 0 )) { 
                        sprintf(message, "Operand: \"%s\" hat eine ungültige Konstante.", operand);
                        MELDE_FEHLER_P2(i, message );
                    } else {
                        if ( is_error == -2 ) {
                            if ( isValidLabel(label)) {
                                addSymbol(label, programCounter | 010000000000 , relativAdresse, operation, operand,12,i);
                            }
                        } else {
                            if ( is_error != 0 ) {
                                is_error2 = 1; 
                            } else {
                                if ( isValidLabel(label)) {
                                    addSymbol(label, programCounter, relativAdresse, operation, operand,13,i);
                                }
                            } 
                        }
                    }
                }
                programCounter++;
            } else {
                is_error2 = 1;
                sprintf(message, "Operand: \"%s\" ohne `Operation`.", operand);
                MELDE_FEHLER_P2(i, message );
            }
        }

        if (operation && strcmp(operation, "end") == 0) {
            if ( isValidLabel(label)) {
                addSymbol(label, programCounter, relativAdresse, operation,operand,14,i);
            }
        }
        line_ausgegeben=0;

        // Der Programmzaehler zeigt auf die NAECHSTE freie Zelle. Nach einem Wort auf Zelle 7777
        // steht er daher auf 010000 (= 8 * 1024); das ist noch zulaessig. Ein Fehler liegt erst vor,
        // wenn ein Wort auf Zelle 010000 oder darueber abgelegt werden muesste.
        if ( programCounter + startAdresse > 010000 ) { 
            is_error2 = 1;
            MELDE_FEHLER_P2(i, "Programmzählerüberlauf über 7777.");
        }

    }

    // --------------------------------------------------------------------------------------

    // Das Kommentarfeld `orig_operation` in der Symboltabelle ergänzen
    //
    // BUGFIX (siehe Analyse): Die ursprüngliche Implementierung suchte `orig_operation`
    // (z.B. "a" oder "b") per strstr() als reinen Teilstring in der Operanden-Spalte und
    // ersetzte den ERSTEN Treffer - unabhängig davon, ob dieser Treffer tatsächlich ein
    // eigenständiges Symbol war oder nur zufällig als Teilzeichenkette in einem längeren
    // Bezeichner vorkam. Dadurch wurden z.B. "adr_a" (enthält "a"), "adr_b" (enthält "a"
    // UND "b") und "beginn" (beginnt mit "b") fälschlich beschädigt, sobald Symbole mit
    // kurzen, einbuchstabigen Namen ("a", "b") aufgelöst wurden - mit der Folge, dass die
    // betroffenen Operanden in der .dmp-Datei korrupt waren und Pass 3 "Adresse ist
    // ungültig"-Fehler meldete.
    //
    // Fix: Ein Treffer zählt nur dann als Symbol-Treffer, wenn das Zeichen davor und das
    // Zeichen danach kein weiterer Bezeichner-Bestandteil (alphanumerisch oder '_') ist -
    // also eine echte Wortgrenze vorliegt. Andernfalls wird die Suche hinter dem (falschen)
    // Treffer fortgesetzt.
    void replaceOrigOperation( const char *orig_operation, unsigned int result) {
        // Suche der `orig_operation` in `lineAsmAufgeloest` und ersetzen durch `result`

        char line[1024];
        size_t opLen = strlen(orig_operation);
        if (opLen == 0) {
            return; // nichts zu ersetzen
        }
        for (int i = 0; i < lineCountAsmAufgeloest; i++) {
            strcpy(line, lineAsmAufgeloest[i].sp3);

            char *searchStart = line;
            char *pos;
            while ((pos = strstr(searchStart, orig_operation)) != NULL) {
                char before = (pos == line) ? '\0' : *(pos - 1);
                char after  = *(pos + opLen);
                int grenzeDavor  = (pos == line) || !(isalnum((unsigned char)before) || before == '_');
                int grenzeDanach = !(isalnum((unsigned char)after) || after == '_');

                if (grenzeDavor && grenzeDanach) {
                    char newLine[1024];
                    int offset = pos - line;

                    strncpy(newLine, line, offset);
                    newLine[offset] = '\0';

                    char resultStr[256];
                    snprintf(resultStr, sizeof(resultStr), "%012o", result);
                    strcat(newLine, resultStr);
                    strcat(newLine, pos + opLen);

                    strcpy(line, newLine);
                    strcpy(lineAsmAufgeloest[i].sp3, line);
                    break; // ein echter Treffer pro Zeile genügt
                }

                // Kein echtes Wortgrenzen-Match - hinter diesem Fundort weitersuchen
                searchStart = pos + 1;
            }
        }
        //printf("INFO: '%s' wurde in %s durch '%011o' ersetzt.\n", orig_operation, inputFileName, result);
    }

    // späte symbole auflösen
    void resolveSymbols() {
        int isNumber(char *token) {
            for (int i = 0; token[i] != '\0'; i++) {
                if (!isdigit((unsigned char)token[i])) {
                    return 0; // Nicht numerisch
                }
            }
            return 1; // Numerisch
        }

        int getSymbolAddress(char *token) {
            for (int i = 0; i < symbolCount; i++) {
                if (strcmp(symbolTable[i].symbol, token) == 0) {
                    return symbolTable[i].address; // Rückgabe der Adresse des Symbols
                }
            }
            return -1; // Symbol nicht gefunden
        }

        for (int i = 0; i < symbolCount; i++) {
            if (symbolTable[i].address & BITMASK) {

                char *expr = symbolTable[i].orig_operation;
                int result = 0;
                int value = 0;
                char lastOp = '+';

                while (*expr) {
                    // Überspringe Leerzeichen
                    while (*expr && isspace((unsigned char)*expr)) expr++;

                    // Wenn Operator gefunden, speichern
                    if (*expr == '+' || *expr == '-' || *expr == '*' || *expr == '/') {
                        lastOp = *expr;
                        expr++;
                        continue;
                    }

                    // Extrahiere nächstes Token (Symbol oder Zahl)
                    char token[50] = {0};  // Buffer für Token
                    int j = 0;
                    while (*expr && !isspace((unsigned char)*expr) && *expr != '+' && *expr != '-' && *expr != '*' && *expr != '/') {
                        token[j++] = *expr++;
                    }
                    token[j] = '\0';  // Null-terminieren

                    // Prüfe Token: Zahl oder Symbol
                    if (isNumber(token)) {
                        value = atoi(token);
                    } else if (isSymbol(token)) {
                        value = getSymbolAddress(token);
                        if (value == -1) {
                            is_error = 1;
                        }
                    } else {
                        sprintf(message, "   Ausdruck: \"%s\" ist ungültig.", token);
                        MELDE_FEHLER_P2(i, message );
                        is_error = 1;
                    }

                    // Berechnung basierend auf vorherigem Operator
                    switch (lastOp) {
                        case '+': result += value; break;
                        case '-': result -= value; break;
                        case '*': result *= value; break;
                        case '/': result /= (value == 0 ? 1 : value); break;
                    }
                }

                replaceOrigOperation(symbolTable[i].orig_operation, result);  
                sprintf(symbolTable[i].orig_operation, "%012o", result);
                symbolTable[i].address &= ~BITMASK;
                //printf("INFO: Symbol '%s' auf %012o gesetzt.\n", symbolTable[i].symbol, result);
            }
        }
    }

    // --------------------------------------------------------------------------------------

    resolveSymbols();

    // `dw <literal>` in einer Zeile OHNE Label (Doku 3.3: "Speichert die <adresse> von
    // <literalsymbol> auf dem aktuellen <speicherplatz>").
    //
    // resolveSymbols() ersetzt den Literalnamen im Operanden (z. B. "l0001") nur dann durch die
    // Adresse des Literals, wenn die dw-Zeile ein Label hat, denn der "spaete Symbol"-Eintrag
    // haengt an addSymbol(label, ...). Ohne Label blieb "l0001" im Operanden stehen, und Pass 3
    // meldete "Operand l0001 ist ungueltig" (rc 16), obwohl `dw #5` und `dw @a` zulaessig sind.
    //
    // Hier wird derselbe Ersatztext (12 Oktalziffern, keine Hauptleitadresse) nachgetragen, den
    // resolveSymbols() bei einer Zeile mit Label erzeugt. Ersetzt werden nur echte Literalnamen
    // aus der Literaltabelle. Andere Symbole im Operanden von dw (`dw a`, `dw a-b`, `dw x1+1`) bleiben
    // unveraendert stehen und werden in Pass 3 nach den Regeln von Doku 3.3 ausgewertet (evaluateValue).
    for (int li = 0; li < lineCountAsmAufgeloest; li++) {
        if (strcmp(lineAsmAufgeloest[li].sp2, "dw") != 0) continue;
        if (!isLiteralInTable(lineAsmAufgeloest[li].sp3)) continue;
        for (int si = 0; si < symbolCount; si++) {
            if (strcmp(symbolTable[si].symbol, lineAsmAufgeloest[li].sp3) == 0) {
                sprintf(lineAsmAufgeloest[li].sp3, "%012o", (unsigned int)symbolTable[si].address);
                break;
            }
        }
    }

    fprintf(symbolLog, "Symboltabelle\n\n");
    fprintf(symbolLog, "Symbol                             | RelAddr |    Adresse      | original Operation\n");
    fprintf(symbolLog, "-----------------------------------| ------- | --------------- | ----------------\n");
    bubbleSortBySymbol(symbolTable, symbolCount);
    for (int i = 0; i < symbolCount; i++) {
        fprintf(symbolLog, "%-34s |   %04o  |  %012o   | %s\n", symbolTable[i].symbol, symbolTable[i].relativAdresse, symbolTable[i].address, symbolTable[i].orig_operation);
    }

    fprintf(symbolLog, "\n\n");
    fprintf(symbolLog, "Adresstabelle\n\n");
    fprintf(symbolLog, "Symbol                             | RelAddr |    Adresse\n");
    fprintf(symbolLog, "-----------------------------------| ------- | ---------------\n");
    bubbleSortByAddress(symbolTable, symbolCount);
    for (int i = 0; i < symbolCount; i++) {
        fprintf(symbolLog, "%-34s |   %04o  | %012o\n", symbolTable[i].symbol, symbolTable[i].relativAdresse, symbolTable[i].address);
    }

    fclose(symbolLog);

    for (int i = 0; i < symbolCount; i++) {
        fprintf(symFile, "%s,%04o\n", symbolTable[i].symbol, symbolTable[i].address);
    }
    fclose(symFile);


    if (is_error2 != 0) {
       printFormattedAsmListing(lineAsmAufgeloest, lineCountAsmAufgeloest);
    } 
//exit(2);

}

// -------------------------------------------------------

// Grund des letzten Fehlers von evaluateValue (NULL = kein besonderer Grund, nur Syntax-/Bereichsfehler).
// Wird von Pass 3 an die Meldung "Operand ist ungueltig" angehaengt.
static const char *evaluateValueGrund = NULL;

// Liefert 1 und setzt *wert und *absolut, wenn das Symbol in der Symboltabelle steht (sonst 0).
// *absolut = 1: Symbol wurde mit abs definiert (nicht verschieblich); sonst ist es eine Relativadresse
// (Marke, equ-Symbol, Literalsymbol).
static int sucheSymbolFuerWert(const char *name, long long *wert, int *absolut) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, name) == 0) {
            *wert = (long long)(symbolTable[i].address & ~BITMASK);
            *absolut = sucheInAbsTabelle(name) ? 1 : 0;
            return 1;
        }
    }
    return 0;
}

// Wertet den <werteausdruck> von dw aus (Doku 3.3).
//   Zahlen:    Oktalzahl (fuehrende 0) oder Dezimalzahl.
//   Symbole:   abs-Symbole sind erlaubt. Relative Symbole (Marken, equ-Symbole) sind nur erlaubt, wenn sich ihre
//              Verschiebung aufhebt: die Differenz zweier symbolischer Adressen ist absolut und zulaessig.
//              Eine einzelne symbolische Adresse (Ergebnis relativ) ist nicht zulaessig; Adressen schreibt man mit da.
//   Rechnen:   * und / vor + und -, links nach rechts. Relative Symbole duerfen nicht multipliziert oder dividiert werden.
// Jedes Symbol wird mit seinem Verschiebungsgrad gefuehrt: abs-Symbole und Zahlen 0, relative Symbole +1;
// bei + addieren, bei - subtrahieren sich die Grade. Das Ergebnis ist nur bei Grad 0 absolut.
long long int evaluateValue(char *operand, int *errorFlag) {
    long long values[512];     // vorzeichenbehaftet, damit Subtraktion und negative Werte stimmen
    int       grade[512];      // Verschiebungsgrad je Wert (0 = absolut)
    char operators[512];
    int valueIndex = 0, operatorIndex = 0;

    *errorFlag = 0; // Standardmäßig kein Fehler
    evaluateValueGrund = NULL;

    char *currentPos = operand;

    while (*currentPos != '\0') {
        while (*currentPos == ' ') currentPos++;

        char tempToken[512];
        int tokenLength = 0;

        // Extrahiere Zahl oder Symbol bis zum Operator
        while (*currentPos != '\0' && !strchr("+-*/", *currentPos)) {
            if (!(isalnum((unsigned char)*currentPos) || *currentPos == '_') || tokenLength >= (int)sizeof(tempToken) - 1) {
                *errorFlag = 1;
                return 0;
            }
            tempToken[tokenLength++] = *currentPos;
            currentPos++;
        }
        tempToken[tokenLength] = '\0';

        // Fuehrendes Vorzeichen (-5, +5): als 0-5 bzw. 0+5 auswerten
        if (tokenLength == 0 && valueIndex == 0 && *currentPos != '\0' && strchr("+-", *currentPos)) {
            grade[valueIndex] = 0;
            values[valueIndex++] = 0;
        }

        if (tokenLength > 0) {
            long long value = 0;
            int grad = 0;
            if (isdigit((unsigned char)tempToken[0])) {
                // Zahl: nur Ziffern
                char *endPtr;
                if (tempToken[0] == '0') {
                    value = strtol(tempToken, &endPtr, 8);
                } else {
                    value = strtol(tempToken, &endPtr, 10);
                }
                if (*endPtr != '\0') {
                    *errorFlag = 1; // Nicht konvertierbarer Wert
                    return 0;
                }
            } else {
                // Symbol
                int absolut = 0;
                if (!sucheSymbolFuerWert(tempToken, &value, &absolut)) {
                    evaluateValueGrund = "Symbol nicht definiert";
                    *errorFlag = 1;
                    return 0;
                }
                grad = absolut ? 0 : 1;
            }
            grade[valueIndex] = grad;
            values[valueIndex++] = value; // Speichere den konvertierten Wert
        }

        // Speichere den Operator
        if (*currentPos != '\0' && strchr("+-*/", *currentPos)) {
            operators[operatorIndex++] = *currentPos;
            currentPos++;
        }
    }

    // Jeder Operator braucht einen rechten Operanden (z. B. "5-" ist ungueltig)
    if (operatorIndex >= valueIndex) {
        *errorFlag = 1;
        return 0;
    }

    // Multiplikation und Division zuerst ausführen
    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '*' || operators[i] == '/') {
            long long leftValue = values[i];
            long long rightValue = values[i + 1];

            // Eine relative Adresse darf nicht multipliziert oder dividiert werden.
            if (grade[i] != 0 || grade[i + 1] != 0) {
                evaluateValueGrund = "symbolische Adresse in * oder /";
                *errorFlag = 1;
                return 0;
            }

            if (operators[i] == '*') {
                if (__builtin_mul_overflow(leftValue, rightValue, &values[i])) {
                    *errorFlag = 1; // Ueberlauf
                    return 0;
                }
            } else if (operators[i] == '/') {
                if (rightValue == 0) {
                    *errorFlag = 1; // Division durch Null ist unzulässig
                    return 0;
                }
                values[i] = leftValue / rightValue;
            }

            // Werte und Operatoren verschieben
            for (int j = i + 1; j < valueIndex - 1; j++) {
                values[j] = values[j + 1];
                grade[j] = grade[j + 1];
            }
            valueIndex--;
            for (int j = i; j < operatorIndex - 1; j++) {
                operators[j] = operators[j + 1];
            }
            operatorIndex--;
            i--;
        }
    }

    // Addition und Subtraktion ausführen
    long long totalValue = values[0];
    int totalGrad = grade[0];
    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '+') {
            if (__builtin_add_overflow(totalValue, values[i + 1], &totalValue)) { *errorFlag = 1; return 0; }
            totalGrad += grade[i + 1];
        } else if (operators[i] == '-') {
            if (__builtin_sub_overflow(totalValue, values[i + 1], &totalValue)) { *errorFlag = 1; return 0; }
            totalGrad -= grade[i + 1];
        }
    }

    // Ergebnis relativ (z. B. eine einzelne symbolische Adresse, "a+1", "a+b"): nicht zulaessig.
    if (totalGrad != 0) {
        evaluateValueGrund = "Ergebnis ist relativ; Adressen mit da schreiben, erlaubt ist nur die Differenz zweier Adressen";
        *errorFlag = 1;
        return 0;
    }

    return totalValue;
}

int getSymbolAddress(char *operand) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, operand) == 0) {
            return symbolTable[i].address;
        }
    }
    return -1; // Operand nicht gefunden
}

// ############################

int isSymbol(char *token) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, token) == 0) {
            return 1; // Symbol
        }
    }
    return 0; // Kein Symbol
}

// Prüfung auf nummerisch
int isValidToken(const char *tempToken) {
    for (int i = 0; tempToken[i] != '\0'; i++) {
        if (!(tempToken[i] == '-' || (tempToken[i] >= '0' && tempToken[i] <= '9'))) {
            return 0; // Ungültiges Zeichen gefunden
        }
    }
    return 1; // Alle Zeichen sind gültig
}

unsigned int sternadresseBearbeiten(char *xoperand, char *line, int *errorFlag, unsigned int programCounter) {
    if (!xoperand) {
        printAdressError(xoperand, "Operand", "Ungültige Sternadresse", line);
        *errorFlag = -1;
        return 0;
    }

    unsigned int result = programCounter; // Setze die Sternadresse

    char operand[1024];
    strcpy(operand, xoperand);
    char *expr = operand + 1; // Ignoriere das erste '*'
    char *token = strtok(expr, "+-*/");
    char lastOperator = '+'; // Standardmäßig Addition
    unsigned int value;

    while (token) {
        if (isdigit(token[0])) {
            if (token[0] == '0') {
               value = strtoul(token, NULL, 8);
            } else {  
               value = strtoul(token, NULL, 10);
            }
            switch (lastOperator) {
                case '+': result += value; break;
                case '-': result -= value; break;
                case '*': result *= value; break;
                case '/': if (value != 0) result /= value; else {
                              printAdressError(token, "Operand", "Division durch Null", line);
                              *errorFlag = -1;
                              return 0;
                          }
                          break;
            }
        } else {
            int symbolValue = getSymbolAddress(token);
            if (symbolValue == -1) {
                printAdressError(token, "Operand", "Ungültiges Symbol", line);
                *errorFlag = -1;
                return 0;
            }
            switch (lastOperator) {
                case '+': result += symbolValue; break;
                case '-': result -= symbolValue; break;
                case '*': result *= symbolValue; break;
                case '/': if (symbolValue != 0) result /= symbolValue; else {
                              printAdressError(token, "Operand", "Division durch Null", line);
                              *errorFlag = -1;
                              return 0;
                          }
                          break;
            }
        }

        char *operatorToken = strtok(NULL, "+-*/");
        if (operatorToken) {
            lastOperator = expr[token + strlen(token) - operand];
            token = strtok(NULL, "+-*/");
        } else {
            token = NULL;
        }
    }

    return result;
}

unsigned int evaluateAddress(char *operand, char *line, int *errorFlag, int *raAdr, char *label, unsigned int programCounter, unsigned int *absolutadresse) {
    unsigned int values[MAX_LINE_LENGTH];
    values[0] = 0;
    char operators[MAX_LINE_LENGTH];
    int valueIndex = 0, operatorIndex = 0, symbolCount = 0;

    *errorFlag = 0;      // Standardmäßig kein Fehler
    *raAdr = 0;          // Standardmäßig keine relativAdresse
    *absolutadresse = 0; // Standartmäßig relativ

    char *endPtr;    
    char *currentPos = operand;
    unsigned int totalValue=0;

    if (*currentPos == '*') {
       totalValue = sternadresseBearbeiten(operand, line, errorFlag, programCounter) ;
       return totalValue; 
    }

    // currentPos == operand
    while (*currentPos != '\0') {
        while (*currentPos == ' ') currentPos++;

        char tempToken[MAX_LINE_LENGTH];
        int tokenLength = 0;

        while (*currentPos != '\0' && !strchr("+-*/", *currentPos)) {
            tempToken[tokenLength++] = *currentPos;
            currentPos++;
        }
        tempToken[tokenLength] = '\0';

        if (tokenLength > 0) {
            unsigned int value = 0;
            if (isSymbol(tempToken)) {
                symbolCount++;

                //testeAdress(tempToken, line);
                if ( sucheInAbsTabelle(tempToken) ) { 
                   *absolutadresse = 1;
                }
                value = getSymbolAddress(tempToken);
                if (value == -1) {
                    printAdressError(operand, "Operand", " Ungültiges Symbol", line);
                    *errorFlag = -1; // Fehler: Ungültiges Symbol
                    return 0;
                }

                // Relativadresse für das Symbol finden
                for (int i = 0; i < symbolCount; i++) {
                    if (strcmp(symbolTable[i].symbol, tempToken) == 0) {
                        *raAdr = symbolTable[i].relativAdresse;
                        break;
                    }
                }

            } else if (!isValidToken(tempToken) && (strcmp(tempToken, label) == 0)) { 
                value = programCounter;

            } else {
                if (tempToken[0] == '0') {
                            value = strtol(tempToken, &endPtr, 8);
                } else { 
                            value = strtol(tempToken, &endPtr, 10);
                }
                if (*endPtr != '\0') {
                    *errorFlag = -2; 
                    return 0;
                }
            }
            values[valueIndex++] = value;
        }

        if (*currentPos != '\0' && strchr("+-*/", *currentPos)) {
            operators[operatorIndex++] = *currentPos;
            currentPos++;
        }
    }

    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '*' || operators[i] == '/') {
            unsigned int leftValue = values[i];
            unsigned int rightValue = values[i + 1];

            if (operators[i] == '*') {
                values[i] = leftValue * rightValue;
            } else if (operators[i] == '/') {
                if (rightValue == 0) {
                    printAdressError(operand, "Operand", " Division durch Null", line);
                    *errorFlag = -4; // Fehler: Division durch Null
                    return 0;
                }
                values[i] = leftValue / rightValue;
            }

            for (int j = i + 1; j < valueIndex - 1; j++) {
                values[j] = values[j + 1];
            }
            valueIndex--;
            for (int j = i; j < operatorIndex - 1; j++) {
                operators[j] = operators[j + 1];
            }
            operatorIndex--;
            i--;
        }
    }

    totalValue = values[0];

    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '+') {
            totalValue += values[i + 1];
        } else if (operators[i] == '-') {
            totalValue -= values[i + 1];
        }
    }

    return totalValue; 
}


// Prueft den <adressausdruck> von da (und von @-Literalen, die als da-Zeile erzeugt werden) gemaess
// Doku 3.4: kein Vorzeichen (negative Adressen gibt es nicht), hoechstens ein Symbol, keine fehlenden
// Operanden (z. B. "5-" oder "x+*2"). Der Wertebereich 00000 bis 07777 wird nach der Auswertung
// geprueft. Eine Sternadresse (*) wird von sternadresseBearbeiten geprueft.
// Rueckgabe 1 = in Ordnung, 0 = Fehler (Text in meldung).
static int pruefeAdressausdruck(const char *operand, char *meldung, size_t groesse) {
    const char *p = (operand != NULL) ? operand : "";
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0') {
        snprintf(meldung, groesse, "Adressausdruck fehlt.");
        return 0;
    }
    if (*p == '*') return 1;
    if (*p == '-' || *p == '+') {
        snprintf(meldung, groesse, "Der Adressausdruck darf nicht mit einem Vorzeichen beginnen (Adressen sind 00000 bis 07777).");
        return 0;
    }
    int symbole = 0;
    for (;;) {
        char token[MAX_LINE_LENGTH];
        int n = 0;
        while (*p && !strchr("+-*/", *p)) {
            if (n < (int)sizeof(token) - 1) token[n++] = *p;
            p++;
        }
        while (n > 0 && (token[n - 1] == ' ' || token[n - 1] == '\t')) n--;   // Leerraum am Ende entfernen
        token[n] = '\0';
        if (n == 0) {
            snprintf(meldung, groesse, "Im Adressausdruck fehlt ein Operand (zwei Operatoren hintereinander oder Operator am Ende).");
            return 0;
        }
        if (isSymbol(token)) symbole++;
        if (*p == '\0') break;
        p++;                       // Operator ueberspringen
        if (*p == '\0') {
            snprintf(meldung, groesse, "Im Adressausdruck fehlt ein Operand (zwei Operatoren hintereinander oder Operator am Ende).");
            return 0;
        }
    }
    if (symbole > 1) {
        snprintf(meldung, groesse, "Der Adressausdruck enthält mehr als ein Symbol (höchstens ein Symbol ist erlaubt).");
        return 0;
    }
    return 1;
}

char* getOperationCode(char *operation) {
    static char octalCodeString[4]; 
    for (int i = 0; opsTable[i].symbolicCode != NULL; i++) {
        if (strcmp(opsTable[i].symbolicCode, operation) == 0) {
            sprintf(octalCodeString, "%03o", opsTable[i].octalCode);
            return octalCodeString;
        }
    }

    // Oktale Operationscodes bestehen aus genau drei Oktalziffern (0-7); z. B. 999 ist ungueltig
    if (strlen(operation) == 3 &&
        operation[0] >= '0' && operation[0] <= '7' &&
        operation[1] >= '0' && operation[1] <= '7' &&
        operation[2] >= '0' && operation[2] <= '7') {
        strncpy(octalCodeString, operation, 3);
        octalCodeString[3] = '\0'; 
        return octalCodeString;
    }

    // Rückgabe für ungültigen Code
    return "XXX";
}


void formatLabel(char **label) {
    if (*label == NULL) {
        fprintf(stderr, "\033[35mFehler: Ungültiger Label-Zeiger\033[0m\n");
        exit(RC_FEHLER);
    }

    char temp[35] = {0};
    const char *start = *label;
    while (*start == ' ') start++;
    const char *end = *label + strlen(*label) - 1;
    while (end > start && *end == ' ') end--;

    size_t trimmedLength = end - start + 1;
    strncpy(temp, start, trimmedLength);

    for (size_t i = trimmedLength; i < 34; i++) {
        temp[i] = ' ';
    }
    temp[34] = '\0';

    free(*label);
    *label = malloc(35 * sizeof(char));
    if (*label == NULL) exit(RC_FEHLER);
    strcpy(*label, temp);
}


char *formatOperand(const char *op) {
    // Speicher für das neue Format reservieren
    char *formatted = malloc(9 * sizeof(char)); // 8 Zeichen + Nullterminator

    // Leerzeichen entfernen (Trimmen)
    const char *start = op;
    while (isspace((unsigned char)*start)) start++; // Führende Leerzeichen entfernen
    const char *end = start + strlen(start) - 1;
    while (end > start && isspace((unsigned char)*end)) end--; // Nachfolgende Leerzeichen entfernen

    size_t length = end - start + 1;
    // Zeichen kopieren und auffüllen
    if (length > 0) {
        strncpy(formatted, start, length);
    }
    for (size_t i = length; i < 8; i++) {
        formatted[i] = ' '; // Mit Leerzeichen auffüllen
    }
    formatted[8] = '\0'; // Nullterminator setzen
    return formatted;
}


typedef struct {
    unsigned int spalte1; // Erste Spalte (xxxx)
    unsigned int spalte2; // Zweite Spalte (ASCII-Wert)
    unsigned int spalte3; // Dritte Spalte (Alternative ASCII-Wert)
} TableRow;

#define OUT_SIZE 50 
TableRow outUmschluesselungsTable[OUT_SIZE] = {
    {0010, 60, 49},
    {0020, 34, 50},
    {0230, 0, 51},
    {0040, 91, 52},
    {0250, 62, 53},
    {0260, 39, 54},
    {0070, 0, 55},
    {0100, 126, 56},
    {0310, 93, 57},
    {0200, 35, 48},
    {01740, 42, 37},
    {01550, 9, 9},
    {01300, 81, 113},
    {01660, 87, 119},
    {0450, 69, 101},
    {01110, 82, 114},
    {01630, 84, 116},
    {01710, 90, 122},
    {01440, 85, 117},
    {0510, 73, 105},
    {01060, 79, 111},
    {01270, 80, 112},
    {0150, 40, 58},
    {0400, 61, 43},
    {0610, 65, 97},
    {01420, 83, 115},
    {0640, 68, 100},
    {0460, 70, 102},
    {0670, 71, 103},
    {0700, 72, 104},
    {01210, 74, 106},
    {01220, 75, 107},
    {01030, 76, 108},
    {01600, 59, 96},
    {01410, 41, 47},
    {02720, 10, 10},
    {01500, 89, 121},
    {01470, 88, 120},
    {0430, 67, 99},
    {01650, 86, 118},
    {0620, 66, 98},
    {01050, 78, 110},
    {01240, 77, 109},
    {01530, 63, 44},
    {0730, 33, 46},
    {01000, 465, 45},   // Zeile 48: Tabelle 1: Gbuch = 465 (Dreieck), Klbuch = 45 (Minus)
    {0320, 32, 32}
};
//    {0320, 32, 32}

// Prüfen, ob die Zeichen der Text-Definition in der Tabelle vorhanden sind.
int isValueInTable(const char *operand, TableRow outUmschluesselungsTable[], int size, int *missingPos) {
    for (size_t i = 0; i < strlen(operand); i++) {
        unsigned char asciiValue = (unsigned char)operand[i]; // ASCII-Wert des Zeichens

        int found = 0; // Flag, ob das Zeichen gefunden wurde

        for (int j = 0; j < size; j++) {
            if (outUmschluesselungsTable[j].spalte2 == asciiValue || outUmschluesselungsTable[j].spalte3 == asciiValue) {
                found = 1; // Zeichen gefunden
                break;
            }
        }

        if (!found) {
            *missingPos = (int)i; // Speichere die Position des fehlenden Zeichens
            return 0; // Fehler: Zeichen nicht gefunden
        }
    }

    return 1; // Alle Zeichen gültig
}


void copyAndIncrementLineElementsX(int i, char *buffer) {
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, buffer);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, lineAsmAufgeloest[i].sp1);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, lineAsmAufgeloest[i].sp2);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, lineAsmAufgeloest[i].sp3);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, lineAsmAufgeloest[i].sp4);
    
    lineCountAsmAufgeloestX++; 
}

void copyAndIncrementLineElementsSpOnly(int i, char *buffer) {
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, buffer);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, "; ");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");
    
    lineCountAsmAufgeloestX++; 
}


// Schreibt eine Zeile in die Objektdatei (.obj).
//  - Die Adreßspalte entfaellt: "0007: 01 0006 241" wird zu "01 0006 241"; bei Zeilen, die schon bisher keine
//    Adresse hatten ("      20 0000 0100"), entfallen die fuehrenden Leerzeichen.
//  - Das Kennzeichen 01 wird durch den Wert des Pragmas LEITADRESSE ersetzt (Standard 01).
// Die Puffer fuer .dmp und .test behalten die Adresse; sie werden von dieser Funktion nicht veraendert.
// Das Listing (STDOUT und .dmp) erhaelt das Kennzeichen xx in schreibeListingX (ersetzeKennzeichen01).
static void schreibeObjZeile(FILE *objFile, const char *zeile) {
    const char *p = zeile;
    while (*p == ' ') p++;

    // Adreßspalte "<oktalzahl>:" samt folgenden Leerzeichen ueberspringen
    const char *q = p;
    while (*q >= '0' && *q <= '7') q++;
    if (q > p && *q == ':') {
        p = q + 1;
        while (*p == ' ') p++;
    }

    if (p[0] == '0' && p[1] == '1' && (p[2] == ' ' || p[2] == '\0')) {
        fprintf(objFile, "%02d%s.\n", leitadresseKennzeichen, p + 2);
    } else {
        fprintf(objFile, "%s.\n", p);
    }
}

// Auflösen des dt Befehls
int zFlagErz = 0; // Zustandsflag
int textPC = 0;   // Trommeladresse des naechsten von erzeugenText ausgegebenen Wortes
void erzeugenText(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int no_kbgb ,int iii) {
    int ersteAusgabe = 1; // Flag, um die erste Ausgabe zu erkennen
    char *zeichenfolge = operand;
    int missingChar;
    char buffer[32];

    // Entferne die umschließenden \-Zeichen
    if (zeichenfolge[0] == '\\') zeichenfolge++;
    if (zeichenfolge[strlen(zeichenfolge) - 1] == '\\') zeichenfolge[strlen(zeichenfolge) - 1] = '\0';

    if (isValueInTable(zeichenfolge, outUmschluesselungsTable, OUT_SIZE, &missingChar) == 0) {
        is_error3 = 1;
        printHell = 1;
        PRINT_FEHLER("dt Operand enthält unzulässige Zeichen an Position: %i.", missingChar);
        return;
    }

    // Jedes Wort (auch ein Umschalt-Praefix 0570/1170) belegt genau eine
    // Trommeladresse, beginnend bei textPC. Die Adresse wird pro Zeile in
    // .adr/.adrValid gemerkt, damit erzeugeTestDatei sie verwenden kann.
    void ausgabeWort(const char *wort) {
        schreibeObjZeile(machineCodeFile, wort);
        lineElementsX *z = &lineAsmAufgeloestX[lineCountAsmAufgeloestX];
        if (ersteAusgabe == 1) {
            fprintf(hilfsFile, "%s\n", line);
            strcpy(z->sp0, wort);
            strcpy(z->sp1, lineAsmAufgeloest[iii].sp1);
            strcpy(z->sp2, lineAsmAufgeloest[iii].sp2);
            strcpy(z->sp3, lineAsmAufgeloest[iii].sp3);
            strcpy(z->sp4, lineAsmAufgeloest[iii].sp4);
            ersteAusgabe = 0;
        } else {
            fprintf(hilfsFile, "%s\n", "; ");
            strcpy(z->sp0, wort);
            strcpy(z->sp1, "; ");
            strcpy(z->sp2, "");
            strcpy(z->sp3, "");
            strcpy(z->sp4, "");
        }
        z->adr = textPC++;
        z->adrValid = 1;
        lineCountAsmAufgeloestX++;
    }

    // Zeichenweise Verarbeitung
    for (size_t i = 0; i < strlen(zeichenfolge); i++) {
        int asciiWert = (int) zeichenfolge[i];
        int spalte = 0;       // 2 oder 3: in welcher Tabellenspalte gefunden
        int code = 0;         // Oktalcode aus Spalte 1
        for (size_t j = 0; j < OUT_SIZE; j++) {
            if (outUmschluesselungsTable[j].spalte2 == asciiWert) { spalte = 2; code = outUmschluesselungsTable[j].spalte1; break; }
        }
        if (!spalte) {
            for (size_t j = 0; j < OUT_SIZE; j++) {
                if (outUmschluesselungsTable[j].spalte3 == asciiWert) { spalte = 3; code = outUmschluesselungsTable[j].spalte1; break; }
            }
        }
        if (!spalte) continue;

        int steuer = (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10);
        int zustandPasst = (spalte == 2) ? (zFlagErz == 1) : (zFlagErz == 0);
        int direkt = steuer || ((zustandPasst || (no_kbgb == 1)) && !((no_kbgb == 2) && (i == 0)));

        if (!direkt) {
            if (no_kbgb != 1) {
                sprintf(buffer, "      00 %04o 030", (spalte == 2) ? 0570 : 01170);
                ausgabeWort(buffer);
            }
            zFlagErz = (spalte == 2) ? 1 : 0;
        }
        sprintf(buffer, "      00 %04o 030", code);
        ausgabeWort(buffer);
    }
}

// ---------

int zFlag = 0; // Unterscheidung 2. Spalte -- 3. Spalte
int zaehleText(char operand[], int no_kbgb) {
    int zaehler = 0; 
    char *zeichenfolge = operand;

    if (zeichenfolge[0] == '\\') zeichenfolge++;
    if (zeichenfolge[strlen(zeichenfolge) - 1] == '\\') zeichenfolge[strlen(zeichenfolge) - 1] = '\0';

    for (size_t i = 0; i < strlen(zeichenfolge); i++) {
        char zeichen = zeichenfolge[i];
        int asciiWert = (int)zeichen;

        // Suche in der zweiten Spalte der Tabelle
        int gefunden = 0;
        for (size_t j = 0; j < OUT_SIZE; j++) {
            if (outUmschluesselungsTable[j].spalte2 == asciiWert) {
                // Treffer in der zweiten Spalte   
                if (  ( 
                        (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10) 
                        )
                        || 
                        ((
                        (zFlag == 1) || (no_kbgb == 1)  //|| ((no_kbgb == 0) && (j == 0 ))
                        ) 
                        && 
                        ! ( (no_kbgb == 2) && (i == 0 ) ) 
                        ) 
                    ) {
                    zaehler++; // Ein fprintf
                } else {
                    if ( no_kbgb != 1) {
                       zaehler++; // Zwei fprintfs
                    }
                    zaehler++; 
                    zFlag = 1; 
                }
                gefunden = 1;
                break;
            }
        }

        if (!gefunden) {
            // Suche in der dritten Spalte der Tabelle
            for (size_t j = 0; j < OUT_SIZE; j++) {
                if (outUmschluesselungsTable[j].spalte3 == asciiWert) {
                    // Treffer in der dritten Spalte
                    if (  ( 
                            (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10) 
                          )
                          || 
                          ((
                            (zFlag == 0) || (no_kbgb == 1) //|| ((no_kbgb == 0) && (j == 0 ))
                          ) 
                          && 
                          ! ( (no_kbgb == 2) && (i == 0 ) )
                          )  
                       ) {
                        zaehler++;
                    } else {
                        if ( no_kbgb != 1) {
                            zaehler++; // Zwei fprintfs
                        }
                        zaehler++; 
                        zFlag = 0; 
                    }
                    gefunden = 1;
                    break;
                }
            }
        }
    }

    return zaehler; 
}


typedef struct {
    char *symbol; 
    int octalValue; 
} dzZeichen;

dzZeichen dzTable[] = {
    {"$wrzl",  02720},
    {"$sm",    02720},
    {"$inkb",  01170},
    {"$ingb",   0570},
    {"$irrz",  03770},
    {"$irrs",   0160},
    {"$trans", 01770},
    {"$bm",    03520},
    {"$vorl",     00},
    {"$irrb",   0760},
    {"$tab",   01550},
    {"$zr",     0320},
    {"$wr",    01120},
    {"%",      01740},
    {":",       0150},
    {"+",       0400},
    {"`",      01600},
    {"/",      01410},
    {",",      01530},
    {".",       0730},
    {"-",      01000}
};

// Anzahl der Einträge in der Tabelle
const int dzCount = sizeof(dzTable) / sizeof(dzTable[0]);

void dzAuswertung(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii) {
    char buffer[32];

    for (int i = 0; i < dzCount; i++) {
        // Prüfe, ob der Operand in der ersten Spalte der Tabelle enthalten ist
        if (strcmp(operand, dzTable[i].symbol) == 0) {
            // Zweite Spalte ausgeben
            sprintf(buffer, "      00 %04o 030", dzTable[i].octalValue);
            schreibeObjZeile(machineCodeFile, buffer);

            fprintf(hilfsFile, "%s\n", line);
            copyAndIncrementLineElementsX(iii, buffer);
            // Adresse fuer die .test-Datei merken (wie bei dt/dto/dtm): die
            // dz-Zeile traegt in sp0 keine Adresse. textPC wird vom Aufrufer gesetzt.
            lineAsmAufgeloestX[lineCountAsmAufgeloestX - 1].adr = textPC;
            lineAsmAufgeloestX[lineCountAsmAufgeloestX - 1].adrValid = 1;
            return; // Funktion beenden, da der Eintrag gefunden wurde
        }
    }
    is_error3=1;
    printHell = 1;
    PRINT_FEHLER ("dz Operand %s nicht gültig.", operand);
}

int zaehleBackslashes(const char *templine) {
    int count = 0;
    for (size_t i = 0; i < strlen(templine); i++) {
        if (templine[i] == '\\') {
            count++;
        }
    }
    return count; 
}

// replaceSubstring sucht in line nach dem Substring operand und ersetzt ihn durch den Octal-Wert von dwValue
void replaceSubstring(char *line, const char *operand, unsigned int dwValue) {
    char tempLine[1024]; 
    char *pos = strstr(line, operand); 

    if (pos) {
        strncpy(tempLine, line, pos - line);
        tempLine[pos - line] = '\0'; 
        sprintf(tempLine + strlen(tempLine), "%05o", dwValue);
        strcat(tempLine, pos + strlen(operand));
        strcpy(line, tempLine);
    }
}

void outAdressError(const char *label, char *typ, char *text) {
    char line1[256];
    char xline[1024];
    sprintf(line1, "bei Operand: %s %s %s", label, typ, text);
    sprintf(xline, "%s%s%s",_weiss, line1,_normal);
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, xline);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");    
    lineCountAsmAufgeloestX++; 


}
// ----------------------

// Belegungspruefung (Pass 3): Jedes durch Befehle oder Daten (dw, da, dbn, dt, dto, dtm, dz)
// tatsaechlich beschriebene Wort der Trommel wird genau einmal belegt. Ueberschneidet sich die
// sequentielle Speicherbelegung mit einem frueher belegten Bereich (z.B. Programm laeuft in einen
// mit equ weiter hinten angelegten Datenbereich, oder ein spaeteres equ springt zurueck), ist das
// ein Fehler. `db` reserviert nur und beschreibt keine Zellen: es wird nicht geprueft.
#define BELEGUNG_ADRESSEN 010000   // 4 Oktalstellen
static int belegtVonZeile[BELEGUNG_ADRESSEN];   // 0 = frei, sonst Index in lineAsmAufgeloest + 1

static void meldeBelegungskonflikt(int adresse, int alteZeile, int neueZeile) {
    char text[1024];
    char alt[300];
    char neu[300];
    snprintf(alt, sizeof(alt), "%.60s %.20s %.60s", lineAsmAufgeloest[alteZeile].sp1, lineAsmAufgeloest[alteZeile].sp2, lineAsmAufgeloest[alteZeile].sp3);
    snprintf(neu, sizeof(neu), "%.60s %.20s %.60s", lineAsmAufgeloest[neueZeile].sp1, lineAsmAufgeloest[neueZeile].sp2, lineAsmAufgeloest[neueZeile].sp3);
    snprintf(text, sizeof(text), ";%s*** 3 Fehler%s: Adresse %04o doppelt belegt: \"%s\" ueberschneidet sich mit \"%s\".",
             _violett, _normal, adresse, neu, alt);
    PRINT_FEHLER("Adresse %04o doppelt belegt: \"%s\" ueberschneidet sich mit \"%s\".", adresse, neu, alt);
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, text);
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    strcpy(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");
    lineCountAsmAufgeloestX++;
    is_error3 = 1;
}

// Belegt die Worte [von, bis) fuer die Zeile `zeile`; meldet pro Zeile hoechstens einen Konflikt.
static void belegeAdressen(int von, int bis, int zeile) {
    int gemeldet = 0;
    for (int a = von; a < bis; a++) {
        if (a < 0 || a >= BELEGUNG_ADRESSEN) {
            if (!gemeldet) {
                PRINT_FEHLER("Adresse %04o liegt ausserhalb der Trommel (0000-7777).", a);
                is_error3 = 1;
                gemeldet = 1;
            }
            break;
        }
        if (belegtVonZeile[a] != 0) {
            if (!gemeldet) {
                meldeBelegungskonflikt(a, belegtVonZeile[a] - 1, zeile);
                gemeldet = 1;
            }
        } else {
            belegtVonZeile[a] = zeile + 1;
        }
    }
}

// ----------------------

// Erzeugt die .test-Datei direkt aus den strukturierten Listing-Zeilen
// (denselben Daten, aus denen auch die .dmp-Datei erzeugt wird - siehe
// printFormattedAsmListingX). Jede Zeile hat sp0 = "<adresse>: <K1> [<K2>] [<Wert>]",
// sp1 = Label, sp2 = Mnemonic, sp3 = Operand, sp4 = Kommentar.
// Es werden nur Zeilen mit K1 (Spalte 2) == "00" oder "01" berücksichtigt.
// Aus sp0 (Spalten 1,3,4) werden alle Ziffern eingesammelt und linksbündig
// mit Nullen auf 11 Stellen aufgefüllt. Alles ab Spalte 6 (Mnemonic, Operand,
// Kommentar) wird - falls vorhanden - als "# ..."-Kommentar angehängt.
void erzeugeTestDatei(lineElementsX lineAsmAufgeloest[], int lineCountAsmAufgeloest, const char *testFileName) {
    FILE *testFile = fopen(testFileName, "w");
    if (!testFile) {
        PRINT_FEHLER("Testdatei %s konnte nicht angelegt werden.", testFileName);
        return;
    }

    // Kopfzeilen (Platzhalter fuer die Testbeschreibung, s. C8205-Interpreter-Durchfuehrung_eines_Tests.md)
    fprintf(testFile, "Trommeldatei:\n");
    fprintf(testFile, "#DOK-0001\n");
    fprintf(testFile, "#SPEI-0001 0000-0000\n");
    fprintf(testFile, "#PROT STUFE=2\n");

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        const char *sp0 = lineAsmAufgeloest[i].sp0;

        char adresse[64] = "";
        char k1[16] = "";
        int pos = 0;
        int adrZeile = lineAsmAufgeloest[i].adrValid;

        if (adrZeile) {
            // dt/dto/dtm-Zeile: Adresse steht nicht in sp0, sondern in .adr
            snprintf(adresse, sizeof(adresse), "%04o", lineAsmAufgeloest[i].adr);
            if (sscanf(sp0, "%15s%n", k1, &pos) != 1) {
                continue;
            }
        } else if (sscanf(sp0, "%63[^:]:%15s%n", adresse, k1, &pos) != 2) {
            continue; // keine "<adresse>: <K1> ..."-Zeile (z.B. equ-Zeile, Fehlerzeile ohne Adresse)
        }

        // Nullwort: pass3 schreibt "dw 0" als "<adr>: 0" (nur "0", ohne K1/K2/Wert, s. .dmp/.obj).
        // Diese Zeile gehoert ebenfalls in die .test-Datei (als Wort 00000000000).
        int nullwort = (strcmp(k1, "0") == 0);

        if (!nullwort && strcmp(k1, "00") != 0 && strcmp(k1, "01") != 0) {
            continue; // nur Spalte 2 == 00 oder 01 (oder Nullwort "0") verwenden
        }

        // Verbleibende Ziffern aus sp0 (Spalten 3/4) einsammeln - sp0 enthält
        // ausschließlich Adresse/K1/K2/Wert, also keine Gefahr, versehentlich
        // Ziffern aus einem Label wie "l0001" mit aufzunehmen.
        char ziffern[64] = "";
        int zIdx = 0;
        for (const char *p = sp0 + pos; *p != '\0'; p++) {
            if (isdigit((unsigned char)*p)) {
                if (zIdx < (int)sizeof(ziffern) - 1) {
                    ziffern[zIdx++] = *p;
                }
            }
        }
        ziffern[zIdx] = '\0';

        if (nullwort && zIdx == 0) {
            ziffern[0] = '0';
            ziffern[1] = '\0';
            zIdx = 1;
        }

        if (zIdx == 0 || zIdx > 11) {
            continue; // keine verwertbaren Ziffern bzw. unerwartet lang -> überspringen
        }

        fprintf(testFile, "%s: ", adresse);
        for (int pad = 0; pad < 11 - zIdx; pad++) {
            fputc('0', testFile);
        }
        fprintf(testFile, "%s", ziffern);

        // Ab "Spalte 6" (Mnemonic, Operand, Kommentar) - und, sofern vorhanden,
        // auch das Label - als lesbaren Kommentar anhängen.
        char kommentar[600] = "";
        const char *teile[4] = { lineAsmAufgeloest[i].sp1, lineAsmAufgeloest[i].sp2,
                                  lineAsmAufgeloest[i].sp3, lineAsmAufgeloest[i].sp4 };
        for (int t = 0; t < 4; t++) {
            const char *s = teile[t];
            while (*s == ' ' || *s == '\t') s++;
            size_t len = strlen(s);
            while (len > 0 && (s[len-1] == ' ' || s[len-1] == '\t' || s[len-1] == '\n' || s[len-1] == '\r')) len--;
            if (len == 0) continue;
            if (kommentar[0] != '\0') strncat(kommentar, " ", sizeof(kommentar) - strlen(kommentar) - 1);
            strncat(kommentar, s, (len < sizeof(kommentar) - strlen(kommentar) - 1) ? len : sizeof(kommentar) - strlen(kommentar) - 1);
        }
        if (kommentar[0] != '\0' && strcmp(kommentar, ";") != 0) {
            fprintf(testFile, " # %s", kommentar);
        }
        fprintf(testFile, "\n");
    }

    // Fusszeilen (Platzhalter fuer die Tastenfolge)
    fprintf(testFile, "Tastenfolge:\n");
    fprintf(testFile, "H G R\n");

    fclose(testFile);
}

// ----------------------

void pass3(char *machineCodeFileName, char *hilfsFileName, char *dmpFileName, char *testFileName) {
    printf("Erzeuge Kennzeichen-Befehle in Objektdatei %s\n\n", machineCodeFileName);

    FILE *machineCodeFile = fopen(machineCodeFileName, "w");  //.obj
    FILE *hilfsFile = fopen(hilfsFileName, "w");
    FILE *dmpFile = fopen(dmpFileName, "w");  //.dmp

    line_ausgegeben=0;
    int errorFlag=0;
    int relativadresse=0;
    int programCounter = 0;
    int raAdr=0;
    const char semikolon = ';';
    char buffer[512];

    memset(belegtVonZeile, 0, sizeof(belegtVonZeile));

    zFlag = 0; // Unterscheidung 2. Spalte -- 3. Spalte

    const char *dreua[] = { "251", "271", "030", "032", "034", "036", "132", "134", "136", "031", "033", "035", "037", "131", "133", "135", "137"};
    #define DREUA_SIZE (sizeof(dreua) / sizeof(dreua[0]))

    // Operationscode-Sonderbehandlungs-Tabelle
    int istInDreua(const char *operationCode) {
        for (size_t i = 0; i < DREUA_SIZE; i++) {
            if (strcmp(operationCode, dreua[i]) == 0) {
                return 1;  
            }
        }
        return 0; 
    }


    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;

    // Funktion zum Trimmen eines Strings (erstellt nur eine Pointer-Referenz)
    char* getTrimmed(const char *str) {
        while (*str && isspace(*str)) str++; // Entfernt führende Leerzeichen
        const char *end = str + strlen(str) - 1;
        while (end > str && isspace(*end)) end--; // Entfernt nachfolgende Leerzeichen
        static char trimmed[256]; // Statische Variable für Ausgabe
        size_t len = end - str + 1;
        strncpy(trimmed, str, len);
        trimmed[len] = '\0';  // Null-Terminierung nicht vergessen
        return trimmed;
    }

    // Anwendung ohne direkte Änderung der Originalwerte
    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        const char *trimmed1 = getTrimmed(lineAsmAufgeloest[i].sp1);
        const char *trimmed2 = getTrimmed(lineAsmAufgeloest[i].sp2);
        const char *trimmed3 = getTrimmed(lineAsmAufgeloest[i].sp3);
        if (*trimmed1 != ';' && *trimmed1 != '#' && *trimmed1 != '$' &&
            *trimmed1 != '*' && *trimmed1 != '&') {
            int len1 = strlen(trimmed1) + 2;
            if (len1 > maxWidth1) maxWidth1 = len1;
        }
        int len2 = strlen(trimmed2) + 2;
        int len3 = strlen(trimmed3) + 2;
        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    char formatString[256]; 
    snprintf(formatString, sizeof(formatString), "%%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    // für die c82asm - Ausgabe
    lineCountAsmAufgeloestX = 0;
    lineElementsX fstrct;

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        char textkonst[1024]="";
        

        // übergehen
        if (  ((lineAsmAufgeloest[i].sp1[0] == ';') || (lineAsmAufgeloest[i].sp1[0] == '#') || (lineAsmAufgeloest[i].sp1[0] == '$')  ||
                (lineAsmAufgeloest[i].sp1[0] == '&') || (strstr(lineAsmAufgeloest[i].sp1, "***") != NULL)   ) ) {
            continue;
        } 
        // Leerzeile
        if (lineAsmAufgeloest[i].sp1[0] == '\0' && lineAsmAufgeloest[i].sp2[0] == '\0' &&
            lineAsmAufgeloest[i].sp3[0] == '\0' && lineAsmAufgeloest[i].sp4[0] == '\0') 
        {
            continue;
        }



        errorFlag=0;
        int pcVorher = programCounter;   // fuer die Belegungspruefung

        char label[256];     
        char operation[256]; 
        char kommentar[256]; 
        char operand[256];
        char line[MAX_LINE_LENGTH];

        removeNewlines(lineAsmAufgeloest[i].sp1) ;
        removeNewlines(lineAsmAufgeloest[i].sp2) ;
        removeNewlines(lineAsmAufgeloest[i].sp3) ;
        removeNewlines(lineAsmAufgeloest[i].sp4) ;

        strcpy(label, lineAsmAufgeloest[i].sp1 );
        strcpy(operation, lineAsmAufgeloest[i].sp2 );
        strcpy(operand, lineAsmAufgeloest[i].sp3 );
        strcpy(kommentar, lineAsmAufgeloest[i].sp4 );

        int zaehleBackslaShes = zaehleBackslashes(lineAsmAufgeloest[i].sp3);

        if (zaehleBackslaShes == 2) {
            extractBackslashContent(operand,textkonst);
/**    
            char *start = strchr(operand, '\\');  
            char *end = strrchr(operand, '\\');

            if (start && end && start != end) {
                start++;  // Nach dem ersten Backslash beginnen
                size_t length = end - start;

                strncpy(operand, start, length);
                operand[length] = '\0';  // Null-Terminierung nicht vergessen!
                strcpy(textkonst,operand);
            }
*/
        } 

        char *trimmed = label;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen
        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*'|| *trimmed == '&') {
            sprintf(line, "%s %s %s %s", 
                    lineAsmAufgeloest[i].sp1, 
                    lineAsmAufgeloest[i].sp2, 
                    lineAsmAufgeloest[i].sp3, 
                    lineAsmAufgeloest[i].sp4);
        } else {
            sprintf(line, formatString, 
                    lineAsmAufgeloest[i].sp1, 
                    lineAsmAufgeloest[i].sp2, 
                    lineAsmAufgeloest[i].sp3, 
                    lineAsmAufgeloest[i].sp4);
        }


        line[strcspn(line, "\r")] = '\0';
        removeNewlines(line);
 
        if (strlen(operation) > 0) {
            if (strcmp(operation, "start") == 0) {
                if ( startAdresse != 0) {
                    sprintf(buffer, "      21 0000 %04o", startAdresse);
                    schreibeObjZeile(machineCodeFile, buffer);
                    copyAndIncrementLineElementsX(i,buffer);
                    fprintf(hilfsFile,"%s\n", line);
                }
                
            } else if (strstr(operation, "equ") != NULL) {
                raAdr=relativadresse;               
                unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", programCounter , &absolutadresse);
                if (errorFlag == 0) {
                    relativadresse = dwValue;
                    if (strcmp(operation, "equ100") == 0) {
                        relativadresse = (relativadresse + 0100 - 1) & ~(0100 - 1); // Aufrunden auf nächste 0100
                    } else if (strcmp(operation, "equ40") == 0) {
                        relativadresse = (relativadresse + 0040 - 1) & ~(0040 - 1); // Aufrunden auf nächste 0040
                    } else if (strcmp(operation, "equ10") == 0) {
                        relativadresse = (relativadresse + 0010 - 1) & ~(0010 - 1); // Aufrunden auf nächste 0010
                    }                
                    sprintf(buffer, "      20 0000 %04o", relativadresse);
                    schreibeObjZeile(machineCodeFile, buffer);
                    replaceSubstring(line, operand, relativadresse);
                    fprintf(hilfsFile,"%s\n", line);
                    replaceSubstring(lineAsmAufgeloest[i].sp3, operand, relativadresse);
                    copyAndIncrementLineElementsX(i,buffer);                    
                    programCounter=relativadresse;
                } else {
                    printHell = 1;
                    is_error3=1;
                }

            } else if (strcmp(operation, "abs") == 0) {
                raAdr=relativadresse;
                unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", 0 , &absolutadresse);  // nur zweks Prüfung
                (void)dwValue; //Warnung unterdrücken
                if ( errorFlag != 0) {is_error3=1; printHell = 1; }

            } else if (strcmp(operation, "dw") == 0) {
                if (strspn(operand, "-0123456789") == strlen(operand) && operand[0] != '0' && !(operand[0] == '-' && operand[1] == '0') && strchr(operand + 1, '-') == NULL) {
                    char octalString[MAX_LINE_LENGTH];
                    if ( (operand[0] == '-') || (operand[0] == '+') ) {
                        // Falls das erste Zeichen ein '-', prüfe das zweite Zeichen
                        if (operand[1] == '0') {
                            snprintf(octalString, sizeof(octalString), "%012lo", (unsigned long int) strtol(operand, NULL, 8));
                        } else {
                            snprintf(octalString, sizeof(octalString), "%ld", (unsigned long int) strtol(operand, NULL, 10));
                        }
                    } else {
                        // Falls kein '-+', prüfe das erste Zeichen direkt
                        if (operand[0] == '0') {
                            snprintf(octalString, sizeof(octalString), "%012lo", (unsigned long int) strtol(operand, NULL, 8));
                        } else {
                            snprintf(octalString, sizeof(octalString), "%ld", (unsigned long int) strtol(operand, NULL, 10));
                        }
                    }
                    strcpy(operand, octalString); 
                }
                unsigned long long dwValue = evaluateValue(operand, &errorFlag);
                // Negative Werte als 33-Bit-Wort (11 Oktalziffern) im Zweierkomplement ausgeben.
                // Falls die C8205 negative Zahlen anders darstellt, nur diese Zeile aendern.
                // Zulaessiger Bereich: -2^32 ... 2^33-1 (33-Bit-Wort, vorzeichenlos bzw. Zweierkomplement).
                if (errorFlag == 0) {
                    long long dwWert = (long long)dwValue;
                    if (dwWert < -4294967296LL || dwWert > 0x1FFFFFFFFLL) {
                        errorFlag = 1;   // passt nicht in ein Maschinenwort
                    } else if (dwWert < 0) {
                        dwValue &= 0x1FFFFFFFFULL;
                    }
                }

                if (errorFlag == 0 ) {
                    if ( dwValue == 0) {
                        sprintf(buffer, "%04o: 0",programCounter);
                        schreibeObjZeile(machineCodeFile, buffer);

                    } else {
                        sprintf(buffer, "%04o: 00 %011llo", programCounter,dwValue);
                        schreibeObjZeile(machineCodeFile, buffer);
                    }
                    fprintf(hilfsFile,"%s\n", line);
                    copyAndIncrementLineElementsX(i,buffer); 
                } else {
                    sprintf(buffer, "%04o: %sEE%s %04o %s   ", programCounter, _violett, _normal, 0, operand); // Fehlerausgabe
                    copyAndIncrementLineElementsX (i,buffer);
                    if (evaluateValueGrund != NULL) {
                        // Symbolfehler (Doku 3.3): Grund an die Standardmeldung anhaengen
                        char dwMeldung[512];
                        snprintf(dwMeldung, sizeof(dwMeldung), " ist ungültig (%s)", evaluateValueGrund);
                        outAdressError(operand, "Operand", dwMeldung);
                    } else {
                        outAdressError(operand, "Operand", " ist ungültig");
                    }
                    printHell = 1;
                    is_error3=1;
                }
                programCounter++;

            } else if (strcmp(operation, "da") == 0) {
              char adrMeldung[512];
              if (!pruefeAdressausdruck(operand, adrMeldung, sizeof(adrMeldung))) {
                sprintf(buffer, "%04o: %sEE%s %04o %s   ", programCounter, _violett, _normal, 0, operand); // Fehlerausgabe
                copyAndIncrementLineElementsX (i,buffer);
                outAdressError(operand, "Operand", adrMeldung);
                printHell = 1;
                is_error3=1;
                programCounter++;
              } else {
                // Frueher wurde hier eine reine Dezimalzahl in eine Oktalzeichenkette umgewandelt und danach von
                // evaluateAddress wieder als Dezimalzahl gelesen (da 10 ergab Adresse 12). evaluateAddress versteht
                // Dezimal- und Oktalzahlen selbst; die Umwandlung entfaellt.
                raAdr=relativadresse;
                unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", programCounter, &absolutadresse );
                if (errorFlag == 0 && dwValue > 07777) {
                    // Wertebereich der Adresse (negative Werte erscheinen hier als sehr grosse Zahl)
                    sprintf(buffer, "%04o: %sEE%s %04o %s   ", programCounter, _violett, _normal, 0, operand); // Fehlerausgabe
                    copyAndIncrementLineElementsX (i,buffer);
                    outAdressError(operand, "Operand", "Der Adressausdruck liegt außerhalb des Bereichs 00000 bis 07777.");
                    printHell = 1;
                    is_error3=1;
                } else if (errorFlag == 0 ) {
                    if ( absolutadresse != 0 ) { 
                        sprintf(buffer, "%04o: 00 %04o",programCounter,dwValue<<9);
                        schreibeObjZeile(machineCodeFile, buffer);
                    } else { 
                        sprintf(buffer, "%04o: 01 %04o",programCounter,dwValue<<9);
                        schreibeObjZeile(machineCodeFile, buffer);
                    }
                    fprintf(hilfsFile,"%s\n", line);
                    copyAndIncrementLineElementsX(i,buffer); 
                } else {
                    printAdressError(operand, "Adresse (1)", " ist ungültig", line);
                    printHell = 1;
                    is_error3=1;
                }
                programCounter++;
              }

            } else if (strcmp(operation, "db") == 0) {
                // Bereich ohne initialisierung definieren
                if (operand) {
                    int byteCount;
                    if (operand[0] == '0') {
                        byteCount = strtol(operand, NULL, 8);
                    } else {
                        byteCount = strtol(operand, NULL, 10);
                    }
                    programCounter += byteCount;
                    sprintf(buffer, "%04o: 20 %04o", programCounter-byteCount,programCounter);
                    schreibeObjZeile(machineCodeFile, buffer);
                    fprintf(hilfsFile,"%s\n",line);
                    copyAndIncrementLineElementsX(i,buffer); 
                } else {
                    // eigentlich ein fehlerfall, der in pass2 gemeldet wurde
                }
            } else if (strcmp(operation, "dbn") == 0) {
                // Bereich auf Null definieren
                if (operand) {
                    sprintf(buffer, "%04o: 00 0",programCounter);
                    schreibeObjZeile(machineCodeFile, buffer);
                    fprintf(hilfsFile,"%s\n",line);
                    copyAndIncrementLineElementsX(i,buffer); 
                    int byteCount;
                    if (operand[0] == '0') {
                        byteCount = strtol(operand, NULL, 8);
                    } else {
                        byteCount = strtol(operand, NULL, 10);
                    }
                    // Folgeworte des Bereichs: eigene Schleifenvariable k (das aeussere i ist der
                    // Index der Quelltextzeile) und aufsteigende Adressen.
                    for (int k = 0; k < byteCount - 1; k++) {
                        sprintf(buffer, "%04o: 00 0", programCounter + k + 1);
                        schreibeObjZeile(machineCodeFile, buffer);
                        fprintf(hilfsFile, "\n");
                        copyAndIncrementLineElementsSpOnly(i,buffer); 
                    }
                    programCounter += byteCount;
                } else {
                     // eigentlich ein Fehlerfall, der in pass2 gemeldet wurde
                }
            } else if ( (strcmp(operation, "dt") == 0) ) {
                if ( zaehleBackslaShes != 2 ) { 
                   textPC = programCounter;
                   erzeugenText(operand, machineCodeFile,hilfsFile, line, 0, i);
                   if (operand) {
                       programCounter += zaehleText(operand,0);
                   }
                } else { 
                   textPC = programCounter;
                   erzeugenText(textkonst, machineCodeFile,hilfsFile, line, 0, i);
                   if (textkonst[0] != '\0') {
                       programCounter += zaehleText(textkonst,0);
                   }
                }
            } else if ( (strcmp(operation, "dto") == 0) ) {
                if ( zaehleBackslaShes != 2 ) { 
                   textPC = programCounter;
                   erzeugenText(operand, machineCodeFile,hilfsFile, line, 1, i);
                   if (operand) {
                       programCounter += zaehleText(operand,1);
                   }
                } else { 
                   textPC = programCounter;
                   erzeugenText(textkonst, machineCodeFile,hilfsFile, line, 1, i);
                   if (textkonst[0] != '\0') {
                       programCounter += zaehleText(textkonst,1);
                   }
                }
            } else if ( (strcmp(operation, "dtm") == 0) ) {
                if ( zaehleBackslaShes != 2 ) { 
                   textPC = programCounter;
                   erzeugenText(operand, machineCodeFile,hilfsFile, line, 2, i);
                   if (operand) {
                       programCounter += zaehleText(operand,2);
                   }
                } else { 
                   textPC = programCounter;
                   erzeugenText(textkonst, machineCodeFile,hilfsFile, line, 2, i);
                   if (textkonst[0] != '\0') {
                       programCounter += zaehleText(textkonst,2);
                   }
                }
            } else if (strcmp(operation, "dz") == 0) {
                textPC = programCounter;
                dzAuswertung(operand, machineCodeFile,hilfsFile,line, i);
                programCounter++;
            } else if (strcmp(operation, "end") == 0) {
                // nix zu tun.
            } else {
                // Normale Anweisungen mit Kennzeichen "01"

                // operation --> operationCode (geprüft)
                char *operationCode = getOperationCode(operation);
                if (istInDreua(operationCode)) {
                    // Operationen, deren Adreßteil nicht verändert werden darf, z.B. 030
                    if (operand != NULL && operand != 0) {  // != NULL und beginnt nicht mit Semikolon
                        raAdr=0;
                        unsigned int address = evaluateAddress(operand, "", &errorFlag, &raAdr, "", programCounter, &absolutadresse);
                        if (errorFlag == 0 ) {
                            sprintf(buffer, "%04o: 00 %04o %s", programCounter, address, operationCode);
                            schreibeObjZeile(machineCodeFile, buffer);

                            fprintf(hilfsFile,"%s\n", line);
                            copyAndIncrementLineElementsX(i,buffer); 
                        } else {
                            printAdressError(operand, "Adresse (2)", " ist ungültig", line);
                            is_error3 = 1;
                            printHell = 1;
                        }
                    } else {
                        sprintf(buffer, "%04o: 00 %s", programCounter, operationCode);
                        schreibeObjZeile(machineCodeFile, buffer);
                        fprintf(hilfsFile,"%s\n", line);
                        copyAndIncrementLineElementsX(i,buffer); 
                    }
                } else if (strcmp(operationCode, "XXX") != 0)  { 
                     if (operand != NULL && operand != 0 && operand[0] != semikolon) { // != NULL und beginnt nicht mit Semikolon
                        raAdr=relativadresse;
                        unsigned int address = evaluateAddress(operand, "", &errorFlag, &raAdr, "", programCounter, &absolutadresse);
                        if (errorFlag == 0) {
                            if ( absolutadresse != 0 ) { 
                                sprintf(buffer, "%04o: 00 %04o %s", programCounter, address, operationCode);
                                schreibeObjZeile(machineCodeFile, buffer);
                            } else {
                                sprintf(buffer, "%04o: 01 %04o %s", programCounter, address, operationCode);
                                schreibeObjZeile(machineCodeFile, buffer);
                            }
                            fprintf(hilfsFile,"%s\n", line);
                            copyAndIncrementLineElementsX(i,buffer); 
                        } else {
                            sprintf(buffer, "%04o: %sEE%s %04o %s   ", programCounter, _violett, _normal, 0, operationCode); // Fehlerausgabe
                            copyAndIncrementLineElementsX (i,buffer);
                            outAdressError(operand, "Adresse (3)", " ist ungültig");
                            is_error3 = 1;
                            printHell = 1;
                        }
                    } else {
                        sprintf(buffer, "%04o: 01 %s", programCounter, operationCode);
                        schreibeObjZeile(machineCodeFile, buffer);
                        fprintf(hilfsFile,"%s\n", line);
                        copyAndIncrementLineElementsX(i,buffer); 
                    }
                } else {
                    sprintf(buffer, "%04o: %sEE%s %04o %s   ", programCounter, _violett, _normal, 0, operationCode); // Fehlerausgabe
                    copyAndIncrementLineElementsX (i,buffer);
                    outAdressError(operation, "Operationscode", " ist ungültig");
                    is_error3 = 1;
                    printHell = 1;
                }
                programCounter++;
            }
        }

        // Belegungspruefung: equ/start setzen nur den Zaehler, abs/end/db belegen keine Zelle.
        if ( programCounter > pcVorher
             && strstr(operation, "equ") == NULL
             && strcmp(operation, "start") != 0
             && strcmp(operation, "abs") != 0
             && strcmp(operation, "end") != 0
             && strcmp(operation, "db") != 0 ) {
            belegeAdressen(pcVorher, programCounter, i);
        }

        printHell = 0;   
    }
    printFormattedAsmListingX(lineAsmAufgeloestX, lineCountAsmAufgeloestX, dmpFile);
    erzeugeTestDatei(lineAsmAufgeloestX, lineCountAsmAufgeloestX, testFileName);

    fprintf(machineCodeFile, "/\n"); 
    fclose(machineCodeFile);
    fclose(hilfsFile);
    if (dmpFile) fclose(dmpFile);

}

// ------------------------------------------

void printUsage(const char *programName) {
    printf("Usage: %s -p Projektverzeichnis -s Quellcode-Datei\n", programName);
}
void greetings() {
    printf("C8205 Assembler C82aas Version 1.00\n");
}

char projektVerzeichnis[512] = {0};
unsigned int oktalzahl = 0;

char quellcodeDatei[512] = "";
char inputFileName[1024] = "";
char logFileName[1024] = "";
char machineCodeFileName[1024] = "";
char hilfsFileName[1024] = "";
char symFileName[1024] = "";
char testFileName[1024] = "";
char dmpFileName[1024] = "";


// Funktion, um sicherzustellen, dass eine Datei eine Endung hat
void ensureFileExtension(char *fileName, const char *defaultExtension, size_t maxSize) {
    if (strchr(fileName, '.') == NULL) { // Prüfen, ob keine Dateiendung vorhanden ist
        size_t currentLength = strlen(fileName);
        if (currentLength + strlen(defaultExtension) >= maxSize) {
            PRINT_FEHLER("Puffer für Dateiname ist zu klein, um die Erweiterung hinzuzufügen: %s", fileName);
            PRINT_FEHLER("%s", "Abbruch.");
            exit(RC_FEHLER); // Abbruch bei Pufferoverflow
        }
        strcat(fileName, defaultExtension); // .asm anhängen
    }
}

// ----------------------------------------

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '>') { 
            // Entferne alles ab diesem Parameter
            argv[i] = NULL;
            argc = i;
            break;
        }
    }

    greetings();
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0) { 
            printUsage(argv[0]);
            return RC_OK;
        }
    }

    pruefeProjektverzeichnis(argc, argv, projektVerzeichnis, printUsage);
    int pruefeDatei_rc = pruefeDatei(argc, argv, "-s", ".asm", projektVerzeichnis, quellcodeDatei);

    // Erstellen der Dateinamen basierend auf Quellcodedatei
    snprintf(inputFileName, sizeof(inputFileName), "%s/%s", projektVerzeichnis, quellcodeDatei);
    snprintf(logFileName, sizeof(logFileName), "%s/%.*s.log", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);
    snprintf(machineCodeFileName, sizeof(machineCodeFileName), "%s/%.*s.obj", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);
    snprintf(hilfsFileName, sizeof(hilfsFileName), "%s/%.*s.mqo", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);
    snprintf(symFileName, sizeof(symFileName), "%s/%.*s.sym", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);
    snprintf(testFileName, sizeof(testFileName), "%s/%.*s.test", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);
    snprintf(dmpFileName, sizeof(dmpFileName), "%s/%.*s.dmp", projektVerzeichnis, (int)(strrchr(quellcodeDatei, '.') - quellcodeDatei), quellcodeDatei);

    ensureFileExtension(inputFileName, ".asm", sizeof(inputFileName));

    // Prüfung, ob die Datei existiert
    if (!doesPathExist(inputFileName)) {
        PRINT_FEHLER("Die Quellcode-Datei existiert nicht: %s", inputFileName);
        PRINT_FEHLER("%s", "Abbruch.");
        exit(RC_FEHLER); 
    }

    remove(logFileName);
    remove(machineCodeFileName);
    remove(hilfsFileName);
    remove(symFileName);
    remove(testFileName);
    remove(dmpFileName);

    // Kleine anfangen mit macroCapacity
    macros = (macroDefinitionen *)malloc(macroCapacity * sizeof(macroDefinitionen));
    if (!macros) {
        fprintf(stderr, "Speicherzuweisung für Makros fehlgeschlagen!\n");
        exit(RC_FEHLER);
    }

    resetParsedLinesArrays(lineAsmAufgeloest, lineCountAsmAufgeloest);
    resetParsedLinesArrays(lineAsmAufgeloestTemp, lineCountAsmAufgeloestTemp);

    //abs
    ladeAssemblerZeilen(inputFileName); 
    if ((is_error_abs != 0) || (is_error != 0)) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch.");
        for (int i = 0; i < macroCount; i++) {
            free(macros[i].macroParsedLines);  
        }
        free(macros); 
        macros = NULL; 
        return RC_FEHLER;
    }
    printf("\n");
    if (leitadressePragmaGesetzt) {
        PRINT_MSG("Leitadresse: %02d", leitadresseKennzeichen);
    }

    printf("\n");
    printf("Pass 0\n");
    pass0( ); 
    if ( (is_error != 0)) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
        for (int i = 0; i < macroCount; i++) {
            free(macros[i].macroParsedLines);  
        }
        free(macros); 
        macros = NULL; 
        return RC_FEHLER;
    }
    for (int i = 0; i < macroCount; i++) {
        free(macros[i].macroParsedLines);  
    }
    free(macros); 
    macros = NULL; 
    printf("\n");

    printf("Pass 1\n");
    pass1(logFileName);  //.mac .log
    if ((is_error != 0)) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
        return RC_FEHLER;
    }
    printf("\n");

    if (is_error == 0) {
        printf("Pass 2\n");
        pass2( logFileName, symFileName);
        if (is_error2 != 0) {
            printf("\n");
            PRINT_FEHLER("%s", "Abbruch wegen Syntaxfehler.");
            return RC_FEHLER;
        }
    }
    printf("\n");

    if (is_error == 0) {
        printf("Pass 3\n");
        pass3( machineCodeFileName, hilfsFileName, dmpFileName, testFileName);
        if (is_error3 != 0) {
            printf("\n");
            PRINT_FEHLER("%s", "Abbruch.");
            return RC_FEHLER;
        }
        if (is_error == 0) {
            printf("\n");
            printf("Ausgabe als Minimalprogramm-Objektdatei nach: %s\n", machineCodeFileName);
            printf("Ausgabe der formatierten Speicherbelegung nach: %s\n", dmpFileName);
            printf("Ausgabe der Testdatei (Spalten 1,3,4,5 fuer K1=00/01) nach: %s\n", testFileName);
            return RC_OK;
        }
    }

    if (is_error != 0) {
        printf("\n");
        PRINT_FEHLER("%s", "Abbruch.");
        return RC_FEHLER;
    } 
    return RC_OK;
}

