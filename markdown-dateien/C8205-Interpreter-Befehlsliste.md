### Befehlslisten ###

Version: 0.95-001

Maschinenbefehle, kurz auch nur Befehle genannt, werden bezüglich des Operationsteiles
BAZ bitweise dekodiert. Das ist die Grundlage der folgenden generischen Befehlsbeschreibung.

#
## generische Befehlszusammenfassung nach Befehlsarten
#

# Einleitung

Der Operationsteil eines Befehls besteht aus den drei
Triaden **B, A, Z**, die im Sinne eines analytischen Befehlscodes
weitgehend selbständige Bedeutung haben:

- **B** = Befehlstyp
- **A** = Operationsart
- **Z** = Operationszusatz — setzt sich zusammen aus dem Paar **R**
  (Resultatbehandlung) und dem **Löschbit L**.

(Bedeutung von A im Detail: s. Abschnitt 4.3 und "Einzelbefehlsübersicht" unten. Bedeutung von
Z im Detail: s. Abschnitt 4.2 unten.)

# Befehlstyp

Der Befehlstyp wird durch die Bits **z₂₄, z₂₅, z₂₆** angegeben (= Triade
B); er kann einen der acht Zahlenwerte 0 bis 7 besitzen. Durch die
verschiedenen Werte des Befehlstyps werden verschiedene Bedeutungen der
Operationsart festgelegt.

| B (oktal/dez. gleich, 0–7) | Bezeichnung | Kurzbeschreibung |
|---|---|---|
| 0 | Organisationsbefehl 1. Art | S. 4.1.1 |
| 1 | Organisationsbefehl 2. Art | S. 4.1.2 |
| 2 | Einzelbefehl | S. 4.1.3 |
| 3 | Markierter Einzelbefehl | S. 4.1.4 |
| 4 | Gruppenbefehl (G-Befehl) | S. 4.1.5 |
| 5 | Verkürzter Gruppenbefehl (GX-Befehl) | S. 4.1.6 |
| 6 | Wiederholungsbefehl (W-Befehl) | S. 4.1.7 |
| 7 | Verkürzter Wiederholungsbefehl (WX-Befehl) | S. 4.1.8 |

**4.1.1. Organisationsbefehl 1. Art (B=0)**
Charakterisiert durch B = 0. In Abhängigkeit von der Operationsart
brauchen nicht alle Phasen der Befehlsschleife durchlaufen zu werden;
die Phasen I oder IV können entfallen.

**4.1.2. Organisationsbefehl 2. Art (B=1)**
Charakterisiert durch B = 1. Der Phasenablauf kann wie bei
Organisationsbefehlen 1. Art modifiziert werden.

**4.1.3. Einzelbefehl (B=2)**
Charakterisiert durch B = 2. Die Operation bezieht sich auf eine
einzige Speicherzelle.

**4.1.4. Markierter Einzelbefehl (B=3)**
Charakterisiert durch B = 3. Zusätzlich zur Wirkung des Einzelbefehls
wird ein Vergleichszustand erzeugt. Welcher Vergleichszustand erzeugt
wird, ist vom Resultat eines Vergleichs abhängig. Für die Darstellung
wird der Inhalt des Vergleicher-Flip-Flop-Paares als zweistellige
Dualzahl aufgefaßt.

*Vergleichsmechanismus (Details zu 4.1.4):*
- Verglichen wird der Akkumulatorinhalt nach Phase III mit einer Größe
  v. Dabei ist v = ⟨a⟩ für Operationsarten A ≤ 3 mit dem Adreßteil a,
  und es ist v = 0 für Operationsarten A ≥ 4.
- Der Akkumulatorinhalt selbst ist zum Zeitpunkt des Vergleichs für
  alle markierten Einzelbefehle mit Löschanweisung gleich Null.
- Flip-Flop 1 bleibt eingeschaltet, wenn ⟨Ac⟩ ≤ v gilt; für ⟨Ac⟩ ≥ v
  bleibt Flip-Flop 2 eingeschaltet. Gilt ⟨Ac⟩ = v, so bleiben beide
  Flip-Flop eingeschaltet; der Wert des Vergleichszustandes ist dann
  gleich 3.
- Im Mechanismus des Vergleichersetzens werden zunächst am Ende von
  Phase III beide Flip-Flop eingeschaltet; der Vergleicher wird
  gesetzt (= 3). In Phase IV findet nur bei Ungleichheit von ⟨Ac⟩ und v
  eine Korrektur des Vergleichers statt, wobei beide Flip-Flop stets
  entgegengesetzt geschaltet werden.
- Notation: Das Symbol V(a, b) bedeutet im weiteren, daß a als ⟨Ac⟩
  mit b verglichen wird.

*Vergleichsregister Vgl1/Vgl2 — Zustandstabelle:*

| Vgl 2 | Vgl 1 | Bezeichnung |
|---|---|---|
| 0 | 1 | "Vgl 1 gesetzt" |
| 1 | 0 | "Vgl 2 gesetzt" |
| 1 | 1 | "Vgl 1 und Vgl 2 gesetzt", auch: "Vgl 3 gesetzt" |

**4.1.5. Gruppenbefehl (G-Befehl) (B=4)**
Charakterisiert durch B = 4. Beginnt wie ein Einzelbefehl, d. h. die
Phasen I bis III werden wie bei diesem ausgeführt. Phase IV bezieht
sich dagegen auf alle Zellen der Spur, zu der die im Adreßteil genannte
Zelle gehört; sie wird also 32-mal durchlaufen. Die Zellen dieser Spur
werden dabei in der Reihenfolge ihrer geometrischen Anordnung auf der
Trommel bearbeitet.

**4.1.6. Verkürzter Gruppenbefehl (GX-Befehl) (B=5)**
Charakterisiert durch B = 5. Beginnt wie ein Gruppenbefehl, hat aber
eine zusätzliche Abbruchbedingung (X-Bedingung).

- Die zusätzliche Abbruchbedingung besteht in der Negativität des
  Akkumulatorinhaltes; bei R≠1 wird z₀, bei R=1 wird z₃₂ als Vorzeichen
  interpretiert. Nachdem diese Abbruchbedingung erfüllt ist, werden
  Operation und Resultatbehandlung noch mit einer Sektornummer
  ausgeführt. Der Abbruch erfolgt spätestens nach voller Ausführung des
  Gruppenbefehls.
- Der nächste Befehl wird nach erfolgtem X-Abbruch ohne Wartezeit W₁
  sofort entnommen. Demnach wird die Spur für diese Befehlsentnahme
  durch den Inhalt des Befehlszählers bestimmt, während die
  Sektornummer in der zweiten Wortzeit nach Abbruch des GX-Befehles
  liegt; in der ersten Wortzeit nach dem Abbruch erfolgt Phase I.
- Wird die X-Bedingung nicht realisiert, so erfolgen Abbruch und
  Fortsetzung wie beim G-Befehl.
- Werden normale und zusätzliche Abbruchbedingungen gleichzeitig
  erfüllt, geschieht die Entnahme des nächsten Befehls so, als ob die
  normale Abbruchbedingung den Vorrang hätte. Genauer ist der
  Wirkungsmechanismus aus Abb. 10 zu entnehmen.
- Konsequenzen für die Programmfortsetzung (für den auf den GX-Befehl
  folgenden Befehl), wenn die X-Bedingung zum Abbruch führt: Wurde der
  X-Befehl aus der Zelle b entnommen, so hat der Befehlszähler nach
  Phase III des nächsten Befehls den Inhalt b+2. Ist der nach dem
  GX-Befehl entnommene Befehl ein tatsächlich auszuführender
  Sprungbefehl (Sprung ohne Bedingung oder bedingter Sprung mit
  erfüllter Bedingung), so wird dieser Befehlszählerinhalt nicht
  ausgewertet. Wird kein Sprung ausgeführt, so wird der nunmehr folgende
  Befehl aus Zelle b+2 entnommen.

*Ausführliches Beispiel zum GX-Befehl (Befehl 520): s. „Beispiel: Befehl 520“ am Ende der Einzelbefehlsübersicht.*

**4.1.7. Wiederholungsbefehl (W-Befehl) (B=6)**
Charakterisiert durch B = 6. Der Wiederholungsbefehl wirkt wie ein
Gruppenbefehl mit anderer Abbruchbedingung für die Wiederholung. Er
beginnt bei der im Adreßteil angegebenen Speicherzelle und endet bei
derjenigen mit der (oktalen) Sektornummer 23; ein Wiederholungsbefehl
mit einer Adresse mit der Sektornummer 0 wirkt wie ein Gruppenbefehl
mit derselben Adresse. Durch einen Wiederholungsbefehl kann also eine
n-malige Ausführung von Operationen mit 1 ≤ n ≤ 32 realisiert werden.

**4.1.8. Verkürzter Wiederholungsbefehl (WX-Befehl) (B=7)**
Charakterisiert durch B = 7. Der verkürzte Wiederholungsbefehl beginnt
wie ein Wiederholungsbefehl, hat aber dieselbe zusätzliche
Abbruchbedingung wie der verkürzte Gruppenbefehl. Der Abbruch erfolgt
spätestens nach voller Ausführung des Wiederholungsbefehls. Die
Programmabarbeitung wird wie beim verkürzten Gruppenbefehl fortgesetzt.

### 4.2. Operationszusatz

