"""Tests für den Anwendungs-Einstiegspunkt app.py."""

import runpy
from unittest.mock import MagicMock, patch

import app


def test_main_initialization_and_run():
    """Prüft, ob main() die Theme-Konfiguration vornimmt und die GUI startet."""
    with (
        patch("app.ctk.set_appearance_mode") as mock_set_mode,
        patch("app.ctk.set_default_color_theme") as mock_set_theme,
        patch("app.MainApplication") as mock_app_class,
    ):
        mock_instance = MagicMock()
        mock_app_class.return_value = mock_instance

        app.main()

        mock_set_mode.assert_called_once_with("System")
        mock_set_theme.assert_called_once_with("blue")
        mock_app_class.assert_called_once()
        mock_instance.mainloop.assert_called_once()


def test_app_main_module_execution():
    """Prüft den Aufruf bei direkter Modulausführung als __main__ mit gemockter GUI."""
    with (
        patch("gui.MainApplication") as mock_app_class,
        patch("customtkinter.set_appearance_mode"),
        patch("customtkinter.set_default_color_theme"),
    ):
        mock_instance = MagicMock()
        mock_app_class.return_value = mock_instance
        runpy.run_module("app", run_name="__main__")
        mock_app_class.assert_called_once()
        mock_instance.mainloop.assert_called_once()
