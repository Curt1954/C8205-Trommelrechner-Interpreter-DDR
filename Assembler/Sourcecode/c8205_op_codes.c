#include <stddef.h> // Für NULL

typedef struct {
    char *symbolicCode; // Symbolischer Operationscode
    int octalCode;      // Entsprechender Oktalwert
} OpsCode;

OpsCode opsTable[] = {
    {"add", 003},
    {"sub", 004},
    {"ld", 005},
    {"jmp", 006},
    {"211", 0211},
    {"stopp", 007},
    {"nop", 000},
    {NULL, -1} // Markiert das Ende der Tabelle
};

