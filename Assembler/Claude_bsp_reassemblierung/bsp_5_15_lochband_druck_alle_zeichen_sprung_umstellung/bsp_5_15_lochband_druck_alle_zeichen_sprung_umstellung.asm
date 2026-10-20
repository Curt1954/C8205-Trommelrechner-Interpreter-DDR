; bsp_5_15_lochband_druck_alle_zeichen_sprung_umstellung.asm  -  symbolisches Assemblerprogramm zu Testdatei
;   bsp_5_15_lochband_druck_alle_zeichen_sprung_umstellung.txt
; #DOK-0003 Prüfung der Sprung-Umstellung aller Zeichen des R 300-Codes (Streifen r300_alle_zeichen.txt, "/" am Ende), Leser 2
; --leser2 Test-virtuelleGeraete/Leser2/r300_alle_zeichen.txt
; #PROT STUFE=2
; Automatisch vergebene Symbole (Zahl = Adresse im Original): m = Befehlszelle/Sprungziel, d = Daten-/Arbeitszelle, t = Textzelle; Symbole
;   ohne Zelle im Programm sind am Ende per abs definiert.

                start

; Zweck: Der Test macht die Spalte "Sprung-Umstellung" der Tabelle 1 prüfbar. Der Eingabebefehl 011 3000 wählt die Zelle 3000 v
;   Eingabeadresse.
; - Sprung-Umstellung ja: Der Rechner löscht den AC und springt in die Zelle. Sie enthält einen Sprung zu einer eigenen Routine, die den AC
; in die Markenzelle 34xx (xx = Eingabeadresse) speichert. Erwartet: AC = 0, Marke = 0.
; - Sprung-Umstellung nein: Der Rechner addiert den Zelleninhalt zum gelöschten AC. Die Zelle enthält den Speicherbefehl "240 34xx".
; Er wird bei 3105 ausgeführt. Erwartet: Marke = dieser Befehl selbst (AC = Zelleninhalt).
; Wird ein Zeichen falsch eingeordnet, hat die Marke einen anderen Wert und die Prüfung der Marke schlägt fehl.
; Die Marken sind mit 77777777777 vorbelegt, so fällt auch ein Zeichen auf, das gar nicht gelesen wird.
; Das Zeichen "/" (Eingabeadresse 61, Sprung-Umstellung ja) beendet den Streifen: Zelle 3061 = unbedingter Stopp; bei falscher Einordnung
; stoppt der Rechner stattdessen bei 3105 (BZ=3106).
; "Irrung Zeichen" (gerade Parität) wird vom Leser übersprungen, "Transport" (Relikt) fehlt im Streifen.

; Startstück
m0000:          000     m3100                    ; Sprung zum Startstück
                equ     03100
m3100:          030     04500                    ; Anwahl Kanal K2 (Leser 2)
                000     m3102                    ; Sprung zur Eingabe

; Eingabeschleife
m3102:          011     m3000                    ; Eingabe eines Zeichens, <AC> := Zelleninhalt, falls Umstellung in Addition
                240     m3105                    ; <3105> := <AC>
                000     m3105                    ; Sprung zu 3105
m3105:          000     m0000                    ; (wird zur Laufzeit gesetzt)
                000     m3102                    ; Sprung zur Eingabe

; Zeichenzellen (3000-3077), Routinen (ab 3200), Marken (3400-3477)
                equ     03000
