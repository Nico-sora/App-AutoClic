import subprocess
import sys
import os

def build():
    root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(root, "src", "main.py")
    icon_path = os.path.join(root, "assets", "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "AutoClic",
        "--add-data", f"assets;assets",
    ]

    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    cmd.append(main_script)

    print("Ejecutando:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\nBuild completado. Ejecutable en: dist/AutoClic.exe")


if __name__ == "__main__":
    build()