Der Operationszusatz Z steht in den Bits z₃₀, z₃₁, z₃₂; er hat also
einen der acht Zahlenwerte 0 bis 7. Das Bitpaar z₃₀, z₃₁ besitzt die
Bedeutung der Resultatbehandlung R, das Bit z₃₂ die Bedeutung der
Löschanweisung L.

**4.2.1. Resultatbehandlung**

Die Resultatbehandlung geschieht stets nach Ausführung der Operation
in Phase IV und bezieht sich auf den Inhalt des Akkumulators. Bei
einigen Organisationsbefehlen wird dieser Teil der Befehlsschleife
nicht durchlaufen; die Resultatbehandlung ist dann wirkungslos. Es gibt vier Möglichkeiten der
Resultatbehandlung, die den Zahlenwerten 0 bis 3 entsprechen.

- **R = 0:** keine Resultatbehandlung; Bitpaar z₃₀, z₃₁ wirkungslos:
  ⟨Ac⟩ := ⟨Ac⟩
- **R = 1:** Rechtsverschiebung. Das Resultat wird um ein Bit nach
  rechts verschoben; das rechts überlaufende Bit geht verloren, z₀
  wird mit 0 besetzt:
  ⟨Ac⟩ := ½ · ⟨Ac⟩ =def V_r^I (⟨Ac⟩)
- **R = 2:** Linksverschiebung. Das Resultat wird um ein Bit nach
  links verschoben; das links überlaufende Bit geht verloren, z₃₂ wird
  mit 0 besetzt:
  ⟨Ac⟩ := 2 · ⟨Ac⟩ =def V_l^I (⟨Ac⟩)
- **R = 3:** zyklische Linksverschiebung. Das Resultat wird um ein Bit
  nach links verschoben; das links überlaufende Bit wird in die Stelle
  z₃₂ übertragen:
  ⟨Ac⟩ := 2 · ⟨Ac⟩ + z₀ · 2⁻³² =def V_zl^I (⟨Ac⟩)

**4.2.1a. Verallgemeinerung: Vr/Vl auf beliebigen Registern**

Die obigen Formeln sind hier für AC angegeben; an anderer Stelle dieser Datei (z. B. 4.3-Formeln wie "Vr⟨BZ⟩", "Vr⟨a⟩") wird dieselbe Bit-Operation auf andere Register/Operanden angewendet. Bit-exakte Definition, allgemein für ein Register X:

- **Vr** (Rechtsverschiebung): `X := X um 1 Bit rechtsverschoben; z₀ := 0` (das rechts herausfallende Bit z₃₂ geht verloren, sofern nicht zyklisch).
- **Vl** (Linksverschiebung): `X := X um 1 Bit linksverschoben; z₃₂ := 0` (das links herausfallende Bit z₀ geht verloren, sofern nicht zyklisch).
- **Zyklisch** (in diesem Befehlssatz nur als zyklische Linksverschiebung, R=3, realisiert): statt der 0-Belegung wird das herausfallende Bit auf die freiwerdende Stelle übertragen — allgemein formuliert: bei zyklischer Verschiebung gilt `z₀ := z₃₂` bzw. `z₃₂ := z₀` (je nach Richtung), d. h. das jeweils "herausfallende" Bit wird an der anderen Seite wieder eingespeist statt verworfen. Für R=3 entspricht das genau der oben angegebenen Formel `V_zl^I`.
- **Kein Überlauf durch Verschiebung:** Laut Definition des Überlauf-Sprungs (A=7, s. u.) entsteht ein Überlauf ausschließlich bei Add., Subtr., bedingter Add./Sub. oder R-Operation (Zahlenbereich überschritten) – **keine** Verschiebung (Vr, Vl, zyklisch) erzeugt einen Überlauf. (Korrektur einer eigenen früheren Fehlannahme.) Überlauf wird außerdem nur bei R=0 (Z=0 oder 1, ohne Resultatbehandlung) eingeschaltet (Programmieranleitung 4.3.2.10, bestätigt 03.10.2026).
- **Notation "(a₁a₂a₃a₄)_X" / "(b₁b₂b₃b₄)_X":** a₁a₂a₃a₄ bzw. b₁b₂b₃b₄ bezeichnen stets die 4 Oktal-Triaden einer Adresse a (=ADR), also die Bits z₁₂–z₂₃ (Spur z₁₂–z₁₈, Sektor z₁₉–z₂₃) eines Maschinenwortes – dieselbe feste Bit-Lage wie beim Adreßteil jedes Befehlswortes (s. Datei "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md"). Der Suffix (_AC bzw. _AR) gibt an, in welchem Register diese Bits gerade stehen: `(a₁a₂a₃a₄)_AC` = Bits z₁₂–z₂₃ des (33-Bit-)Registers AC, ausgelesen wie ein Adreßteil; `(b₁b₂b₃b₄)_AR` = Bits z₁₂–z₂₃ des (12-Bit-)Registers AR, was wegen AR's Breite mit ⟨AR⟩ insgesamt übereinstimmt.

**4.2.2. Löschbit**

Das Löschbit wird in Phase III wirksam und bezieht sich auf den Inhalt
des Akkumulators. Es gibt zwei Möglichkeiten.

Hat das Löschbit den Wert L = 0, so ist es wirkungslos. Für L = 1 wird
der Akkumulatorinhalt in Phase III des Befehls, der die
Löschanweisung enthält, gelöscht: alle Bits werden zu Null.

**4.2.3. Zusammenfassung von Resultatbehandlung und Löschanweisung**

Aus den vier Möglichkeiten für die Resultatbehandlung und den zwei
Möglichkeiten für die Löschanweisung ergeben sich acht mögliche Werte
für den Operationszusatz mit ihren verschiedenen Bedeutungen:

| Z | Bedeutung |
|---|---|
| 0 | keine Löschung, keine Resultatbehandlung |
| 1 | Löschen, keine Resultatbehandlung |
| 2 | keine Löschung, Rechtsverschiebung |
| 3 | Löschen, Rechtsverschiebung |
| 4 | keine Löschung, Linksverschiebung |
| 5 | Löschen, Linksverschiebung |
| 6 | keine Löschung, zyklische Linksverschiebung |
| 7 | Löschen, zyklische Linksverschiebung |

### 4.3. Vollständige Befehlsübersicht (Original-Tabelle, mehrteilig)

**Anmerkung (Konsistenzprüfung gegen die Einzelbefehlsübersicht, alle 512 Codes gegengeprüft, s. Abschnitt "Einzelbefehlsübersicht"):**
Vollständigkeit bestätigt (alle 512 Codes 000–777 oktal genau einmal vorhanden, keine Lücken/Duplikate). Bei den Zeilen A=0 (Konjunktion in AC) und A=6 (Konjunktion mit negiertem AC) gilt zusätzlich, obwohl hier pauschal "Z=0…7" angegeben ist: für die vier Z-Werte mit L=1 (Löschen; Z=1,3,5,7) wird die jeweilige Formel durch das vorherige Löschen des AC (Phase III) wirkungslos – A=0: ⟨AC⟩:=0∧⟨a⟩=0; A=6: ⟨a⟩:=(¬0)∧⟨a⟩=⟨a⟩ (Speicherzelle bleibt unverändert) – und ist in der Einzelbefehlsübersicht deshalb konsequent als „Leer-Operation" geführt (gilt gleichermaßen für B=2, B=3 [markiert], B=4–7 [G/GX/W/WX]).

ERGEBNIS (korrigiert 05.10.2026): z₃₂ in der A=3-Variantenformel (A=3, Z=2,3) ist das **niederwertigste Bit des Akkumulators** (⟨AC⟩ nach Phase III), nicht das Löschbit L des Befehls – dieselbe Lesart wie bei A=7/Z=2, wo die Tabelle ausdrücklich „(z₃₂)_AC“ schreibt. Die frühere Deutung z₃₂ = L (und damit „bei Z=2 nie Addition“) war falsch: Sie ist mit der Multiplikation der Programmieranleitung 6.1.2 und 6.2.1 (Befehle 7700 432 und 7700 462) unvereinbar, wo das jeweils niederwertigste Bit des Multiplikators über die Addition entscheidet und der Multiplikator durch die Rechtsverschiebung abgebaut wird. Maßgebliche Wirkung: z₃₂(AC) = 1 → ⟨AC⟩ := Vr[⟨AC⟩ + ⟨a⟩] (ein Übertrag aus der Addition rückt als z₀ nach der Verschiebung ein); z₃₂(AC) = 0 → ⟨AC⟩ := Vr⟨AC⟩. Für A=7/Z=3 besteht kein Widerspruch: dort gibt 4.3 bereits direkt „⟨AC⟩:=0“ an (eigene Formelzeile, unabhängig von Vr-Berechnung), passend zu „Leer-Operation“.

Für A=3/Z=3 (Codes 233, 433, 533, 633, 733) besteht ebenfalls **kein** Widerspruch zur Einzelbefehlsübersicht: Das Löschen (L=1) wirkt bereits in Phase III, also ist ⟨AC⟩ = 0 und damit z₃₂(AC) = 0; die Formel ergibt `⟨AC⟩:=Vr⟨AC⟩=0`, das ist die „Leer-Operation“ der Einzelbefehlsübersicht. (Unter der früheren, falschen Deutung z₃₂ = L hätte sich scheinbar `Vr⟨a⟩` ergeben und einen Widerspruch vorgetäuscht.)
**Auflösung (Grundsatz, gilt für alle künftigen Widersprüche dieser Art):** Die Einzelbefehlsübersicht ist die unmittelbare Definition je Oktalcode; diese Tabelle (4.3) ist eine generische Ableitung über A/Z-Bereiche und steht bei Widerspruch zurück. Für Z=3 gilt verbindlich „Leer-Operation" (Einzelbefehlsübersicht). Seit der Korrektur vom 05.10.2026 (z₃₂ = niederwertigstes AC-Bit) ist die Formel dieser Zeile damit auch verträglich, weil ⟨AC⟩ bei Z=3 durch das Löschen bereits 0 ist; ein Widerspruch besteht hier nicht mehr. Der Grundsatz bleibt für künftige Fälle bestehen.

