"""Baut aus einer Ausgabe-JSON den Textbericht (.md), die Druckvorlage (.html) und das PDF.

Aufruf:  python3 bericht_bauen.py Ausgaben/Nr01_Travia_1053.json
Das PDF braucht Chromium (in der Cloud-Umgebung unter /opt/pw-browsers/chromium; sonst Umgebungsvariable CHROMIUM setzen).
"""
import html
import json
import sys
from pathlib import Path

HIER = Path(__file__).parent
STUFEN = {1: "verfallen", 2: "schlecht", 3: "mittel", 4: "gut", 5: "blühend"}
PFEIL = {"+": "▲", "-": "▼", "o": "●"}
ART = {"gut": "Gutes", "schlecht": "Schlechtes", "gemischt": "Zwiespältiges"}


def s(betrag):
    return f"{betrag:+d} S".replace("-", "−")


def trend(b):
    if b["nachher"] > b["vorher"]:
        return "▲"
    if b["nachher"] < b["vorher"]:
        return "▼"
    return "●"


def wirkungen_je_bereich(d):
    """Sammelt die Pfeile aller Ereignisse je Bereich, damit jeder Bereich im Überblick erscheint."""
    sammlung = {b["name"]: [] for b in d["bereiche"]}
    for e in d["ereignisse"]:
        for w in e["wirkungen"]:
            sammlung.setdefault(w["bereich"], []).append(PFEIL[w["richtung"]])
    return sammlung


def alle_schreiben(d):
    """Beigelegte Briefe an Mitspieler. Sie werden mit der Briefvorlage in ../Schreiben/ gebaut, hier nur verwiesen."""
    return d.get("schreiben", [])


def als_markdown(d):
    z = [f"# {d['titel']}", "", f"Ausgabe Nr. {d['nr']} · {d['monat']} {d['jahr']} · {d['verfasser']}", ""]
    z += ["> ⚑ **Vorschlag, kein Kanon.** Alle Ereignisse dieser Ausgabe gelten erst nach Constantins Bestätigung. "
          "Belegte Ausgangswerte stammen aus dem Übergabebefund [E].", ""]
    z += [d["anrede"], "", d["einleitung"], "", "## Was geschah"]
    for e in d["ereignisse"]:
        z += ["", f"### {e['titel']} ({ART[e['art']]})", "", e["text"], ""]
        for w in e["wirkungen"]:
            betrag = f" ({s(w['betrag'])})" if "betrag" in w else ""
            z.append(f"- {PFEIL[w['richtung']]} {w['bereich']}{betrag}: {w['notiz']}")
    if d.get("fest"):
        f = d["fest"]
        z += ["", f"## Im Jahreskreis: {f['name']}", "", f["text"]]
    if d.get("geruechte"):
        z += ["", "## Was man sich erzählt", "", "*Gerüchte, wahr oder nicht. Die Schreibstube verbürgt sich für keines.*", ""]
        z += [f"- **{g['quelle']}:** {g['text']}" for g in d["geruechte"]]
    z += ["", "## Stand der Bereiche", "", "| Bereich | Wirkungen | Stufe | Lage |", "|---|---|---|---|"]
    ww = wirkungen_je_bereich(d)
    for b in d["bereiche"]:
        stufe = f"{b['nachher']} {STUFEN[b['nachher']]} {trend(b)}"
        z.append(f"| {b['name']} | {' '.join(ww[b['name']]) or '–'} | {stufe} | {b['lage']} |")
    k = d["kasse"]
    z += ["", "## Kasse", "", "| Posten | Betrag |", "|---|---|"]
    z += [f"| {posten} | {betrag} |" for posten, betrag in k["zeilen"]]
    z += ["", f"Barreserve: **{k['reserve']}**", ""]
    z += ["## Zu Eurem Entscheid", ""]
    for x in d["entscheidungen"]:
        if isinstance(x, str):
            z.append(f"- {x}")
            continue
        z += [f"**{x['frage']}**", ""]
        for i, o in enumerate(x["optionen"]):
            rat = " *(Rat der Schreibstube)*" if i == x.get("empfehlung") else ""
            z.append(f"- {'abcd'[i]}) **{o['label']}**{rat}: {o['folge']}")
        z.append("")
    z += ["", "## Ausblick", ""] + [f"- {x}" for x in d["ausblick"]]
    z += ["", f"*{d['schluss']}*", ""]
    if alle_schreiben(d):
        z += ["## Beigelegte Schreiben (Entwürfe, ⚑)", ""]
        z += [f"- An {sv['an']}: `../Schreiben/{sv['datei']}.pdf` – {sv.get('anlass', '')}" for sv in alle_schreiben(d)]
        z.append("")
    z += ["Skala: 1 verfallen · 2 schlecht · 3 mittel · 4 gut · 5 blühend. ▲ besser · ▼ schlechter · ● spürbar, ohne Richtung.", ""]
    return "\n".join(z)


