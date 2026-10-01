# ** Datenstrukturen **

Namensbereiche: Flags, Register, Felder des Befehlswortes sowie die Knoten und
   Konnektoren der Knotentabelle sind getrennte Beschreibungsbereiche. Innerhalb
   eines Bereichs muss jeder Name eindeutig sein, zwischen Bereichen dürfen gleiche
   Namen vorkommen (z.B. Flag A und Feld A, Feld B und Konnektor B) und sind
   voneinander unabhängig. Wird ein Name außerhalb seines Bereichs benutzt,
   wird er qualifiziert: "Flag A", "Feld A".
   <> gelten an Stelle einer Qualifizierung, da sie nur bei Registern und Speicherinhalten vorkommen.


Zahlensysteme: Original-Zahlen in Befehlen, Registern und im Speicher sind oktal (außer
   ausdrücklich als dual oder dezimal gekennzeichnet). Element-Referenznummern
   dieses Dokuments sind immer dezimal.

Dualzahlen
- Bei der Ausführung der verdrahteten Rechenbefehle (Addition,
  Subtraktion) wird das interne Wort vom Rechner als **Dualzahl in
  Festkommadarstellung** interpretiert.
- Die Stellung des Kommas wird nicht festgelegt; man denkt es sich
  beispielsweise zwischen z₀ und z₁.
- **z₀** enthält das **Vorzeichen**.
- **z₃₂** ist das **niederwertigste Bit** (z₁ demnach das höchstwertige
  Betragsbit, unmittelbar nach dem Vorzeichenbit), bei vorzeichenlosen Zahlen ist z₀ das höchstwertige Bit.
- Positive Zahlen z: z = Σ (i=1 bis 32) zᵢ · 2⁻ⁱ
- Negative Zahlen z̃ werden als **Zweierkomplement** dargestellt:
  z̃ = 2 − z. Dabei werden alle Bits vor dem niedrigstwertigen mit 1
  besetzten Bit negiert (siehe Original-Abb. 7, hier nicht enthalten).


Zahlen treten auf
   in Flags ( 1 dual-bit)
   in Registern ( oktal oder dual )
   im Trommelspeicher ( oktal oder dual )

Der Rechner selbst ist Hardware. Er wird vom Menschen bedient und arbeitet Befehle sukzessive ab
(das Programm). 1968 gab es dafür keine Bildschirme mit anklickbaren Schaltflächen; man benutzte Schalter,
die räumlich konzentriert am sogenannten Bedienpult angeordnet waren. Im Bedienpult befinden sich Lampen,
die den aktuellen Zustand aller Flags anzeigen, sowie Schalter, mit denen ein Mensch diese Flags setzen
oder löschen kann. Der Rechner reagiert als elektronische Hardware auf den Zustand der Flags; ein Mensch
kann den Rechner also über die Schalter beeinflussen. Beispiel: Wird der Schalter BS gesetzt, kann der
Rechner das auswerten, wenn ein entsprechender Befehl es abtestet. Dass BS gesetzt ist, wird im Flag BS
gespeichert und in der Lampe BS angezeigt. Schalter und Flag desselben Namens (z.B. BS) sind also keine
zwei verschiedenen Dinge, sondern zwei Seiten derselben Sache: der Schalter ist die Handlung, das Flag
der gespeicherte Zustand, die Lampe seine Anzeige.

Ein Flag ist ein elektronischer Speicher für den Wert 0 oder 1. Ein Flag setzt seinen Wert nicht selbst,
sondern wird vom Rechenwerk (RW) oder vom Menschen mittels Schalter mit 0 oder 1 belegt; wer zuletzt
setzt, bestimmt den Zustand. Den meisten Flags ist im Bedienpult eine Lampe zugeordnet, damit Menschen
sie erkennen können. Befehle reagieren bei ihrer Abarbeitung im RW auf den Wert bestimmter Flags
oder setzen bestimmte Flags neu.

Flags sind:
| Flag-Name | Beschreibung |
|----|---------------------|
| E  | =1, wenn ein Eingabebefehl aufgestellt ist |
| A  | =1, wenn ein Ausgabebefehl aufgestellt ist |
| T  | Subflag, ist =1 für "Tastatur aktiv" im Kanal K0; T und SW sind ALTERNATIV |
| SW | Subflag, ist =1 für "Schreibwerk (SW) aktiv" im Kanal K0; T und SW sind ALTERNATIV |
| K1 | =1, wenn Kanal 1 angewählt ist |
| K2 | =1, wenn Kanal 2 angewählt ist |
| K3 | =1, wenn Kanal 3 angewählt ist |
| FE | =1, wenn "Fehler bei Eingabe" ; Fehler bei Eingabe tritt ein, wenn im 8-Kanal-Kode ein Zeichen mit einer geraden Zahl von Lochungen eingelesen werden soll (Paritätskontrolle) |
| FÜ | =1, wenn ein Überlauf auftritt. |
| BS | =1, wenn der Rechner einen "bedingten Stopp" Befehl ausführt. |
| US | =1, wenn der Rechner einen "unbedingten Stopp" Befehl ausführt. |
| V1 | Vergleicher 1, =1, wenn gesetzt |
| V2 | Vergleicher 2, =1, wenn gesetzt, V1+V2 sind die 2 Bit des (Pseudo)Vergleichers V3, V3 true ist Sprachgebrauch für V1==1 und V2==1 |
| H  | =1, wenn Schalter H-R auf Stellung "H" (Halt) steht; =0 bei Stellung "R" (Rechnen) |
| SP | =1, wenn Selektor-Schalter "SP" gesetzt ist; Bedingung für "Bedingter Sprung mit Rückkehrabsicht" |

