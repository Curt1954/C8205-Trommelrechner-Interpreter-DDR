//ca82_standards.c - Version 1.00-030 (siehe ca82_version.h)
#include "ca82_standards.h"
#include <errno.h>


int kommentar = 0;
FILE *berichtLog = NULL;   // gesetzt, solange die Berichte nach Pass 3 auch ins .log geschrieben werden
int farbeAktiv = 0;   // 1 = ANSI-Farbcodes ausgeben (wird in main gesetzt)
Register regs;


// Funktion: Feld aus einem Wort extrahieren (Bitweise Operation)
unsigned long long int extractField(unsigned long long word, int from, int to) {
    int totalBits = 33; // Für ein 33-Bit-Wort
    unsigned long long int mask = ((1ULL << (to - from + 1)) - 1) << (totalBits - to - 1);
    unsigned long long int extracted = (word & mask) >> (totalBits - to - 1); 
    return extracted;
}


void printX(const char *message) {
    printf("%s\n", message);
}

void printMsg(const char *message) {
    fprintf(stderr,"%s%s%s\n", _gruen, message, _normal);
}

void printFehler(const char *message) {
    fprintf(stderr,"%sFehler: %s %s\n", _violett, _normal, message);
}

void printWarnung(const char *message) {
    fprintf(stderr,"%sWarnung: %s %s\n", _gelb, _normal, message);
    if (berichtLog) fprintf(berichtLog, "Warnung: %s\n", message);
}

void berichtPrintf(const char *format, ...) {
    va_list ap;
    va_start(ap, format);
    vprintf(format, ap);
    va_end(ap);
    if (berichtLog) {
        va_start(ap, format);
        vfprintf(berichtLog, format, ap);
        va_end(ap);
    }
}

void printBits(unsigned int num, int bits) {
    for (int i = bits - 1; i >= 0; i--) {
        printf("%c", (num & (1 << i)) ? '1' : '0');
    }
}

void removeNewline(char *line) {
    char *pos = strchr(line, '\n');
    if (pos != NULL) {
        *pos = '\0';
    }
}

void removeNewlines(char *line) {
    char *src = line, *dst = line;
    while (*src != '\0') {
        if (*src != '\n') {
            *dst++ = *src;
        }
        src++;
    }
    *dst = '\0';
}

void removeSpaces(char *str) {
    int i = 0, j = 0;
    while (str[i] != '\0') {
        if (str[i] != ' ') {
            str[j++] = str[i];
        }
        i++;
    }
    str[j] = '\0';
}

void entfernePunkt(char *line) {
    int i = 0, j = 0;
    while (line[i] != '\0') {
        if (line[i] != '.') {
            line[j++] = line[i];
        }
        i++;
    }
    line[j] = '\0';
}

void entferneSlash(char *line) {
    int i = 0, j = 0;
    while (line[i] != '\0') {
        if (line[i] != '/') {
            line[j++] = line[i];
        }
        i++;
    }
    line[j] = '\0';
}

void padWithLeadingZeros(char *str, int totalLength) {
    int len = strlen(str);
    if (len < totalLength) {
        memmove(str + (totalLength - len), str, len + 1);
        memset(str, '0', totalLength - len);
    }
}

bool fileExists(const char *filename) {
    return access(filename, F_OK) == 0;
}

// -------------------------------------------

// Funktion zur Prüfung, ob ein Pfad existiert
int doesPathExist(const char *path) {
    //printf("%s\n",path);
    struct stat st;
    return stat(path, &st) == 0; // Gibt 1 zurück, wenn der Pfad existiert, sonst 0
}