**Notation der Sprungbefehle (Originaldokumentation):** Die Originaltabelle beschreibt jeden Sprungbefehl als Fallunterscheidung: nächster Befehl := a, falls die Sprungbedingung erfüllt ist, sonst nächster Befehl := ⟨BZ⟩ + 1°. Beim unbedingten Sprung (000) gilt immer a. Die Bedingungen: 040 ⟨AC⟩ < 0; 050 ⟨AC⟩ ≥ 0; 070 Überlauf; 140 Vergleicher 1 oder 3; 150 Vergleicher 2 oder 3; 170 Vergleicher 3 (die Bedingung der Codes mit A=4/5/7 gilt für alle Z-Werte, s. Tabellen unten). **1° bedeutet eine Adresseinheit**, also die nächste Zelle: Im Befehlszähler, der nur Adressen kennt, ist 1° = 1. Zur Darstellung im Maschinenwort s. "C8205-Interpreter-Datenstruktur_und_Verarbeitungseinheiten.md" (Abschnitt Maschinenwort, Adresseinheit). Die Wirkung bei nicht erfüllter Bedingung (Befehl aus Zelle b+1, ohne Phase IV, ohne Verschiebung) bildet der Knotenautomat ab (ANWEISUNG-001 in Phase III, Knoten 59 und 60).

**Organisationsbefehle 1. Art (B=0)**

| A | Z | Befehl | Formel/Bemerkung |
|---|---|---|---|
| 0 | 0,1,2,3,4,5,6,7 | Unbedingter Sprung | Fortsetzung des Programms mit dem Befehl, dessen Adresse im Adreßteil des Sprungbefehls steht |
| 1 | 0,1,2,3,4,5,6,7 | Eingabebefehl 1. Art | Rechner erwartet Eingabe eines Zeichens über angewähltes Eingabegerät |
| 2 | 0,1,2,3 | Unbedingter Stop 1. Art | — |
| 2 | 4,5,6,7 | Unbedingter Sprung mit Rückkehrabsicht | ⟨AC⟩ := Vr⟨BZ⟩ ∨ ⟨AC⟩ |
| 3 | 0,1,2,3,4,5,6,7 | Ausgabe-/Anwahl-Befehl | Ausgabe eines Zeichens über angewähltes Ausgabegerät. a=4700 (oktal): Anwahl Kanal 0 (Tastatur oder SW-Eingabe). a=4600 (oktal): Anwahl Kanal 1 (Leser 1 oder Stanzer). a=4500 (oktal): Anwahl Kanal 2 (Leser 2 oder SW-Ausgabe). Ist z₁₂=0, wird ein Zeichen ausgegeben; Stanzer: Bits z₁₃–z₂₀ (1 = gelocht), Schreibwerk: nur z₁₄, z₁₅, z₁₇–z₂₀. Die Anwahl bleibt bis zur nächsten Anwahl erhalten. Fehlt das Ausgabegerät (K0, K3, keine Anwahl) oder wird eine nicht existierende Anwahl programmiert, stoppt der Rechner mit gesetztem Flag A (Lampe A). Der AC unterliegt nur der Löschanweisung (keine Resultatbehandlung, Phase IV läuft nicht ab). Die acht Operationsteile 030–037 unterscheiden sich nur durch die Löschanweisung. Von der Stelle unmittelbar nach der Löschanweisung (Phase III) bis zum Beginn der Phase I vergehen mindestens zwei Wortzeiten (Originaldokumentation 4.3.2.5, Abb. 21; im Interpreter gilt Wartezeit=0). Eine Umstellung der Operation nach Phase III in Überlaufsprung oder Vergleichersprung 3 ist für die Wirkung des Befehls bedeutungslos, weil die Auswertung der Sprungbedingung nur vorher in Phase II erfolgen kann (ebenda; im Knotengraphen nicht abgebildet). Bei vorhandenem Überlauf folgt nach der Ausgabe bzw. Anwahl ein Halt wegen Überlauf (Originaldokumentation 4.3.2.5, Abb. 21) |
| 4 | 0,1,2,3,4,5,6,7 | Negativ-Sprung | Sprung bei ⟨AC⟩ < 0. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |
| 5 | 0,1,2,3,4,5,6,7 | Positiv-Sprung | Sprung bei ⟨AC⟩ ≥ 0. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |
| 6 | 0,1,2,3 | Bedingter Stop | Stop am Ende der Phase III, wenn Schalter "BS" gesetzt. Bemerkung: wenn Schalter "BS" nicht gesetzt, keine Verschiebung |
| 6 | 4,5,6,7 | Bedingter Sprung mit Rückkehrabsicht | wie Unbedingter Sprung mit Rückkehrabsicht, wenn Schalter "SP" gesetzt. Bemerkung: wenn Schalter "SP" nicht gesetzt, keine Verschiebung |
| 7 | 0,1,2,3,4,5,6,7 | Überlauf-Sprung | Sprung, wenn bei Add., Subtr., bed. Add. oder R-Operation als Einzel- oder markierter Einzelbefehl ohne Resultatbehandlung (R=0) der Zahlenbereich überschritten wird. Bei vorhandenem Überlauf wird der Befehl wie ein unbedingter Sprung ausgeführt und der Überlauf dabei gelöscht. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |

**Organisationsbefehle 2. Art (B=1)**

| A | Z | Befehl | Formel/Bemerkung |
|---|---|---|---|
| 0 | 0,1,2,3,4,5,6,7 | Unbedingter Sprung 2. Art | wie Unbedingter Sprung 1. Art |
| 1 | 0,1,2,3,4,5,6,7 | Eingabebefehl 2. Art | wie Eingabebefehl 1. Art. Bemerkung: wenn keine Umstellung in Sprungbefehl, Korrektur des Vergleicherstandes (Vgl 3 kann nicht gesetzt werden) |
| 2 | 0,1,2,3 | Unbedingter Stop 2. Art | bis zum "Halt" wie unbedingter Stop 1. Art wirkend |
| 2 | 4,5,6,7 | Unbedingter Sprung mit Rückkehrabsicht 2. Art | wie unbedingter Sprung mit Rückkehrabsicht 1. Art |
| 3 | 0,1,2,3,4,5,6,7 | Ausgabe-/Anwahl-Befehl | wie 0 3 Z |
| 4 | 0,1,2,3,4,5,6,7 | Vergleicher-Sprung 1 | wie unbedingter Sprung, wenn Vgl 1 oder Vgl 3 gesetzt. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |
| 5 | 0,1,2,3,4,5,6,7 | Vergleicher-Sprung 2 | wie unbedingter Sprung, wenn Vgl 2 oder Vgl 3 gesetzt. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |
| 6 | 0,1,2,3 | Bedingter Stop 2. Art | wenn Schalter "BS" gesetzt, bis zum "Halt", oder wenn Schalter "BS" nicht gesetzt, wie 0 6 Z (Z<4) |
| 6 | 4,5,6,7 | Leer-Befehl | Bemerkung: befohlene AC-Löschung wird ausgeführt |
| 7 | 0,1,2,3,4,5,6,7 | Vergleicher-Sprung 3 | wie unbedingter Sprung, wenn Vgl 3 gesetzt. Bemerkung: bei nicht erfüllter Sprungbedingung keine Verschiebung |

**Einzelbefehle (B=2)**

