# Regressionstest für c82ass

Version 1.00-030 (Stand 22.10.2026)

Prüft, dass der Assembler nach einer Änderung dieselben Ergebnisse liefert wie vorher.

## Aufruf (aus dem Verzeichnis `Assembler`)

```
Regressionstest/regressionstest.sh              # alles prüfen
Regressionstest/regressionstest.sh -v           # bei Abweichungen die ersten Unterschiede zeigen
Regressionstest/regressionstest.sh Projekt_1    # nur ein Verzeichnis
Regressionstest/regressionstest.sh --binary PFAD   # anderes Binary prüfen
Regressionstest/regressionstest.sh --referenz   # Referenz neu schreiben (nur nach bewusster Änderung!)
```

Rückgabe 0 = alles gleich, 1 = Abweichung, 2 = Aufruffehler. Das Skript arbeitet in einem
temporären Verzeichnis und legt im Projekt nichts ab (auch keine `projekdetails`).

## Was geprüft wird

1. **Programme gegen Referenz.** Jede `.asm` unterhalb von `Assembler` (außer `Regressionstest`,
   `Sourcecode`, `Dokumentation`) wird assembliert. Verglichen werden `.obj`, `.mqo`, `.sym`, `.dmp`,
   `.test`, `.log` und der Rückgabecode mit `referenz/`. Fehlende oder zusätzlich erzeugte Dateien zählen
   als Abweichung (so fällt auf, wenn bei einem Fehlerlauf wieder halbe `.obj` liegen bleiben).
   Jedes Programm wird ein zweites Mal mit dem Schalter `--ABSPR` assembliert (in einem eigenen Arbeitsverzeichnis);
   verglichen werden der Lochstreifen `.kep` und der Rückgabecode (`.rck`) mit `referenz/`. Die übrigen Dateien dieses Laufs
   entsprechen dem normalen Lauf. Bei Programmen, bei denen `--ABSPR` mit einem Fehler endet, gibt es keine `.kep`; dann zählt der Rückgabecode.
2. **Negativtests** in `negativ/`: je Test `<name>.asm` und `<name>.erwartet` (Rückgabecode, Texte in
   STDOUT/STDERR, vorhandene/fehlende Ausgabedateien, Farbcodes). Das Format steht im Kopf des Skripts.

Mit Version 1.00-030 kamen der `--ABSPR`-Lauf in Teil 1 (`.kep` und `.rck` in `referenz/`) und vier Negativtests hinzu (insgesamt 54): `abspr_ok` (`.kep` statt `.obj`, Hinweis zum Pragma `LEITADRESSE 00`, keine Bahn-Warnung), `abspr_bahn_warnung` (Wörter auf den Zellen 0002 und 0003 lösen die Bahn-Warnung aus), `abspr_start_warnung` (Pragma `LEITADRESSE 00` mit `start <adresse>`) und `abspr_ohne_schalter` (ohne Schalter bleibt es bei `.obj`). `negativ/version.erwartet` erwartet 1.00-030. Die Referenz von `namen_raten` und `pj2-bis_minimalprogramm` (`.obj`, `.dmp`) ist nach dem Pragma `LEITADRESSE 00` (Checkpoint 7) neu geschrieben.

## Gesamtprüfung

`Regressionstest/pruefe_alles.sh` übersetzt mit `-Wall -Wextra -Wshadow -Werror`, führt den Regressionstest aus und wiederholt ihn unter AddressSanitizer/UBSan mit Leak-Prüfung (`--ohne-asan` lässt den letzten Schritt weg). Das Skript läuft auch in der CI (`.github/workflows/assembler.yml`).

## Stand der Referenz

Die Referenz wurde mit dem Assembler nach dem Patch „Fehlerorte, Farbe, Optionen“ erzeugt. Für alle
138 vorhandenen Programme stimmt sie mit dem Ergebnis des Assemblers davor überein; Ausnahme ist
`Projekt_1/equ-ueberlauf` (Fehlerfall), bei dem `.obj`, `.mqo` und `.test` jetzt bewusst fehlen.

Mit Version 1.00-017 kam der Negativtest `makrodatei_fehlerort` hinzu (insgesamt 33; Fehler in einer Makrodatei nennen Datei und Zeile der Makrodefinition). Ein Negativtest kann jetzt eine eigene Makrodatei `<name>.makros` mitbringen (`args -m w/negativ/<name>.makros`).
Mit Version 1.00-019 kamen die Negativtests `da_relativ_fehler` und `da_relativ_ok` hinzu (insgesamt 35): `da` verlangt eine relative Adresse, Konstanten und Differenzen wie `a-b` werden abgewiesen.

Mit Version 1.00-016 kam der Negativtest `da_symbol_fehlt` hinzu (insgesamt 32; `da` mit nicht definiertem Symbol muss mit Rückgabecode 16 enden).

