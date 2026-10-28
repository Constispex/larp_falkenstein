# Gutsbericht: monatliche Chronik des Ritterguts Falkenstein

Einmal im Monat erscheint eine Ausgabe: als Text (`.md`) und als mittelalterlich gestaltetes PDF. Jede Ausgabe berichtet einen Spielmonat weiter. Es gelten zusätzlich die Regeln aus `../CLAUDE.md`.

## Dateien

```
Gutsstatus.md          Spielstand aller Bereiche, Kasse, offene Entscheidungen, Ausgabenliste
Vorlage_Ausgabe.json   leere Vorlage für eine neue Ausgabe (Felder erklärt in diesem Dokument)
vorlage_bericht.html   Druckvorlage (Pergament, Fraktur); Platzhalter {{...}}
bericht_bauen.py       baut aus der JSON den Text (.md), die Druckvorlage (.html) und das PDF
Ausgaben/              je Ausgabe NrNN_Monat_Jahr.json/.md/.html/.pdf
```

PDF bauen: `python3 bericht_bauen.py Ausgaben/NrNN_Monat_Jahr.json` (braucht Chromium; in der Cloud-Umgebung vorhanden. Auf Constantins PC ist kein Chromium; dort nur lesen). Gearbeitet wird im Repo `Constispex/larp_falkenstein` (Pfade relativ zu `Gutsbericht/`).

## Ablauf einer neuen Ausgabe

1. `Gutsstatus.md`, `../Kontinuitaet.md` und die letzte Ausgabe lesen. Prüfen, ob Constantin Ereignisse bestätigt, abgelehnt oder Entscheidungen getroffen hat (Entscheidungskarten im Thread, Kontinuität). Abgelehnte Wirkungen im Status zurücknehmen. **Jede getroffene Entscheidung zeigt im neuen Monat sichtbare Folgen**: in mindestens einem Ereignis, in den Bereichen und in der Haltung der betroffenen NPCs. Unbeantwortete Entscheidungen: die Schreibstube handelt nach ihrem Rat (Empfehlung) und sagt das im Bericht.
2. Den nächsten Spielmonat bestimmen (Monatsfolge in `Gutsstatus.md`).
3. **4–5 Ereignisse** entwerfen, immer **gute und schlechte** gemischt (mindestens je eines, gern ein zwiespältiges). Jedes Ereignis wirkt auf **mehrere Bereiche**; über alle Ereignisse hinweg soll jeder Bereich im Blick sein (in der Tabelle steht sonst „–“ und die Lage wird trotzdem beschrieben).
4. Bereiche: Kasse und Finanzen · Felder und Ernte · Steinmühle · Forst und Köhlerei · Steinbruch (Kalkstein) · Bergbau Kaltentann · Herberge und Weststraße · Burg und Befestigung · Sicherheit und Wehr · Bevölkerung und Stimmung · Beziehungen (Markgraf, Kanzlei, Junker von Elzwalde, Kirche).
5. Stufen (1–5) nur ändern, wenn sich ein Bereich über einen oder mehrere Monate deutlich bewegt hat; einzelne Pfeile reichen nicht.
6. Kasse nach [F]: Tageskraft 9 S/Tag (5 S eigen + 4 S Grenzzulage), also 270 S je Monat; kleine Ereignisbeträge gehen dagegen. Große Ausgaben gehen an die Barreserve (Start 8.100 S). Regeln im Abschnitt „Kasse“ von `Gutsstatus.md`.
7. **Schreiben an Mitspieler:** Echte Mitspieler (nie ausspielen, keine Antworten vorwegnehmen): **Vilmos von Freiberg** (Markgraf), **der Junker von Elzwalde**, **der Ritter von Markwacht**, **Baron Kirschgeu**. Betrifft ein Ereignis einen von ihnen, einen Brief von Varion entwerfen, und zwar **mit der Briefvorlage**: JSON in `../Schreiben/JJJJ-MM-TT_Betreff.json` (Felder: `empfaenger` = vilmos | elzwalde | markwacht | kirschgeu, `ueberschrift`, `absaetze`, `datum`, optional `anlass`, `status`), bauen mit `python3 ../Schreiben/Vorlage/brief_bauen.py ../Schreiben/<Datei>.json`. Regeln in `../CLAUDE.md`, Abschnitt „Schreiben an Mitspieler“; Beispiel `../Schreiben/2026-10-28_Lage_am_Gut_Travia_1053.json`. In der Ausgabe-JSON nur verweisen: `schreiben: [{"an": "Seine Erlaucht", "datei": "<Dateiname ohne Endung>", "anlass": "…"}]`; die Chronik zeigt dann „Beigelegt: …“. **Jeder Brief ist ein eigenes PDF** in `../Schreiben/` (Wunsch Constantin): `bericht_bauen.py` baut beigelegte Briefe automatisch mit, sobald ihre JSON in `../Schreiben/` liegt. Brief-PDFs Constantin zusammen mit der Chronik schicken. Der Brief trifft keine Entscheidung, die Constantin nicht getroffen hat. Im Brief kein Wappen (vorerst, Wunsch Constantin).
7b. **Entscheidungen:** 2–4 je Ausgabe, jede mit 2–4 Antworten (`frage`, `optionen` mit `label` ≤ 40 Bytes und `folge` ≤ 200 Bytes, `empfehlung` = Index). Jede Antwort nennt ihre Folgen für Bereiche **und** Beziehungen. Mindestens eine Entscheidung soll eine persönliche Beziehung zu einem NPC berühren. Spieler-Abmachungen (Mitspieler) nie über Karten entscheiden, sondern nur Briefentwürfe anbieten.
7c. **Haltung der NPCs:** Ereignisse und Entscheidungen verschieben die Haltung (−2 bis +2) in `Gutsstatus.md`. Die Haltung färbt Ereignisse: Gewogene helfen, Verstimmte murren, verzögern oder streuen Gerüchte. Hintergrund der Beziehungen steht in `../Kontinuitaet.md` Abschnitt 2; bestätigte Verschiebungen dort unter „Ausgespielt“ nachtragen.
7d. **Im Jahreskreis:** Fällt in den Monat ein Fest oder Brauch, eine kleine Szene ins Feld `fest` (`name`, `text`) schreiben und gern eine Entscheidung daraus machen (Wie begeht Varion das Fest? Was spendet er? Wen lädt er ein?). Jeder Monat steht unter seinem Gott (Praios, Rondra, Efferd, Travia, Boron, Hesinde, Firun, Tsa, Phex, Peraine, Ingerimm, Rahja), dazu die Namenlosen Tage als Unglückstage vor Neujahr. Feste und Bräuche sind ⚑ Vorschläge im DSA-Ton; Einzelheiten aus dem offiziellen Kalender nicht als Kanon behaupten, wenn nicht nachgeprüft. Kanon im Gut: Praiosfest (Lehnszehnt), Kapelle in Hochfeld dem Praios geweiht [G], Kirchenzehnt an Rondra [F].
7e. **Was man sich erzählt:** 3–5 Gerüchte und Dorfgeschichten im Feld `geruechte` (`quelle` = Herberge zum Silberbach, Hochfeld, Silberbach, Weststraße …; `text`). Gesprächsstoff für Szenen und Aufhänger für spätere Ereignisse. Gerüchte dürfen offene Fragen berühren (Vogt, bläuliche Ader, Silber im Kaltentann), aber nie auflösen; wahr oder falsch bleibt offen. Haltungen der NPCs färben, wer was erzählt. Nichts über Mitspieler behaupten, was sie nicht selbst ins Spiel gebracht haben.
8. JSON unter `Ausgaben/` anlegen, Skript ausführen, PDF ansehen (4 Seiten erwartet, nichts abgeschnitten).
9. `Gutsstatus.md` fortschreiben: Bereiche, Kasse, offene Entscheidungen, Ausgabenliste.
9b. Alle neuen und geänderten Dateien (Ausgabe, Briefe, `Gutsstatus.md`, `../Kontinuitaet.md`, Tagebuch) im Repo committen und pushen.
10. Constantin Text und PDF schicken (kurze Liste der Ereignisse), danach **jede Entscheidung als eigene Karte im Chat** stellen (`request_decision`: Frage, Antworten mit Folgen, Empfehlung). Antworten in `Gutsstatus.md` unter „Entscheidungen“ mit ihren Folgen eintragen.

