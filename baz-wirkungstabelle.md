# BAZ-Wirkungstabelle (Cache für den Claude-Interpreter)

Zweck: Für jeden bereits in einem Test aufgetretenen BAZ-Wert (Operationsteil, oktal,
B-A-Z) wird hier einmalig der Knotenpfad Knoten 10 bis 34 sowie die Wirkungsformel
festgehalten. Da dieser Teil des Knotenautomaten eine reine Funktion von B/A/Z ist
(vgl. ANWEISUNG-021), bleibt ein einmal eingetragener BAZ-Wert dauerhaft gültig -
solange sich die zugrundeliegenden Dokumente (C8205-Interpreter-Eingänge_der_Knoten.md, C8205-Interpreter-Beschreibung_der_Knoten.md [Variablentabelle T2], C8205-Interpreter-Befehlsliste-Zwischenstand.md) nicht ändern. Bei einer Korrektur dieser
Quelldateien ist der betroffene Eintrag hier neu herzuleiten.

Neue BAZ-Werte werden bei Auftreten ergänzt, nichts wird im Voraus vorbefüllt.

## Feststehender Rahmen (für JEDEN Befehl gleich, unabhängig vom BAZ - NICHT cachebar)

Diese Knoten sind laufzeitabhängig und werden bei jeder Instruktion neu ausgewertet,
auch wenn derselbe BAZ wiederholt auftritt (Schleifen!):

- **Vor der Dekodierung:** 1(od. Rücksprung)->2->3->4->5->8->9
  - Knoten 4 (ANWEISUNG-002, X-Abbruch-Merker): hängt vom VORIGEN Befehl ab, nicht vom
    aktuellen BAZ. I. d. R. falsch, außer direkt nach einem per X-Bedingung
    abgebrochenen GX-/WX-Befehl.
  - Knoten 5 (ANWEISUNG-003, Koinzidenz): laut Konvention der interpretativen
    Abarbeitung immer "wahr" (Wartezeit=0, wird übergangen).
- **Nach der Ausführung, vor Phase IV:** ...->26->28->31
  - Knoten 26 (ANWEISUNG-003, Koinzidenz): wie Knoten 5, immer "wahr" per Konvention.
  - Knoten 28 (ANWEISUNG-020, Überlauf FÜ vorhanden?): globaler Flag-Zustand,
    UNABHÄNGIG vom aktuellen BAZ. Wahr -> Knoten 30 (Endknoten "---", Rechner
    blockiert), egal welcher Befehl gerade dekodiert wurde.
- **Nach Phase IV:** 32->33->34(Test B=4-7) -> zurück zu Knoten 2 (falls B nicht in
  {4,5,6,7}; Gruppen-/Wiederholungsbefehle mit Phase-IV-Wiederholung sind hier noch
  nicht tabelliert).

Der eigentliche BAZ-Cache betrifft nur den Kernpfad **Knoten 10 bis 25 (Dispatch)
und 32/33 (Formel)**.

---

## Cache-Einträge

### BAZ 000 (oktal) — B=0, A=0, Z=0 — Unbedingter Sprung ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(falsch)->21(falsch)
->22(falsch)->24(**wahr**)->55(falsch, kein Überlauf)->59(**wahr**)->61

**Formel/Wirkung (statt 32/33 hier 61/62/63, da Sprungpfad):**
Knoten 62 (ANWEISUNG-022, Z=0 → R=0,L=0): keine Resultatbehandlung.
Eigentliche Sprungwirkung entsteht bereits strukturell durch Phase III (Knoten 16:
`<AR>:=<BZ>=ADR`); der Sprung besteht darin, dass AR **nicht** erneut über Phase I
(`<AR>:=<BZ>`) überschrieben wird, sondern über Knoten 63->7->6->5->8 direkt wieder
Phase II (Befehlsentnahme) an der bereits in AR stehenden Adresse ADR erfolgt.
Kein Speicher-/AC-Effekt.

---

### BAZ 211 (oktal) — B=2, A=1, Z=1 (L=1, R=0) — Einzel-Addition mit Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(**wahr**)->18->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)->28(falsch)->31

**Formel (32/33):**
Knoten 18 (Phase III, wegen L=1): `<AC>:=0`.
Knoten 32: `<AC>:=<AC>+<a>` (Festkomma-Addition).
Knoten 33 (Z=1 → R=0): keine Resultatbehandlung, AC bleibt Additionsergebnis.

---

