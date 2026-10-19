/* testframe.c — Wegwerf-Rahmenprozess zum Testen des Trommel-Moduls.
 * 1. Trommel einschalten.
 * 2. Adresse 1000 (oktal) in Bahn/Sektor zerlegen.
 * 3. Über die externe Variable auf Koinzidenz mit dieser Sektornummer warten.
 * 4. Bei Koinzidenz genau dann 77777777777 (oktal) an Adresse 1000 schreiben.
 * 5. Trommel wieder ausschalten, Prozess beenden.
 */
#include <stdio.h>
#include <stdint.h>
#include "trommel.h"
#include "unterbrechung.h"

int main(void)
{
    const unsigned int adresse = 01000;   /* oktal-Literal: 1000(8) */
    unsigned int bahn, sektor;
    unsigned int wartezyklen = 0;

    unterbrechung_einrichten();

    if (trommel_einschalten("trommel.txt") != 0) {
        fprintf(stderr, "Einschalten fehlgeschlagen.\n");
        return 1;
    }

    bahn   = trommel_bahn(adresse);
    sektor = trommel_sektor(adresse);
    printf("Adresse %04o -> Bahn %03o, Sektor %02o\n", adresse, bahn, sektor);
    printf("Sektornummer bei Einschalten (zufaellig): %02o\n",
           trommel_aktuelle_sektornummer);

    /* Koinzidenzprüfung: extern zum Modul, wie vorgegeben.
     * Zusätzlich auf abbruch_angefordert prüfen (Strg+C-Konvention,
     * s. unterbrechung.h) — gilt für jede wartende Schleife im Projekt. */
    while (trommel_aktuelle_sektornummer != sektor && !abbruch_angefordert) {
        wartezyklen++;
    }

    if (abbruch_angefordert) {
        printf("\nAbbruch angefordert (Strg+C) — raeume auf.\n");
        trommel_ausschalten();
        printf("Trommel ausgeschaltet, Rahmenprozess vorzeitig beendet.\n");
        return 130;   /* Konvention: 128+SIGINT */
    }

    printf("Koinzidenz erreicht nach %u Polling-Durchlaeufen "
           "(Sektor jetzt: %02o)\n", wartezyklen, trommel_aktuelle_sektornummer);

    int rc = trommel_schreiben(adresse, 077777777777ULL);
    if (rc == TROMMEL_SCHREIBEN_GESPERRT) {
        printf("Schreiben verweigert: Bahn %03o ist gesperrt.\n", bahn);
        trommel_ausschalten();
        return 1;
    }
    printf("Geschrieben: 77777777777 (oktal) an Adresse %04o\n", adresse);

    /* Kontrolle: direkt zurücklesen */
    uint64_t kontrolle = trommel_lesen(adresse);
    printf("Rueckgelesen: %011llo (oktal)\n", (unsigned long long)kontrolle);

    trommel_ausschalten();
    printf("Trommel ausgeschaltet, Rahmenprozess beendet.\n");
    return 0;
}
