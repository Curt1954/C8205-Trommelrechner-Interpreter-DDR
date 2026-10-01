//ca82_standards.h
#ifndef CA82_STANDARDS_H
#define CA82_STANDARDS_H

#include "c82_austausch.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/file.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

#ifdef _WIN32
#include <conio.h>
#else
#include <termios.h>
#endif


#define PFs(label, param) printf(" %s %s :%s:", label, #param, (param))
#define PFi(label, param) printf(" %s %s :%i:", label, #param, (param))
#define PF11o(label, param) printf(" %s %s :%011o:", label, #param, (param))
#define PF4o(label, param) printf(" %s %s :%04o:", label, #param, (param))
#define PF11lo(label, param) printf(" %s %s :%011lo:", label, #param, (param))
#define PF4lo(label, param) printf(" %s %s :%04lo:", label, #param, (param))
#define PF11llo(label, param) printf(" %s %s :%011llo:", label, #param, (param))
#define PF4llo(label, param) printf(" %s %s :%04llo:", label, #param, (param))

#define PFend(param) printf("\n")

#define PFX(...) printf("!!!!### " #__VA_ARGS__ " :%s:\n", ##__VA_ARGS__)


// Makros
#define PRINT_FEHLER(format, ...) \
    do { \
        int len = snprintf(NULL, 0, format, __VA_ARGS__) + 1; \
        char *em = malloc(len); \
        if (em) { \
            snprintf(em, len, format, __VA_ARGS__); \
            printFehler(em); \
            free(em); \
        } \
    } while (0)


#define PRINT_WARNUNG(format, ...) \
    do { \
        int len = snprintf(NULL, 0, format, __VA_ARGS__) + 1; \
        char *em = malloc(len); \
        if (em) { \
            snprintf(em, len, format, __VA_ARGS__); \
            printWarnung(em); \
            free(em); \
        } \
    } while (0)

#define PRINT_MSG(format, ...) \
    do { \
        int len = snprintf(NULL, 0, format, __VA_ARGS__) + 1; \
        char *em = malloc(len); \
        if (em) { \
            snprintf(em, len, format, __VA_ARGS__); \
            printMsg(em); \
            free(em); \
        } \
    } while (0)

#define PRINT_X(format, ...) \
do { \
    int len = snprintf(NULL, 0, format, __VA_ARGS__) + 1; \
    char *em = malloc(len); \
    if (em) { \
        snprintf(em, len, format, __VA_ARGS__); \
        printX(em); \
        free(em); \
    } \
} while (0)


#define _violett  "\033[35m"
#define _gruen    "\033[32m"
#define _gelb     "\033[33m"
#define _normal   "\033[0m"
#define _weiss    "\033[1;37m"
#define _hellgelb "\033[1;93m"
#define _hellgrau "\033[0;37m"
#define _softgelb "\033[0;93m"
#define _blau     "\033[0;34m"
#define _hellblau "\033[1;34m"
#define _hellrot "\033[1;31m"


// Konstanten

#define MAX_SYMBOLS 4096
#define MAX_LITERALS 4096
#define MAX_LINE_LENGTH 4096
#define MAX_SYMBOL_LENGTH 33
#define MAX_LABEL_LENGTH 32
#define MAX_ADRESS_LENGTH (MAX_LINE_LENGTH - MAX_SYMBOL_LENGTH - 8)
#define MAX_LINE_LENGTH2 256 // für Zeilen-rest
#define MAX_ENTRIES 8192

//für Macro
#define MAX_LABELS 4096 // Maximale Anzahl von Makro-Labels
#define LABEL_SIZE 64   // Maximale Länge eines Labels
#define MAX_LINES 8192  // Maximale Größe des Ergebnis-Strings

void pruefeProjektverzeichnis(int argc, char *argv[], char projektVerzeichnis[], void (*printUsage)()) ;
int pruefeDatei(int argc, char *argv[], const char *kennzeichen, const char *standardEndung, const char *projektVerzeichnis, char dateiname[]);
//void pruefeDateiX(int argc, char *argv[], const char *kennzeichen, const char *standardEndung, const char *projektVerzeichnis, char dateiname[]);
void pruefeLadeadresse(int argc, char *argv[], const char *kennzeichen, unsigned int *ladeadresse);
void removeParameter(int *argc, char *argv[], const char *kz) ;

void trimWhitespace(char *str);

// Funktionen
void printBits(unsigned int num, int bits);
void printX(const char *message);
void printMsg(const char *message);
void printFehler(const char *message);
void printWarnung(const char *message);
void removeNewline(char *line);
void removeNewlines(char *line);
void removeSpaces(char *str);
void entfernePunkt(char *line);
void entferneSlash(char *line);
void padWithLeadingZeros(char *str, int totalLength);
void ensureFullStructure(const char *projektVerzeichnis);

bool fileExists(const char *filename);
int doesPathExist(const char *path);
int isDirectory(const char *path);
int isFile(const char *path);

typedef void (*usageFunction)(const char *);


extern int kommentar;

typedef struct {
    unsigned long long old_befehlsZaehler;
    unsigned long long akkumulator;
    
    unsigned long zusatzteil;
    unsigned long adressteil;
    unsigned long operationsteil;
    unsigned long long befehlsregister;
    unsigned long resultatsbehandlung;
    unsigned long loeschbit;
    unsigned long baz_b;
    unsigned long baz_a;
    unsigned long baz_z;
    unsigned int spur;
    unsigned int sektor;
} Register;

extern Register regs;

// Funktion: Feld aus einem Wort extrahieren (Bitweise Operation)
extern unsigned long long extractField(unsigned long long word, int from, int to);
// Funktion: Spurnummer aus Adresse extrahieren
extern unsigned int spurnummer(unsigned int address);
// Funktion: Sektornummer aus Adresse extrahieren
extern unsigned int sektornummer(unsigned int address);


#endif // CA82_STANDARDS_H

