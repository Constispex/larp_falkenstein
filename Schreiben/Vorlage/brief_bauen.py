"""Baut aus einer Brief-JSON das Schreiben als Pergament-PDF (dazu .html und .md).

Aufruf:  python3 Schreiben/Vorlage/brief_bauen.py Schreiben/2026-10-28_Lage_am_Gut_Travia_1053.json
Das PDF braucht Chromium (in der Cloud-Umgebung unter /opt/pw-browsers/chromium; sonst Umgebungsvariable CHROMIUM setzen).

Felder der JSON (Pflicht: empfaenger, ueberschrift, absaetze, datum):
  empfaenger    Schlüssel aus EMPFAENGER (vilmos, elzwalde, markwacht, kirschgeu)
  ueberschrift  rote Überschrift statt Betreffzeile, z. B. "Von der Lage am Gut Falkenstein im Monat der Travia"
  absaetze      Liste der Absätze; der letzte ist meist der Segenswunsch
  datum         z. B. "im Monat der Travia des Jahres 1053 nach Bosparans Fall"
  optional: eroeffnung, anrede, status, gruss, unterschrift, titel, ort, anlass, papier (Zahl: anderes Pergament)

Jedes Schreiben bekommt ein eigenes Pergament (Flecken, Kratzer, Farbton), abgeleitet aus dem Dateinamen.
Mit "papier": <Zahl> lässt sich ein anderes Blatt würfeln.
"""
import hashlib
import html
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from string import Template

HIER = Path(__file__).parent
VARION = "Varion von Falkenstein, Ritter zu Falkenstein an der Westmark der Markgrafschaft Freiberg"

# Anrede nach Rang, siehe CLAUDE.md "Schreiben an Mitspieler".
EMPFAENGER = {
    "vilmos": {
        "an": "Seiner Erlaucht Vilmos von Freiberg, Markgrafen der Markgrafschaft Freiberg, seinem gnädigen Lehnsherrn",
        "gruss_eroeffnung": "Gruß und treuen Dienst",
        "anrede": "Euer Erlaucht,",
        "gruss": "In Treue ergeben",
    },
    "elzwalde": {
        "an": "dem edlen Herrn Junker von Elzwalde, seinem Nachbarn jenseits der Großen Weststraße",
        "gruss_eroeffnung": "seinen Gruß zuvor",
        "anrede": "Edler Herr,",
        "gruss": "In nachbarlicher Achtung",
    },
    "markwacht": {
        "an": "dem wohlgeborenen Herrn Ritter von Markwacht",
        "gruss_eroeffnung": "seinen Gruß zuvor",
        "anrede": "Euer Wohlgeboren,",
        "gruss": "Mit ritterlichem Gruß",
    },
    "kirschgeu": {
        "an": "Seiner Hochgeboren Baron Kirschgeu",
        "gruss_eroeffnung": "Gruß und ergebenen Dienst",
        "anrede": "Euer Hochgeboren,",
        "gruss": "In Ergebenheit",
    },
}


def felder(d):
    e = EMPFAENGER.get(d["empfaenger"], {})
    return {
        "eroeffnung": d.get("eroeffnung") or f"{VARION}, entbietet {e['an']}, {e['gruss_eroeffnung']}.",
        "anrede": d.get("anrede") or e["anrede"],
        "gruss": d.get("gruss") or e["gruss"],
        "unterschrift": d.get("unterschrift", "Varion von Falkenstein"),
        "titel": d.get("titel", "Ritter zu Falkenstein"),
        "ort": d.get("ort", "Gegeben auf Burg Falkenstein am Kaltentann"),
    }