| A | Z | Befehl | Formel/Bemerkung |
|---|---|---|---|
| 0 | 0,1,2,3,4,5,6,7 | Konjunktion in AC | ⟨AC⟩ := ⟨AC⟩ ∧ ⟨a⟩ |
| 1 | 0,1,2,3,4,5,6,7 | Festkomma-Addition | ⟨AC⟩ := ⟨AC⟩ + ⟨a⟩ |
| 2 | 0,1,2,3,4,5,6,7 | Festkomma-Subtraktion | ⟨AC⟩ := ⟨AC⟩ − ⟨a⟩ |
| 3 | 0,1,4,5,6,7 | Bedingte Festkomma-Addition/Subtraktion | wenn ⟨AC⟩<0: ⟨AC⟩:=⟨AC⟩+⟨a⟩; wenn ⟨AC⟩≥0: ⟨AC⟩:=⟨AC⟩−⟨a⟩ |
| 3 | 2,3 | Bedingte Festkomma-Addition/Subtraktion (Variante) | wenn (z₃₂)_AC=1: ⟨AC⟩:=Vr[⟨AC⟩+⟨a⟩]; wenn (z₃₂)_AC=0: ⟨AC⟩:=Vr⟨AC⟩ (z₃₂ = niederwertigstes Bit des AC, nicht das Löschbit; Anwendung: Multiplikation, Programmieranleitung 6.1.2 und 6.2.1) |
| 4 | 0,1,2,3,4,5,6,7 | Transportbefehl | ⟨a⟩ := ⟨AC⟩ |
| 5 | 0,2,4,6 | Konjunktion im Speicher mit ⟨AC⟩ | ⟨a⟩ := ⟨AC⟩ ∧ ⟨a⟩ |
| 5 | 1,3,5,7 | R-Befehl (Umstellung in Addition) — funktional: R-Lesebefehl (indirektes Lesen über berechnete Adresse) | ⟨AC⟩ := ⟨(a₁a₂a₃a₄)_AC ∨ (b₁b₂b₃b₄)_AR⟩ ; Beispiel (a=0000, also ⟨AR⟩=0000): "0000 251" (Z=1) → ⟨AC⟩:=⟨a₁a₂a₃a₄⟩, d. h. AC wird durch den Inhalt der Speicherzelle ersetzt, deren Adresse gerade in den Triaden t5–t8 von AC steht. Zweck: da beim C 8205 kein Indexregister verdrahtet ist, laufen alle Adreßrechnungen (Adressenänderung) über AC; mit diesem Befehl wird in einem Schritt über die selbst berechnete Adresse dereferenziert. Formel ist bereits die VOLLSTÄNDIGE Wirkung, keine weitere "Umstellung/Re-Dispatch" nötig. Validierter Testfall (Original-Beispiel "Bringe Inhalt von A nach 7774", Programm ab 3710, AC=0000 "A" 000 zu Beginn — Variante mit R-Lesebefehl): `3710: 0000 251` (⟨AC⟩:=⟨A⟩) → `3711: 7774 240` (Transport: ⟨7774⟩:=⟨AC⟩) → `3712: 0000 020` (Unbedingter Stop). Ohne R-Lesebefehl (Variante 1) braucht dasselbe Ergebnis 6 statt 3 Speicherplätze (erst Lesebefehl in AC konstruieren, abspeichern nach 3712, dann erst ausführen). |
| 6 | 0,1,2,3,4,5,6,7 | Konjunktion im Speicher mit negiertem AC | ⟨a⟩ := (¬AC) ∧ ⟨a⟩ — "negierter AC" = binäre (bitweise) Negation des Akkumulatorinhalts, Ergebnis dann bitweise UND-verknüpft mit dem Inhalt der Speicherzelle a |
| 7 | 0,4,6 | Vorzeichenbefehl (bedingte Speicherlöschung) | wenn ⟨AC⟩≥0: ⟨a⟩:=0 |
| 7 | 2 | Vorzeichenbefehl (bedingte Speicherlöschung), Variante | wenn (z₃₂)_AC=0: ⟨a⟩:=0 |
| 7 | 1,5,7 | R-Befehl (Umstellung in bed. Add./Sub.) — funktional: R-Minuslesebefehl (indirektes Lesen, negiert) | ⟨AC⟩ := −⟨(a₁a₂a₃a₄)_AC ∨ (b₁b₂b₃b₄)_AR⟩ ; Beispiel (a=0000): "0000 271" (Z=1) → ⟨AC⟩:=−⟨a₁a₂a₃a₄⟩, holt das NEGATIVE Maschinenzahlwort der berechneten Adresse nach AC. Analog zu A=5/Z=1,3,5,7 (s. dort), nur mit Negation des gelesenen Wortes. |
| 7 | 3 | R-Befehl (Umstellung in bed. Add./Sub.), Variante | ⟨AC⟩ := 0 |

**Markierte Einzelbefehle (B=3)**

| A | Z | Befehl | Formel/Bemerkung |
|---|---|---|---|
| 0 | 0,1,2,3,4,5,6,7 | wie B=2, zusätzlich Setzen des Vergleichers vor Ausführung der Operation | Vgl 1, wenn ⟨AC⟩<⟨a⟩ |
| 1 | 0,1,2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | Vgl 2, wenn ⟨AC⟩>⟨a⟩ |
| 2 | 0,1,2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | Vgl 3, wenn AC=⟨a⟩ |
| 3 | 2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | (Vergleichersetzung wie oben) |
| 3 | 0,1 | keine Operation, nur Setzen des Vergleichers | Vgl 1 wenn ⟨AC⟩<⟨a⟩; Vgl 2 wenn ⟨AC⟩>⟨a⟩; Vgl 3 wenn ⟨AC⟩=⟨a⟩. Bemerkung: befohlene AC-Löschung wird ausgeführt |
| 4 | 0,1,2,3,4,5,6,7 | wie B=2, zusätzlich Setzen des Vergleichers vor Ausführen der Operation | Vgl 1, wenn ⟨AC⟩<0 |
| 5 | 0,1,2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | Vgl 2, wenn ⟨AC⟩>0 |
| 6 | 0,1,2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | Vgl 3, wenn ⟨AC⟩=0 |
| 7 | 0,1,2,3,4,5,6,7 | (Fortsetzung obiger Gruppe) | (Vergleichersetzung wie oben) |

**Gruppenbefehle (B=4)**

Operationsausführung wie bei B=2, aber mit allen Zellen der Spur, zu
der die durch den Adreßteil festgelegte Zelle gehört (Phasen I bis III
werden einmal, Phase IV 32-mal durchlaufen). Die Abarbeitung erfolgt in
der Reihenfolge der geometrischen Anordnung der Zellen, beginnend mit
der im Adreßteil angegebenen Zelle.

**Verkürzte Gruppenbefehle (GX-Befehle) (B=5)**

Operationsausführung wie bei B=4, es erfolgt jedoch Abbruch der Phase
IV eine Wortzeit nach Negativwerden des Akkumulatorinhalts
(X-Bedingung), d. h. Operation und Resultatbehandlung werden noch mit
einer Zelle ausgeführt. Bei Rechtsverschiebung (R=1) wird z₃₂ als
Vorzeichen interpretiert, sonst (R≠1) z₀. Wird das Vorzeichen des
Akkumulatorinhalts während einer Trommelumdrehung nicht negativ, so
erfolgt Abbruch wie bei G-Befehl.

**Wiederholungsbefehle (W-Befehle) (B=6)**

Operationsausführung wie bei B=4, es erfolgt jedoch Abbruch der Phase
IV, sobald die Sektornummer 00 (oktal) erreicht ist.

**Verkürzte Wiederholungsbefehle (WX-Befehle) (B=7)**

Operationsausführung wie bei B=5, es erfolgt jedoch Abbruch der Phase
IV wie bei GX-Befehl nach Negativwerden des Akkumulatorinhalts. Wird
das Vorzeichen des Akkumulatorinhalts vor Erreichen der Sektornummer 00
(oktal) nicht negativ, erfolgt Abbruch wie bei W-Befehl.

#
## Einzelbefehlsübersicht
#

*Original-Quelle: separates Dokument, lexikographisch (nach Oktalcode)
geordnete Aufzählung "aller Operationsteile in Gruppen mit
verschiedener Wirkung zusammengefaßt". Codes sind
dreistellige Oktalzahlen, gelesen als B-A-Z (Befehlstyp-Operationsart-
Operationszusatz). Mehrere Codes in einer
Zeile = laut Original identische Wirkung trotz unterschiedlicher
Bit-Repräsentation.*

*Ein Befehl dieser Liste ist ausführlich durchgerechnet: Nr. 234, Code 520 (GX-Subtraktion), s. „Beispiel: Befehl 520“ am Ende dieses Abschnitts.*

