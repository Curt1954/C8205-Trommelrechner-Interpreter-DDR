# Anforderung: Symbol-Literal `!<symbolname>` im Assembler c82ass

Version: 0.01-003
Status: umgesetzt in c82ass 1.03-005 (Doku 1.03-015, 10.11.2026); Freigabe zum Programmieren des Inhabers am 10.11.2026

## 1 Zweck

Wer eine Arbeits- oder Merkzelle braucht (Hilfszelle, Zähler, Zwischenwert), schreibt heute eine eigene Zeile `x dbn 1` an eine selbst gewählte Stelle. Das Symbol-Literal legt diese Zelle im Operanden an, ohne eigene Zeile, und lässt den Optimierer (Doku 5) sie in freie Zellen legen, wie er es bei `#`- und `@`-Literalen tut.

## 2 Syntax (Änderung an Doku 3.2)

```
<literal> ::= #<werteausdruck> | @<adressausdruck> | !<symbolname>
```

- `<symbolname>` ist ein Adresssymbol **ohne** Doppelpunkt (1 bis 32 Zeichen, Regeln wie beim Adresssymbol, Doku 3.2). Die Grammatik verwendet `<symbolname>`, weil `<symbol>` dort mit Doppelpunkt definiert ist.
- Die Beschreibung der Literale in 3.2 bekommt den Satz: Bei `!` wird kein Wert gespeichert; der Assembler legt eine Zelle mit dem Inhalt 0 an (wie `dbn 1`, Doku 3.3.2) und gibt ihr den Namen `<symbolname>`.
- Zulässig ist `!x` überall, wo auch `#` und `@` stehen dürfen: als Operand eines Befehls und hinter `da` (Doku 3.3.4). Bei `dw` nicht (eine Adresse ist dort unzulässig, 3.3.3).

## 3 Festlegungen

1. **Zelle:** wie `x dbn 1`: eine Zelle, Inhalt 0, in der Objektdatei die Zeile `000.` (3.3.2). Der Name `x` ist danach eine gewöhnliche Marke (Eintrag in `.sym` und Symboltabelle der `.log`).
2. **Mehrfach:** Derselbe Name in mehreren `!x` meint dieselbe Zelle (wie gleiche Werte bei `#` sich ein Literal teilen). Die Zelle entsteht beim ersten Auftreten im Quelltext.
3. **Namenskonflikt:** Gibt es zusätzlich eine Marke `x:`, ein `equ`- oder `abs`-Symbol `x`, ist das der Fehler „doppelt definiert“ (3.2).
4. **Optimierer (Entscheidung des Inhabers):** Die Zelle darf verlegt werden: wie ein Literal in eine freie Zelle vor dem Programmende (5.2), bei `FILL` auch in die Lücke eines verschobenen Blocks (5.4). Ihr Name gilt mit der neuen Adresse im ganzen Programm. Reihenfolge der Zellenwahl: Reihenfolge des ersten Auftretens, gemeinsam mit den `#`- und `@`-Literalen in einer Folge. Mit `--no-opt` steht sie im Literalbereich hinter dem ersten `end` (3.3.11, 5.3).
5. **Reihenfolge und Nachbarschaft (Entscheidung des Inhabers):** Der Programmierer verantwortet sie. Anders als bei `l0002-l0001` (5.2) unterbleibt die Umordnung nicht. Der Assembler **warnt**, wenn der Name eines `!`-Symbols in einem Rechenausdruck vorkommt (zum Beispiel `dw b-a`, `da x+1`); die Warnung ändert den Rückgabecode nicht (Rückgabecode 0). Als Ausdruck gilt jedes Vorkommen des Namens mit einem Rechenzeichen; das bloße `!x` und der Name als ganzer Operand zählen nicht.
6. **Pass 0 (Annahme des Entwurfs):** wie die Literalsymbole (Doku 4.x, `def`/`art`/`adr`/`abstand`): `def(x)` ergibt 0, solange nur `!x` die Zelle erzeugt; `adr` und `abstand` lehnen den Namen ab (Fehler „kommt nach Pass 2 nicht in der Symboltabelle vor“ bzw. Literalmarke), weil die Adresse sich durch den Optimierer ändert.
7. **Warnung `SYM`** („definiert, nirgends verwendet“): Ein `!x` ist immer verwendet, es meldet nichts.
8. **Ausgaben:** `.mqo`: Zeile `x dbn 1` am Ende bei den Literalen (wie `l0001 dw 5`); `.log`: Eintrag in der Literaltabelle (Art `!`); `.sym`: `x,<adresse>`; Listing: die Zelle an ihrer endgültigen Stelle.

## 4 Geklärte Punkte (Stand 10.11.2026, geprüft mit c82ass 1.03-006)

- **Name der Warnung:** Die Warnung (3, Punkt 5) ist standardmäßig eingeschaltet; `-WARN=NOSLIT` schaltet sie ab (gehört nicht zu `ALLE`). Wortlaut unverändert.
- **Makros:** `!$1` und `!z$V(n)` gehen (Name aus Parameter oder `$V`); derselbe Name in mehreren Aufrufen = dieselbe Zelle. Ein lokaler Makroname `!hilf%` ist kein gültiger Name (Fehler).
- **`$IF`/`$CALC`:** In `$IF` ist `!x` nur Text (Textvergleich, keine Zelle, keine Meldung); in `$CALC(!x+1)` ist es ein Fehler (rc 16). Gegenüber der früheren Annahme („in `$IF` Fehler“) bleibt das so, es wird nur dokumentiert.
- **Gruppengrenzen:** keine Sonderregel (wie bisher).

## 5 Umsetzung, wenn freigegeben

1. `Assembler.odt` zuerst (3.2 Grammatik und Literalbeschreibung, 3.3.4 bei `da`, 5.2, 5.3, Warnungsliste, Ausgaben), danach `.md` (Primat der `.odt`); beide Versionsdateien in die Lieferung.
2. C-Quelltext (Pass 1: Literaltabelle; Optimierer `ca82_opt.c`: Zellenwahl; Pass 0: `def`/`adr`/`abstand`; Warnung), `ca82_version.h` hochzählen (Haupt-/Unterversion erhöht nur der Inhaber) und `Assembler/version_abgleich.sh`.
3. Testprogramm unter `Assembler/Claude/` (Sollwerte im `;#PRUEFE`-Block, `Assembler/asm_und_test.sh`), Negativtests im Regressionstest (Namenskonflikt, `dw !x`, Warnung bei Ausdruck, `--no-opt`, `FILL`), danach `Assembler/Regressionstest/pruefe_alles.sh` (einmal mit ASAN vor der Lieferung).
