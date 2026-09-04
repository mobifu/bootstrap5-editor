import html
import uuid
from typing import Any
from urllib.parse import urlparse


class Element:
    """Basisklasse für alle UI-Elemente im Generator."""

    def __init__(
        self,
        element_id: str | None = None,
        margin_top: str = "none",
        margin_bottom: str = "none",
        padding_top: str = "none",
        padding_bottom: str = "none",
    ):
        self.id = element_id if element_id else str(uuid.uuid4())
        self.margin_top = margin_top  # "none", "0", "1", "2", "3", "4", "5"
        self.margin_bottom = margin_bottom
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom

    def get_spacing_classes(self, version: str = "5") -> str:
        """Erzeugt Bootstrap Spacing Utility Klassen (z.B. mt-3 mb-2 pt-1 pb-4)."""
        classes = []
        if self.margin_top != "none":
            classes.append(f"mt-{self.margin_top}")
        if self.margin_bottom != "none":
            classes.append(f"mb-{self.margin_bottom}")
        if self.padding_top != "none":
            classes.append(f"pt-{self.padding_top}")
        if self.padding_bottom != "none":
            classes.append(f"pb-{self.padding_bottom}")
        return " ".join(classes)

    def apply_spacing_to_html(self, html_code: str, version: str = "5") -> str:
        """Verpackt das Element in ein Wrapper-div, falls Spacings gesetzt sind."""
        spacing_classes = self.get_spacing_classes(version=version)
        if not spacing_classes:
            return html_code
        return f'<div class="{spacing_classes}">\n{html_code}\n</div>'

    def base_to_dict(self) -> dict[str, Any]:
        return {
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "padding_top": self.padding_top,
            "padding_bottom": self.padding_bottom,
        }

    def render(self, version: str = "5") -> str:
        raise NotImplementedError("Subklassen müssen render() implementieren.")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": "Element", **self.base_to_dict()}

    @classmethod
    def extract_spacing_kwargs(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "element_id": data.get("id"),
            "margin_top": data.get("margin_top", "none"),
            "margin_bottom": data.get("margin_bottom", "none"),
            "padding_top": data.get("padding_top", "none"),
            "padding_bottom": data.get("padding_bottom", "none"),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Element":
        # Factory Methode
        element_type = data.get("type")
        if element_type == "TextBlock":
            return TextBlock.from_dict(data)
        elif element_type == "ImageBlock":
            return ImageBlock.from_dict(data)
        elif element_type == "ButtonBlock":
            return ButtonBlock.from_dict(data)
        elif element_type == "AlertBlock":
            return AlertBlock.from_dict(data)
        elif element_type == "HtmlBlock":
            return HtmlBlock.from_dict(data)
        elif element_type == "TableBlock":
            return TableBlock.from_dict(data)
        elif element_type == "CardBlock":
            return CardBlock.from_dict(data)
        elif element_type == "BadgeBlock":
            return BadgeBlock.from_dict(data)
        elif element_type == "AccordionBlock":
            return AccordionBlock.from_dict(data)
        elif element_type == "FormInputBlock":
            return FormInputBlock.from_dict(data)
        elif element_type == "NavbarBlock":
            return NavbarBlock.from_dict(data)
        elif element_type == "ListGroupBlock":
            return ListGroupBlock.from_dict(data)
        elif element_type == "Column":
            return Column.from_dict(data)
        elif element_type == "Row":
            return Row.from_dict(data)
        elif element_type == "Page":
            return Page.from_dict(data)
        raise ValueError(f"Unbekannter Element-Typ: {element_type}")


class TextBlock(Element):
    """Repräsentiert einen einfachen Text-Block (P oder H1)."""

    def __init__(self, text: str, tag: str = "p", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.tag = tag

    def render(self, version: str = "5") -> str:
        escaped_text = html.escape(self.text)
        return f"<{self.tag}>{escaped_text}</{self.tag}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "TextBlock",
            "text": self.text,
            "tag": self.tag,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TextBlock":
        return cls(
            text=data.get("text", ""),
            tag=data.get("tag", "p"),
            **cls.extract_spacing_kwargs(data),
        )


def _sanitize_css_class(name: str, fallback: str = "primary") -> str:
    """Verhindert Class/Attribute Injection durch Begrenzung auf alfanumerische Zeichen und Bindestriche."""
    if not name or not isinstance(name, str):
        return fallback
    clean = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
    return clean if clean else fallback


def _sanitize_url(url: str, fallback: str = "#", allow_image_data: bool = False) -> str:
    """
    Entfernt gefährliche URL-Schemata (wie javascript:, vbscript:, data:text/html)
    und erlaubt sichere Web-Links, relative Pfade, Anker sowie Mailto/Tel.
    """
    if not url or not isinstance(url, str):
        return fallback
    clean = url.strip()
    if not clean:
        return fallback

    # Sichere relative Links, Anker und Standard-Protokolle
    if clean.startswith(("#", "/", "./", "../", "mailto:", "tel:")):
        return html.escape(clean, quote=True)

    if allow_image_data and clean.startswith("data:image/"):
        return html.escape(clean, quote=True)

    try:
        parsed = urlparse(clean)
        # Relative Dateipfade ohne Schema (z. B. "bild.png" oder "assets/logo.jpg")
        if not parsed.scheme:
            return html.escape(clean, quote=True)
        if parsed.scheme.lower() in ("http", "https"):
            return html.escape(clean, quote=True)
    except ValueError:
        return fallback

    return fallback


class ImageBlock(Element):
    """Repräsentiert ein Bild (img)."""

    def __init__(self, url: str, alt: str = "Bild", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.alt = alt

    def render(self, version: str = "5") -> str:
        img_class = "img-responsive" if version == "3" else "img-fluid"
        safe_url = _sanitize_url(
            self.url,
            fallback="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
            allow_image_data=True,
        )
        escaped_alt = html.escape(self.alt, quote=True)
        return f'<img src="{safe_url}" alt="{escaped_alt}" class="{img_class}">'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "ImageBlock",
            "url": self.url,
            "alt": self.alt,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImageBlock":
        return cls(
            url=data.get("url", ""),
            alt=data.get("alt", "Bild"),
            **cls.extract_spacing_kwargs(data),
        )


class ButtonBlock(Element):
    """Repräsentiert einen Bootstrap-Button / Link-Button."""

    def __init__(self, text: str, url: str = "#", style: str = "primary", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url
        self.style = style

    def render(self, version: str = "5") -> str:
        escaped_text = html.escape(self.text)
        safe_url = _sanitize_url(self.url, fallback="#")
        safe_style = _sanitize_css_class(self.style, "primary")
        return f'<a href="{safe_url}" class="btn btn-{safe_style}" role="button">{escaped_text}</a>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "ButtonBlock",
            "text": self.text,
            "url": self.url,
            "style": self.style,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ButtonBlock":
        return cls(
            text=data.get("text", "Button"),
            url=data.get("url", "#"),
            style=data.get("style", "primary"),
            **cls.extract_spacing_kwargs(data),
        )


class AlertBlock(Element):
    """Repräsentiert eine Bootstrap-Hinweisbox (Alert)."""

    def __init__(self, text: str, style: str = "info", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.style = style

    def render(self, version: str = "5") -> str:
        escaped_text = html.escape(self.text)
        safe_style = _sanitize_css_class(self.style, "info")
        return f'<div class="alert alert-{safe_style}" role="alert">{escaped_text}</div>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "AlertBlock",
            "text": self.text,
            "style": self.style,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlertBlock":
        return cls(
            text=data.get("text", ""),
            style=data.get("style", "info"),
            **cls.extract_spacing_kwargs(data),
        )


class HtmlBlock(Element):
    """Repräsentiert einen benutzerdefinierten HTML-Code-Block."""

    def __init__(self, code: str, **kwargs):
        super().__init__(**kwargs)
        self.code = code

    def render(self, version: str = "5") -> str:
        return self.code

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "HtmlBlock",
            "code": self.code,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HtmlBlock":
        return cls(code=data.get("code", ""), **cls.extract_spacing_kwargs(data))


class TableBlock(Element):
    """Repräsentiert eine Bootstrap Tabelle."""

    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[str]] | None = None,
        striped: bool = True,
        bordered: bool = False,
        hover: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.headers = headers if headers is not None else ["Spalte 1", "Spalte 2", "Spalte 3"]
        self.rows = (
            rows
            if rows is not None
            else [
                ["Zeile 1 A", "Zeile 1 B", "Zeile 1 C"],
                ["Zeile 2 A", "Zeile 2 B", "Zeile 2 C"],
            ]
        )
        self.striped = striped
        self.bordered = bordered
        self.hover = hover

    def render(self, version: str = "5") -> str:
        classes = ["table"]
        if self.striped:
            classes.append("table-striped")
        if self.bordered:
            classes.append("table-bordered")
        if self.hover:
            classes.append("table-hover")

        class_str = " ".join(classes)
        th_html = "".join([f"<th>{html.escape(h)}</th>" for h in self.headers])

        tr_html_list = []
        for r in self.rows:
            tds = "".join([f"<td>{html.escape(cell)}</td>" for cell in r])
            tr_html_list.append(f"<tr>{tds}</tr>")

        tbody_html = "\n".join(tr_html_list)
        return f'<table class="{class_str}">\n<thead>\n<tr>{th_html}</tr>\n</thead>\n<tbody>\n{tbody_html}\n</tbody>\n</table>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "TableBlock",
            "headers": self.headers,
            "rows": self.rows,
            "striped": self.striped,
            "bordered": self.bordered,
            "hover": self.hover,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TableBlock":
        return cls(
            headers=data.get("headers"),
            rows=data.get("rows"),
            striped=data.get("striped", True),
            bordered=data.get("bordered", False),
            hover=data.get("hover", True),
            **cls.extract_spacing_kwargs(data),
        )


class CardBlock(Element):
    """Repräsentiert eine Card (BS5) / Panel (BS3)."""

    def __init__(
        self,
        title: str = "Titel",
        content: str = "Inhalt der Karte...",
        style: str = "default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.style = style

    def render(self, version: str = "5") -> str:
        escaped_title = html.escape(self.title)
        escaped_content = html.escape(self.content)
        if version == "3":
            panel_style = "default" if self.style in ["default", "light"] else self.style
            return (
                f'<div class="panel panel-{panel_style}">\n'
                f'  <div class="panel-heading"><h3 class="panel-title">{escaped_title}</h3></div>\n'
                f'  <div class="panel-body">{escaped_content}</div>\n'
                f"</div>"
            )
        else:
            bg_class = f" text-bg-{self.style}" if self.style not in ["default", "light"] else ""
            return (
                f'<div class="card{bg_class} mb-3">\n'
                f'  <div class="card-header">{escaped_title}</div>\n'
                f'  <div class="card-body">\n'
                f'    <p class="card-text">{escaped_content}</p>\n'
                f"  </div>\n"
                f"</div>"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "CardBlock",
            "title": self.title,
            "content": self.content,
            "style": self.style,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CardBlock":
        return cls(
            title=data.get("title", "Titel"),
            content=data.get("content", ""),
            style=data.get("style", "default"),
            **cls.extract_spacing_kwargs(data),
        )


class BadgeBlock(Element):
    """Repräsentiert ein Badge (BS5) / Label (BS3)."""

    def __init__(self, text: str = "Badge", style: str = "primary", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.style = style

    def render(self, version: str = "5") -> str:
        escaped_text = html.escape(self.text)
        if version == "3":
            lbl_style = "default" if self.style == "secondary" else self.style
            return f'<span class="label label-{lbl_style}">{escaped_text}</span>'
        else:
            bg_style = "secondary" if self.style == "default" else self.style
            return f'<span class="badge bg-{bg_style}">{escaped_text}</span>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "BadgeBlock",
            "text": self.text,
            "style": self.style,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BadgeBlock":
        return cls(
            text=data.get("text", "Badge"),
            style=data.get("style", "primary"),
            **cls.extract_spacing_kwargs(data),
        )


class AccordionBlock(Element):
    """Repräsentiert ein Akkordeon / Collapse Element."""

    def __init__(self, items: list[dict[str, str]] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.items = (
            items
            if items is not None
            else [
                {"title": "Abschnitt 1", "content": "Inhalt von Abschnitt 1..."},
                {"title": "Abschnitt 2", "content": "Inhalt von Abschnitt 2..."},
            ]
        )

    def render(self, version: str = "5") -> str:
        clean_id = self.id.replace("-", "")
        acc_id = f"acc-{clean_id}"
        if version == "3":
            panels = []
            for idx, item in enumerate(self.items):
                item_id = f"collapse-{clean_id}-{idx}"
                escaped_title = html.escape(item.get("title", ""))
                escaped_content = html.escape(item.get("content", ""))
                in_class = " in" if idx == 0 else ""
                panels.append(
                    f'<div class="panel panel-default">\n'
                    f'  <div class="panel-heading">\n'
                    f'    <h4 class="panel-title"><a data-toggle="collapse" data-parent="#{acc_id}" href="#{item_id}">{escaped_title}</a></h4>\n'
                    f"  </div>\n"
                    f'  <div id="{item_id}" class="panel-collapse collapse{in_class}">\n'
                    f'    <div class="panel-body">{escaped_content}</div>\n'
                    f"  </div>\n"
                    f"</div>"
                )
            return f'<div class="panel-group" id="{acc_id}">\n' + "\n".join(panels) + "\n</div>"
        else:
            items_html = []
            for idx, item in enumerate(self.items):
                item_id = f"c{clean_id}i{idx}"
                escaped_title = html.escape(item.get("title", ""))
                escaped_content = html.escape(item.get("content", ""))
                collapsed_class = "" if idx == 0 else " collapsed"
                show_class = " show" if idx == 0 else ""
                aria_expanded = "true" if idx == 0 else "false"

                items_html.append(
                    f'<div class="accordion-item">\n'
                    f'  <h2 class="accordion-header" id="heading-{item_id}">\n'
                    f'    <button class="accordion-button{collapsed_class}" type="button" data-bs-toggle="collapse" data-bs-target="#{item_id}" aria-expanded="{aria_expanded}" aria-controls="{item_id}">\n'
                    f"      {escaped_title}\n"
                    f"    </button>\n"
                    f"  </h2>\n"
                    f'  <div id="{item_id}" class="accordion-collapse collapse{show_class}" data-bs-parent="#{acc_id}">\n'
                    f'    <div class="accordion-body">{escaped_content}</div>\n'
                    f"  </div>\n"
                    f"</div>"
                )
            return f'<div class="accordion" id="{acc_id}">\n' + "\n".join(items_html) + "\n</div>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "AccordionBlock",
            "items": self.items,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccordionBlock":
        return cls(items=data.get("items"), **cls.extract_spacing_kwargs(data))


class ListGroupBlock(Element):
    """Repräsentiert eine Bootstrap List Group."""

    def __init__(self, items: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.items = items if items is not None else ["Eintrag 1", "Eintrag 2", "Eintrag 3"]

    def render(self, version: str = "5") -> str:
        items_html = "\n".join([f'  <li class="list-group-item">{html.escape(item)}</li>' for item in self.items])
        return f'<ul class="list-group">\n{items_html}\n</ul>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "ListGroupBlock",
            "items": self.items,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ListGroupBlock":
        return cls(items=data.get("items"), **cls.extract_spacing_kwargs(data))


class FormInputBlock(Element):
    """Repräsentiert ein Bootstrap 5 Formulardefinitions-Feld (Input, Select, Textarea)."""

    def __init__(
        self,
        label: str = "Eingabefeld",
        input_type: str = "text",
        placeholder: str = "",
        help_text: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = label
        self.input_type = input_type  # text, email, password, number, textarea
        self.placeholder = placeholder
        self.help_text = help_text

    def render(self, version: str = "5") -> str:
        field_id = f"field-{self.id}"
        esc_label = html.escape(self.label)
        esc_placeholder = html.escape(self.placeholder, quote=True)
        esc_help = html.escape(self.help_text)

        form_group_class = "form-group" if version == "3" else "mb-3"
        control_class = "form-control"

        label_class = "control-label" if version == "3" else "form-label"
        label_html = f'<label for="{field_id}" class="{label_class}">{esc_label}</label>'

        if self.input_type == "textarea":
            input_html = f'<textarea class="{control_class}" id="{field_id}" rows="3" placeholder="{esc_placeholder}"></textarea>'
        else:
            safe_type = _sanitize_css_class(self.input_type, "text")
            input_html = (
                f'<input type="{safe_type}" class="{control_class}" id="{field_id}" placeholder="{esc_placeholder}">'
            )

        help_class = "help-block" if version == "3" else "form-text"
        help_html = (
            f'<span class="{help_class}" id="{field_id}-help">{esc_help}</span>'
            if (esc_help and version == "3")
            else (f'<div id="{field_id}-help" class="form-text">{esc_help}</div>' if esc_help else "")
        )

        return f'<div class="{form_group_class}">\n  {label_html}\n  {input_html}\n  {help_html}\n</div>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "FormInputBlock",
            "label": self.label,
            "input_type": self.input_type,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormInputBlock":
        return cls(
            label=data.get("label", "Eingabefeld"),
            input_type=data.get("input_type", "text"),
            placeholder=data.get("placeholder", ""),
            help_text=data.get("help_text", ""),
            **cls.extract_spacing_kwargs(data),
        )


class NavbarBlock(Element):
    """Repräsentiert eine Bootstrap Navigation Bar."""

    def __init__(
        self,
        brand: str = "Meine Website",
        links: list[dict[str, str]] | None = None,
        bg_style: str = "dark",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.brand = brand
        self.links = (
            links
            if links is not None
            else [
                {"text": "Start", "url": "#"},
                {"text": "Über uns", "url": "#"},
                {"text": "Kontakt", "url": "#"},
            ]
        )
        self.bg_style = bg_style  # dark, primary, light

    def render(self, version: str = "5") -> str:
        esc_brand = html.escape(self.brand)
        safe_bg = _sanitize_css_class(self.bg_style, "dark")

        links_html_list = []
        for link in self.links:
            text = html.escape(link.get("text", "Link"))
            safe_url = _sanitize_url(link.get("url", "#"), fallback="#")
            if version == "3":
                links_html_list.append(f'        <li><a href="{safe_url}">{text}</a></li>')
            else:
                links_html_list.append(
                    f'      <li class="nav-item"><a class="nav-link" href="{safe_url}">{text}</a></li>'
                )
        links_html = "\n".join(links_html_list)

        if version == "3":
            nav_class = "navbar-inverse" if safe_bg in ["dark", "primary"] else "navbar-default"
            return (
                f'<nav class="navbar {nav_class}">\n'
                f'  <div class="container-fluid">\n'
                f'    <div class="navbar-header">\n'
                f'      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#nav-{self.id}">\n'
                f'        <span class="sr-only">Toggle navigation</span>\n'
                f'        <span class="icon-bar"></span>\n'
                f'        <span class="icon-bar"></span>\n'
                f'        <span class="icon-bar"></span>\n'
                f"      </button>\n"
                f'      <a class="navbar-brand" href="#">{esc_brand}</a>\n'
                f"    </div>\n"
                f'    <div class="collapse navbar-collapse" id="nav-{self.id}">\n'
                f'      <ul class="nav navbar-nav">\n'
                f"{links_html}\n"
                f"      </ul>\n"
                f"    </div>\n"
                f"  </div>\n"
                f"</nav>"
            )
        else:
            dark_class = " navbar-dark" if safe_bg in ["dark", "primary"] else ""
            return (
                f'<nav class="navbar navbar-expand-lg bg-{safe_bg}{dark_class}">\n'
                f'  <div class="container-fluid">\n'
                f'    <a class="navbar-brand" href="#">{esc_brand}</a>\n'
                f'    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav-{self.id}">\n'
                f'      <span class="navbar-toggler-icon"></span>\n'
                f"    </button>\n"
                f'    <div class="collapse navbar-collapse" id="nav-{self.id}">\n'
                f'      <ul class="navbar-nav me-auto mb-2 mb-lg-0">\n'
                f"{links_html}\n"
                f"      </ul>\n"
                f"    </div>\n"
                f"  </div>\n"
                f"</nav>"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "NavbarBlock",
            "brand": self.brand,
            "links": self.links,
            "bg_style": self.bg_style,
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NavbarBlock":
        return cls(
            brand=data.get("brand", "Meine Website"),
            links=data.get("links"),
            bg_style=data.get("bg_style", "dark"),
            **cls.extract_spacing_kwargs(data),
        )


class Column(Element):
    """Repräsentiert eine Bootstrap Spalte (z.B. col-md-6)."""

    def __init__(self, span: int = 12, element_id: str | None = None, **kwargs):
        super().__init__(element_id=element_id, **kwargs)
        self.span = span
        self.elements: list[Element] = []

    def add_element(self, element: Element):
        self.elements.append(element)

    def remove_element(self, element_id: str):
        self.elements = [e for e in self.elements if e.id != element_id]

    def move_element_up(self, element_id: str):
        for i, e in enumerate(self.elements):
            if e.id == element_id:
                if i > 0:
                    self.elements[i], self.elements[i - 1] = (
                        self.elements[i - 1],
                        self.elements[i],
                    )
                break

    def move_element_down(self, element_id: str):
        for i, e in enumerate(self.elements):
            if e.id == element_id:
                if i < len(self.elements) - 1:
                    self.elements[i], self.elements[i + 1] = (
                        self.elements[i + 1],
                        self.elements[i],
                    )
                break

    def render(self, version: str = "5") -> str:
        rendered_elements = [e.apply_spacing_to_html(e.render(version=version), version=version) for e in self.elements]
        inner_html = "\n".join(rendered_elements)
        html_code = f'<div class="col-md-{self.span}">\n{inner_html}\n</div>'
        return self.apply_spacing_to_html(html_code, version=version)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "Column",
            "span": self.span,
            "elements": [e.to_dict() for e in self.elements],
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Column":
        kwargs = cls.extract_spacing_kwargs(data)
        kwargs.pop("element_id", None)
        col = cls(
            span=data.get("span", 12),
            element_id=data.get("id"),
            **kwargs,
        )
        for e_data in data.get("elements", []):
            col.add_element(Element.from_dict(e_data))
        return col


class Row(Element):
    """Repräsentiert eine Bootstrap Zeile (row)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.columns: list[Column] = []

    def add_column(self, column: Column):
        self.columns.append(column)

    def remove_column(self, col_id: str):
        self.columns = [c for c in self.columns if c.id != col_id]

    def render(self, version: str = "5") -> str:
        cols_html = "\n".join([c.render(version=version) for c in self.columns])
        row_class = "row" if version == "3" else "row mb-3"
        html_code = f'<div class="{row_class}">\n{cols_html}\n</div>'
        return self.apply_spacing_to_html(html_code, version=version)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "Row",
            "columns": [c.to_dict() for c in self.columns],
            **self.base_to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Row":
        row = cls(**cls.extract_spacing_kwargs(data))
        for c_data in data.get("columns", []):
            row.add_column(Element.from_dict(c_data))
        return row


class Page(Element):
    """Das Haupt-Dokument (container)."""

    def __init__(self, title: str = "Neues Projekt", element_id: str | None = None):
        super().__init__(element_id)
        self.title = title
        self.rows: list[Row] = []

    def add_row(self, row: Row):
        self.rows.append(row)

    def remove_row(self, row_id: str):
        self.rows = [r for r in self.rows if r.id != row_id]

    def move_row_up(self, row_id: str):
        for i, r in enumerate(self.rows):
            if r.id == row_id:
                if i > 0:
                    self.rows[i], self.rows[i - 1] = self.rows[i - 1], self.rows[i]
                break

    def move_row_down(self, row_id: str):
        for i, r in enumerate(self.rows):
            if r.id == row_id:
                if i < len(self.rows) - 1:
                    self.rows[i], self.rows[i + 1] = self.rows[i + 1], self.rows[i]
                break

    def render(self, version: str = "5") -> str:
        rows_html = "\n".join([r.render(version=version) for r in self.rows])
        container_class = "container" if version == "3" else "container mt-5"
        return f'<div class="{container_class}">\n{rows_html}\n</div>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "Page",
            "title": self.title,
            "rows": [r.to_dict() for r in self.rows],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Page":
        page = cls(title=data.get("title", "Neues Projekt"), element_id=data.get("id"))
        for r_data in data.get("rows", []):
            page.add_row(Element.from_dict(r_data))
        return page
