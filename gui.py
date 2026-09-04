import json
import os
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

import security
from generator import HTMLConverter, HTMLGenerator
from models import (
    AccordionBlock,
    AlertBlock,
    BadgeBlock,
    ButtonBlock,
    CardBlock,
    Column,
    Element,
    FormInputBlock,
    HtmlBlock,
    ImageBlock,
    ListGroupBlock,
    NavbarBlock,
    Page,
    Row,
    TableBlock,
    TextBlock,
)

BASE_APP_DIR = Path(__file__).resolve().parent


def get_resource_path(relative_path):
    """Gibt den absoluten Pfad zur Ressource zurück (funktioniert auch im PyInstaller Bundle)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return str((BASE_APP_DIR / relative_path).resolve())


def apply_window_icon(window):
    """Setzt das Anwendungs-Icon (.ico und .png) für Hauptfenster, Handbuch und Dialoge."""
    # 1. ICO für Windows
    ico_path = get_resource_path("favicon.ico")
    if os.path.exists(ico_path):
        try:
            window.iconbitmap(ico_path)
        except Exception:
            pass

    # 2. PNG für Fenster & Taskleiste
    png_path = get_resource_path("android-chrome-512x512.png")
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path)
            photo = ImageTk.PhotoImage(img)
            window.iconphoto(False, photo)
            window._icon_photo_ref = photo  # GC-Schutz
        except Exception:
            pass


# Automatisches Anwenden des Icons auf ALLE CTkToplevel-Dialoge / Werkzeug-Fenster
_original_toplevel_init = ctk.CTkToplevel.__init__


def _toplevel_init_with_icon(self, *args, **kwargs):
    _original_toplevel_init(self, *args, **kwargs)
    apply_window_icon(self)


ctk.CTkToplevel.__init__ = _toplevel_init_with_icon


class ButtonSelectionDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Button hinzufügen",
        default_text="Klick mich",
        default_url="#",
        default_style="primary",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("400x300")
        self.result_text = None
        self.result_url = None
        self.result_style = None

        ctk.CTkLabel(self, text="Button-Text:").pack(pady=(15, 2))
        self.text_entry = ctk.CTkEntry(self, width=320)
        self.text_entry.insert(0, default_text)
        self.text_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Ziel-URL:").pack(pady=(5, 2))
        self.url_entry = ctk.CTkEntry(self, width=320)
        self.url_entry.insert(0, default_url)
        self.url_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Stil:").pack(pady=(5, 2))
        self.style_var = ctk.StringVar(value=default_style)
        styles = [
            "primary",
            "secondary",
            "success",
            "danger",
            "warning",
            "info",
            "light",
            "dark",
        ]
        self.style_optionmenu = ctk.CTkOptionMenu(self, values=styles, variable=self.style_var, width=150)
        self.style_optionmenu.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_text = self.text_entry.get()
        self.result_url = self.url_entry.get()
        self.result_style = self.style_var.get()
        self.destroy()

    def cancel(self):
        self.result_text = None
        self.destroy()


class AlertSelectionDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Hinweisbox (Alert) hinzufügen",
        default_text="Dies ist ein Hinweis",
        default_style="info",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("400x280")
        self.result_text = None
        self.result_style = None

        ctk.CTkLabel(self, text="Hinweis-Text:").pack(pady=(15, 2))
        self.text_entry = ctk.CTkEntry(self, width=320)
        self.text_entry.insert(0, default_text)
        self.text_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Stil / Farbe:").pack(pady=(5, 2))
        self.style_var = ctk.StringVar(value=default_style)
        styles = [
            "info",
            "success",
            "warning",
            "danger",
            "primary",
            "secondary",
            "light",
            "dark",
        ]
        self.style_optionmenu = ctk.CTkOptionMenu(self, values=styles, variable=self.style_var, width=150)
        self.style_optionmenu.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_text = self.text_entry.get()
        self.result_style = self.style_var.get()
        self.destroy()

    def cancel(self):
        self.result_text = None
        self.destroy()


class HtmlInputDialog(ctk.CTkToplevel):
    def __init__(self, master, title="HTML-Code einfügen", default_code=""):
        super().__init__(master)
        self.title(title)
        self.geometry("600x450")
        self.result_code = None

        ctk.CTkLabel(self, text="Eigener HTML-Code:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        self.textbox = ctk.CTkTextbox(self, width=560, height=300, font=("Consolas", 11))
        self.textbox.pack(padx=10, pady=5)
        if default_code:
            self.textbox.insert("1.0", default_code)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_code = self.textbox.get("1.0", "end-1c")
        self.destroy()

    def cancel(self):
        self.result_code = None
        self.destroy()


class TableDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Tabelle konfigurieren",
        default_headers=None,
        default_rows_text="",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("540x530")
        self.result_headers = None
        self.result_rows = None

        headers_str = (
            HTMLConverter.format_table_line(default_headers) if default_headers else "Spalte 1 | Spalte 2 | Spalte 3"
        )
        if not default_rows_text:
            default_rows_text = "Zeile 1 A | Zeile 1 B | Zeile 1 C\nZeile 2 A | Zeile 2 B | Zeile 2 C"

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(top_frame, text="Spaltenköpfe (Getrennt mit '|'):").pack(side="left")
        ctk.CTkButton(
            top_frame,
            text="📋 HTML-Tabelle importieren",
            width=180,
            height=26,
            fg_color="purple",
            hover_color="#4a148c",
            command=self.import_html_table,
        ).pack(side="right")

        self.headers_entry = ctk.CTkEntry(self, width=500)
        self.headers_entry.insert(0, headers_str)
        self.headers_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Zeilen-Daten (Pro Zeile 1 Datenzeile, Getrennt mit '|'):").pack(pady=(10, 2))
        self.rows_textbox = ctk.CTkTextbox(self, width=500, height=220, font=("Consolas", 11))
        self.rows_textbox.insert("1.0", default_rows_text)
        self.rows_textbox.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def import_html_table(self):
        import_win = ctk.CTkToplevel(self)
        import_win.title("HTML-Tabellencode einfügen")
        import_win.geometry("550x380")

        ctk.CTkLabel(
            import_win,
            text="Füge hier deinen HTML-Tabellencode (<table>...</table>) ein:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(15, 5))

        html_textbox = ctk.CTkTextbox(import_win, width=500, height=220, font=("Consolas", 11))
        html_textbox.pack(pady=5)

        def parse_and_apply():
            html_code = html_textbox.get("1.0", "end-1c")
            if not html_code.strip():
                import_win.destroy()
                return
            headers, rows = HTMLConverter.parse_html_table(html_code)
            if not headers and not rows:
                messagebox.showwarning(
                    "Hinweis",
                    "Es konnte keine gültige <table> Struktur gefunden werden.",
                )
                return

            if headers:
                self.headers_entry.delete(0, "end")
                self.headers_entry.insert(0, HTMLConverter.format_table_line(headers))

            if rows:
                self.rows_textbox.delete("1.0", "end")
                formatted_rows = "\n".join([HTMLConverter.format_table_line(r) for r in rows])
                self.rows_textbox.insert("1.0", formatted_rows)

            messagebox.showinfo(
                "Erfolg",
                f"HTML-Tabelle erfolgreich importiert! ({len(headers)} Spalten, {len(rows)} Zeilen)",
            )
            import_win.destroy()

        btn_f = ctk.CTkFrame(import_win, fg_color="transparent")
        btn_f.pack(pady=15)
        ctk.CTkButton(
            btn_f,
            text="Importieren & Übernehmen",
            command=parse_and_apply,
            fg_color="green",
            hover_color="darkgreen",
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_f,
            text="Abbrechen",
            command=import_win.destroy,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        import_win.transient(self)
        import_win.grab_set()

    def save(self):
        raw_h = self.headers_entry.get()
        self.result_headers = HTMLConverter.parse_table_line(raw_h)

        raw_rows = self.rows_textbox.get("1.0", "end-1c").strip().split("\n")
        self.result_rows = []
        for line in raw_rows:
            if line.strip():
                cells = HTMLConverter.parse_table_line(line)
                if cells:
                    self.result_rows.append(cells)
        self.destroy()

    def cancel(self):
        self.result_headers = None
        self.result_rows = None
        self.destroy()


class CardDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Card / Panel konfigurieren",
        default_title="Titel",
        default_content="Inhalt...",
        default_style="default",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("450x400")
        self.result_title = None
        self.result_content = None
        self.result_style = None

        ctk.CTkLabel(self, text="Karten-Titel:").pack(pady=(10, 2))
        self.title_entry = ctk.CTkEntry(self, width=400)
        self.title_entry.insert(0, default_title)
        self.title_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Karten-Inhalt:").pack(pady=(5, 2))
        self.content_textbox = ctk.CTkTextbox(self, width=400, height=150)
        self.content_textbox.insert("1.0", default_content)
        self.content_textbox.pack(pady=5)

        ctk.CTkLabel(self, text="Stil:").pack(pady=(5, 2))
        self.style_var = ctk.StringVar(value=default_style)
        styles = [
            "default",
            "primary",
            "secondary",
            "success",
            "danger",
            "warning",
            "info",
            "dark",
        ]
        self.style_optionmenu = ctk.CTkOptionMenu(self, values=styles, variable=self.style_var, width=150)
        self.style_optionmenu.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_title = self.title_entry.get()
        self.result_content = self.content_textbox.get("1.0", "end-1c")
        self.result_style = self.style_var.get()
        self.destroy()

    def cancel(self):
        self.result_title = None
        self.destroy()


class BadgeDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Badge / Label hinzufügen",
        default_text="Badge",
        default_style="primary",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("380x250")
        self.result_text = None
        self.result_style = None

        ctk.CTkLabel(self, text="Badge-Text:").pack(pady=(15, 2))
        self.text_entry = ctk.CTkEntry(self, width=300)
        self.text_entry.insert(0, default_text)
        self.text_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Stil:").pack(pady=(5, 2))
        self.style_var = ctk.StringVar(value=default_style)
        styles = [
            "primary",
            "secondary",
            "success",
            "danger",
            "warning",
            "info",
            "dark",
            "light",
        ]
        self.style_optionmenu = ctk.CTkOptionMenu(self, values=styles, variable=self.style_var, width=150)
        self.style_optionmenu.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_text = self.text_entry.get()
        self.result_style = self.style_var.get()
        self.destroy()

    def cancel(self):
        self.result_text = None
        self.destroy()


class ListGroupDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="List Group (Liste) hinzufügen",
        default_items_text="Eintrag 1\nEintrag 2\nEintrag 3",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("400x350")
        self.result_items = None

        ctk.CTkLabel(self, text="Einträge (Ein Eintrag pro Zeile):").pack(pady=(15, 5))
        self.textbox = ctk.CTkTextbox(self, width=350, height=200)
        self.textbox.insert("1.0", default_items_text)
        self.textbox.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        raw = self.textbox.get("1.0", "end-1c").strip().split("\n")
        self.result_items = [item.strip() for item in raw if item.strip()]
        self.destroy()

    def cancel(self):
        self.result_items = None
        self.destroy()


class AccordionDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Akkordeon bearbeiten", default_items=None):
        super().__init__(master)
        self.title(title)
        self.geometry("550x480")
        self.result_items = None

        if default_items:
            lines = [f"{item.get('title', '')} | {item.get('content', '')}" for item in default_items]
            default_text = "\n".join(lines)
        else:
            default_text = "Abschnitt 1 | Inhalt von Abschnitt 1...\nAbschnitt 2 | Inhalt von Abschnitt 2..."

        ctk.CTkLabel(
            self,
            text="Akkordeon Abschnitte (Format: Titel | Inhalt - Ein Eintrag pro Zeile):",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(15, 5))

        self.textbox = ctk.CTkTextbox(self, width=500, height=300)
        self.textbox.insert("1.0", default_text)
        self.textbox.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        raw = self.textbox.get("1.0", "end-1c").strip().split("\n")
        items = []
        for line in raw:
            if "|" in line:
                parts = line.split("|", 1)
                items.append({"title": parts[0].strip(), "content": parts[1].strip()})
            elif line.strip():
                items.append({"title": line.strip(), "content": ""})
        self.result_items = items
        self.destroy()

    def cancel(self):
        self.result_items = None
        self.destroy()


class FormInputDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Formularfeld hinzufügen",
        default_label="Eingabefeld",
        default_type="text",
        default_placeholder="",
        default_help="",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("420x360")
        self.result_label = None
        self.result_type = None
        self.result_placeholder = None
        self.result_help = None

        ctk.CTkLabel(self, text="Beschriftung (Label):").pack(pady=(15, 2))
        self.label_entry = ctk.CTkEntry(self, width=340)
        self.label_entry.insert(0, default_label)
        self.label_entry.pack(pady=3)

        ctk.CTkLabel(self, text="Feld-Typ:").pack(pady=(5, 2))
        self.type_var = ctk.StringVar(value=default_type)
        types = ["text", "email", "password", "number", "textarea"]
        self.type_menu = ctk.CTkOptionMenu(self, values=types, variable=self.type_var, width=200)
        self.type_menu.pack(pady=3)

        ctk.CTkLabel(self, text="Platzhalter (Placeholder):").pack(pady=(5, 2))
        self.ph_entry = ctk.CTkEntry(self, width=340)
        self.ph_entry.insert(0, default_placeholder)
        self.ph_entry.pack(pady=3)

        ctk.CTkLabel(self, text="Hilfetext:").pack(pady=(5, 2))
        self.help_entry = ctk.CTkEntry(self, width=340)
        self.help_entry.insert(0, default_help)
        self.help_entry.pack(pady=3)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_label = self.label_entry.get().strip()
        self.result_type = self.type_var.get()
        self.result_placeholder = self.ph_entry.get().strip()
        self.result_help = self.help_entry.get().strip()
        self.destroy()

    def cancel(self):
        self.destroy()


class NavbarDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Navigationsleiste hinzufügen",
        default_brand="Meine Website",
        default_bg="dark",
        default_links_text="Start | #\nÜber uns | #\nKontakt | #",
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("480x420")
        self.result_brand = None
        self.result_bg = None
        self.result_links = None

        ctk.CTkLabel(self, text="Website-/Shop-Name (Brand):").pack(pady=(15, 2))
        self.brand_entry = ctk.CTkEntry(self, width=400)
        self.brand_entry.insert(0, default_brand)
        self.brand_entry.pack(pady=3)

        ctk.CTkLabel(self, text="Hintergrundfarbe:").pack(pady=(5, 2))
        self.bg_var = ctk.StringVar(value=default_bg)
        bgs = ["dark", "primary", "light"]
        self.bg_menu = ctk.CTkOptionMenu(self, values=bgs, variable=self.bg_var, width=180)
        self.bg_menu.pack(pady=3)

        ctk.CTkLabel(
            self,
            text="Links (Format: Text | Ziel-URL - Ein Eintrag pro Zeile):",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(10, 2))

        self.textbox = ctk.CTkTextbox(self, width=400, height=120)
        self.textbox.insert("1.0", default_links_text)
        self.textbox.pack(pady=3)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_brand = self.brand_entry.get().strip()
        self.result_bg = self.bg_var.get()
        raw = self.textbox.get("1.0", "end-1c").strip().split("\n")
        links = []
        for line in raw:
            if "|" in line:
                parts = line.split("|", 1)
                links.append({"text": parts[0].strip(), "url": parts[1].strip()})
            elif line.strip():
                links.append({"text": line.strip(), "url": "#"})
        self.result_links = links
        self.destroy()

    def cancel(self):
        self.destroy()


class ElementSpacingDialog(ctk.CTkToplevel):
    def __init__(self, master, element: Element):
        super().__init__(master)
        self.title("Abstände (Margin & Padding) anpassen")
        self.geometry("400x380")
        self.saved = False

        self.element = element
        spacing_options = ["none", "0", "1", "2", "3", "4", "5"]

        ctk.CTkLabel(self, text="Aussenabstände (Margin)", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        m_frame = ctk.CTkFrame(self, fg_color="transparent")
        m_frame.pack(pady=5)

        ctk.CTkLabel(m_frame, text="Oben (mt-):").grid(row=0, column=0, padx=10, pady=5)
        self.mt_var = ctk.StringVar(value=element.margin_top)
        ctk.CTkOptionMenu(m_frame, values=spacing_options, variable=self.mt_var, width=100).grid(
            row=0, column=1, padx=10, pady=5
        )

        ctk.CTkLabel(m_frame, text="Unten (mb-):").grid(row=1, column=0, padx=10, pady=5)
        self.mb_var = ctk.StringVar(value=element.margin_bottom)
        ctk.CTkOptionMenu(m_frame, values=spacing_options, variable=self.mb_var, width=100).grid(
            row=1, column=1, padx=10, pady=5
        )

        ctk.CTkLabel(self, text="Innenabstände (Padding)", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        p_frame = ctk.CTkFrame(self, fg_color="transparent")
        p_frame.pack(pady=5)

        ctk.CTkLabel(p_frame, text="Oben (pt-):").grid(row=0, column=0, padx=10, pady=5)
        self.pt_var = ctk.StringVar(value=element.padding_top)
        ctk.CTkOptionMenu(p_frame, values=spacing_options, variable=self.pt_var, width=100).grid(
            row=0, column=1, padx=10, pady=5
        )

        ctk.CTkLabel(p_frame, text="Unten (pb-):").grid(row=1, column=0, padx=10, pady=5)
        self.pb_var = ctk.StringVar(value=element.padding_bottom)
        ctk.CTkOptionMenu(p_frame, values=spacing_options, variable=self.pb_var, width=100).grid(
            row=1, column=1, padx=10, pady=5
        )

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.element.margin_top = self.mt_var.get()
        self.element.margin_bottom = self.mb_var.get()
        self.element.padding_top = self.pt_var.get()
        self.element.padding_bottom = self.pb_var.get()
        self.saved = True
        self.destroy()

    def cancel(self):
        self.saved = False
        self.destroy()


class ConverterDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Bootstrap 3 ➔ Bootstrap 5 Konverter"):
        super().__init__(master)
        self.title(title)
        self.geometry("800x600")

        ctk.CTkLabel(
            self,
            text="Füge hier deinen Bootstrap 3 HTML-Code ein:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(10, 5))

        self.input_textbox = ctk.CTkTextbox(self, width=760, height=200, font=("Consolas", 11))
        self.input_textbox.pack(padx=10, pady=5)

        btn_convert = ctk.CTkButton(
            self,
            text="➔ In Bootstrap 5 Konvertieren",
            command=self.convert,
            fg_color="purple",
            hover_color="#4a148c",
        )
        btn_convert.pack(pady=10)

        ctk.CTkLabel(
            self,
            text="Konvertierter Bootstrap 5 Code:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(5, 5))

        self.output_textbox = ctk.CTkTextbox(self, width=760, height=200, font=("Consolas", 11))
        self.output_textbox.pack(padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Code Kopieren",
            command=self.copy_output,
            fg_color="green",
            hover_color="darkgreen",
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Schließen", command=self.destroy).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()

    def convert(self):
        input_code = self.input_textbox.get("1.0", "end-1c")
        if not input_code.strip():
            messagebox.showwarning(
                "Hinweis",
                "Bitte füge erst Bootstrap 3 HTML Code in das obere Feld ein.",
            )
            return

        converted_code = HTMLConverter.convert_bs3_to_bs5(input_code)
        _, repairs = HTMLConverter.fix_html_syntax(input_code)

        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", converted_code)

        if repairs:
            repair_info = "\n• " + "\n• ".join(repairs)
            messagebox.showinfo(
                "Erfolg & Reparatur",
                f"HTML-Code erfolgreich konvertiert und repariert:{repair_info}",
            )
        else:
            messagebox.showinfo("Erfolg", "HTML-Code erfolgreich nach Bootstrap 5 konvertiert!")

    def copy_output(self):
        code = self.output_textbox.get("1.0", "end-1c")
        if code.strip():
            self.clipboard_clear()
            self.clipboard_append(code)
            messagebox.showinfo(
                "Kopiert",
                "Konvertierter Bootstrap 5 Code wurde in die Zwischenablage kopiert.",
            )


class MultilineTextInputDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Text hinzufügen", default_tag="p"):
        super().__init__(master)
        self.title(title)
        self.geometry("400x400")
        self.result_text = None
        self.result_tag = default_tag

        tag_frame = ctk.CTkFrame(self, fg_color="transparent")
        tag_frame.pack(pady=(10, 0))
        ctk.CTkLabel(tag_frame, text="Typ:").pack(side="left", padx=5)
        self.tag_var = ctk.StringVar(value=default_tag)
        self.tag_optionmenu = ctk.CTkOptionMenu(
            tag_frame,
            values=["p", "h1", "h2", "h3", "h4", "h5", "h6"],
            variable=self.tag_var,
        )
        self.tag_optionmenu.pack(side="left", padx=5)

        self.textbox = ctk.CTkTextbox(self, width=380, height=250)
        self.textbox.pack(padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Speichern", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        self.result_text = self.textbox.get("1.0", "end-1c")
        self.result_tag = self.tag_var.get()
        self.destroy()

    def cancel(self):
        self.result_text = None
        self.destroy()


class ImageSelectionDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Bild hinzufügen"):
        super().__init__(master)
        self.title(title)
        self.geometry("450x280")
        self.result = None
        self.local_filepath = None

        self.choice_var = ctk.StringVar(value="url")

        ctk.CTkRadioButton(
            self,
            text="Bild-URL eingeben",
            variable=self.choice_var,
            value="url",
            command=self.update_view,
        ).pack(pady=10)
        ctk.CTkRadioButton(
            self,
            text="Lokales Bild wählen",
            variable=self.choice_var,
            value="file",
            command=self.update_view,
        ).pack(pady=5)

        self.url_entry = ctk.CTkEntry(self, width=380, placeholder_text="https://...")
        self.url_entry.pack(pady=10)

        self.file_btn = ctk.CTkButton(self, text="Datei durchsuchen...", command=self.browse_file)
        self.file_path_label = ctk.CTkLabel(self, text="")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Hinzufügen", command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=10)

        self.update_view()
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def update_view(self):
        if self.choice_var.get() == "url":
            self.file_btn.pack_forget()
            self.file_path_label.pack_forget()
            self.url_entry.pack(pady=10)
        else:
            self.url_entry.pack_forget()
            self.file_btn.pack(pady=5)
            self.file_path_label.pack(pady=5)

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Bilder", "*.png;*.jpg;*.jpeg;*.gif;*.webp;*.svg;*.bmp")])
        if filepath:
            self.local_filepath = filepath
            display_path = filepath if len(filepath) < 40 else "..." + filepath[-37:]
            self.file_path_label.configure(text=display_path)

    def save(self):
        if self.choice_var.get() == "url":
            self.result = self.url_entry.get()
        else:
            if self.local_filepath:
                self.result = self.local_filepath
                messagebox.showwarning(
                    "Wichtiger Server-Hinweis",
                    "Du hast ein lokales Bild ausgewählt.\n\nDas Bild wird im Editor lokal korrekt angezeigt.\n\nWenn du den generierten HTML-Code online verwendest, musst du sicherstellen, dass das Bild auf deinen Server hochgeladen wird und der Pfad (src) im HTML angepasst wird!",
                )

        if self.result:
            self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class ColumnLayoutDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Spaltenaufteilung wählen"):
        super().__init__(master)
        self.title(title)
        self.geometry("340x200")
        self.result = None

        ctk.CTkLabel(self, text="Wähle die Spaltenaufteilung:").pack(pady=(15, 5))

        self.layout_var = ctk.StringVar(value="1 Spalte (12)")
        layouts = [
            "1 Spalte (12)",
            "2 Spalten (6 / 6)",
            "2 Spalten (8 / 4)",
            "2 Spalten (4 / 8)",
            "2 Spalten (9 / 3)",
            "2 Spalten (3 / 9)",
            "2 Spalten (10 / 2)",
            "2 Spalten (2 / 10)",
            "2 Spalten (7 / 5)",
            "2 Spalten (5 / 7)",
            "3 Spalten (4 / 4 / 4)",
            "3 Spalten (6 / 3 / 3)",
            "3 Spalten (3 / 6 / 3)",
            "4 Spalten (3 / 3 / 3 / 3)",
        ]

        self.optionmenu = ctk.CTkOptionMenu(self, values=layouts, variable=self.layout_var, width=260)
        self.optionmenu.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="OK", command=self.save, width=80).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="red",
            hover_color="darkred",
            width=80,
        ).pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def save(self):
        selection = self.layout_var.get()
        # Extrahiere Zahlen aus den Klammern e.g. "(6 / 6)" oder "(12)"
        raw_numbers = selection.split("(")[1].split(")")[0]
        parts = raw_numbers.split("/")
        self.result = [int(p.strip()) for p in parts]
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class HelpDialog(ctk.CTkToplevel):
    """Integriertes Handbuch-Fenster mit Live-Suchfunktion."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Benutzerhandbuch - Bootstrap 5 Low-Code Editor")
        self.geometry("1100x750")
        apply_window_icon(self)

        # Handbuch-Datenbank (Kategorien, Titel, Inhalt, Schlagworte)
        self.sections_data = [
            {
                "category": "🚀 Erste Schritte",
                "title": "Über die Software & Praxiseinsatz",
                "keywords": [
                    "anfang",
                    "start",
                    "einführung",
                    "hilfe",
                    "lernen",
                    "konzept",
                    "schritt",
                    "gambio",
                    "shopware",
                    "bootstrap3",
                    "bootstrap5",
                    "artikelbeschreibung",
                    "shop",
                ],
                "content": (
                    "Willkommen beim Bootstrap 5 & 3 Low-Code Editor!\n\n"
                    "Diese Software unterstützt Onlineshop-Betreiber dabei, einzelne Bereiche in Ihrem Shop "
                    "(wie z. B. Artikelbeschreibungen, Kategoriestexte oder Infoboxen) ansprechend und übersichtlich "
                    "zu gestalten – völlig ohne HTML- oder Programmierkenntnisse.\n\n"
                    "💡 Welches Bootstrap soll ich wählen?\n"
                    "• Gambio Shopsysteme: Wählen Sie oben rechts 'Bootstrap 3'. Gambio basiert in vielen Templates auf Bootstrap 3.\n"
                    "• Shopware 6 / Moderne Systeme: Wählen Sie oben rechts 'Bootstrap 5'. Shopware 6 und moderne Systeme nutzen Bootstrap 5.\n\n"
                    "In 3 einfachen Schritten zur perfekten Artikelbeschreibung:\n"
                    "1. Element hinzufügen: Klicken Sie links auf ein Werkzeug (z. B. Spalten für Produktvorteile, Hinweisboxen, Karten).\n"
                    "2. Inhalt anpassen: Tragen Sie Ihren Text ein, wählen Sie Bilder, Links und passende Farben.\n"
                    "3. Code kopieren & einfügen: Klicken Sie auf 'Code Kopieren' und fügen Sie den HTML-Code direkt in die Artikelbeschreibung Ihres Shops ein."
                ),
            },
            {
                "category": "🖥️ Werkzeuge im Detail",
                "title": "Werkzeuge (Linke Leiste)",
                "keywords": [
                    "werkzeuge",
                    "leiste",
                    "zeile",
                    "spalte",
                    "überschrift",
                    "html",
                    "konverter",
                    "speichern",
                    "laden",
                ],
                "content": (
                    "Hier ist jedes Werkzeug der linken Leiste im Detail erklärt:\n\n"
                    "• Button '+ Neue Zeile / Spalten':\n"
                    "  Erstellt ein neues Layout-Gitter. Sie werden gefragt, wie viele Spalten Sie nebeneinander möchten "
                    "  (z. B. 2 Spalten für Bild links, Text rechts). Danach können Sie in jede Spalte Bausteine einfügen.\n\n"
                    "• Button '+ Überschrift (H1-H6)':\n"
                    "  Fügt eine alleinstehende Haupt- oder Unterüberschrift in voller Breite ein.\n\n"
                    "• Button '+ Eigener HTML Code':\n"
                    "  Fügt einen freien HTML-Block ein. Ideal für eingebundene Widgets, iFrames, YouTube-Videos oder spezielle Skripte.\n\n"
                    "• Button 'BS3 ➔ BS5 Konverter':\n"
                    "  Wandelt alten Bootstrap 3 Code (z. B. aus älteren Gambio-Vorlagen) automatisch in modernen Bootstrap 5 Code um.\n\n"
                    "• Button 'Projekt Speichern / Laden':\n"
                    "  Sichert Ihren kompletten Entwurf in einer passwortgeschützten Datei auf Ihrem PC."
                ),
            },
            {
                "category": "🖥️ Werkzeuge im Detail",
                "title": "Seitenstruktur (Mittlerer Bereich)",
                "keywords": [
                    "struktur",
                    "mitte",
                    "bearbeiten",
                    "löschen",
                    "hoch",
                    "runter",
                    "spalte",
                    "element",
                ],
                "content": (
                    "Der mittlere Bereich zeigt den hierarchischen Aufbau Ihrer Seite:\n\n"
                    "• Zeilen & Spalten:\n"
                    "  Jeder Zeilenblock enthält 1 bis 4 Spalten. An jeder Spalte finden Sie einen Button '+ Element hinzufügen'.\n\n"
                    "• Steuerungselemente an jedem Baustein:\n"
                    "  - ✏️ Bearbeiten: Öffnet den Dialog, um Texte, Links oder Farben anzupassen.\n"
                    "  - 📐 Abstände: Stellt die Außen- (Margin) und Innenabstände (Padding) ein.\n"
                    "  - ⬆️ / ⬇️ Verschieben: Ändert die Reihenfolge der Elemente nach oben oder unten.\n"
                    "  - 🗑️ Löschen: Entfernt das Element aus der Struktur."
                ),
            },
            {
                "category": "🖥️ Werkzeuge im Detail",
                "title": "Code, Version & Vorschau (Rechter Bereich)",
                "keywords": [
                    "code",
                    "version",
                    "bootstrap3",
                    "bootstrap5",
                    "vorschau",
                    "export",
                    "kopieren",
                    "gambio",
                    "shopware",
                ],
                "content": (
                    "Der rechte Bereich kümmert sich um den Quellcode und die Ausgabe:\n\n"
                    "• Dropdown 'Version' (Bootstrap 5 / Bootstrap 3):\n"
                    "  Hier schalten Sie um, welchen Code der Editor erzeugen soll.\n"
                    "  - Für Gambio: 'Bootstrap 3' wählen.\n"
                    "  - Für Shopware 6 & neue Webseiten: 'Bootstrap 5' wählen.\n\n"
                    "• Button 'Vorschau im Browser':\n"
                    "  Öffnet Ihre erstelle Webseite im Browser, damit Sie das Aussehen vor der Veröffentlichung testen können.\n\n"
                    "• Button 'HTML Exportieren':\n"
                    "  Speichert eine fertige `.html`-Datei ab.\n\n"
                    "• Button 'Code Kopieren':\n"
                    "  Kopiert den fertigen HTML-Code direkt in die Zwischenablage. Sie können ihn dann direkt im Admin-Bereich Ihres Shops (Gambio / Shopware) einfügen."
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Überschriften & Textblöcke",
                "keywords": [
                    "überschrift",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "text",
                    "absatz",
                    "schreiben",
                    "titel",
                ],
                "content": (
                    "Überschriften (H1 bis H6):\n"
                    "- H1 ist die wichtigste Hauptüberschrift (sollte 1x pro Seite genutzt werden).\n"
                    "- H2 & H3 sind für Themen-Abschnitte und Unterkapitel gedacht.\n"
                    "- H4 bis H6 eignen sich für kleinere Box-Titel.\n\n"
                    "Textblöcke:\n"
                    "- FürFließtext, Produktbeschreibungen oder Einleitungstexte."
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Bilder (URL & Lokale Dateien)",
                "keywords": [
                    "bild",
                    "foto",
                    "grafik",
                    "url",
                    "datei",
                    "img",
                    "hochladen",
                ],
                "content": (
                    "Sie können zwei Arten von Bildern einbinden:\n\n"
                    "1. Bild-URL:\n"
                    "   Geben Sie die Web-Adresse eines Bildes ein (z. B. `https://meinshop.de/bilder/produkt.jpg`).\n\n"
                    "2. Lokales Bild:\n"
                    "   Wählen Sie eine Bilddatei von Ihrem Computer. Das Bild wird im HTML-Code eingebettet und bleibt immer sichtbar."
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Schaltflächen (Buttons)",
                "keywords": [
                    "button",
                    "knopf",
                    "schaltfläche",
                    "link",
                    "klick",
                    "farbe",
                    "stil",
                ],
                "content": (
                    "Buttons leiten Besucher auf wichtige Seiten weiter:\n\n"
                    "• Button-Text: Angezeigte Beschriftung (z. B. 'Jetzt bestellen', 'Zum Angebot').\n"
                    "• Ziel-URL: Web-Link oder Unterseite.\n"
                    "• Stil (Farbe):\n"
                    "  - Primary: Blau (Standard-Aktion)\n"
                    "  - Success: Grün (Positive Aktion / Kauf)\n"
                    "  - Warning: Gelb (Aufmerksamkeit)\n"
                    "  - Danger: Rot (Wichtige Aktionen)"
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Hinweisboxen (Alerts)",
                "keywords": [
                    "alert",
                    "hinweis",
                    "warnung",
                    "info",
                    "erfolg",
                    "box",
                    "nachricht",
                ],
                "content": (
                    "Infoboxen lenken den Blick des Kunden auf wichtige Hinweise:\n\n"
                    "• Info (Hellblau): z. B. 'Kostenloser Versand ab 50€'\n"
                    "• Success (Grün): z. B. 'Artikel auf Lager'\n"
                    "• Warning (Gelb): z. B. 'Nur noch wenige Stück auf Lager'\n"
                    "• Danger (Rot): z. B. 'Betriebsferien vom 1. bis 15. August'"
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Karten (Cards / Panels)",
                "keywords": ["card", "karte", "panel", "kasten", "container", "rahmen"],
                "content": (
                    "Karten verpacken Inhalte in einen sauberen Kasten mit Rahmen:\n"
                    "Perfekt für Highlights, Vorteile oder Kategorie-Teaser in Ihrem Online-Shop.\n"
                    "Der Editor wandelt eine Card bei Bootstrap 3 automatisch in ein 'Panel' um."
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Akkordeon & Listen",
                "keywords": [
                    "akkordeon",
                    "accordion",
                    "klapp",
                    "faq",
                    "fragen",
                    "tabelle",
                    "liste",
                ],
                "content": (
                    "Akkordeon (Einklappbereich):\n"
                    "Ermöglicht das Auf- und Zuklappen von Inhalten per Klick – ideal für FAQ-Bereiche.\n\n"
                    "Listen (ListGroup):\n"
                    "Saubere Aufzählungen für Produkteigenschaften, Vorteile oder Lieferumfang."
                ),
            },
            {
                "category": "🧩 Bausteine im Detail",
                "title": "Formulare & Navigationsleisten",
                "keywords": [
                    "formular",
                    "input",
                    "eingabe",
                    "textarea",
                    "email",
                    "passwort",
                    "navbar",
                    "navigation",
                    "menü",
                    "header",
                ],
                "content": (
                    "• Formularfelder (FormInputBlock):\n"
                    "  Ermöglicht das Hinzufügen von Eingabefeldern (z. B. E-Mail, Text, Passwort, Textarea) inklusive Label und Hilfetexten.\n\n"
                    "• Navigationsleiste (NavbarBlock):\n"
                    "  Erstellt eine responsive Bootstrap-Headerleiste mit Shop-/Website-Namen (Brand) und frei definierbaren Navigationslinks."
                ),
            },
            {
                "category": "📐 Layout & Abstände",
                "title": "Abstände anpassen (Margin & Padding)",
                "keywords": [
                    "abstand",
                    "margin",
                    "padding",
                    "platz",
                    "oben",
                    "unten",
                    "mt",
                    "mb",
                    "pt",
                    "pb",
                ],
                "content": (
                    "Mit den Abständen sorgen Sie für ein aufgeräumtes Design:\n\n"
                    "• Außenabstand (Margin - mt / mb):\n"
                    "  Schafft Platz AUSSERHALB des Elements nach oben (mt) oder unten (mb).\n\n"
                    "• Innenabstand (Padding - pt / pb):\n"
                    "  Schafft Platz INNERHALB des Elements (z. B. Luft zwischen Text und Kartenrahmen).\n\n"
                    "Werte von 0 (kein Abstand) bis 5 (maximaler Abstand)."
                ),
            },
            {
                "category": "🛍️ Shopsysteme",
                "title": "Praxis-Tipps: Gambio vs. Shopware",
                "keywords": [
                    "gambio",
                    "shopware",
                    "shop",
                    "online-shop",
                    "e-commerce",
                    "bootstrap3",
                    "bootstrap5",
                ],
                "content": (
                    "So nutzen Sie den Editor für Ihr Online-Shopsystem:\n\n"
                    "🛒 Gambio Shopsystem:\n"
                    "• Wählen Sie oben rechts im Editor 'Bootstrap 3'.\n"
                    "• Erstellen Sie Ihre Inhalte.\n"
                    "• Klicken Sie auf 'Code Kopieren'.\n"
                    "• Fügen Sie den Code im Gambio Admin-Bereich (Content Manager / Artikelbeschreibung) im Quellcode-Modus ein.\n\n"
                    "🛒 Shopware 6:\n"
                    "• Wählen Sie oben rechts im Editor 'Bootstrap 5'.\n"
                    "• Erstellen Sie Ihr Layout.\n"
                    "• Kopieren Sie den Code und fügen Sie ihn in Shopware Erlebniswelten / HTML-Elementen ein."
                ),
            },
            {
                "category": "🔄 Konverter",
                "title": "Bootstrap 3 ➔ Bootstrap 5 Konverter",
                "keywords": [
                    "konverter",
                    "converter",
                    "bs3",
                    "bs5",
                    "bootstrap3",
                    "bootstrap5",
                    "alt",
                    "neu",
                ],
                "content": (
                    "Sie möchten alte Gambio-Texte (Bootstrap 3) für Shopware 6 (Bootstrap 5) umrüsten?\n"
                    "1. Klicken Sie links auf 'BS3 ➔ BS5 Konverter'.\n"
                    "2. Fügen Sie Ihren alten Gambio HTML-Code ein.\n"
                    "3. Klicken Sie auf 'Konvertieren'. Verwendete Klassen wie `panel`, `well` oder `img-responsive` werden automatisch zu Bootstrap 5 konvertiert!"
                ),
            },
            {
                "category": "💾 Projektverwaltung",
                "title": "Projekt Speichern & Laden",
                "keywords": [
                    "speichern",
                    "laden",
                    "projekt",
                    "passwort",
                    "verschlüsseln",
                    "datei",
                ],
                "content": (
                    "• Projekt Speichern:\n"
                    "  Sichert Ihren Arbeitsstand in einer verschlüsselten `.enc`-Datei.\n"
                    "  Sie vergeben ein Passwort, damit Ihre Daten geschützt sind.\n\n"
                    "• Projekt Laden:\n"
                    "  Stellt ein gespeichertes Projekt nach Passworteingabe wieder her."
                ),
            },
        ]

        self._build_ui()
        self.transient(master)

    def _build_ui(self):
        # Header / Suchleiste Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="📖 Benutzerhandbuch",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_lbl.pack(side="top", anchor="w", pady=(0, 5))

        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(search_frame, text="🔍 Suche:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suchbegriff eingeben (z. B. Button, Bild, Abstand, Speichern)...",
            width=500,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.reset_search_btn = ctk.CTkButton(search_frame, text="Zurücksetzen", width=100, command=self.reset_search)
        self.reset_search_btn.pack(side="left", padx=(0, 10))

        pdf_btn = ctk.CTkButton(
            search_frame,
            text="📥 Handbuch als PDF herunterladen",
            fg_color="green",
            hover_color="darkgreen",
            command=self.export_pdf,
        )
        pdf_btn.pack(side="left")

        # Scrollbarer Inhaltsbereich
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.render_sections(self.sections_data)

    def render_sections(self, sections):
        # Bestehende Widgets entfernen
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        if not sections:
            no_res_box = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            no_res_box.pack(pady=40)
            ctk.CTkLabel(
                no_res_box,
                text="Keine passenden Themen gefunden.",
                font=ctk.CTkFont(size=16, weight="bold"),
            ).pack()
            ctk.CTkLabel(
                no_res_box,
                text="Versuchen Sie einen anderen Suchbegriff wie 'Text', 'Bild', 'Tabelle' oder 'Speichern'.",
                text_color="gray",
            ).pack(pady=5)
            return

        current_category = None
        for sec in sections:
            # Kategorie-Titel wenn neu
            if sec["category"] != current_category:
                current_category = sec["category"]
                cat_lbl = ctk.CTkLabel(
                    self.scroll_frame,
                    text=current_category,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#0d6efd",
                )
                cat_lbl.pack(anchor="w", pady=(15, 5), padx=5)

            # Karten-Box für jedes Thema
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            t_lbl = ctk.CTkLabel(card, text=sec["title"], font=ctk.CTkFont(size=15, weight="bold"))
            t_lbl.pack(anchor="w", padx=15, pady=(10, 5))

            c_lbl = ctk.CTkLabel(
                card,
                text=sec["content"],
                font=ctk.CTkFont(size=13),
                justify="left",
                anchor="w",
                wraplength=1000,
            )
            c_lbl.pack(anchor="w", padx=15, pady=(0, 12))

    def on_search(self, event=None):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.render_sections(self.sections_data)
            return

        filtered = []
        for sec in self.sections_data:
            match_title = query in sec["title"].lower()
            match_content = query in sec["content"].lower()
            match_category = query in sec["category"].lower()
            match_keywords = any(query in kw for kw in sec["keywords"])

            if match_title or match_content or match_category or match_keywords:
                filtered.append(sec)

        self.render_sections(filtered)

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.render_sections(self.sections_data)

    def export_pdf(self):
        """Exportiert das vollständige Benutzerhandbuch als saubere PDF-Datei (mit Fallback auf HTML)."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf"), ("HTML Document", "*.html")],
            initialfile="Benutzerhandbuch_Bootstrap_Editor.pdf",
            title="Handbuch speichern",
        )
        if not filepath:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                HRFlowable,
                Paragraph,
                SimpleDocTemplate,
                Spacer,
            )

            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Heading1"],
                fontSize=22,
                leading=26,
                textColor=colors.HexColor("#0d6efd"),
                spaceAfter=15,
            )

            category_style = ParagraphStyle(
                "CategoryHeader",
                parent=styles["Heading2"],
                fontSize=16,
                leading=20,
                textColor=colors.HexColor("#0d6efd"),
                spaceBefore=15,
                spaceAfter=8,
            )

            section_title_style = ParagraphStyle(
                "SectionTitle",
                parent=styles["Heading3"],
                fontSize=12,
                leading=16,
                textColor=colors.HexColor("#212529"),
                spaceBefore=8,
                spaceAfter=4,
            )

            body_style = ParagraphStyle(
                "BodyTextCustom",
                parent=styles["Normal"],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#333333"),
                spaceAfter=10,
            )

            story = []
            story.append(
                Paragraph(
                    "Benutzerhandbuch – Bootstrap 5 &amp; 3 Low-Code Editor",
                    title_style,
                )
            )
            story.append(
                Paragraph(
                    "Anleitung für Onlineshop-Betreiber zur Gestaltung von Artikelbeschreibungen &amp; Inhalten",
                    body_style,
                )
            )
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor("#0d6efd"),
                    spaceAfter=15,
                )
            )

            current_cat = None
            for sec in self.sections_data:
                if sec["category"] != current_cat:
                    current_cat = sec["category"]
                    story.append(Paragraph(current_cat, category_style))

                story.append(Paragraph(sec["title"], section_title_style))

                lines = sec["content"].split("\n")
                formatted_lines = []
                for line in lines:
                    safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    formatted_lines.append(safe_line)

                content_p = "<br/>".join(formatted_lines)
                story.append(Paragraph(content_p, body_style))
                story.append(Spacer(1, 0.2 * cm))

            doc.build(story)
            messagebox.showinfo(
                "PDF Export",
                f"Das Handbuch wurde erfolgreich als PDF gespeichert:\n{filepath}",
            )

        except ImportError:
            # Fallback falls reportlab nicht vorhanden ist
            html_filepath = filepath.replace(".pdf", ".html") if filepath.endswith(".pdf") else filepath + ".html"
            try:
                html_content = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Benutzerhandbuch - Bootstrap Editor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
        h1 { color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 10px; }
        h2 { color: #0d6efd; margin-top: 30px; }
        h3 { color: #212529; margin-top: 20px; }
        .card { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>Benutzerhandbuch – Bootstrap 5 & 3 Low-Code Editor</h1>
    <p>Anleitung für Onlineshop-Betreiber zur Gestaltung von Artikelbeschreibungen & Inhalten</p>
"""
                current_cat = None
                for sec in self.sections_data:
                    if sec["category"] != current_cat:
                        current_cat = sec["category"]
                        html_content += f"<h2>{current_cat}</h2>\n"

                    content_html = sec["content"].replace("\n", "<br>")
                    html_content += f"""<div class="card">
    <h3>{sec["title"]}</h3>
    <p>{content_html}</p>
</div>\n"""

                html_content += "</body>\n</html>"
                with open(html_filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                messagebox.showinfo(
                    "Handbuch Export",
                    f"Da 'reportlab' in der Umgebung fehlt, wurde das Handbuch als HTML-Dokument gespeichert:\n{html_filepath}",
                )
            except Exception as ex:
                messagebox.showerror(
                    "Fehler beim Export",
                    f"Handbuch konnte nicht gespeichert werden: {ex}",
                )
        except Exception as e:
            messagebox.showerror(
                "Fehler beim PDF Export",
                f"Die PDF-Datei konnte nicht erstellt werden:\n{e}",
            )


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            from version import __version__

            self.title(f"Bootstrap 5 Low-Code Editor - v{__version__}")
        except Exception:
            self.title("Bootstrap 5 Low-Code Editor")
        self.geometry("1400x800")
        apply_window_icon(self)

        self.page = Page("Mein Neues Projekt")
        self.preview_filepath = str((BASE_APP_DIR / ".preview.html").resolve())

        # Einstellungen laden
        self.settings_file = str((BASE_APP_DIR / "settings.json").resolve())
        self.settings = self.load_settings()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._build_ui()
        self.update_ui()

        # Verzögerte Wiederherstellung der PanedWindow Positionen
        self.after(100, self.restore_layout)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file) as f:
                    data = json.load(f)
                    sash1 = data.get("sash1", 220)
                    sash2 = data.get("sash2", 800)
                    return {"sash1": sash1, "sash2": sash2}
            except (json.JSONDecodeError, OSError):
                pass
        return {"sash1": 220, "sash2": 800}

    def save_settings(self):
        try:
            sash1 = self.main_paned.sash_coord(0)[0]
            sash2 = self.main_paned.sash_coord(1)[0]
            # Sicherstellen, dass keine extrem verschobenen Positionen gespeichert werden
            width = self.winfo_width()
            if width > 100:
                sash1 = max(150, min(sash1, width - 400))
                sash2 = max(sash1 + 200, min(sash2, width - 150))
            self.settings["sash1"] = sash1
            self.settings["sash2"] = sash2
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f)
        except (OSError, tk.TclError):
            pass

    def on_closing(self):
        self.save_settings()
        self.destroy()

    def _build_ui(self):
        self.main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6, bg="#777777")
        self.main_paned.pack(fill="both", expand=True)

        # --- LINKE SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self.main_paned, width=200, corner_radius=0)
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Werkzeuge", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="+ Neue Zeile / Spalten", command=self.add_column_row).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="+ Überschrift (H1-H6)", command=self.add_heading_row).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="+ Eigener HTML Code", command=self.add_html_row).pack(pady=10, padx=20)

        # Spacer
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="BS3 ➔ BS5 Konverter",
            fg_color="purple",
            hover_color="#4a148c",
            command=self.open_converter,
        ).pack(pady=10, padx=20)

        # Spacer
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="Projekt Speichern",
            fg_color="green",
            hover_color="darkgreen",
            command=self.save_project,
        ).pack(pady=10, padx=20)
        ctk.CTkButton(
            self.sidebar,
            text="Projekt Laden",
            fg_color="orange",
            hover_color="darkorange",
            command=self.load_project,
        ).pack(pady=10, padx=20)

        # Spacer
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="📖 Handbuch öffnen",
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self.open_help,
        ).pack(pady=10, padx=20)

        self.main_paned.add(self.sidebar)

        # --- MITTLERER BEREICH (Struktur) ---
        self.structure_container = ctk.CTkFrame(self.main_paned, corner_radius=0)
        self.structure_container.grid_rowconfigure(1, weight=1)
        self.structure_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.structure_container,
            text="Seitenstruktur",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, pady=10)

        self.structure_scroll = ctk.CTkScrollableFrame(self.structure_container)
        self.structure_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.main_paned.add(self.structure_container)

        # --- RECHTER BEREICH (Code & Vorschau Button) ---
        self.code_frame = ctk.CTkFrame(self.main_paned, corner_radius=0)
        self.code_frame.grid_rowconfigure(1, weight=1)
        self.code_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.code_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(5, 5), padx=5)

        # Zeile 1: Titel & Bootstrap-Version
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(2, 5))

        ctk.CTkLabel(top_row, text="Generierter HTML Code", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        ctk.CTkLabel(top_row, text="Version:").pack(side="left", padx=(15, 5))
        self.bs_version_var = ctk.StringVar(value="Bootstrap 5")
        self.bs_version_optionmenu = ctk.CTkOptionMenu(
            top_row,
            values=["Bootstrap 5", "Bootstrap 3"],
            variable=self.bs_version_var,
            width=120,
            command=lambda _: self.update_ui(),
        )
        self.bs_version_optionmenu.pack(side="left", padx=5)

        # Zeile 2: Aktions-Buttons
        btn_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=2)

        ctk.CTkButton(
            btn_row,
            text="Vorschau im Browser",
            command=self.launch_preview,
            fg_color="blue",
            hover_color="darkblue",
        ).pack(side="left", padx=4, expand=True, fill="x")
        ctk.CTkButton(
            btn_row,
            text="HTML Exportieren",
            command=self.export_html,
            fg_color="purple",
            hover_color="#4a148c",
        ).pack(side="left", padx=4, expand=True, fill="x")
        ctk.CTkButton(btn_row, text="Code Kopieren", command=self.copy_code).pack(
            side="left", padx=4, expand=True, fill="x"
        )

        self.code_textbox = ctk.CTkTextbox(self.code_frame, wrap="none", font=("Consolas", 12))
        self.code_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.code_textbox.configure(state="disabled")

        self.main_paned.add(self.code_frame)

        # --- FOOTER BEREICH ---
        import datetime

        current_year = datetime.datetime.now().year

        self.footer_frame = ctk.CTkFrame(self, height=35, corner_radius=0)
        self.footer_frame.pack(side="bottom", fill="x")

        # Links: Versionsnummer
        from version import __version__

        self.footer_left = ctk.CTkLabel(
            self.footer_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray",
        )
        self.footer_left.pack(side="left", padx=15, pady=5)

        # Mitte: Branding / Company Name
        company_name = f"© Agentur Schölzke {current_year}"
        company_url = "https://www.agentur-schoelzke.de"

        self.footer_brand = ctk.CTkLabel(
            self.footer_frame,
            text=company_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            cursor="hand2",
        )
        self.footer_brand.pack(side="left", expand=True, pady=5)
        self.footer_brand.bind("<Button-1>", lambda e: webbrowser.open(company_url))

        # Rechts: Spenden Button
        self.donate_btn = ctk.CTkButton(
            self.footer_frame,
            text="☕ Spenden (PayPal)",
            fg_color="#0070BA",
            hover_color="#005ea6",
            height=24,
            width=130,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: webbrowser.open("https://paypal.me/kaischoelzke"),
        )
        self.donate_btn.pack(side="right", padx=15, pady=5)

    def restore_layout(self):
        try:
            self.update_idletasks()
            total_width = self.winfo_width()
            if total_width <= 100:
                total_width = 1400

            # Mindestbreiten für die 3 Bereiche:
            min_sidebar = 200
            min_structure = 350
            min_code = 350

            sash1 = self.settings.get("sash1", 220)
            sash2 = self.settings.get("sash2", 800)

            # Korrigiere sash1 (Sidebar-Rechtsgrenze)
            sash1 = max(min_sidebar, min(sash1, total_width - (min_structure + min_code)))

            # Korrigiere sash2 (Struktur-Rechtsgrenze / Code-Linksgrenze)
            min_sash2 = sash1 + min_structure
            max_sash2 = total_width - min_code
            if min_sash2 < max_sash2:
                sash2 = max(min_sash2, min(sash2, max_sash2))
            else:
                sash2 = sash1 + ((total_width - sash1) // 2)

            self.main_paned.sash_place(0, int(sash1), 0)
            self.main_paned.sash_place(1, int(sash2), 0)
        except tk.TclError:
            pass

    # --- ACTIONS ---

    def open_converter(self):
        ConverterDialog(self)

    def add_column_row(self):
        dialog = ColumnLayoutDialog(self, title="Spaltenaufteilung")
        if dialog.result:
            self.add_row(dialog.result)

    def add_heading_row(self):
        dialog = MultilineTextInputDialog(self, title="Überschrift hinzufügen", default_tag="h1")
        text = dialog.result_text
        tag = dialog.result_tag
        if text:
            row = Row()
            col = Column(span=12)
            col.add_element(TextBlock(text=text, tag=tag))
            row.add_column(col)
            self.page.add_row(row)
            self.update_ui()

    def add_html_row(self):
        dialog = HtmlInputDialog(self, title="HTML-Code als eigenen Block hinzufügen")
        code = dialog.result_code
        if code:
            row = Row()
            col = Column(span=12)
            col.add_element(HtmlBlock(code=code))
            row.add_column(col)
            self.page.add_row(row)
            self.update_ui()

    def add_row(self, col_spans: list):
        row = Row()
        for span in col_spans:
            row.add_column(Column(span=span))
        self.page.add_row(row)
        self.update_ui()

    def add_text_to_col(self, col: Column):
        dialog = MultilineTextInputDialog(self, title="Text hinzufügen", default_tag="p")
        text = dialog.result_text
        tag = dialog.result_tag
        if text:
            col.add_element(TextBlock(text=text, tag=tag))
            self.update_ui()

    def add_heading_to_col(self, col: Column):
        dialog = MultilineTextInputDialog(self, title="Überschrift hinzufügen", default_tag="h2")
        text = dialog.result_text
        tag = dialog.result_tag
        if text:
            col.add_element(TextBlock(text=text, tag=tag))
            self.update_ui()

    def add_image_to_col(self, col: Column):
        dialog = ImageSelectionDialog(self, title="Bild hinzufügen")
        if dialog.result:
            col.add_element(ImageBlock(url=dialog.result))
            self.update_ui()

    def add_button_to_col(self, col: Column):
        dialog = ButtonSelectionDialog(self, title="Button hinzufügen")
        if dialog.result_text:
            col.add_element(
                ButtonBlock(
                    text=dialog.result_text,
                    url=dialog.result_url,
                    style=dialog.result_style,
                )
            )
            self.update_ui()

    def add_alert_to_col(self, col: Column):
        dialog = AlertSelectionDialog(self, title="Hinweisbox (Alert) hinzufügen")
        if dialog.result_text:
            col.add_element(AlertBlock(text=dialog.result_text, style=dialog.result_style))
            self.update_ui()

    def add_html_to_col(self, col: Column):
        dialog = HtmlInputDialog(self, title="HTML-Code hinzufügen")
        if dialog.result_code is not None:
            col.add_element(HtmlBlock(code=dialog.result_code))
            self.update_ui()

    def add_table_to_col(self, col: Column):
        dialog = TableDialog(self, title="Tabelle hinzufügen")
        if dialog.result_headers and dialog.result_rows:
            col.add_element(TableBlock(headers=dialog.result_headers, rows=dialog.result_rows))
            self.update_ui()

    def add_card_to_col(self, col: Column):
        dialog = CardDialog(self, title="Card / Panel hinzufügen")
        if dialog.result_title:
            col.add_element(
                CardBlock(
                    title=dialog.result_title,
                    content=dialog.result_content,
                    style=dialog.result_style,
                )
            )
            self.update_ui()

    def add_badge_to_col(self, col: Column):
        dialog = BadgeDialog(self, title="Badge / Label hinzufügen")
        if dialog.result_text:
            col.add_element(BadgeBlock(text=dialog.result_text, style=dialog.result_style))
            self.update_ui()

    def add_listgroup_to_col(self, col: Column):
        dialog = ListGroupDialog(self, title="List Group hinzufügen")
        if dialog.result_items:
            col.add_element(ListGroupBlock(items=dialog.result_items))
            self.update_ui()

    def add_accordion_to_col(self, col: Column):
        dialog = AccordionDialog(self, title="Akkordeon hinzufügen")
        if dialog.result_items:
            col.add_element(AccordionBlock(items=dialog.result_items))
            self.update_ui()

    def add_form_input_to_col(self, col: Column):
        dialog = FormInputDialog(self, title="Formularfeld hinzufügen")
        if dialog.result_label:
            col.add_element(
                FormInputBlock(
                    label=dialog.result_label,
                    input_type=dialog.result_type,
                    placeholder=dialog.result_placeholder,
                    help_text=dialog.result_help,
                )
            )
            self.update_ui()

    def add_navbar_to_col(self, col: Column):
        dialog = NavbarDialog(self, title="Navigationsleiste hinzufügen")
        if dialog.result_brand:
            col.add_element(
                NavbarBlock(
                    brand=dialog.result_brand,
                    bg_style=dialog.result_bg,
                    links=dialog.result_links,
                )
            )
            self.update_ui()

    def show_add_element_menu(self, col: Column, widget):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="📝 Text", command=lambda: self.add_text_to_col(col))
        menu.add_command(label="📌 Überschrift", command=lambda: self.add_heading_to_col(col))
        menu.add_command(label="🖼️ Bild", command=lambda: self.add_image_to_col(col))
        menu.add_command(label="🔘 Button", command=lambda: self.add_button_to_col(col))
        menu.add_command(label="⚠️ Hinweisbox (Alert)", command=lambda: self.add_alert_to_col(col))
        menu.add_separator()
        menu.add_command(label="📊 Tabelle", command=lambda: self.add_table_to_col(col))
        menu.add_command(label="🎴 Card / Panel", command=lambda: self.add_card_to_col(col))
        menu.add_command(label="🏷️ Badge / Label", command=lambda: self.add_badge_to_col(col))
        menu.add_command(
            label="📋 List Group (Liste)",
            command=lambda: self.add_listgroup_to_col(col),
        )
        menu.add_command(label="🗂️ Akkordeon", command=lambda: self.add_accordion_to_col(col))
        menu.add_separator()
        menu.add_command(
            label="📝 Formularfeld (Input)",
            command=lambda: self.add_form_input_to_col(col),
        )
        menu.add_command(
            label="🧭 Navigationsleiste (Navbar)",
            command=lambda: self.add_navbar_to_col(col),
        )
        menu.add_separator()
        menu.add_command(label="💻 Eigener HTML Code", command=lambda: self.add_html_to_col(col))

        # Position berechnen
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        menu.tk_popup(x, y)

    def edit_element(self, element: Element):
        if isinstance(element, TextBlock):
            title = "Überschrift bearbeiten" if element.tag.startswith("h") else "Text bearbeiten"
            dialog = MultilineTextInputDialog(self, title=title, default_tag=element.tag)
            if dialog.result_text is not None:
                element.text = dialog.result_text
                element.tag = dialog.result_tag
                self.update_ui()
        elif isinstance(element, ImageBlock):
            dialog = ImageSelectionDialog(self, title="Bild bearbeiten")
            if dialog.result:
                element.url = dialog.result
                self.update_ui()
        elif isinstance(element, ButtonBlock):
            dialog = ButtonSelectionDialog(
                self,
                title="Button bearbeiten",
                default_text=element.text,
                default_url=element.url,
                default_style=element.style,
            )
            if dialog.result_text is not None:
                element.text = dialog.result_text
                element.url = dialog.result_url
                element.style = dialog.result_style
                self.update_ui()
        elif isinstance(element, AlertBlock):
            dialog = AlertSelectionDialog(
                self,
                title="Hinweisbox bearbeiten",
                default_text=element.text,
                default_style=element.style,
            )
            if dialog.result_text is not None:
                element.text = dialog.result_text
                element.style = dialog.result_style
                self.update_ui()
        elif isinstance(element, HtmlBlock):
            dialog = HtmlInputDialog(self, title="HTML-Code bearbeiten", default_code=element.code)
            if dialog.result_code is not None:
                element.code = dialog.result_code
                self.update_ui()
        elif isinstance(element, TableBlock):
            rows_str = "\n".join([HTMLConverter.format_table_line(r) for r in element.rows])
            dialog = TableDialog(
                self,
                title="Tabelle bearbeiten",
                default_headers=element.headers,
                default_rows_text=rows_str,
            )
            if dialog.result_headers and dialog.result_rows:
                element.headers = dialog.result_headers
                element.rows = dialog.result_rows
                self.update_ui()
        elif isinstance(element, CardBlock):
            dialog = CardDialog(
                self,
                title="Card / Panel bearbeiten",
                default_title=element.title,
                default_content=element.content,
                default_style=element.style,
            )
            if dialog.result_title is not None:
                element.title = dialog.result_title
                element.content = dialog.result_content
                element.style = dialog.result_style
                self.update_ui()
        elif isinstance(element, BadgeBlock):
            dialog = BadgeDialog(
                self,
                title="Badge / Label bearbeiten",
                default_text=element.text,
                default_style=element.style,
            )
            if dialog.result_text is not None:
                element.text = dialog.result_text
                element.style = dialog.result_style
                self.update_ui()
        elif isinstance(element, ListGroupBlock):
            items_str = "\n".join(element.items)
            dialog = ListGroupDialog(self, title="List Group bearbeiten", default_items_text=items_str)
            if dialog.result_items is not None:
                element.items = dialog.result_items
                self.update_ui()
        elif isinstance(element, AccordionBlock):
            dialog = AccordionDialog(self, title="Akkordeon bearbeiten", default_items=element.items)
            if dialog.result_items is not None:
                element.items = dialog.result_items
                self.update_ui()
        elif isinstance(element, FormInputBlock):
            dialog = FormInputDialog(
                self,
                title="Formularfeld bearbeiten",
                default_label=element.label,
                default_type=element.input_type,
                default_placeholder=element.placeholder,
                default_help=element.help_text,
            )
            if dialog.result_label is not None:
                element.label = dialog.result_label
                element.input_type = dialog.result_type
                element.placeholder = dialog.result_placeholder
                element.help_text = dialog.result_help
                self.update_ui()
        elif isinstance(element, NavbarBlock):
            links_str = "\n".join([f"{link.get('text', '')} | {link.get('url', '#')}" for link in element.links])
            dialog = NavbarDialog(
                self,
                title="Navigationsleiste bearbeiten",
                default_brand=element.brand,
                default_bg=element.bg_style,
                default_links_text=links_str,
            )
            if dialog.result_brand is not None:
                element.brand = dialog.result_brand
                element.bg_style = dialog.result_bg
                element.links = dialog.result_links
                self.update_ui()

    def edit_element_spacing(self, element: Element):
        dialog = ElementSpacingDialog(self, element=element)
        if dialog.saved:
            self.update_ui()

    def export_html(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML-Datei", "*.html")])
        if not filepath:
            return
        version = self.get_bs_version()
        html_code = HTMLGenerator.generate_html(self.page, bootstrap_version=version)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_code)
            messagebox.showinfo(
                "Export Erfolgreich",
                f"Die HTML-Datei wurde erfolgreich gespeichert unter:\n{filepath}",
            )
        except Exception as e:
            messagebox.showerror("Fehler beim Export", f"Datei konnte nicht gespeichert werden: {e}")

    def remove_element(self, parent_col: Column, element_id: str):
        parent_col.remove_element(element_id)
        self.update_ui()

    def move_element_up(self, parent_col: Column, element_id: str):
        parent_col.move_element_up(element_id)
        self.update_ui()

    def move_element_down(self, parent_col: Column, element_id: str):
        parent_col.move_element_down(element_id)
        self.update_ui()

    def move_row_up(self, row_id: str):
        self.page.move_row_up(row_id)
        self.update_ui()

    def move_row_down(self, row_id: str):
        self.page.move_row_down(row_id)
        self.update_ui()

    def remove_row(self, row_id: str):
        self.page.remove_row(row_id)
        self.update_ui()

    def get_bs_version(self) -> str:
        return "3" if "3" in self.bs_version_var.get() else "5"

    def copy_code(self):
        version = self.get_bs_version()
        html = self.page.render(version=version)
        self.clipboard_clear()
        self.clipboard_append(html)
        self.update()
        messagebox.showinfo(
            "Kopiert",
            f"Der generierte Bootstrap {version} Content-Code wurde in die Zwischenablage kopiert.",
        )

    def update_ui(self):
        """Aktualisiert die Struktur-Ansicht und die Vorschau."""
        # 1. Struktur Ansicht neu aufbauen
        for widget in self.structure_scroll.winfo_children():
            widget.destroy()

        for r_idx, row in enumerate(self.page.rows):
            row_frame = ctk.CTkFrame(
                self.structure_scroll,
                fg_color="#e0e0e0",
                border_width=1,
                border_color="gray",
            )
            row_frame.pack(fill="x", pady=5, padx=5)

            # Row Header
            row_header = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_header.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row_header, text=f"Zeile {r_idx+1}", text_color="black").pack(side="left")

            btn_frame_row = ctk.CTkFrame(row_header, fg_color="transparent")
            btn_frame_row.pack(side="right")
            ctk.CTkButton(
                btn_frame_row,
                text="↑",
                width=30,
                height=20,
                fg_color="gray",
                command=lambda r_id=row.id: self.move_row_up(r_id),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_frame_row,
                text="↓",
                width=30,
                height=20,
                fg_color="gray",
                command=lambda r_id=row.id: self.move_row_down(r_id),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_frame_row,
                text="X",
                width=30,
                height=20,
                fg_color="red",
                hover_color="darkred",
                command=lambda r_id=row.id: self.remove_row(r_id),
            ).pack(side="left", padx=2)

            # Columns container
            cols_container = ctk.CTkFrame(row_frame, fg_color="transparent")
            cols_container.pack(fill="x", padx=5, pady=5)

            for col in row.columns:
                col_frame = ctk.CTkFrame(cols_container, fg_color="#f0f0f0", border_width=1)
                col_frame.pack(side="left", fill="both", expand=True, padx=2)

                ctk.CTkLabel(
                    col_frame,
                    text=f"col-{col.span}",
                    text_color="gray",
                    font=("Arial", 10),
                ).pack(pady=2)

                # Render Elements in Column
                for el in col.elements:
                    el_frame = ctk.CTkFrame(col_frame, fg_color="white", corner_radius=5)
                    el_frame.pack(fill="x", padx=5, pady=2)

                    if isinstance(el, TextBlock):
                        display_text = el.text[:20] + "..." if len(el.text) > 20 else el.text
                        ctk.CTkLabel(
                            el_frame,
                            text=f"{el.tag.upper()}: {display_text}",
                            text_color="black",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, ImageBlock):
                        ctk.CTkLabel(el_frame, text="[Bild]", text_color="blue").pack(side="left", padx=5)
                    elif isinstance(el, ButtonBlock):
                        display_text = el.text[:15] + "..." if len(el.text) > 15 else el.text
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Btn:{el.style}] {display_text}",
                            text_color="darkgreen",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, AlertBlock):
                        display_text = el.text[:15] + "..." if len(el.text) > 15 else el.text
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Alert:{el.style}] {display_text}",
                            text_color="darkorange",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, HtmlBlock):
                        display_text = (
                            el.code.strip().replace("\n", " ")[:15] + "..."
                            if len(el.code.strip()) > 15
                            else el.code.strip()
                        )
                        ctk.CTkLabel(el_frame, text=f"[HTML] {display_text}", text_color="purple").pack(
                            side="left", padx=5
                        )
                    elif isinstance(el, TableBlock):
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Tabelle] ({len(el.headers)} Spalten)",
                            text_color="#006699",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, CardBlock):
                        display_text = el.title[:15] + "..." if len(el.title) > 15 else el.title
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Card] {display_text}",
                            text_color="#880088",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, BadgeBlock):
                        ctk.CTkLabel(el_frame, text=f"[Badge] {el.text}", text_color="#008888").pack(
                            side="left", padx=5
                        )
                    elif isinstance(el, AccordionBlock):
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Akkordeon] ({len(el.items)} Elemente)",
                            text_color="#666600",
                        ).pack(side="left", padx=5)
                    elif isinstance(el, ListGroupBlock):
                        ctk.CTkLabel(
                            el_frame,
                            text=f"[Liste] ({len(el.items)} Einträge)",
                            text_color="#444444",
                        ).pack(side="left", padx=5)

                    btn_actions_frame = ctk.CTkFrame(el_frame, fg_color="transparent")
                    btn_actions_frame.pack(side="right", padx=2, pady=2)

                    ctk.CTkButton(
                        btn_actions_frame,
                        text="✎",
                        width=20,
                        height=20,
                        fg_color="blue",
                        hover_color="darkblue",
                        command=lambda elem=el: self.edit_element(elem),
                    ).pack(side="left", padx=1)
                    ctk.CTkButton(
                        btn_actions_frame,
                        text="⇕",
                        width=20,
                        height=20,
                        fg_color="purple",
                        hover_color="#4a148c",
                        command=lambda elem=el: self.edit_element_spacing(elem),
                    ).pack(side="left", padx=1)
                    ctk.CTkButton(
                        btn_actions_frame,
                        text="↑",
                        width=20,
                        height=20,
                        fg_color="gray",
                        command=lambda c=col, e_id=el.id: self.move_element_up(c, e_id),
                    ).pack(side="left", padx=1)
                    ctk.CTkButton(
                        btn_actions_frame,
                        text="↓",
                        width=20,
                        height=20,
                        fg_color="gray",
                        command=lambda c=col, e_id=el.id: self.move_element_down(c, e_id),
                    ).pack(side="left", padx=1)
                    ctk.CTkButton(
                        btn_actions_frame,
                        text="x",
                        width=20,
                        height=20,
                        fg_color="red",
                        command=lambda c=col, e_id=el.id: self.remove_element(c, e_id),
                    ).pack(side="left", padx=1)

                # Add Menu for Column
                btn_frame = ctk.CTkFrame(col_frame, fg_color="transparent")
                btn_frame.pack(pady=5)

                add_menu_btn = ctk.CTkButton(
                    btn_frame,
                    text="+ Element ▾",
                    width=100,
                    height=24,
                    fg_color="#1f538d",
                    hover_color="#14375e",
                    command=lambda c=col, btn_widget=btn_frame: self.show_add_element_menu(c, btn_widget),
                )
                add_menu_btn.pack(side="left", padx=2)

        # 2. HTML Code aktualisieren
        version = self.get_bs_version()
        html_code = HTMLGenerator.generate_html(self.page, bootstrap_version=version)
        self.code_textbox.configure(state="normal")
        self.code_textbox.delete("1.0", "end")
        self.code_textbox.insert("1.0", html_code)
        self.code_textbox.configure(state="disabled")

        # 3. WebView Datei (.preview.html) aktualisieren für den externen Prozess
        try:
            with open(self.preview_filepath, "w", encoding="utf-8") as f:
                f.write(html_code)
        except Exception as e:
            print("Fehler beim Schreiben der Preview-Datei:", e)

    # --- PREVIEW ---
    def launch_preview(self):
        """Öffnet die Vorschau im Standard-Browser des Systems (erzwingt Webbrowser)."""
        version = self.get_bs_version()
        html_code = HTMLGenerator.generate_html(self.page, bootstrap_version=version)
        try:
            with open(self.preview_filepath, "w", encoding="utf-8") as f:
                f.write(html_code)

            # Versuche explizit einen echten Webbrowser zu finden, um IDEs wie DreamWeaver zu umgehen
            preview_uri = Path(self.preview_filepath).resolve().as_uri()
            browser_opened = False
            if sys.platform == "win32":
                for b_name in ["chrome", "msedge", "edge", "firefox"]:
                    try:
                        browser = webbrowser.get(b_name)
                        # webbrowser.get() prüft nicht immer, ob er existiert, daher fangen wir Fehler ab
                        browser.open(preview_uri)
                        browser_opened = True
                        break
                    except webbrowser.Error:
                        continue

            if not browser_opened:
                webbrowser.open(preview_uri)

        except Exception as e:
            messagebox.showerror("Fehler", f"Vorschau konnte nicht gestartet werden:\n{e}")

    # --- SPEICHERN & LADEN (Security) ---
    def save_project(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Project", "*.enc")])
        if not filepath:
            return

        dialog = ctk.CTkInputDialog(text="Master-Passwort eingeben:", title="Passwort")
        password = dialog.get_input()
        if not password:
            messagebox.showwarning("Abbruch", "Ohne Passwort kann nicht gespeichert werden.")
            return

        try:
            data_dict = self.page.to_dict()
            encrypted_bytes = security.encrypt_project(data_dict, password)
            with open(filepath, "wb") as f:
                f.write(encrypted_bytes)
            messagebox.showinfo("Erfolg", "Projekt erfolgreich verschlüsselt gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def load_project(self):
        filepath = filedialog.askopenfilename(filetypes=[("Encrypted Project", "*.enc")])
        if not filepath:
            return

        dialog = ctk.CTkInputDialog(text="Master-Passwort eingeben:", title="Passwort")
        password = dialog.get_input()
        if not password:
            return

        try:
            with open(filepath, "rb") as f:
                encrypted_bytes = f.read()
            data_dict = security.decrypt_project(encrypted_bytes, password)
            self.page = Page.from_dict(data_dict)
            self.update_ui()
            messagebox.showinfo("Erfolg", "Projekt erfolgreich geladen und entschlüsselt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Entschlüsselung fehlgeschlagen: {e}")

    def open_help(self):
        HelpDialog(self)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MainApplication()
    app.mainloop()