### BAZ 050 (oktal) — B=0, A=5, Z=0 — Positivsprung ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25), Fall Sprungbedingung ERFÜLLT (⟨AC⟩ ≥ 0):**
10(falsch)->11->12(**wahr**)->13(ANWEISUNG-009, Teilbedingung B=0∧A=5∧AC≥0
**wahr**)->14(ANWEISUNG-010: interne Umstellung auf A=0)->15->16->17(falsch)
->19(falsch)->20(falsch)->21(falsch)->22(falsch)->24(**wahr**, da intern A=0)
->55(falsch)->59(**wahr**)->61

**Formel (statt 32/33 hier 61/62/63, da Sprung erfüllt):**
Wie BAZ 000: Sprung wird wie unbedingter Sprung ausgeführt (AR bleibt bei ADR,
direkter Rücksprung zu Phase II ohne Phase I). Keine AC-Wirkung.

*Hinweis:* Der Fall Sprungbedingung NICHT erfüllt (⟨AC⟩ < 0) ist mit diesem Test
noch nicht durchlaufen worden; Knoten 13 wäre dann falsch -> Pfad über 15(4. Eingang
über weitere Verzweigung)/decode weiter wie ein "normaler" Befehl ohne Sprungwirkung.
Dieser Teilfall ist hier noch nicht bestätigt und müsste bei Auftreten separat
verifiziert werden.

---

### BAZ 240 (oktal) — B=2, A=4, Z=0 — Einzel-Transport ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

**Formel (32/33):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, Speicherzelle a erhält AC-Inhalt).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung.

---

### BAZ 164 (oktal) — B=1, A=6, Z=4 (R=2, L=0) — Leer-Operation ohne Löschen

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

**Formel (32/33):**
Laut Organisationsbefehle-2.-Art-Tabelle (A=6, Z=4–7: "Leer-Befehl") und
Einzelbefehlsübersicht Nr. 66 ("164, 166 | Leer-Operation ohne Löschen") hat
Knoten 32 keine Ausführungsformel. Knoten 33 (Resultatbehandlung Z=4→R=2,
Linksverschiebung) bleibt für diesen als Leer-Operation definierten Code ohne
Wirkung — keine Änderung an AC oder Speicher.

**Besonderheit:** Löst bei Auftreten mit einer Adresse a, für die in der
Trommeldatei `#DOK-a` definiert ist, die Diagnoseausgabe gemäß Durchführung
eines Tests, Abschnitt 7, aus (unabhängig vom Cache-Eintrag hier, testspezifisch).

---

### BAZ 210 (oktal) — B=2, A=1, Z=0 (L=0, R=0) — Einzel-Addition ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch, Z=0→L=0)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

**Formel (32/33):**
Knoten 32: `<AC>:=<AC>+<a>` (Festkomma-Addition, AC bleibt vor der Ausführung
unverändert, da L=0).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung.

---

### BAZ 220 (oktal) — B=2, A=2, Z=0 (L=0, R=0) — Einzel-Subtraktion ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch, Z=0→L=0)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

**Formel (32/33):**
Knoten 32: `<AC>:=<AC>-<a>` (Festkomma-Subtraktion).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung.

---

### BAZ 241 (oktal) — B=2, A=4, Z=1 (L=1, R=0) — Einzel-Transport mit Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(**wahr**, Z=1→L=1)->18->19(falsch)
->20(falsch)->21(falsch)->22(falsch)->24(falsch)->25(falsch)
->26(wahr, Konvention)->28(falsch)->31

**Formel (32/33) — WICHTIGER SONDERFALL:**
Knoten 18 (Phase III, VOR Phase IV): `<AC>:=0`.
Knoten 32 (Phase IV): `<a>:=<AC>` — da AC bereits in Phase III gelöscht wurde,
wird hierdurch effektiv **0** in die Speicherzelle a geschrieben, nicht der vor
der Instruktion in AC stehende Wert! Ein vorheriger AC-Inhalt geht dabei
verloren.
Knoten 33 (Z=1 → R=0): keine Resultatbehandlung; AC bleibt 0.
Bestätigt durch Test #DOK-0011 (Zyklus 8: Speicherzelle 3021 wird auf 0
gesetzt statt den vorher berechneten AC-Wert -8 zu übernehmen).

---

### BAZ 544 (oktal) — B=5, A=4, Z=4 (R=2, L=0) — GX-Transport ohne Löschen, mit Linksverschiebung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

