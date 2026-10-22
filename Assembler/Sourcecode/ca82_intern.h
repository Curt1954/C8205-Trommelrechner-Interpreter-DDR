// ca82_intern.h - gemeinsame interne Deklarationen der Module des Assemblers c82ass
// (Version siehe ca82_version.h). Wird nur von den ca82_*.c-Modulen eingebunden.
//
// Modulaufbau:
//   ca82_main.c       Optionen, Dateinamen, Ablauf der Paesse
//   ca82_quelle.c     Einlesen der Quelltextzeilen
//   ca82_pass0.c      Makroaufloesung            ca82_makros.c   Makrodefinitionen und -expansion
//   ca82_pass1.c      Literale, equ/abs          ca82_pass2.c    Adressen, Symbole
//   ca82_ausdruck.c   Ausdrucksauswertung        ca82_codierung.c Operationscodes, Text, dz
//   ca82_pass3.c      Objektcode (.obj/.mqo/.dmp) ca82_testdatei.c .test-Datei
//   ca82_listing.c    Listing                    ca82_hilfen.c   Zeilenfelder, Meldungen, Textwerkzeuge
//   ca82_zustand.c    globale Zustandsvariablen
#ifndef CA82_INTERN_H
#define CA82_INTERN_H

#include "ca82_standards.h"
#include "ca82_version.h"
#include "ca82_symbole.h"
#include "ca82_berichte.h"
#include <stdarg.h>
#include <errno.h>
#include "ca82_typen.h"
#include "ca82_makros.h"


typedef struct {
    char sp0[32];
    elementType sp1;
    elementType sp2;
    elementType sp3;
    elementType sp4;
    int adr;        // Trommeladresse der Zeile (nur gueltig, wenn adrValid == 1)
    int adrValid;   // 1 = Zeile traegt eine Adresse, die sp0 nicht enthaelt (dt/dto/dtm)
} lineElementsX;



// ----------------------------
//