// Funktion zur Prüfung, ob ein Pfad ein Verzeichnis ist
int isDirectory(const char *path) {
    struct stat st;
    return stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

// Funktion zur Prüfung, ob ein Pfad eine Datei ist
int isFile(const char *path) {
    struct stat st;
    return stat(path, &st) == 0 && S_ISREG(st.st_mode);
}

// -------------------------------------------

// Typdefinition für Funktionszeiger
typedef void (*usageFunction)(const char *);

// ----------

void trimWhitespace(char *str) {
    char *start = str;
    char *end;

    // Entferne führende Leerzeichen
    while (*start && isspace((unsigned char)*start)) {
        start++;
    }

    if (*start == '\0') { // Falls die Zeichenkette nur Leerzeichen enthält
        *str = '\0';
        return;
    }

    // Entferne nachfolgende Leerzeichen
    end = start + strlen(start) - 1;
    while (end > start && isspace((unsigned char)*end)) {
        end--;
    }

    // Null-Terminierung nach letztem Nicht-Leerzeichen
    *(end + 1) = '\0';

    // Kopiere das getrimmte Ergebnis zurück in str
    memmove(str, start, end - start + 2);
}


void removeParameter(int *argc, char *argv[], const char *kz) {
    for (int i = 1; i < *argc; i++) { // Durchsuche argv ab Index 1 (Index 0 ist das Programm selbst)
        if (strcmp(argv[i], kz) == 0) { // Falls das Argument `kz` gefunden wird
            for (int j = i; j < *argc - 1; j++) {
                argv[j] = argv[j + 1]; // Verschiebe die restlichen Argumente nach vorne
            }
            (*argc)--; // Anzahl der Argumente reduzieren
            i--; // Index korrigieren, um das nächste Element erneut zu prüfen
        }
    }
}

// Setzt in der Datei 'projekdetails' die Zeile mit dem Kennzeichen auf den neuen Wert (haengt sie an, falls
// sie fehlt). Existiert 'projekdetails' nicht, geschieht nichts. Es wird in eine Temp-Datei geschrieben und
// erst bei Erfolg an die Stelle der alten Datei gesetzt; die alte Datei bleibt bei jedem Fehler unveraendert.
// Rueckgabe 0 = in Ordnung (oder nichts zu tun), -1 = nicht aktualisiert (Warnung ist ausgegeben, der Lauf
// geht weiter: die Angaben stehen ohnehin in der Kommandozeile).
static int projektdetailsZeileSetzen(const char *kennzeichen, const char *wert) {
    static int schonGewarnt = 0;   // je Lauf hoechstens eine Warnung, auch wenn mehrere Zeilen betroffen sind
    const char *details = "projekdetails";
    const char *temp = "temp_projekdetails";
    FILE *file = fopen(details, "r");
    if (!file) return 0;

    FILE *tempFile = fopen(temp, "w");
    if (!tempFile) {
        if (!schonGewarnt) PRINT_WARNUNG("Die Datei '%s' kann nicht aktualisiert werden (Temp-Datei nicht schreibbar: %s); der Lauf wird fortgesetzt.\n", details, strerror(errno));
        schonGewarnt = 1;
        fclose(file);
        return -1;
    }

    char line[512];
    int gefunden = 0;
    size_t kzLen = strlen(kennzeichen);
    while (fgets(line, sizeof(line), file)) {
        if (strncmp(line, kennzeichen, kzLen) == 0) {
            gefunden = 1;
            fprintf(tempFile, "%s %s\n", kennzeichen, wert);
        } else {
            fputs(line, tempFile);
        }
    }
    if (!gefunden) {
        fprintf(tempFile, "%s %s\n", kennzeichen, wert);
    }
    fclose(file);

    int fehler = ferror(tempFile);
    if (fclose(tempFile) != 0) fehler = 1;
    if (fehler) {
        if (!schonGewarnt) PRINT_WARNUNG("Die Datei '%s' wurde nicht aktualisiert (Schreibfehler: %s); der Lauf wird fortgesetzt.\n", details, strerror(errno));
        schonGewarnt = 1;
        remove(temp);
        return -1;
    }
#ifdef _WIN32
    remove(details);   // unter Windows ersetzt rename() eine vorhandene Datei nicht
#endif
    if (rename(temp, details) != 0) {
        if (!schonGewarnt) PRINT_WARNUNG("Die Datei '%s' wurde nicht aktualisiert (%s); der Lauf wird fortgesetzt.\n", details, strerror(errno));
        schonGewarnt = 1;
        remove(temp);
        return -1;
    }
    return 0;
}

void pruefeLadeadresse(int argc, char *argv[], const char *kennzeichen, unsigned int *ladeadresse) {
    char projektdetailsDatei[] = "projekdetails";
    char ladeadresseStr[5] = "0000";

    FILE *file = fopen(projektdetailsDatei, "r");
    if (file) {
        char line[512];
        while (fgets(line, sizeof(line), file)) {
            if (strncmp(line, kennzeichen, strlen(kennzeichen)) == 0 && strlen(line) > strlen(kennzeichen) + 1) {
                strncpy(ladeadresseStr, line + strlen(kennzeichen) + 1, 4);
                ladeadresseStr[4] = '\0';
                break;
            }
        }
        fclose(file);
    }

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], kennzeichen) == 0 && i + 1 < argc) {
            if (strlen(argv[i + 1]) == 4 && strspn(argv[i + 1], "01234567") == 4) {
                strncpy(ladeadresseStr, argv[i + 1], 4);
            }
            break;
        }
    }

    *ladeadresse = strtoul(ladeadresseStr, NULL, 8);

    projektdetailsZeileSetzen(kennzeichen, ladeadresseStr);

    PRINT_MSG("%sBenutze Ladeadresse %s%s", _normal, _gruen, ladeadresseStr);
}

