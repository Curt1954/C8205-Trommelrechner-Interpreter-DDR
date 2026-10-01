//ca82_protokoll.h
#ifndef CA82_PROTOKOLL_H
#define CA82_PROTOKOLL_H

#include "ca82_standards.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

// Globale Variablen für Protokolldateien
extern int protokollFile;
extern const char *protokollFilePath;
extern FILE *htmlFile;
extern const char *htmlFilePath;
extern int kommentar;

// Funktionsdeklarationen
void parseMessageToHTML(const char *message, char *htmlMessage);
void cleanMessage(const char *input, char *output);
void writeProtokoll(const char *message);
void writeHtmlProtokoll(const char *message);
void closeProtokoll();
void writeDebugLine(const char *message);

#endif // CA82_PROTOKOLL_H