#define MELDE_FEHLER_P1(format, ...) \
    do { \
        pruefeZeilenfeld(lineCountAsmAufgeloestTemp); \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 1 Fehler%s: " format , _violett, _normal, __VA_ARGS__); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, fehlertext); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, ""); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, ""); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, ""); \
        lineCountAsmAufgeloestTemp++; \
    } while (0)

#define MELDE_WARNUNG_P1(format, ...) \
    do { \
        pruefeZeilenfeld(lineCountAsmAufgeloestTemp); \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 1 Warnung%s: " format , _gelb, _normal, __VA_ARGS__); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp1, fehlertext); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp2, ""); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp3, ""); \
        STRKOPIE(lineAsmAufgeloestTemp[lineCountAsmAufgeloestTemp].sp4, ""); \
        lineCountAsmAufgeloestTemp++; \
    } while (0)



#define MELDE_FEHLER_P2(i, message) \
    meldeFehlerP2(lineAsmAufgeloestTemp, lineAsmAufgeloest, &lineCountAsmAufgeloest, &i, message)

#define MELDE_WARNUNG_P2(format, ...) \
    do { \
        pruefeZeilenfeld(lineCountAsmAufgeloest); \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 2 Warnung%s: " format , _gelb, _normal, __VA_ARGS__); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, fehlertext); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, ""); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, ""); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, ""); \
        lineCountAsmAufgeloest++; \
    } while (0)

#define MELDE_MSG_P2(format, ...) \
    do { \
        pruefeZeilenfeld(lineCountAsmAufgeloest); \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** 2 Hinweis%s: " format "\n", _gruen, _normal, __VA_ARGS__); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, fehlertext); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, ""); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, ""); \
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, ""); \
        lineCountAsmAufgeloest++; \
    } while (0)

// Warnung mit Ort auf STDERR (datei:zeile: Warnung: text). Die Warnung erscheint nicht im Listing und
// aendert deshalb weder .log noch .dmp. Wird fuer Hinweise genutzt, die kein Abbruch sind.

typedef struct {
    unsigned int spalte1; // Erste Spalte (xxxx)
    unsigned int spalte2; // Zweite Spalte (ASCII-Wert)
    unsigned int spalte3; // Dritte Spalte (Alternative ASCII-Wert)
} TableRow;

// ---- globale Zustandsvariablen (definiert in ca82_zustand.c) ----
extern lineElements linesAsm[PROGRAMMZEILEN];              // Quelltextzeilen nach dem Einlesen
extern int lineCountAsm;
extern lineElements lineAsmAufgeloest[PROGRAMMZEILEN];     // Zeilen nach Pass 0 bzw. Pass 2
extern int lineCountAsmAufgeloest;
extern lineElements lineAsmAufgeloestTemp[PROGRAMMZEILEN]; // Zeilen nach Pass 1
extern int lineCountAsmAufgeloestTemp;
extern lineElementsX lineAsmAufgeloestX[PROGRAMMZEILEN];   // Listingzeilen fuer .dmp und .test
extern int lineCountAsmAufgeloestX;

extern int is_error, is_error0, is_error1, is_error2, is_error3, is_error_abs;
extern int printHell;
extern int leitadresseKennzeichen;
extern int leitadressePragmaGesetzt;
extern unsigned int absolutadresse;
extern int line_ausgegeben;
extern unsigned int startAdresse;
extern int absprAktiv;            // 1 = --ABSPR: .kep statt .obj
void absprStart(FILE *f);         // erster Leitbefehl der .kep-Datei
extern int absprAnzahl0209;       // K1=02..09-Zeilen, nicht umgesetzt (Warnung)
extern int absprBahnAnzahl;                 // Woerter auf den Zellen 0002..0037 (KEP)
extern unsigned long absprBahnAdresse[];    // deren Adressen (hoechstens 64 gespeichert)
extern int absprAnzahl01;         // verbleibende K1=01-Zeilen (Warnung, wenn 0)

extern char inputFileName[1024];

extern int zFlagErz, textPC, zFlag;     // Zustand von Pass 3 / Textausgabe (ca82_codierung.c)
extern const char *evaluateValueGrund;   // Grund eines Auswertungsfehlers (ca82_ausdruck.c)
extern int objWortAnzahl;   // Anzahl der in die .obj geschriebenen Worte (Warnung bei leerem Programm)

// ---- Funktionen der Module ----

/* ---- ca82_fehler.c: zentrale Fehlerausgabe mit Zaehler und Obergrenze ---- */
void fehlerMitOrt(int quellzeile, const char *text);
int anzahlFehler(void);
void fehlerZusammenfassung(void);

/* ---- ca82_hilfen.c: Zeilenfelder, Meldungen mit Ort und kleine Textwerkzeuge ---- */
FILE *oeffneAusgabedatei(const char *pfad, const char *modus);
void resetParsedLinesArrays(lineElements lineAsmAufgeloest[], int lineCountAsmAufgeloest);
void copyLineElements(lineElements *output, lineElements *ergebnis, int i);
bool isValidLabel(const char *label);
void copyAndIncrementLineElements(int i);
void meldeFehlerP2(lineElements lineAsmAufgeloestTemp_p[], lineElements lineAsmAufgeloest_p[], int *lineCountAsmAufgeloest_p, int *i, const char *message);
void toLowerCase(char *str);
void trim(char *str);
void removeTrailingSpaces(char *line);
void printHexLine(const char *line);
void cleanLine(char *line);
void printAdressError(const char *label, char *typ, char *text, char *line);
void printLabelError(const char *label, char *typ, char *text, char *line);
void printLabelWarning(const char *label, char *typ, char *text);
void printMacroParameterWarning(const char *label, char *typ, char *text, char *line);
void printMacroParameterError(const char *label, char *typ, char *text, char *line);
void trimLeadingSpaces(char *line);
void printAssemblerzeilenArray(void);
void pruefeZeilenfeld(int belegt);
void meldeZuVieleZeilen(int quellzeile);
void meldeWarnungOrt(int quellzeile, const char *text);
void meldeListingFehlerAufStderr(lineElements zeilen[], int anzahl);

/* ---- ca82_quelle.c: Einlesen der Quelltextzeilen (Pragmas, Kommentare, Wiederholungsadressen) ---- */
int istTextAnweisung(const char *operation);
void processLine(char *line, lineElements linesAsm_p[], int *lineCount);
void ladeAssemblerZeilen(const char *inputFileName_p);
unsigned int berechneWiederholAdr(int anzahl, unsigned int basisAdr);
int berechneOperand(const char *operand_str);
void verarbeiteZeile_wdhl_adr_e(char *tempLine);
int verarbeiteZeile_wdhl(char *tempLine, char *loe, char *resu, char *opcode, char *anzahl, char *adresse);

/* ---- ca82_listing.c: Formatierte Ausgabe des Listings (STDOUT und .dmp) ---- */
void printFormattedAsmListing(lineElements lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p);
void printFormattedAsmListingX(lineElementsX lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p, FILE *dmpFile);

/* ---- ca82_pass0.c: Pass 0: Aufloesung der Makros ---- */
void pass0(void);

/* ---- ca82_pass1.c: Pass 1: Literale, equ/abs-Tabellen, Operandenpruefung ---- */
int isKeywordMatch(const char *token);
int isValidSp3_keinLiteralEnthalten(const char *sp3);
void processLiteralEntry(lineElements lineAsmAufgeloestTemp_p[], int *lineCountAsmAufgeloestTemp_p, Literal literalTable_p[], int i);
int pruefeDbOperand(const char *operation, const char *operand, long *wert, char *meldung, size_t groesse);
int pruefeSpaOperand(const char *operand, long *wert, char *meldung, size_t groesse);
unsigned int spaAdresse(unsigned int befehlszaehler, long wert);
void pass1(char *symbolLogFile);
const char* addLiteral(char *literalName, char *literalValue, unsigned int relativAdresse);

/* ---- ca82_pass2.c: Pass 2: Adressen, Symboltabelle, Fehlermarken ---- */
void sanitizeLabel(char *label);
void printLineIfNotPrinted(const char *line);
void testeAdress(char *label, char *line);
void extractBackslashContent(char *line, char *textkonst);
void pass2(char *symbolLogFile, char *symFileName);
void addSymbol(char *symbol, int address, int relativAdresse, char *operation, char *operand, int nr, int i);

/* ---- ca82_ausdruck.c: Auswertung von Werte- und Adressausdruecken ---- */
long long int evaluateValue(char *operand, int *errorFlag);
int isValidToken(const char *tempToken);
unsigned int sternadresseBearbeiten(char *xoperand, char *line, int *errorFlag, unsigned int programCounter);
unsigned int evaluateAddress(char *operand, char *line, int *errorFlag, int *raAdr, char *label, unsigned int programCounter, unsigned int *absolutadresse_p);
int pruefeAdressausdruck(const char *operand, char *meldung, size_t groesse);

/* ---- ca82_codierung.c: Codierung: Operationscodes, Text (dt/dz), Umschluesselung ---- */
char* getOperationCode(char *operation);
void formatLabel(char **label);
char * formatOperand(const char *op);
int isValueInTable(const char *operand, TableRow outUmschluesselungsTable_p[], int size, int *missingPos);
void copyAndIncrementLineElementsX(int i, char *buffer);
void copyAndIncrementLineElementsSpOnly(int i, char *buffer);
void schreibeObjZeile(FILE *objFile, const char *zeile);
void erzeugenText(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int no_kbgb ,int iii);
int zaehleText(char operand[], int no_kbgb);
void dzAuswertung(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii);
int zaehleBackslashes(const char *templine);
void replaceSubstring(char *line, size_t lineSize, const char *operand, unsigned int dwValue);

/* ---- ca82_pass3.c: Pass 3: Erzeugung von .obj, .mqo und .dmp ---- */
void outAdressError(const char *label, char *typ, char *text);
void pass3(char *machineCodeFileName, char *hilfsFileName, char *dmpFileName, char *testFileName);

/* ---- ca82_testdatei.c: Erzeugung der .test-Datei ---- */
void erzeugeTestDatei(lineElementsX lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p, const char *testFileName);

/* ---- ca82_main.c: Hauptprogramm: Optionen, Dateinamen, Ablauf der Paesse ---- */
void ensureFileExtension(char *fileName, const char *defaultExtension, size_t maxSize);

#endif