// ----------

int pruefeDatei(int argc, char *argv[], const char *kennzeichen, const char *standardEndung, const char *projektVerzeichnis, char dateiname[]) {
    char projektdetailsDatei[] = "projekdetails";
    int kennzeichenGefunden = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], kennzeichen) == 0 && i + 1 < argc) {
            strncpy(dateiname, argv[i + 1], 512 - 1);
            kennzeichenGefunden = 1;
            break;
        }
    }
    
    memmove(dateiname, strrchr(dateiname, '/') ? strrchr(dateiname, '/') + 1 : dateiname, strlen(strrchr(dateiname, '/') ? strrchr(dateiname, '/') + 1 : dateiname) + 1);
    if (( kennzeichenGefunden == 0 ) && (strlen(dateiname ) == 0)) {
        //Heraussuchen des Dateinamens
        FILE *file = fopen(projektdetailsDatei, "r");
        if (file) {
            char line[2048]={0};

            while (fgets(line, sizeof(line), file)) {
                // Prüft, ob das Kennzeichen am Anfang der Zeile steht
                if (strncmp(line, kennzeichen, strlen(kennzeichen)) == 0) {
                    
                    char rest[2048]={0};  // Statisches Array statt Zeiger
                    memmove(rest, line + strlen(kennzeichen), sizeof(rest) - 20);
                    rest[sizeof(rest) - 1] = '\0';

                    if (rest[0] == ' ' || rest[0] == '.' || rest[0] == '\n') {
                        size_t copy_length = strlen(rest);  // Nur die echte Länge kopieren
                        if (copy_length > MAX_LINE_LENGTH - 1) {
                            copy_length = MAX_LINE_LENGTH - 1;  // Begrenzung setzen
                        }
                        
                        memmove(dateiname, rest + 1, copy_length);
                        dateiname[copy_length] = '\0'; // Null-Termination sicherstellen
                        kennzeichenGefunden = 1;
                    }
                }
            }

            fclose(file);
        }
    }

    // Zeilenende aus projekdetails entfernen, bevor die Endung geprüft/ergänzt wird
    // (sonst steht der Zeilenumbruch vor ".asm" und die Endung geht verloren).
    removeNewline(dateiname);

    char tempdn[1024]={0};
    strcpy(tempdn,dateiname);
    char *dotPos = strrchr(dateiname, '.'); // Sucht letzten Punkt
    if (dotPos == NULL || strlen(dotPos + 1) != 3) { // Prüft, ob keine Endung existiert oder sie nicht genau 3 Zeichen hat
        strncat(dateiname, standardEndung, 1024 - strlen(dateiname) - 1);
    }

    char fullPath[1024]; 
    removeNewline(dateiname);

    snprintf(fullPath, sizeof(fullPath), "%s/%s", projektVerzeichnis, dateiname);

    if (access(fullPath, F_OK) != 0) {
        if (strcmp(kennzeichen, "-u") == 0 || strcmp(kennzeichen, "-y") == 0) {
            PRINT_WARNUNG("Die Datei %s für Parameter %s existiert nicht im Projektverzeichnis\n", fullPath, kennzeichen);
            return 1;
        } else { 
            PRINT_FEHLER("Die Datei %s für Parameter %s existiert nicht im Projektverzeichnis\n", fullPath, kennzeichen);
            exit(RC_FEHLER);
            return -1; //dummy-return
        }
    }
        
    char vollstaendigerPfad[1024];
    snprintf(vollstaendigerPfad, sizeof(vollstaendigerPfad), "%s/%s", projektVerzeichnis, dateiname);

    if (doesPathExist(vollstaendigerPfad)) {
        PRINT_MSG("%sBenutze für %s%s %sdie Datei: %s%s", _normal, _gruen ,kennzeichen, _normal, _gruen,tempdn);
        projektdetailsZeileSetzen(kennzeichen, tempdn);
        return 0;
    } else {
        if (strcmp(kennzeichen, "-u") == 0 || strcmp(kennzeichen, "-y") == 0) {
            PRINT_WARNUNG("Die Datei für Parameter %s existiert nicht im Projektverzeichnis\n", kennzeichen);   
            return 1;
        } else { 
            PRINT_FEHLER("Die Datei für Parameter %s existiert nicht im Projektverzeichnis\n", kennzeichen);   
            exit(RC_FEHLER);
            return -1; //dummy-return
        }
    }
}

