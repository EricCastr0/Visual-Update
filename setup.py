import sys
from cx_Freeze import setup, Executable

# Dependências extras
build_exe_options = {
    "packages": ["os", "tkinter", "customtkinter", "pyodbc", "socket", "winreg"],
    "include_files": [],
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Ferramenta Visual de Update de Banco de Dados",
    version="1.0",
    description="Ferramenta visual para manipulação segura de bancos SQL Server",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base, target_name="IdeiaDB.exe")],
) 