def pergament(saat, seite=0):
    """Zeichnet ein Pergamentblatt mit Zierrand als SVG; die Saat bestimmt Flecken, Kratzer und Farbton."""
    r = random.Random(saat * 31 + seite)
    s = [r.randint(1, 9999) for _ in range(5)]
    ton = r.uniform(-0.06, 0.06)  # leichter Farbton-Schub: mehr Grün oder mehr Rot

    def farbe(rgb):
        rr, gg, bb = rgb
        return "#%02X%02X%02X" % (max(0, min(255, int(rr * (1 - ton)))), max(0, min(255, int(gg * (1 + ton / 2)))), bb)

    kratzer = "".join(
        f'<path d="M{x} {y} L{x + r.randint(-60, 90)} {y + r.randint(40, 200)}"></path>'
        for x, y in ((r.randint(90, 700), r.randint(90, 1030)) for _ in range(r.randint(4, 8)))
    )
    flecken = "".join(
        f'<ellipse cx="{r.randint(80, 714)}" cy="{r.randint(80, 1043)}" rx="{r.randint(25, 80)}" ry="{r.randint(20, 60)}" '
        f'fill="#7A4E1E" filter="url(#weich)" fill-opacity="{r.uniform(0.10, 0.22):.2f}"></ellipse>'
        for _ in range(r.randint(2, 5))
    )
    falten = "".join(
        f'<path d="M60 {y} C200 {y + r.randint(-6, 6)} 420 {y + r.randint(-8, 8)} 734 {y + r.randint(-8, 8)}" '
        f'fill="none" stroke="#4E3410" stroke-width="1.2" stroke-opacity="0.22"></path>'
        for y in (374 + r.randint(-6, 6), 748 + r.randint(-6, 6))
    )
    ranke_h = ('<path d="M0 17 C10 4 20 4 20 17 C20 30 30 30 40 17" fill="none" stroke="#7E3420" stroke-width="1.6"></path>'
               '<circle cx="10" cy="9" r="2.2" fill="#7E3420"></circle><circle cx="30" cy="25" r="2.2" fill="#7E3420"></circle>')
    ranke_v = ('<path d="M17 0 C4 10 4 20 17 20 C30 20 30 30 17 40" fill="none" stroke="#7E3420" stroke-width="1.6"></path>'
               '<circle cx="9" cy="10" r="2.2" fill="#7E3420"></circle><circle cx="25" cy="30" r="2.2" fill="#7E3420"></circle>')
    svg = f'''<svg viewBox="0 0 794 1123" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<defs>
<radialGradient id="grund" cx="{r.uniform(44, 56):.0f}%" cy="{r.uniform(40, 52):.0f}%" r="75%"><stop offset="0" stop-color="{farbe((234, 219, 176))}"></stop><stop offset="0.5" stop-color="{farbe((216, 195, 138))}"></stop><stop offset="0.8" stop-color="{farbe((181, 152, 88))}"></stop><stop offset="1" stop-color="{farbe((90, 66, 30))}"></stop></radialGradient>
<filter id="wolken" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.004" numOctaves="3" seed="{s[0]}"></feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.34  0 0 0 0 0.12  0 0 0 1.5 -0.55"></feColorMatrix></filter>
<filter id="flecken" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="5" seed="{s[1]}"></feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 0.62  0 0 0 0 0.40  0 0 0 0 0.14  0 0 0 2.2 -0.78"></feColorMatrix></filter>
<filter id="flecken2" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.025" numOctaves="4" seed="{s[2]}"></feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 0.42  0 0 0 0 0.28  0 0 0 0 0.10  0 0 0 2.4 -1.0"></feColorMatrix></filter>
<filter id="poren" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="3" seed="{s[3]}"></feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 0.50  0 0 0 0 0.36  0 0 0 0 0.14  0 0 0 1.0 -0.42"></feColorMatrix></filter>
<filter id="koernung" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{s[4]}"></feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.26  0 0 0 0 0.10  0 0 0 0.45 -0.1"></feColorMatrix></filter>
<filter id="weich" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="24"></feGaussianBlur></filter>
<pattern id="rankeO" x="22" y="22" width="40" height="34" patternUnits="userSpaceOnUse">{ranke_h}</pattern>
<pattern id="rankeU" x="22" y="1067" width="40" height="34" patternUnits="userSpaceOnUse">{ranke_h}</pattern>
<pattern id="rankeL" x="22" y="22" width="34" height="40" patternUnits="userSpaceOnUse">{ranke_v}</pattern>
<pattern id="rankeR" x="738" y="22" width="34" height="40" patternUnits="userSpaceOnUse">{ranke_v}</pattern>
<g id="rosette"><circle r="21" fill="#C9AE72" stroke="#6B4A22" stroke-width="1.2"></circle>
<circle cx="0" cy="-11" r="6" fill="#8E3A22"></circle><circle cx="0" cy="11" r="6" fill="#8E3A22"></circle><circle cx="-11" cy="0" r="6" fill="#8E3A22"></circle><circle cx="11" cy="0" r="6" fill="#8E3A22"></circle>
<circle cx="-7.8" cy="-7.8" r="5" fill="#A3492C"></circle><circle cx="7.8" cy="-7.8" r="5" fill="#A3492C"></circle><circle cx="-7.8" cy="7.8" r="5" fill="#A3492C"></circle><circle cx="7.8" cy="7.8" r="5" fill="#A3492C"></circle>
<circle r="6.5" fill="#6E2A18"></circle><circle r="2.6" fill="#D9B86E"></circle></g>
</defs>
<rect width="794" height="1123" fill="url(#grund)"></rect>
<rect width="794" height="1123" filter="url(#wolken)"></rect>
<rect width="794" height="1123" filter="url(#flecken)"></rect>
<rect width="794" height="1123" filter="url(#flecken2)"></rect>
<rect width="794" height="1123" filter="url(#poren)"></rect>
<rect width="794" height="1123" filter="url(#koernung)"></rect>
{flecken}
<rect width="794" height="1123" fill="none" stroke="#3E2A10" filter="url(#weich)" stroke-width="80" stroke-opacity="0.65"></rect>
<g fill="none" stroke="#FFF3D2" stroke-opacity="0.35" stroke-width="1">{kratzer}</g>
{falten}
<g opacity="0.92">
<rect x="22" y="22" width="750" height="34" fill="url(#rankeO)"></rect>
<rect x="22" y="1067" width="750" height="34" fill="url(#rankeU)"></rect>
<rect x="22" y="22" width="34" height="1079" fill="url(#rankeL)"></rect>
<rect x="738" y="22" width="34" height="1079" fill="url(#rankeR)"></rect>
<rect x="22" y="22" width="750" height="1079" fill="none" stroke="#6B4A22" stroke-width="1.6"></rect>
<rect x="56" y="56" width="682" height="1011" fill="none" stroke="#6B4A22" stroke-width="1.2"></rect>
<rect x="64" y="64" width="666" height="995" fill="none" stroke="#7E3420" stroke-width="0.8"></rect>
<use href="#rosette" transform="translate(39 39)"></use><use href="#rosette" transform="translate(755 39)"></use>
<use href="#rosette" transform="translate(39 1084)"></use><use href="#rosette" transform="translate(755 1084)"></use>
<use href="#rosette" transform="translate(397 39) scale(0.8)"></use><use href="#rosette" transform="translate(397 1084) scale(0.8)"></use>
<use href="#rosette" transform="translate(39 561) scale(0.8)"></use><use href="#rosette" transform="translate(755 561) scale(0.8)"></use>
</g>
</svg>'''
    # Jede Seite bekommt eigene ids, damit sich die Blätter nicht gegenseitig überschreiben.
    for name in ("grund", "wolken", "flecken2", "flecken", "poren", "koernung", "weich", "rankeO", "rankeU", "rankeL", "rankeR", "rosette"):
        svg = svg.replace(f'id="{name}"', f'id="s{seite}{name}"').replace(f'url(#{name})', f'url(#s{seite}{name})').replace(f'href="#{name}"', f'href="#s{seite}{name}"')
    return svg