// -------------

int kopiereDateiWennExistiert(const char *quelle, const char *ziel) {
    int rc=-1;
    FILE *sourceFile = fopen(quelle, "r");
    if (sourceFile) {
        FILE *targetFile = fopen(ziel, "w");
        if (targetFile) {
            char buffer[512];
            while (fgets(buffer, sizeof(buffer), sourceFile)) {
                fputs(buffer, targetFile);
            }
            fclose(targetFile);
            rc=0;
        } else {
            rc=1; 
        }
        fclose(sourceFile);
    } else {
        rc=1; 
    }
    return rc;
}


void replaceSlashes(char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] == '/') {
            str[i] = '_';  // Ersetzt alle '/'
        }
    }
}

void createFileName(char *neueDateiName, size_t size, const char *projektdetailsDatei, char *oldProjekt) {
    replaceSlashes(oldProjekt);  // Slashes ersetzen
    snprintf(neueDateiName, size, "%s.%s", projektdetailsDatei, oldProjekt);
}

void pruefeProjektverzeichnis(int argc, char *argv[], char projektVerzeichnis[], void (*printUsage)()) {
    char projektdetailsDatei[] = "projekdetails";
    int parameterGefunden = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            strncpy(projektVerzeichnis, argv[i + 1], 512 - 1);
            parameterGefunden = 1;

            if (!doesPathExist(projektVerzeichnis)) {

                PRINT_FEHLER("Projektverzeichnis '%s' existiert nicht.", projektVerzeichnis);
                projektVerzeichnis[0] = '\0';
                printUsage(argv[0]);
                exit(RC_FEHLER);
            } else {
                PRINT_MSG("%sProjektverzeichnis: %s%s", _normal, _gruen, projektVerzeichnis);
            }


            FILE *file = fopen(projektdetailsDatei, "r+");
            if (file) {
                char line[512] = {0};   // auch bei leerer projekdetails definiert (removeNewline unten)
                char oldProjekt[512] = {0};
                int found = 0;
                while (fgets(line, sizeof(line), file)) {
                    if (strncmp(line, "-p ", 3) == 0) {
                        found = 1;
                        // Speichert das Wort nach "-p" in oldProjekt
                        sscanf(line + 3, "%s", oldProjekt);
                        break;
                    }
                }

                removeNewline(line);
                if (found && strstr(line, oldProjekt) != NULL && strcmp(projektVerzeichnis, oldProjekt) == 0)  {
                    // Gleicher Projektname: nur die -p-Zeile neu schreiben (Fehler sind nicht fatal)
                    fclose(file);
                    projektdetailsZeileSetzen("-p", projektVerzeichnis);
                    file = fopen(projektdetailsDatei, "r+");
                } else {
                    // Erstelle eine Kopie der Datei mit dem neuen Namen
                    char neueDateiName[1024];
                    snprintf(neueDateiName, sizeof(neueDateiName), "%s.%s", projektdetailsDatei, oldProjekt);
                    createFileName(neueDateiName, sizeof(neueDateiName), projektdetailsDatei, oldProjekt);

                    // Gesicherte Datei des neuen Projekts: der Name wird genauso gebildet wie beim
                    // Sichern (Schrägstriche -> '_'), sonst wird sie bei Pfaden wie A/x nie gefunden.
                    char neuesProjektKopie[512];
                    strncpy(neuesProjektKopie, projektVerzeichnis, sizeof(neuesProjektKopie) - 1);
                    neuesProjektKopie[sizeof(neuesProjektKopie) - 1] = '\0';
                    char neueDateiName2[1024];
                    createFileName(neueDateiName2, sizeof(neueDateiName2), projektdetailsDatei, neuesProjektKopie);

                
                    FILE *kopieFile = fopen(neueDateiName, "w");
                    if (kopieFile && file) {
                        char kopieZeile[512];
                        rewind(file);
                        while (fgets(kopieZeile, sizeof(kopieZeile), file)) {
                            fputs(kopieZeile, kopieFile);
                        }
                        fclose(kopieFile);
                    }
                    fclose(file);

                    // ev. das alte Projekt zurückkopieren
                    int rc = kopiereDateiWennExistiert(neueDateiName2, projektdetailsDatei); 
                    if ( rc == 1 ) { 
                            // Leere die ursprüngliche Datei
                        file = fopen(projektdetailsDatei, "w");
                        if (file) fprintf(file, "-p %s\n", projektVerzeichnis);
                    } else {  file = fopen(projektdetailsDatei, "r+"); }   
                }                                
                if (file) fclose(file);

            } else {
                file = fopen(projektdetailsDatei, "w");
                if (file) {
                    fprintf(file, "-p %s\n", projektVerzeichnis);
                    fclose(file);
                }
            }
            return;
        }
    }

    if (!parameterGefunden) {
        FILE *file = fopen(projektdetailsDatei, "r");
        if (file) {
            char line[512];
            while (fgets(line, sizeof(line), file)) {
                if (strncmp(line, "-p ", 3) == 0) {
                    strncpy(projektVerzeichnis, line + 3, 512 - 1);
                    projektVerzeichnis[strcspn(projektVerzeichnis, "\n")] = '\0';

                    if (doesPathExist(projektVerzeichnis)) {
                        fclose(file);
                        PRINT_MSG("%sProjektverzeichnis: %s%s", _normal, _gruen, projektVerzeichnis);
                        return;
                    } else {
                        PRINT_FEHLER("Projektverzeichnis '%s' existiert nicht.", projektVerzeichnis);
                        projektVerzeichnis[0] = '\0';
                        fclose(file);
                        printUsage();
                        exit(RC_FEHLER);
                    }
                }
            }
            fclose(file);
        }
        PRINT_FEHLER("%s","Es wurde kein Projektverzeichnis angegeben.");
        projektVerzeichnis[0] = '\0';
        printUsage(argv[0]);
        exit(RC_FEHLER);
    } else {
        PRINT_MSG("%sProjektverzeichnis: %s%s", _normal, _gruen, projektVerzeichnis);
    }
}