| Nr. | Code(s) (oktal, B-A-Z) | Original-Beschreibung |
|---|---|---|
| 1 | 000, 100 | unbedingter Sprung ohne Löschen, ohne Resultatbehandlung |
| 2 | 001, 003, 005, 007, 101, 103, 105, 107 | unbedingter Sprung mit Löschen |
| 3 | 002, 102 | unbedingter Sprung mit Rechtsverschiebung |
| 4 | 004, 104 | unbedingter Sprung mit Linksverschiebung |
| 5 | 006, 106 | unbedingter Sprung mit zyklischer Linksverschiebung |
| 6 | 010 | Eingabe-Halt 1. Art ohne Löschen, ohne Resultatbehandlung |
| 7 | 011 | Eingabe-Halt 1. Art mit Löschen, ohne Resultatbehandlung |
| 8 | 012 | Eingabe-Halt 1. Art ohne Löschen, mit Rechtsverschiebung |
| 9 | 013 | Eingabe-Halt 1. Art mit Löschen, mit Rechtsverschiebung |
| 10 | 014 | Eingabe-Halt 1. Art ohne Löschen, mit Linksverschiebung |
| 11 | 015 | Eingabe-Halt 1. Art mit Löschen, mit Linksverschiebung |
| 12 | 016 | Eingabe-Halt 1. Art ohne Löschen, mit zyklischer Linksverschiebung |
| 13 | 017 | Eingabe-Halt 1. Art mit Löschen, mit zyklischer Linksverschiebung |
| 14 | 020 | unbedingter Stop 1. Art ohne Löschen, ohne Resultatbehandlung |
| 15 | 021, 023 | unbedingter Stop 1. Art mit Löschen |
| 16 | 022 | unbedingter Stop 1. Art ohne Löschen, mit Rechtsverschiebung |
| 17 | 024, 124 | Sprung mit Rückkehrabsicht ohne Löschen, mit Linksverschiebung |
| 18 | 025, 027, 125, 127 | Sprung mit Rückkehrabsicht mit Löschen, mit (zyklischer oder azyklischer) Linksverschiebung |
| 19 | 026, 126 | Sprung mit Rückkehrabsicht ohne Löschen, mit zyklischer Linksverschiebung |
| 20 | 030, 032, 034, 036, 130, 132, 134, 136 | Ausgabe-Halt ohne Löschen |
| 21 | 031, 033, 035, 037, 131, 133, 135, 137 | Ausgabe-Halt mit Löschen |
| 22 | 040 | Negativsprung ohne Löschen, ohne Resultatbehandlung |
| 23 | 041, 043, 045, 047 | Negativsprung mit Löschen |
| 24 | 042 | Negativsprung ohne Löschen, mit Rechtsverschiebung |
| 25 | 044 | Negativsprung ohne Löschen, mit Linksverschiebung |
| 26 | 046 | Negativsprung ohne Löschen, mit zyklischer Linksverschiebung |
| 27 | 050 | Positivsprung ohne Löschen, ohne Resultatbehandlung |
| 28 | 051, 053, 055, 057 | Positivsprung mit Löschen |
| 29 | 052 | Positivsprung ohne Löschen, mit Rechtsverschiebung |
| 30 | 054, 056 | Positivsprung ohne Löschen, mit (zyklischer oder azyklischer) Linksverschiebung |
| 31 | 060 | bedingter Stop 1. Art ohne Löschen, ohne Resultatbehandlung |
| 32 | 061, 063 | bedingter Stop 1. Art mit Löschen |
| 33 | 062 | bedingter Stop 1. Art ohne Löschen, mit Rechtsverschiebung |
| 34 | 064 | bedingter Sprung mit Rückkehrabsicht ohne Löschen, mit Linksverschiebung |
| 35 | 065, 067 | bedingter Sprung mit Rückkehrabsicht mit Löschen, mit (zyklischer oder azyklischer) Linksverschiebung |
| 36 | 066 | bedingter Sprung mit Rückkehrabsicht ohne Löschen, mit zyklischer Linksverschiebung |
| 37 | 070 | Überlaufsprung ohne Löschen, ohne Resultatbehandlung |
| 38 | 071, 073, 075, 077 | Überlaufsprung mit Löschen |
| 39 | 072 | Überlaufsprung ohne Löschen, mit Rechtsverschiebung |
| 40 | 074 | Überlaufsprung ohne Löschen, mit Linksverschiebung |
| 41 | 076 | Überlaufsprung ohne Löschen, mit zyklischer Linksverschiebung |
| 42 | 110 | Eingabe-Halt 2. Art ohne Löschen, ohne Resultatbehandlung |
| 43 | 111 | Eingabe-Halt 2. Art mit Löschen, ohne Resultatbehandlung |
| 44 | 112 | Eingabe-Halt 2. Art ohne Löschen, mit Rechtsverschiebung |
| 45 | 113 | Eingabe-Halt 2. Art mit Löschen, mit Rechtsverschiebung |
| 46 | 114 | Eingabe-Halt 2. Art ohne Löschen, mit Linksverschiebung |
| 47 | 115 | Eingabe-Halt 2. Art mit Löschen, mit Linksverschiebung |
| 48 | 116 | Eingabe-Halt 2. Art ohne Löschen, mit zyklischer Linksverschiebung |
| 49 | 117 | Eingabe-Halt 2. Art mit Löschen, mit zyklischer Linksverschiebung |
| 50 | 120 | unbedingter Stop 2. Art ohne Löschen, ohne Resultatbehandlung |
| 51 | 121, 123 | unbedingter Stop 2. Art mit Löschen |
| 52 | 122 | unbedingter Stop 2. Art ohne Löschen, mit Rechtsverschiebung |
| 53 | 140 | Vergleichersprung 1 ohne Löschen, ohne Resultatbehandlung |
| 54 | 141, 143, 145, 147 | Vergleichersprung 1 mit Löschen |
| 55 | 142 | Vergleichersprung 1 ohne Löschen, mit Rechtsverschiebung |
| 56 | 144 | Vergleichersprung 1 ohne Löschen, mit Linksverschiebung |
| 57 | 146 | Vergleichersprung 1 ohne Löschen, mit zyklischer Linksverschiebung |
| 58 | 150 | Vergleichersprung 2 ohne Löschen, ohne Resultatbehandlung |
| 59 | 151, 153, 155, 157 | Vergleichersprung 2 mit Löschen |
| 60 | 152 | Vergleichersprung 2 ohne Löschen, mit Rechtsverschiebung |
| 61 | 154 | Vergleichersprung 2 ohne Löschen, mit Linksverschiebung |
| 62 | 156 | Vergleichersprung 2 ohne Löschen, mit zyklischer Linksverschiebung |
| 63 | 160 | bedingter Stop 2. Art ohne Löschen, ohne Resultatbehandlung |
| 64 | 161, 163 | bedingter Stop 2. Art mit Löschen |
| 65 | 162 | bedingter Stop 2. Art ohne Löschen, mit Rechtsverschiebung |
| 66 | 164, 166 | Leer-Operation ohne Löschen |
| 67 | 165, 167, 201, 203, 205, 207, 233, 261, 263, 265, 267, 273, 401, 403, 405, 407, 433, 461, 463, 465, 467, 473, 501, 503, 505, 507, 533, 561, 563, 565, 567, 573, 601, 603, 605, 607, 633, 661, 663, 665, 667, 673, 701, 703, 705, 707, 733, 761, 763, 765, 767, 773 | Leer-Operation mit Löschen |
| 68 | 170 | Vergleichersprung 3 ohne Löschen, ohne Resultatbehandlung |
| 69 | 171, 173, 175, 177 | Vergleichersprung 3 mit Löschen |
| 70 | 172 | Vergleichersprung 3 ohne Löschen, mit Rechtsverschiebung |
| 71 | 174 | Vergleichersprung 3 ohne Löschen, mit Linksverschiebung |
| 72 | 176 | Vergleichersprung 3 ohne Löschen, mit zyklischer Linksverschiebung |
| 73 | 200 | Einzel-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 74 | 202 | Einzel-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 75 | 204 | Einzel-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 76 | 206 | Einzel-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 77 | 210 | Einzel-Addition ohne Löschen, ohne Resultatbehandlung |
| 78 | 211 | Einzel-Addition mit Löschen, ohne Resultatbehandlung |
| 79 | 212 | Einzel-Addition ohne Löschen, mit Rechtsverschiebung |
| 80 | 213 | Einzel-Addition mit Löschen, mit Rechtsverschiebung |
| 81 | 214 | Einzel-Addition ohne Löschen, mit Linksverschiebung |
| 82 | 215 | Einzel-Addition mit Löschen, mit Linksverschiebung |
| 83 | 216 | Einzel-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 84 | 217 | Einzel-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 85 | 220 | Einzel-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 86 | 221, 231 | Einzel-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 87 | 222 | Einzel-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 88 | 223 | Einzel-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 89 | 224 | Einzel-Subtraktion ohne Löschen, mit Linksverschiebung |
| 90 | 225, 235 | Einzel-Subtraktion mit Löschen, mit Linksverschiebung |
| 91 | 226 | Einzel-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 92 | 227, 237 | Einzel-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 93 | 230 | Einzelbefehl bedingte Addition ohne Löschen, ohne Resultatbehandlung |
| 94 | 232 | Einzelbefehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 95 | 234 | Einzelbefehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 96 | 236 | Einzelbefehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 97 | 240 | Einzel-Transport ohne Löschen, ohne Resultatbehandlung |
| 98 | 241, 243, 245, 247 | Einzel-Transport mit Löschen |
| 99 | 242 | Einzel-Transport ohne Löschen, mit Rechtsverschiebung |
| 100 | 244 | Einzel-Transport ohne Löschen, mit Linksverschiebung |
| 101 | 246 | Einzel-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 102 | 250 | Einzel-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 103 | 251 | Einzel-R-Operation mit Löschen, ohne Resultatbehandlung |
| 104 | 252 | Einzel-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 105 | 253 | Einzel-R-Operation mit Löschen, mit Rechtsverschiebung |
| 106 | 254 | Einzel-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 107 | 255 | Einzel-R-Operation mit Löschen, mit Linksverschiebung |
| 108 | 256 | Einzel-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 109 | 257 | Einzel-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 110 | 260 | Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 111 | 262 | Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 112 | 264 | Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 113 | 266 | Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 114 | 270 | Einzelbefehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 115 | 271 | Einzel-R-Operation mit Löschen, ohne Resultatbehandlung |
| 116 | 272 | Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 117 | 274 | Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 118 | 275 | Einzel-R-Operation mit Löschen, mit Linksverschiebung |
| 119 | 276 | Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 120 | 277 | Einzel-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 121 | 300 | markierte Einzel-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 122 | 301, 303, 305, 307, 331, 333, 373 | markierte Leer-Operation mit Löschen |
| 123 | 302 | markierte Einzel-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 124 | 304 | markierte Einzel-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 125 | 306 | markierte Einzel-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 126 | 310 | markierte Einzel-Addition ohne Löschen, ohne Resultatbehandlung |
| 127 | 311 | markierte Einzel-Addition mit Löschen, ohne Resultatbehandlung |
| 128 | 312 | markierte Einzel-Addition ohne Löschen, mit Rechtsverschiebung |
| 129 | 313 | markierte Einzel-Addition mit Löschen, mit Rechtsverschiebung |
| 130 | 314 | markierte Einzel-Addition ohne Löschen, mit Linksverschiebung |
| 131 | 315 | markierte Einzel-Addition mit Löschen, mit Linksverschiebung |
| 132 | 316 | markierte Einzel-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 133 | 317 | markierte Einzel-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 134 | 320 | markierte Einzel-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 135 | 321 | markierte Einzel-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 136 | 322 | markierte Einzel-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 137 | 323 | markierte Einzel-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 138 | 324 | markierte Einzel-Subtraktion ohne Löschen, mit Linksverschiebung |
| 139 | 325, 335 | markierte Einzel-Subtraktion mit Löschen, mit Linksverschiebung |
| 140 | 326 | markierte Einzel-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 141 | 327, 337 | markierte Einzel-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 142 | 330 | reines Vergleichersetzen ohne Löschen |
| 143 | 332 | markierter Einzelbefehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 144 | 334 | markierter Einzelbefehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 145 | 336 | markierter Einzelbefehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 146 | 340 | markierter Einzel-Transport ohne Löschen, ohne Resultatbehandlung |
| 147 | 341, 343, 345, 347 | markierter Einzel-Transport mit Löschen |
| 148 | 342 | markierter Einzel-Transport ohne Löschen, mit Rechtsverschiebung |
| 149 | 344 | markierter Einzel-Transport ohne Löschen, mit Linksverschiebung |
| 150 | 346 | markierter Einzel-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 151 | 350 | markierte Einzel-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 152 | 351 | markierte Einzel-R-Operation mit Löschen, ohne Resultatbehandlung |
| 153 | 352 | markierte Einzel-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 154 | 353 | markierte Einzel-R-Operation mit Löschen, mit Rechtsverschiebung |
| 155 | 354 | markierte Einzel-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 156 | 355 | markierte Einzel-R-Operation mit Löschen, mit Linksverschiebung |
| 157 | 356 | markierte Einzel-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 158 | 357 | markierte Einzel-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 159 | 360 | markierte Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 160 | 361, 363, 365, 367 | markierte Leer-Operation mit Löschen |
| 161 | 362 | markierte Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 162 | 364 | markierte Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 163 | 366 | markierte Einzel-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 164 | 370 | markierter Einzelbefehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 165 | 371 | markierte Einzel-R-Operation mit Löschen, ohne Resultatbehandlung |
| 166 | 372 | markierter Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 167 | 374 | markierter Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 168 | 375 | markierte Einzel-R-Operation mit Löschen, mit Linksverschiebung |
| 169 | 376 | markierter Einzelbefehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 170 | 377 | markierte Einzel-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 171 | 400 | G-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 172 | 402 | G-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 173 | 404 | G-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 174 | 406 | G-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 175 | 410 | G-Addition ohne Löschen, ohne Resultatbehandlung |
| 176 | 411 | G-Addition mit Löschen, ohne Resultatbehandlung |
| 177 | 412 | G-Addition ohne Löschen, mit Rechtsverschiebung |
| 178 | 413 | G-Addition mit Löschen, mit Rechtsverschiebung |
| 179 | 414 | G-Addition ohne Löschen, mit Linksverschiebung |
| 180 | 415 | G-Addition mit Löschen, mit Linksverschiebung |
| 181 | 416 | G-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 182 | 417 | G-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 183 | 420 | G-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 184 | 421 | G-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 185 | 422 | G-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 186 | 423 | G-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 187 | 424 | G-Subtraktion ohne Löschen, mit Linksverschiebung |
| 188 | 425 | G-Subtraktion mit Löschen, mit Linksverschiebung |
| 189 | 426 | G-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 190 | 427 | G-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 191 | 430 | G-Befehl bedingte Addition ohne Löschen, ohne Resultatbehandlung |
| 192 | 431 | G-Befehl bedingte Addition mit Löschen, ohne Resultatbehandlung |
| 193 | 432 | G-Befehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 194 | 434 | G-Befehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 195 | 435 | G-Befehl bedingte Addition mit Löschen, mit Linksverschiebung |
| 196 | 436 | G-Befehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 197 | 437 | G-Befehl bedingte Addition mit Löschen, mit zyklischer Linksverschiebung |
| 198 | 440 | G-Transport ohne Löschen, ohne Resultatbehandlung |
| 199 | 441, 443, 445, 447, 541, 543, 545, 547 | G-Transport mit Löschen |
| 200 | 442 | G-Transport ohne Löschen, mit Rechtsverschiebung |
| 201 | 444 | G-Transport ohne Löschen, mit Linksverschiebung |
| 202 | 446 | G-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 203 | 450 | G-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 204 | 451 | G-R-Operation mit Löschen, ohne Resultatbehandlung |
| 205 | 452 | G-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 206 | 453 | G-R-Operation mit Löschen, mit Rechtsverschiebung |
| 207 | 454 | G-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 208 | 455 | G-R-Operation mit Löschen, mit Linksverschiebung |
| 209 | 456 | G-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 210 | 457 | G-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 211 | 460 | G-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 212 | 462 | G-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 213 | 464 | G-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 214 | 466 | G-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 215 | 470 | G-Befehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 216 | 471 | G-R-Operation mit Löschen, ohne Resultatbehandlung |
| 217 | 472 | G-Befehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 218 | 474 | G-Befehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 219 | 475 | G-R-Operation mit Löschen, mit Linksverschiebung |
| 220 | 476 | G-Befehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 221 | 477 | G-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 222 | 500 | GX-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 223 | 502 | GX-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 224 | 504 | GX-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 225 | 506 | GX-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 226 | 510 | GX-Addition ohne Löschen, ohne Resultatbehandlung |
| 227 | 511 | GX-Addition mit Löschen, ohne Resultatbehandlung |
| 228 | 512 | GX-Addition ohne Löschen, mit Rechtsverschiebung |
| 229 | 513 | GX-Addition mit Löschen, mit Rechtsverschiebung |
| 230 | 514 | GX-Addition ohne Löschen, mit Linksverschiebung |
| 231 | 515 | GX-Addition mit Löschen, mit Linksverschiebung |
| 232 | 516 | GX-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 233 | 517 | GX-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 234 | 520 | GX-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 235 | 521 | GX-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 236 | 522 | GX-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 237 | 523 | GX-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 238 | 524 | GX-Subtraktion ohne Löschen, mit Linksverschiebung |
| 239 | 525 | GX-Subtraktion mit Löschen, mit Linksverschiebung |
| 240 | 526 | GX-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 241 | 527 | GX-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 242 | 530 | GX-Befehl bedingte Addition ohne Löschen, ohne Resultatbehandlung |
| 243 | 531 | GX-Befehl bedingte Addition mit Löschen, ohne Resultatbehandlung |
| 244 | 532 | GX-Befehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 245 | 534 | GX-Befehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 246 | 535 | GX-Befehl bedingte Addition mit Löschen, mit Linksverschiebung |
| 247 | 536 | GX-Befehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 248 | 537 | GX-Befehl bedingte Addition mit Löschen, mit zyklischer Linksverschiebung |
| 249 | 540 | GX-Transport ohne Löschen, ohne Resultatbehandlung |
| 250 | 542 | GX-Transport ohne Löschen, mit Rechtsverschiebung |
| 251 | 544 | GX-Transport ohne Löschen, mit Linksverschiebung |
| 252 | 546 | GX-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 253 | 550 | GX-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 254 | 551 | GX-R-Operation mit Löschen, ohne Resultatbehandlung |
| 255 | 552 | GX-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 256 | 553 | GX-R-Operation mit Löschen, mit Rechtsverschiebung |
| 257 | 554 | GX-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 258 | 555 | GX-R-Operation mit Löschen, mit Linksverschiebung |
| 259 | 556 | GX-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 260 | 557 | GX-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 261 | 560 | GX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 262 | 562 | GX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 263 | 564 | GX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 264 | 566 | GX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 265 | 570 | GX-Befehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 266 | 571 | GX-R-Operation mit Löschen, ohne Resultatbehandlung |
| 267 | 572 | GX-Befehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 268 | 574 | GX-Befehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 269 | 575 | GX-R-Operation mit Löschen, mit Linksverschiebung |
| 270 | 576 | GX-Befehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 271 | 577 | GX-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 272 | 600 | W-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 273 | 602 | W-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 274 | 604 | W-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 275 | 606 | W-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 276 | 610 | W-Addition ohne Löschen, ohne Resultatbehandlung |
| 277 | 611 | W-Addition mit Löschen, ohne Resultatbehandlung |
| 278 | 612 | W-Addition ohne Löschen, mit Rechtsverschiebung |
| 279 | 613 | W-Addition mit Löschen, mit Rechtsverschiebung |
| 280 | 614 | W-Addition ohne Löschen, mit Linksverschiebung |
| 281 | 615 | W-Addition mit Löschen, mit Linksverschiebung |
| 282 | 616 | W-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 283 | 617 | W-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 284 | 620 | W-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 285 | 621 | W-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 286 | 622 | W-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 287 | 623 | W-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 288 | 624 | W-Subtraktion ohne Löschen, mit Linksverschiebung |
| 289 | 625 | W-Subtraktion mit Löschen, mit Linksverschiebung |
| 290 | 626 | W-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 291 | 627 | W-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 292 | 630 | W-Befehl bedingte Addition ohne Löschen, ohne Resultatbehandlung |
| 293 | 631 | W-Befehl bedingte Addition mit Löschen, ohne Resultatbehandlung |
| 294 | 632 | W-Befehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 295 | 634 | W-Befehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 296 | 635 | W-Befehl bedingte Addition mit Löschen, mit Linksverschiebung |
| 297 | 636 | W-Befehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 298 | 637 | W-Befehl bedingte Addition mit Löschen, mit zyklischer Linksverschiebung |
| 299 | 640 | W-Transport ohne Löschen, ohne Resultatbehandlung |
| 300 | 641, 643, 645, 647, 741, 743, 745, 747 | W-Transport mit Löschen |
| 301 | 642 | W-Transport ohne Löschen, mit Rechtsverschiebung |
| 302 | 644 | W-Transport ohne Löschen, mit Linksverschiebung |
| 303 | 646 | W-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 304 | 650 | W-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 305 | 651 | W-R-Operation mit Löschen, ohne Resultatbehandlung |
| 306 | 652 | W-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 307 | 653 | W-R-Operation mit Löschen, mit Rechtsverschiebung |
| 308 | 654 | W-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 309 | 655 | W-R-Operation mit Löschen, mit Linksverschiebung |
| 310 | 656 | W-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 311 | 657 | W-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 312 | 660 | W-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 313 | 662 | W-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 314 | 664 | W-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 315 | 666 | W-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 316 | 670 | W-Befehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 317 | 671 | W-R-Operation mit Löschen, ohne Resultatbehandlung |
| 318 | 672 | W-Befehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 319 | 674 | W-Befehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 320 | 675 | W-R-Operation mit Löschen, mit Linksverschiebung |
| 321 | 676 | W-Befehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 322 | 677 | W-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 323 | 700 | WX-Konjunktion im Akkumulator ohne Löschen, ohne Resultatbehandlung |
| 324 | 702 | WX-Konjunktion im Akkumulator ohne Löschen, mit Rechtsverschiebung |
| 325 | 704 | WX-Konjunktion im Akkumulator ohne Löschen, mit Linksverschiebung |
| 326 | 706 | WX-Konjunktion im Akkumulator ohne Löschen, mit zyklischer Linksverschiebung |
| 327 | 710 | WX-Addition ohne Löschen, ohne Resultatbehandlung |
| 328 | 711 | WX-Addition mit Löschen, ohne Resultatbehandlung |
| 329 | 712 | WX-Addition ohne Löschen, mit Rechtsverschiebung |
| 330 | 713 | WX-Addition mit Löschen, mit Rechtsverschiebung |
| 331 | 714 | WX-Addition ohne Löschen, mit Linksverschiebung |
| 332 | 715 | WX-Addition mit Löschen, mit Linksverschiebung |
| 333 | 716 | WX-Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 334 | 717 | WX-Addition mit Löschen, mit zyklischer Linksverschiebung |
| 335 | 720 | WX-Subtraktion ohne Löschen, ohne Resultatbehandlung |
| 336 | 721 | WX-Subtraktion mit Löschen, ohne Resultatbehandlung |
| 337 | 722 | WX-Subtraktion ohne Löschen, mit Rechtsverschiebung |
| 338 | 723 | WX-Subtraktion mit Löschen, mit Rechtsverschiebung |
| 339 | 724 | WX-Subtraktion ohne Löschen, mit Linksverschiebung |
| 340 | 725 | WX-Subtraktion mit Löschen, mit Linksverschiebung |
| 341 | 726 | WX-Subtraktion ohne Löschen, mit zyklischer Linksverschiebung |
| 342 | 727 | WX-Subtraktion mit Löschen, mit zyklischer Linksverschiebung |
| 343 | 730 | WX-Befehl bedingte Addition ohne Löschen, ohne Resultatbehandlung |
| 344 | 731 | WX-Befehl bedingte Addition mit Löschen, ohne Resultatbehandlung |
| 345 | 732 | WX-Befehl bedingte Addition ohne Löschen, mit Rechtsverschiebung |
| 346 | 734 | WX-Befehl bedingte Addition ohne Löschen, mit Linksverschiebung |
| 347 | 735 | WX-Befehl bedingte Addition mit Löschen, mit Linksverschiebung |
| 348 | 736 | WX-Befehl bedingte Addition ohne Löschen, mit zyklischer Linksverschiebung |
| 349 | 737 | WX-Befehl bedingte Addition mit Löschen, mit zyklischer Linksverschiebung |
| 350 | 740 | WX-Transport ohne Löschen, ohne Resultatbehandlung |
| 351 | 742 | WX-Transport ohne Löschen, mit Rechtsverschiebung |
| 352 | 744 | WX-Transport ohne Löschen, mit Linksverschiebung |
| 353 | 746 | WX-Transport ohne Löschen, mit zyklischer Linksverschiebung |
| 354 | 750 | WX-Konjunktion im Speicher ohne Löschen, ohne Resultatbehandlung |
| 355 | 751 | WX-R-Operation mit Löschen, ohne Resultatbehandlung |
| 356 | 752 | WX-Konjunktion im Speicher ohne Löschen, mit Rechtsverschiebung |
| 357 | 753 | WX-R-Operation mit Löschen, mit Rechtsverschiebung |
| 358 | 754 | WX-Konjunktion im Speicher ohne Löschen, mit Linksverschiebung |
| 359 | 755 | WX-R-Operation mit Löschen, mit Linksverschiebung |
| 360 | 756 | WX-Konjunktion im Speicher ohne Löschen, mit zyklischer Linksverschiebung |
| 361 | 757 | WX-R-Operation mit Löschen, mit zyklischer Linksverschiebung |
| 362 | 760 | WX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, ohne Resultatbehandlung |
| 363 | 762 | WX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Rechtsverschiebung |
| 364 | 764 | WX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit Linksverschiebung |
| 365 | 766 | WX-Konjunktion mit negiertem Akkumulatorinhalt ohne Löschen, mit zyklischer Linksverschiebung |
| 366 | 770 | WX-Befehl bedingte Speicherlöschung ohne Löschen, ohne Resultatbehandlung |
| 367 | 771 | WX-R-Operation mit Löschen, ohne Resultatbehandlung |
| 368 | 772 | WX-Befehl bedingte Speicherlöschung ohne Löschen, mit Rechtsverschiebung |
| 369 | 774 | WX-Befehl bedingte Speicherlöschung ohne Löschen, mit Linksverschiebung |
| 370 | 775 | WX-R-Operation mit Löschen, mit Linksverschiebung |
| 371 | 776 | WX-Befehl bedingte Speicherlöschung ohne Löschen, mit zyklischer Linksverschiebung |
| 372 | 777 | WX-R-Operation mit Löschen, mit zyklischer Linksverschiebung |