Register sind:                     (dezimal)
  AC       Akkumulator               33 Bit
  V1 / V2  Vergleicher                1 Bit
  OR       Operationsregister         9 Bit ; OR ist identisch mit BAZ
  BZ       Befehlszähler             12 Bit
  AR       Adreßregister             12 Bit
  BR       Befehlsregister           21 Bit ; BR:=a||OR  (a verkettet mit OR)

Weitere Begriffe bei der Beschreibung des Befehlsablaufes sind:
                                   (dezimal)
  a        Adresse                   12 Bit ; Adresse im Adreßteil eines Befehlswortes
  a[1-4]   Adreß-Oktal-Ziffer         3 Bit ; a:=a1 a2 a3 a4
           Spur                       7 Bit ; Bitbreite von Spur-Nr passt exakt zur Trommelgeometrie: 7 Bit → 128 Spuren
           Sektor (auch Zelle)        5 Bit ; Bitbreite von Sektor-Nr passt exakt zur Trommelgeometrie: 5 Bit → 32 Sektoren
           Speicherwort              33 Bit
           Maschinenwort             33 Bit
           Speicher-Trommel        4096 Maschinenworte


Maschinenwort

- Das interne Maschinenwort besteht aus **33 Bit**.
- Es kann gleichermaßen zur Darstellung von **Zahlen, Befehlen oder
  Alpha-Zeichen** dienen; die Art der Interpretation wird durch das
  Programm bestimmt. Verschiedenartige Interpretationen innerhalb eines
  Wortes sind möglich.
- Die 33 Bits werden von links nach rechts als **z₀, z₁, …, z₃₂**
  bezeichnet. Jedes Bit kann mit 0 oder 1 besetzt sein (2³³ mögliche
  Wörter). In jeder Speicherzelle kann ein Wort untergebracht werden.

Die 33 Bit des Maschinenwortes lassen sich in **11 Dreiergruppen
(Triaden)** t₁₀ bis t₀ aufteilen (33 = 11 × 3 Bit, ohne Rest). Jede
Triade entspricht genau einer Oktalziffer.


Das 33-Bit-Maschinenwort enthält in den Bit z₁₂ – z₃₂ das Befehlswort.
Es gliedert sich (in dieser Interpretation) wie folgt:

| Feld | Bits (z-Index) | Breite |
|------|------------------|--------|
| "beliebig" (Original-Bezeichnung) | z₀ – z₁₁ | 12 Bit |
| Maschinenbefehl, davon: | z₁₂ – z₃₂ | 21 Bit |
| Adresse, davon: | z₁₂ – z₂₃ | 12 Bit |
| — Spur-Nr (= Bahn, Synonym) | z₁₂ – z₁₈ | 7 Bit |
| — Sektor-Nr | z₁₉ – z₂₃ | 5 Bit |
| Operation, davon: | z₂₄ – z₃₂ | 9 Bit |
| — B (Befehlstyp) | z₂₄ – z₂₆ | 3 Bit |
| — A (Operationsart) | z₂₇ – z₂₉ | 3 Bit |
| — Z (Operationszusatz), davon: | z₃₀ – z₃₂ | 3 Bit |
| —— R (Resultatbehandlung) ; ACHTUNG: Nicht mit dem R-Befehl verwechseln | z₃₀ – z₃₁ | 2 Bit |
| —— L (Löschbit) | z₃₂ | 1 Bit |

Das Feld "Operation" (z₂₄ – z₃₂) bezeichnet die Bits des Maschinenbefehls, die festlegen, welche
konkrete Durchführung (welcher bestimmte Befehl) gemeint ist. "Operation" im Sinne einer elektronischen
Reaktion ist dagegen die Durchführung dieses Befehls in der Elektronik des Rechners: die Ausführung
eines Maschinenbefehls (kurz: Befehl, auch Befehlswort genannt).
Ein Maschinenbefehl (aus dem Speicher kommend) steht während seiner Ausführung im BR.
Er besteht aus der Adresse ADR (auch a genannt) und dem Operationsteil BAZ (auch OP genannt).
Das Operationsregister OR ist eine elektronische Baueinheit des Rechners; im OR steht der Operationsteil.
Der Maschinenbefehl wird in der Regel aus dem Trommelspeicher geholt. Dort liegt er als Teil (21 Bit)
eines Maschinenwortes (33 Bit) auf einer Befehlsadresse BADR. ADR ist dabei jede beliebige Adresse,
BADR die Adresse eines Befehls; im Sprachgebrauch wird das oft nicht unterschieden.


Die spitzen Klammern <> angewendet bei Registern und Speicheradressen haben die
Bedeutung "Inhalt von". Bei Registern ist das auch die einzige Lesart, beim
Speicher aber macht es den Unterschied; <1000> und 1000, das sind
der Inhalt der Adresse 1000 und die Adresse 1000 selbst.