Mit Version 1.00-015 kamen vier Negativtests hinzu (insgesamt 31): `makro_if_geschachtelt`, `makro_if_parameterzahl` und `makro_if_operator_lang` (Fehler in `$IF` eines Makros; die alte Fassung las dabei hinter das Zeilenfeld bzw. überschrieb den Stack).

Mit Version 1.00-013 kamen zwei Negativtests hinzu (insgesamt 28): `leeres_programm` und `dt_ohne_text`.

Mit Version 1.00-012 kamen sechs Negativtests hinzu (insgesamt 26): `makro_aufruf_parameter`, `belegung_ort`,
`division_null`, `bom_ok`, `zu_viele_zeilen`, `zeilenfeld_voll`. Die Referenz der Programme blieb unverändert.

## Neues Programm oder Negativtest aufnehmen

* Neues Programm: `.asm` ablegen, Ergebnis prüfen, dann `--referenz` ausführen.
* Neuer Negativtest: `negativ/<name>.asm` und `negativ/<name>.erwartet` anlegen.

## Zufallstest (Fuzzing)

`Regressionstest/fuzz.py` verändert die vorhandenen `.asm` zufällig (Zeilen löschen, vervielfachen, kürzen, lange Zeilen,
Sonderzeichen, BOM) und sucht Abstürze und Sanitizer-Meldungen. Er gehört nicht zum Standardlauf.

```
gcc -g -O1 -fsanitize=address,undefined -o /tmp/c82ass_asan Sourcecode/ca82_protokoll.c Sourcecode/ca82_standards.c Sourcecode/ca82_symbole.c Sourcecode/ca82_berichte.c Sourcecode/ca82_makros.c Sourcecode/ca82_zustand.c Sourcecode/ca82_hilfen.c Sourcecode/ca82_fehler.c Sourcecode/ca82_quelle.c Sourcecode/ca82_listing.c Sourcecode/ca82_pass0.c Sourcecode/ca82_pass1.c Sourcecode/ca82_pass2.c Sourcecode/ca82_ausdruck.c Sourcecode/ca82_codierung.c Sourcecode/ca82_pass3.c Sourcecode/ca82_fluss.c Sourcecode/ca82_testdatei.c Sourcecode/ca82_main.c
python3 Regressionstest/fuzz.py 2000 1      # Anzahl Läufe, Startwert
```

Kürzer: `make fuzz` (Läufe und Startwert mit `FUZZ_N=2000 FUZZ_SEED=7`); Rückgabecode 1, wenn etwas gefunden wurde.

Gefundene Fälle liegen in `/tmp/c82fuzzwork/fund_*.asm`; fehlerfrei heißt: Rückgabecode nur 0 oder 16, keine Sanitizer-Meldung.

Mit Version 1.00-021 kam der Negativtest `viele_fehler` hinzu (insgesamt 36): mehr als 20 Fehler werden nur zum Teil ausgegeben, danach folgt die Zusammenfassung.

Mit Version 1.00-022 kam der Negativtest `projekdetails_nicht_schreibbar` hinzu (insgesamt 37): kann `temp_projekdetails` nicht angelegt werden, endet der Lauf mit Warnung und Rückgabecode 0 statt mit einem Absturz. Dafür kennt das Prüfskript die Schlüsselwörter `vorher-verz` und `vorher-datei`. Außerdem wurden die veralteten Referenzdateien von `asm_0001_bsp_5_16` gelöscht (Fehlerfall, schreibt keine `.obj`/`.mqo`/`.dmp`/`.test`).
Mit Version 1.00-023 kam der Negativtest `makro_rekursion` hinzu (insgesamt 38): ein rekursiver Makroaufruf bricht den Lauf nicht mehr ab, weitere Fehler werden mit Zeile gemeldet.
Mit Version 1.00-024 kamen acht Negativtests hinzu (insgesamt 46): `warn_spr_datenwort`, `warn_spr_ok`, `warn_spr_leer`, `warn_tot`, `warn_tot_ok`, `warn_alle`, `warn_unbekannt`, `warn_ohne_option` (Optionen `-WARN=SPR`, `-WARN=TOT`, `-WARN=ALLE`). Die Referenz der 139 Programme blieb unverändert, weil die Warnungen nur mit der Option erscheinen und `.obj`, `.log`, `.dmp` nicht ändern.

Mit Version 1.00-025 kamen zwei Negativtests hinzu (insgesamt 48): `warn_log` und `warn_log_aus` prüfen mit den neuen Schlüsselwörtern `log-da` und `log-weg`, dass die Berichte von `-WARN=…` und `--xref` am Ende der `.log` stehen und ohne diese Optionen nicht. `makro_rekursion` prüft zusätzlich den Ort im Rekursionsfehler. Neu ist auch `make fuzz`.

Mit Version 1.00-027 kamen `xref_makro` (Makroexpansionen in der Querverweisliste) und `mnemonic_entfallen` (`add` ist kein Operationscode mehr) hinzu (insgesamt 50).