# Beispiel: Befehl 520 (GX-Subtraktion), ausführlich erläutert

**Lesehilfe, nicht Wortlaut der Quelle** (Stand 18.10.2026). An einem einzigen Befehl wird gezeigt, wie die Angaben dieser
Datei zusammenwirken: Dekodierung nach B-A-Z (4.1, 4.2), Wirkung auf die Zellen einer Spur (4.1.5, 4.1.6), X-Abbruch mit
Zusatzzelle, Befehlsentnahme nach dem Abbruch und Lage der Sektoren auf der Trommel (`C8205-Interpreter-Magnettrommel.md`,
Abschnitt „Speichernumerierung / Interleaving“). Die Zahlen des Ablaufbeispiels stammen aus Läufen des Python-Interpreters
(Protokollstufe 2) mit dem Baustein „Triadendruck“ des Minimalprogramms
(`Assembler/Projekt_2/pj2-bis_minimalprogramm_v2_triadendruck.asm`). Alle Zahlen sind oktal, sofern nicht „dezimal“ dasteht.

**1. Dekodierung des Operationsteils 520**

Der Operationsteil wird als Triadenfolge B-A-Z gelesen (Nr. 234 der Liste oben):

| Triade | Wert | Bedeutung |
|---|---|---|
| B | 5 | Verkürzter Gruppenbefehl (GX-Befehl), 4.1.6 |
| A | 2 | Operationsart Subtraktion: ⟨AC⟩ := ⟨AC⟩ − ⟨a⟩ (wie beim Einzelbefehl 220) |
| Z | 0 | R = 0 und L = 0: keine Resultatbehandlung, kein Löschen |