**Formel (32/33), abweichend vom Einzelbefehl: Gruppenschleife (32-33-34-35-36):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, wie B=2/B=4 A=4).
Knoten 33 (Z=4 → R=2): `<AC>:=Vl(<AC>)` (Linksverschiebung).
Knoten 34: B=4-7 → wahr (Gruppentyp, Schleife läuft weiter statt zu Knoten 2).
Knoten 35 (ANWEISUNG-024 = 040 ODER 041 ODER 042): für B=5 relevant sind 040
(32 Sektoren bearbeitet) und 042 (B=5∨7 UND AC<0, Vorzeichen bei R≠1 = z₀).
Solange beide falsch: Knoten 36 (a:=a+15 oktal mod 40, = nächste physische
Zelle der Spur gemäß Trommel-Interleaving) → zurück zu Knoten 32.
Wird 042 (oder 040) wahr, endet die Schleife SOFORT (kein Knoten 36 mehr,
kein "Nachziehen" einer weiteren Zelle) → zurück zu Knoten 2.

**Bestätigt durch Test #DOK-0007:** Start-AC mit einzigem Bit bei z₁₄ (positiv).
Nach jeder Runde wandert das Bit um eine Stelle Richtung z₀ (Linksshift).
Nach der 14. Runde (Zelle, die bei Start-ADR + 13 physische Schritte liegt)
erreicht das Bit z₀ → AC wird negativ → ANWEISUNG-042 sofort wahr → Abbruch
nach genau 14 bearbeiteten Zellen (nicht 15 — die "eine Wortzeit nach
Negativwerden" aus der Befehlsliste-Beschreibung beschreibt lediglich, dass
Operation+Resultatbehandlung der Zelle, in der die Negativität entsteht,
noch vollständig ausgeführt werden, nicht eine zusätzliche Folgezelle).
Die 18 nicht erreichten Zellen der Spur bleiben unverändert (Vorbelegung
`00000000000`, falls in der Trommeldatei
nicht anders definiert).

---

### BAZ 540 (oktal) — B=5, A=4, Z=0 (R=0, L=0) — GX-Transport ohne Löschen, ohne Verschiebung (X-Wiederholungs-Speicherbefehl)

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch, Z=0→L=0)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

(Identisch zum Standardrahmen — B=5 erfüllt keine der B=0/1-Sonderbedingungen
an den Knoten 10/12/19/20/21/22/24/25, wie bereits bei BAZ 544/640/744
festgestellt.)

**Formel (32/33), Wiederholungsschleife (32-33-34-35-36):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, wie B=2/4/5/6/7 A=4).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung, AC bleibt über die gesamte
Wiederholung hinweg unverändert (kein Vl/Vr wie bei den Z=4-Varianten
544/744 — Kernunterschied zu jenen Einträgen; identisches Verhalten zu
BAZ 640, dort jedoch B=6 statt B=5).
Knoten 34: B=4-7 → wahr (Gruppentyp, Schleife läuft weiter statt zu Knoten 2).
Knoten 35 (ANWEISUNG-024 = 040 ODER 041 ODER 042): für B=5 sind NUR 040 und
042 relevant (041 nur für B=6∨7, hier stets falsch):
  - 040 (32 Sektoren bearbeitet) — Obergrenze wie bei jedem Gruppentyp.
  - 042 (B=5∨7 UND AC<0) — X-Abbruch bei negativem AC.
Solange beide falsch: Knoten 36 (a:=a+15 oktal mod 40, nächste physische
Zelle der Spur) → zurück zu Knoten 32. Wird 042 (oder 040) wahr, endet die
Schleife SOFORT (kein Knoten 36 mehr) → zurück zu Knoten 2.

**Bestätigt durch Test #DOK-0003:** Startadresse 4001, AC-Startwert 64
(dezimal, positiv, konstant über die gesamte Wiederholung, da Z=0 keine
Verschiebung vornimmt). ANWEISUNG-042 (AC<0) wird daher nie wahr; die
Schleife läuft bis zum regulären Abbruch durch ANWEISUNG-040 nach genau
32 bearbeiteten Sektoren. Da die physische Schrittweite (+15 oktal) zu
40 oktal (32 Sektoren) teilerfremd ist, werden in diesen 32 Runden alle
32 Sektoren der Spur (4000–4037) genau einmal getroffen — anders als bei
BAZ 640 (Test #DOK-0005, Abbruch schon nach Sektor 23 durch ANWEISUNG-041,
nur 27 von 32 Zellen beschrieben) endet dieser Testfall erst nach
vollständigem Durchlauf aller 32 Zellen, die alle auf den AC-Wert 64
gesetzt werden. AR steht danach auf der zuletzt bearbeiteten Adresse 4024
(kein Nachziehen einer weiteren Zelle, analog 544/640/744).