## Regeln für Ereignisse

- Grundlage ist der Ausdruck [F] (`../docs/Gutsbeschreibung_1053_Ausdruck.md`); `falkenstein_gesamt.html` [G] ergänzt, wo es [F] nicht widerspricht (Entscheid Constantin, 28.10.2026). `gut_falkenstein.html` [E] ist veraltet, bis auf Familiengeschichte, Varions Knappenzeit und den alten Vogt (weiter Kanon). Garnison: 2 Waffenknechte (Turmwache, Straßenpatrouille).

- Alle Ereignisse sind ⚑ **Vorschläge**, kein vergangener Kanon, bis Constantin sie bestätigt. Im Text steht das als Hinweis oben (md) bzw. unten (PDF).
- Nichts festlegen, was offen ist: Inbetriebnahmekosten Kaltentann (Quellenabgleich Nr. 2), Schuld des alten Vogts, Natur der bläulichen Ader, Höhe des Lehnszehnts. Ereignisse dürfen diese Fragen berühren (Gerücht, Brief, Anfrage), aber nicht beantworten.
- Die Förderung am Kaltentann beginnt erst, wenn Constantin sie freigibt. Danach gelten die Pflichten aus [A][B] (vierteljährlicher Bericht an die Kanzlei, ungewöhnliche Funde sofort an Obrist und Kanzlei).
- Kanon-Figuren nur im Rahmen ihrer Profile einsetzen (`../NPC-Profile/`). Neue Nebenfiguren als ⚑ in `../NPC-Profile/Nebenfiguren.md` festhalten.
- Ton: Chronik einer gutsherrlichen Schreibstube, Mittelreich, Zwölfgötter, Monatsnamen nach BF, Silbertaler (S). Varion heißt **Varion** (ältere Unterlagen schreiben teils Navarion). Anrede „Euer Wohlgeboren“, Markgraf „Euer Erlaucht“.
- Jahreszeit beachten: Ernte im Travia/Efferd, Winter Firun, Aussaat Peraine, Praiosfest mit Lehnszehnt. Monatliche Aufgebotsübung [F] eignet sich als wiederkehrender Anlass.