def als_bild(svg):
    """Rechnet das Pergament einmal als JPEG (2-fache Auflösung) aus; als Vektorfilter wäre das PDF über 25 MB groß."""
    import base64
    import tempfile

    from PIL import Image

    chromium = os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")
    with tempfile.TemporaryDirectory() as tmp:
        seite = Path(tmp) / "blatt.html"
        seite.write_text(f'<html><body style="margin:0">{svg.replace("<svg ", '<svg width="794" height="1123" ', 1)}</body></html>', encoding="utf-8")
        png = Path(tmp) / "blatt.png"
        subprocess.run(
            [chromium, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--window-size=794,1123",
             "--force-device-scale-factor=2", f"--screenshot={png}", seite.as_uri()],
            check=True, capture_output=True,
        )
        jpg = Path(tmp) / "blatt.jpg"
        Image.open(png).convert("RGB").save(jpg, quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()


def als_html(d, saat, html_datei, seiten=1):
    f = felder(d)
    e = html.escape
    eroeffnung = f["eroeffnung"]
    absaetze = "\n".join(f'<p><span class="pilcrow">¶ </span>{e(a)}</p>' for a in d["absaetze"])
    inhalt = f'''<p><span class="initiale">{e(eroeffnung[0])}</span>{e(eroeffnung[1:])}</p>
<div class="ueberschrift">{e(d["ueberschrift"])}</div>
<p>{e(f["anrede"])}</p>
{absaetze}
<div class="schluss">
<p class="datum">{e(f["ort"])}, {e(d["datum"])}.</p>
<div class="unterschrift"><span style="font-style: italic;">{e(f["gruss"])}</span><span class="name">{e(f["unterschrift"])}</span><span class="titel">{e(f["titel"])}</span></div>
<div class="siegel-block"><div class="schnuere"><span></span><span></span></div><div class="siegel"><div>{e(f["unterschrift"][0])}</div></div></div>
</div>'''
    blaetter = "".join(
        f'<div class="pergament" style="top: {297 * i}mm"><img src="{als_bild(pergament(saat, i))}" alt=""></div>' for i in range(seiten)
    )
    schriften = Path(os.path.relpath(HIER / "schriften", html_datei.parent)).as_posix()
    vorlage = Template((HIER / "brief_vorlage.html").read_text(encoding="utf-8"))
    return vorlage.substitute(titel=e(d["ueberschrift"]), schriften=schriften, pergament=blaetter, inhalt=inhalt, hoehe=f"{297 * seiten}mm")


def als_markdown(d):
    f = felder(d)
    z = [f"# {d['ueberschrift']}", ""]
    if d.get("status"):
        z += [f"⚑ {d['status']}", ""]
    if d.get("anlass"):
        z += [f"*Anlass:* {d['anlass']}", ""]
    z += [f["eroeffnung"], "", f["anrede"], ""] + [a + "\n" for a in d["absaetze"]]
    z += [f"*{f['ort']}, {d['datum']}.*", "", f["gruss"], "", f"{f['unterschrift']}, {f['titel']}", ""]
    return "\n".join(z)


def als_pdf(html_datei, pdf_datei):
    """Druckt die HTML-Datei mit Chromium (ohne Kopf- und Fußzeilen) als PDF."""
    chromium = os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")
    subprocess.run(
        [chromium, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=15000", f"--print-to-pdf={pdf_datei.resolve()}", html_datei.resolve().as_uri()],
        check=True, capture_output=True,
    )


if __name__ == "__main__":
    quelle = Path(sys.argv[1])
    daten = json.loads(quelle.read_text(encoding="utf-8"))
    saat = int(hashlib.sha1(quelle.stem.encode()).hexdigest()[:8], 16) + int(daten.get("papier", 0))
    quelle.with_suffix(".md").write_text(als_markdown(daten), encoding="utf-8")
    html_datei = quelle.with_suffix(".html")
    pdf_datei = quelle.with_suffix(".pdf")
    # Erst mit einem Blatt drucken, dann so viele Pergamentblätter hinterlegen, wie der Text Seiten braucht.
    seiten = 1
    while True:
        html_datei.write_text(als_html(daten, saat, html_datei, seiten), encoding="utf-8")
        als_pdf(html_datei, pdf_datei)
        gedruckt = pdf_datei.read_bytes().count(b"/Type /Page") - pdf_datei.read_bytes().count(b"/Type /Pages")
        if gedruckt <= seiten or seiten >= 10:
            break
        seiten = gedruckt
    print(quelle.with_suffix(".pdf"))