def als_html(d):
    e_ = html.escape
    teile = []
    for i, e in enumerate(d["ereignisse"]):
        wirk = "".join(
            f'<li><span class="pf {w["richtung"]}">{PFEIL[w["richtung"]]}</span> {e_(w["bereich"])}'
            + (f' <b>{s(w["betrag"])}</b>' if "betrag" in w else "")
            + f' <i>– {e_(w["notiz"])}</i></li>'
            for w in e["wirkungen"]
        )
        teile.append(
            f'<section class="ereignis {e["art"]}"><h3><span class="nr">{["I","II","III","IV","V","VI","VII","VIII"][i]}.</span> '
            f'{e_(e["titel"])} <span class="art">{ART[e["art"]]}</span></h3>'
            f'<p>{e_(e["text"])}</p><ul class="wirk">{wirk}</ul></section>'
        )
    fest = ""
    if d.get("fest"):
        fest = f'<h2>Im Jahreskreis</h2><section class="fest"><h3>{e_(d["fest"]["name"])}</h3><p>{e_(d["fest"]["text"])}</p></section>'
    geruechte = ""
    if d.get("geruechte"):
        geruechte = ('<h2>Was man sich erzählt</h2><p class="hinweis">Gerüchte, wahr oder nicht. Die Schreibstube verbürgt sich für keines.</p><ul class="geruechte">'
                     + "".join(f'<li><span class="quelle">{e_(g["quelle"])}:</span> {e_(g["text"])}</li>' for g in d["geruechte"])
                     + "</ul>")
    ww = wirkungen_je_bereich(d)
    zeilen = "".join(
        f'<tr><td>{e_(b["name"])}</td><td class="pfe">{" ".join(ww[b["name"]]) or "–"}</td>'
        f'<td class="stufe">{"◆" * b["nachher"]}{"◇" * (5 - b["nachher"])} <small>{STUFEN[b["nachher"]]} {trend(b)}</small></td>'
        f'<td>{e_(b["lage"])}</td></tr>'
        for b in d["bereiche"]
    )
    k = d["kasse"]
    ent = ""
    for x in d["entscheidungen"]:
        if isinstance(x, str):
            ent += f"<li>{e_(x)}</li>"
            continue
        opts = "".join(
            f'<li><b>{"abcd"[i]}) {e_(o["label"])}</b>{" ✦" if i == x.get("empfehlung") else ""} – {e_(o["folge"])}</li>'
            for i, o in enumerate(x["optionen"])
        )
        ent += f'<li class="frage"><b>{e_(x["frage"])}</b><ol class="optionen">{opts}</ol></li>'
    
    aus = "".join(f"<li>{e_(x)}</li>" for x in d["ausblick"])
    schreiben = ""
    if alle_schreiben(d):
        schreiben = '<p class="beilage">Beigelegt: ' + " · ".join(f"Schreiben an {e_(sv['an'])}" for sv in alle_schreiben(d)) + "</p>"
    wappen = (HIER / "wappen.svg").read_text(encoding="utf-8")
    vorlage = (HIER / "vorlage_bericht.html").read_text(encoding="utf-8")
    ersatz = {
        "WAPPEN": wappen,
        "TITEL": e_(d["titel"]), "NR": str(d["nr"]), "MONAT": e_(d["monat"]), "JAHR": e_(d["jahr"]),
        "VERFASSER": e_(d["verfasser"]), "ANREDE": e_(d["anrede"]),
        "INITIAL": e_(d["einleitung"][0].upper()), "EINLEITUNG": e_(d["einleitung"][1:]),
        "EREIGNISSE": "".join(teile), "FEST": fest, "GERUECHTE": geruechte, "BEREICHE": zeilen,
        "KASSE": "".join(f"<tr><td>{e_(p)}</td><td>{e_(b)}</td></tr>" for p, b in k["zeilen"]),
        "RESERVE": e_(k["reserve"]),
        "ENTSCHEIDUNGEN": ent, "AUSBLICK": aus, "SCHLUSS": e_(d["schluss"]), "SCHREIBEN": schreiben,
    }
    for schluessel, wert in ersatz.items():
        vorlage = vorlage.replace("{{" + schluessel + "}}", wert)
    return vorlage


def als_pdf(html_datei, pdf_datei):
    """Druckt die HTML-Datei mit Chromium (Kommandozeile, ohne Kopf- und Fußzeilen) als PDF."""
    import os
    import subprocess

    chromium = os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")
    subprocess.run(
        [chromium, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=15000", f"--print-to-pdf={pdf_datei.resolve()}", html_datei.resolve().as_uri()],
        check=True, capture_output=True,
    )


def briefe_bauen(d):
    """Baut jedes beigelegte Schreiben als eigenes PDF mit der Briefvorlage in ../Schreiben/."""
    import subprocess

    schreiben_ordner = HIER.parent / "Schreiben"
    for sv in alle_schreiben(d):
        quelle = schreiben_ordner / f"{sv['datei']}.json"
        if not quelle.exists():
            print("FEHLT:", quelle, "(Brief-JSON zuerst anlegen)")
            continue
        subprocess.run([sys.executable, str(schreiben_ordner / "Vorlage" / "brief_bauen.py"), str(quelle)], check=True)
        print("Brief:", quelle.with_suffix(".pdf"))


if __name__ == "__main__":
    quelle = Path(sys.argv[1])
    daten = json.loads(quelle.read_text(encoding="utf-8"))
    quelle.with_suffix(".md").write_text(als_markdown(daten), encoding="utf-8")
    html_datei = quelle.with_suffix(".html")
    html_datei.write_text(als_html(daten), encoding="utf-8")
    als_pdf(html_datei, quelle.with_suffix(".pdf"))
    print("fertig:", quelle.with_suffix(".pdf"))
    briefe_bauen(daten)
