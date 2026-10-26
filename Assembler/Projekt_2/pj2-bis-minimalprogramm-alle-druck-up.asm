; C8205 BIS - Hauptprogramm "alle Druckunterprogramme" des Minimalprogramms v6 (pj2-bis_minimalprogramm_v6.asm)
; #DOK-0001 BIS v6: Hauptprogramm alle-druck-up  Adressdruck, Befehlsdruck und Triadendruck nacheinander, 
; #DOK-0001         Start mit Sofortbefehl 000 2000 von K0, Ausgabe auf SW
; #SPEI-0001 0000-0000
; #PROT STUFE=2
; #TROMMEL=MP
; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/pj2-bis-minimalprogramm-alle-druck-up.txt
; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/pj2-bis-minimalprogramm-alle-druck-up
;
; Voraussetzungen: Das KEP und das Minimalprogramm v6 stehen auf der Trommel 
; Dieses Hauptprogramm liegt ab 02000. Es wird mit einem Sofortbefehl gestartet:
; Tastenfolge K0 R bei BZ = 0262 (Eingabe eines Wortes mit Kennzeichen), Band von K0:  1 0 0 0 0 0 2 0 0 0 0 0 0 .
; (K1 = 1, K2 = 0, Wort 00002000000 = Befehl 000 2000; Sprung zum Hauptprogramm).
;
; Ablauf: Schreibwerk SW1 anwaehlen, Kleinbuchstabenlage, dann nacheinander je ein Wort aus den Konstanten ueber die Uebergabezelle
; R1 (7773) an das Druckunterprogramm geben, jeweils mit Zeilenschaltung danach; zuletzt unbedingter Stopp.
;   Adressdruck  (0220): druckt die Ziffern 5 bis 8 des Wortes (Adressteil)       Konstante k_adr = 0123 4567 012
;   Befehlsdruck (0240): druckt die Ziffern 5 bis 11 des Wortes, 4 + 3 Ziffern    Konstante k_bef = 0321 0765 432
;   Triadendruck (0200): druckt alle 11 Ziffern, 4 + 4 + 3 Ziffern                Konstante k_tri = 0765 4321 065
; Erwartete Ausgabe auf SW (von Hand hergeleitet):
;     4567
;     0765 432
;     0765 4321 065
;
; Adressen im Minimalprogramm (Ansprungzellen und Uebergabezelle des Druckteils)
triadendruck:   abs     0200            ; Ansprungzelle Triadendruck (Wort in R1 = 7773)
adressdruck:    abs     0220            ; Ansprungzelle Adressdruck
befehlsdruck:   abs     0240            ; Ansprungzelle Befehlsdruck
adr7773:        abs     07773           ; Uebergabezelle R1

; Absolute Startadresse 02000 per equ, kein Pragma LEITADRESSE (Laden ueber die Testdatei mit #TROMMEL=MP, kein Lochstreifen), Assemblerdokumentation 3.3.12
                start
                equ     02000
haupt:          030     04500           ; Schreibwerk SW1 als Ausgabe anwaehlen
                dz      $inkb           ; Zeichenlage Kleinbuchstaben (beim Start zufaellig)
                211     k_adr           ; AC := Wort fuer den Adressdruck
                240     adr7773         ; Uebergabe in R1
                025     adressdruck     ; Adressdruck
                dz      $wrzl           ; Zeilenschaltung
                211     k_bef           ; AC := Wort fuer den Befehlsdruck
                240     adr7773
                025     befehlsdruck    ; Befehlsdruck
                dz      $wrzl
                211     k_tri           ; AC := Wort fuer den Triadendruck
                240     adr7773
                025     triadendruck    ; Triadendruck
                dz      $wrzl
                020     0               ; unbedingter Stopp
k_adr:          dw      01234567012     ; Adressdruck: Ziffern 5 bis 8 = 4567
k_bef:          dw      03210765432     ; Befehlsdruck: Ziffern 5 bis 11 = 0765 432
k_tri:          dw      07654321065     ; Triadendruck: alle Ziffern = 0765 4321 065
                end
;#PRUEFE-START
; BZ=2017 FE=0 FUE=0 BS=0 US=1 E=0 A=0
; 2016: 00000000020
; 2017: 01234567012
; 2020: 03210765432
; 2021: 07654321065
; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/pj2-bis-minimalprogramm-alle-druck-up-sw-ausgabe.txt
;#PRUEFE-ENDE

