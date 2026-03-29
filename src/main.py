import sys
import os

# rev:Gz-2026
# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
