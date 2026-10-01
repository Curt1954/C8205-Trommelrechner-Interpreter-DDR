# ** Variablentabelle T2 **
#
# Variablenname;  Beschreibung der Anweisung oder des Tests;  Behandlungsart
#
# Behandlungsart (unabhängig vom Knotentyp Anweisung/Test):
#   ARW  Ausführen der Operation durch das Rechenwerk (Bedeutung: präzise genug, um direkt als Rechenwerk-Befehl formuliert zu werden)
#   AH   Anweisung wird durch Hardware ausgeführt, nicht vom Rechenwerk. Der Unterschied zu ARW
#        ist fließend: bei ARW lässt sich der resultierende Zustand in Registern, Speicher und
#        Flags ablesen; bei AH ist es eher ein Allgemeinzustand der Hardware, der nicht weiter
#        vertieft wird.
#        Bestätigt für ANWEISUNG-003 (Koinzidenz), ANWEISUNG-004 (Zeitablauf),
#        und ANWEISUNG-031 (Schalterzustände SP).
#   ZST  End-Zustand, den der Knotenautomat erreicht. Von hier aus geht es nicht weiter, der Knotenautomat hält an.
#   V    allgemein formuliert, braucht noch Detailklärung, bevor sie als Befehl abfragbar ist
# Bekannte Lücken in der Nummerierung
#  ANWEISUNG-039 existiert nicht
#
ANWEISUNG-001;  <AR>:=<BZ> && <BZ>:=<AR>+1;  ARW
ANWEISUNG-002;  Merker "X-Abbruch aufgetreten" (durch ANWEISUNG-044 in Phase IV des vorigen Befehls gesetzt) - wenn gesetzt: Koinzidenz gilt als erfüllt, Warten entfällt;  ARW
ANWEISUNG-003;  Am Lese-/Schreibkopf anstehende Sektornummer = Sektor-Feld von AR (z₁₉–z₂₃);  AH
ANWEISUNG-004;  Zeitablauf: eine Wortzeit (104 µs) abwarten (AH, nicht weiter vertieft) — welcher Knoten anschließend angesprungen wird (zurück zum selben Test wie an Knoten 6/27/64, oder Neustart bei Phase I wie an Knoten 47/60) ist Teil der Graph-Verdrahtung, nicht der Definition dieser Anweisung: logisch macht der Knotenautomat in beiden Fällen einfach so weiter, wie er verdrahtet ist. Die Wartezeit selbst ist ein physischer Zustand ohne logische Wirkung — für die interpretative Abarbeitung des Knotenautomaten gilt Wartezeit=0 (wird übergangen, als immer erfüllt gesetzt);  AH
ANWEISUNG-005;  <OR>:=Operationsteil BAZ;  ARW
ANWEISUNG-006;  BAZ B≠0 UND B≠1 UND (A=5 ODER A=7) UND L=1;  ARW
ANWEISUNG-007;  <BZ>:=a (Adreßteil des Befehls);  ARW
ANWEISUNG-008;  (BAZ (B=0 ODER B=1) UND A=4 )  ODER (BAZ (B=0 ODER B=1) UND A=5 ) ODER (BAZ B=0 UND A=7) ODER (BAZ B=1 UND A=7);  ARW
ANWEISUNG-009;  (BAZ B=0 UND A=4 UND AC<0) ODER (BAZ B=0  UND A=5 UND AC=>0) ODER (BAZ B=1 UND A=4 UND (V1 ODER V3)) ODER (BAZ B=1  UND A=5 UND (V2 ODER V3)) ODER (BAZ B=0  UND A=7 UND "Überlauf vorhanden" ) ODER (BAZ B=1 UND A=7 UND V3)  ;  ARW 
ANWEISUNG-010;  interne Umstellung auf A=0;  ARW
ANWEISUNG-011;  Feld L (z₃₂ von BR) = 1 ?;  ARW
ANWEISUNG-012;  <AC>:=0;  ARW
ANWEISUNG-013;  BAZ (B=0 ODER B=1) UND A=2 UND z₃₀=1 (Z=4-7) — Sprung mit Rückkehrabsicht (1./2. Art; erreicht entweder original codiert oder nach Umstellung durch ANWEISUNG-010 aus A=6). Grenzt damit ab von A=2 UND z₃₀=0 (Unbedingter Stop, Z<4 — s. Knoten 20/42/ANWEISUNG-043), der hier NICHT erfasst ist. Die „Umstellung" (Bemerkung in der Befehlsliste) bedeutet: nach Sicherung der Rücksprungadresse in AC (Knoten 40, ANWEISUNG-029) wird der Operationscode auf „Unbedingter Sprung" umgestellt, sodass der Rest des Knotenautomaten den Sprungteil wie einen gewöhnlichen unbedingten Sprung behandelt;  ARW
ANWEISUNG-014;  BAZ (B=0 ODER B=1) UND A=2 UND z₃₀=0;  ARW
ANWEISUNG-015;  BAZ (B=0 ODER B=1) UND A=1;  ARW
ANWEISUNG-016;  BAZ (B=0 ODER B=1) UND A=3;  ARW
ANWEISUNG-017;  keine eigenständige Wirkung über ANWEISUNG-028 hinaus, höchstens Herauslösung der drei informationstragenden Triaden a1,a2,a3 aus dem Adreßteil (ADR hier als Datencode, nicht als Speicheradresse);  ARW
ANWEISUNG-018;  BAZ (B=0 ODER B=1) UND (A=0 ODER A=4 ODER A=5 ODER A=7)  # Sprungbefehl, jeder Untertyp; Kontext Knoten 24: setzt voraus, dass A=1 (Eingabe, Knoten 21), A=2 (Stop/Sprung mit Rückkehrabsicht, Knoten 19/20), A=3 (Ausgabe/Anwahl, Knoten 22) und A=6+z₃₀=1 (bedingter Sprung mit Rückkehrabsicht bzw. Umstellung, Knoten 12–14) an vorherigen Knoten bereits ausgeschlossen wurden;  ARW
ANWEISUNG-019;  BAZ B=3;  ARW
ANWEISUNG-020;  Überlauf (noch) vorhanden;  ARW
ANWEISUNG-021;  Ausführung gemäß BAZ: B wählt den Befehlstyp, A (im Kontext von B) die Operationsart, Z (R + L) Resultatbehandlung und Löschanweisung. Die vollständige Zuordnung Formel ↔ BAZ ist NICHT hier dupliziert, sondern maßgeblich in der Datei "C8205-Interpreter-Befehlsliste-Zwischenstand.md", Abschnitt 4.3 ("Vollständige Befehlsübersicht") und "Einzelbefehlsübersicht" (lexikographisch nach Oktalcode). Diese Datei ist die alleinige Quelle für die Einzelformeln – Änderungen dort wirken automatisch hier.;  ARW
ANWEISUNG-022;  Resultatbehandlung;  ARW
ANWEISUNG-023;  BAZ B=4 ODER B=5 ODER B=6 ODER B=7;  ARW
ANWEISUNG-024;  $ANWEISUNG-040 ODER $ANWEISUNG-041, # normale Abbruchbedingung; sie hat an den Knoten 35 und 77 Vorrang vor der X-Bedingung ANWEISUNG-042, die an Knoten 73 getestet wird; ARW
ANWEISUNG-025;  a:=a+15 mod 40;  ARW
ANWEISUNG-026;  <BZ>:=<AC> "bitweise ODER" a (Adreßteil);  ARW
ANWEISUNG-027;  Umstellung der Operation R-Befehl: im Operationsregister OR wird z₂₇:=0 gesetzt (B und Z bleiben unverändert). Wirkung auf A (z₂₇–z₂₉): 5(101)→1(001) "Addition", 7(111)→3(011) "bedingte Addition/Subtraktion". Da AC zu diesem Zeitpunkt noch ungelöscht ist und L=1 (aus Z=1/5/7) weiterhin gilt, löscht die nun folgende Phase III AC auf 0; Phase IV führt dann Addition bzw. bedingte Addition/Subtraktion mit 0 aus, was genau die R-Lesebefehl- bzw. R-Minuslesebefehl-Wirkung ergibt (⟨AC⟩:=⟨BZ⟩ bzw. ⟨AC⟩:=−⟨BZ⟩, mit BZ = kombinierte Adresse aus Knoten 37);  ARW
ANWEISUNG-028;  z₁₂=1 (Anwahlbefehl, a1≥4) bzw. z₁₂=0 (Ausgabebefehl, a1≤3);  ARW
ANWEISUNG-029;  <AC>:=<AC> "bitweise ODER" mit dem um 1 Bit rechtsverschobenen <BZ>;  ARW
ANWEISUNG-030;  "unbedingter Stopp-Befehl" wird ausgeführt, kein Ausgang, Flag US=1 setzen;  ZST
ANWEISUNG-031;  Test, ob Schalter "BS" gesetzt;  AH
ANWEISUNG-032;  Ausführen der Eingabe;  ARW
ANWEISUNG-033;  Umstellung der Operation Eingabe;  ARW
ANWEISUNG-034;  BAZ B=3;  ARW
ANWEISUNG-035;  Vergleicher 3 setzen;  ARW
ANWEISUNG-036;  BAZ (B=0 ODER B=1) UND A=0;  ARW
ANWEISUNG-037;  Vergleicher korrigieren;  ARW
ANWEISUNG-038;  BAZ B=2;  ARW
ANWEISUNG-040;  BAZ (B=4 ODER B=5 ODER B=6 ODER B=7) UND 32 Sektoren bearbeitet;  ARW  # KORREKTUR (vormals ohne Klammern "B=4 ODER B=5 ODER B=6 ODER B=7 UND 32 Sektoren bearbeitet", was analog zum ANWEISUNG-008-Fehler als "B=4 ODER B=5 ODER B=6 ODER (B=7 UND 32 Sektoren bearbeitet)" fehlgelesen werden konnte und dadurch jeden B=4/5/6-Befehl faelschlich unabhaengig vom Sektorstand hätte abbrechen lassen; Klammern jetzt analog zu ANWEISUNG-008/013 ergaenzt. Inhaltlich gemeint: Abbruch nach 32 bearbeiteten Sektoren gilt fuer JEDEN Gruppen-/Wiederholungsbefehl (B=4,5,6,7 gleichermassen)
ANWEISUNG-041;  BAZ (B=6 ODER B=7) UND Sektor 23 erreicht (Sonderfall: Startadresse mit Sektor 0 → diese Bedingung wird NICHT ausgewertet, stattdessen wirkt der Befehl wie ein Gruppenbefehl, d. h. es gilt dann nur noch ANWEISUNG-040 als Abbruch nach 32 Sektoren, s. Befehlsliste 4.1.7);  ARW  # KORREKTUR (vormals ohne Klammern "B=6 ODER B=7 UND Sektor 23 erreicht", was analog zum ANWEISUNG-008-Fehler als "B=6 ODER (B=7 UND Sektor 23 erreicht)" fehlgelesen werden konnte und dadurch jeden B=6-Befehl faelschlich immer (unabhaengig vom Sektorstand) hätte abbrechen lassen; Klammern jetzt analog zu ANWEISUNG-008/013/040 ergaenzt. Inhaltlich gemeint: der Sektor-23-Sonderabbruch gilt gleichermassen fuer B=6 UND B=7 (Wiederholungsbefehle), nicht unbedingt fuer B=6 allein
ANWEISUNG-042;  BAZ (B=5 ODER B=7) UND AC<0, wobei das Vorzeichenbit R-abhängig gewählt wird: bei R≠1 (also R=0,2,3) ist z₀ das Vorzeichen, bei R=1 (Rechtsverschiebung) ist stattdessen z₃₂ das Vorzeichen (weil Vr das eigentliche z₀ auf 0 zwingt, s. Befehlsliste 4.1.6 und 4.2.1a). Getestet wird nach Operation und Resultatbehandlung (ANWEISUNG-022) der soeben bearbeiteten Zelle an Knoten 73. Ist die Bedingung erfüllt, werden Operation und Resultatbehandlung noch mit genau einer weiteren Zelle ausgeführt (Knoten 74 bis 76), danach erfolgt der Abbruch;  ARW  # KORREKTUR (vormals ohne Klammern "B=5 ODER B=7 UND AC<0", was analog zum ANWEISUNG-008-Fehler als "B=5 ODER (B=7 UND AC<0)" fehlgelesen werden konnte und dadurch jeden B=5-Befehl faelschlich immer, unabhaengig vom AC-Vorzeichen, hätte abbrechen lassen; Klammern jetzt analog zu ANWEISUNG-008/013/040/041 ergaenzt. Inhaltlich gemeint: der X-Abbruch bei negativem AC gilt gleichermassen fuer B=5 UND B=7 (die beiden "bedingten" Gruppen-/Wiederholungsbefehlsarten)
ANWEISUNG-043;  BAZ (B=0 ODER B=1) UND (A=2 UND z₃₀=0 ODER A=6 UND z₃₀=0);  ARW
ANWEISUNG-044;  Merker "X-Abbruch aufgetreten" setzen (Knoten 78: der Abbruch erfolgte durch die X-Bedingung ANWEISUNG-042, nicht durch die normale Abbruchbedingung ANWEISUNG-024); der Merker wird an Knoten 4 (ANWEISUNG-002) beim Auswerten gelöscht;  ARW
