import customtkinter as ctk

from gui import MainApplication


def main():
    """
    Haupt-Einstiegspunkt für den Bootstrap 5 Low-Code Editor.
    Startet das CustomTkinter GUI.
    """
    # Globale Theme-Einstellungen
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    # App instanziieren und starten
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
