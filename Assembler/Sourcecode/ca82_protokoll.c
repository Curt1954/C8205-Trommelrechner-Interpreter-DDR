#include "ca82_protokoll.h"

int protokollFile = -1;                       
const char *protokollFilePath = "ca82simi.log"; 
const char *htmlFilePath = "ca82simi.html"; 
FILE *htmlFile = NULL;
void closeProtokoll();


void parseMessageToHTML(const char *message, char *htmlMessage) {
    const char *ptr = message;
    int insideColorTag = 0; // Flag für aktive Farbänderung

    while (*ptr) {
        if (strncmp(ptr, "^w", 2) == 0) { // Weiß starten
            strcat(htmlMessage, "<span style='color:white; text-shadow: 0 0 5px white; background-color: #333;'>");
            insideColorTag = 1;
            ptr += 2;
        } else if (strncmp(ptr, "^r", 2) == 0) { // Rot starten
            strcat(htmlMessage, "<span style='color:red;'>");
            insideColorTag = 1;
            ptr += 2;
        } else if (strncmp(ptr, "^g", 2) == 0) { // Grün starten
            strcat(htmlMessage, "<span style='color:lime;'>");
            insideColorTag = 1;
            ptr += 2;
        } else if (strncmp(ptr, "^n", 2) == 0) { // Zur Normalfarbe wechseln
            if (insideColorTag) {
                strcat(htmlMessage, "</span>");
                insideColorTag = 0;
            }
            ptr += 2;
        } else if (*ptr == '<') { // "<" als HTML-Entity umwandeln
            strcat(htmlMessage, "&lt;");
            ptr++;
        } else if (*ptr == '>') { // ">" als HTML-Entity umwandeln
            strcat(htmlMessage, "&gt;");
            ptr++;
        } else {
            strncat(htmlMessage, ptr, 1);
            ptr++;
        }
    }

    // Falls eine Farbänderung am Ende noch aktiv ist, schließen
    if (insideColorTag) {
        strcat(htmlMessage, "</span>");
    }
}

void cleanMessage(const char *input, char *output) {
    const char *ptr = input;
    
    while (*ptr) {
        if (strncmp(ptr, "^w", 2) == 0 || strncmp(ptr, "^r", 2) == 0 || 
            strncmp(ptr, "^g", 2) == 0 || strncmp(ptr, "^n", 2) == 0) {
            ptr += 2; // Steuerzeichen überspringen
        } else {
            strncat(output, ptr, 1);
            ptr++;
        }
    }
}

void writeProtokoll(const char *message) {
    // Protokolldatei schreiben
    if (protokollFile < 0) {
        protokollFile = open(protokollFilePath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (protokollFile < 0) {
            perror("Fehler beim Öffnen der Protokolldatei");
            return;
        }
    }
    
    char cleanedMessage[2048] = ""; // Puffer für bereinigten Text
    cleanMessage(message, cleanedMessage); // Steuerzeichen entfernen
    if (write(protokollFile, cleanedMessage, strlen(cleanedMessage)) < 0) {
        perror("Fehler beim Schreiben in die Protokolldatei");
    }
}

void writeHtmlProtokoll(const char *message) {
    // HTML-Datei öffnen und Vorspann hinzufügen (falls nicht vorhanden)
    if (!htmlFile) {
        htmlFile = fopen(htmlFilePath, "w");
        if (!htmlFile) {
            perror("Fehler beim Öffnen der HTML-Datei");
            return;
        }
        fprintf(htmlFile, "<html><head><style>body { background-color: #333; color: #ccc; }</style></head><body>\n"); // Hintergrund setzen
    }

    char htmlMessage[2048] = ""; // Puffer für umgewandelten HTML-Text
    if (strcmp(message, "\n") == 0) {
        fprintf(htmlFile, "<br>\n");
    } else { 
        parseMessageToHTML(message, htmlMessage);
    };
    fprintf(htmlFile, "<p>%s</p>\n", htmlMessage);
    fflush(htmlFile);
}

void closeProtokoll() {
    if (htmlFile) {
        fprintf(htmlFile, "</body></html>\n"); 
        fclose(htmlFile);
        htmlFile = NULL;
    }
    if (protokollFile >= 0) {
        close(protokollFile);
        protokollFile = -1; // Setzt den Deskriptor zurück
    }
}


// Funktion zur Ausgabe einer Debug-Zeile
void writeDebugLine(const char *message) {
    if ( kommentar == 1 ) { 
       printf("\r   %s\n",message);
       writeProtokoll(message) ;
       writeHtmlProtokoll(message);
       writeProtokoll("\n") ;
       //printf("-> ");
    }
}