Dieselbe Operation (A = 2, Z = 0) gibt es in allen Befehlstypen. Sie unterscheiden sich nur darin, auf wie viele Zellen die
Subtraktion angewendet wird und wann sie endet:

| Code | Befehl | Zellen, auf die die Subtraktion wirkt |
|---|---|---|
| 220 | Einzel-Subtraktion | nur die Zelle a |
| 420 | G-Subtraktion | alle 32 Zellen der Spur, zu der a gehört |
| 520 | GX-Subtraktion | wie 420, aber vorzeitiger Abbruch, sobald der AC negativ ist (X-Bedingung) |

Bei 520 entscheidet also der Inhalt des AC, nach wie vielen Zellen der Befehl endet. Im Beispiel unten steht der Befehl
`7721 520` mit dem Adreßteil a = 7721. Dessen Spur umfasst die 32 Adressen 7700 bis 7737; die Sektornummer von a ist 21,
nämlich die letzten fünf Bit der Adresse (Spur z₁₂–z₁₈, Sektor z₁₉–z₂₃).

**2. Wirkung im Einzelnen**

- Die Phasen I bis III laufen einmal, Phase IV läuft für jede bearbeitete Zelle c der Spur: ⟨AC⟩ := ⟨AC⟩ − ⟨c⟩ (4.1.5).
- Die Zellen werden in der Reihenfolge ihrer geometrischen Anordnung auf der Trommel bearbeitet, beginnend mit der Zelle a.
  Von einer Zelle zur nächsten wächst die logische Sektoradresse um 15 (modulo 40), weil physisch benachbarte Sektoren
  durchgehend um +15 verschiedene logische Adressen haben (Magnettrommel, Interleaving).
