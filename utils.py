import sys
import os

def resource_path(relative_path):
    """
    Funktioniert im Dev-Modus und im PyInstaller-Bundle
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)