---

### BAZ 440 (oktal) — B=4, A=4, Z=0 (R=0, L=0) — Reiner Gruppenbefehl, Transport ohne Löschen, ohne Verschiebung (Wiederholungs-Speicherbefehl, ohne X-Bedingung)

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch, Z=0→L=0)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

(Identisch zum Standardrahmen — B=4 erfüllt keine der B=0/1-Sonderbedingungen
an den Knoten 10/12/19/20/21/22/24/25, wie bereits bei BAZ 540/544/640/744
festgestellt.)

**Formel (32/33), Wiederholungsschleife (32-33-34-35-36):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, wie B=2/4/5/6/7 A=4).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung, AC bleibt über die gesamte
Wiederholung hinweg unverändert (kein Vl/Vr, identisch zu BAZ 540/640).
Knoten 34: B=4-7 → wahr (Gruppentyp, Schleife läuft weiter statt zu Knoten 2).
Knoten 35 (ANWEISUNG-024 = 040 ODER 041 ODER 042): für B=4 ist AUSSCHLIESSLICH
040 relevant — sowohl 041 (nur B=6∨7) als auch 042 (nur B=5∨7, X-Bedingung)
sind für B=4 strukturell stets falsch; dieser Befehlstyp kennt daher, anders
als GX (B=5) und WX (B=6/7), KEINEN vorzeitigen X- oder Sektor-23-Abbruch,
sondern ausschließlich die 32-Sektoren-Obergrenze:
  - 040 (32 Sektoren bearbeitet) — einzige Abbruchbedingung für B=4.
Solange 040 falsch: Knoten 36 (a:=a+15 oktal mod 40, nächste physische Zelle
der Spur) → zurück zu Knoten 32. Wird 040 wahr, endet die Schleife SOFORT
(kein Knoten 36 mehr) → zurück zu Knoten 2.

**Bestätigt durch Test #DOK-0002:** Startadresse 4001, AC-Startwert 64
(dezimal, positiv). Da für B=4 ohnehin nur 040 greift (042 strukturell
ausgeschlossen, unabhängig vom AC-Vorzeichen), läuft die Wiederholung stets
über exakt 32 Runden. Wie bei BAZ 540 (Test #DOK-0003, identische
Startadresse 4001) sind die physische Schrittweite (+15 oktal) und die
Sektorzahl (40 oktal = 32) teilerfremd, sodass alle 32 Sektoren der Spur
(4000–4037) in den 32 Runden genau einmal getroffen und auf den AC-Wert 64
gesetzt werden. AR steht danach auf der zuletzt bearbeiteten Adresse 4024.
Ergebnis (Speicherinhalt aller 32 Zellen, Endwerte AR/BZ/AC) identisch zu
BAZ 540 — der einzige Unterschied zwischen beiden Befehlen liegt in der
(hier nicht ausgelösten) X-Abbruchmöglichkeit bei negativem AC.

---

### BAZ 041 (oktal) — B=0, A=4, Z=1 (R=0, L=1) — Negativsprung mit Löschen

**Dispatch-Pfad (10–12), gemeinsam für beide Fälle:**
10(falsch)->11->12(**wahr**, ANWEISUNG-008: B=0∧A=4)->13(ANWEISUNG-009,
Teilbedingung B=0∧A=4∧AC<0)

**Fall A — Sprungbedingung ERFÜLLT (⟨AC⟩ < 0), NOCH NICHT DURCH TEST BESTÄTIGT:**
13(**wahr**)->14(ANWEISUNG-010: interne Umstellung auf A=0)->15->16->
17(**wahr**, Z=1→L=1)->18(AC:=0)->19(falsch)->20(falsch)->21(falsch)
->22(falsch)->24(**wahr**, da intern A=0)->55(falsch, kein Überlauf)
->59(**wahr**, da intern A=0)->61->62(Z=1→R=0, keine Resultatbehandlung)
->63->7->6->5->8 (Sprung wird wie unbedingter Sprung ausgeführt: AR bleibt
auf der Zieladresse a stehen, direkter Rücksprung zu Phase II ohne Phase I;
AC bleibt 0 durch die vorherige Löschung). Analog zum unbestätigten Fall
bei BAZ 050 (Positivsprung) — dort wie hier durch interne Umstellung auf
A=0 strukturell identisch zum unbedingten Sprung (BAZ 000).