m3000:          240     d3400                    ; "0 / #" (Eingabe 00, Sprung-Umstellung nein): <3400> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3401                    ; "1 / <" (Eingabe 01, Sprung-Umstellung nein): <3401> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3402                    ; "2 / "" (Eingabe 02, Sprung-Umstellung nein): <3402> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3403                    ; "3 / ≈" (Eingabe 03, Sprung-Umstellung nein): <3403> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3404                    ; "4 / [" (Eingabe 04, Sprung-Umstellung nein): <3404> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3405                    ; "5 / >" (Eingabe 05, Sprung-Umstellung nein): <3405> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3406                    ; "6 / '" (Eingabe 06, Sprung-Umstellung nein): <3406> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3407                    ; "7 / ≋" (Eingabe 07, Sprung-Umstellung nein): <3407> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3410                    ; "8 / ~" (Eingabe 10, Sprung-Umstellung nein): <3410> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3411                    ; "9 / ]" (Eingabe 11, Sprung-Umstellung nein): <3411> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                000     m3222                    ; "Leertaste / ZR" (Eingabe 12, Sprung-Umstellung ja): Sprung zur Routine
                equ     03015
                000     m3202                    ; ": / (" (Eingabe 15, Sprung-Umstellung ja): Sprung zur Routine
                000     m3224                    ; "Irrung Satz" (Eingabe 16, Sprung-Umstellung ja): Sprung zur Routine
                equ     03020
                000     m3204                    ; "+ / =" (Eingabe 20, Sprung-Umstellung ja): Sprung zur Routine
                240     d3421                    ; "a / A" (Eingabe 21, Sprung-Umstellung nein): <3421> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3422                    ; "b / B" (Eingabe 22, Sprung-Umstellung nein): <3422> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3423                    ; "c / C" (Eingabe 23, Sprung-Umstellung nein): <3423> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3424                    ; "d / D" (Eingabe 24, Sprung-Umstellung nein): <3424> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3425                    ; "e / E" (Eingabe 25, Sprung-Umstellung nein): <3425> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3426                    ; "f / F" (Eingabe 26, Sprung-Umstellung nein): <3426> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3427                    ; "g / G" (Eingabe 27, Sprung-Umstellung nein): <3427> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3430                    ; "h / H" (Eingabe 30, Sprung-Umstellung nein): <3430> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3431                    ; "i † / I" (Eingabe 31, Sprung-Umstellung nein): <3431> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                000     m3212                    ; "SatzMarke / WRZL" (Eingabe 32, Sprung-Umstellung ja): Sprung zur Routine
                000     m3216                    ; ". / !" (Eingabe 33, Sprung-Umstellung ja): Sprung zur Routine
                equ     03037
                000     m3210                    ; "Um. GB" (Eingabe 37, Sprung-Umstellung ja): Sprung zur Routine
                000     m3220                    ; "- / △" (Eingabe 40, Sprung-Umstellung ja): Sprung zur Routine
                240     d3441                    ; "j / J" (Eingabe 41, Sprung-Umstellung nein): <3441> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3442                    ; "k / K" (Eingabe 42, Sprung-Umstellung nein): <3442> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3443                    ; "l / L" (Eingabe 43, Sprung-Umstellung nein): <3443> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3444                    ; "m / M" (Eingabe 44, Sprung-Umstellung nein): <3444> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3445                    ; "n / N" (Eingabe 45, Sprung-Umstellung nein): <3445> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3446                    ; "o / O" (Eingabe 46, Sprung-Umstellung nein): <3446> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3447                    ; "p / P" (Eingabe 47, Sprung-Umstellung nein): <3447> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3450                    ; "q / Q" (Eingabe 50, Sprung-Umstellung nein): <3450> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3451                    ; "r / R" (Eingabe 51, Sprung-Umstellung nein): <3451> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                equ     03057
                000     m3206                    ; "Um. KB" (Eingabe 57, Sprung-Umstellung ja): Sprung zur Routine
                240     d3460                    ; "` / ;" (Eingabe 60, Sprung-Umstellung nein): <3460> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                020     0                        ; "/" (Eingabe 61, Streifenende): unbedingter Stopp, Sprung-Umstellung ja
                240     d3462                    ; "s / S" (Eingabe 62, Sprung-Umstellung nein): <3462> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3463                    ; "t / T" (Eingabe 63, Sprung-Umstellung nein): <3463> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3464                    ; "u / U" (Eingabe 64, Sprung-Umstellung nein): <3464> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3465                    ; "v / V" (Eingabe 65, Sprung-Umstellung nein): <3465> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3466                    ; "w / W" (Eingabe 66, Sprung-Umstellung nein): <3466> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3467                    ; "x / X" (Eingabe 67, Sprung-Umstellung nein): <3467> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3470                    ; "y / Y" (Eingabe 70, Sprung-Umstellung nein): <3470> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                240     d3471                    ; "z / Z" (Eingabe 71, Sprung-Umstellung nein): <3471> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                equ     03073
                000     m3214                    ; ", / ?" (Eingabe 73, Sprung-Umstellung ja): Sprung zur Routine
                240     d3474                    ; "% / *" (Eingabe 74, Sprung-Umstellung nein): <3474> := <AC> (erwartet: dieser Befehl
;                                                selbst)
                000     m3200                    ; "Tabulator" (Eingabe 75, Sprung-Umstellung ja): Sprung zur Routine
                equ     03200
m3200:          240     d3475                    ; <3475> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3202:          240     d3415                    ; <3415> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3204:          240     d3420                    ; <3420> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3206:          240     d3457                    ; <3457> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3210:          240     d3437                    ; <3437> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3212:          240     d3432                    ; <3432> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3214:          240     d3473                    ; <3473> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3216:          240     d3433                    ; <3433> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3220:          240     d3440                    ; <3440> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3222:          240     d3412                    ; <3412> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
m3224:          240     d3416                    ; <3416> := <AC>  (erwartet 0)
                000     m3102                    ; Sprung zur Eingabe
                equ     03400
d3400:          dw      077777777777             ; Marke für "0 / #" (Eingabe 00): Vorbelegung, wird bei Lauf überschrieben
d3401:          dw      077777777777             ; Marke für "1 / <" (Eingabe 01): Vorbelegung, wird bei Lauf überschrieben
d3402:          dw      077777777777             ; Marke für "2 / "" (Eingabe 02): Vorbelegung, wird bei Lauf überschrieben
d3403:          dw      077777777777             ; Marke für "3 / ≈" (Eingabe 03): Vorbelegung, wird bei Lauf überschrieben
d3404:          dw      077777777777             ; Marke für "4 / [" (Eingabe 04): Vorbelegung, wird bei Lauf überschrieben
d3405:          dw      077777777777             ; Marke für "5 / >" (Eingabe 05): Vorbelegung, wird bei Lauf überschrieben
d3406:          dw      077777777777             ; Marke für "6 / '" (Eingabe 06): Vorbelegung, wird bei Lauf überschrieben
d3407:          dw      077777777777             ; Marke für "7 / ≋" (Eingabe 07): Vorbelegung, wird bei Lauf überschrieben
d3410:          dw      077777777777             ; Marke für "8 / ~" (Eingabe 10): Vorbelegung, wird bei Lauf überschrieben
d3411:          dw      077777777777             ; Marke für "9 / ]" (Eingabe 11): Vorbelegung, wird bei Lauf überschrieben
d3412:          dw      077777777777             ; Marke für "Leertaste / ZR" (Eingabe 12): Vorbelegung, wird bei Lauf überschrieben
                equ     03415
d3415:          dw      077777777777             ; Marke für ": / (" (Eingabe 15): Vorbelegung, wird bei Lauf überschrieben
d3416:          dw      077777777777             ; Marke für "Irrung Satz" (Eingabe 16): Vorbelegung, wird bei Lauf überschrieben
                equ     03420
d3420:          dw      077777777777             ; Marke für "+ / =" (Eingabe 20): Vorbelegung, wird bei Lauf überschrieben
d3421:          dw      077777777777             ; Marke für "a / A" (Eingabe 21): Vorbelegung, wird bei Lauf überschrieben
d3422:          dw      077777777777             ; Marke für "b / B" (Eingabe 22): Vorbelegung, wird bei Lauf überschrieben
d3423:          dw      077777777777             ; Marke für "c / C" (Eingabe 23): Vorbelegung, wird bei Lauf überschrieben
d3424:          dw      077777777777             ; Marke für "d / D" (Eingabe 24): Vorbelegung, wird bei Lauf überschrieben
d3425:          dw      077777777777             ; Marke für "e / E" (Eingabe 25): Vorbelegung, wird bei Lauf überschrieben
d3426:          dw      077777777777             ; Marke für "f / F" (Eingabe 26): Vorbelegung, wird bei Lauf überschrieben
d3427:          dw      077777777777             ; Marke für "g / G" (Eingabe 27): Vorbelegung, wird bei Lauf überschrieben
d3430:          dw      077777777777             ; Marke für "h / H" (Eingabe 30): Vorbelegung, wird bei Lauf überschrieben
d3431:          dw      077777777777             ; Marke für "i † / I" (Eingabe 31): Vorbelegung, wird bei Lauf überschrieben
d3432:          dw      077777777777             ; Marke für "SatzMarke / WRZL" (Eingabe 32): Vorbelegung, wird bei Lauf überschrieben
d3433:          dw      077777777777             ; Marke für ". / !" (Eingabe 33): Vorbelegung, wird bei Lauf überschrieben
                equ     03437
d3437:          dw      077777777777             ; Marke für "Um. GB" (Eingabe 37): Vorbelegung, wird bei Lauf überschrieben
d3440:          dw      077777777777             ; Marke für "- / △" (Eingabe 40): Vorbelegung, wird bei Lauf überschrieben
d3441:          dw      077777777777             ; Marke für "j / J" (Eingabe 41): Vorbelegung, wird bei Lauf überschrieben
d3442:          dw      077777777777             ; Marke für "k / K" (Eingabe 42): Vorbelegung, wird bei Lauf überschrieben
d3443:          dw      077777777777             ; Marke für "l / L" (Eingabe 43): Vorbelegung, wird bei Lauf überschrieben
d3444:          dw      077777777777             ; Marke für "m / M" (Eingabe 44): Vorbelegung, wird bei Lauf überschrieben
d3445:          dw      077777777777             ; Marke für "n / N" (Eingabe 45): Vorbelegung, wird bei Lauf überschrieben
d3446:          dw      077777777777             ; Marke für "o / O" (Eingabe 46): Vorbelegung, wird bei Lauf überschrieben
d3447:          dw      077777777777             ; Marke für "p / P" (Eingabe 47): Vorbelegung, wird bei Lauf überschrieben
d3450:          dw      077777777777             ; Marke für "q / Q" (Eingabe 50): Vorbelegung, wird bei Lauf überschrieben
d3451:          dw      077777777777             ; Marke für "r / R" (Eingabe 51): Vorbelegung, wird bei Lauf überschrieben
                equ     03457
d3457:          dw      077777777777             ; Marke für "Um. KB" (Eingabe 57): Vorbelegung, wird bei Lauf überschrieben
d3460:          dw      077777777777             ; Marke für "` / ;" (Eingabe 60): Vorbelegung, wird bei Lauf überschrieben
                equ     03462
d3462:          dw      077777777777             ; Marke für "s / S" (Eingabe 62): Vorbelegung, wird bei Lauf überschrieben
d3463:          dw      077777777777             ; Marke für "t / T" (Eingabe 63): Vorbelegung, wird bei Lauf überschrieben
d3464:          dw      077777777777             ; Marke für "u / U" (Eingabe 64): Vorbelegung, wird bei Lauf überschrieben
d3465:          dw      077777777777             ; Marke für "v / V" (Eingabe 65): Vorbelegung, wird bei Lauf überschrieben
d3466:          dw      077777777777             ; Marke für "w / W" (Eingabe 66): Vorbelegung, wird bei Lauf überschrieben
d3467:          dw      077777777777             ; Marke für "x / X" (Eingabe 67): Vorbelegung, wird bei Lauf überschrieben
d3470:          dw      077777777777             ; Marke für "y / Y" (Eingabe 70): Vorbelegung, wird bei Lauf überschrieben
d3471:          dw      077777777777             ; Marke für "z / Z" (Eingabe 71): Vorbelegung, wird bei Lauf überschrieben
                equ     03473
d3473:          dw      077777777777             ; Marke für ", / ?" (Eingabe 73): Vorbelegung, wird bei Lauf überschrieben
d3474:          dw      077777777777             ; Marke für "% / *" (Eingabe 74): Vorbelegung, wird bei Lauf überschrieben
d3475:          dw      077777777777             ; Marke für "Tabulator" (Eingabe 75): Vorbelegung, wird bei Lauf überschrieben

                end

; Tastenfolge:
; H G R
;
; Prüfungen:
; BZ=3062 AC=00000000000 AR=0000 FE=0 FUE=0 BS=0 US=1 E=0 A=0 V1=0 V2=0
; 3061: 00000000020
; 3400: 00003400240
; 3401: 00003401240
; 3402: 00003402240
; 3403: 00003403240
; 3404: 00003404240
; 3405: 00003405240
; 3406: 00003406240
; 3407: 00003407240
; 3410: 00003410240
; 3411: 00003411240
; 3412: 00000000000
; 3415: 00000000000
; 3416: 00000000000
; 3420: 00000000000
; 3421: 00003421240
; 3422: 00003422240
; 3423: 00003423240
; 3424: 00003424240
; 3425: 00003425240
; 3426: 00003426240
; 3427: 00003427240
; 3430: 00003430240
; 3431: 00003431240
; 3432: 00000000000
; 3433: 00000000000
; 3437: 00000000000
; 3440: 00000000000
; 3441: 00003441240
; 3442: 00003442240
; 3443: 00003443240
; 3444: 00003444240
; 3445: 00003445240
; 3446: 00003446240
; 3447: 00003447240
; 3450: 00003450240
; 3451: 00003451240
; 3457: 00000000000
; 3460: 00003460240
; 3462: 00003462240
; 3463: 00003463240
; 3464: 00003464240
; 3465: 00003465240
; 3466: 00003466240
; 3467: 00003467240
; 3470: 00003470240
; 3471: 00003471240
; 3473: 00000000000
; 3474: 00003474240
; 3475: 00000000000
;
