import os
import sys
from unittest.mock import MagicMock, mock_open, patch

import security
from gui import (
    MainApplication,
    apply_window_icon,
    get_resource_path,
)
from models import Column, Page, Row, TextBlock


def test_get_resource_path_standard():
    path = get_resource_path("favicon.ico")
    assert isinstance(path, str)
    assert path.endswith("favicon.ico")
    assert os.path.isabs(path)


def test_get_resource_path_meipass(monkeypatch):
    dummy_meipass = r"C:\fake\meipass"
    monkeypatch.setattr(sys, "_MEIPASS", dummy_meipass, raising=False)
    path = get_resource_path("test_asset.png")
    assert path == os.path.join(dummy_meipass, "test_asset.png")


def test_apply_window_icon():
    mock_window = MagicMock()
    # Test ohne Fehler
    apply_window_icon(mock_window)
    assert mock_window.iconbitmap.called or mock_window.iconphoto.called


def _create_headless_app():
    """Erstellt ein Mock-Objekt der MainApplication für Headless-Tests der Controller-Logik."""
    app = MagicMock(spec=MainApplication)
    app.page = Page(title="Testseite")
    app.get_bs_version = MagicMock(return_value="5")
    app.update_ui = MagicMock()
    return app


def test_gui_row_and_element_manipulation():
    app = _create_headless_app()
    row1 = Row(element_id="row-1")
    row2 = Row(element_id="row-2")
    col = Column(span=12, element_id="col-1")
    elem1 = TextBlock(text="Text 1", element_id="el-1")
    elem2 = TextBlock(text="Text 2", element_id="el-2")

    col.add_element(elem1)
    col.add_element(elem2)
    row1.add_column(col)
    app.page.add_row(row1)
    app.page.add_row(row2)

    assert app.page.rows[0].id == "row-1"

    # Reihen verschieben
    MainApplication.move_row_down(app, "row-1")
    assert app.page.rows[0].id == "row-2"
    app.update_ui.assert_called()

    MainApplication.move_row_up(app, "row-1")
    assert app.page.rows[0].id == "row-1"

    # Elemente verschieben
    MainApplication.move_element_down(app, col, "el-1")
    assert col.elements[0].id == "el-2"

    MainApplication.move_element_up(app, col, "el-1")
    assert col.elements[0].id == "el-1"

    # Element und Zeile entfernen
    MainApplication.remove_element(app, col, "el-1")
    assert len(col.elements) == 1
    assert col.elements[0].id == "el-2"

    MainApplication.remove_row(app, "row-2")
    assert len(app.page.rows) == 1


def test_gui_export_html_success():
    app = _create_headless_app()
    row = Row()
    col = Column(span=12)
    col.add_element(TextBlock(text="Hallo Welt"))
    row.add_column(col)
    app.page.add_row(row)

    fake_file_content = {}

    def mock_write(path, mode="r", encoding="utf-8"):
        class FakeFile:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def write(self, text):
                fake_file_content["content"] = text

        return FakeFile()

    with (
        patch("gui.filedialog.asksaveasfilename", return_value="C:/fake/export.html"),
        patch("builtins.open", side_effect=mock_write),
        patch("gui.messagebox.showinfo") as mock_info,
    ):
        MainApplication.export_html(app)
        mock_info.assert_called_once()
        assert "Hallo Welt" in fake_file_content.get("content", "")


def test_gui_save_and_load_project_encrypted():
    app = _create_headless_app()
    row = Row()
    col = Column(span=12)
    col.add_element(TextBlock(text="Geheimer Text"))
    row.add_column(col)
    app.page.add_row(row)

    saved_bytes = {}

    def fake_open_write(path, mode="wb"):
        class FakeBinaryFile:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def write(self, b):
                saved_bytes["data"] = b

        return FakeBinaryFile()

    # 1. Speichern testen
    with (
        patch("gui.filedialog.asksaveasfilename", return_value="C:/fake/proj.enc"),
        patch("gui.ctk.CTkInputDialog") as mock_input_dlg,
        patch("builtins.open", side_effect=fake_open_write),
        patch("gui.messagebox.showinfo") as mock_info,
    ):
        mock_input_dlg.return_value.get_input.return_value = "TestPass123!"
        MainApplication.save_project(app)
        mock_info.assert_called_once()

    assert "data" in saved_bytes
    assert saved_bytes["data"].startswith(security.GCM_MAGIC_HEADER)

    # 2. Laden testen
    app.page = Page(title="Vor Dem Laden")

    with (
        patch("gui.filedialog.askopenfilename", return_value="C:/fake/proj.enc"),
        patch("gui.ctk.CTkInputDialog") as mock_input_dlg,
        patch("builtins.open", mock_open(read_data=saved_bytes["data"])),
        patch("gui.messagebox.showinfo") as mock_info,
    ):
        mock_input_dlg.return_value.get_input.return_value = "TestPass123!"
        MainApplication.load_project(app)
        mock_info.assert_called_once()
        assert len(app.page.rows) == 1
        assert app.page.rows[0].columns[0].elements[0].text == "Geheimer Text"


def test_gui_load_project_wrong_password():
    app = _create_headless_app()
    dummy_encrypted = security.encrypt_project({"title": "Test"}, "RichtigesPasswort")

    with (
        patch("gui.filedialog.askopenfilename", return_value="C:/fake/proj.enc"),
        patch("gui.ctk.CTkInputDialog") as mock_input_dlg,
        patch("builtins.open", mock_open(read_data=dummy_encrypted)),
        patch("gui.messagebox.showerror") as mock_error,
    ):
        mock_input_dlg.return_value.get_input.return_value = "FalschesPasswort"
        MainApplication.load_project(app)
        mock_error.assert_called_once()