// -------------------------------------------

void ensureFullStructure(const char *verz) {
    struct stat st;
    const char *geraeteDir = "Geraete";
    const char *subdirectories[] = {
        "LochbandLeser_1", "LochbandLeser_2", "LochkartenLeser_1", "LochbandStanzer_1", "LochkartenStanzer_1", "Schreibwerk_out_1", "Schreibwerk_out_2", "Trommel"
    };
    int subdirCount = sizeof(subdirectories) / sizeof(subdirectories[0]);


    if (stat(verz, &st) != 0) {
        if (MKDIR(verz, 0777) != 0) {
            PRINT_FEHLER("beim Erstellen des Geräteverzeichnisses: %s", verz);
            return;
        }
    } else if (!S_ISDIR(st.st_mode)) {
        PRINT_FEHLER("Objekt existiert, ist aber kein Verzeichnis: %s", verz);
        return;
    }

    // Pfad zum Geraete-Verzeichnis
    char geraetePath[1024];
    snprintf(geraetePath, sizeof(geraetePath), "%s/%s", verz, geraeteDir);

    if (stat(geraetePath, &st) != 0) {
        if (MKDIR(geraetePath, 0777) != 0) {
            PRINT_FEHLER("beim Erstellen des Verzeichnisses: %s", geraetePath);
            return;
        }
    } else if (!S_ISDIR(st.st_mode)) {
        PRINT_FEHLER("Objekt existiert, ist aber kein Verzeichnis: %s", geraetePath);
        return;
    }

    // Unterverzeichnisse prüfen und erstellen
    for (int i = 0; i < subdirCount; i++) {
        char fullPath[2048]; 
        size_t maxLength = strlen(geraetePath) + strlen(subdirectories[i]) + 2; // +2 für "/" und null-terminator
        if (maxLength > sizeof(fullPath)) {
            PRINT_FEHLER("Puffer für den Pfad überschritten: %s/%s", geraetePath, subdirectories[i]);
            continue;
        }

        snprintf(fullPath, sizeof(fullPath), "%s/%s", geraetePath, subdirectories[i]);

        if (stat(fullPath, &st) != 0) {
            if (MKDIR(fullPath, 0777) != 0) {
                PRINT_FEHLER("beim Erstellen des Unterverzeichnisses: %s", fullPath);
                continue;
            }
        } else if (!S_ISDIR(st.st_mode)) {
            PRINT_FEHLER("Objekt existiert, ist aber kein Verzeichnis: %s", fullPath);
        }
    }
}