**Fall B — Sprungbedingung NICHT erfüllt (⟨AC⟩ ≥ 0):**
13(**falsch**)->15->16->17(**wahr**, Z=1→L=1)->18(AC:=0)->19(falsch)
->20(falsch)->21(falsch)->22(falsch)->24(**wahr**, A=4 unverändert,
keine Umstellung)->55(falsch, kein Überlauf)->59(**falsch**, da A=4≠0,
keine Umstellung erfolgt)->60(ANWEISUNG-004, Zeitablauf)->2 (Eingang 6)

**Formel/Wirkung Fall B:** Kein Sprung; da L=1 unabhängig vom Sprungerfolg
bereits in Phase III (Knoten 18) ausgeführt wird, ist die einzige Wirkung
des Befehls das Löschen von AC (`<AC>:=0`). Kein Speicher-Effekt. BZ zeigt
nach Abschluss regulär auf den nächsten sequentiellen Befehl (BADR+1).

**Bestätigt durch Test #DOK-0014 (Zyklus bei Adresse 5002):** Fall B.
Startwert AC=64 (positiv, aus vorangegangener Addition), Sprungbedingung
(AC<0) daher nicht erfüllt; Befehl wirkt als reiner Löschbefehl (`<AC>:=0`),
kein Sprung, Fortsetzung mit dem sequentiell folgenden Befehl. Fall A
(Sprungbedingung erfüllt) ist durch keinen bisherigen Test durchlaufen
worden und müsste bei Auftreten separat verifiziert werden — insbesondere
die Annahme, dass Knoten 59 nach der Umstellung auf A=0 tatsächlich wahr
wird (strukturell identisch zur bestätigten Herleitung bei BAZ 000/050).

---

### BAZ 744 (oktal) — B=7, A=4, Z=4 (R=2, L=0) — WX-Transport ohne Löschen, mit Linksverschiebung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

(Identisch zum Standardrahmen — B=7 erfüllt keine der B=0/1-Sonderbedingungen
an den Knoten 10/12/19/20/21/22/24/25, ebenso wie bereits bei BAZ 544
festgestellt.)