- **X-Bedingung:** Ist nach Operation und Resultatbehandlung einer Zelle der AC negativ, wird die Operation noch mit genau
  einer weiteren Zelle ausgeführt (**Zusatzzelle**); der negative AC wird also noch weiterverarbeitet. Danach folgt der
  Abbruch. Bei R = 0 ist z₀ das Vorzeichen; negative Zahlen sind Zweierkomplemente mit 33 Bit.
- **Normale Abbruchbedingung:** Alle 32 Zellen sind bearbeitet (eine Trommelumdrehung). Sie hat Vorrang, wenn beide
  Bedingungen in derselben Zelle erfüllt werden (4.1.6).

**3. Durchgerechnetes Beispiel: Spur mit lauter Einsen, AC = 2**

Annahme: Alle Zellen der Spur 7700–7737 enthalten das Wort 1, ⟨AC⟩ = 2, der Befehl `7721 520` steht in Zelle b. „Position“
ist die physische Sektorposition auf der Trommel (Tabelle in der Magnettrommel-Datei), „Sektor“ die zugehörige logische
Sektornummer:

| Schritt | Position | Sektor | Zelle | AC vorher → nachher | Bemerkung |
|---|---|---|---|---|---|
| 1 | 25 | 21 | 7721 | 2 → 1 | Startzelle a |
| 2 | 26 | 36 | 7736 | 1 → 0 | |
| 3 | 27 | 13 | 7713 | 0 → −1 | AC negativ: X-Bedingung erfüllt |
| 4 | 30 | 30 | 7730 | −1 → −2 | Zusatzzelle, danach Abbruch |

Der AC endet bei −2, das ist 77777777776 (33 Bit, Zweierkomplement), unabhängig vom Anfangswert d. Von AC = d aus sind d + 1
Subtraktionen nötig, bis der AC negativ wird, dazu kommt die Zusatzzelle; insgesamt werden also d + 2 Zellen bearbeitet.
Wie weit der Befehl kommt, hängt damit allein von d ab.

**4. Befehlsentnahme nach dem Abbruch**

Nach dem X-Abbruch wird der nächste Befehl ohne Wartezeit entnommen (4.1.6). Zwei Angaben legen die Zelle fest:

- **Spur:** Sie kommt aus dem Befehlszähler. Stand der GX-Befehl in Zelle b, so ist BZ = b + 1, und die Spur ist die von b + 1.
- **Sektor:** Er ergibt sich aus der Lage der Trommel in der zweiten Wortzeit nach dem Abbruch. Der Interpreter rechnet:
  Sektor der Zusatzzelle plus 2 physische Schritte (je +15).

Der entnommene Befehl muss deshalb **nicht** in Zelle b + 1 stehen. BZ bleibt b + 1; nach Phase III des entnommenen Befehls
ist BZ = b + 2. Ist der entnommene Befehl kein Sprung, geht es in Zelle b + 2 weiter. Zelle b + 1 wird übersprungen.

Für die Spur mit lauter Einsen und der Startposition p₀ folgt: Die Zusatzzelle liegt auf Position p₀ + d + 1, der entnommene
Befehl auf Position p₀ + d + 3. Mit p₀ = 25 (Sektor 21) ist das die Position 30 + d.

**5. Anwendung: Auswahl eines von acht Druckbefehlen (Triadendruck)**

Der Triadendruck (Zellen 0100 bis 0137) druckt die 11 Oktalziffern eines Wortes nacheinander. Je Ziffer d (0 bis 7) muss einer
von acht Ausgabebefehlen `030 <Zeichen>` ausgeführt werden, ohne dass ein Sprungbefehl auf ihn zeigt. Die Auswahl trifft der
Befehl 520 in Zelle 0107 (b = 0107, also BZ = 0110 und damit die Spur 0100–0137).

Vorbereitung: `7724 440` (G-Transport, B = 4, A = 4) schreibt den AC = 1 in alle 32 Zellen der Spur 7700–7737. Die Zelle 7720
überschreibt anschließend ein `240`-Befehl mit dem Ziffernzähler; sie liegt auf Position 20 und käme erst als 28. Zelle an
die Reihe, wird also nie erreicht. In jedem Durchlauf holt `7777 217` das Wort aus Zelle 7777; die Befehle 217, 006 und 006
drehen es insgesamt um 3 Bit (eine Oktalstelle) zyklisch nach links, `7777 240` speichert es zurück, und `0117 200` blendet
die unterste Triade aus. Im AC steht dann die Ziffer d. Der Startsektor des 520 ist 21 (Position 25), also gilt Abschnitt 4
mit p₀ = 25:

| Ziffer d | Position | Sektor | Zelle | Inhalt (Adreßteil Operationsteil) | gedrucktes Zeichen |
|---|---|---|---|---|---|
| 0 | 30 | 30 | 0130 | 0200 030 | 0 |
| 1 | 31 | 05 | 0105 | 0010 030 | 1 |
| 2 | 32 | 22 | 0122 | 0020 030 | 2 |
| 3 | 33 | 37 | 0137 | 0230 030 | 3 |
| 4 | 34 | 14 | 0114 | 0040 030 | 4 |
| 5 | 35 | 31 | 0131 | 0250 030 | 5 |
| 6 | 36 | 06 | 0106 | 0260 030 | 6 |
| 7 | 37 | 23 | 0123 | 0070 030 | 7 |

Der Operationsteil 030 ist der Ausgabe-Halt (Ausgabe eines Zeichens), der Adreßteil die Ausgabeadresse des Zeichens
(Kodetabellen, Tabelle 1). Die Sektoren 30, 05, 22, 37, 14, 31, 06, 23 sind genau die Zeile der Positionen 30 bis 37 in der
Interleaving-Tabelle der Magnettrommel; als Formel: Sektor = (30 + d · 15) mod 40.

**Protokollierter Durchlauf für die Ziffer 0** (Wort 0000 0000 100, dezimal 64; erste Ziffer von links). Die Spalte „AC danach“
zeigt den Akkumulator nach der Ausführung des Befehls:

| Zelle | Befehl | AC danach | Wirkung |
|---|---|---|---|
| 0103 | 7777 217 | 00000000200 | AC := ⟨7777⟩ = 100, zyklisch 1 Bit nach links |
| 0104 | 0115 006 | 00000000400 | Sprung nach 0115, AC zyklisch 1 Bit nach links |
| 0115 | 0124 006 | 00000001000 | Sprung nach 0124, AC zyklisch 1 Bit nach links |
| 0124 | 7777 240 | 00000001000 | ⟨7777⟩ := ⟨AC⟩ (Wort um 3 Bit gedreht) |
| 0125 | 0117 200 | 00000000000 | AC := AC ∧ 7: unterste Triade, hier d = 0 |
| 0126 | 0107 000 | 00000000000 | Sprung nach 0107 |
| 0107 | 7721 520 | 77777777776 | GX-Subtraktion über die Spur 7700–7737, AC = −2 |
| (0130) | 0200 030 | 77777777776 | entnommener Befehl: druckt „0“; danach BZ = 0111 |
| 0111 | 7720 311 | | weiter in der Ziffernzählung, nicht mehr Teil des Beispiels |

Die Zelle 0110 steht zwischen den Zeilen 0107 und 0111, wird aber nie ausgeführt: Dort liegt die Konstante 77740000000, die
nur als Datenwort dient.

**6. Prüfung und Folgerungen**

- **Prüfung:** Läufe mit den Wörtern 64 (dezimal), 01234567012 und 76543210765 drucken die Wörter richtig. Für jede Ziffer 0
  bis 7 zeigt das Protokoll: AC nach dem 520 = 77777777776, nächster ausgeführter Befehl = die Zelle aus der Tabelle oben,
  BZ danach = 0111 (= b + 2).
- **Wert → Zeit → Sektor:** Der AC-Wert wirkt wie ein Index in die Spur von b + 1. Damit ist eine Mehrfachverzweigung ohne
  Sprungbefehle möglich; die Zielbefehle liegen verstreut auf ihren Sektoren.
- **Sektoren sind Teil des Programms:** Wird das Programm verschoben, darf sich nur die Spur ändern. Die Sektoren der
  Zielbefehle müssen erhalten bleiben, sonst druckt der Befehl eine falsche Ziffer.
- **Zelle b + 1 wird übersprungen** und kann Daten enthalten (hier die Konstante in 0110).
- **Der Wert d geht verloren** (AC = −2 nach dem Befehl). Wird er danach noch gebraucht, muss er vorher gesichert werden.
- **Gültigkeitsbereich:** Der beschriebene Ablauf gilt für Spuren mit lauter Einsen und 0 ≤ d ≤ 30. Wird der AC erst in
  der letzten Zelle der Spur (der 32.) negativ (d = 31) oder innerhalb der Spur gar nicht (d > 31), gilt die normale
  Abbruchbedingung (Vorrang, 4.1.6), und die Entnahme erfolgt wie beim G-Befehl.