// Vergleich ohne Beachtung der Gross-/Kleinschreibung (Pragma-Schluesselwort, start, Optionen).
int gleichOhneGrossKlein(const char *a, const char *b) {
    while (*a && *b) {
        if (toupper((unsigned char)*a) != toupper((unsigned char)*b)) return 0;
        a++; b++;
    }
    return *a == '\0' && *b == '\0';
}

// Vergleicht die ersten n Zeichen ohne Beruecksichtigung der Gross-/Kleinschreibung.
int beginntOhneGrossKlein(const char *text, const char *praefix) {
    while (*praefix) {
        if (toupper((unsigned char)*text) != toupper((unsigned char)*praefix)) return 0;
        text++; praefix++;
    }
    return 1;
}


// Kopiert quelle nach ziel (max. groesse-1 Zeichen) und terminiert immer.
void strkopiere(char *ziel, size_t groesse, const char *quelle) {
    if (groesse == 0) return;
    size_t n = strlen(quelle);
    if (n >= groesse) n = groesse - 1;
    memmove(ziel, quelle, n);          // memmove: Quelle darf im Ziel liegen
    ziel[n] = '\0';
}

// Haengt quelle an ziel an (Gesamtlaenge max. groesse-1) und terminiert immer.
void stranhaengen(char *ziel, size_t groesse, const char *quelle) {
    size_t l = strnlen(ziel, groesse);
    if (l >= groesse) { if (groesse) ziel[groesse - 1] = '\0'; return; }
    strkopiere(ziel + l, groesse - l, quelle);
}
