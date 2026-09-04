import csv
import io
import re

from models import Page


class HTMLGenerator:
    """Generiert HTML Code aus dem Model für Bootstrap 3 oder Bootstrap 5."""

    BOOTSTRAP5_CSS = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">'
    BOOTSTRAP5_JS = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmxc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>'

    BOOTSTRAP3_CSS = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">'
    BOOTSTRAP3_JS = '<script src="https://code.jquery.com/jquery-1.12.4.min.js" integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=" crossorigin="anonymous"></script>\n    <script src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>'

    @staticmethod
    def generate_html(page: Page, bootstrap_version: str = "5") -> str:
        """
        Nimmt eine Page-Instanz entgegen und verpackt die Inhalte
        in ein valides HTML5 Dokument mit Bootstrap 3 oder 5.
        """
        page_content = page.render(version=bootstrap_version)

        if bootstrap_version == "3":
            css_link = HTMLGenerator.BOOTSTRAP3_CSS
            js_script = HTMLGenerator.BOOTSTRAP3_JS
        else:
            css_link = HTMLGenerator.BOOTSTRAP5_CSS
            js_script = HTMLGenerator.BOOTSTRAP5_JS

        import html as py_html

        title_escaped = py_html.escape(page.title)

        html_template = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped}</title>
    {css_link}
    <style>

        /* Zusätzliche Styles für besseres visuelles Feedback im Editor (optional) */
        body {{
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>

    <!-- Generierter Content Start -->
    {page_content}
    <!-- Generierter Content Ende -->

    {js_script}
</body>
</html>
"""
        return html_template


class HTMLConverter:
    """Konvertiert bestehenden Bootstrap 3 HTML Code in Bootstrap 5 Code."""

    _RE_BS3_CSS = re.compile(r'<link[^>]*href="[^"]*bootstrap[^"]*3\.[^"]*"[^>]*>', re.IGNORECASE)
    _RE_BS3_JS = re.compile(r'<script[^>]*src="[^"]*bootstrap[^"]*3\.[^"]*"[^>]*></script>', re.IGNORECASE)
    _RE_JQUERY = re.compile(r'<script[^>]*src="[^"]*jquery[^"]*"[^>]*></script>\s*', re.IGNORECASE)

    _RE_REPLACEMENTS = [
        (re.compile(r"\bimg-responsive\b"), "img-fluid"),
        (re.compile(r"\bform-group\b"), "mb-3"),
        (re.compile(r"\bbtn-default\b"), "btn-secondary"),
        (re.compile(r"\bwell\b"), "card card-body"),
        (re.compile(r"\bpanel panel-default\b"), "card"),
        (re.compile(r"\bpanel-heading\b"), "card-header"),
        (re.compile(r"\bpanel-body\b"), "card-body"),
        (re.compile(r"\bpanel-footer\b"), "card-footer"),
        (re.compile(r"\bhelp-block\b"), "form-text"),
        (re.compile(r"\bcontrol-label\b"), "form-label"),
        (re.compile(r"\binput-lg\b"), "form-control-lg"),
        (re.compile(r"\binput-sm\b"), "form-control-sm"),
        (re.compile(r"\bpull-right\b"), "float-end"),
        (re.compile(r"\bpull-left\b"), "float-start"),
        (re.compile(r"\bcenter-block\b"), "mx-auto d-block"),
        (re.compile(r"\bdata-toggle\b="), "data-bs-toggle="),
        (re.compile(r"\bdata-target\b="), "data-bs-target="),
        (re.compile(r"\bdata-dismiss\b="), "data-bs-dismiss="),
        (re.compile(r"\bdata-slide\b="), "data-bs-slide="),
        (re.compile(r"\bdata-ride\b="), "data-bs-ride="),
    ]

    _TAG_PATTERNS = {
        tag: re.compile(rf"<({tag}\b[^>/]*)(?<!/)>", re.IGNORECASE) for tag in ["img", "input", "br", "hr"]
    }

    @staticmethod
    def convert_bs3_to_bs5(html_code: str) -> str:
        code = html_code

        # 1. CDN Links austauschen
        code = HTMLConverter._RE_BS3_CSS.sub(HTMLGenerator.BOOTSTRAP5_CSS, code)
        code = HTMLConverter._RE_BS3_JS.sub(HTMLGenerator.BOOTSTRAP5_JS, code)
        code = HTMLConverter._RE_JQUERY.sub("", code)

        # 2. Ersetzungen durchführen
        for pattern, replacement in HTMLConverter._RE_REPLACEMENTS:
            code = pattern.sub(replacement, code)

        # 3. Automatische Syntax-Reparatur
        code, _repairs = HTMLConverter.fix_html_syntax(code)

        return code

    @staticmethod
    def fix_html_syntax(html_code: str) -> tuple[str, list[str]]:
        """Prüft und repariert typische HTML-Syntaxfehler."""
        repairs = []
        code = html_code

        # 0. Ungeschlossene Anführungszeichen in Attributen reparieren (z. B. class="img...>)
        def fix_unclosed_quotes(match):
            tag_content = match.group(0)
            quotes_count = tag_content.count('"')
            if quotes_count % 2 != 0:
                if tag_content.endswith("/>"):
                    return tag_content[:-2] + '" />'
                elif tag_content.endswith(">"):
                    return tag_content[:-1] + '">'
            return tag_content

        fixed_code = re.sub(r"<[^>]+>", fix_unclosed_quotes, code)
        if fixed_code != code:
            code = fixed_code
            repairs.append('Fehlendes schließendes Anführungszeichen `"` in Attribut ergänzt.')

        # Ungeschlossene selbstschließende Tags reparieren (z. B. <img ...> -> <img ... />)
        for tag, pattern in HTMLConverter._TAG_PATTERNS.items():
            if pattern.search(code):
                code = pattern.sub(r"<\1 />", code)
                repairs.append(f"Selbstschließendes Tag `<{tag}>` mit `/>` ergänzt.")

        # Prüfung auf ungeschlossene Tags (<div ...> ohne </div>)
        tags_to_check = [
            "div",
            "p",
            "span",
            "a",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "button",
            "form",
        ]
        for tag in tags_to_check:
            open_count = len(re.findall(rf"<{tag}\b[^>]*>", code, re.IGNORECASE))
            close_count = len(re.findall(rf"</{tag}\s*>", code, re.IGNORECASE))

            diff = open_count - close_count
            if diff > 0:
                code += "\n" + (f"</{tag}>\n" * diff)
                repairs.append(f"{diff}x fehlendes `</{tag}>` am Ende ergänzt.")

        return code, repairs

    @staticmethod
    def parse_html_table(html_code: str) -> tuple[list[str], list[list[str]]]:
        """Extrahiert Spaltenköpfe und Datenzeilen aus beliebigem <table> HTML-Code."""
        headers = []
        rows = []

        # 1. <th> Extraktion
        th_matches = re.findall(r"<th[^>]*>(.*?)</th>", html_code, re.DOTALL | re.IGNORECASE)
        for th in th_matches:
            clean_text = re.sub(r"<[^>]+>", "", th).strip()
            headers.append(clean_text)

        # 2. <tr> Extraktion für <td> Zellen
        tr_matches = re.findall(r"<tr[^>]*>(.*?)</tr>", html_code, re.DOTALL | re.IGNORECASE)
        for tr in tr_matches:
            td_matches = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE)
            if td_matches:
                row_cells = [re.sub(r"<[^>]+>", "", td).strip() for td in td_matches]
                rows.append(row_cells)
        return headers, rows

    @staticmethod
    def format_table_line(items: list[str], delimiter: str = " | ") -> str:
        """Konvertiert eine Liste von Zellwerten in einen lesbaren String mit Pipe-Trennzeichen."""
        return delimiter.join(items)

    @staticmethod
    def parse_table_line(line: str) -> list[str]:
        """
        Parst eine Tabellenzeile.
        Verwendet bevorzugt '|', ';', oder Tab, falls vorhanden.
        Fällt sonst auf CSV-Parsing (Komma mit Quoting) zurück.
        """
        raw = line.strip()
        if not raw:
            return []
        if "|" in raw:
            return [cell.strip() for cell in raw.split("|")]
        if ";" in raw:
            return [cell.strip() for cell in raw.split(";")]
        if "\t" in raw:
            return [cell.strip() for cell in raw.split("\t")]
        return HTMLConverter.parse_csv_line(raw)

    @staticmethod
    def format_csv_line(items: list[str]) -> str:
        """Konvertiert eine Liste von Zellwerten in eine CSV-Zeile mit korrektem Quoting für Kommas."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(items)
        return output.getvalue()

    @staticmethod
    def parse_csv_line(line: str) -> list[str]:
        """Parst eine CSV-Zeile zu Zellwerten unter Berücksichtigung von Anführungszeichen."""
        if not line.strip():
            return []
        reader = csv.reader([line], skipinitialspace=True)
        for row in reader:
            return [cell.strip() for cell in row]
        return []