**Formel (32/33), Wiederholungsschleife (32-33-34-35-36):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, wie B=2/4/5 A=4).
Knoten 33 (Z=4 → R=2): `<AC>:=Vl(<AC>)` (Linksverschiebung).
Knoten 34: B=4-7 → wahr (Schleife läuft weiter).
Knoten 35 (ANWEISUNG-024 = 040 ODER 041 ODER 042) — für B=7 sind ALLE DREI
Teilbedingungen relevant:
  - 040 (32 Sektoren bearbeitet) — Obergrenze wie bei jedem Gruppentyp.
  - 041 (B=6∨7 UND Sektor 23 erreicht) — nur ausgewertet, wenn Startsektor
    ≠ 0 (sonst Sonderfall „wirkt wie Gruppenbefehl", s. T2-Kommentar).
  - 042 (B=5∨7 UND AC<0) — wie beim GX-Befehl (BAZ 544).
  Bei WX gilt: welche der drei Bedingungen zuerst (in welcher Runde) wahr
  wird, entscheidet den Abbruch; es gilt kein Vorrang einer Bedingung vor
  den anderen (anders als ANWEISUNG-024s Kommentarzeile "ANWEISUNG-040 hat
  Vorrang" — jener Vorrang bezieht sich auf den GX/WX-Fall, in dem NORMALE
  und ZUSÄTZLICHE Abbruchbedingung GLEICHZEITIG in derselben Runde erfüllt
  sind, nicht auf einen Vergleich unterschiedlicher Rundenzahlen).

**Bestätigt durch Test #DOK-0006:** Startadresse 4001 (Sektor 01, also ≠0,
Sektor-23-Bedingung wird reguär ausgewertet). Mit demselben AC-Startwert
und derselben Formel wie bei BAZ 544 (Test #DOK-0007) wandert das einzige
AC-Bit identisch von z₁₄ Richtung z₀ und macht AC in Runde 14 negativ
(ANWEISUNG-042). Der logische Sektor 23 (oktal) wird in der physischen
Zugriffsreihenfolge dieser Spur erst in Runde 27 erreicht (ANWEISUNG-041),
also deutlich nach dem 042-Abbruch — für diesen konkreten Testfall ist
041 damit gegenstandslos, obwohl sie grundsätzlich ausgewertet würde.
Ergebnis (14 beschriebene Zellen, Endwerte AR/BZ/AC) identisch zu BAZ 544.

---

### BAZ 020 (oktal) — B=0, A=2, Z=0 — Unbedingter Stop 1. Art ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25, abweichend vom Standardpfad ab Knoten 20):**
10(falsch)->11->12(falsch)->15->16->17(falsch)->19(falsch)->20(**wahr**,
ANWEISUNG-043: A=2 ∧ z₃₀=0)->42(ANWEISUNG-014, **wahr**: B=0/1 ∧ A=2 ∧ z₃₀=0)
->45

**Formel:**
Knoten 45 (ANWEISUNG-030): Flag US:=1, Endzustand (ZST) — kein Ausgang, kein
Rücksprung zu Knoten 2. Kernpfad endet hier vorzeitig, Knoten 32/33 werden bei
diesem BAZ nicht durchlaufen.

---

### BAZ 640 (oktal) — B=6, A=4, Z=0 (R=0, L=0) — W-Transport ohne Löschen, ohne Resultatbehandlung

**Dispatch-Pfad (10–25):**
10(falsch)->11->12(falsch)->15->16->17(falsch, Z=0→L=0)->19(falsch)->20(falsch)
->21(falsch)->22(falsch)->24(falsch)->25(falsch)->26(wahr, Konvention)
->28(falsch)->31

(Identisch zum Standardrahmen — B=6 erfüllt keine der B=0/1-Sonderbedingungen
an den Knoten 10/12/19/20/21/22/24/25, wie bereits bei BAZ 544/744
festgestellt.)

**Formel (32/33), Wiederholungsschleife (32-33-34-35-36):**
Knoten 32: `<a>:=<AC>` (Transportbefehl, wie B=2/4/5/7 A=4).
Knoten 33 (Z=0 → R=0): keine Resultatbehandlung, AC bleibt über die gesamte
Wiederholung hinweg unverändert (kein Vl/Vr wie bei den Z=4-Varianten
544/744 — Kernunterschied zu jenen Einträgen).
Knoten 34: B=4-7 → wahr (Gruppentyp, Schleife läuft weiter statt zu Knoten 2).
Knoten 35 (ANWEISUNG-024 = 040 ODER 041 ODER 042): für B=6 sind NUR 040 und
041 relevant (042 nur für B=5∨7, hier stets falsch):
  - 040 (32 Sektoren bearbeitet) — Obergrenze wie bei jedem Gruppentyp.
  - 041 (B=6∨7 UND Sektor 23 erreicht) — nur ausgewertet, wenn Startsektor
    ≠ 0 (sonst wirkt der Befehl wie ein Gruppenbefehl, d. h. nur noch 040
    zählt, s. Befehlsliste 4.1.7).
Solange beide falsch: Knoten 36 (a:=a+15 oktal mod 40, nächste physische
Zelle der Spur) → zurück zu Knoten 32. Wird 041 (oder 040) wahr, endet die
Schleife SOFORT (kein Knoten 36 mehr) → zurück zu Knoten 2. Die Zelle, in
der die Abbruchbedingung eintritt, wird noch vollständig bearbeitet
("endet bei derjenigen [Zelle] mit der Sektornummer 23", Befehlsliste
4.1.7) — Abbruch nach genau dieser Zelle, nicht danach.

**Bestätigt durch Test #DOK-0005:** Startadresse 4001 (Sektor 01, also ≠0,
Sektor-23-Bedingung wird regulär ausgewertet). In der physischen
Zugriffsreihenfolge (Schrittweite +15 oktal je Runde) wird der logische
Sektor 23 (oktal) exakt in Runde 27 erreicht — identische Rechnung wie
beim GX-/WX-Test zu BAZ 544/744 (dieselbe Startadresse 4001), dort jedoch
zusätzlich durch den früheren AC<0-Abbruch (ANWEISUNG-042) überlagert, der
bei B=6 nicht existiert. Hier läuft die Wiederholung daher ungehindert bis
Runde 27 durch: 27 von 32 Zellen der Spur (4000–4037) werden mit dem
unveränderten AC-Wert beschrieben, 5 Zellen (4000, 4007, 4015, 4024, 4032 —
die in Runde 28–32 fälligen, nicht mehr erreichten Sektoren 00, 07, 13, 20,
26 oktal) bleiben bei ihrer Vorbelegung `00000000000`. AC selbst bleibt über den gesamten Befehl hinweg gleich dem vor der
Wiederholung im Akkumulator stehenden Wert (keine Linksverschiebung, anders
als bei 544/744).
