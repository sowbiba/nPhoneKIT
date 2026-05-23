# PyInstaller spec for nPhoneKIT Windows --onefile build.
# Invoked as: pyinstaller --clean --noconfirm packaging/nPhoneKIT.spec
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

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

a = Analysis(
    [os.path.join(SPECPATH, "launcher.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
        "requests",
    ],
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
