# PyInstaller spec for nPhoneKIT Windows --onefile build.
# Invoked as: pyinstaller --clean --noconfirm packaging/nPhoneKIT.spec
import os

from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

# main.py is loaded via runpy from launcher.py, so PyInstaller's static
# analysis of launcher.py does not see PyQt5. collect_all pulls in every
# PyQt5 submodule plus its Qt DLLs, plugins (platforms/qwindows.dll is
# required for any Qt5 app on Windows) and translation files.
pyqt5_datas, pyqt5_binaries, pyqt5_hiddenimports = collect_all("PyQt5")

datas = [
    (os.path.join(ROOT, "main.py"), "."),
    (os.path.join(ROOT, "settings.json"), "."),
    (os.path.join(ROOT, "strings.xml"), "."),
    (os.path.join(ROOT, "unlocks.json"), "."),
    (os.path.join(ROOT, "favicon.ico"), "."),
    (os.path.join(ROOT, "images"), "images"),
    (os.path.join(ROOT, "screenlockset"), "screenlockset"),
    (os.path.join(SPECPATH, "access_hash.json"), "."),
]

# Bundled Android platform-tools (adb.exe, fastboot.exe + DLLs).
# The workflow stages them under packaging/bin/ before invoking PyInstaller.
bin_src = os.path.join(SPECPATH, "bin")
if os.path.isdir(bin_src):
    datas.append((bin_src, "bin"))

# Bundled third-party installers (Samsung USB Driver).
installers_src = os.path.join(SPECPATH, "installers")
if os.path.isdir(installers_src):
    datas.append((installers_src, "installers"))

a = Analysis(
    [os.path.join(SPECPATH, "launcher.py")],
    pathex=[ROOT],
    binaries=pyqt5_binaries,
    datas=datas + pyqt5_datas,
    hiddenimports=[
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
        "requests",
        # main.py imports these via runpy at runtime, so PyInstaller's static
        # analysis of launcher.py would otherwise miss them.
        "tkinter",
        "tkinter.ttk",
        "tkinter.font",
        "tkinter.messagebox",
        "tkinter.simpledialog",
        "tkinter.filedialog",
        "xml.etree.ElementTree",
        "multiprocessing",
    ] + pyqt5_hiddenimports,
    hookspath=[],
    runtime_hooks=[os.path.join(SPECPATH, "runtime_hook.py")],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="nPhoneKIT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(ROOT, "favicon.ico"),
    uac_admin=True,
)
