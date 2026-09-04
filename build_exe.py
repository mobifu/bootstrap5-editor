import os
import re
import shutil
import subprocess
import sys
import zipfile

from PIL import Image


def log_step(msg):
    print("\n==================================================")
    print(f"[BUILD] {msg}")
    print("==================================================")


def run_cmd(cmd_args: list[str], check: bool = True):
    print(f"> Running: {' '.join(cmd_args)}")
    res = subprocess.run(cmd_args, shell=False)
    if check and res.returncode != 0:
        print(f"[FEHLER] Befehl fehlgeschlagen mit Exit-Code {res.returncode}")
        sys.exit(res.returncode)


def get_current_version() -> str:
    version_file = os.path.abspath("version.py")
    if os.path.exists(version_file):
        with open(version_file, encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    return "1.0.0"


def bump_version_prompt() -> str:
    current_ver = get_current_version()
    print(f"\nAktuelle Version: {current_ver}")
    print("Möchtest du die Version vor dem Build anpassen?")
    print("1: Nicht ändern")
    print("2: Patch-Release (z.B. 1.0.0 -> 1.0.1)")
    print("3: Minor-Release (z.B. 1.0.0 -> 1.1.0)")
    print("4: Major-Release (z.B. 1.0.0 -> 2.0.0)")
    print("5: Manuelle Eingabe")

    # In nicht-interaktiven Umgebungen oder Standard-Build
    if not sys.stdin.isatty():
        print("> Automatische Ausführung im non-interactive Modus. Behalte Version bei.")
        return current_ver

    choice = input("Auswahl [1-5] (Standard 1): ").strip() or "1"
    parts = [int(p) for p in current_ver.split(".")]
    while len(parts) < 3:
        parts.append(0)

    if choice == "2":
        parts[2] += 1
        new_ver = f"{parts[0]}.{parts[1]}.{parts[2]}"
    elif choice == "3":
        parts[1] += 1
        parts[2] = 0
        new_ver = f"{parts[0]}.{parts[1]}.{parts[2]}"
    elif choice == "4":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
        new_ver = f"{parts[0]}.{parts[1]}.{parts[2]}"
    elif choice == "5":
        new_ver = input("Gib die neue Versionsnummer ein (z.B. 1.2.3): ").strip()
    else:
        new_ver = current_ver

    if new_ver != current_ver:
        version_file = os.path.abspath("version.py")
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(f'__version__ = "{new_ver}"\n')
        print(f"[VERSION] Version aktualisiert auf v{new_ver}")

    return new_ver


def create_zip_archive(source_dir: str, output_zip_path: str):
    print(f"> Erstelle ZIP-Archiv: {output_zip_path} ...")
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
    print(f"[ERFOLG] ZIP-Archiv erstellt: {output_zip_path}")


def main():
    log_step("0. Versionsprüfung & Aktualisierung")
    version = bump_version_prompt()

    log_step("1. Sicherheits- & Qualitätsprüfung (Ruff, Pytest & Bandit)")
    # 1. Ruff Code-Analyse
    print("> Starte Ruff Code-Analyse...")
    ruff_res = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select=E,F,W",
            "--ignore=E501,W293",
            ".",
        ],
        shell=False,
    )
    if ruff_res.returncode != 0:
        print("[FEHLER] Ruff hat Syntax- oder schwere Code-Fehler festgestellt! Build wird abgebrochen.")
        sys.exit(1)

    # 2. Pytest Unit-Tests
    print("> Starte Pytest Unit-Tests...")
    test_res = subprocess.run([sys.executable, "-m", "pytest"], shell=False)
    if test_res.returncode != 0:
        print("[FEHLER] Unit-Tests fehlgeschlagen! Build wird abgebrochen.")
        sys.exit(1)

    # 3. Bandit Security Audit
    print("> Starte Bandit Sicherheitsanalyse...")
    audit_res = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", ".", "-x", "./.venv,./build,./dist,./build_staging,./test_*.py", "-ll"],
        shell=False,
    )
    if audit_res.returncode != 0:
        print("[FEHLER] Bandit hat kritische Sicherheitslücken gemeldet! Build wird abgebrochen.")
        sys.exit(1)

    log_step("2. Code-Verschleierung & Vorbereitung")
    build_staging = os.path.abspath("build_staging")
    if os.path.exists(build_staging):
        shutil.rmtree(build_staging)
    os.makedirs(build_staging)

    # Relevante Dateien kopieren
    files_to_copy = [
        "app.py",
        "gui.py",
        "models.py",
        "generator.py",
        "security.py",
        "version.py",
        "favicon.ico",
        "android-chrome-512x512.png",
        "help.html",
    ]
    for fname in files_to_copy:
        if os.path.exists(fname):
            shutil.copy(fname, os.path.join(build_staging, fname))

    log_step("3. Executable-Build (PyInstaller oder Nuitka)")
    dist_dir = os.path.abspath("dist")

    ico_staging = os.path.join(build_staging, "favicon.ico")
    png_staging = os.path.join(build_staging, "android-chrome-512x512.png")
    help_staging = os.path.join(build_staging, "help.html")

    # Erzeuge vollwertiges Multi-Resolution Windows ICO
    icon_to_use = os.path.join(build_staging, "favicon.ico")
    if os.path.exists(png_staging):
        try:
            multi_ico = os.path.join(build_staging, "app_icon.ico")
            img = Image.open(png_staging)
            img.save(
                multi_ico,
                format="ICO",
                sizes=[
                    (16, 16),
                    (24, 24),
                    (32, 32),
                    (48, 48),
                    (64, 64),
                    (128, 128),
                    (256, 256),
                ],
            )
            icon_to_use = multi_ico
        except Exception as e:
            print(f"[HINWEIS] Konnte Multi-Res ICO nicht erstellen: {e}")

    # Build-Tool Ausführen (PyInstaller vs. Nuitka)
    use_nuitka = "--nuitka" in sys.argv

    if use_nuitka:
        print("> Verwende Nuitka für den Build...")
        nuitka_cmd = [
            sys.executable,
            "-m",
            "nuitka",
            "--standalone",
            "--windows-disable-console",
            "--enable-plugin=tk-inter",
            "--output-dir=" + dist_dir,
            "--output-filename=BootstrapEditor.exe",
            "--windows-icon-from-ico=" + icon_to_use,
            # Nuitka Inclusions
            "--include-package=customtkinter",
            "--include-package=cryptography",
            "--include-package=reportlab",
            f"--include-data-files={ico_staging}=./favicon.ico",
            f"--include-data-files={png_staging}=./android-chrome-512x512.png",
            f"--include-data-files={help_staging}=./help.html",
            "--assume-yes-for-downloads",
            os.path.join(build_staging, "app.py"),
        ]
        run_cmd(nuitka_cmd)
        target_dist_folder = os.path.join(dist_dir, "app.dist")
        if os.path.exists(target_dist_folder):
            final_dist_folder = os.path.join(dist_dir, "BootstrapEditor")
            if os.path.exists(final_dist_folder):
                shutil.rmtree(final_dist_folder)
            os.rename(target_dist_folder, final_dist_folder)
        target_dist_folder = final_dist_folder
    else:
        print("> Verwende PyInstaller für den Build (schneller Start & aufgeräumte Ordnerstruktur)...")
        pyinstaller_cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onedir",
            "--windowed",
            "--name",
            "BootstrapEditor",
            "--clean",
            "--icon",
            icon_to_use,
            "--contents-directory",
            "_internal",
        ]

        if os.path.exists(ico_staging):
            pyinstaller_cmd.extend(["--add-data", f"{ico_staging};."])
        if os.path.exists(png_staging):
            pyinstaller_cmd.extend(["--add-data", f"{png_staging};."])
        if os.path.exists(help_staging):
            pyinstaller_cmd.extend(["--add-data", f"{help_staging};."])

        pyinstaller_cmd.append(os.path.join(build_staging, "app.py"))
        run_cmd(pyinstaller_cmd)
        target_dist_folder = os.path.join(dist_dir, "BootstrapEditor")

    log_step("4. ZIP-Variante der Release-Dateien erstellen")
    zip_filename = os.path.join(dist_dir, f"BootstrapEditor_v{version}.zip")
    if os.path.exists(target_dist_folder):
        create_zip_archive(target_dist_folder, zip_filename)

    log_step("5. Fertigstellung & Überprüfung")
    exe_path = os.path.join(target_dist_folder, "BootstrapEditor.exe")
    if os.path.exists(exe_path):
        print(f"\n[ERFOLG] Die Executable wurde erfolgreich erstellt unter:\n{exe_path}")
        if os.path.exists(zip_filename):
            print(f"[ERFOLG] Die ZIP-Variante wurde erfolgreich erstellt unter:\n{zip_filename}\n")
    else:
        print("\n[FEHLER] Die .exe Datei konnte nicht gefunden werden!")
        sys.exit(1)


if __name__ == "__main__":
    main()
